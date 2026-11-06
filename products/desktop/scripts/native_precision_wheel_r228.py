"""Real Tk/Xvfb partial-wheel event test; does not open customer data."""
import tkinter as tk
from tkinter import ttk
from fvs_suite.scroll_access import ScrollableForm


def main():
    root = tk.Tk()
    try:
        root.geometry('320x230')
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        form = ScrollableForm(root)
        # Model Win32 high-resolution deltas on Linux/Xvfb. This is not native
        # Windows acceptance or physical precision-touchpad certification.
        form._wheel_platform = "win32"
        fields = []
        for i in range(22):
            ttk.Label(form.frame, text=f'Field {i}').grid(row=2*i, column=0)
            entry = ttk.Entry(form.frame, width=15)
            entry.grid(row=2*i+1, column=0)
            fields.append(entry)
        root.update()
        if form.canvas.yview()[1] >= 1.0:
            raise RuntimeError("R228 smoke was not scrollable")
        first = form.canvas.yview()[0]
        for _ in range(3):
            fields[0].event_generate('<MouseWheel>', delta=-30)
            root.update()
            if form.canvas.yview()[0] != first:
                raise RuntimeError("Partial wheel amplified prematurely")
        fields[0].event_generate('<MouseWheel>', delta=-30)
        root.update()
        after = form.canvas.yview()[0]
        if after <= first:
            raise RuntimeError("Accumulated notch failed to scroll")
        dialog = tk.Toplevel(root)
        other = ttk.Entry(dialog)
        other.pack()
        root.update()
        other.event_generate('<MouseWheel>', delta=-30)
        root.update()
        if form.canvas.yview()[0] != after or form._wheel_remainder:
            raise RuntimeError("Dialog changed parent viewport or wheel state")
        dialog.destroy()
        print("PASS: 3 partials silent; fourth scrolls; unrelated Tk dialog isolated")
    finally:
        root.destroy()


if __name__ == '__main__':
    main()
