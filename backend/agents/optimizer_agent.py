import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

def optimizer_agent(state):
    print("\n[Optimizer Agent] 🧠 Analyzing Financial Horizon & Mismatches for HITL report...")
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.1
    )

    financial_context = state.get("financial_context", {})
    mismatches = state.get("mismatches", [])

    mismatch_summary = []
    for m in mismatches:
        mismatch_summary.append({
            "invoice_number": m.get("invoice_number", "Unknown"),
            "issue_description": m.get("issue", "No description provided"),
            "tax_value": m.get("tax_amount", 0)
        })

    prompt = PromptTemplate(
        template="""You are a quantitative Indian GST Tax AI Analyst.
        Your job is to analyze invoice mismatches and produce a structured report with EXACT numbers.
        
        --- FINANCIAL HORIZON ---
        Strategy: {strategy}
        Current Month Output Tax Liability: ₹{current_tax}
        Accrued Next Month Liability: ₹{accrued_tax}
        Total Liability Horizon: ₹{total_liability}
        Validated Safe ITC (GSTR-2B reconciled): ₹{safe_itc}
        Net Cash Requirement (Liability - Safe ITC): ₹{cash_gap}

        --- MISMATCH DATA ---
        {mismatches}

        INSTRUCTIONS:
        1. For every claim/defer recommendation, you MUST include exact ₹ values showing the impact.
        2. Reference specific CGST Act sections (Section 16(2), Section 16(4), Section 17(5), Rule 36(4), Section 16(2)(aa)) where applicable.
        3. Show how each recommendation changes the net cash position numerically.
        4. For variance, compute the exact percentage: ((books_val - gstn_val) / books_val * 100).

        Return ONLY a valid JSON object with EXACTLY these keys:
        {{
            "mismatch_analysis": [
                {{
                    "invoice_number": "...",
                    "variance_calculation": "Books: ₹X vs GSTN: ₹Y — Difference: ₹Z (N% variance)",
                    "action_required": "Concise step for recovery."
                }}
            ],
            "recommended_to_claim": [
                {{
                    "invoice_number": "...",
                    "itc_value": <number>,
                    "financial_justification": "This ITC of ₹X is validated in GSTR-2B. Claiming it reduces net liability from ₹A to ₹B, saving ₹C in cash outflow. Fully compliant under Section 16 of CGST Act.",
                    "legal_sections": ["Section 16(2)(aa)", "Rule 36(4)"],
                    "impact_breakdown": {{
                        "current_liability": <number>,
                        "after_claim": <number>,
                        "cash_saved": <number>,
                        "variance_from_gstn": "0% — fully matched" 
                    }}
                }}
            ],
            "recommended_to_defer": [
                {{
                    "invoice_number": "...",
                    "itc_value": <number>,
                    "risk_assessment": "This ₹X claim has a Y% variance from GSTN records. Under Section 16(2)(aa), ITC is only available if reflected in GSTR-2B. Claiming this risks ₹Z in penalties under Section 74 plus 18% interest under Section 50.",
                    "legal_sections": ["Section 16(2)(aa)", "Section 74"],
                    "risk_score": <1-10>
                }}
            ]
        }}
        """,
        input_variables=["strategy", "current_tax", "accrued_tax", "total_liability", "safe_itc", "cash_gap", "mismatches"]
    )

    chain = prompt | llm
    
    try:
        response = chain.invoke({
            "strategy": financial_context.get("strategy_indicator", "STABLE"),
            "current_tax": financial_context.get("current_output_tax", 0),
            "accrued_tax": financial_context.get("accrued_next_month_tax", 0),
            "total_liability": financial_context.get("total_liability_horizon", 0),
            "safe_itc": financial_context.get("total_validated_itc", 0),
            "cash_gap": financial_context.get("net_tax_payable_current", 0),
            "mismatches": json.dumps(mismatch_summary)
        })

        clean_json = response.content.replace("```json", "").replace("```", "").strip()
        report_draft = json.loads(clean_json)

        return {
            "gstr3b_draft": report_draft,
            "hitl_flag": True
        }

    except Exception as e:
        print(f"   ❌ Optimizer Error: {e}")
        return {"hitl_flag": False}