"""Isolate SpendMap Lite callbacks from exact financial Decimal context.

Parsers and display formatters are injected by callers. A callback may change
getcontext(), call setcontext(), or set traps/flags. Those changes must not
change later spend totals, medians, review thresholds, or formatting. This
helper does not validate callback results; the owning input/report boundary
must continue doing so. Nor does it sanitize errors: that boundary must
translate exceptions without preserving private source text.
"""
from __future__ import annotations

from decimal import localcontext
from typing import Callable, TypeVar

_Input = TypeVar("_Input")
_Output = TypeVar("_Output")


def invoke_spend_callback(callback: Callable[[_Input], _Output],
                          value: _Input) -> _Output:
    """Restore the calling Decimal environment even on callback failure.

    ``localcontext`` saves/restores the full active context, including
    changes from ``setcontext`` and direct mutation of rounding/traps/flags.
    It deliberately does not suppress an exception; callers own sanitized
    errors and human-review workflows. Financial operands are not rounded or
    converted here.
    """
    with localcontext():
        return callback(value)
