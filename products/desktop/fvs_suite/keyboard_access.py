"""Local-only, keyboard-first navigation for all six Tk desktop apps.

Shortcuts invoke the EXISTING widgets and their commands. In particular,
Ctrl+Enter and Alt+R cannot bypass premium entitlement/reviewer checks.
The binding is scoped to the application toplevel (not global bind_all), and
nothing here reads, transmits, or records paths or customer data.
"""
from __future__ import annotations


def install_shortcuts(root, inputs, output, generate, *, review=None,
                      invoice_window=None, policy_rules=None) -> tuple[str, ...]:
    """Install shortcut access without replacing native Tab or focus-reveal.

    Alt+1..3 focuses source fields; Ctrl+1..3 opens their existing Browse
    buttons. Alt+O/Ctrl+O access the output folder. Alt+G/Ctrl+Return invokes
    the existing Generate button; Alt+R invokes the gated premium review.
    Invoice Twin's additional near-match window is focused by Alt+W.
    ProcureGuard's optional policy input/Browse use Alt+P/Ctrl+P. No shortcut
    authorizes a report or executes a financial rule without the app's button.
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

    widgets = [widget for pair in (*fields, output) for widget in pair]
    if invoice_window is not None:
        widgets.append(invoice_window)
    if policy_rules is not None:
        widgets.extend(policy_rules)
    if len({id(widget) for widget in widgets}) != len(widgets):
        raise ValueError("Input and optional controls must be independent")

    actions = {}
    for i, (entry, browse) in enumerate(fields, start=1):
        actions[f"<Alt-Key-{i}>"] = entry.focus_set
        actions[f"<Control-Key-{i}>"] = browse.invoke
    actions["<Alt-Key-o>"] = output[0].focus_set
    actions["<Control-Key-o>"] = output[1].invoke
    if invoice_window is not None:
        actions["<Alt-Key-w>"] = invoice_window.focus_set
    if policy_rules is not None:
        actions["<Alt-Key-p>"] = policy_rules[0].focus_set
        actions["<Control-Key-p>"] = policy_rules[1].invoke
    actions["<Alt-Key-g>"] = generate.invoke
    actions["<Control-Return>"] = generate.invoke
    if review is not None:
        actions["<Alt-Key-r>"] = review.invoke

    def make_handler(operation):
        def handle(_event):
            operation()
            return "break"
        return handle

    for sequence, operation in actions.items():
        root.bind(sequence, make_handler(operation), add="+")
    return tuple(actions)
