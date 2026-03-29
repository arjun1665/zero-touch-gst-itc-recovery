"""
Mock GSTN Tests

Tests the mock government portal data and API router.
"""
import pytest


class TestMockGSTNData:
    def test_payload_has_invoices(self):
        from mock_gstn.mock_gstn import mock_gstr2b_payload
        assert isinstance(mock_gstr2b_payload, list)
        assert len(mock_gstr2b_payload) > 0

    def test_each_record_has_required_fields(self):
        from mock_gstn.mock_gstn import mock_gstr2b_payload
        required = {"invoice_number", "vendor_gstin", "igst", "cgst", "sgst"}
        for record in mock_gstr2b_payload:
            for field in required:
                assert field in record, f"Missing '{field}' in {record}"

    def test_tax_values_are_numeric(self):
        from mock_gstn.mock_gstn import mock_gstr2b_payload
        for record in mock_gstr2b_payload:
            assert isinstance(record["igst"], (int, float))
            assert isinstance(record["cgst"], (int, float))
            assert isinstance(record["sgst"], (int, float))

    def test_invoice_numbers_unique(self):
        from mock_gstn.mock_gstn import mock_gstr2b_payload
        inv_nums = [r["invoice_number"] for r in mock_gstr2b_payload]
        assert len(inv_nums) == len(set(inv_nums))

    def test_deliberate_mismatch_present(self):
        """INV-2026-088 has intentionally wrong value for testing."""
        from mock_gstn.mock_gstn import mock_gstr2b_payload
        inv88 = next(r for r in mock_gstr2b_payload if r["invoice_number"] == "INV-2026-088")
        assert inv88["igst"] == 8500  # Vendor filed 8500 instead of real value

    def test_missing_invoice_for_reconciliation(self):
        """INV-2026-102 should NOT be in the payload (vendor didn't file)."""
        from mock_gstn.mock_gstn import mock_gstr2b_payload
        inv_nums = [r["invoice_number"] for r in mock_gstr2b_payload]
        assert "INV-2026-102" not in inv_nums
