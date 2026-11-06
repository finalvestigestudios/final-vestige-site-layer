"""Real Tk/Xvfb key-modifier wheel smoke; synthetic fields only."""
import tkinter as tk
from tkinter import ttk
from fvs_suite.scroll_access import ScrollableForm


def main():
    root = tk.Tk()
    try:
        root.geometry("320x230")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        form = ScrollableForm(root)
        form._wheel_platform = "win32"  # Linux Xvfb simulates Win32 deltas.
        field = None
        for index in range(24):
            ttk.Label(form.frame, text=f"Synthetic {index}").grid(row=2*index, column=0)
            entry = ttk.Entry(form.frame)
            entry.grid(row=2*index+1, column=0)
            if field is None:
                field = entry
        root.update()
        before = form.canvas.yview()[0]
        if form.canvas.yview()[1] >= 1:
            raise RuntimeError("Preflight form must be scrollable")
        field.event_generate("<MouseWheel>", delta=-30, state=0)
        root.update()
        if form._wheel_remainder != -30:
            raise RuntimeError("Plain delta failed to accumulate")
        for modifier in (0x1, 0x4, 0x8, 0xD):
            field.event_generate("<MouseWheel>", delta=-120, state=modifier)
            root.update()
            if form.canvas.yview()[0] != before or form._wheel_remainder != -30:
                raise RuntimeError(f"Modified wheel hijacked viewport/residual: {modifier}")
        field.event_generate("<MouseWheel>", delta=-90, state=0)
        root.update()
        if not form.canvas.yview()[0] > before or form._wheel_remainder != 0:
            raise RuntimeError("Plain wheel failed after modified events")
        print("PASS: real Tk synthetic Shift/Ctrl/Alt wheel preserved; plain wheel resumed")
    finally:
        root.destroy()


if __name__ == "__main__":
    main()
