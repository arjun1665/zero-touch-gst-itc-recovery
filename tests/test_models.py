"""
Unit Tests — State Models (Pydantic + TypedDict)

Tests the data models in state.py for:
  • Correct instantiation & defaults
  • Field type enforcement via Pydantic
  • Edge cases: negative values, empty strings, missing fields
"""
import pytest
from state import Invoice, MismatchRecord, ITCRecommendation


# ══════════════════════════════════════════════════════════════════════════════
# Invoice Model
# ══════════════════════════════════════════════════════════════════════════════

class TestInvoiceModel:
    """Invoice Pydantic model validation."""

    def test_valid_invoice_creation(self):
        inv = Invoice(
            invoice_number="INV-001",
            vendor_gstin="27AADCB2230M1Z2",
            date="2026-03-01",
            amount=50000.0,
            tax_amount=9000.0,
            type="Purchase"
        )
        assert inv.invoice_number == "INV-001"
        assert inv.tax_amount == 9000.0
        assert inv.status == "filed"  # default

    def test_invoice_default_status(self):
        inv = Invoice(
            invoice_number="INV-002",
            vendor_gstin="29BBBCB1120K1Z5",
            date="2026-03-05",
            amount=100000.0,
            tax_amount=18000.0,
            type="Sale"
        )
        assert inv.status == "filed"

    def test_invoice_custom_status(self):
        inv = Invoice(
            invoice_number="INV-003",
            vendor_gstin="29BBBCB1120K1Z5",
            date="2026-03-05",
            amount=100000.0,
            tax_amount=18000.0,
            type="Sale",
            status="pending"
        )
        assert inv.status == "pending"

    def test_invoice_zero_amount(self):
        inv = Invoice(
            invoice_number="INV-ZERO",
            vendor_gstin="29X",
            date="2026-03-01",
            amount=0.0,
            tax_amount=0.0,
            type="Sale"
        )
        assert inv.amount == 0.0
        assert inv.tax_amount == 0.0

    def test_invoice_negative_amount(self):
        """Credit notes may have negative amounts."""
        inv = Invoice(
            invoice_number="CN-001",
            vendor_gstin="29X",
            date="2026-03-01",
            amount=-5000.0,
            tax_amount=-900.0,
            type="Credit_Note"
        )
        assert inv.amount < 0
        assert inv.tax_amount < 0

    def test_invoice_missing_required_field(self):
        with pytest.raises(Exception):
            Invoice(invoice_number="INV-FAIL", vendor_gstin="29X")

    def test_invoice_serialization(self):
        inv = Invoice(
            invoice_number="INV-SER",
            vendor_gstin="29X",
            date="2026-03-01",
            amount=10000.0,
            tax_amount=1800.0,
            type="Purchase"
        )
        data = inv.model_dump()
        assert isinstance(data, dict)
        assert data["invoice_number"] == "INV-SER"
        assert "status" in data


# ══════════════════════════════════════════════════════════════════════════════
# MismatchRecord Model
# ══════════════════════════════════════════════════════════════════════════════

class TestMismatchRecordModel:
    """MismatchRecord Pydantic model validation."""

    def test_critical_mismatch(self):
        m = MismatchRecord(
            invoice_number="INV-102",
            vendor_gstin="24DDDCB4450M1Z1",
            issue_type="Missing from GSTR-2B",
            tax_value=21600.0,
            is_critical=True
        )
        assert m.is_critical is True
        assert m.tax_value == 21600.0

    def test_non_critical_mismatch(self):
        m = MismatchRecord(
            invoice_number="INV-088",
            vendor_gstin="07CCDCB3340L1Z8",
            issue_type="Value Mismatch",
            tax_value=500.0,
            is_critical=False
        )
        assert m.is_critical is False

    def test_mismatch_zero_tax(self):
        m = MismatchRecord(
            invoice_number="INV-ZZZ",
            vendor_gstin="29X",
            issue_type="Trivial difference",
            tax_value=0.0,
            is_critical=False
        )
        assert m.tax_value == 0.0

    def test_mismatch_serialization(self):
        m = MismatchRecord(
            invoice_number="INV-001",
            vendor_gstin="27X",
            issue_type="Missing",
            tax_value=5000.0,
            is_critical=True
        )
        data = m.model_dump()
        assert set(data.keys()) == {"invoice_number", "vendor_gstin", "issue_type", "tax_value", "is_critical"}


# ══════════════════════════════════════════════════════════════════════════════
# ITCRecommendation Model
# ══════════════════════════════════════════════════════════════════════════════

class TestITCRecommendationModel:
    """ITCRecommendation Pydantic model validation."""

    def test_claim_recommendation(self):
        r = ITCRecommendation(
            invoice_number="INV-001",
            action="CLAIM",
            reasoning="Fully compliant under Section 16",
            financial_impact=50000.0
        )
        assert r.action == "CLAIM"
        assert r.financial_impact == 50000.0

    def test_defer_recommendation(self):
        r = ITCRecommendation(
            invoice_number="INV-088",
            action="DEFER",
            reasoning="Variance detected — risk of penalty",
            financial_impact=-8500.0
        )
        assert r.action == "DEFER"
        assert r.financial_impact < 0

    def test_recommendation_missing_fields(self):
        with pytest.raises(Exception):
            ITCRecommendation(invoice_number="INV-X")
