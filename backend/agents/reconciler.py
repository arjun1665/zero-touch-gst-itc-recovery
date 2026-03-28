<<<<<<< HEAD
import requests
import os
from db_schema import erp_collection, log_audit  # Import from your new schema

# --- HELPER ---
def safe_float(value, default=0.0) -> float:
=======
import csv
import requests
import os

# --- HELPER ---

def safe_float(value, default=0.0) -> float:
    """
    Safely converts a CSV cell to float.
    Handles: empty strings, 'FALSE', 'TRUE', None, whitespace.
    """
>>>>>>> 4430d31c7c4005d4e1f09af7d1bf87472b8d2b60
    if value is None:
        return default
    stripped = str(value).strip()
    if stripped.upper() in ("", "FALSE", "TRUE", "N/A", "NONE"):
        return default
    try:
        return float(stripped)
    except ValueError:
        return default
<<<<<<< HEAD

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
=======

# --- CORE BUSINESS LOGIC ---

def load_erp_purchases(filepath: str):
    purchases = []
    if not os.path.exists(filepath):
        print(f"⚠️  Warning: CSV file not found at {filepath}")
        return purchases

    with open(filepath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["Transaction_Type"].strip().title() != "Purchase":
                continue

            # Guard: skip malformed rows where Invoice_Number is missing or blank
            inv_num = row.get("Invoice_Number", "").strip()
            if not inv_num:
                print(f"⚠️  Skipping malformed row (missing Invoice_Number): {dict(row)}")
                continue

            igst = safe_float(row.get("IGST"))
            cgst = safe_float(row.get("CGST"))
            sgst = safe_float(row.get("SGST"))

            # Inside load_erp_purchases loop:

            purchases.append({
                "invoice_number":  inv_num,
                "vendor_name":     row.get("Party_Name", "Unknown"),
                "tax_amount":      igst + cgst + sgst,
                "goods_received":  (row.get("Goods_Received") or "").strip().upper() == "TRUE",
                "itc_eligibility": (row.get("ITC_Eligibility") or "").strip(),
                "is_rcm":          (row.get("Is_RCM") or "").strip().upper() == "TRUE",
            })
    return purchases


def run_reconciliation(period: str, csv_filepath: str):
    try:
        response = requests.get(
            f"http://localhost:8000/mock-gstn/gstr2b/{period}", timeout=10
        )
        response.raise_for_status()
        gstr2b_data = response.json().get("data", [])
    except Exception as e:
        print(f"❌ Error fetching GSTN data: {e}")
        return []

    gstr2b_lookup = {item["invoice_number"]: item for item in gstr2b_data}
    internal_purchases = load_erp_purchases(csv_filepath)

    mismatches = []
    for book_invoice in internal_purchases:
        inv_num = book_invoice["invoice_number"]

        # FIX: use "goods_received" (lowercase) — matches what load_erp_purchases stores
        if not book_invoice["goods_received"]:
            mismatches.append({
                "invoice_number": inv_num,
                "issue": "Goods not received (Sec 16 Block)"
            })
            continue

        if book_invoice["itc_eligibility"] == "Blocked_Sec17_5":
            mismatches.append({
                "invoice_number": inv_num,
                "issue": "Blocked under Section 17(5)"
            })
            continue

        if book_invoice["is_rcm"]:
            # RCM handled separately — output tax liability, not vendor match
            continue

        if inv_num not in gstr2b_lookup:
            mismatches.append({
                "invoice_number": inv_num,
                "issue": "Missing from GSTR-2B (Vendor failed to file)"
            })
            continue

        gstn_record = gstr2b_lookup[inv_num]
        gstn_igst   = safe_float(gstn_record.get("igst"))
        gstn_cgst   = safe_float(gstn_record.get("cgst"))
        gstn_sgst   = safe_float(gstn_record.get("sgst"))
        gstn_total  = gstn_igst + gstn_cgst + gstn_sgst
>>>>>>> 4430d31c7c4005d4e1f09af7d1bf87472b8d2b60

        difference = abs(book_invoice["tax_amount"] - gstn_total)
        if difference > 5.0:
            mismatches.append({
<<<<<<< HEAD
                "invoice_number": inv_num, 
                "issue": f"Value Mismatch of ₹{difference:.2f} (Books: ₹{book_invoice['tax_amount']:.2f} vs GSTN: ₹{gstn_total:.2f})"
=======
                "invoice_number": inv_num,
                "issue": (
                    f"Value Mismatch of ₹{difference:.2f} "
                    f"(Books: ₹{book_invoice['tax_amount']:.2f} "
                    f"vs GSTN: ₹{gstn_total:.2f})"
                )
>>>>>>> 4430d31c7c4005d4e1f09af7d1bf87472b8d2b60
            })

    return mismatches

<<<<<<< HEAD
# --- LANGGRAPH AGENT NODES ---
=======

# --- LANGGRAPH AGENT NODES ---

>>>>>>> 4430d31c7c4005d4e1f09af7d1bf87472b8d2b60
def watcher_agent(state):
    print("\n[Watcher Agent] Checking GSTN Portal for new GSTR-2B data...")
    period = state.get("current_period", "2026-03")
    return {"current_period": period}

<<<<<<< HEAD
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
=======

def reconciliation_agent(state):
    print("\n[Reconciliation Agent] Comparing ERP Purchases against Government GSTR-2B...")
    period   = state.get("current_period", "2026-03")
    csv_path = os.path.join("erp_register.csv")
    found_mismatches = run_reconciliation(period, csv_path)
    print(f"   => Found {len(found_mismatches)} mismatches/issues requiring attention.")

    books_data = load_erp_purchases(csv_path)

    return {
        "mismatches":  found_mismatches,
        "books_data":  books_data,
    }
>>>>>>> 4430d31c7c4005d4e1f09af7d1bf87472b8d2b60
