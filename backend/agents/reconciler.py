import requests
import os
from db_schema import erp_collection, log_audit  # Import from your new schema

# --- HELPER ---
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

# --- CORE BUSINESS LOGIC ---
def load_erp_purchases_from_mongo():
    """Pulls purchases directly from the MongoDB collection."""
    # Find all records where Transaction_Type is Purchase
    cursor = erp_collection.find({"Transaction_Type": {"$regex": "Purchase", "$options": "i"}})
    purchases = []
    
    for row in cursor:
        inv_num = row.get("Invoice_Number", "").strip()
        if not inv_num:
            continue

        igst = safe_float(row.get("IGST"))
        cgst = safe_float(row.get("CGST"))
        sgst = safe_float(row.get("SGST"))

        purchases.append({
            "invoice_number":  inv_num,
            "vendor_name":     row.get("Party_Name", "Unknown"),
            "gstin":           row.get("GSTIN", "Unknown"),
            "tax_amount":      igst + cgst + sgst,
            # FIXED: Handle MongoDB native booleans directly instead of treating them as strings
            "goods_received":  bool(row.get("Goods_Received", False)),
            "itc_eligibility": str(row.get("ITC_Eligibility", "")).strip(),
            "is_rcm":          bool(row.get("Is_RCM", False)),
        })
    return purchases

def run_reconciliation(period: str):
    try:
        response = requests.get(f"http://localhost:8000/mock-gstn/gstr2b/{period}", timeout=10)
        response.raise_for_status()
        gstr2b_data = response.json().get("data", [])
    except Exception as e:
        log_audit("Reconciler", "API_ERROR", {"details": str(e)})
        return []

    gstr2b_lookup = {item["invoice_number"]: item for item in gstr2b_data}
    internal_purchases = load_erp_purchases_from_mongo()

    mismatches = []
    for book_invoice in internal_purchases:
        inv_num = book_invoice["invoice_number"]

        # Uses the newly fixed boolean value
        if not book_invoice["goods_received"]:
            mismatches.append({"invoice_number": inv_num, "issue": "Goods not received (Sec 16 Block)"})
            continue

        if book_invoice["itc_eligibility"] == "Blocked_Sec17_5":
            mismatches.append({"invoice_number": inv_num, "issue": "Blocked under Section 17(5)"})
            continue

        if book_invoice["is_rcm"]:
            continue

        if inv_num not in gstr2b_lookup:
            mismatches.append({"invoice_number": inv_num, "issue": "Missing from GSTR-2B (Vendor failed to file)"})
            continue

        gstn_record = gstr2b_lookup[inv_num]
        gstn_total = safe_float(gstn_record.get("igst")) + safe_float(gstn_record.get("cgst")) + safe_float(gstn_record.get("sgst"))

        difference = abs(book_invoice["tax_amount"] - gstn_total)
        if difference > 5.0:
            mismatches.append({
                "invoice_number": inv_num, 
                "issue": f"Value Mismatch of ₹{difference:.2f} (Books: ₹{book_invoice['tax_amount']:.2f} vs GSTN: ₹{gstn_total:.2f})"
            })

    return mismatches

# --- LANGGRAPH AGENT NODES ---
def watcher_agent(state):
    print("\n[Watcher Agent] Checking GSTN Portal for new GSTR-2B data...")
    period = state.get("current_period", "2026-03")
    return {"current_period": period}

def reconciliation_agent(state):
    print("\n[Reconciliation Agent] Comparing MongoDB ERP against Government GSTR-2B...")
    period = state.get("current_period", "2026-03")
    
    found_mismatches = run_reconciliation(period)
    books_data = load_erp_purchases_from_mongo()

    # AUDIT LOGGING
    log_audit("Reconciler", "RECONCILIATION_RUN", {
        "mismatches_count": len(found_mismatches),
        "total_records_checked": len(books_data)
    })

    return {"mismatches": found_mismatches, "books_data": books_data}