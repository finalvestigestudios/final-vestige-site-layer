"""Local-only, keyboard-first navigation for all six Tk desktop apps.

Shortcuts invoke the EXISTING widgets and their commands. In particular,
Ctrl+Enter and Alt+R cannot bypass premium entitlement/reviewer checks.
The binding is scoped to the application toplevel (not global bind_all), and
nothing here reads, transmits, or records paths or customer data.
"""
from __future__ import annotations


def install_shortcuts(root, inputs, output, generate, *, review=None) -> tuple[str, ...]:
    """Install discoverable keyboard controls on the root Tk window.

    Alt+1/2/3 focus the corresponding input; Ctrl+1/2/3 open the matching
    file picker. Alt+O focuses the output folder; Ctrl+O opens its picker.
    Alt+G or Ctrl+Return invokes Generate; Alt+R invokes the premium review
    button when present. The existing button command is always responsible
    for permissions and input validation.

    Inputs is a sequence of (Entry, Browse Button) pairs and output
    is the (Entry, Browse Button) pair for the output folder.
    """
    fields = tuple(inputs)
    if not 1 <= len(fields) <= 3:
        raise ValueError("Expected one to three required input fields")
    if any(len(pair) != 2 for pair in (*fields, output)):
        raise ValueError("Each input/output needs an entry and browse button")
    if len({id(widget) for pair in (*fields, output) for widget in pair}) != 2 * (len(fields) + 1):
        raise ValueError("Input and output controls must be independent")

    actions = {}
    for i, (entry, browse) in enumerate(fields, start=1):
        actions[f"<Alt-Key-{i}>"] = entry.focus_set
        actions[f"<Control-Key-{i}>"] = browse.invoke
    actions["<Alt-Key-o>"] = output[0].focus_set
    actions["<Control-Key-o>"] = output[1].invoke
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
