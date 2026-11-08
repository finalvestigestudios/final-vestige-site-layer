"""Native Tk/Xvfb keyboard acceptance for all six local-only desktop variants.

Only synthetic widget commands run: no dialogs, network, customer files,
financial rules, entitlement changes, or payment approvals. Physical Windows
keyboard/screen-reader acceptance is a separate release gate.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from fvs_suite.keyboard_access import install_shortcuts


CASES = (
    ("LedgerDiffLite", 2, "ledger_headers", 20),
    ("InvoiceTwinScout", 1, "invoice_window", 11),
    ("SpendMapLite", 1, "", 10),
    ("PolicyDeltaDesk", 2, "", 16),
    ("GrantAuditStudioPro", 3, "review", 23),
    ("ProcureGuardStudioPro", 3, "policy_rules", 25),
)


def run_case(name: str, count: int, option: str, expected: int) -> int:
    root = tk.Tk()
    observed: list[str] = []
    authorized = {"generate": False, "review": False}

    def button(label: str, gate: str | None = None):
        def command():
            # Simulates the existing command's human-approval/validation gate.
            # The shortcut must invoke this widget, never a naked side effect.
            if gate is None or authorized[gate]:
                observed.append(label)
        widget = ttk.Button(root, text=label, command=command)
        widget.pack()
        return widget

    def entry():
        widget = ttk.Entry(root)
        widget.pack()
        return widget

    def press(sequence: str):
        inputs[0][0].focus_force()
        root.update()
        inputs[0][0].event_generate(sequence)
        root.update()

    try:
        root.geometry("650x850")
        inputs = [(entry(), button(f"browse{i}")) for i in range(count)]
        output = (entry(), button("out-browse"))
        generate = button("generate", gate="generate")
        kw = {}
        if option == "ledger_headers":
            kw["ledger_headers"] = [entry() for _ in range(4)]
        elif option == "invoice_window":
            kw["invoice_window"] = entry()
        elif option == "review":
            kw["review"] = button("review", gate="review")
        elif option == "policy_rules":
            kw["policy_rules"] = (entry(), button("policy-browse"))
            kw["review"] = button("review", gate="review")

        # Misconfigured command aliases must fail before adding any Tk binds.
        try:
            install_shortcuts(root, inputs, output, inputs[0][1], **kw)
        except ValueError:
            pass
        else:
            raise RuntimeError(f"{name}: aliased Generate accepted")
        if root.bind("<Control-Return>"):
            raise RuntimeError(f"{name}: invalid widgets partially bound")

        installed = install_shortcuts(root, inputs, output, generate, **kw)
        if len(installed) != expected or observed:
            raise RuntimeError(f"{name}: unexpected shortcut inventory/callback")
        root.update()
        root.focus_force()
        root.update()

        press("<Alt-Key-1>")
        if root.focus_get() != inputs[0][0]:
            raise RuntimeError(f"{name}: first input focus lost")
        press("<Control-Key-1>")
        if observed != ["browse0"]:
            raise RuntimeError(f"{name}: browse dispatched a forbidden command")
        press("<Alt-Key-o>")
        if root.focus_get() != output[0]:
            raise RuntimeError(f"{name}: output focus failed")

        if option == "ledger_headers":
            press("<Alt-Key-r>")
            if root.focus_get() != kw["ledger_headers"][1]:
                raise RuntimeError("LedgerDiff: Alt+R did not focus right header")
        if option == "invoice_window":
            press("<Alt-Key-w>")
            if root.focus_get() != kw["invoice_window"]:
                raise RuntimeError("Invoice Twin: near-match focus failed")
        if option == "policy_rules":
            press("<Alt-Key-p>")
            if root.focus_get() != kw["policy_rules"][0]:
                raise RuntimeError("ProcureGuard: policy focus failed")
            press("<Control-Key-p>")
            if observed[-1] != "policy-browse":
                raise RuntimeError("ProcureGuard: policy Browse failed")

        # The existing widget commands remain responsible for business gates.
        baseline = list(observed)
        press("<Control-Return>")
        if observed != baseline:
            raise RuntimeError(f"{name}: shortcut bypassed generation validation")
        generate.state(["disabled"])
        authorized["generate"] = True
        press("<Alt-Key-g>")
        if observed != baseline:
            raise RuntimeError(f"{name}: shortcut invoked disabled Generate")
        generate.state(["!disabled"])
        press("<Control-Return>")
        if observed != baseline + ["generate"]:
            raise RuntimeError(f"{name}: enabled command did not execute")

        if "review" in kw:
            baseline = list(observed)
            press("<Alt-Key-r>")
            if observed != baseline:
                raise RuntimeError(f"{name}: review approval gate bypassed")
            kw["review"].state(["disabled"])
            authorized["review"] = True
            press("<Alt-Key-r>")
            if observed != baseline:
                raise RuntimeError(f"{name}: disabled Review button invoked")
            kw["review"].state(["!disabled"])
            press("<Alt-Key-r>")
            if observed != baseline + ["review"]:
                raise RuntimeError(f"{name}: authorized Review button not reached")
        elif name != "LedgerDiffLite" and "<Alt-Key-r>" in installed:
            raise RuntimeError(f"{name}: free tier accidentally gained Review")
        return len(installed)
    finally:
        root.destroy()


def main():
    counts = [(name, run_case(name, fields, option, expected))
              for name, fields, option, expected in CASES]
    print("PASS: native Tk six-app shortcut checks, all control aliases rejected; "
          f"{sum(total for _, total in counts)} bindings validated, "
          "disabled and gated actions preserved")


if __name__ == "__main__":
    main()
