"""Bind SpendMap vendor matching keys to source-identical labels for one report.

Custom normalization callbacks must not split the same source vendor across
separate financial aggregates. ASCII case and ASCII boundary whitespace are
insignificant for source identity; non-ASCII bytes remain significant evidence.
This is a fail-closed consistency check, not supplier verification.
"""
from __future__ import annotations

import re

_ASCII_BOUNDARY_WHITESPACE = " \t\r\n\v\f"
_ASCII_LOWERCASE = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")
_PHYSICAL_ROW = re.compile(r"[1-9][0-9]{0,9}\Z", re.ASCII)


class SpendVendorSession:
    """One-report mapping of source-equivalent labels to a stable vendor key."""

    def __init__(self) -> None:
        self._keys: dict[str, str] = {}

    def attest(self, original: str, vendor_key: str, physical_row: str) -> None:
        """Reject stateful callbacks that split one source identity into keys.

        Input and normalized keys are validated again by the caller; local
        native-type checks prevent hostile user objects from executing methods.
        No sensitive source/vendor strings are included in error messages.
        """
        if (type(original) is not str or type(vendor_key) is not str
                or type(physical_row) is not str
                or _PHYSICAL_ROW.fullmatch(physical_row) is None):
            raise ValueError("Invalid SpendMap vendor session evidence")
        identity = original.strip(_ASCII_BOUNDARY_WHITESPACE).translate(_ASCII_LOWERCASE)
        previous = self._keys.get(identity)
        if previous is not None and previous != vendor_key:
            raise ValueError(f"Inconsistent vendor normalization at physical row {physical_row}")
        self._keys[identity] = vendor_key
