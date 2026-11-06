"""Pure row geometry for the five non-Ledger Windows desktop forms.

At high DPI the old 65-character entries plus Browse buttons exceeded the
viewport. Independent rows keep the native Tk Tab order and allow the parent
canvas to give each entry its available width. This module reads no input,
paths, entitlements, or financial data; visual acceptance still needs Windows.
"""
from __future__ import annotations

_INPUT_COUNTS = {
    "invoices": 1,
    "spend": 1,
    "policy": 2,
    "grants": 3,
    "procurement": 3,
}
_PREMIUM = frozenset(("grants", "procurement"))


def standard_stacked_rows(app_id: str, input_count: int) -> dict[str, object]:
    """Return deterministic, nonoverlapping rows for input/edit/action controls.

    All controls are created in document order; row placement must not hide
    Browse, policy picker, or review buttons below high-DPI input entries.
    The existing LedgerDiff-specific plan remains its own verified contract.
    """
    if (type(app_id) is not str or app_id not in _INPUT_COUNTS
            or type(input_count) is not int
            or input_count != _INPUT_COUNTS[app_id]):
        raise ValueError("Unexpected desktop form inventory")

    start = 3  # Title/description/pre-release notice own rows 0..2.
    inputs = tuple((start + 3 * i, start + 3 * i + 1, start + 3 * i + 2)
                   for i in range(input_count))
    row = start + 3 * input_count
    plan: dict[str, object] = {"inputs": inputs}
    if app_id == "invoices":
        plan["window"] = (row, row + 1)
        row += 2
    plan["output"] = (row, row + 1, row + 2)
    row += 3
    if app_id == "procurement":
        plan["rules"] = (row, row + 1, row + 2)
        row += 3
    plan["status"] = row
    plan["generate"] = row + 1
    if app_id in _PREMIUM:
        plan["review"] = row + 2
        row += 1
    plan["disclaimer"] = row + 2
    plan["hint"] = row + 3
    return plan
