"""Unit tests for modules.validators."""
import unittest
from datetime import date
from unittest.mock import patch

from modules.validators import is_duplicate_quotation_number, validate_quotation


def _valid_quotation():
    return {
        "quotation_number": "ASE-Q-001-26-27",
        "quotation_date": date(2026, 9, 15),
        "customer": {"name": "The President"},
        "items": [
            {"description": "Throttle", "quantity": 1, "rate": 600, "gst_rate": 18},
        ],
    }


class TestValidateQuotation(unittest.TestCase):
    def test_valid_quotation_has_no_errors(self):
        self.assertEqual(validate_quotation(_valid_quotation()), [])

    def test_missing_quotation_number(self):
        quotation = _valid_quotation()
        quotation["quotation_number"] = ""
        errors = validate_quotation(quotation)
        self.assertIn("Quotation Number is required.", errors)

    def test_invalid_quotation_date(self):
        quotation = _valid_quotation()
        quotation["quotation_date"] = "not-a-date"
        errors = validate_quotation(quotation)
        self.assertTrue(any("Quotation Date" in e for e in errors))

    def test_missing_customer_name(self):
        quotation = _valid_quotation()
        quotation["customer"] = {"name": ""}
        errors = validate_quotation(quotation)
        self.assertIn("Customer / Buyer Name is required.", errors)

    def test_at_least_one_item_required(self):
        quotation = _valid_quotation()
        quotation["items"] = []
        errors = validate_quotation(quotation)
        self.assertIn("At least one line item is required.", errors)

    def test_negative_quantity_rejected(self):
        quotation = _valid_quotation()
        quotation["items"][0]["quantity"] = -1
        errors = validate_quotation(quotation)
        self.assertTrue(any("Quantity must be a positive number" in e for e in errors))

    def test_negative_rate_rejected(self):
        quotation = _valid_quotation()
        quotation["items"][0]["rate"] = -5
        errors = validate_quotation(quotation)
        self.assertTrue(any("Rate must be zero or a positive number" in e for e in errors))

    def test_invalid_gst_rate_rejected(self):
        quotation = _valid_quotation()
        quotation["items"][0]["gst_rate"] = 150
        errors = validate_quotation(quotation)
        self.assertTrue(any("GST Rate must be between 0 and 100" in e for e in errors))


class TestDuplicateQuotationNumber(unittest.TestCase):
    @patch("modules.database.quotation_exists", return_value=True)
    def test_detects_existing_number(self, _mock):
        self.assertTrue(is_duplicate_quotation_number("ASE-Q-001-26-27"))

    @patch("modules.database.quotation_exists", return_value=False)
    def test_returns_false_for_new_number(self, _mock):
        self.assertFalse(is_duplicate_quotation_number("ASE-Q-999-26-27"))


if __name__ == "__main__":
    unittest.main()
