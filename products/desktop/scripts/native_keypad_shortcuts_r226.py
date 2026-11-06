"""R226 Xvfb/native-Tk keypad smoke on synthetic widgets only.

This tests Tk's Num-Lock-off navigation aliases and matching output actions;
it NEVER opens dialogs, reads customer data, approves reports, or exercises
entitlement. It is not physical Windows/NVDA accessibility acceptance.
"""
import tkinter as tk
from tkinter import ttk
from fvs_suite.keyboard_access import install_shortcuts


def main():
    root = tk.Tk()
    calls = []
    try:
        root.geometry("560x420")
        inputs = []
        for i in range(3):
            entry = ttk.Entry(root)
            entry.pack()
            browse = ttk.Button(root, text=f"Synthetic picker {i}",
                                command=lambda number=i: calls.append(number))
            browse.pack()
            inputs.append((entry, browse))
        out_entry = ttk.Entry(root)
        out_entry.pack()
        out_browse = ttk.Button(root, text="Synthetic output",
                                command=lambda: calls.append("output"))
        out_browse.pack()
        generated = ttk.Button(root, text="Synthetic generate",
                               command=lambda: calls.append("generate"))
        generated.pack()
        install_shortcuts(root, inputs, (out_entry, out_browse), generated)
        root.update()
        root.focus_force()
        root.update()
        # Xvfb commonly has Num Lock off. Native generated KP_1..KP_3 events
        # therefore arrive with keysyms KP_End, KP_Down and KP_Next.
        for index, symbol in enumerate(("KP_1", "KP_2", "KP_3")):
            inputs[0][0].focus_force()
            root.update()
            inputs[0][0].event_generate("<Alt-Key-" + symbol + ">")
            root.update()
            if root.focus_get() != inputs[index][0]:
                raise RuntimeError("Keypad focus did not reach the intended source")
            inputs[0][0].focus_force()
            root.update()
            inputs[0][0].event_generate("<Control-Key-" + symbol + ">")
            root.update()
            if calls != list(range(index + 1)):
                raise RuntimeError("Keypad browse invoked an unexpected action")
        if "generate" in calls or "output" in calls:
            raise RuntimeError("Keypad unexpectedly activated report/output")
        print("PASS: 3 native focus + 3 synthetic picker actions; 0 reports")
    finally:
        root.destroy()


if __name__ == "__main__":
    main()
