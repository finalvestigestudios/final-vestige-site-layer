#!/usr/bin/env python3
"""R233: freeze every optional editorial hub input before/after draft replay.

The authenticated build.py reads content/hubs/<section>.body.html directly.
Without a frozen directory roster and byte identities, modified hub copy and
newly generated matching HTML can pass R232's exact-render replay. This read-only
gate is *not* publication, independent QD, source, or safety approval.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

HOLD = 'DRAFT_HARD_HOLD'
# Authenticated from the R232 base commit 2b686cffda69c125e8f1ab1f1b8a647dd6be6778.
# Absence is significant: adding a new optional hub is a reviewable source change.
FROZEN_HUB_INPUTS = {
    'start-here.body.html': 'e1e749169a58e35a32c1d48ee8c46c209630965b',
}
_NAME = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\.body\.html\Z')
_SHA = re.compile(r'[0-9a-f]{40}\Z')


def _git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def _verify(root: Path, expected: dict[str, str]) -> dict:
    """Validate a complete directory snapshot (synthetic expected map in tests)."""
    if type(expected) is not dict or not expected:
        raise ValueError('R233 invalid frozen hub manifest')
    for name, sha in expected.items():
        if (type(name) is not str or _NAME.fullmatch(name) is None
                or type(sha) is not str or _SHA.fullmatch(sha) is None):
            raise ValueError('R233 malformed hub source identity')
    if not isinstance(root, Path):
        raise ValueError('R233 invalid Preparedness root')
    content = root / 'content'
    hub_dir = content / 'hubs'
    if (root.is_symlink() or content.is_symlink() or hub_dir.is_symlink()
            or not root.is_dir() or not content.is_dir() or not hub_dir.is_dir()):
        raise ValueError('R233 missing/symlinked hub directory')
    members = list(hub_dir.iterdir())
    observed = {p.name for p in members}
    if observed != set(expected) or len(members) != len(expected):
        raise ValueError('R233 hub source membership drift missing='
                         + repr(sorted(set(expected) - observed))
                         + ' extra=' + repr(sorted(observed - set(expected))))
    for name in sorted(expected):
        path = hub_dir / name
        if path.is_symlink() or not path.is_file():
            raise ValueError('R233 unsafe hub input member: ' + name)
        raw = path.read_bytes()
        if _git_blob(raw) != expected[name]:
            raise ValueError('R233 hub source byte identity drift: ' + name)
        try:
            raw.decode('utf-8', 'strict')
        except UnicodeDecodeError as exc:
            raise ValueError('R233 non-UTF8 editorial hub: ' + name) from exc
    return {'state': HOLD, 'hub_input_files_verified': len(expected),
            'release_authorized': False, 'independent_qd_pass': False,
            'source_or_medical_safety_approved': False, 'commercial_approval': False}


def verify_hub_inputs(root: Path) -> dict:
    """Production API: the caller cannot override the frozen source identities."""
    return _verify(root, FROZEN_HUB_INPUTS)
