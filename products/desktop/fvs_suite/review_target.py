"""Invalidate an implicit premium review report after an input edit or failed run.

A previous report is never silently reselected after the operator changes the
source, output, mapping or review policy. Historical reports remain available
through the explicit, entitlement-checked Browse action in the review window.
"""
from __future__ import annotations


def clear_auto_review_target(report_slot: list[str | None]) -> None:
    """Drop the implicit latest-report path, including before a failed attempt."""
    if type(report_slot) is not list or len(report_slot) != 1:
        raise ValueError("Invalid premium review target")
    report_slot[0] = None


def watch_auto_review_target(variables, report_slot: list[str | None]):
    """Bind Tk StringVar write traces to a fail-closed latest-report slot.

    Called after all UI variables exist. It deliberately never deletes or
    changes a prior report on disk: an operator can explicitly browse to one.
    """
    if type(variables) not in (list, tuple) or not variables:
        raise ValueError("Invalid premium review inputs")
    clear_auto_review_target(report_slot)

    def invalidate(*_tk_trace_arguments):
        clear_auto_review_target(report_slot)

    for variable in variables:
        variable.trace_add("write", invalidate)
    return invalidate
