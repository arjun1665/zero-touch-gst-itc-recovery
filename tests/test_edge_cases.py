"""
Edge Case & Stress Tests

Tests boundary conditions, malformed data, and unusual inputs that
could cause silent failures in production.
"""
import pytest
from gst_engine import EnterpriseGSTEngine
from agents.filling_agent import clean_currency
from pdf_service import fmt


class TestEdgeCaseGSTEngine:
    """Boundary conditions for the GST engine."""

    @pytest.fixture
    def engine(self):
        return EnterpriseGSTEngine()

    def test_massive_tax_value(self, engine):
        records = [{
            "Invoice_Number": "BIG-001", "Date": "2026-03-01",
            "Transaction_Type": "Sale", "Document_Type": "Invoice",
            "IGST": 999999999.99, "CGST": 0, "SGST": 0, "Is_RCM": False
        }]
        result = engine.process_erp_data(records, 3, 2026)
        assert result["current_output_tax"] == 999999999.99

    def test_all_fields_missing(self, engine):
        records = [{}]
        result = engine.process_erp_data(records, 3, 2026)
        assert result["records_processed"] == 1
        assert result["current_output_tax"] == 0.0

    def test_missing_date_key(self, engine):
        records = [{"Transaction_Type": "Sale", "IGST": 1000, "CGST": 0, "SGST": 0, "Is_RCM": False}]
        result = engine.process_erp_data(records, 3, 2026)
        assert result["current_output_tax"] == 0.0

    def test_hundred_records(self, engine):
        records = [{
            "Invoice_Number": f"INV-{i}", "Date": "2026-03-15",
            "Transaction_Type": "Sale", "Document_Type": "Invoice",
            "IGST": 100, "CGST": 0, "SGST": 0, "Is_RCM": False
        } for i in range(100)]
        result = engine.process_erp_data(records, 3, 2026)
        assert result["records_processed"] == 100
        assert result["current_output_tax"] == 10000.0

    def test_mixed_string_and_numeric_tax(self, engine):
        records = [{
            "Invoice_Number": "MIX-001", "Date": "2026-03-01",
            "Transaction_Type": "Sale", "Document_Type": "Invoice",
            "IGST": "₹5,000", "CGST": 0, "SGST": "1000", "Is_RCM": "FALSE"
        }]
        result = engine.process_erp_data(records, 3, 2026)
        assert result["current_output_tax"] == 6000.0

    def test_leap_year_date(self, engine):
        records = [{
            "Invoice_Number": "LEAP-001", "Date": "2028-02-29",
            "Transaction_Type": "Sale", "Document_Type": "Invoice",
            "IGST": 1000, "CGST": 0, "SGST": 0, "Is_RCM": False
        }]
        result = engine.process_erp_data(records, 2, 2028)
        assert result["current_output_tax"] == 1000.0


class TestEdgeCaseCleanCurrency:
    def test_string_zero(self):
        assert clean_currency("0") == 0.0

    def test_negative_with_symbol(self):
        assert clean_currency("₹-5,000") == -5000.0

    def test_bool_true(self):
        assert clean_currency(True) == 1.0

    def test_very_long_number(self):
        assert clean_currency("9" * 15) == float("9" * 15)


class TestEdgeCaseFmt:
    def test_very_small_nonzero(self):
        result = fmt(0.001)
        assert "Rs." in result

    def test_exactly_zero_float(self):
        assert fmt(0.0) == "—"

    def test_negative_large(self):
        result = fmt(-9999999)
        assert "-" in result
        assert "Rs." in result
