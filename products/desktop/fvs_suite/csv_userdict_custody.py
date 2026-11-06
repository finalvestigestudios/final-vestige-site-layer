"""Verify a UserDict's emitted CSV evidence against its native backing storage.

A UserDict subclass can override ``items()`` and advertise well-formed but
fabricated values. The CSV report writer first validates native two-tuples and
keys, then calls this helper to reject a view that does not correspond to the
actual built-in backing dict. No user-defined equality/string hooks are run.
"""
from __future__ import annotations

from collections import UserDict
from decimal import Decimal
from itertools import islice


class UserDictCustodyError(ValueError):
    """The source row's advertised evidence cannot be trusted."""


def verify_userdict_storage(row: object, entries: tuple, max_columns: int) -> tuple:
    """Return authoritative stored pairs, or reject an inconsistent virtual view.

    For mappings other than UserDict, keep the existing contract unchanged.
    ``entries`` must already have passed the caller's strict native-pair and
    native-key validation. Comparisons of user-supplied objects use identity;
    only exact built-in immutable primitives use value equality.
    """
    if not isinstance(row, UserDict):
        return entries
    invalid = "CSV report UserDict view differs from stored evidence"
    failed = False
    try:
        state = object.__getattribute__(row, "__dict__")
        if type(state) is not dict:
            failed = True
        else:
            backing = dict.get(state, "data")
            if not isinstance(backing, dict):
                failed = True
            else:
                native = tuple(islice(dict.items(backing), max_columns + 1))
    except Exception:
        failed = True
    # Raise outside except: even `from None` leaves private __context__ reachable.
    if failed:
        raise UserDictCustodyError(invalid)
    if (len(native) > max_columns or len(native) != len(entries)
            or any(type(k) is not str for k, _ in native)):
        raise UserDictCustodyError(invalid)
    for (view_key, view_value), (stored_key, stored_value) in zip(entries, native):
        if view_key != stored_key or type(view_value) is not type(stored_value):
            raise UserDictCustodyError(invalid)
        # Only compare exact built-in value types; arbitrary value equality can
        # execute user callbacks or fabricate a matching audit record.
        if type(stored_value) in (str, int, bool, Decimal, float, type(None), bytes):
            if view_value != stored_value:
                raise UserDictCustodyError(invalid)
        elif view_value is not stored_value:
            raise UserDictCustodyError(invalid)
    return native
