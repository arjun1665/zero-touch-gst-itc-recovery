"""
Unit Tests — Filing Agent (agents/filling_agent.py)

Tests:
  • clean_currency() helper
  • compute_gstr3b_from_db() — table calculations (mocked MongoDB)
  • filing_agent() — end-to-end with mocked DB
"""
import pytest
from unittest.mock import patch, MagicMock
from agents.filling_agent import clean_currency


# ══════════════════════════════════════════════════════════════════════════════
# clean_currency()
# ══════════════════════════════════════════════════════════════════════════════

class TestCleanCurrency:
    """Currency string → float conversion."""

    def test_integer_passthrough(self):
        assert clean_currency(500) == 500.0

    def test_float_passthrough(self):
        assert clean_currency(123.45) == 123.45

    def test_string_with_rupee_symbol(self):
        assert clean_currency("₹50,000") == 50000.0

    def test_string_with_commas(self):
        assert clean_currency("1,00,000.50") == 100000.50

    def test_empty_string(self):
        assert clean_currency("") == 0.0

    def test_none_value(self):
        assert clean_currency(None) == 0.0

    def test_false_value(self):
        assert clean_currency(False) == 0.0

    def test_garbage_string(self):
        assert clean_currency("abc") == 0.0


# ══════════════════════════════════════════════════════════════════════════════
# compute_gstr3b_from_db() — mocked MongoDB queries
# ══════════════════════════════════════════════════════════════════════════════

