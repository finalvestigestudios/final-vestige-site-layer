#!/usr/bin/env python3
"""R370 fail-closed, read-only Tool #104 print-disclosure remediation candidate.

Produces a review-only unified diff, never changes the source tree, never grants
publication, medical, child-privacy, physical-print, QD or merchant approval.
"""
from __future__ import annotations
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import re
import sys

SCHEMA = 'fv-preparedness-r370-print-candidate-v1'
PATH = 'content/tools/family-reunification-card.body.html'
META = 'content/tools/family-reunification-card.meta.json'
EXPECTED_BODY = 'be8698ac5d020476ff649d85813810e2000c6f98'
EXPECTED_META = '47da1e7e20e39f0ea85e26d54a8d58301f6e0a15'
NOTICE = ('A printed card can be lost. Anyone who finds it can read it. '
          "Do not put a child's full name, a home address, a government ID number, "
          'a medical diagnosis or a password on it.')
JS_OLD = "pr.appendChild(el('p', 'pa-printpage-note', 'Cut out each card and fold it on the dotted line to wallet size. Keep the card with you. Review it each year.'));"
JS_NEW = "pr.appendChild(el('p', 'pa-printpage-note', '" + NOTICE.replace("'", "\\'") + " Cut out each card and fold it on the dotted line to wallet size. Keep the card with you. Review it each year.'));"
NOJS_OLD = '<noscript><div class="pa-printsheet"><div class="pa-foldcard">'
NOJS_NEW = '<noscript><div class="pa-printsheet"><p class="pa-printpage-note">' + NOTICE + '</p><div class="pa-foldcard">'
COPY_OLD = 'The form below still works and prints. Only the automatic reminders and the text download need JavaScript.'
COPY_NEW = 'Automatic card generation needs JavaScript. Print the blank fold-over card below and fill it in by hand. The form is disabled without JavaScript.'
CHECKS = {
    'source_print_warning': 'A printed card can be lost',
    'print_hidden_alert': '.pa-card-mainhide { display: none !important; }',
    'print_page_note': '.pa-printpage-note { display: block;',
    'original_nojs_disabled': '<noscript><style>#rc, #rc-warn { display: none; }</style></noscript>',
    'form': '<form class="pa-sheet pa-card-mainhide" id="rc" onsubmit="return false"',
    'render': 'function render() {',
    'source_citation': '{{cite:shelter-cdc-reunification}}',
}
RELEASE_FLAGS = {key: False for key in (
    'may_merge','may_publish','qd_pass','privacy_approved','emergency_approved',
    'physical_print_verified','card_cutout_warning_verified','native_build_verified',
    'verified_paid_orders','verified_net_revenue')}


def git_blob(content: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()


def exactly_once(text: str, old: str) -> None:
    if text.count(old) != 1:
        raise ValueError('expected_exactly_one_match:' + old[:48])


def build_candidate(original: str) -> str:
    """Construct a reproducible private candidate; never mutate original in place."""
    for label, needle in CHECKS.items():
        if needle not in original:
            raise ValueError('missing_source_guard:' + label)
    for old in (JS_OLD, NOJS_OLD, COPY_OLD):
        exactly_once(original, old)
    candidate = original.replace(JS_OLD, JS_NEW).replace(NOJS_OLD, NOJS_NEW).replace(COPY_OLD, COPY_NEW)
    for old in (JS_OLD, NOJS_OLD, COPY_OLD):
        if old in candidate:
            raise ValueError('old_text_survived')
    if candidate.count(NOJS_NEW) != 1 or candidate.count(JS_NEW) != 1:
        raise ValueError('printed_notice_missing_or_duplicate')
    if candidate.count('{{cite:') != original.count('{{cite:'):
        raise ValueError('citation_occurrence_change')
    if re.findall(r'{{cite:[^}]+}}',candidate) != re.findall(r'{{cite:[^}]+}}', original):
        raise ValueError('citation_order_change')
    for needle in ('.pa-card-mainhide { display: none !important; }',
                   '<noscript><style>#rc, #rc-warn { display: none; }</style></noscript>',
                   '<form class="pa-sheet pa-card-mainhide" id="rc" onsubmit="return false"'):
        if candidate.count(needle) != original.count(needle):
            raise ValueError('source_control_modified')
    if len(candidate) - len(original) > 900 or len(candidate) <= len(original):
        raise ValueError('unexpected_patch_size')
    return candidate


def review(root: Path) -> dict:
    out = dict(schema=SCHEMA, status='INVALID_HARD_HOLD', errors=[], evidence={}, **RELEASE_FLAGS)
    root = root.resolve()
    try:
        body_path, meta_path = root / PATH, root / META
        # Reject symlinks and paths outside the exact local source tree.
        if body_path.is_symlink() or meta_path.is_symlink():
            raise ValueError('symlink_source_refused')
        body, meta = body_path.read_bytes(), meta_path.read_bytes()
        original_sha, meta_sha = git_blob(body), git_blob(meta)
        out['evidence'].update(source_blob=original_sha, metadata_blob=meta_sha)
        if original_sha != EXPECTED_BODY or meta_sha != EXPECTED_META:
            raise ValueError('source_ref_changed_requires_manual_rebase')
        data = json.loads(meta)
        if (data.get('n') != 104 or data.get('status') != {'editorial':'drafted','publish':'draft'}
                or data.get('safety_review',{}).get('state') != 'pending'):
            raise ValueError('draft_pending_safety_state_changed')
        original = body.decode('utf-8')
        candidate = build_candidate(original)
        diff = ''.join(difflib.unified_diff(
            original.splitlines(keepends=True), candidate.splitlines(keepends=True),
            fromfile='a/preparedness/' + PATH, tofile='b/preparedness/' + PATH))
        if diff.count('@@') < 2 or not diff:
            raise ValueError('missing_review_diff')
        out['evidence'].update(candidate_sha256=hashlib.sha256(candidate.encode()).hexdigest(),
                               diff_sha256=hashlib.sha256(diff.encode()).hexdigest(),
                               changed_bytes=len(candidate)-len(original),
                               citation_occurrences=original.count('{{cite:'),
                               original_unchanged=(git_blob(body_path.read_bytes()) == original_sha),
                               proposal_only=True)
        out['evidence']['review_diff'] = diff
        out['status'] = 'REVIEW_REQUIRED_HARD_HOLD'
    except (OSError, ValueError, UnicodeError, KeyError, TypeError, json.JSONDecodeError) as exc:
        out['errors'].append(type(exc).__name__ + ':' + str(exc))
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    args=p.parse_args(argv)
    print(json.dumps(review(args.root), sort_keys=True, indent=2))
    return 2  # Intentional publication hard hold even if review candidate was formed.

if __name__ == '__main__':
    sys.exit(main())
