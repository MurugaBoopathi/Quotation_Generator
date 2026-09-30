"""Unit tests for sequential quotation number generation (modules.quotation_form)."""
import tempfile
import unittest
from datetime import date
from pathlib import Path

import modules.quotation_form as quotation_form


class TestFinancialYearFor(unittest.TestCase):
    def test_date_in_first_half_of_calendar_year(self):
        self.assertEqual(quotation_form.financial_year_for(date(2026, 2, 15)), "25-26")

    def test_date_in_second_half_of_calendar_year(self):
        self.assertEqual(quotation_form.financial_year_for(date(2026, 9, 15)), "26-27")

    def test_date_on_fy_boundary(self):
        self.assertEqual(quotation_form.financial_year_for(date(2026, 4, 1)), "26-27")
        self.assertEqual(quotation_form.financial_year_for(date(2026, 3, 31)), "25-26")


class TestQuotationNumbering(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._original_seq_file = quotation_form.QUOTATION_SEQ_FILE
        quotation_form.QUOTATION_SEQ_FILE = Path(self._tmpdir.name) / "quotation_seq.json"

    def tearDown(self):
        quotation_form.QUOTATION_SEQ_FILE = self._original_seq_file
        self._tmpdir.cleanup()

    def test_first_number_for_new_financial_year(self):
        number = quotation_form.peek_next_quotation_number("ASE-Q", "26-27")
        self.assertEqual(number, "ASE-Q-001-26-27")

    def test_peek_does_not_consume_sequence(self):
        first_peek = quotation_form.peek_next_quotation_number("ASE-Q", "26-27")
        second_peek = quotation_form.peek_next_quotation_number("ASE-Q", "26-27")
        self.assertEqual(first_peek, second_peek)

    def test_commit_advances_sequence(self):
        quotation_form.commit_quotation_number("ASE-Q", "26-27")
        self.assertEqual(
            quotation_form.peek_next_quotation_number("ASE-Q", "26-27"), "ASE-Q-002-26-27"
        )

    def test_sequences_are_independent_per_financial_year(self):
        quotation_form.commit_quotation_number("ASE-Q", "26-27")
        self.assertEqual(
            quotation_form.peek_next_quotation_number("ASE-Q", "27-28"), "ASE-Q-001-27-28"
        )


if __name__ == "__main__":
    unittest.main()
