"""R357: verify SpendMap formatted money against its exact Decimal evidence.

User-provided display callbacks are not allowed to replace financial facts.
This validates display strings without rounding, stringifying private source
values in errors, or treating a human review flag as an approval decision.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
import re

# ASCII-only, unambiguous fixed-point output. Accounting parentheses and $ are
# accepted as display options; exponents, formula prefixes and extra fractional
# digits are not. Two cents precision prevents a rounded string masking source.
_DISPLAY_NUMBER = re.compile(
    r"(?P<prefix>(?:[+-]?\$|\$[+-]?|[+-]?))"
    r"(?P<number>(?:[0-9]{1,3}(?:,[0-9]{3})+|[0-9]+)(?:\.[0-9]{1,2})?)\Z"
)
_ERROR = "Invalid SpendMap monetary display; no report was saved"


def verified_spend_money_display(amount: Decimal, text: object) -> str:
    """Return original display only if it expresses exactly ``amount``.

    Sign-of-zero is retained as evidence. No float conversion, implicit
    ROUND_HALF_UP, locale guessing, trimming or caller-controlled error text.
    """
    if type(amount) is not Decimal or not amount.is_finite():
        raise ValueError(_ERROR)
    if type(text) is not str or not text or len(text) > 80:
        raise ValueError(_ERROR)

    accounting = text.startswith("(") or text.endswith(")")
    value_text = text
    if accounting:
        if not (text.startswith("(") and text.endswith(")")):
            raise ValueError(_ERROR)
        value_text = text[1:-1]
    match = _DISPLAY_NUMBER.fullmatch(value_text)
    if match is None:
        raise ValueError(_ERROR)
    prefix = match.group("prefix")
    if accounting and ("+" in prefix or "-" in prefix):
        raise ValueError(_ERROR)
    try:
        displayed = Decimal(match.group("number").replace(",", ""))
    except InvalidOperation:
        raise ValueError(_ERROR) from None
    if accounting or "-" in prefix:
        displayed = displayed.copy_negate()
    if displayed != amount or (amount.is_zero() and displayed.is_signed() != amount.is_signed()):
        raise ValueError(_ERROR)
    return text
