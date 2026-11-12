"""Fail-closed product/report-role contract for six synthetic desktop smokes.

The real smoke runner already checks the temporary report bytes. This helper
ensures those bytes belong to each application's expected *report roles* rather
than merely accepting the correct number of unrelated files. Source-only
assertion; NOT a Windows binary release, signing, or QD-approval gate.
"""
from __future__ import annotations

import re
from pathlib import Path

# In emission order: the two premium inventories must end in a .txt manifest.
# These stems are the real engine outpath/save and bundle naming contracts.
SMOKE_REPORT_ROLES: dict[str, tuple[tuple[str, str], ...]] = {
    "ledger": (("ledger-diff", ".csv"),),
    "invoices": (("invoice-twins", ".csv"),),
    "spend": (("spend-map", ".csv"),),
    "policy": (("policy-delta", ".txt"),),
    "grants": (("grant-audit-exceptions", ".csv"),
               ("grant-budget-check", ".csv"),
               ("evidence-manifest", ".txt")),
    "procurement": (("procurement-three-way", ".csv"),
                    ("evidence-manifest", ".txt")),
}
_NATIVE_PATH = type(Path())
# Produced by engine.outpath: YYYYMMDD-HHMMSS-microseconds.
_STAMP = r"[0-9]{8}-[0-9]{6}-[0-9]{6}"


def verify_smoke_output_roles(app_id: object, outputs: object) -> None:
    """Reject unrelated, mislabeled, missing, or reordered synthetic reports.

    Do not call arbitrary path hooks or trust subclasses; reports are already
    checked for content and local provenance inside run_smoke. We inspect only
    immutable native Path.name and fixed product contracts, never data rows.
    """
    if type(app_id) is not str or app_id not in SMOKE_REPORT_ROLES:
        raise RuntimeError("Unknown desktop smoke application")
    roles = SMOKE_REPORT_ROLES[app_id]
    if type(outputs) is not list or len(outputs) != len(roles):
        raise RuntimeError("Incomplete desktop smoke report role set")
    for item, (stem, extension) in zip(outputs, roles):
        if type(item) is not _NATIVE_PATH:
            raise RuntimeError("Unsafe desktop smoke report reference")
        expected = rf"{re.escape(stem)}-{_STAMP}{re.escape(extension)}"
        if re.fullmatch(expected, item.name, flags=re.ASCII) is None:
            raise RuntimeError("Unexpected desktop smoke report role")
