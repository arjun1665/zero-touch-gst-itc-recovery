import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

# --- PHYSICAL DELIVERY FUNCTIONS ---

def send_whatsapp(body: str, to_number: str):
    """Fires a physical WhatsApp message via Twilio."""
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_whatsapp = os.getenv("TWILIO_WHATSAPP_NUMBER")
    
    if not all([account_sid, auth_token, from_whatsapp]):
        print("   ❌ Twilio credentials missing in .env")
        return None

    client = Client(account_sid, auth_token)
    try:
        # Ensure number is prefixed for WhatsApp
        formatted_to = f"whatsapp:{to_number}" if not to_number.startswith("whatsapp:") else to_number
        message = client.messages.create(body=body, from_=from_whatsapp, to=formatted_to)
        return message.sid
    except Exception as e:
        print(f"   ❌ Twilio Error: {e}")
        return None

def send_email(subject: str, body: str, to_email: str):
    """Fires a physical Email via SMTP."""
    sender_email = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDER_APP_PASSWORD")
    
    if not all([sender_email, password]):
        print("   ❌ SMTP credentials missing in .env")
        return False

    msg = MIMEMultipart()
    msg['From'] = f"Vishal Rajaraman <{sender_email}>"
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
        print(f"   ❌ SMTP Error: {e}")
        return False

# --- AGENT LOGIC ---

def vendor_chase_agent(state: dict) -> dict:
    print("\n[Vendor Chase Agent] 🤖 Analyzing mismatches for Omnichannel Outreach...")
    
    mismatches = state.get("mismatches", [])
    books_data = state.get("books_data", []) # Loaded from CSV by Reconciler
    days_left = state.get("days_to_cutoff", 10)
    chase_logs = []
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2,
        api_key=os.getenv("GEMINI_API_KEY")
    )
    
    prompt_template = PromptTemplate.from_template("""
    You are an autonomous Financial Operations AI.
    A vendor has a GST filing mismatch blocking our Input Tax Credit. 
    
    Vendor: {vendor_name} (GSTIN: {vendor_gstin})
    Invoice: {invoice_number}
    Error: {issue_text}
    Tax Value at Risk: ₹{tax_value}
    
    Sign off as Vishal Rajaraman from the Finance Team.
    Return ONLY a JSON object: {{"whatsapp_body": "...", "email_subject": "...", "email_body": "..."}}
    """)

    for mismatch in mismatches:
        # FIX: Use .get() for dictionary access
        inv_num = mismatch.get("invoice_number")
        issue_text = mismatch.get("issue", "").lower()

        # Lookup details from books_data (central ERP register)
        record = next((item for item in books_data if item.get("invoice_number") == inv_num), None)
        
        if not record:
            continue

        # Filter: Only chase specific vendor-side errors
        if "missing" in issue_text or "value mismatch" in issue_text:
            print(f"   📝 Generating recovery drafts for {inv_num}...")
            
            chain = prompt_template | llm
            try:
                response = chain.invoke({
                    "vendor_name": record.get("vendor_name", "Vendor"),
                    "vendor_gstin": record.get("gstin", "Unknown"),
                    "invoice_number": inv_num,
                    "issue_text": issue_text,
                    "tax_value": record.get("tax_amount", 0.0),
                    "days_left": days_left
                })
                
                # Parse JSON safely
                clean_json = response.content.replace("```json", "").replace("```", "").strip()
                drafts = json.loads(clean_json)
                
                # EXECUTION: Send to your demo numbers/emails
                target_phone = os.getenv("MY_WHATSAPP_NUMBER")
                target_email = os.getenv("SENDER_EMAIL") 
                
                send_whatsapp(drafts["whatsapp_body"], target_phone)
                send_email(drafts["email_subject"], drafts["email_body"], target_email)
                
                chase_logs.append({
                    "invoice": inv_num,
                    "status": "Omnichannel Chase Executed",
                    "vendor": record.get("vendor_name")
                })
            except Exception as e:
                print(f"   ❌ Outreach Failed for {inv_num}: {e}")

    return {"vendor_chase_log": chase_logs}