"""R356: independently validate original SpendMap CSV money before custom parsers.

The direct summarizer accepts pluggable parse_money callbacks; a callback must
not turn an imported source amount into a different financial fact. Keep the
same lexical rules and HALF_UP cent rounding as the shared engine.money CSV
importer. This is a source-value consistency check, not source authentication.
"""
from __future__ import annotations

from decimal import Context, Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
import re

_SOURCE_AMOUNT = re.compile(
    r"(?P<prefix>(?:[+-]?\$|\$[+-]?|[+-]?))"
    r"(?P<number>(?:(?:[0-9]{1,3}(?:,[0-9]{3})+)|[0-9]+)(?:\.[0-9]*)?|\.[0-9]+)\Z"
)
_CENT = Decimal("0.01")
_MAX_SOURCE = Decimal("1000000000000")


def canonical_spend_source_cents(raw: str) -> Decimal:
    """Return exact imported cents or raise ValueError without revealing raw."""
    if type(raw) is not str:
        raise ValueError("Invalid original spend amount format")
    clean = raw.strip()
    if not clean or len(clean) > 80:
        raise ValueError("Invalid original spend amount format")
    in_parentheses = clean.startswith("(") or clean.endswith(")")
    if in_parentheses:
        if not (clean.startswith("(") and clean.endswith(")")):
            raise ValueError("Invalid original spend amount format")
        clean = clean[1:-1].strip()
    match = _SOURCE_AMOUNT.fullmatch(clean)
    if match is None:
        raise ValueError("Invalid original spend amount format")
    prefix = match.group("prefix")
    if in_parentheses and ("+" in prefix or "-" in prefix):
        raise ValueError("Invalid original spend amount format")
    try:
        amount = Decimal(match.group("number").replace(",", ""))
    except InvalidOperation:
        raise ValueError("Invalid original spend amount format") from None
    if not amount.is_finite() or amount > _MAX_SOURCE:
        raise ValueError("Invalid original spend amount range")
    if in_parentheses or "-" in prefix:
        amount = amount.copy_negate()
    # The shared CSV importer rounds inputs to cents (ROUND_HALF_UP). Even if
    # the caller poisoned decimal.getcontext(), no rounding mode may leak in.
    with localcontext(Context(prec=64)):
        return amount.quantize(_CENT, rounding=ROUND_HALF_UP)


def spend_parser_preserves_source(source_cents: Decimal, parsed: object) -> bool:
    """Compare exact cents; sign on zero is meaningful original evidence."""
    return (type(parsed) is Decimal and parsed.is_finite()
            and parsed == source_cents
            and (not source_cents.is_zero()
                 or parsed.is_signed() == source_cents.is_signed()))
