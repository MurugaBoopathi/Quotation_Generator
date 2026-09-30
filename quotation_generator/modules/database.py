"""SQLite persistence for generated quotations (Stage 4: history & dashboard)."""
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from config import DATABASE_FILE

SCHEMA = """
CREATE TABLE IF NOT EXISTS quotations (
    quotation_number TEXT PRIMARY KEY,
    quotation_date TEXT NOT NULL,
    financial_year TEXT,
    customer_name TEXT,
    customer_organisation TEXT,
    vehicle_number TEXT,
    tax_type TEXT,
    subtotal TEXT NOT NULL,
    cgst TEXT NOT NULL,
    sgst TEXT NOT NULL,
    igst TEXT NOT NULL,
    round_off TEXT NOT NULL,
    grand_total TEXT NOT NULL,
    pdf_path TEXT,
    generated_at TEXT NOT NULL
);
"""


@contextmanager
def get_connection():
    DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DATABASE_FILE))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(SCHEMA)


def quotation_exists(quotation_number: str) -> bool:
    init_db()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM quotations WHERE quotation_number = ?", (quotation_number,)
        ).fetchone()
        return row is not None


def get_quotation(quotation_number: str) -> Optional[dict]:
    init_db()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM quotations WHERE quotation_number = ?", (quotation_number,)
        ).fetchone()
        return dict(row) if row else None


def save_quotation(record: dict, overwrite: bool = False) -> None:
    """Insert (or, if explicitly allowed, replace) a quotation history record."""
    init_db()
    if not overwrite and quotation_exists(record["quotation_number"]):
        raise ValueError(
            f"Quotation number '{record['quotation_number']}' already exists in history."
        )

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO quotations (
                quotation_number, quotation_date, financial_year, customer_name,
                customer_organisation, vehicle_number, tax_type, subtotal, cgst, sgst,
                igst, round_off, grand_total, pdf_path, generated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(quotation_number) DO UPDATE SET
                quotation_date=excluded.quotation_date,
                financial_year=excluded.financial_year,
                customer_name=excluded.customer_name,
                customer_organisation=excluded.customer_organisation,
                vehicle_number=excluded.vehicle_number,
                tax_type=excluded.tax_type,
                subtotal=excluded.subtotal,
                cgst=excluded.cgst,
                sgst=excluded.sgst,
                igst=excluded.igst,
                round_off=excluded.round_off,
                grand_total=excluded.grand_total,
                pdf_path=excluded.pdf_path,
                generated_at=excluded.generated_at
            """,
            (
                record["quotation_number"],
                record["quotation_date"],
                record.get("financial_year", ""),
                record.get("customer_name", ""),
                record.get("customer_organisation", ""),
                record.get("vehicle_number", ""),
                record.get("tax_type", ""),
                str(record["subtotal"]),
                str(record["cgst"]),
                str(record["sgst"]),
                str(record["igst"]),
                str(record["round_off"]),
                str(record["grand_total"]),
                record.get("pdf_path", ""),
                record.get("generated_at", datetime.now().isoformat(timespec="seconds")),
            ),
        )


def list_quotations(
    search_number: str = "",
    customer_name: str = "",
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> list:
    init_db()
    query = "SELECT * FROM quotations WHERE 1=1"
    params = []

    if search_number:
        query += " AND quotation_number LIKE ?"
        params.append(f"%{search_number}%")
    if customer_name:
        query += " AND (customer_name LIKE ? OR customer_organisation LIKE ?)"
        params.extend([f"%{customer_name}%", f"%{customer_name}%"])
    if date_from:
        query += " AND quotation_date >= ?"
        params.append(date_from.isoformat())
    if date_to:
        query += " AND quotation_date <= ?"
        params.append(date_to.isoformat())

    query += " ORDER BY generated_at DESC"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def get_dashboard_stats() -> dict:
    init_db()
    all_rows = list_quotations()
    total_count = len(all_rows)
    total_value = sum((Decimal(row["grand_total"]) for row in all_rows), Decimal("0"))

    today = date.today()
    this_month_count = sum(
        1 for row in all_rows
        if row["quotation_date"][:7] == f"{today.year:04d}-{today.month:02d}"
    )
    recent = all_rows[:5]

    return {
        "total_count": total_count,
        "total_value": total_value,
        "this_month_count": this_month_count,
        "recent": recent,
    }
