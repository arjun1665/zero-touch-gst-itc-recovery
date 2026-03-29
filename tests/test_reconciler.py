"""
Unit Tests — Reconciler Agent (agents/reconciler.py)

Tests:
  • safe_float in reconciler module
  • run_reconciliation logic — goods not received, blocked, missing from 2B, value mismatch
  • watcher_agent — passthrough
  • reconciliation_agent with mocked DB
"""
import pytest
from unittest.mock import patch, MagicMock


# ══════════════════════════════════════════════════════════════════════════════
# Reconciler safe_float
# ══════════════════════════════════════════════════════════════════════════════

class TestReconcilerSafeFloat:
    def test_basic_conversion(self):
        from agents.reconciler import safe_float
        assert safe_float("5000") == 5000.0

    def test_none_returns_default(self):
        from agents.reconciler import safe_float
        assert safe_float(None) == 0.0

    def test_boolean_strings(self):
        from agents.reconciler import safe_float
        assert safe_float("FALSE") == 0.0
        assert safe_float("TRUE") == 0.0


# ══════════════════════════════════════════════════════════════════════════════
# Reconciliation logic — mocked DB + mock GSTN
# ══════════════════════════════════════════════════════════════════════════════

class TestRunReconciliation:
    """Test reconciliation mismatch detection with mocked data sources."""

    @patch("agents.reconciler.load_erp_purchases_from_mongo")
    @patch("agents.reconciler.mock_gstr2b_payload", [
        {"invoice_number": "INV-001", "igst": 0, "cgst": 25000, "sgst": 25000},
    ])
    def test_matched_invoice_no_mismatch(self, mock_load):
        from agents.reconciler import run_reconciliation
        mock_load.return_value = [{
            "invoice_number": "INV-001",
            "vendor_name": "Test",
            "gstin": "27X",
            "tax_amount": 50000,
            "goods_received": True,
            "itc_eligibility": "Eligible",
            "is_rcm": False,
        }]
        mismatches = run_reconciliation("2026-03")
        assert len(mismatches) == 0

    @patch("agents.reconciler.load_erp_purchases_from_mongo")
    @patch("agents.reconciler.mock_gstr2b_payload", [])
    def test_missing_from_gstr2b(self, mock_load):
        from agents.reconciler import run_reconciliation
        mock_load.return_value = [{
            "invoice_number": "INV-GHOST",
            "vendor_name": "Ghost Vendor",
            "gstin": "27X",
            "tax_amount": 10000,
            "goods_received": True,
            "itc_eligibility": "Eligible",
            "is_rcm": False,
        }]
        mismatches = run_reconciliation("2026-03")
        assert len(mismatches) == 1
        assert "Missing" in mismatches[0]["issue"]

    @patch("agents.reconciler.load_erp_purchases_from_mongo")
    @patch("agents.reconciler.mock_gstr2b_payload", [])
    def test_goods_not_received_blocks_itc(self, mock_load):
        from agents.reconciler import run_reconciliation
        mock_load.return_value = [{
            "invoice_number": "INV-UNDELIVERED",
            "vendor_name": "Slow Corp",
            "gstin": "29X",
            "tax_amount": 5000,
            "goods_received": False,
            "itc_eligibility": "Eligible",
            "is_rcm": False,
        }]
        mismatches = run_reconciliation("2026-03")
        assert len(mismatches) == 1
        assert "Goods not received" in mismatches[0]["issue"]

    @patch("agents.reconciler.load_erp_purchases_from_mongo")
    @patch("agents.reconciler.mock_gstr2b_payload", [])
    def test_blocked_sec17_5(self, mock_load):
        from agents.reconciler import run_reconciliation
        mock_load.return_value = [{
            "invoice_number": "INV-BLOCKED",
            "vendor_name": "Club Service",
            "gstin": "29X",
            "tax_amount": 18000,
            "goods_received": True,
            "itc_eligibility": "Blocked_Sec17_5",
            "is_rcm": False,
        }]
        mismatches = run_reconciliation("2026-03")
        assert len(mismatches) == 1
        assert "17(5)" in mismatches[0]["issue"]

    @patch("agents.reconciler.load_erp_purchases_from_mongo")
    @patch("agents.reconciler.mock_gstr2b_payload", [])
    def test_rcm_skipped(self, mock_load):
        from agents.reconciler import run_reconciliation
        mock_load.return_value = [{
            "invoice_number": "INV-RCM",
            "vendor_name": "Legal Co",
            "gstin": "27X",
            "tax_amount": 4500,
            "goods_received": True,
            "itc_eligibility": "Eligible",
            "is_rcm": True,
        }]
        mismatches = run_reconciliation("2026-03")
        assert len(mismatches) == 0

    @patch("agents.reconciler.load_erp_purchases_from_mongo")
    @patch("agents.reconciler.mock_gstr2b_payload", [
        {"invoice_number": "INV-V", "igst": 1000, "cgst": 0, "sgst": 0},
    ])
    def test_value_mismatch_detected(self, mock_load):
        from agents.reconciler import run_reconciliation
        mock_load.return_value = [{
            "invoice_number": "INV-V",
            "vendor_name": "MismatchCo",
            "gstin": "29X",
            "tax_amount": 5000,
            "goods_received": True,
            "itc_eligibility": "Eligible",
            "is_rcm": False,
        }]
        mismatches = run_reconciliation("2026-03")
        assert len(mismatches) == 1
        assert "Value Mismatch" in mismatches[0]["issue"]

    @patch("agents.reconciler.load_erp_purchases_from_mongo")
    @patch("agents.reconciler.mock_gstr2b_payload", [
        {"invoice_number": "INV-CLOSE", "igst": 4998, "cgst": 0, "sgst": 0},
    ])
    def test_small_difference_within_threshold(self, mock_load):
        """Difference ≤ ₹5 should NOT be flagged."""
        from agents.reconciler import run_reconciliation
        mock_load.return_value = [{
            "invoice_number": "INV-CLOSE",
            "vendor_name": "CloseMatch",
            "gstin": "29X",
            "tax_amount": 5000,
            "goods_received": True,
            "itc_eligibility": "Eligible",
            "is_rcm": False,
        }]
        mismatches = run_reconciliation("2026-03")
        assert len(mismatches) == 0


# ══════════════════════════════════════════════════════════════════════════════
# Watcher Agent — simple passthrough
# ══════════════════════════════════════════════════════════════════════════════

class TestWatcherAgent:
    def test_returns_current_period(self):
        from agents.reconciler import watcher_agent
        state = {"current_period": "2026-03"}
        result = watcher_agent(state)
        assert result["current_period"] == "2026-03"

    def test_default_period(self):
        from agents.reconciler import watcher_agent
        result = watcher_agent({})
        assert result["current_period"] == "2026-03"