class TestComputeGSTR3B:
    """Full GSTR-3B table computation from MongoDB data."""

    @patch("agents.filling_agent.erp_collection")
    def test_basic_computation(self, mock_erp, sample_erp_records, sample_optimizer_draft, sample_financial_context):
        from agents.filling_agent import compute_gstr3b_from_db
        mock_erp.find.return_value = sample_erp_records

        result = compute_gstr3b_from_db("2026-03", sample_optimizer_draft, sample_financial_context)

        assert result["period"] == "2026-03"
        assert "tables" in result
        assert "filing_meta" in result
        assert "generated_at" in result

    @patch("agents.filling_agent.erp_collection")
    def test_has_all_tables(self, mock_erp, sample_erp_records, sample_optimizer_draft, sample_financial_context):
        from agents.filling_agent import compute_gstr3b_from_db
        mock_erp.find.return_value = sample_erp_records

        result = compute_gstr3b_from_db("2026-03", sample_optimizer_draft, sample_financial_context)
        tables = result["tables"]

        expected_tables = ["3_1", "3_2", "4_ITC", "5_Exempt", "5_1_Interest", "6_1_Payment"]
        for t in expected_tables:
            assert t in tables, f"Missing table: {t}"

    @patch("agents.filling_agent.erp_collection")
    def test_empty_period_returns_zeroes(self, mock_erp):
        from agents.filling_agent import compute_gstr3b_from_db
        mock_erp.find.return_value = []

        result = compute_gstr3b_from_db("2026-01", {}, {})
        assert result["tables"]["6_1_Payment"]["total_payable"] == 0

    @patch("agents.filling_agent.erp_collection")
    def test_sales_output_tax_positive(self, mock_erp):
        """A single sale should produce positive output tax."""
        from agents.filling_agent import compute_gstr3b_from_db
        mock_erp.find.return_value = [{
            "Invoice_Number": "SALE-001", "Date": "2026-03-01",
            "Transaction_Type": "Sale", "Document_Type": "Invoice",
            "Taxable_Value": 100000, "IGST": 0, "CGST": 9000, "SGST": 9000,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": False, "ITC_Eligibility": "", "Import_Type": ""
        }]

        result = compute_gstr3b_from_db("2026-03", {}, {})
        t31 = result["tables"]["3_1"]["a"]
        assert t31["taxable_value"] == 100000
        assert t31["cgst"] == 9000
        assert t31["sgst"] == 9000

    @patch("agents.filling_agent.erp_collection")
    def test_rcm_shows_in_table_3_1_d(self, mock_erp):
        """RCM purchases should appear in Table 3.1(d)."""
        from agents.filling_agent import compute_gstr3b_from_db
        mock_erp.find.return_value = [{
            "Invoice_Number": "RCM-001", "Date": "2026-03-01",
            "Transaction_Type": "Purchase", "Document_Type": "Invoice",
            "Taxable_Value": 50000, "IGST": 0, "CGST": 4500, "SGST": 4500,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": True, "ITC_Eligibility": "Eligible", "Import_Type": ""
        }]

        result = compute_gstr3b_from_db("2026-03", {}, {})
        t31d = result["tables"]["3_1"]["d"]
        assert t31d["taxable_value"] == 50000
        assert t31d["cgst"] == 4500

    @patch("agents.filling_agent.erp_collection")
    def test_import_goods_in_table_4a1(self, mock_erp):
        from agents.filling_agent import compute_gstr3b_from_db
        mock_erp.find.return_value = [{
            "Invoice_Number": "IMP-001", "Date": "2026-03-06",
            "Transaction_Type": "Purchase", "Document_Type": "Bill of Entry",
            "Taxable_Value": 180000, "IGST": 32400, "CGST": 0, "SGST": 0,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": False, "ITC_Eligibility": "Eligible", "Import_Type": "goods"
        }]

        result = compute_gstr3b_from_db("2026-03", {}, {})
        assert result["tables"]["4_ITC"]["4_A"]["import_goods"]["igst"] == 32400

    @patch("agents.filling_agent.erp_collection")
    def test_blocked_sec17_5_in_table_4d(self, mock_erp):
        from agents.filling_agent import compute_gstr3b_from_db
        mock_erp.find.return_value = [{
            "Invoice_Number": "BLK-001", "Date": "2026-03-11",
            "Transaction_Type": "Purchase", "Document_Type": "Invoice",
            "Taxable_Value": 200000, "IGST": 0, "CGST": 18000, "SGST": 18000,
            "Supply_Type": "taxable", "Recipient_Type": "registered",
            "Is_RCM": False, "ITC_Eligibility": "Blocked_Sec17_5", "Import_Type": ""
        }]

        result = compute_gstr3b_from_db("2026-03", {}, {})
        t4d = result["tables"]["4_ITC"]["4_D_Ineligible"]["sec_17_5"]
        assert t4d["cgst"] == 18000
        assert t4d["sgst"] == 18000

    @patch("agents.filling_agent.erp_collection")
    def test_filing_meta_counts(self, mock_erp, sample_erp_records):
        from agents.filling_agent import compute_gstr3b_from_db
        mock_erp.find.return_value = sample_erp_records

        result = compute_gstr3b_from_db("2026-03", {}, {})
        meta = result["filing_meta"]
        assert meta["records_processed"] == len(sample_erp_records)
        assert meta["sales_count"] >= 0
        assert meta["purchase_count"] >= 0

    @patch("agents.filling_agent.erp_collection")
    def test_due_date_format(self, mock_erp):
        from agents.filling_agent import compute_gstr3b_from_db
        mock_erp.find.return_value = []

        result = compute_gstr3b_from_db("2026-03", {}, {})
        assert result["filing_meta"]["due_date"] == "2026-04-20"

    @patch("agents.filling_agent.erp_collection")
    def test_december_due_date(self, mock_erp):
        from agents.filling_agent import compute_gstr3b_from_db
        mock_erp.find.return_value = []

        result = compute_gstr3b_from_db("2026-12", {}, {})
        assert result["filing_meta"]["due_date"] == "2027-01-20"


# ══════════════════════════════════════════════════════════════════════════════
# filing_agent() — end-to-end with mocked DB
# ══════════════════════════════════════════════════════════════════════════════

class TestFilingAgent:
    """Integration-style test for the filing_agent function."""

    @patch("agents.filling_agent.gstr3b_collection")
    @patch("agents.filling_agent.erp_collection")
    @patch("agents.filling_agent.log_audit")
    def test_filing_agent_returns_final_gstr3b(self, mock_audit, mock_erp, mock_3b, sample_erp_records):
        from agents.filling_agent import filing_agent
        mock_erp.find.return_value = sample_erp_records

        state = {
            "current_period": "2026-03",
            "financial_context": {},
            "gstr3b_draft": {}
        }
        result = filing_agent(state)

        assert "final_gstr3b" in result
        assert result["final_gstr3b"]["period"] == "2026-03"
        mock_3b.delete_many.assert_called_once()
        mock_3b.insert_one.assert_called_once()
        mock_audit.assert_called()
