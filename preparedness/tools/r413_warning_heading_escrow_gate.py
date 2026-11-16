#!/usr/bin/env python3
"""R413: original warning-qualifier and section-heading preservation escrow.

Read-only structural review on top of R412.  PRESENCE IS NOT SAFETY: a copied
warning may still be inaccurate, incomplete, contradicted or out of scope.
Never selects a branch/fork, publishes content or reports qualified clearance.
"""
from __future__ import annotations

import argparse
from collections import Counter
from html.parser import HTMLParser
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re

_spec = spec_from_file_location('r412_baseline_citation_gate', Path(__file__).with_name('r412_baseline_citation_gate.py'))
_r412 = module_from_spec(_spec)
_spec.loader.exec_module(_r412)

# Literal tokens, not medical or legal classification. Intentional overcapture
# makes borderline omissions visible to a human rather than quietly passing.
QUALIFIERS = frozenset('''not no never cannot can't don't shouldn't wouldn't must mustn't only except unless until avoid discard unsafe dangerous danger emergency 911 poison medical infant child children pregnant allergy contaminated boil boiling refrigerate refrigerated reheat thaw thawing cooked temperature evacuate evacuation shelter contact call stop warning caution prohibited required immediately'''.split())
HEADING = re.compile(r'^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$', re.M)
TOKEN = _r412._r411.WORD


def lexical_tokens(text):
    return tuple(w.casefold() for w in TOKEN.findall(text))


class HeadingHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.headings = []
        self.active = None
    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in {f'h{i}' for i in range(1, 7)}:
            if self.active is not None:
                raise ValueError('nested original headings require human review')
            self.active = [tag, []]
        if tag not in _r412._r411.VOID:
            self.stack.append(tag)
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in _r412._r411.VOID:
            self.handle_endtag(tag)
    def handle_data(self, data):
        if self.active is not None:
            self.active[1].append(data)
    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in _r412._r411.VOID:
            raise ValueError('invalid close tag for void element')
        if not self.stack or self.stack[-1] != tag:
            raise ValueError('unbalanced heading source HTML')
        self.stack.pop()
        if self.active is not None and self.active[0] == tag:
            self.headings.append(lexical_tokens(' '.join(self.active[1])))
            self.active = None
    def finish(self):
        self.close()
        if self.active or self.stack:
            raise ValueError('unclosed heading source HTML')
        return self.headings


def headings(data: bytes | str):
    if isinstance(data, bytes):
        txt = data.decode('utf-8', 'strict')
    elif isinstance(data, str):
        txt = data
    else:
        raise ValueError('invalid source heading type')
    if re.search(r'<(?:article|section|p|h[1-6]|div)\b', txt[:2000], re.I):
        parser = HeadingHTML()
        parser.feed(txt)
        return parser.finish()
    return [lexical_tokens(line) for line in HEADING.findall(txt)]


def warning_windows(words, radius=7):
    """Count literal context around every risk/qualifier token, not just token totals."""
    words = tuple(w.casefold() for w in words)
    return Counter(tuple(words[max(0, i-radius):min(len(words), i+radius+1)])
                   for i, token in enumerate(words) if token in QUALIFIERS)


