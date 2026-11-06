"""Real Tk/Xvfb boundary smoke; synthetic fields only, no financial imports."""
import tkinter as tk
from tkinter import ttk
from fvs_suite.scroll_access import ScrollableForm


def run():
    root = tk.Tk()
    try:
        root.geometry('400x220')
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        form = ScrollableForm(root)
        entry = None
        for n in range(48):
            current = ttk.Entry(form.frame)
            current.insert(0, 'synthetic row')
            current.grid(row=n, column=0, sticky='ew', pady=4)
            if entry is None:
                entry = current
        root.update()
        assert form.canvas.yview()[1] < 1.0, 'Expected scrollable test canvas'
        form._wheel_platform = 'win32'  # simulate Win32 delta arithmetic on Linux Tk
        form.canvas.yview_moveto(0.0)
        root.update()
        entry.event_generate('<MouseWheel>', delta=120)
        root.update()
        assert form.canvas.yview()[0] == 0.0
        assert form._wheel_remainder == 0
        for _ in range(4):
            entry.event_generate('<MouseWheel>', delta=-30)
        root.update()
        assert form.canvas.yview()[0] > 0.0
        form.canvas.yview_moveto(1.0)
        root.update()
        assert form.canvas.yview()[1] == 1.0
        entry.event_generate('<MouseWheel>', delta=-30)
        root.update()
        assert form._wheel_remainder == 0, 'Blocked outward scroll must not linger'
        for _ in range(4):
            entry.event_generate('<MouseWheel>', delta=30)
        root.update()
        assert form.canvas.yview()[1] < 1.0
        print('PASS: real Tk nested-entry events, both edges, reverse precision delta; no files')
    finally:
        root.destroy()


if __name__ == '__main__':
    run()
