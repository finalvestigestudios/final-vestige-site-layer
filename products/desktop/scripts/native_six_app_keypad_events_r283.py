"""Xvfb native Tk keypad event regression for all six desktop configurations.

Uses synthetic widgets and X11-generated KeyPress events only. No file dialogs,
customer data, network, report generation, entitlement, or financial decisions.
Physical Windows 11 keyboards and assistive technology require separate QA.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from fvs_suite.keyboard_access import install_shortcuts

# product, required sources, optional controls, total R282 shortcut inventory
CASES = (
    ("LedgerDiffLite", 2, "ledger", 20),
    ("InvoiceTwinScout", 1, "invoice", 11),
    ("SpendMapLite", 1, "", 10),
    ("PolicyDeltaDesk", 2, "", 16),
    ("GrantAuditStudioPro", 3, "grant", 23),
    ("ProcureGuardStudioPro", 3, "procure", 25),
)
KEYPAD = (("KP_1", "KP_End"), ("KP_2", "KP_Down"), ("KP_3", "KP_Next"))
ALT, CTRL, NUMLOCK = 0x08, 0x04, 0x10  # X11 Mod1, Control, Mod2


def run_case(name: str, count: int, optional: str, expected: int) -> int:
    root = tk.Tk()
    called: list[str] = []

    def entry():
        widget = ttk.Entry(root)
        widget.pack()
        return widget

    def button(label: str):
        widget = ttk.Button(root, text=label, command=lambda: called.append(label))
        widget.pack()
        return widget

    try:
        root.geometry("640x800")
        fields = [(entry(), button(f"browse-{index}")) for index in range(1, count + 1)]
        output = (entry(), button("output-browse"))
        generate = button("generate")
        kw = {}
        if optional == "ledger":
            kw["ledger_headers"] = tuple(entry() for _ in range(4))
        elif optional == "invoice":
            kw["invoice_window"] = entry()
        elif optional in ("grant", "procure"):
            kw["review"] = button("review")
            if optional == "procure":
                kw["policy_rules"] = (entry(), button("policy-browse"))

        installed = install_shortcuts(root, fields, output, generate, **kw)
        if len(installed) != expected or called:
            raise RuntimeError(f"{name}: incorrect shortcut inventory or installation side effect")

        source = fields[0][0]
        root.update()
        dispatched = 0
        for index, (target, _picker) in enumerate(fields, start=1):
            variants = (
                (str(index), ALT, "focus"),
                (str(index), CTRL, "browse"),
                (KEYPAD[index - 1][0], ALT | NUMLOCK, "focus"),
                (KEYPAD[index - 1][0], CTRL | NUMLOCK, "browse"),
                (KEYPAD[index - 1][1], ALT, "focus"),
                (KEYPAD[index - 1][1], CTRL, "browse"),
            )
            for keysym, state, operation in variants:
                source.focus_force()
                root.update()
                if root.focus_get() is not source:
                    raise RuntimeError(f"{name}: cannot establish native Tk event target")
                baseline = tuple(called)
                # X11 normalizes KP_1 to KP_End when Num Lock is off. State
                # toggles ensure BOTH registered Tk callbacks really dispatch.
                source.event_generate(f"<KeyPress-{keysym}>", state=state)
                root.update()
                if operation == "focus":
                    if root.focus_get() is not target or tuple(called) != baseline:
                        raise RuntimeError(f"{name}: {keysym} focused wrong source or invoked a command")
                elif tuple(called) != (*baseline, f"browse-{index}"):
                    raise RuntimeError(f"{name}: {keysym} invoked wrong Browse/Generate/Review")
                dispatched += 1
        if any(label in {"generate", "review", "output-browse", "policy-browse"}
               for label in called):
            raise RuntimeError(f"{name}: input shortcut bypassed privileged control")
        return dispatched
    finally:
        root.destroy()


def main() -> None:
    dispatched = sum(run_case(*case) for case in CASES)
    if dispatched != 72:
        raise RuntimeError("Six-app native keypad dispatch count changed")
    print(f"PASS: {dispatched} native Tk KeyPress events across six configurations; "
          "keypad Num Lock on/off, distinct input focus/Browse, no generation/review")


if __name__ == "__main__":
    main()
