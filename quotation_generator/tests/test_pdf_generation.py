"""Unit test for PDF generation: renders a quotation and sanity-checks the output file."""
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from modules.calculations import LineItem, TAX_INTRA_STATE, calculate_totals
from modules.pdf_generator import generate_quotation_pdf

COMPANY = {
    "company_name": "Aayam Sustainable Energy Private Limited",
    "address": "No. 133D, H.P. Bunk Thottam, Jothipuram, Coimbatore North, Periyanaickenpalayam, Coimbatore - 641047",
    "cin": "U27101TZ2025PTC036168",
    "gstin": "33ABDCA8409J1ZO",
    "pan": "ABDCA8409J",
    "email": "aayamse@gmail.com",
    "state_name": "Tamil Nadu",
    "state_code": "33",
    "authorised_signatory": "Authorised Signatory",
}


class TestPdfGeneration(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_generates_non_empty_pdf(self):
        items = [
            LineItem("Throttle", Decimal(18), "10 Days", Decimal(1), "Nos", Decimal(600), sl_no=1),
            LineItem("Labour Charges", Decimal(18), "10 Days", Decimal(1), "Nos", Decimal(1000), sl_no=2),
            LineItem("Throttle Connector Pin", Decimal(18), "10 Days", Decimal(1), "Nos", Decimal(300), sl_no=3),
        ]
        totals = calculate_totals(items, TAX_INTRA_STATE)
        quotation = {
            "quotation_number": "ASE-Q-TEST-26-27",
            "quotation_date": date(2026, 9, 15),
            "buyer_ref": "", "other_ref": "", "payment_terms": "", "delivery_terms": "",
            "despatch_through": "", "destination": "", "remarks": "",
            "customer": {"name": "The President", "organisation": "Thriuvettanallur Village Panchayat"},
            "delivery": None,
            "vehicle_number": "Yellow",
            "tax_type": "intra",
        }
        output_path = Path(self._tmpdir.name) / "test_quotation.pdf"

        result_path = generate_quotation_pdf(COMPANY, quotation, items, totals, output_path)

        self.assertTrue(result_path.exists())
        content = result_path.read_bytes()
        self.assertGreater(len(content), 0)
        self.assertTrue(content.startswith(b"%PDF"))

    def test_raises_on_missing_output_directory_permissions(self):
        # A path whose parent does not exist should surface a clear error rather than silently fail.
        items = [LineItem("Item", Decimal(18), "10 Days", Decimal(1), "Nos", Decimal(100), sl_no=1)]
        totals = calculate_totals(items, TAX_INTRA_STATE)
        quotation = {
            "quotation_number": "ASE-Q-TEST-2-26-27",
            "quotation_date": date(2026, 9, 15),
            "customer": {"name": "Test Customer"},
            "delivery": None,
            "tax_type": "intra",
        }
        bad_path = Path(self._tmpdir.name) / "missing_dir" / "test.pdf"
        with self.assertRaises(OSError):
            generate_quotation_pdf(COMPANY, quotation, items, totals, bad_path)


if __name__ == "__main__":
    unittest.main()
