"""Exact money handling. Amounts are Decimal, max 2 decimal places (pesewas)."""
from decimal import Decimal, InvalidOperation

from .errors import SusuError

CENT = Decimal("0.01")


def parse_money(value) -> Decimal:
    """Convert str/int/Decimal to a valid positive 2dp Decimal.

    Floats are rejected on purpose: 0.1 + 0.2 != 0.3 in binary floating point.
    """
    if isinstance(value, float) or isinstance(value, bool):
        raise SusuError("Amount must be given as text or Decimal, not float.")
    try:
        amount = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        raise SusuError(f"'{value}' is not a valid amount.")
    if not amount.is_finite():
        raise SusuError(f"'{value}' is not a valid amount.")
    if amount <= 0:
        raise SusuError("Amount must be greater than zero.")
    if amount != amount.quantize(CENT):
        raise SusuError("Amount can have at most 2 decimal places.")
    return amount.quantize(CENT)


def fmt(amount: Decimal) -> str:
    return f"{amount:.2f}"
