"""Pre-launch six-product identity gate for native Windows release candidates.

Distinct names alone cannot establish that six build outputs contain six
separately packaged apps. This is a structural SHA-256 collision/duplicate
check, not product identity attestation, entitlement, AV, or release approval.
"""
from __future__ import annotations

import re

_SHA256 = re.compile(r"[0-9a-f]{64}\Z")


class CandidateIdentityError(ValueError):
    """Fixed, non-sensitive diagnostic for malformed or duplicated outputs."""


def require_distinct_candidate_images(records: list[dict],
                                      expected_names: tuple[str, ...]) -> None:
    """Reject a six-EXE bundle reusing any byte-identical image.

    `records` must be the ordered, internally constructed records already bound
    to their on-descriptor digests. Never use paths or executable-provided
    labels as the authority for the expected product set. A forged hash is not
    detected by this function; the independent manifest/PE gate remains needed.
    """
    valid = False
    try:
        if (type(expected_names) is tuple and len(expected_names) == 6
                and all(type(name) is str and name for name in expected_names)
                and len(set(expected_names)) == 6
                and type(records) is list and len(records) == 6):
            names = []
            hashes = []
            for record in records:
                if type(record) is not dict:
                    break
                name = record.get("name")
                digest = record.get("sha256")
                if (type(name) is not str or type(digest) is not str
                        or _SHA256.fullmatch(digest) is None):
                    break
                names.append(name)
                hashes.append(digest)
            valid = (len(names) == 6 and tuple(names) == expected_names
                     and len(set(hashes)) == 6)
    except Exception:
        # No untrusted local path, OS message, or exception chain escapes.
        valid = False
    if not valid:
        raise CandidateIdentityError("Six Windows candidate images must be distinct")
