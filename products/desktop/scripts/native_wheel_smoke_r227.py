"""R227 actual Tk event test; run only in an available private desktop/Xvfb."""
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
        entries = []
        for n in range(20):
            ttk.Label(form.frame, text=f'Source {n}').grid(row=2*n, column=0)
            entry = ttk.Entry(form.frame, width=12)
            entry.grid(row=2*n+1, column=0)
            entries.append(entry)
        root.update()
        start = form.canvas.yview()[0]
        if form.canvas.yview()[1] >= 1.0:
            raise RuntimeError('inconclusive: test form does not overflow')
        entries[0].event_generate('<MouseWheel>', delta=-120)
        root.update()
        after_mouse = form.canvas.yview()[0]
        if not after_mouse > start:
            raise RuntimeError('mouse wheel event did not scroll nested Entry')
        entries[0].event_generate('<Button-5>')
        root.update()
        after_x11 = form.canvas.yview()[0]
        if not after_x11 > after_mouse:
            raise RuntimeError('X11 wheel event did not scroll nested Entry')
        # A separate Toplevel must not trigger the parent application's viewport.
        dialog = tk.Toplevel(root)
        dialog_entry = ttk.Entry(dialog)
        dialog_entry.pack()
        root.update()
        dialog_entry.event_generate('<MouseWheel>', delta=-120)
        root.update()
        if form.canvas.yview()[0] != after_x11:
            raise RuntimeError('dialog scroll escaped into parent form')
        dialog.destroy()
        print('R227 native Tk wheel event smoke PASS: nested MouseWheel, Button-5 and modal isolation')
    finally:
        root.destroy()


if __name__ == '__main__':
    main()
