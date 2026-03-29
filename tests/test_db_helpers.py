"""
Unit Tests — db_schema.py helpers

Tests:
  • safe_float() — type coercion edge cases
  • log_audit() — audit entry structure (mocked DB)
  • get_raw_erp_inventory() — error handling (mocked DB)
"""
import pytest
from unittest.mock import patch, MagicMock
from db_schema import safe_float


# ══════════════════════════════════════════════════════════════════════════════
# safe_float() — identical logic to gst_engine but different function
# ══════════════════════════════════════════════════════════════════════════════

class TestDBSafeFloat:
    """Cover all branches of the db_schema.safe_float helper."""

    def test_none(self):
        assert safe_float(None) == 0.0

    def test_valid_float(self):
        assert safe_float("25000.50") == 25000.50

    def test_integer_value(self):
        assert safe_float(100) == 100.0

    def test_empty_string(self):
        assert safe_float("") == 0.0

    def test_false_string(self):
        assert safe_float("FALSE") == 0.0

    def test_true_string(self):
        assert safe_float("TRUE") == 0.0

    def test_na_string(self):
        assert safe_float("N/A") == 0.0

    def test_none_string(self):
        assert safe_float("NONE") == 0.0

    def test_garbage(self):
        assert safe_float("abc") == 0.0

    def test_custom_default(self):
        assert safe_float(None, default=99.0) == 99.0

    def test_whitespace(self):
        assert safe_float("  500  ") == 500.0

    def test_negative(self):
        assert safe_float("-1000") == -1000.0

    def test_zero(self):
        assert safe_float("0") == 0.0
        assert safe_float(0) == 0.0


# ══════════════════════════════════════════════════════════════════════════════
# log_audit() — mocked MongoDB
# ══════════════════════════════════════════════════════════════════════════════

class TestLogAudit:
    """Verify audit log entries are structured correctly."""

    @patch("db_schema.audit_collection")
    def test_log_audit_inserts_entry(self, mock_collection):
        from db_schema import log_audit
        log_audit("Test_Agent", "TEST_ACTION", {"key": "value"})
        mock_collection.insert_one.assert_called_once()
        call_args = mock_collection.insert_one.call_args[0][0]
        assert call_args["agent"] == "Test_Agent"
        assert call_args["action"] == "TEST_ACTION"
        assert call_args["details"] == {"key": "value"}
        assert "timestamp" in call_args

    @patch("db_schema.audit_collection")
    def test_log_audit_with_string_details(self, mock_collection):
        from db_schema import log_audit
        log_audit("Agent_X", "SYNC", "Some plain text")
        call_args = mock_collection.insert_one.call_args[0][0]
        assert call_args["details"] == "Some plain text"


# ══════════════════════════════════════════════════════════════════════════════
# get_raw_erp_inventory() — mocked MongoDB
# ══════════════════════════════════════════════════════════════════════════════

class TestGetRawERPInventory:
    """ERP inventory fetching with error handling."""

    @patch("db_schema.db")
    def test_returns_list(self, mock_db):
        from db_schema import get_raw_erp_inventory
        mock_db.__getitem__.return_value.find.return_value = [
            {"Invoice_Number": "INV-001", "IGST": 5000}
        ]
        result = get_raw_erp_inventory()
        assert isinstance(result, list)
        assert len(result) == 1

    @patch("db_schema.db")
    def test_returns_empty_on_error(self, mock_db):
        from db_schema import get_raw_erp_inventory
        mock_db.__getitem__.return_value.find.side_effect = Exception("Connection failed")
        result = get_raw_erp_inventory()
        assert result == []
