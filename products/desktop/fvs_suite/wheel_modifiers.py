"""Native Tk wheel modifier routing for local-only desktop navigation.

Do not intercept horizontal-scroll (Shift), Control-wheel or Alt-wheel
sequences. Consume no user data or widget contents. ``state`` is the native
integer X/Tk bit field: Shift=0x1, Control=0x4, Mod1/Alt=0x8.
"""

# Lock keys and mouse-button flags are deliberately *not* exclusions.
_MODIFIERS_TO_PRESERVE = 0x0001 | 0x0004 | 0x0008


def is_plain_vertical_wheel(state):
    """Return true only when native wheel events have no Shift/Ctrl/Alt.

    Fail closed for non-native, negative or conversion-hook objects. The value
    is only event metadata, never a file path or contents of a financial field.
    """
    if type(state) is not int or state < 0:
        raise ValueError("Invalid wheel modifier state")
    return (state & _MODIFIERS_TO_PRESERVE) == 0
