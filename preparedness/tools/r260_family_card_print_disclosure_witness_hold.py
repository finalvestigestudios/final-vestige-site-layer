#!/usr/bin/env python3
"""R260 read-only witness of original Tool #104's screen/print privacy-disclosure gap.

This is an integrity and review-queue gate, NOT a CSS/browser rendering test or
privacy, source, medical, QD, checkout or publication approval. Never normalise
away the observed print omission; changing original bytes requires new review.
"""
from __future__ import annotations

import hashlib
import re

SCHEMA = 'fv-preparedness-r260-print-disclosure-witness-v1'
HOLD = 'DRAFT_HARD_HOLD'
BODY_PATH = 'content/tools/family-reunification-card.body.html'
BODY_BLOB = 'be8698ac5d020476ff649d85813810e2000c6f98'
LABELS = (
    'Household:', 'Phone:', 'Out-of-area contact:', 'Out-of-area phone:',
    'Meet first at:', 'If not, meet at:', 'School or childcare:',
    'Reunification plan:', 'Pick-up reminder:', 'Caregiver:',
    'Caregiver phone:', 'Communication needs:', 'Reviewed:',
)


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def print_css(text: str) -> str:
    """Extract only balanced @media print scopes, not screen-only rules."""
    styles = re.findall(r'<style(?:\s[^>]*)?>(.*?)</style\s*>', text, re.I | re.S)
    if not styles:
        raise ValueError('R260 no style blocks')
    blocks = []
    for style in styles:
        clean = re.sub(r'/\*.*?\*/', '', style, flags=re.S)
        for match in re.finditer(r'@media\s+print\s*\{', clean, re.I):
            depth, pos = 1, match.end()
            start = pos
            while pos < len(clean) and depth:
                if clean[pos] == '{':
                    depth += 1
                elif clean[pos] == '}':
                    depth -= 1
                pos += 1
            if depth:
                raise ValueError('R260 unclosed print media block')
            blocks.append(clean[start:pos - 1])
    if not blocks:
        raise ValueError('R260 no print media block')
    return '\n'.join(blocks)


def rule_hides(css: str, selector: str) -> bool:
    # Only a literal whole-class selector; this audits original authored source,
    # not a browser CSSOM or computed style across all possible nested rules.
    pattern = r'(?<![\w-])\.' + re.escape(selector) + r'\s*\{([^{}]*)\}'
    return any(re.search(r'(?<![\w-])display\s*:\s*none\s*!important\b', m.group(1), re.I)
               for m in re.finditer(pattern, css, re.I | re.S))


def inspect(raw: bytes, *, expected_blob: str = BODY_BLOB) -> dict:
    if type(raw) is not bytes or not raw or len(raw) > 3_000_000 or b'\0' in raw:
        raise ValueError('R260 invalid original body bytes')
    if type(expected_blob) is not str or not re.fullmatch('[0-9a-f]{40}', expected_blob):
        raise ValueError('R260 invalid custody pin')
    actual = git_blob(raw)
    if actual != expected_blob:
        raise ValueError('R260 original body identity changed')
    text = raw.decode('utf-8', 'strict')
    css = print_css(text)
    if not rule_hides(css, 'pa-card-mainhide'):
        raise ValueError('R260 observed print-hide rule changed; re-review CSS')
    screen_alert = re.search(
        r'<div\b(?=[^>]*\bclass\s*=\s*["\x27][^"\x27]*\bpa-alert--stop\b[^"\x27]*["\x27])'
        r'(?=[^>]*\bclass\s*=\s*["\x27][^"\x27]*\bpa-card-mainhide\b[^"\x27]*["\x27])'
        r'[^>]*>(.*?)</div\s*>', text, re.I | re.S)
    if not screen_alert:
        raise ValueError('R260 original privacy alert missing or no longer print-hidden')
    if not all(phrase in screen_alert.group(1) for phrase in (
            'A printed card can be lost', 'Anyone who finds it can read it.',
            "a child's full name", 'a medical diagnosis', 'a password')):
        raise ValueError('R260 observed screen privacy warning altered')
    note = re.search(r"el\(\s*['\"]p['\"]\s*,\s*['\"]pa-printpage-note['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)", text)
    if not note or not all(x in note.group(1) for x in ('Cut out each card', 'Review it each year.')):
        raise ValueError('R260 original JavaScript print-page note changed')
    if re.search(r'\b(?:lost|private|privacy|password|medical|child|school|confidential)\b', note.group(1), re.I):
        raise ValueError('R260 print note may now include disclosure; re-review required')
    fallback = re.search(r'<noscript\s*>\s*<div\b[^>]*\bclass="pa-printsheet"[^>]*>(.*?)</div>\s*</noscript\s*>',
                         text, re.I | re.S)
    if not fallback:
        raise ValueError('R260 no-JS print fallback structure changed')
    labels = re.findall(r'<b>([^<]+)</b>', fallback.group(1), re.I)
    if labels != list(LABELS):
        raise ValueError('R260 13-field no-JS fallback changed')
    if re.search(r'\b(?:lost|private|privacy|password|diagnosis|confidential)\b',
                 fallback.group(1), re.I):
        raise ValueError('R260 no-JS fallback disclosure may have changed; review')
    if 'The form below still works and prints.' not in text:
        raise ValueError('R260 original no-JS contradictory copy altered')
    return {
        'schema': SCHEMA, 'state': HOLD, 'source_path': BODY_PATH,
        'source_git_blob': actual, 'print_css_hides_original_privacy_alert': True,
        'screen_only_warning_observed': True,
        'javascript_print_note_lacks_privacy_warning': True,
        'nojs_print_fallback_field_count': len(labels),
        'nojs_print_fallback_lacks_privacy_warning': True,
        'nojs_form_print_claim_requires_review': True,
        'human_editorial_and_privacy_review_required': True,
        'browser_print_verified': False, 'privacy_certified': False,
        'medical_safety_verified': False, 'source_review_approved': False,
        'independent_qd_pass': False, 'merchant_approved': False,
        'release_authorized': False,
    }


def audit(root, safe_read):
    return inspect(safe_read(root, BODY_PATH))
