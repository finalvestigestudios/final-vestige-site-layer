"""R225 actual Tk LedgerDiff shortcut smoke, intended for Linux/Xvfb CI.

This verifies physical Tk bindtag/event propagation with synthetic controls;
Windows real-device keyboard, screen reader and scrolling remain release gates.
No customer financial records, network calls, filesystem inputs or telemetry.
"""
import tkinter as tk
from tkinter import ttk
from fvs_suite.keyboard_access import install_shortcuts


def main():
    root = tk.Tk()
    callbacks = []
    try:
        root.geometry("520x400")
        inputs = []
        for index in (0, 1):
            entry = ttk.Entry(root)
            entry.pack()
            browse = ttk.Button(root, text="Browse", command=lambda i=index: callbacks.append(i))
            browse.pack()
            inputs.append((entry, browse))
        output = ttk.Entry(root)
        output.pack()
        output_picker = ttk.Button(root, text="Output", command=lambda: callbacks.append("output"))
        output_picker.pack()
        headers = []
        for _ in range(4):
            entry = ttk.Entry(root)
            entry.pack()
            headers.append(entry)
        generate = ttk.Button(root, text="Generate", command=lambda: callbacks.append("generate"))
        generate.pack()
        keys = install_shortcuts(root, inputs, (output, output_picker), generate,
                                 ledger_headers=tuple(headers))
        # R226 added eight keypad aliases to the legacy 12 shortcuts.
        if len(keys) != 20 or callbacks:
            raise RuntimeError("R225 shortcut installation mutated the GUI")
        root.update()
        root.focus_force()
        root.update()
        for mnemonic, expected in zip(("l", "r", "a", "m"), headers):
            inputs[0][0].focus_force()
            root.update()
            inputs[0][0].event_generate("<Alt-Key-" + mnemonic + ">")
            root.update()
            if root.focus_get() != expected:
                raise RuntimeError("R225 native Tk optional header focus failed")
        if callbacks:
            raise RuntimeError("R225 native Tk optional focus invoked an action")
        print("R225 native Tk LedgerDiff focus: PASS (4 events, 0 actions)")
    finally:
        root.destroy()


if __name__ == "__main__":
    main()
