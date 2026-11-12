"""Fail-closed source-smoke report multiplicity for all six desktop products.

The synthetic runner checks actual temporary output bytes before returning;
this boundary asserts its receipt contains the complete product-specific
report set. It does not prove Windows packaging or authorize publication.
"""
from __future__ import annotations

from pathlib import Path

from scripts.smoke_result_custody_r386 import checked_smoke_outputs

# Counts observed from fvs_suite.smoke.run_smoke and its engine contracts.
# Changing an engine's report set must require an explicit, reviewed update.
EXPECTED_REPORT_COUNTS = {
    "ledger": 1,
    "invoices": 1,
    "spend": 1,
    "policy": 1,
    "grants": 3,       # exceptions, budget, provenance manifest
    "procurement": 2,  # three-way exceptions, provenance
}


def checked_app_smoke_receipt(app_id: str, outputs: object) -> list[Path]:
    """Return a defensive snapshot only for a complete expected app receipt."""
    if type(app_id) is not str or app_id not in EXPECTED_REPORT_COUNTS:
        raise RuntimeError("Unknown desktop source smoke application")
    paths = checked_smoke_outputs(outputs)
    if len(paths) != EXPECTED_REPORT_COUNTS[app_id]:
        raise RuntimeError("Incomplete desktop source smoke report set")
    return paths
