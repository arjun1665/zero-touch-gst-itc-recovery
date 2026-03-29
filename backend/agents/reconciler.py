import os
from db_schema import erp_collection, log_audit
from mock_gstn.mock_gstn import mock_gstr2b_payload 

def safe_float(value, default=0.0) -> float:
    if value is None:
        return default
    stripped = str(value).strip()
    if stripped.upper() in ("", "FALSE", "TRUE", "N/A", "NONE"):
        return default
    try:
        return float(stripped)
    except ValueError:
        return default

def load_erp_purchases_from_mongo():
    cursor = erp_collection.find({"Transaction_Type": {"$regex": "Purchase", "$options": "i"}})
    purchases = []
    
    for row in cursor:
        inv_num = row.get("Invoice_Number", "").strip()
        if not inv_num: continue
        igst = safe_float(row.get("IGST"))
        cgst = safe_float(row.get("CGST"))
        sgst = safe_float(row.get("SGST"))

        purchases.append({
            "invoice_number":  inv_num,
            "vendor_name":     row.get("Party_Name", "Unknown"),
            "gstin":           row.get("GSTIN", "Unknown"),
            "tax_amount":      igst + cgst + sgst,
            "goods_received":  bool(row.get("Goods_Received", False)),
            "itc_eligibility": str(row.get("ITC_Eligibility", "")).strip(),
            "is_rcm":          bool(row.get("Is_RCM", False)),
        })
    return purchases

def run_reconciliation(period: str):
    try:
        gstr2b_data = mock_gstr2b_payload
    except Exception as e:
        log_audit("Reconciler", "API_ERROR", {"details": str(e)})
        return []

    gstr2b_lookup = {item["invoice_number"]: item for item in gstr2b_data}
    internal_purchases = load_erp_purchases_from_mongo()
    mismatches = []
    
    for book_invoice in internal_purchases:
        inv_num = book_invoice["invoice_number"]

        if not book_invoice["goods_received"]:
            mismatches.append({"invoice_number": inv_num, "issue": "Goods not received (Sec 16 Block)", "tax_amount": book_invoice["tax_amount"]})
            continue

        if book_invoice["itc_eligibility"] == "Blocked_Sec17_5":
            mismatches.append({"invoice_number": inv_num, "issue": "Blocked under Section 17(5)", "tax_amount": book_invoice["tax_amount"]})
            continue

        if book_invoice["is_rcm"]:
            continue

        if inv_num not in gstr2b_lookup:
            mismatches.append({"invoice_number": inv_num, "issue": "Missing from GSTR-2B (Vendor failed to file)", "tax_amount": book_invoice["tax_amount"]})
            continue

        gstn_record = gstr2b_lookup[inv_num]
        gstn_total = safe_float(gstn_record.get("igst")) + safe_float(gstn_record.get("cgst")) + safe_float(gstn_record.get("sgst"))

        difference = abs(book_invoice["tax_amount"] - gstn_total)
        if difference > 5.0:
            mismatches.append({
                "invoice_number": inv_num, 
                "issue": f"Value Mismatch (Books: ₹{book_invoice['tax_amount']} vs GSTN: ₹{gstn_total})",
                "tax_amount": difference # Adding the difference as the risk value
            })

    return mismatches

def watcher_agent(state):
    print("\n[Watcher Agent] Checking GSTN Portal for new GSTR-2B data...")
    return {"current_period": state.get("current_period", "2026-03")}

def reconciliation_agent(state):
    print("\n[Reconciliation Agent] Comparing MongoDB ERP against Government GSTR-2B...")
    period = state.get("current_period", "2026-03")
    found_mismatches = run_reconciliation(period)
    books_data = load_erp_purchases_from_mongo()
    log_audit("Reconciler", "RECONCILIATION_RUN", {"mismatches_count": len(found_mismatches)})
    return {"mismatches": found_mismatches, "books_data": books_data}