def check(original, manifest, exports, candidates, *, raw_original=None, test_only=False):
    """Fail closed if any original qualifier context or section heading is lost.

    Receipts include counts and blob pins only, never private article excerpts.
    """
    base = _r412.check(original, manifest, exports, candidates,
                       raw_original=raw_original, test_only=test_only)
    errors = list(base.get('errors', []))
    details = []
    try:
        if not isinstance(original, dict) or not isinstance(exports, dict) or not isinstance(candidates, dict):
            raise ValueError('originals, exports and candidate escrow must be mappings')
        for entry in original['original_articles']:
            slug = entry['slug']
            pair = exports.get(slug)
            if not isinstance(pair, (tuple, list)) or len(pair) != 2:
                errors.append('R413 missing paired output: ' + str(slug)); continue
            renders = []
            for html in pair:
                if isinstance(html, bytes):
                    html = html.decode('utf-8', 'strict')
                if not isinstance(html, str) or not 0 < len(html.encode('utf-8')) <= 1_000_000:
                    raise ValueError('invalid output HTML')
                p = _r412.CitationAccessibilityHTML()
                p.feed(html)
                p.finish()
                renders.append((tuple(w.casefold() for w in p.visible_words), headings(html)))
            if renders[0] != renders[1]:
                errors.append('R413 output qualifier/heading parity changed: ' + slug)
            for pin in set(entry['body_candidate_git_blobs']):
                data = candidates.get((slug, pin))
                if not isinstance(data, bytes) or _r412._r409.blob(data) != pin:
                    errors.append('R413 unverified original candidate: ' + slug); continue
                src = tuple(_r412.source_words(data))
                protected = warning_windows(src)
                lost = protected - warning_windows(renders[0][0])
                original_headings = headings(data)
                missing_headings = sum((Counter(original_headings)-Counter(renders[0][1])).values())
                # Cumulative counters alone could hide heading reordering.
                if original_headings:
                    j = 0
                    for h in renders[0][1]:
                        if j < len(original_headings) and h == original_headings[j]:
                            j += 1
                    if j != len(original_headings):
                        missing_headings = max(missing_headings, len(original_headings)-j)
                if lost:
                    errors.append('R413 original safety/qualifier context changed or omitted: ' + slug + ' @ ' + pin)
                if missing_headings:
                    errors.append('R413 original heading text/order changed or omitted: ' + slug + ' @ ' + pin)
                details.append({'slug': slug, 'original_blob': pin, 'protected_windows': sum(protected.values()),
                                'missing_windows': sum(lost.values()), 'baseline_headings': len(original_headings),
                                'missing_or_reordered_headings': missing_headings, 'human_review_required': True})
    except (ValueError, TypeError, KeyError, UnicodeError, AttributeError, OverflowError) as exc:
        errors.append('R413 missing/malformed evidence: ' + str(exc))
    return {'release_state': 'DRAFT_HARD_HOLD', 'eligible': False,
            'publication_approved': False, 'qualified_safety_approved': False,
            'integrity_ok': bool(base.get('integrity_ok')) and not errors,
            'errors': sorted(set(errors)), 'original_candidates_inspected': len(details),
            'details': details, 'warnings': list(base.get('warnings', [])) + [
                'Literal qualifier/heading retention is NOT factual source support or safety adjudication',
                'All original forks remain unselected; no QD PASS or CMS/merchant publication authorization']}


def main():
    p = argparse.ArgumentParser(description='R413 warning and heading integrity, ALWAYS DRAFT HARD HOLD')
    p.add_argument('original', type=Path)
    p.add_argument('manifest', type=Path)
    p.add_argument('export_root', type=Path)
    p.add_argument('private_candidate_root', type=Path)
    a = p.parse_args()
    try:
        raw = _r412._r409.read_original(a.original)
        original = json.loads(raw.decode('utf-8'), object_pairs_hook=_r412._r409.unique_pairs)
        manifest = json.loads(_r412._r409.read_original(a.manifest).decode('utf-8'),
                              object_pairs_hook=_r412._r409.unique_pairs)
        exports, candidates = {}, {}
        for entry in original['original_articles']:
            slug = entry['slug']
            if not isinstance(slug, str) or not _r412._r411._r410.SLUG.fullmatch(slug):
                raise ValueError('unsafe article slug')
            exports[slug] = (_r412._r409.read_original(a.export_root/'wordpress'/(slug+'.html')),
                             _r412._r409.read_original(a.export_root/'preview'/(slug+'.html')))
            for sha in set(entry['body_candidate_git_blobs']):
                if not isinstance(sha, str) or not _r412.HEX40.fullmatch(sha):
                    raise ValueError('unsafe original SHA')
                candidates[(slug, sha)] = _r412.checked_candidate_read(
                    a.private_candidate_root/slug/(sha+'.txt'), root=a.private_candidate_root)
        result = check(original, manifest, exports, candidates, raw_original=raw)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, UnicodeError, OverflowError) as exc:
        result = {'release_state': 'DRAFT_HARD_HOLD', 'eligible': False,
                  'publication_approved': False, 'qualified_safety_approved': False,
                  'integrity_ok': False, 'errors': [str(exc)]}
    print(json.dumps(result, sort_keys=True, indent=2))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
