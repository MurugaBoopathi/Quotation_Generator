"""GST and totals calculation engine. All money math uses Decimal, never float."""
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import List, Optional

from modules.number_to_words import amount_to_words

TAX_INTRA_STATE = "intra"
TAX_INTER_STATE = "inter"

TWO_PLACES = Decimal("0.01")


def to_decimal(value) -> Decimal:
    """Safely convert a value (str/int/float/Decimal) to Decimal, defaulting to 0."""
    if isinstance(value, Decimal):
        return value if value.is_finite() else Decimal("0")
    try:
        result = Decimal(str(value))
        return result if result.is_finite() else Decimal("0")
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0")


@dataclass
class LineItem:
    description: str
    gst_rate: Decimal
    due_on: str
    quantity: Decimal
    unit: str
    rate: Decimal
    sl_no: int = 0

    @property
    def amount(self) -> Decimal:
        qty = to_decimal(self.quantity)
        rate = to_decimal(self.rate)
        # Labour-type items: when quantity is 0 or blank, the rate IS the amount.
        if qty == 0:
            return rate.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        return (qty * rate).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    @property
    def cgst_amount(self) -> Decimal:
        return (self.amount * to_decimal(self.gst_rate) / 2 / 100).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    @property
    def sgst_amount(self) -> Decimal:
        return self.cgst_amount

    @property
    def igst_amount(self) -> Decimal:
        return (self.amount * to_decimal(self.gst_rate) / 100).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


@dataclass
class QuotationTotals:
    subtotal: Decimal
    cgst: Decimal
    sgst: Decimal
    igst: Decimal
    round_off: Decimal
    grand_total: Decimal
    amount_in_words: str


def calculate_item_amount(quantity, rate) -> Decimal:
    """Amount = Quantity x Rate, rounded to 2 decimal places."""
    return (to_decimal(quantity) * to_decimal(rate)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def calculate_totals(
    items: List[LineItem],
    tax_type: str = TAX_INTRA_STATE,
    rounding: str = ROUND_HALF_UP,
) -> QuotationTotals:
    """Compute subtotal, GST (CGST+SGST or IGST) and rounded grand total for a quotation."""
    subtotal = sum((item.amount for item in items), Decimal("0"))

    if tax_type == TAX_INTER_STATE:
        igst = sum((item.igst_amount for item in items), Decimal("0"))
        cgst = Decimal("0")
        sgst = Decimal("0")
    else:
        cgst = sum((item.cgst_amount for item in items), Decimal("0"))
        sgst = sum((item.sgst_amount for item in items), Decimal("0"))
        igst = Decimal("0")

    unrounded_total = subtotal + cgst + sgst + igst
    grand_total = unrounded_total.quantize(Decimal("1"), rounding=rounding)
    round_off = (grand_total - unrounded_total).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    return QuotationTotals(
        subtotal=subtotal.quantize(TWO_PLACES),
        cgst=cgst.quantize(TWO_PLACES),
        sgst=sgst.quantize(TWO_PLACES),
        igst=igst.quantize(TWO_PLACES),
        round_off=round_off,
        grand_total=grand_total.quantize(TWO_PLACES),
        amount_in_words=amount_to_words(grand_total),
    )
