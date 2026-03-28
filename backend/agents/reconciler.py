# backend/agents/reconciler.py
import requests
from typing import Dict, Any
from state import GSTGraphState, MismatchRecord

# Our company's mock GSTIN
OUR_COMPANY_GSTIN = "27AADCB2230M1Z2"

def watcher_agent(state: GSTGraphState) -> Dict[str, Any]:
    """
    Agent 1: Connects to the GSTN Portal (our mock API) and pulls the static 2B data.
    """
    print("\n[Watcher Agent] 👁️ Waking up. Polling GSTN Portal for GSTR-2B...")
    
    period = state.get("current_period", "2026-03")
    url = f"http://127.0.0.1:8000/mock-gstn/gstr2b/{period}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        portal_data = response.json().get("data", [])
        
        print(f"[Watcher Agent] ✅ Successfully retrieved {len(portal_data)} records from GSTN.")
        return {"gstr2b_static_data": portal_data}
        
    except requests.exceptions.RequestException as e:
        print(f"[Watcher Agent] ❌ Failed to connect to GSTN API: {e}")
        return {"gstr2b_static_data": []}


def reconciliation_agent(state: GSTGraphState) -> Dict[str, Any]:
    """
    Agent 2: Performs the 3-way mathematical match between Internal Books and GSTR-2B.
    """
    print("\n[Reconciliation Agent] 🧮 Starting 3-way match analysis...")
    
    books = state.get("books_data", [])
    gstr2b = state.get("gstr2b_static_data", [])
    days_to_cutoff = state.get("days_to_cutoff", 250)
    
    is_critical_timeline = days_to_cutoff < 30 
    new_mismatches = []
    
    gstr2b_dict = {item["invoice_number"]: item for item in gstr2b}

    # Check our books against the government portal
    for book_invoice in books:
        inv_num = book_invoice["invoice_number"]
        
        # Scenario A: Missing Invoice
        if inv_num not in gstr2b_dict:
            print(f"   ⚠️ Mismatch Found: {inv_num} is missing from GSTR-2B.")
            new_mismatches.append(
                MismatchRecord(
                    invoice_number=inv_num,
                    vendor_gstin=book_invoice["vendor_gstin"],
                    issue_type="vendor_not_filed",
                    tax_value=book_invoice["tax_amount"],
                    is_critical=is_critical_timeline
                )
            )
            continue
            
        portal_invoice = gstr2b_dict[inv_num]
        
        # Scenario B: GSTIN Typo
        if portal_invoice.get("status") == "filed_wrong_gstin":
            print(f"   ⚠️ Mismatch Found: {inv_num} has a GSTIN typo in the portal.")
            new_mismatches.append(
                MismatchRecord(
                    invoice_number=inv_num,
                    vendor_gstin=book_invoice["vendor_gstin"],
                    issue_type="gstin_mismatch",
                    tax_value=book_invoice["tax_amount"],
                    is_critical=is_critical_timeline
                )
            )

    # Look for Credit Notes
    for portal_invoice in gstr2b:
        if portal_invoice.get("type") == "credit_note":
             print(f"   ℹ️ Credit Note Detected: {portal_invoice['invoice_number']}. Flagging for ITC reversal.")
             new_mismatches.append(
                MismatchRecord(
                    invoice_number=portal_invoice["invoice_number"],
                    vendor_gstin=portal_invoice["vendor_gstin"],
                    issue_type="credit_note_pending",
                    tax_value=portal_invoice["tax_amount"],
                    is_critical=False 
                )
             )

    print(f"[Reconciliation Agent] ✅ Analysis complete. Identified actionable mismatches.")
    return {"mismatches": new_mismatches}
