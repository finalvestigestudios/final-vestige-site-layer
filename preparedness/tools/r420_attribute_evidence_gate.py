#!/usr/bin/env python3
"""R420: review gate for non-text-node claims and invisible HTML presentation.

R419 conserves text nodes; text in alt/title/ARIA/tooltip/form-default attributes
and CSS-generated content is not in those text nodes. This additive, read-only
inspection requires exact original-candidate custody of meaningful attributes,
rejects high-risk embedded/dynamic presentation, and never grants safety/QD or
publishing approval. Results disclose counts and hashes, not private article text.

False positives require a qualified human review, not an automatic exemption.
CSS external to these exports and actual browser behavior remain untested.
"""
from __future__ import annotations
import argparse
from collections import Counter
from html.parser import HTMLParser
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re
import sys

_spec = spec_from_file_location('r419_unbound_evidence_gate',
                              Path(__file__).with_name('r419_unbound_evidence_gate.py'))
_r419 = module_from_spec(_spec)
sys.modules[_spec.name] = _r419
_spec.loader.exec_module(_r419)
_r409, _r412, _r414, _r418 = _r419._r409, _r419._r412, _r419._r414, _r419._r418
VOID = _r419.VOID
TEXT_ATTRS = frozenset({'alt', 'title', 'aria-label', 'aria-description',
    'aria-valuetext', 'placeholder', 'data-tooltip', 'data-title',
    'data-content', 'data-help', 'data-instruction'})
EMBEDDED = frozenset({'iframe', 'object', 'embed', 'applet'})
STYLE_RISK = re.compile(r'(?:\bcontent\s*:|@import\b|\bdisplay\s*:\s*none\b|'
    r'\bvisibility\s*:\s*hidden\b|\bopacity\s*:\s*0(?:\.0+)?\s*(?:;|$)|'
    r'\bfont-size\s*:\s*0(?:px|rem|em|pt|%)?\b|\bclip-path\s*:|'
    r'\btext-indent\s*:\s*-|\bcolor\s*:\s*transparent\b|'
    r'\b-webkit-text-fill-color\s*:\s*transparent\b)', re.I)
MAX_ATTRIBUTES = 12000
MAX_VALUE_CHARS = 8192


def normalize_value(value):
    if not isinstance(value, str) or len(value) > MAX_VALUE_CHARS:
        raise ValueError('missing, nontext, or oversized evidence attribute')
    if any(ord(c) < 32 and c not in '\t\r\n' for c in value):
        raise ValueError('control character in evidence attribute')
    return ' '.join(value.split()).casefold()


class AttributeInspector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.labels = []
        self.risks = []
        self.style_depth = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.casefold()
        names = [k.casefold() for k, _ in attrs]
        if len(names) != len(set(names)):
            raise ValueError('duplicate evidence HTML attributes')
        a = dict((k.casefold(), v) for k, v in attrs)
        if tag in EMBEDDED:
            self.risks.append('embedded remote or HTML content')
        if tag == 'meta' and (a.get('http-equiv') or '').casefold() == 'refresh':
            self.risks.append('HTML auto-redirect')
        if 'srcdoc' in a:
            self.risks.append('nested srcdoc HTML')
        if any(n.startswith('on') for n in names):
            self.risks.append('inline event handler')
        if 'style' in a and STYLE_RISK.search(a['style'] or ''):
            self.risks.append('inline CSS can hide or synthesize reader text')
        for name in sorted(TEXT_ATTRS):
            if name in a:
                val = normalize_value(a[name])
                if val:
                    self.labels.append((tag, name, val))
        if tag in {'button', 'input', 'option'} and 'value' in a:
            typ = (a.get('type') or '').casefold()
            if typ not in {'hidden', 'password'}:
                val = normalize_value(a['value'])
                if val:
                    self.labels.append((tag, 'value', val))
        if len(self.labels) > MAX_ATTRIBUTES:
            raise ValueError('evidence attribute budget exceeded')
        if tag not in VOID:
            self.stack.append(tag)
            if tag == 'style':
                self.style_depth += 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.casefold() not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        tag = tag.casefold()
        if tag in VOID or not self.stack or self.stack[-1] != tag:
            raise ValueError('unbalanced evidence attribute HTML')
        self.stack.pop()
        if tag == 'style':
            self.style_depth -= 1

    def handle_data(self, data):
        if self.style_depth and STYLE_RISK.search(data):
            self.risks.append('stylesheet can hide or synthesize reader text')

    def finish(self):
        self.close()
        if self.stack or self.style_depth:
            raise ValueError('unclosed evidence attribute HTML')
        return self


def inspect(data, *, candidate=False):
    if isinstance(data, bytes):
        data = data.decode('utf-8', 'strict')
    if not isinstance(data, str) or not 0 < len(data.encode('utf-8')) <= _r419.MAX_HTML_BYTES:
        raise ValueError('invalid HTML attribute evidence input')
    if candidate and _r419.is_markdown_original(data):
        # Markdown originals are source text, not rendered HTML attributes.
        return AttributeInspector()
    p = AttributeInspector()
    p.feed(data)
    return p.finish()


