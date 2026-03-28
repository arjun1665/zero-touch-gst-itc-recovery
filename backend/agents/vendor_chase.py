# backend/agents/vendor_chase.py
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from state import GSTGraphState
from dotenv import load_dotenv
load_dotenv()
def send_whatsapp(body: str, to_number: str):
    """Fires the physical WhatsApp message via Twilio."""
    client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
    try:
        message = client.messages.create(
            from_=os.getenv("TWILIO_WHATSAPP_NUMBER"),
            body=body,
            to=to_number
        )
        return message.sid
    except Exception as e:
        print(f"❌ Twilio Error: {e}")
        return None

def send_email(subject: str, body: str, to_email: str):
    """Fires the physical Email via SMTP."""
    sender_email = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDER_APP_PASSWORD")
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"❌ SMTP Error: {e}")
        return False

def vendor_chase_agent(state: GSTGraphState) -> dict:
    """
    Agent 3: Reads mismatches, uses Gemini to draft messages, and sends them.
    """
    print("\n[Vendor Chase Agent] 🤖 Waking up. Analyzing mismatches for outreach...")
    
    mismatches = state.get("mismatches", [])
    days_left = state.get("days_to_cutoff", 30)
    chase_logs = []
    
    # Initialize Gemini 1.5 Flash (Fast and perfect for text generation)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2, # Keep it low for professional tone
        api_key=os.getenv("GEMINI_API_KEY")
    )
    
    # We instruct Gemini to return strict JSON so we can parse the two separate drafts
    prompt_template = PromptTemplate.from_template("""
    You are an autonomous Financial Operations AI.
    A vendor has made a GST filing error. 
    
    Vendor GSTIN: {vendor_gstin}
    Invoice Number: {invoice_number}
    Error Type: {issue_type}
    Blocked ITC Amount: ₹{tax_value}
    Days until filing deadline: {days_left}
    
    Write two messages to recover this cost. Sign off as Vishal Rajaraman from the Finance Team.
    1. A short, urgent WhatsApp message.
    2. A formal, legally sound Email.
    
    Return ONLY a valid JSON object with the keys "whatsapp_body", "email_subject", and "email_body". Do not include markdown blocks.
    """)
    
    for mismatch in mismatches:
        # We don't chase for Credit Notes, only vendor errors
        if mismatch.issue_type == "credit_note_pending":
            continue
            
        print(f"   Drafting omnichannel outreach for {mismatch.invoice_number}...")
        
        # 1. Generate the content with Gemini
        chain = prompt_template | llm
        response = chain.invoke({
            "vendor_gstin": mismatch.vendor_gstin,
            "invoice_number": mismatch.invoice_number,
            "issue_type": mismatch.issue_type,
            "tax_value": mismatch.tax_value,
            "days_left": days_left
        })
        
        try:
            # Clean the response in case Gemini adds ```json
            clean_json = response.content.replace("```json", "").replace("```", "").strip()
            drafts = json.loads(clean_json)
            
            # 2. Fire the APIs (Hardcoded to your test numbers for the hackathon demo)
            target_phone = os.getenv("MY_WHATSAPP_NUMBER")
            target_email = os.getenv("SENDER_EMAIL") # Sending to yourself for the live demo
            
            print("   📲 Sending WhatsApp via Twilio...")
            send_whatsapp(drafts["whatsapp_body"], target_phone)
            
            print("   📧 Sending Email via SMTP...")
            send_email(drafts["email_subject"], drafts["email_body"], target_email)
            
            # 3. Log the action to the LangGraph State
            chase_logs.append({
                "invoice_number": mismatch.invoice_number,
                "vendor": mismatch.vendor_gstin,
                "action": "Omnichannel Chase Executed",
                "whatsapp_snippet": drafts["whatsapp_body"][:50] + "..."
            })
            
        except Exception as e:
            print(f"   ❌ Failed to process or send for {mismatch.invoice_number}: {e}")

    print(f"[Vendor Chase Agent] ✅ Outreach complete. Logged {len(chase_logs)} communications.")
    return {"vendor_chase_log": chase_logs}