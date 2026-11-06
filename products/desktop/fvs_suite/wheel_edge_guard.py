"""Privacy-preserving native vertical-wheel boundary guard for six Tk apps.

Only Tk geometry and integer event metadata are used. A wheel gesture pushing
out of the visible canvas must not poison the next precision-touchpad gesture.
"""
from __future__ import annotations

import math


def wheel_points_outward(lo, hi, *, delta=0, button=None):
    """True for an outward wheel at the top/bottom of a native Tk yview.

    X11 button 4 is up, 5 is down; native Windows/macOS delta > 0 is up.
    Geometry must be a real finite view fraction; do not invoke arbitrary
    conversion hooks on source-controlled or customer-provided objects.
    """
    if (type(lo) not in (int, float) or type(hi) not in (int, float)
            or not math.isfinite(lo) or not math.isfinite(hi)
            or not 0.0 <= lo <= hi <= 1.0):
        raise ValueError("Invalid vertical scroll view")
    if button is not None:
        if type(button) is not int or button not in (4, 5):
            raise ValueError("Invalid vertical wheel button")
        up = button == 4
        down = button == 5
    else:
        if type(delta) is not int:
            raise ValueError("Invalid native wheel delta")
        up = delta > 0
        down = delta < 0
    return (up and lo == 0.0) or (down and hi == 1.0)
