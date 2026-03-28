import os
from datetime import datetime
from db_schema import gstr3b_collection, log_audit  # <-- Import the new collection and logger

def clean_currency(value):
    """Removes ₹, commas, and whitespace so a string can be converted to float."""
    if isinstance(value, (int, float)):
        return float(value)
    if not value:
        return 0.0
    clean_val = str(value).replace('₹', '').replace(',', '').strip()
    try:
        return float(clean_val)
    except ValueError:
        return 0.0

def filing_agent(state):
    print("\n[Filing Agent] 📝 Compiling GSTR-3B Draft and saving to Database...")

    period = state.get("current_period", "2026-03")
    context = state.get("financial_context", {})
    draft = state.get("gstr3b_draft", {})
    
    # 1. Dynamically calculate ITC using the CLEAN helper
    approved_claims = draft.get("recommended_to_claim", [])
    total_itc_available = sum(clean_currency(item.get("itc_value", 0)) for item in approved_claims)

    # 2. Extract Output Liability (Assuming 200000 for the demo if context is missing)
    outward_tax = context.get("current_output_tax", 200000.0)
    
    # 3. Calculate Net Tax Payable
    net_cash_payable = max(0, outward_tax - total_itc_available)

    # 4. Electronic Cash Ledger Check
    current_ledger_balance = 50000.0
    top_up_required = max(0, net_cash_payable - current_ledger_balance)

    # 5. Construct Table 4 for Reversals
    deferred_list = draft.get("recommended_to_defer", [])
    total_itc_reversed = sum(clean_currency(item.get("itc_value", 0)) for item in deferred_list)

    # 6. Final JSON Structure
    gstr3b_final = {
        "period": period,                     # <-- Tag it with the month
        "generated_at": datetime.now(),       # <-- Timestamp of creation
        "tables": {
            "3_1_Outward_Supplies": outward_tax,
            "4_ITC": {
                "4_A_All_Other_ITC": total_itc_available,
                "4_B_ITC_Reversed": total_itc_reversed,
                "4_C_Net_ITC_Available": total_itc_available
            },
            "6_1_Payment": {
                "tax_payable_cash": net_cash_payable,
                "ledger_balance": current_ledger_balance,
                "top_up_amount": top_up_required
            }
        },
        "filing_meta": {
            "due_date": "2026-04-20",
            "filing_status": "READY_FOR_APPROVAL" if top_up_required == 0 else "AWAITING_FUNDS"
        }
    }

    # --- 7. SAVE TO MONGODB ---
    # Delete any previous draft for this period to avoid duplicates, then insert the new one
    gstr3b_collection.delete_many({"period": period})
    gstr3b_collection.insert_one(gstr3b_final.copy()) # Use .copy() so LangGraph doesn't trip over the MongoDB _id
    
    # Audit log the action
    log_audit("Filing_Agent", "GSTR3B_SAVED", f"Saved final draft for {period} with Net Payable: ₹{net_cash_payable}")

    print(f"   => GSTR-3B Prepared & Saved to MongoDB. Net Cash Payable: ₹{net_cash_payable:,.2f}")
    
    # Remove the datetime object before returning to LangGraph state, as LangGraph prefers pure JSON
    del gstr3b_final["generated_at"]
    return {"final_gstr3b": gstr3b_final}