"""Bind the retained six-app source-test receipt to the current checkout.

Verification is local, read-only and never authorizes an EXE release. The
production readers independently fingerprint the *complete* source and test
trees using existing descriptor-custody rules; changes after the source tests
must prevent private candidate construction.
"""
from __future__ import annotations

from pathlib import Path

SAFE_ERROR = "REJECTED: private tested-source binding did not match checkout"
MAX_ENTRIES = 512


class SourceBindingRejected(ValueError):
    """Fixed, path-free diagnostic for untrusted receipt evidence."""


def _valid_inventory(items, prefix: str) -> bool:
    if type(items) is not list or not 1 <= len(items) <= MAX_ENTRIES:
        return False
    previous = ""
    for item in items:
        if type(item) is not dict or set(item) != {"path", "sha256"}:
            return False
        path, digest = item["path"], item["sha256"]
        if (type(path) is not str or not path.startswith(prefix)
                or not path.endswith(".py") or not previous < path
                or any(part in ("", ".", "..") for part in path.split("/"))
                or "\\" in path or type(digest) is not str or len(digest) != 64
                or any(ch not in "0123456789abcdef" for ch in digest)):
            return False
        previous = path
    return True


def verify_source_binding(root: Path, receipt: dict, *,
                          source_inventory_reader=None,
                          test_inventory_reader=None) -> None:
    """Compare receipt inventories to fresh independently inventoried bytes.

    Readers are injectable solely for small deterministic unit fixtures. The
    actual private candidate uses Git-owned complete source/test inventory
    readers with per-file descriptor, link and mutation custody checks.
    """
    valid = False
    try:
        if type(receipt) is dict and type(receipt.get("source_smoke")) is dict:
            expected_source = receipt["source_smoke"].get("source_inventory")
            expected_tests = receipt.get("test_inventory")
            if (_valid_inventory(expected_source, "products/desktop/")
                    and _valid_inventory(expected_tests, "products/desktop/tests/")):
                if source_inventory_reader is None:
                    from source_smoke_gate import source_inventory as source_inventory_reader
                if test_inventory_reader is None:
                    from offline_source_gate import _test_inventory as test_inventory_reader
                checkout = Path(root).resolve(strict=True)
                valid = (expected_source == source_inventory_reader(checkout)
                         and expected_tests == test_inventory_reader(checkout))
    except Exception:
        # Swallow only the private underlying details; raise *outside* the
        # handler so even __context__ cannot retain a financial pathname.
        pass
    if not valid:
        raise SourceBindingRejected(SAFE_ERROR)