def attribute_fidelity(original, rendered):
    src, dst = inspect(original, candidate=True), inspect(rendered)
    old, new = Counter(src.labels), Counter(dst.labels)
    return {'original_attributes':sum(old.values()),
        'missing_attributes':sum((old-new).values()),
        'new_or_changed_attributes':sum((new-old).values()),
        'original_unsafe_presentation':len(src.risks),
        'rendered_unsafe_presentation':len(dst.risks)}


def check(original, manifest, exports, candidates, *, raw_original=None, test_only=False):
    parent = _r419.check(original, manifest, exports, candidates,
                         raw_original=raw_original, test_only=test_only)
    errors = list(parent.get('errors', []))
    details = []
    try:
        for entry in original['original_articles']:
            slug = entry['slug']
            if not isinstance(slug, str) or not _r414.SLUG.fullmatch(slug):
                raise ValueError('unsafe article slug')
            pair = exports[slug]
            if not isinstance(pair, (tuple, list)) or len(pair) != 2:
                raise ValueError('missing draft export pair')
            for pin in sorted(set(entry['body_candidate_git_blobs'])):
                body = candidates[(slug, pin)]
                if not isinstance(body, bytes) or _r409.blob(body) != pin:
                    errors.append('R420 original Git blob mismatch: '+slug)
                    continue
                for i, rendered in enumerate(pair):
                    channel = ('wordpress', 'private_preview')[i]
                    result = attribute_fidelity(body, rendered)
                    if result['missing_attributes'] or result['new_or_changed_attributes']:
                        errors.append('R420 original accessible/tooltip/visual attribute custody changed: '
                                      +slug+' @ '+pin+' '+channel)
                    if result['original_unsafe_presentation'] or result['rendered_unsafe_presentation']:
                        errors.append('R420 embedded, executable or deceptive visual presentation requires review: '
                                      +slug+' @ '+pin+' '+channel)
                    details.append({'slug':slug,'original_blob':pin,'channel':channel,
                                    **result,'qualified_human_review_required':True})
    except (ValueError, TypeError, KeyError, IndexError, UnicodeError,
            OverflowError, AttributeError, RecursionError) as exc:
        errors.append('R420 missing or malformed attribute provenance: '+str(exc))
    return {'release_state':'DRAFT_HARD_HOLD','eligible':False,
        'publication_approved':False,'qualified_safety_approved':False,
        'merchant_offer_verified':False,
        'integrity_ok':bool(parent.get('integrity_ok')) and not errors,
        'errors':sorted(set(errors)),'draft_checks':len(details),'details':details,
        'warnings':list(parent.get('warnings', []))+[
            'Attributes and CSS are mechanical provenance checks, not source-truth or medical-safety review',
            'External stylesheet/browser/a11y behavior remains unverified',
            'Legitimate alt text, tooltips or layout CSS changes require editorial review; HARD HOLD remains']}


def main():
    ap = argparse.ArgumentParser(description='R420 attribute evidence custody — NEVER PUBLISH')
    for name in ('original','manifest','export_root','private_candidate_root'):
        ap.add_argument(name,type=Path)
    args = ap.parse_args()
    try:
        raw = _r409.read_original(args.original)
        original = json.loads(raw.decode('utf-8'), object_pairs_hook=_r409.unique_pairs)
        manifest = json.loads(_r409.read_original(args.manifest).decode('utf-8'),
                              object_pairs_hook=_r409.unique_pairs)
        exports,candidates={},{}
        for entry in original['original_articles']:
            slug=entry['slug']
            if not isinstance(slug, str) or not _r414.SLUG.fullmatch(slug):
                raise ValueError('invalid original article slug')
            exports[slug]=(_r409.read_original(args.export_root/'wordpress'/(slug+'.html')),
                           _r409.read_original(args.export_root/'preview'/(slug+'.html')))
            for pin in set(entry['body_candidate_git_blobs']):
                if not isinstance(pin,str) or not _r418.HEX40.fullmatch(pin):
                    raise ValueError('invalid original candidate pin')
                candidates[(slug,pin)] = _r412.checked_candidate_read(
                    args.private_candidate_root/slug/(pin+'.txt'),
                    root=args.private_candidate_root)
        result = check(original,manifest,exports,candidates,raw_original=raw)
    except (OSError,ValueError,TypeError,KeyError,IndexError,UnicodeError,
            OverflowError,RecursionError) as exc:
        result={'release_state':'DRAFT_HARD_HOLD','eligible':False,
            'publication_approved':False,'qualified_safety_approved':False,
            'integrity_ok':False,'errors':[str(exc)]}
    print(json.dumps(result,sort_keys=True,indent=2))
    return 2

if __name__=='__main__':
    raise SystemExit(main())
