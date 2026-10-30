"""Fail-closed, privacy-safe GrantAudit claim-kind intake.

This tiny pure helper is deliberately independent of the filesystem and the
reconciliation engine. It must never echo a claim cell or an untrusted row
citation into an exception, GUI dialog, CI log, or support transcript.
"""
from __future__ import annotations

import re
from typing import Mapping

_PHYSICAL_ROW = re.compile(r"[1-9][0-9]{0,9}\Z", re.ASCII)


def claim_kind(row: Mapping[str, str]) -> str:
    """Classify explicit grant claims/credits without revealing private cells.

    Empty/missing claim_type retains the established ``claim`` default.
    CSV parser line references are surfaced only if their representation is
    canonical, positive ASCII decimal; caller-supplied labels cannot escape.
    This is input validation, *not* an eligibility or reimbursement decision.
    """
    value = str(row.get("claim_type", "claim") or "claim").strip().casefold()
    if value in {"claim", "credit"}:
        return value
    location = str(row.get("row", ""))
    safe_row = location if _PHYSICAL_ROW.fullmatch(location) else "?"
    raise ValueError(
        f"Unsupported claim_type at claim CSV physical row {safe_row}; "
        "use claim or credit"
    )
