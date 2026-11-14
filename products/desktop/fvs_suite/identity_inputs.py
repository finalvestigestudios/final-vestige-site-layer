"""Native source identities and calendar text for private offline financial engines.

A direct Python caller can pass a str subclass or arbitrary object overriding
str(), upper(), or strip() to fabricate matching and date evidence. Only exact
built-in strings can reach these transforms. CSV behavior is unchanged.
Identity normalization is lossy; it is never proof of identity/compliance.
"""
from __future__ import annotations

import re
from datetime import datetime

_DATE_FORMATS = (
    (re.compile(r"[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}\Z"), "%Y-%m-%d"),
    (re.compile(r"[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}\Z"), "%m/%d/%Y"),
    (re.compile(r"[0-9]{1,2}/[0-9]{1,2}/[0-9]{2}\Z"), "%m/%d/%y"),
)
_DATE_ERROR = "Invalid date (use YYYY-MM-DD, MM/DD/YYYY, or MM/DD/YY)"
# The reusable direct API must not upper-case or regex-process a string larger
# than a sane source cell. Use the SpendMap native-cell ceiling; the shared CSV
# file reader's 64 MiB limit by itself does not bound a single identifier.
MAX_SOURCE_IDENTITY_CHARS = 1_048_576
_IDENTITY_BUDGET_ERROR = "Source identity text exceeds length limit"


def normalize_key(value: str) -> str:
    """Legacy ASCII matching key, with bounded native input and expansion.

    Unicode uppercasing can expand source text (e.g. sharp S to SS); reject
    such expansions before regex processing. Do not truncate identifiers:
    changing the key could conceal collisions requiring human review.
    """
    if type(value) is not str:
        raise ValueError("Invalid source identity text")
    if len(value) > MAX_SOURCE_IDENTITY_CHARS:
        raise ValueError(_IDENTITY_BUDGET_ERROR)
    upper = value.upper()
    if len(upper) > MAX_SOURCE_IDENTITY_CHARS:
        raise ValueError(_IDENTITY_BUDGET_ERROR)
    return re.sub(r"[^A-Z0-9]+", "", upper)


def parse_date(value: str):
    """Legacy ISO/US calendar parser; reject forged string objects first."""
    if type(value) is not str:
        raise ValueError(_DATE_ERROR)
    raw = value.strip()
    if not raw or len(raw) > 32:
        raise ValueError(_DATE_ERROR)
    for pattern, fmt in _DATE_FORMATS:
        if pattern.fullmatch(raw):
            try:
                return datetime.strptime(raw, fmt).date()
            except ValueError:
                break
    raise ValueError(_DATE_ERROR)
