"""
Unit Tests — GST Engine (gst_engine.py)

Tests the EnterpriseGSTEngine for:
  • safe_float conversion (currency symbols, None, booleans, etc.)
  • process_erp_data tax calculation (output tax, ITC, accrued liability)
  • generate_financial_context (net payable, strategy indicator)
  • Edge cases: empty records, bad dates, December rollover
"""
import pytest
from gst_engine import EnterpriseGSTEngine


@pytest.fixture
def engine():
    return EnterpriseGSTEngine()


# ══════════════════════════════════════════════════════════════════════════════
# safe_float()
# ══════════════════════════════════════════════════════════════════════════════

class TestSafeFloat:
    """Cover every branch of the safe_float helper."""

    def test_none_returns_zero(self, engine):
        assert engine.safe_float(None) == 0.0

    def test_numeric_string(self, engine):
        assert engine.safe_float("12345.67") == 12345.67

    def test_integer(self, engine):
        assert engine.safe_float(500) == 500.0

    def test_float_passthrough(self, engine):
        assert engine.safe_float(99.99) == 99.99

    def test_currency_symbol_removal(self, engine):
        assert engine.safe_float("₹1,00,000") == 100000.0

    def test_commas_removed(self, engine):
        assert engine.safe_float("50,000.50") == 50000.50

    def test_boolean_false(self, engine):
        assert engine.safe_float("FALSE") == 0.0

    def test_boolean_true(self, engine):
        assert engine.safe_float("TRUE") == 0.0

    def test_empty_string(self, engine):
        assert engine.safe_float("") == 0.0

    def test_na_string(self, engine):
        assert engine.safe_float("NA") == 0.0

    def test_none_string(self, engine):
        assert engine.safe_float("None") == 0.0

    def test_garbage_string(self, engine):
        assert engine.safe_float("abc") == 0.0

    def test_whitespace_padding(self, engine):
        assert engine.safe_float("  500  ") == 500.0

    def test_negative_value(self, engine):
        assert engine.safe_float("-1250.50") == -1250.50


# ══════════════════════════════════════════════════════════════════════════════
# process_erp_data()
# ══════════════════════════════════════════════════════════════════════════════

