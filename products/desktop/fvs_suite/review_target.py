"""Invalidate an implicit premium review report after an input edit or failed run.

A previous report is never silently reselected after the operator changes the
source, output, mapping or review policy. Historical reports remain available
through the explicit, entitlement-checked Browse action in the review window.
"""
from __future__ import annotations

from .premium_launch_proof import has_verified_premium_proof

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


def revalidate_or_revoke(authorize, clear_sensitive_view, *, product: str) -> bool:
    """Fail closed unless an exact product-bound entitlement was reverified.

    The product is mandatory. Every premium caller supplies its expected
    native product ID; no unscoped/truthy compatibility route exists. The
    trusted callback verifies the current license Ed25519 signature, expiry
    and product on EVERY action; this function checks only the result shape.
    Exceptions deny without revealing private paths. Scrub failures propagate.
    """
    if not callable(authorize) or not callable(clear_sensitive_view):
        raise ValueError("Invalid premium authorization callbacks")
    if type(product) is not str or product not in ("grants", "procurement"):
        clear_sensitive_view()
        return False
    try:
        from .offline_entitlement import Entitlement
        permitted = has_verified_premium_proof(authorize(), product, Entitlement)
    except Exception:
        permitted = False
    if not permitted:
        clear_sensitive_view()
    return permitted
