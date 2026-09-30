"""Field-level and cross-record validation helpers used by the Create Quotation form."""
import re
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import List

QUOTATION_NUMBER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9/\-]*$")


def validate_quotation(quotation: dict) -> List[str]:
    """Return a list of human-readable validation error messages (empty if valid)."""
    errors: List[str] = []

    quotation_number = quotation.get("quotation_number", "").strip()
    if not quotation_number:
        errors.append("Quotation Number is required.")
    elif not QUOTATION_NUMBER_PATTERN.match(quotation_number):
        errors.append(
            "Quotation Number may only contain letters, digits, '-' and '/' characters."
        )

    if not isinstance(quotation.get("quotation_date"), date):
        errors.append("Quotation Date is invalid.")

    customer = quotation.get("customer", {})
    if not customer.get("name", "").strip():
        errors.append("Customer / Buyer Name is required.")

    items = quotation.get("items", [])
    if not items:
        errors.append("At least one line item is required.")

    for idx, item in enumerate(items, start=1):
        if not str(item.get("description", "")).strip():
            errors.append(f"Item {idx}: Description is required.")

        is_labour = str(item.get("type", "Regular")).strip().lower() == "labour"

        try:
            qty = Decimal(str(item.get("quantity", "0")))
        except (InvalidOperation, ValueError):
            qty = None
        if not is_labour and (qty is None or qty <= 0):
            errors.append(f"Item {idx}: Quantity must be a positive number.")

        try:
            rate = Decimal(str(item.get("rate", "0")))
        except (InvalidOperation, ValueError):
            rate = None
        if rate is None or rate < 0:
            errors.append(f"Item {idx}: Rate must be zero or a positive number.")

        try:
            gst_rate = Decimal(str(item.get("gst_rate", "0")))
        except (InvalidOperation, ValueError):
            gst_rate = None
        if gst_rate is None or gst_rate < 0 or gst_rate > 100:
            errors.append(f"Item {idx}: GST Rate must be between 0 and 100.")

    return errors


def is_duplicate_quotation_number(quotation_number: str) -> bool:
    """Check quotation history (SQLite) for an existing quotation with this number."""
    from modules.database import quotation_exists  # local import avoids a hard DB dependency for callers that don't need it

    return quotation_exists(quotation_number.strip())

