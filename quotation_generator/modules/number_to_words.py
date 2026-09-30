"""Convert a rupee/paise amount to Indian-currency words."""
from decimal import Decimal

_ONES = [
    "", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
    "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
    "Seventeen", "Eighteen", "Nineteen",
]
_TENS = [
    "", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety",
]


def _two_digits_to_words(n: int) -> str:
    if n < 20:
        return _ONES[n]
    tens, ones = divmod(n, 10)
    return (_TENS[tens] + (f"-{_ONES[ones]}" if ones else "")).strip()


def _three_digits_to_words(n: int) -> str:
    hundred, rest = divmod(n, 100)
    parts = []
    if hundred:
        parts.append(f"{_ONES[hundred]} Hundred")
    if rest:
        parts.append(_two_digits_to_words(rest))
    return " ".join(parts)


def _integer_to_words(n: int) -> str:
    """Convert a non-negative integer to words using the Indian numbering system."""
    if n == 0:
        return "Zero"

    crore, n = divmod(n, 10_000_000)
    lakh, n = divmod(n, 100_000)
    thousand, n = divmod(n, 1000)
    hundred_part = n

    segments = []
    if crore:
        segments.append(f"{_integer_to_words(crore)} Crore")
    if lakh:
        segments.append(f"{_two_digits_to_words(lakh) if lakh < 100 else _three_digits_to_words(lakh)} Lakh")
    if thousand:
        segments.append(f"{_two_digits_to_words(thousand) if thousand < 100 else _three_digits_to_words(thousand)} Thousand")
    if hundred_part:
        segments.append(_three_digits_to_words(hundred_part))

    return " ".join(segments)


def amount_to_words(amount: Decimal) -> str:
    """Return an amount (rupees, optionally with paise) as Indian-currency words.

    Example: Decimal("4083.00") -> "Rupees Four Thousand Eighty-Three Only"
    """
    amount = Decimal(amount)
    if not amount.is_finite():
        amount = Decimal("0")
    amount = amount.quantize(Decimal("0.01"))
    rupees = int(amount)
    paise = int((amount - rupees) * 100)

    words = f"Rupees {_integer_to_words(rupees)}"
    if paise:
        words += f" and {_integer_to_words(paise)} Paise"
    words += " Only"
    return words