class TestProcessERPData:
    """Tax computation from ERP records."""

    def test_empty_records(self, engine):
        result = engine.process_erp_data([], current_month=3, current_year=2026)
        assert result["records_processed"] == 0
        assert result["current_output_tax"] == 0.0
        assert result["total_books_itc"] == 0.0

    def test_single_sale(self, engine):
        records = [{
            "Invoice_Number": "SALE-001", "Date": "2026-03-01",
            "Transaction_Type": "Sale", "Document_Type": "Invoice",
            "IGST": 0, "CGST": 9000, "SGST": 9000,
            "Is_RCM": False
        }]
        result = engine.process_erp_data(records, current_month=3, current_year=2026)
        assert result["current_output_tax"] == 18000.0
        assert result["total_books_itc"] == 0.0

    def test_single_purchase(self, engine):
        records = [{
            "Invoice_Number": "INV-001", "Date": "2026-03-02",
            "Transaction_Type": "Purchase", "Document_Type": "Invoice",
            "IGST": 12000, "CGST": 0, "SGST": 0,
            "Is_RCM": False
        }]
        result = engine.process_erp_data(records, current_month=3, current_year=2026)
        assert result["current_output_tax"] == 0.0
        assert result["total_books_itc"] == 12000.0

    def test_rcm_purchase_adds_to_output_tax(self, engine):
        """RCM purchases create output tax liability, not ITC."""
        records = [{
            "Invoice_Number": "RCM-001", "Date": "2026-03-01",
            "Transaction_Type": "Purchase", "Document_Type": "Invoice",
            "IGST": 5400, "CGST": 0, "SGST": 0,
            "Is_RCM": True
        }]
        result = engine.process_erp_data(records, current_month=3, current_year=2026)
        assert result["current_output_tax"] == 5400.0
        assert result["total_books_itc"] == 0.0

    def test_credit_note_reduces_tax(self, engine):
        records = [{
            "Invoice_Number": "CN-001", "Date": "2026-03-01",
            "Transaction_Type": "Sale", "Document_Type": "Credit_Note",
            "IGST": 5000, "CGST": 0, "SGST": 0,
            "Is_RCM": False
        }]
        result = engine.process_erp_data(records, current_month=3, current_year=2026)
        assert result["current_output_tax"] == -5000.0

    def test_invalid_date_skipped(self, engine):
        records = [{
            "Invoice_Number": "BAD-001", "Date": "not-a-date",
            "Transaction_Type": "Sale", "Document_Type": "Invoice",
            "IGST": 1000, "CGST": 0, "SGST": 0,
            "Is_RCM": False
        }]
        result = engine.process_erp_data(records, current_month=3, current_year=2026)
        assert result["records_processed"] == 1
        # Should be skipped due to bad date
        assert result["current_output_tax"] == 0.0

    def test_out_of_period_not_counted(self, engine):
        """February records should not count for March."""
        records = [{
            "Invoice_Number": "OLD-001", "Date": "2026-02-28",
            "Transaction_Type": "Sale", "Document_Type": "Invoice",
            "IGST": 10000, "CGST": 0, "SGST": 0,
            "Is_RCM": False
        }]
        result = engine.process_erp_data(records, current_month=3, current_year=2026)
        assert result["current_output_tax"] == 0.0

    def test_accrued_next_month_tax(self, engine):
        """Sales in first 20 days of next month accrue to current."""
        records = [{
            "Invoice_Number": "FUT-001", "Date": "2026-04-10",
            "Transaction_Type": "Sale", "Document_Type": "Invoice",
            "IGST": 0, "CGST": 3000, "SGST": 3000,
            "Is_RCM": False
        }]
        result = engine.process_erp_data(records, current_month=3, current_year=2026)
        assert result["accrued_next_month_tax"] == 6000.0

    def test_december_to_january_rollover(self, engine):
        """December sales with January accrual."""
        records = [{
            "Invoice_Number": "JAN-001", "Date": "2027-01-05",
            "Transaction_Type": "Sale", "Document_Type": "Invoice",
            "IGST": 8000, "CGST": 0, "SGST": 0,
            "Is_RCM": False
        }]
        result = engine.process_erp_data(records, current_month=12, current_year=2026)
        assert result["accrued_next_month_tax"] == 8000.0

    def test_comprehensive_records(self, engine, sample_erp_records):
        result = engine.process_erp_data(sample_erp_records, current_month=3, current_year=2026)
        assert result["records_processed"] == len(sample_erp_records)
        assert result["current_output_tax"] > 0
        assert result["total_books_itc"] > 0


# ══════════════════════════════════════════════════════════════════════════════
# generate_financial_context()
# ══════════════════════════════════════════════════════════════════════════════

class TestFinancialContext:
    """Financial horizon analysis."""

    def test_stable_strategy(self, engine):
        summary = {"current_output_tax": 100000, "accrued_next_month_tax": 20000, "total_books_itc": 80000}
        ctx = engine.generate_financial_context(summary, total_validated_itc=80000)
        assert ctx["strategy_indicator"] == "STABLE"
        assert ctx["total_liability_horizon"] == 120000
        assert ctx["net_tax_payable_current"] == 20000

    def test_high_cash_required_strategy(self, engine):
        summary = {"current_output_tax": 500000, "accrued_next_month_tax": 300000, "total_books_itc": 100000}
        ctx = engine.generate_financial_context(summary, total_validated_itc=100000)
        # total_liability_horizon = 800000, which > 100000 * 1.5 = 150000
        assert ctx["strategy_indicator"] == "HIGH_CASH_REQUIRED"

    def test_zero_itc(self, engine):
        summary = {"current_output_tax": 50000, "accrued_next_month_tax": 0, "total_books_itc": 0}
        ctx = engine.generate_financial_context(summary, total_validated_itc=0)
        assert ctx["net_tax_payable_current"] == 50000

    def test_itc_exceeds_liability(self, engine):
        """When ITC > output tax, net payable should be 0 (no negative)."""
        summary = {"current_output_tax": 10000, "accrued_next_month_tax": 0, "total_books_itc": 50000}
        ctx = engine.generate_financial_context(summary, total_validated_itc=50000)
        assert ctx["net_tax_payable_current"] == 0

    def test_rounding(self, engine):
        summary = {"current_output_tax": 10000.555, "accrued_next_month_tax": 5000.333, "total_books_itc": 0}
        ctx = engine.generate_financial_context(summary, total_validated_itc=3000.111)
        assert ctx["total_liability_horizon"] == 15000.89
        assert ctx["total_validated_itc"] == 3000.11
