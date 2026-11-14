"""Invalidate an implicit premium review report after an input edit or failed run.

A previous report is never silently reselected after the operator changes the
source, output, mapping or review policy. Historical reports remain available
through the explicit, entitlement-checked Browse action in the review window.
"""
from __future__ import annotations

from .premium_launch_proof import has_verified_premium_proof

_LEGACY_UNSCOPED = object()


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


def revalidate_or_revoke(authorize, clear_sensitive_view, *,
                         product: object = _LEGACY_UNSCOPED) -> bool:
    """Require affirmative offline proof; scrub the visible review on denial.

    Every ordinary verifier failure, missing proof and proof-boolean error is
    a denial. No verifier error details escape to the UI or diagnostic output.
    The verifier remains authoritative; this wrapper cannot validate a license.

    Premium GUI callers MUST pass their exact product. In that mode, require an
    exact offline_entitlement.Entitlement instance for the selected product,
    not a truthy sentinel, incorrect product, or user-defined __bool__ hook.
    The verifier callback still owns Ed25519 signature, expiry and current
    license-file validation on EVERY call. Omitting product retains historical
    helper behavior for old non-gating callers; never omit it at an access gate.
    If the UI scrub itself fails, its exception is deliberately not concealed.
    """
    if not callable(authorize) or not callable(clear_sensitive_view):
        raise ValueError("Invalid premium authorization callbacks")
    try:
        proof = authorize()
        if product is _LEGACY_UNSCOPED:
            permitted = bool(proof)  # Legacy compatibility; NOT a premium gate.
        else:
            from .offline_entitlement import Entitlement
            permitted = has_verified_premium_proof(proof, product, Entitlement)
    except Exception:
        # A verifier dependency/programming failure must not leave previously
        # loaded customer evidence visible or authorize a privileged action.
        permitted = False
    if not permitted:
        clear_sensitive_view()
    return permitted
