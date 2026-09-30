"""Unit tests for modules.database (SQLite quotation history)."""
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

import modules.database as database


def _sample_record(number="ASE-Q-001-26-27"):
    return {
        "quotation_number": number,
        "quotation_date": "2026-09-15",
        "financial_year": "26-27",
        "customer_name": "The President",
        "customer_organisation": "Thriuvettanallur Village Panchayat",
        "vehicle_number": "Yellow",
        "tax_type": "intra",
        "subtotal": Decimal("1900.00"),
        "cgst": Decimal("171.00"),
        "sgst": Decimal("171.00"),
        "igst": Decimal("0.00"),
        "round_off": Decimal("0.00"),
        "grand_total": Decimal("2242.00"),
        "pdf_path": "output/ASE-Q-001-26-27.pdf",
    }


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self._original_db_file = database.DATABASE_FILE
        database.DATABASE_FILE = Path(self._tmpdir.name) / "quotations.db"

    def tearDown(self):
        database.DATABASE_FILE = self._original_db_file
        self._tmpdir.cleanup()

    def test_save_and_retrieve_quotation(self):
        database.save_quotation(_sample_record())
        row = database.get_quotation("ASE-Q-001-26-27")
        self.assertIsNotNone(row)
        self.assertEqual(row["grand_total"], "2242.00")

    def test_quotation_exists(self):
        self.assertFalse(database.quotation_exists("ASE-Q-001-26-27"))
        database.save_quotation(_sample_record())
        self.assertTrue(database.quotation_exists("ASE-Q-001-26-27"))

    def test_duplicate_insert_without_overwrite_raises(self):
        database.save_quotation(_sample_record())
        with self.assertRaises(ValueError):
            database.save_quotation(_sample_record())

    def test_duplicate_insert_with_overwrite_updates_record(self):
        database.save_quotation(_sample_record())
        updated = _sample_record()
        updated["grand_total"] = Decimal("5000.00")
        database.save_quotation(updated, overwrite=True)
        row = database.get_quotation("ASE-Q-001-26-27")
        self.assertEqual(row["grand_total"], "5000.00")

    def test_list_quotations_filters_by_customer(self):
        database.save_quotation(_sample_record("ASE-Q-001-26-27"))
        other = _sample_record("ASE-Q-002-26-27")
        other["customer_name"] = "Someone Else"
        database.save_quotation(other)

        results = database.list_quotations(customer_name="President")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["quotation_number"], "ASE-Q-001-26-27")

    def test_dashboard_stats(self):
        database.save_quotation(_sample_record("ASE-Q-001-26-27"))
        database.save_quotation(_sample_record("ASE-Q-002-26-27"))
        stats = database.get_dashboard_stats()
        self.assertEqual(stats["total_count"], 2)
        self.assertEqual(stats["total_value"], Decimal("4484.00"))


if __name__ == "__main__":
    unittest.main()
