from state import GSTGraphState
from gst_engine import EnterpriseGSTEngine

def erp_agent(state: GSTGraphState):
    print("\n[ERP Agent] 🔄 Connecting to Unified ERP Ledger & Calculating Financial Horizon...")
    
    # 1. Extract year and month dynamically from the state (e.g., "2026-03")
    period = state.get("current_period", "2026-03")
    year, month = int(period.split("-")[0]), int(period.split("-")[1])
    
    # 2. Run your new Enterprise Engine
    engine = EnterpriseGSTEngine()
    engine_summary = engine.process_erp_csv("erp_register.csv", current_month=month, current_year=year)
    
    # 3. Calculate Safe ITC based on mismatches provided by the Reconciler
    mismatched_itc = 0
    mismatches = state.get("mismatches", [])
    
    for m in mismatches:
        # Depending on how the reconciler passes the data, extract the value to subtract
        # If the reconciler only passes the invoice number and issue, you may need to look up the tax amount from books_data
        inv_num = m["invoice_number"] if isinstance(m, dict) else getattr(m, "invoice_number", None)
        
        for book_item in state.get("books_data", []):
            if book_item.get("invoice_number") == inv_num:
                # Assuming books_data is populated directly from the CSV
                tax_amt = float(book_item.get("IGST", 0)) + float(book_item.get("CGST", 0)) + float(book_item.get("SGST", 0))
                mismatched_itc += tax_amt
                break
                
    total_validated_itc = engine_summary["total_books_itc"] - mismatched_itc
    
    # 4. Generate the final context
    financial_context = engine.generate_financial_context(engine_summary, total_validated_itc)
    
    # Save the financial context to the LangGraph state
    return {"financial_context": financial_context}