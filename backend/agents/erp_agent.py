import os
from state import GSTGraphState
from gst_engine import EnterpriseGSTEngine
from db_schema import log_audit, get_raw_erp_inventory  # Added helper for seeding

def erp_agent(state: GSTGraphState):
    print("\n[ERP Agent] 🔄 Connecting to MongoDB Atlas & Calculating Financial Horizon...")
    
    # 1. Extract period from state
    period = state.get("current_period", "2026-03")
    try:
        year = int(period.split("-")[0])
        month = int(period.split("-")[1])
    except (ValueError, IndexError):
        year, month = 2026, 3

    # 2. Run Enterprise Engine using MongoDB data instead of CSV
    engine = EnterpriseGSTEngine()
    
    # FETCH FROM DB: Replacing csv_filename logic
    raw_records = get_raw_erp_inventory() 
    engine_summary = engine.process_erp_data(raw_records, current_month=month, current_year=year)
    
    # 3. Calculate Safe ITC based on Mismatches from Reconciler
    mismatched_itc = 0.0
    mismatches = state.get("mismatches", [])
    
    # We use the raw_records we just fetched to cross-reference
    for m in mismatches:
        inv_num = m.get("invoice_number") if isinstance(m, dict) else getattr(m, "invoice_number", None)
        
        for book_item in raw_records:
            if book_item.get("invoice_number") == inv_num:
                tax_amt = (
                    float(book_item.get("IGST", 0)) + 
                    float(book_item.get("CGST", 0)) + 
                    float(book_item.get("SGST", 0))
                )
                mismatched_itc += tax_amt
                break
                
    total_validated_itc = engine_summary["total_books_itc"] - mismatched_itc
    
    # 4. Generate Financial Context
    financial_context = engine.generate_financial_context(engine_summary, total_validated_itc)
    
    # 5. PERSISTENCE: Log the calculation to MongoDB
    log_audit(
        agent_name="ERP_Agent",
        action="FINANCIAL_HORIZON_CALCULATED",
        details={
            "period": period,
            "total_books_itc": engine_summary["total_books_itc"],
            "mismatched_itc_blocked": mismatched_itc,
            "net_validated_itc": total_validated_itc,
            "status": "Ready for Filing"
        }
    )

    # 6. Return to LangGraph
    return {
        "financial_context": financial_context,
        "total_validated_itc": total_validated_itc,
        "books_data": raw_records # Maintaining state for Reconciler
    }