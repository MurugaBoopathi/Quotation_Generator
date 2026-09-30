"""Unit tests for modules.calculations — verified against the two reference quotations."""
import unittest
from decimal import Decimal

from modules.calculations import (
    LineItem, TAX_INTER_STATE, TAX_INTRA_STATE, calculate_item_amount, calculate_totals,
)


class TestItemAmount(unittest.TestCase):
    def test_amount_is_quantity_times_rate(self):
        self.assertEqual(calculate_item_amount(2, "150.50"), Decimal("301.00"))

    def test_amount_with_decimal_quantity(self):
        self.assertEqual(calculate_item_amount("1.5", "100"), Decimal("150.00"))


class TestIntraStateGst(unittest.TestCase):
    def test_cgst_sgst_split_evenly(self):
        items = [LineItem("Widget", Decimal(18), "10 Days", Decimal(1), "Nos", Decimal(1000))]
        totals = calculate_totals(items, TAX_INTRA_STATE)
        self.assertEqual(totals.cgst, Decimal("90.00"))
        self.assertEqual(totals.sgst, Decimal("90.00"))
        self.assertEqual(totals.igst, Decimal("0.00"))


class TestInterStateGst(unittest.TestCase):
    def test_igst_applied_in_full(self):
        items = [LineItem("Widget", Decimal(18), "10 Days", Decimal(1), "Nos", Decimal(1000))]
        totals = calculate_totals(items, TAX_INTER_STATE)
        self.assertEqual(totals.igst, Decimal("180.00"))
        self.assertEqual(totals.cgst, Decimal("0.00"))
        self.assertEqual(totals.sgst, Decimal("0.00"))


class TestRoundOff(unittest.TestCase):
    def test_round_off_positive(self):
        items = [LineItem("Widget", Decimal(18), "10 Days", Decimal(1), "Nos", Decimal("100.30"))]
        totals = calculate_totals(items, TAX_INTRA_STATE)
        expected_grand_total = (Decimal("100.30") * Decimal("1.18")).quantize(Decimal("1"))
        self.assertEqual(totals.grand_total, expected_grand_total.quantize(Decimal("0.01")))

    def test_round_off_zero_when_already_whole(self):
        items = [LineItem("Widget", Decimal(18), "10 Days", Decimal(1), "Nos", Decimal(100))]
        totals = calculate_totals(items, TAX_INTRA_STATE)
        self.assertEqual(totals.round_off, Decimal("0.00"))


class TestSampleQuotations(unittest.TestCase):
    def test_sample_quotation_1(self):
        items = [
            LineItem("Item A", Decimal(18), "10 Days", Decimal(1), "Nos", Decimal(600), sl_no=1),
            LineItem("Item B", Decimal(18), "10 Days", Decimal(1), "Nos", Decimal(1500), sl_no=2),
            LineItem("Item C", Decimal(18), "10 Days", Decimal(1), "Nos", Decimal(360), sl_no=3),
            LineItem("Item D", Decimal(18), "10 Days", Decimal(1), "Nos", Decimal(1000), sl_no=4),
        ]
        totals = calculate_totals(items, TAX_INTRA_STATE)
        self.assertEqual(totals.subtotal, Decimal("3460.00"))
        self.assertEqual(totals.cgst, Decimal("311.40"))
        self.assertEqual(totals.sgst, Decimal("311.40"))
        self.assertEqual(totals.round_off, Decimal("0.20"))
        self.assertEqual(totals.grand_total, Decimal("4083.00"))

    def test_sample_quotation_2(self):
        items = [
            LineItem("Throttle", Decimal(18), "10 Days", Decimal(1), "Nos", Decimal(600), sl_no=1),
            LineItem("Labour Charges", Decimal(18), "10 Days", Decimal(1), "Nos", Decimal(1000), sl_no=2),
            LineItem("Throttle Connector Pin", Decimal(18), "10 Days", Decimal(1), "Nos", Decimal(300), sl_no=3),
        ]
        totals = calculate_totals(items, TAX_INTRA_STATE)
        self.assertEqual(totals.subtotal, Decimal("1900.00"))
        self.assertEqual(totals.cgst, Decimal("171.00"))
        self.assertEqual(totals.sgst, Decimal("171.00"))
        self.assertEqual(totals.round_off, Decimal("0.00"))
        self.assertEqual(totals.grand_total, Decimal("2242.00"))


if __name__ == "__main__":
    unittest.main()
