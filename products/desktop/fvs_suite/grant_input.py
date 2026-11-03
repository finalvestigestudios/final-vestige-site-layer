"""Fail-closed, privacy-safe GrantAudit claim-kind intake.

This tiny pure helper is deliberately independent of the filesystem and the
reconciliation engine. It must never echo a claim cell or an untrusted row
citation into an exception, GUI dialog, CI log, or support transcript.
"""
from __future__ import annotations

import re
from typing import Mapping

from .event_custody import snapshot_event_record

_PHYSICAL_ROW = re.compile(r"[1-9][0-9]{0,9}\Z", re.ASCII)


def claim_kind(row: Mapping[str, str]) -> str:
    """Classify explicit grant claims/credits without revealing private cells.

    Empty/missing claim_type retains the established ``claim`` default.
    CSV parser line references are surfaced only if their representation is
    canonical, positive ASCII decimal; caller-supplied labels cannot escape.
    This is input validation, *not* an eligibility or reimbursement decision.
    """
    # Classify the actual stored claim_type, not a fabricated dict.get()
    # view. Never invoke source-controlled __str__ while selecting the type.
    owned = snapshot_event_record(row, family="Grant")
    raw = owned.get("claim_type", "claim")
    if raw is None or (type(raw) is str and raw == ""):
        raw = "claim"
    if type(raw) is not str:
        raise ValueError("Grant claim_type must be plain text")
    value = raw.strip().casefold()
    if value in {"claim", "credit"}:
        return value
    location = owned.get("row", "")
    safe_row = (location if type(location) is str
                and _PHYSICAL_ROW.fullmatch(location) and location != "1" else "?")
    raise ValueError(
        f"Unsupported claim_type at claim CSV physical row {safe_row}; "
        "use claim or credit"
    )
