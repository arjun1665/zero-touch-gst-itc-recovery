"""
Unit Tests — PDF Service (pdf_service.py)

Tests:
  • fmt() — currency formatting
  • generate_gstr3b_pdf() — PDF file creation, non-empty, valid path
  • Edge case: empty/missing table data
"""
import os
import pytest
from pdf_service import fmt, generate_gstr3b_pdf


# ══════════════════════════════════════════════════════════════════════════════
# fmt() — Currency formatter
# ══════════════════════════════════════════════════════════════════════════════

class TestFmt:
    """Indian currency display formatting."""

    def test_positive_value(self):
        assert fmt(50000) == "Rs.50,000.00"

    def test_zero_returns_fallback(self):
        assert fmt(0) == "—"

    def test_none_returns_fallback(self):
        assert fmt(None) == "—"

    def test_custom_fallback(self):
        assert fmt(0, fallback="N/A") == "N/A"
        assert fmt(None, fallback="N/A") == "N/A"

    def test_decimal_precision(self):
        result = fmt(12345.678)
        assert "12,345.68" in result

    def test_small_value(self):
        result = fmt(0.01)
        assert "0.01" in result

    def test_large_value(self):
        result = fmt(10000000)
        assert "Rs." in result

    def test_negative_value(self):
        result = fmt(-5000)
        assert "-" in result


# ══════════════════════════════════════════════════════════════════════════════
# generate_gstr3b_pdf() — PDF file creation
# ══════════════════════════════════════════════════════════════════════════════

class TestPDFGeneration:
    """End-to-end PDF generation tests."""

    def test_pdf_file_is_created(self, sample_gstr3b_output):
        pdf_path = generate_gstr3b_pdf(sample_gstr3b_output)
        assert os.path.exists(pdf_path)
        assert pdf_path.endswith(".pdf")

    def test_pdf_file_is_not_empty(self, sample_gstr3b_output):
        pdf_path = generate_gstr3b_pdf(sample_gstr3b_output)
        assert os.path.getsize(pdf_path) > 0

    def test_pdf_filename_contains_period(self, sample_gstr3b_output):
        pdf_path = generate_gstr3b_pdf(sample_gstr3b_output)
        assert "2026-03" in os.path.basename(pdf_path)

    def test_pdf_with_empty_tables(self):
        """PDF should still generate with empty/default data."""
        minimal_data = {
            "period": "2026-01",
            "tables": {},
            "filing_meta": {}
        }
        pdf_path = generate_gstr3b_pdf(minimal_data)
        assert os.path.exists(pdf_path)
        assert os.path.getsize(pdf_path) > 0

    def test_pdf_with_zero_values(self):
        """All zero values should produce valid PDF with '—' fallbacks."""
        zero_data = {
            "period": "2026-02",
            "tables": {
                "3_1": {"a": {"taxable_value": 0, "igst": 0, "cgst": 0, "sgst": 0, "cess": 0}},
                "3_2": {"unregistered": {"taxable_value": 0, "igst": 0}},
                "4_ITC": {},
                "5_Exempt": {},
                "5_1_Interest": {},
                "6_1_Payment": {"total_payable": 0}
            },
            "filing_meta": {"due_date": "2026-03-20", "filing_status": "DRAFT"}
        }
        pdf_path = generate_gstr3b_pdf(zero_data)
        assert os.path.exists(pdf_path)

    def test_pdf_cleanup(self, sample_gstr3b_output):
        """Verify we can generate multiple PDFs (idempotent)."""
        path1 = generate_gstr3b_pdf(sample_gstr3b_output)
        path2 = generate_gstr3b_pdf(sample_gstr3b_output)
        assert os.path.exists(path1)
        assert os.path.exists(path2)
        # Same period = same path (overwritten)
        assert path1 == path2
