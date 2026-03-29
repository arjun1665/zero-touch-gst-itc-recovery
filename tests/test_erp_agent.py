"""
Unit Tests — ERP Agent (agents/erp_agent.py)

Tests:
  • Period parsing
  • Safe ITC calculation with mismatches
  • Financial context integration
"""
import pytest
from unittest.mock import patch


class TestERPAgent:
    @patch("agents.erp_agent.log_audit")
    @patch("agents.erp_agent.get_raw_erp_inventory")
    def test_returns_financial_context(self, mock_inv, mock_audit):
        from agents.erp_agent import erp_agent
        mock_inv.return_value = [
            {"Invoice_Number": "INV-001", "Date": "2026-03-02",
             "Transaction_Type": "Purchase", "Document_Type": "Invoice",
             "IGST": 12000, "CGST": 0, "SGST": 0, "Is_RCM": "FALSE"}
        ]
        result = erp_agent({"current_period": "2026-03", "mismatches": []})
        assert "financial_context" in result
        assert isinstance(result["financial_context"], dict)

    @patch("agents.erp_agent.log_audit")
    @patch("agents.erp_agent.get_raw_erp_inventory")
    def test_mismatches_reduce_itc(self, mock_inv, mock_audit):
        from agents.erp_agent import erp_agent
        # Use lowercase 'invoice_number' key to match erp_agent's lookup
        mock_inv.return_value = [
            {"invoice_number": "INV-001", "Invoice_Number": "INV-001",
             "Date": "2026-03-02",
             "Transaction_Type": "Purchase", "Document_Type": "Invoice",
             "IGST": 12000, "CGST": 0, "SGST": 0, "Is_RCM": "FALSE"}
        ]
        result = erp_agent({
            "current_period": "2026-03",
            "mismatches": [{"invoice_number": "INV-001", "issue": "Missing", "tax_amount": 12000}]
        })
        assert result["total_validated_itc"] == 0.0

    @patch("agents.erp_agent.log_audit")
    @patch("agents.erp_agent.get_raw_erp_inventory")
    def test_default_period_on_bad_input(self, mock_inv, mock_audit):
        from agents.erp_agent import erp_agent
        mock_inv.return_value = []
        result = erp_agent({"current_period": "bad", "mismatches": []})
        assert "financial_context" in result

    @patch("agents.erp_agent.log_audit")
    @patch("agents.erp_agent.get_raw_erp_inventory")
    def test_books_data_returned(self, mock_inv, mock_audit):
        from agents.erp_agent import erp_agent
        records = [{"Invoice_Number": "X", "Date": "2026-03-01",
                     "Transaction_Type": "Sale", "IGST": 0, "CGST": 100,
                     "SGST": 100, "Is_RCM": "FALSE", "Document_Type": "Invoice"}]
        mock_inv.return_value = records
        result = erp_agent({"current_period": "2026-03", "mismatches": []})
        assert result["books_data"] == records

    @patch("agents.erp_agent.log_audit")
    @patch("agents.erp_agent.get_raw_erp_inventory")
    def test_audit_logged(self, mock_inv, mock_audit):
        from agents.erp_agent import erp_agent
        mock_inv.return_value = []
        erp_agent({"current_period": "2026-03", "mismatches": []})
        mock_audit.assert_called_once()
