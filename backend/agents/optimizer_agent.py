import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate


def optimizer_agent(state):
    print("\n[Optimizer Agent] 🧠 Analyzing Financial Horizon & Mismatches for HITL report...")
    
    # 1. Setup the LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.1
    )

    # 2. Extract context from state
    financial_context = state.get("financial_context", {})
    mismatches = state.get("mismatches", [])

    # 3. FIX: Safely transform mismatch data to match the Prompt's expectations
    # We change 'issue' (from reconciler) to 'issue_description' for the LLM
    mismatch_summary = []
    for m in mismatches:
        mismatch_summary.append({
            "invoice_number": m.get("invoice_number", "Unknown"),
            "issue_description": m.get("issue", "No description provided")
        })

    # 4. The Quantitative Prompt Template
    prompt = PromptTemplate(
        template="""You are a quantitative Indian GST Tax AI Analyst. 
        Generate a concise, data-backed financial report for the Finance Team.
        
        --- FINANCIAL HORIZON ---
        Strategy: {strategy}
        Current Month Liability: ₹{current_tax}
        Accrued Next Month Liability: ₹{accrued_tax}
        Validated Safe ITC: ₹{safe_itc}
        Net Cash Requirement: ₹{cash_gap}

        --- MISMATCH DATA ---
        {mismatches}

        Return ONLY a valid JSON object with EXACTLY these keys:
        {{
            "executive_brief": "Strictly numbers-based summary of total liability vs available credit.",
            "mismatch_analysis": [
                {{
                    "invoice_number": "...",
                    "variance_calculation": "Numerical breakdown of the discrepancy.",
                    "action_required": "Concise step for recovery."
                }}
            ],
            "recommended_to_claim": [
                {{
                    "invoice_number": "...",
                    "itc_value": "...",
                    "financial_justification": "Why this bridges the cash gap safely."
                }}
            ],
            "recommended_to_defer": [
                {{
                    "invoice_number": "...",
                    "itc_value": "...",
                    "risk_assessment": "Numerical impact of the risk."
                }}
            ]
        }}
        """,
        input_variables=["strategy", "current_tax", "accrued_tax", "safe_itc", "cash_gap", "mismatches"]
    )

    # 5. Execute the chain
    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "strategy": financial_context.get("strategy_indicator", "STABLE"),
            "current_tax": financial_context.get("current_output_tax", 0),
            "accrued_tax": financial_context.get("accrued_next_month_tax", 0),
            "safe_itc": financial_context.get("total_validated_itc", 0),
            "cash_gap": financial_context.get("net_tax_payable_current", 0),
            "mismatches": json.dumps(mismatch_summary)
        })

        # Clean JSON and parse
        clean_json = response.content.replace("```json", "").replace("```", "").strip()
        report_draft = json.loads(clean_json)

        # 6. Update state and trigger HITL (Human-in-the-loop) flag
        return {
            "gstr3b_draft": report_draft,
            "hitl_flag": True
        }

    except Exception as e:
        print(f"   ❌ Optimizer Error: {e}")
        return {"hitl_flag": False}