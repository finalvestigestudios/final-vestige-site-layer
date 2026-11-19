"""Local-only, keyboard-first navigation for all six Tk desktop apps.

Shortcuts invoke the EXISTING widgets and their commands. In particular,
Ctrl+Enter and Alt+R cannot bypass premium entitlement/reviewer checks.
The binding is scoped to the application toplevel (not global bind_all), and
nothing here reads, transmits, or records paths or customer data.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .shortcut_targets_r403 import validate_shortcut_targets


def _verify_callback_ack(callback_id, used_ids: set[str]) -> None:
    """Accept only a distinct, bounded Tk-created Python callback command ID.

    Native Tkinter Python bindings return compact printable ASCII Tcl command
    names. A duplicate, invisible, non-ASCII or oversized acknowledgement
    cannot safely identify one callback for targeted rollback. Do not hash or
    stringify subclasses: they could execute arbitrary user-defined methods.
    """
    if (type(callback_id) is not str
            or not 1 <= len(callback_id) <= 128
            or not callback_id.isascii()
            or any(not 33 <= ord(ch) <= 126 for ch in callback_id)
            or callback_id in used_ids):
        raise ValueError("Tk shortcut registration returned no unique valid callback ID")
    used_ids.add(callback_id)



def format_keyboard_help(legend: str) -> str:
    """Show the existing, trusted keyboard legend as short screen-reader lines.

    The caller supplies only the app's static shortcut text, never an input
    filename, payment record or entitlement. Reject malformed/unbounded text
    rather than allowing a modal help dialog to render a giant single line.
    """
    if (type(legend) is not str or not legend.startswith("Keyboard: ")
            or not 1 <= len(legend) <= 700):
        raise ValueError("Keyboard help requires a bounded static legend")
    sections = legend[len("Keyboard: "):].split("; ")
    if (not 4 <= len(sections) <= 12
            or any(not part or len(part) > 75 or ";" in part
                   or any(ord(ch) < 32 or ord(ch) == 127 for ch in part)
                   for part in sections)):
        raise ValueError("Keyboard help contains an invalid shortcut section")
    return "Keyboard shortcuts:\n\n" + "\n".join("- " + part for part in sections)



def show_keyboard_help(root, legend: str) -> None:
    """Open one focusable, scrollable, read-only F1 help window per application.

    The only displayed value is the statically authored shortcut legend. A
    bounded window keeps its close control and keyboard scrolling usable on
    high-DPI screens. No inputs, output paths, licenses or report data are read.
    """
    content = format_keyboard_help(legend)  # Validate before any Tk side effect.
    existing = getattr(root, "_fvs_help_dialog", None)
    recovered_focus = None
    if existing is not None:
        try:
            if existing.winfo_exists():
                existing.lift()
                focus_target = getattr(existing, "_fvs_help_text", None)
                if focus_target is None:
                    # Legacy dialogs may not carry a separate text handle.
                    existing.focus_set()
                    return
                if focus_target.winfo_exists():
                    try:
                        focus_target.focus_set()
                    except tk.TclError:
                        # Keep the live window keyboard-reachable if its child
                        # loses focus during a Tk/window-manager transition.
                        existing.focus_set()
                    return
                # The window survived but its help Text was destroyed. Do not
                # keep returning an inaccessible empty window on every F1.
                recovered_focus = getattr(existing, "_fvs_former_focus", None)
                existing.destroy()
        except tk.TclError:
            # A failed raise/focus can leave a live orphan Toplevel. Dispose
            # of it before reconstructing the accessible help text.
            try:
                if existing.winfo_exists():
                    recovered_focus = getattr(existing, "_fvs_former_focus", None)
                    existing.destroy()
            except tk.TclError:
                pass

    former_focus = (recovered_focus if recovered_focus is not None
                    else root.focus_get())  # Widget only; never entry.get().
    dialog = tk.Toplevel(root)
    root._fvs_help_dialog = dialog
    dialog._fvs_former_focus = former_focus

    closed = False

    def close(_event=None):
        nonlocal closed
        # Escape and the window-manager close event may both arrive during
        # teardown. Never destroy twice or restore focus multiple times.
        if closed:
            return
        closed = True
        if getattr(root, "_fvs_help_dialog", None) is dialog:
            root._fvs_help_dialog = None
        try:
            dialog.destroy()
        except tk.TclError:
            pass  # Window already destroyed by the window manager.
        if former_focus is not None:
            try:
                if former_focus.winfo_exists():
                    former_focus.focus_set()
            except tk.TclError:
                pass

    def on_escape(event):
        close()
        return "break"

    try:
        dialog.title("Keyboard shortcuts")
        dialog.transient(root)
        dialog.resizable(True, True)
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)

        frame = ttk.Frame(dialog, padding=12)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        instructions = tk.Text(frame, width=54, height=10,
                               wrap="word", takefocus=True)
        instructions.insert("1.0", content)
        instructions.configure(state="disabled")
        # Retain the keyboard-readable target for repeated F1 focus recovery.
        dialog._fvs_help_text = instructions
        scroll = ttk.Scrollbar(frame, orient="vertical",
                               command=instructions.yview)
        instructions.configure(yscrollcommand=scroll.set)
        instructions.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        ttk.Button(frame, text="Close (Esc)", command=close).grid(
            row=1, column=0, columnspan=2, sticky="e", pady=(12, 0))
        dialog.protocol("WM_DELETE_WINDOW", close)
        dialog.bind("<Escape>", on_escape)

        # Physical window bounds, not unbounded character-based sizing. Users
        # can resize the dialog and scroll via keyboard, wheel or scrollbar.
        width = max(1, min(760, root.winfo_screenwidth() - 64))
        height = max(1, min(480, root.winfo_screenheight() - 96))
        dialog.geometry(f"{width}x{height}")
        instructions.focus_set()
    except BaseException:
        if getattr(root, "_fvs_help_dialog", None) is dialog:
            root._fvs_help_dialog = None
        try:
            dialog.destroy()
        except BaseException:
            pass
        raise

def install_shortcuts(root, inputs, output, generate, *, review=None,
                      invoice_window=None, policy_rules=None,
                      ledger_headers=None, help_action=None) -> tuple[str, ...]:
    """Install shortcut access without replacing native Tab or focus-reveal.

    Alt+1..3 focuses source fields; Ctrl+1..3 opens their existing Browse
    buttons. Both numeric-keypad digit and navigation keysyms map to the same
    actions, including with Num Lock off (KP_End/KP_Down/KP_Next).
    Alt+O/Ctrl+O access the output folder. Alt+G/Ctrl+Return invokes
    the existing Generate button; Alt+R invokes the gated premium review.
    Invoice Twin's additional near-match window is focused by Alt+W.
    ProcureGuard's optional policy input/Browse use Alt+P/Ctrl+P.
    LedgerDiff's optional CSV header inputs use Alt+L (left match),
    Alt+R (right match), Alt+A (left amount) and Alt+M (right amount).
    All optional Ledger shortcuts focus only; no shortcut authorizes a
    report or executes a financial rule without the app's button.
    An optional F1 handler shows caller-supplied, static keyboard help. It
    cannot run Generate or premium Review and reads no financial input.
    """
    fields = tuple(inputs)
    if not 1 <= len(fields) <= 3:
        raise ValueError("Expected one to three required input fields")
    if any(len(pair) != 2 for pair in (*fields, output)):
        raise ValueError("Each input/output needs an entry and browse button")
    if invoice_window is not None and policy_rules is not None:
        raise ValueError("Unexpected combination of optional controls")
    if policy_rules is not None and (
            type(policy_rules) not in (tuple, list) or len(policy_rules) != 2):
        raise ValueError("Policy requires an entry and browse button")

    if ledger_headers is not None:
        if (type(ledger_headers) not in (tuple, list) or len(ledger_headers) != 4
                or len(fields) != 2 or review is not None
                or invoice_window is not None or policy_rules is not None):
            raise ValueError("Ledger headers require two inputs and no other optional controls")

    # Reject an invalid optional help callback before installing ANY shortcut.
    # Existing API clients without help_action keep the same binding inventory.
    if help_action is not None and not callable(help_action):
        raise ValueError("Keyboard help action must be callable")

    # Validate every focus/Browse target before installing any root binding.
    validate_shortcut_targets(fields, output, generate,
                              review=review, invoice_window=invoice_window,
                              policy_rules=policy_rules,
                              ledger_headers=ledger_headers)

    widgets = [widget for pair in (*fields, output) for widget in pair]
    if invoice_window is not None:
        widgets.append(invoice_window)
    if policy_rules is not None:
        widgets.extend(policy_rules)
    if ledger_headers is not None:
        widgets.extend(ledger_headers)
    # The action buttons must not alias a source, Browse, output, optional
    # control, or one another. Otherwise a focus/Browse mnemonic can execute
    # Generate or gated Review unexpectedly. Reject before installing bindings.
    actions_only = [generate] + ([review] if review is not None else [])
    if (any(not callable(getattr(button, "invoke", None)) for button in actions_only)
            or len({id(widget) for widget in (*widgets, *actions_only)})
               != len(widgets) + len(actions_only)):
        raise ValueError("Shortcut actions require independent command buttons")
    if len({id(widget) for widget in widgets}) != len(widgets):
        raise ValueError("Input and optional controls must be independent")

    actions = {}
    keypad_keysyms = (("KP_1", "KP_End"),
                      ("KP_2", "KP_Down"),
                      ("KP_3", "KP_Next"))
    for i, (entry, browse) in enumerate(fields, start=1):
        actions[f"<Alt-Key-{i}>"] = entry.focus_set
        actions[f"<Control-Key-{i}>"] = browse.invoke
        # Tk may report either the digit or its navigation keysym depending
        # on Num Lock. Both receive the identical existing button operation.
        for keysym in keypad_keysyms[i - 1]:
            actions[f"<Alt-Key-{keysym}>"] = entry.focus_set
            actions[f"<Control-Key-{keysym}>"] = browse.invoke
    actions["<Alt-Key-o>"] = output[0].focus_set
    actions["<Control-Key-o>"] = output[1].invoke
    if invoice_window is not None:
        actions["<Alt-Key-w>"] = invoice_window.focus_set
    if policy_rules is not None:
        actions["<Alt-Key-p>"] = policy_rules[0].focus_set
        actions["<Control-Key-p>"] = policy_rules[1].invoke
    if ledger_headers is not None:
        for key, entry in zip(("l", "r", "a", "m"), ledger_headers):
            actions[f"<Alt-Key-{key}>"] = entry.focus_set
    actions["<Alt-Key-g>"] = generate.invoke
    actions["<Control-Return>"] = generate.invoke
    if review is not None:
        actions["<Alt-Key-r>"] = review.invoke
    if help_action is not None:
        # App-level messagebox uses only a static shortcut legend: no paths,
        # entered values or entitlement tokens are captured in this handler.
        actions["<F1>"] = help_action

    # Staged callbacks are inert until every additive Tk bind has succeeded.
    # R404 can retain a callback with an unknown ID after a failed bind; that
    # orphan must never operate Generate, Browse, or premium Review.
    activated = False

    def make_handler(operation):
        def handle(_event):
            if not activated:
                return "break"
            operation()
            return "break"
        return handle

    # Tk's additive bind would execute Generate/Review twice if this helper
    # were called again for the same window (e.g. during UI reconstruction).
    # Reject before changing existing bindings, including preexisting app keys.
    if getattr(root, "_fvs_shortcuts_installed", False):
        raise ValueError("Keyboard shortcuts already installed for this window")
    # A failing bind may have already registered its callback *before* it
    # raises, leaving no callback ID to undo. Mark the window as attempted
    # BEFORE the first bind, so even an interrupt or a perfect-looking cleanup
    # cannot lead to a second additive registration over an unknown handler.
    # Recreate the root to retry; do not silently double-run Generate/Review.
    root._fvs_shortcuts_installed = True
    installed: list[tuple[str, str | None]] = []
    used_callback_ids: set[str] = set()
    try:
        for sequence, operation in actions.items():
            # Tk returns the unique callback id; it lets us roll back only
            # OUR newly added function without erasing a preexisting handler.
            callback_id = root.bind(sequence, make_handler(operation), add="+")
            # Tkinter returns one unique, compact Tcl command ID per Python
            # binding. Reused or noncanonical acknowledgements make targeted
            # cleanup ambiguous. Fail closed before publishing activation.
            # An orphan from an invalid ACK remains staged and permanently inert.
            _verify_callback_ack(callback_id, used_callback_ids)
            installed.append((sequence, callback_id))
    except BaseException:
        # Best effort only: the failing bind has no trustworthy callback ID.
        # Preserve earlier unrelated application bindings; do not clear all.
        for sequence, callback_id in reversed(installed):
            if not callback_id or not callable(getattr(root, "unbind", None)):
                continue
            try:
                root.unbind(sequence, callback_id)
            except BaseException:
                # Preserve the original failure and the conservative hold.
                pass
        raise
    # Publish activation only after the entire shortcut map is registered.
    # On errors the closed-over flag stays False for even orphan callbacks.
    activated = True
    return tuple(actions)
