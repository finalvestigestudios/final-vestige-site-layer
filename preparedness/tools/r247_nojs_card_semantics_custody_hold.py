#!/usr/bin/env python3
"""R247: immutable, read-only no-JS card copy/DOM evidence HOLD, not browser QA.

No unreviewed advice, live CMS content, personal inputs, or release state is changed.
Passing structural checks preserves a disputed original; it never grants approval.
"""
from __future__ import annotations

import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

HOLD = 'DRAFT_HARD_HOLD'
SOURCES = {
    'content/articles/family-communication-plan.body.html': '8ac8bd7dba3be15d477c15737e54d83364d72527',
    'content/tools/family-reunification-card.body.html': 'be8698ac5d020476ff649d85813810e2000c6f98',
    'content/tools/family-reunification-card.meta.json': '47da1e7e20e39f0ea85e26d54a8d58301f6e0a15',
    'tools/reunion_card.js': 'b1a09b1eda1ae26f081de65b400a37bc19538035',
}
A, T, M, J = SOURCES
LABELS = (
    'Household', 'Phone', 'Out-of-area contact', 'Out-of-area phone',
    'Meet first at', 'If not, meet at', 'School or childcare',
    'Reunification plan', 'Pick-up reminder', 'Caregiver',
    'Caregiver phone', 'Communication needs', 'Reviewed',
)
CLAIM = 'The form below still works and prints.'
CSS = re.compile(r'#rc\s*,\s*#rc-warn\s*\{\s*display\s*:\s*none\s*;?\s*\}', re.I)


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


class NoscriptReader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks: list[list[str]] = []
        self.depth = 0
        self.forms: list[dict[str, str | None]] = []

    def handle_starttag(self, tag, attrs):
        if tag == 'noscript':
            if self.depth:
                raise ValueError('R247 nested no-JS block')
            self.depth = 1
            self.blocks.append([])
            return
        if tag == 'form' and not self.depth:
            self.forms.append(dict(attrs))
        if self.depth:
            self.blocks[-1].append('<' + tag + ''.join(' ' + k + '="' + str(v) + '"' for k, v in attrs) + '>')

    def handle_startendtag(self, tag, attrs):
        if self.depth:
            self.blocks[-1].append('<' + tag + '/>')

    def handle_endtag(self, tag):
        if tag == 'noscript':
            if self.depth != 1:
                raise ValueError('R247 unmatched no-JS closing tag')
            self.depth = 0
        elif self.depth:
            self.blocks[-1].append('</' + tag + '>')

    def handle_data(self, data):
        if self.depth:
            self.blocks[-1].append(data)


def inspect(inputs: dict[str, bytes], pins: dict[str, str] | None = None) -> dict:
    pins = SOURCES if pins is None else pins
    if type(inputs) is not dict or type(pins) is not dict or set(inputs) != set(SOURCES) or set(pins) != set(SOURCES):
        raise ValueError('R247 exact four-source roster required')
    sources = {}
    for path in SOURCES:
        raw = inputs[path]
        if type(raw) is not bytes or not 0 < len(raw) < 3_000_000 or b'\x00' in raw:
            raise ValueError('R247 source bytes invalid')
        if git_blob(raw) != pins[path]:
            raise ValueError('R247 source identity changed; require review')
        sources[path] = raw.decode('utf-8', 'strict')
    meta = json.loads(sources[M])
    if (type(meta) is not dict or type(meta.get('n')) is not int or meta['n'] != 104
            or meta.get('status', {}).get('publish') != 'draft'
            or meta.get('safety_review', {}).get('state') != 'pending'):
        raise ValueError('R247 release state changed')
    tool = sources[T]
    parser = NoscriptReader()
    parser.feed(tool)
    parser.close()
    if parser.depth or len(parser.blocks) != 3:
        raise ValueError('R247 original no-JS block count/structure drift')
    if len(parser.forms) != 1 or parser.forms[0].get('id') != 'rc':
        raise ValueError('R247 original form identity drift')
    blocks = [''.join(b) for b in parser.blocks]
    notices = [b for b in blocks if CLAIM in b]
    fallbacks = [b for b in blocks if 'pa-foldcard' in b]
    hiding = [b for b in blocks if CSS.search(b)]
    if len(notices) != 1 or len(fallbacks) != 1 or len(hiding) != 1:
        raise ValueError('R247 original no-JS copy/fallback/CSS evidence changed')
    if len({blocks.index(notices[0]), blocks.index(fallbacks[0]), blocks.index(hiding[0])}) != 3:
        raise ValueError('R247 original no-JS evidence no longer independent')
    if '<input' in fallbacks[0].lower() or '<script' in fallbacks[0].lower():
        raise ValueError('R247 static card fallback replaced with interactive content')
    found = re.findall(r'<b>\s*([^<:]+):\s*</b>', fallbacks[0], re.I)
    if tuple(found) != LABELS:
        raise ValueError('R247 no-JS full-card label inventory drift')
    js_front = re.search(r'var\s+front\s*=\s*keep\s*\(\s*\[(.*?)\]\s*\)\s*;', sources[J], re.S)
    if not js_front:
        raise ValueError('R247 original minimal-card model structure changed')
    front = js_front.group(1)
    hh = front.find('row("Household", c.hhName)')
    ph = front.find('row("Phone", c.hhPhone)')
    minimum = front.find('minimal ? null')
    if not (0 <= hh < ph < minimum):
        raise ValueError('R247 minimal print household identifier witness changed')
    if 'keeps what you type on your own device' not in sources[A]:
        raise ValueError('R247 linked article privacy promise changed')
    witness_ids = ['NOJS_FORM_WORKS_COPY', 'NOJS_FORM_HIDDEN_CSS',
                   'NOJS_FULL_BLANK_FALLBACK', 'MINIMAL_HOUSEHOLD_ROWS',
                   'ARTICLE_PRIVACY_SCOPE_UNVERIFIED']
    receipt = hashlib.sha256(('\n'.join(f'{p}:{git_blob(inputs[p])}' for p in SOURCES)
                              + '\n' + '\n'.join(witness_ids)).encode()).hexdigest()
    return {
        'state': HOLD, 'issue': 136, 'conversion_issue': 820,
        'source_count': 4, 'nojs_block_count': 3, 'blank_fallback_field_count': len(found),
        'held_witnesses': witness_ids, 'held_witness_count': len(witness_ids),
        'receipt_sha256': receipt,
        'nojs_copy_conflicts_with_hidden_form': True,
        'minimal_identifier_disclosure_requires_review': True,
        'nojs_browser_print_verified': False, 'privacy_certified': False,
        'claims_adjudicated': False, 'source_review_approved': False,
        'independent_qd_pass': False, 'release_authorized': False,
        'merchant_approved': False, 'human_review_required': True,
    }


def audit(root: Path, safe_read) -> dict:
    return inspect({p: safe_read(root, p) for p in SOURCES})

