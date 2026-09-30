"""Unit tests for modules.number_to_words."""
import unittest
from decimal import Decimal

from modules.number_to_words import amount_to_words


class TestAmountToWords(unittest.TestCase):
    def test_sample_quotation_1_total(self):
        self.assertEqual(
            amount_to_words(Decimal("4083.00")), "Rupees Four Thousand Eighty-Three Only"
        )

    def test_sample_quotation_2_total(self):
        self.assertEqual(
            amount_to_words(Decimal("2242.00")),
            "Rupees Two Thousand Two Hundred Forty-Two Only",
        )

    def test_zero(self):
        self.assertEqual(amount_to_words(Decimal("0")), "Rupees Zero Only")

    def test_with_paise(self):
        self.assertEqual(
            amount_to_words(Decimal("100.50")), "Rupees One Hundred and Fifty Paise Only"
        )

    def test_lakh_and_crore(self):
        self.assertEqual(
            amount_to_words(Decimal("10000000.00")), "Rupees One Crore Only"
        )
        self.assertEqual(
            amount_to_words(Decimal("100000.00")), "Rupees One Lakh Only"
        )


if __name__ == "__main__":
    unittest.main()
