"""
Shared fixtures and test data for the entire test suite.
All fixtures are auto-available via pytest's conftest mechanism.
"""
import sys
import os
import pytest

# ---------------------------------------------------------------------------
# Ensure the backend package is importable from tests/
# ---------------------------------------------------------------------------
BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, os.path.abspath(BACKEND_DIR))


# ══════════════════════════════════════════════════════════════════════════════
# MOCK DATA FIXTURES
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def sample_erp_records():
    """Realistic ERP inventory records for March 2026."""
    return [
        # ── SALES ──
        {
            "Invoice_Number": "SALE-2026-001", "Date": "2026-03-01",
            "Party_Name": "Alpha Traders", "GSTIN": "29AADCA1234B1Z1",
            "Transaction_Type": "Sale", "Document_Type": "Invoice",
            "Taxable_Value": 500000, "IGST": 0, "CGST": 45000, "SGST": 45000,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": False, "ITC_Eligibility": "", "Goods_Received": True, "Import_Type": ""
        },
        {
            "Invoice_Number": "SALE-2026-003", "Date": "2026-03-08",
            "Party_Name": "Gamma Industries", "GSTIN": "27CCDCC9012D1Z3",
            "Transaction_Type": "Sale", "Document_Type": "Invoice",
            "Taxable_Value": 450000, "IGST": 81000, "CGST": 0, "SGST": 0,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": False, "ITC_Eligibility": "", "Goods_Received": True, "Import_Type": ""
        },
        # ── PURCHASES ──
        {
            "Invoice_Number": "INV-2026-001", "Date": "2026-03-02",
            "Party_Name": "Acme Supplies", "GSTIN": "27AADCB2230M1Z2",
            "Transaction_Type": "Purchase", "Document_Type": "Invoice",
            "Taxable_Value": 277777, "IGST": 0, "CGST": 25000, "SGST": 25000,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": False, "ITC_Eligibility": "Eligible", "Goods_Received": True, "Import_Type": ""
        },
        {
            "Invoice_Number": "INV-2026-045", "Date": "2026-03-05",
            "Party_Name": "TechParts Global", "GSTIN": "29BBBCB1120K1Z5",
            "Transaction_Type": "Purchase", "Document_Type": "Invoice",
            "Taxable_Value": 66666, "IGST": 12000, "CGST": 0, "SGST": 0,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": False, "ITC_Eligibility": "Eligible", "Goods_Received": True, "Import_Type": ""
        },
        # Purchase — RCM
        {
            "Invoice_Number": "INV-2026-150", "Date": "2026-03-02",
            "Party_Name": "Taj Legal Associates", "GSTIN": "27TAJ1234Z5",
            "Transaction_Type": "Purchase", "Document_Type": "Invoice",
            "Taxable_Value": 50000, "IGST": 0, "CGST": 4500, "SGST": 4500,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": True, "ITC_Eligibility": "Eligible", "Goods_Received": True, "Import_Type": ""
        },
        # Purchase — Blocked Sec 17(5)
        {
            "Invoice_Number": "INV-2026-140", "Date": "2026-03-11",
            "Party_Name": "Premium Club", "GSTIN": "29GGGCB7780S1Z7",
            "Transaction_Type": "Purchase", "Document_Type": "Invoice",
            "Taxable_Value": 200000, "IGST": 0, "CGST": 18000, "SGST": 18000,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": False, "ITC_Eligibility": "Blocked_Sec17_5", "Goods_Received": True, "Import_Type": ""
        },
        # Import of Goods
        {
            "Invoice_Number": "IMP-2026-001", "Date": "2026-03-06",
            "Party_Name": "Shanghai Components", "GSTIN": "",
            "Transaction_Type": "Purchase", "Document_Type": "Bill of Entry",
            "Taxable_Value": 180000, "IGST": 32400, "CGST": 0, "SGST": 0,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": False, "ITC_Eligibility": "Eligible", "Goods_Received": True, "Import_Type": "goods"
        },
    ]


@pytest.fixture
def sample_gstr2b_data():
    """Mock GSTR-2B government portal data."""
    return [
        {"invoice_number": "INV-2026-001", "vendor_gstin": "27AADCB2230M1Z2", "igst": 0, "cgst": 25000, "sgst": 25000},
        {"invoice_number": "INV-2026-045", "vendor_gstin": "29BBBCB1120K1Z5", "igst": 12000, "cgst": 0, "sgst": 0},
        # Value mismatch on INV-2026-088
        {"invoice_number": "INV-2026-088", "vendor_gstin": "07CCDCB3340L1Z8", "igst": 8500, "cgst": 0, "sgst": 0},
    ]


