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


def normalize_key(value: str) -> str:
    """Legacy ASCII matching key with no caller-defined conversion hooks."""
    if type(value) is not str:
        raise ValueError("Invalid source identity text")
    return re.sub(r"[^A-Z0-9]+", "", value.upper())


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
