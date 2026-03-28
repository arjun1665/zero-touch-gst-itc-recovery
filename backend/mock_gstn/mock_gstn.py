# backend/mock_gstn/mock_gstn.py  (Note: Make sure your folder structure matches your imports in main.py)
from fastapi import APIRouter
from typing import Dict, List, Any  # Added 'Any' here

router = APIRouter(
    prefix="/mock-gstn",
    tags=["Government Portal Simulation"]
)

mock_gstr2b_payload = [
    {
        "invoice_number": "INV-1001",
        "vendor_gstin": "27AADCB2230M1Z2",
        "date": "2026-03-02",
        "amount": 50000.0,
        "tax_amount": 9000.0,
        "type": "regular",
        "status": "filed"
    },
    {
        "invoice_number": "INV-1002",
        "vendor_gstin": "29BBBCB1120K1Z5",
        "date": "2026-03-05",
        "amount": 120000.0,
        "tax_amount": 21600.0,
        "type": "regular",
        "status": "filed_wrong_gstin" 
    },
    {
        "invoice_number": "CN-2001",
        "vendor_gstin": "27AADCB2230M1Z2",
        "date": "2026-03-10",
        "amount": -10000.0,
        "tax_amount": -1800.0,
        "type": "credit_note",
        "status": "filed"
    }
]

# Changed return type to Dict[str, Any]
@router.get("/gstr2b/{period}")
def fetch_static_gstr2b(period: str) -> Dict[str, Any]:
    return {
        "period": period,
        "generation_date": f"{period}-14",
        "data": mock_gstr2b_payload
    }

# Changed return type to Dict[str, Any]
@router.get("/gstr2a/{period}")
def fetch_dynamic_gstr2a(period: str) -> Dict[str, Any]:
    return {
        "period": period,
        "last_updated": "Real-Time",
        "data": mock_gstr2b_payload 
    }