@pytest.fixture
def sample_mismatches():
    """Pre-computed mismatches as returned by the Reconciler agent."""
    return [
        {"invoice_number": "INV-2026-102", "issue": "Missing from GSTR-2B (Vendor failed to file)", "tax_amount": 21600},
        {"invoice_number": "INV-2026-088", "issue": "Value Mismatch (Books: ₹8500 vs GSTN: ₹8500)", "tax_amount": 0},
        {"invoice_number": "INV-2026-130", "issue": "Goods not received (Sec 16 Block)", "tax_amount": 9900},
        {"invoice_number": "INV-2026-140", "issue": "Blocked under Section 17(5)", "tax_amount": 36000},
    ]


@pytest.fixture
def sample_financial_context():
    """Financial context as produced by the ERP Agent."""
    return {
        "current_output_tax": 171000.0,
        "accrued_next_month_tax": 0.0,
        "total_liability_horizon": 171000.0,
        "total_validated_itc": 87000.0,
        "net_tax_payable_current": 84000.0,
        "strategy_indicator": "STABLE"
    }


@pytest.fixture
def sample_optimizer_draft():
    """Minimal optimizer draft for filing agent tests."""
    return {
        "recommended_to_claim": [
            {"invoice_number": "INV-2026-001", "itc_value": 50000},
            {"invoice_number": "INV-2026-045", "itc_value": 12000},
        ],
        "recommended_to_defer": [
            {"invoice_number": "INV-2026-088", "itc_value": 8500},
        ]
    }


@pytest.fixture
def sample_gstr3b_output():
    """Sample GSTR-3B final output for PDF / downstream tests."""
    return {
        "period": "2026-03",
        "generated_at": "2026-03-20T10:00:00",
        "tables": {
            "3_1": {
                "a": {"taxable_value": 1470000, "igst": 101700, "cgst": 73800, "sgst": 73800, "cess": 0},
                "b": {"taxable_value": 0, "igst": 0, "cess": 0},
                "c": {"taxable_value": 85000},
                "d": {"taxable_value": 80000, "igst": 5400, "cgst": 4500, "sgst": 4500, "cess": 0},
                "e": {"taxable_value": 0}
            },
            "3_2": {
                "unregistered": {"taxable_value": 75000, "igst": 13500},
                "composition": {"taxable_value": 40000, "igst": 7200},
                "uin_holders": {"taxable_value": 0, "igst": 0}
            },
            "4_ITC": {
                "4_A": {
                    "import_goods": {"igst": 32400},
                    "import_services": {"igst": 17100},
                    "rcm": {"igst": 5400, "cgst": 4500, "sgst": 4500},
                    "isd": {"igst": 0, "cgst": 0, "sgst": 0},
                    "all_other_itc": {"igst": 17000, "cgst": 34000, "sgst": 34000},
                    "total": {"igst": 71900, "cgst": 38500, "sgst": 38500}
                },
                "4_B_Reversed": {
                    "rule_42_43": {"igst": 0, "cgst": 0, "sgst": 0},
                    "others": {"igst": 0, "cgst": 0, "sgst": 0}
                },
                "4_C_Net_ITC": {"igst": 71900, "cgst": 38500, "sgst": 38500},
                "4_D_Ineligible": {
                    "sec_17_5": {"igst": 0, "cgst": 18000, "sgst": 18000},
                    "others": {"igst": 0, "cgst": 0, "sgst": 0}
                }
            },
            "5_Exempt": {
                "exempt_nil": {"inter": 0, "intra": 45000},
                "non_gst": {"inter": 0, "intra": 60000}
            },
            "5_1_Interest": {
                "interest": {"igst": 0, "cgst": 0, "sgst": 0, "cess": 0},
                "late_fee": {"cgst": 0, "sgst": 0}
            },
            "6_1_Payment": {
                "igst": {"payable": 107100, "itc_igst": 71900, "itc_cgst": 0, "itc_sgst": 0, "cash": 35200},
                "cgst": {"payable": 78300, "itc_igst": 0, "itc_cgst": 38500, "itc_sgst": 0, "cash": 39800},
                "sgst": {"payable": 78300, "itc_igst": 0, "itc_cgst": 0, "itc_sgst": 38500, "cash": 39800},
                "cess": {"payable": 0, "itc_igst": 0, "itc_cgst": 0, "itc_sgst": 0, "cash": 0},
                "total_payable": 114800,
                "ledger_balance": 50000,
                "top_up_required": 64800
            }
        },
        "filing_meta": {
            "due_date": "2026-04-20",
            "filing_status": "AWAITING_FUNDS",
            "records_processed": 20,
            "sales_count": 6,
            "purchase_count": 14
        }
    }


@pytest.fixture
def empty_graph_state():
    """Minimal empty state dict for graph-level tests."""
    return {
        "current_period": "2026-03",
        "days_to_cutoff": 20,
        "books_data": [],
        "gstr2a_live_data": [],
        "gstr2b_static_data": [],
        "mismatches": [],
        "vendor_chase_log": [],
        "itc_recommendations": [],
        "financial_context": {},
        "gstr3b_draft": {},
        "final_gstr3b": {},
        "hitl_flag": False,
        "workflow_status": ""
    }
