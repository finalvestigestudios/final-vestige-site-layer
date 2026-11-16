"""Bind the R459 fallback result to R408's *complete* six-app source tree.

R459's short regression inventory intentionally does not include every imported
engine, launcher, and local asset. Use R408's separately checked descriptor-
backed inventory to detect changes in the full suite across both phases.
This is source-only evidence, NEVER release approval or a binary signature.
"""
from __future__ import annotations

import json
from pathlib import Path

from offline_source_smoke_r408 import SourceGateError, source_digest
from offline_smoke_receipt_r460 import SourceSmokeReceiptError, require_six_app_smokes


class SourceBindingError(ValueError):
    """Customer-data-free error for source/child digest mismatches."""


def _native_digest(value: object) -> bool:
    return (type(value) is str and len(value) == 64
            and all(char in '0123456789abcdef' for char in value))


def verified_six_app_digest(desktop: Path) -> str:
    """Independently attest launchers and imported assets using R408 custody.

    R408 rejects links, non-source import artifacts and unstable descriptors.
    No exception from a local pathname or customer-derived file escapes.
    """
    try:
        digest = source_digest(desktop)
    except (SourceGateError, OSError, ValueError):
        raise SourceBindingError('Local six-app source inventory rejected') from None
    if not _native_digest(digest):
        raise SourceBindingError('Local six-app source inventory rejected')
    return digest


def require_bound_six_app_smokes(raw: bytes, expected_digest: str) -> int:
    """Prove that the twelve successful R408 statuses were for this inventory.

    A well-formed but unrelated/previous R408 receipt must never be accepted.
    The strict R460 parser independently checks six IDs, both modes, source-only
    scope and release_authorized=false. Nothing is logged or re-emitted.
    """
    if not _native_digest(expected_digest):
        raise SourceBindingError('Local six-app source receipt rejected')
    try:
        total = require_six_app_smokes(raw)
        reported = json.loads(raw)['source_sha256']
    except (SourceSmokeReceiptError, ValueError, KeyError, TypeError):
        raise SourceBindingError('Local six-app source receipt rejected') from None
    if reported != expected_digest:
        raise SourceBindingError('Local six-app source receipt rejected')
    return total
