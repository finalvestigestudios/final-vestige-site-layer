"""Fail-closed preflight for the six local-only desktop keyboard shortcut maps.

A missing focus or Browse method must be found before any root.bind call.
This checks widget capabilities only; it never invokes a command, reads a
field, exports customer data or authorizes a premium human-review action.
"""
from __future__ import annotations


def validate_shortcut_targets(fields, output, generate, *, review=None,
                              invoice_window=None, policy_rules=None,
                              ledger_headers=None) -> None:
    """Reject broken keyboard targets without altering bindings or widgets.

    The caller is responsible for product-specific combinations and aliases.
    Native Tk widget methods are checked by identity-independent callability;
    actual execution always goes through the original Tk widget command.
    """
    if type(fields) not in (tuple, list) or not 1 <= len(fields) <= 3:
        raise ValueError("Invalid keyboard source controls")

    def require(widget, name):
        if not callable(getattr(widget, name, None)):
            raise ValueError("Keyboard shortcut target is unavailable")

    def require_pair(pair):
        if type(pair) not in (tuple, list) or len(pair) != 2:
            raise ValueError("Invalid keyboard control pair")
        require(pair[0], "focus_set")
        require(pair[1], "invoke")

    for pair in fields:
        require_pair(pair)
    require_pair(output)
    require(generate, "invoke")
    if review is not None:
        require(review, "invoke")
    if invoice_window is not None:
        require(invoice_window, "focus_set")
    if policy_rules is not None:
        require_pair(policy_rules)
    if ledger_headers is not None:
        if type(ledger_headers) not in (tuple, list) or len(ledger_headers) != 4:
            raise ValueError("Invalid ledger keyboard controls")
        for widget in ledger_headers:
            require(widget, "focus_set")
