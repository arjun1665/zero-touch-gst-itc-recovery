from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(
    prefix="/mock-gstn",
    tags=["Government Portal Simulation"]
)

mock_gstr2b_payload = [
    {"invoice_number": "INV-2026-001", "vendor_gstin": "27AADCB2230M1Z2", "date": "2026-02-28", "taxable_value": 277777.0, "igst": 0.0, "cgst": 25000.0, "sgst": 25000.0},
    {"invoice_number": "INV-2026-045", "vendor_gstin": "29BBBCB1120K1Z5", "date": "2026-03-05", "taxable_value": 66666.0, "igst": 12000.0, "cgst": 0.0, "sgst": 0.0},
    # Value mismatch: Vendor filed 8500 instead of 85000
    {"invoice_number": "INV-2026-088", "vendor_gstin": "07CCDCB3340L1Z8", "date": "2026-02-15", "taxable_value": 47222.0, "igst": 8500.0, "cgst": 0.0, "sgst": 0.0},
    {"invoice_number": "INV-2026-115", "vendor_gstin": "33EEECB5560Q1Z3", "date": "2026-02-25", "taxable_value": 27777.0, "igst": 5000.0, "cgst": 0.0, "sgst": 0.0},
    {"invoice_number": "INV-2026-150", "vendor_gstin": "27TAJ1234Z5", "date": "2026-03-02", "taxable_value": 50000.0, "igst": 0.0, "cgst": 1250.0, "sgst": 1250.0},
    {"invoice_number": "INV-2026-200", "vendor_gstin": "27SHARMA1234Z5", "date": "2026-03-04", "taxable_value": 100000.0, "igst": 0.0, "cgst": 9000.0, "sgst": 9000.0}
    # Notice INV-2026-102 is missing entirely, simulating a vendor who failed to file.
]

@router.get("/gstr2b/{period}")
def fetch_static_gstr2b(period: str) -> Dict[str, Any]:
    return {
        "period": period,
        "data": mock_gstr2b_payload
    }