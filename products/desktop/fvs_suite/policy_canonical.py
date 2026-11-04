"""Bounded NFC-only edit navigation for Policy Delta Desk.

Inputs are source-owned unified-diff hunk records, not legal clauses. The
exact source text and byte hashes remain the authority for any human review.
"""
from __future__ import annotations

import unicodedata


def render_local_canonical_evidence(hunks: list[dict]) -> str:
    """Cite unique NFC-equivalent *changed* lines within each existing hunk.

    Do not pair ambiguous duplicates, compare across distinct hunks, or
    interpret Unicode normalization as semantic/legal equivalence. This is
    deliberately an index over already-computed physical diff coordinates.
    """
    candidates: list[tuple[int, int, int]] = []
    for hunk_number, hunk in enumerate(hunks, 1):
        removed: dict[str, list[tuple[int, str]]] = {}
        added: dict[str, list[tuple[int, str]]] = {}
        for number, raw in hunk["removed_sources"]:
            removed.setdefault(unicodedata.normalize("NFC", raw), []).append((number, raw))
        for number, raw in hunk["added_sources"]:
            added.setdefault(unicodedata.normalize("NFC", raw), []).append((number, raw))
        for normalized in removed.keys() & added.keys():
            old_group, new_group = removed[normalized], added[normalized]
            if len(old_group) != 1 or len(new_group) != 1:
                continue  # No defensible one-to-one physical source citation.
            old_number, old_raw = old_group[0]
            new_number, new_raw = new_group[0]
            if old_raw != new_raw:
                candidates.append((hunk_number, old_number, new_number))
    if not candidates:
        return ""
    candidates.sort()
    result = [
        "LOCAL REVIEW: NFC-only canonical Unicode changes at cited physical "
        "source lines, including mixed revisions. These are navigation cues, "
        "NOT legal or semantic equivalence; inspect both original files. "
        "Ambiguous duplicate lines are intentionally not paired.\n"
    ]
    for hunk, before, after in candidates[:16]:
        result.append(
            f"Canonical hunk {hunk:03d}: before L{before}; after L{after}; "
            "NFC-only candidate; human review.\n"
        )
    if len(candidates) > 16:
        result.append(
            f"LOCAL REVIEW: +{len(candidates) - 16} additional canonical "
            "candidate pair(s) omitted from bounded navigation.\n"
        )
    return "".join(result) + "\n"
