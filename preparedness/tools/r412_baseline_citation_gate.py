#!/usr/bin/env python3
"""R412 private original-variant depth escrow + reader-discernible citation check.

Only a read-only structural REVIEW gate. Original candidate bytes must be passed
by the reviewer from independently authenticated Git blobs; do not commit them.
Always DRAFT/HARD HOLD, even if all checks are structurally satisfactory.
"""
from __future__ import annotations

import argparse
from collections import Counter
from html.parser import HTMLParser
from importlib.util import module_from_spec, spec_from_file_location
import json
import os
from pathlib import Path
import re
import stat

_spec = spec_from_file_location('r411_visible_evidence_gate', Path(__file__).with_name('r411_visible_evidence_gate.py'))
_r411 = module_from_spec(_spec)
_spec.loader.exec_module(_r411)
_r409 = _r411._r410._r409
HEX40 = re.compile(r'[0-9a-f]{40}\Z')
LABEL_WORD = re.compile(r'\w+', re.UNICODE)
GENERIC_LABELS = {'here', 'click here', 'read more', 'link', 'more', 'learn more', 'source', 'click', 'details'}


class CitationAccessibilityHTML(_r411.VisibleEvidenceHTML):
    """Require link text a sighted/keyboard reader could identify as a source."""

    def __init__(self):
        super().__init__()
        self.anchors = []
        self.completed_anchors = []
        self._active_anchor = None

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attr = {k.lower(): v for k, v in attrs}
        if tag == 'a':
            if self._active_anchor is not None:
                self.errors.append('nested link text is ambiguous')
            if attr.get('tabindex') in ('-1', '-2', '-3') or 'disabled' in attr:
                self.errors.append('citation link removed from keyboard navigation')
            if (attr.get('aria-disabled') or '').lower() == 'true':
                self.errors.append('citation link ARIA-disabled')
            if (attr.get('role') or '').lower() in {'none', 'presentation', 'button'}:
                self.errors.append('citation link role misrepresents link')
            if 'download' in attr:
                self.errors.append('unapproved downloadable citation')
            if (attr.get('target') or '').lower() == '_blank':
                rel = set((attr.get('rel') or '').lower().split())
                if 'noopener' not in rel or 'noreferrer' not in rel:
                    self.errors.append('new-window citation lacks noopener/noreferrer')
            self._active_anchor = {'text': [], 'sid': attr.get('data-source-id'),
                                   'href': attr.get('href'), 'depth': len(self.stack),
                                   'start_hidden': self._is_hidden()}
        super().handle_starttag(tag, attrs)

    def handle_data(self, data):
        super().handle_data(data)
        if self._active_anchor is not None and not self._is_hidden():
            self._active_anchor['text'].append(data)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == 'a' and self._active_anchor is not None:
            a = self._active_anchor
            label = ' '.join(' '.join(a['text']).split())
            if not label or len(label) < 5 or not LABEL_WORD.search(label):
                self.errors.append('citation anchor has no discernible visible label')
            if label.casefold().strip(' .:!?') in GENERIC_LABELS:
                self.errors.append('citation anchor has only a generic label')
            if a['start_hidden']:
                self.errors.append('citation anchor starts concealed')
            self.completed_anchors.append((a['sid'], a['href'], label))
            self._active_anchor = None
        super().handle_endtag(tag)

    def finish(self):
        super().finish()
        if self._active_anchor is not None:
            self.errors.append('unclosed citation label')
        return self


class MarkdownHTMLText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text = []
        self.invisible = []
    def handle_starttag(self, tag, attrs):
        self.invisible.append(tag in {'script', 'style', 'template', 'noscript'} or bool(self.invisible and self.invisible[-1]))
    def handle_endtag(self, tag):
        if self.invisible:
            self.invisible.pop()
    def handle_startendtag(self, tag, attrs):
        pass
    def handle_data(self, data):
        if not self.invisible or not self.invisible[-1]:
            self.text.append(data)


def source_words(data):
    """Approximate source reading depth; not a semantic claim/reading-level review."""
    if not isinstance(data, bytes) or not 0 < len(data) <= 1_000_000:
        raise ValueError('candidate missing, non-byte or oversized')
    txt = data.decode('utf-8', 'strict')
    if '\x00' in txt or any(ch in _r411.FORMAT_CONTROLS for ch in txt):
        raise ValueError('control characters in candidate')
    if re.search(r'<(?:article|section|p|h[1-6]|div)\b', txt[:2000], re.I):
        parser = MarkdownHTMLText(); parser.feed(txt); parser.close()
        txt = ' '.join(parser.text)
    else:
        txt = re.sub(r'\A---\s*\n.*?\n---\s*\n', '', txt, flags=re.S)
        txt = re.sub(r'!\[[^]]*]\([^)]*\)', ' ', txt)
        txt = re.sub(r'\[([^]]+)]\([^)]*\)', r'\1', txt)
    return [w.casefold() for w in _r411.WORD.findall(txt)]


def shingle_score(source, rendered, width=5):
    """Fraction of candidate 5-word windows retained (reported, not proof of fidelity)."""
    if len(source) < width:
        return 1.0 if source == rendered else 0.0
    a = Counter(tuple(source[i:i + width]) for i in range(len(source) - width + 1))
    b = Counter(tuple(rendered[i:i + width]) for i in range(max(0, len(rendered) - width + 1)))
    return sum((a & b).values()) / sum(a.values())


def check(original, manifest, exports, candidates, *, raw_original=None, test_only=False):
    """candidates: dict[(article_slug, original_Git_blob_SHA)] = private original bytes."""
    base = _r411.check(original, manifest, exports, raw_original=raw_original, test_only=test_only)
    errors, details = list(base.get('errors', [])), []
    required = set()
    try:
        items = original['original_articles']
        if not isinstance(items, list) or len(items) != 35:
            raise ValueError('missing original 35-item candidate inventory')
        for entry in items:
            slug, pins = entry['slug'], entry['body_candidate_git_blobs']
            if not isinstance(slug, str) or not _r411._r410.SLUG.fullmatch(slug):
                raise ValueError('invalid original article slug')
            if not isinstance(pins, list) or not pins or any(not isinstance(s, str) or not HEX40.fullmatch(s) for s in pins):
                raise ValueError('missing/invalid original manuscript Git blob pins: ' + slug)
            for pin in set(pins):
                required.add((slug, pin))
        if not isinstance(candidates, dict) or set(candidates) != required:
            raise ValueError('original candidate artifacts missing, extra or unverified')
        if not isinstance(exports, dict):
            raise ValueError('missing draft export pairs')
        for slug, pin in sorted(required):
            data = candidates[(slug, pin)]
            if not isinstance(data, bytes) or _r409.blob(data) != pin:
                errors.append('original Git blob mismatch: ' + slug + ' @ ' + pin)
                continue
            baseline = source_words(data)
            if len(baseline) < 50:
                errors.append('original candidate has insufficient/extractable text: ' + slug + ' @ ' + pin)
                continue
            pair = exports.get(slug)
            if not isinstance(pair, (tuple, list)) or len(pair) != 2:
                errors.append('missing paired export for original comparison: ' + slug)
                continue
            wp = pair[0]
            if isinstance(wp, bytes):
                wp = wp.decode('utf-8', 'strict')
            if not isinstance(wp, str):
                raise ValueError('bad draft HTML for: ' + slug)
            p = CitationAccessibilityHTML(); p.feed(wp); p.finish()
            errors.extend(slug + ': ' + err for err in p.errors)
            words = [w.casefold() for w in p.visible_words]
            ratio = len(words) / len(baseline)
            overlap = shingle_score(baseline, words)
            if ratio < .90 or overlap < .80:
                errors.append('original candidate reading-depth/phrase drift requires human adjudication: ' + slug + ' @ ' + pin)
            details.append({'slug': slug, 'original_blob': pin, 'source_approx_words': len(baseline),
                            'draft_visible_words': len(words), 'depth_ratio': round(ratio, 4),
                            'five_word_shingle_overlap': round(overlap, 4), 'review_required': True})
        for slug, pair in exports.items():
            if not isinstance(pair, (tuple, list)) or len(pair) != 2:
                continue
            parsed = []
            for i, html in enumerate(pair):
                if isinstance(html, bytes):
                    html = html.decode('utf-8', 'strict')
                p = CitationAccessibilityHTML(); p.feed(html); p.finish()
                errors.extend(str(slug) + (' WP: ' if i == 0 else ' preview: ') + e for e in p.errors)
                parsed.append(p)
            if parsed[0].completed_anchors != parsed[1].completed_anchors:
                errors.append('accessible source-label/URL parity lost: ' + str(slug))
    except (TypeError, ValueError, KeyError, UnicodeError, OverflowError, AttributeError) as exc:
        errors.append('missing/malformed baseline evidence: ' + str(exc))
    return {'release_state': 'DRAFT_HARD_HOLD', 'eligible': False, 'publication_approved': False,
            'integrity_ok': bool(base.get('integrity_ok')) and not errors,
            'errors': sorted(set(errors)), 'candidate_compared': len(details), 'details': details,
            'warnings': list(base.get('warnings', [])) + [
                'Every original branch/fork candidate remains unselected; shingle/depth heuristics are NOT human editorial review',
                'Exact content overlap cannot prove source-claim support, safety, authentic browser visibility or paid conversions']}


def checked_candidate_read(path, *, root):
    """Reject candidate symlinks/hardlinks/path escapes before bounded read."""
    p = Path(path)
    resolved_root = Path(root).resolve(strict=True)
    if not p.resolve(strict=True).is_relative_to(resolved_root):
        raise ValueError('candidate escapes private escrow root')
    parent = p.parent.lstat()
    if not stat.S_ISDIR(parent.st_mode) or p.parent.is_symlink():
        raise ValueError('candidate parent is not a normal directory')
    return _r409.read_original(p, max_bytes=1_000_000)


def main():
    parser = argparse.ArgumentParser(description='R412 original-depth/citation preview audit: ALWAYS HARD HOLD')
    parser.add_argument('original', type=Path)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('export_root', type=Path)
    parser.add_argument('private_candidate_root', type=Path,
                        help='PRIVATE authenticated originals, <slug>/<Git SHA>.txt; never commit manuscripts')
    a = parser.parse_args()
    try:
        raw = _r409.read_original(a.original)
        original = json.loads(raw.decode('utf-8'), object_pairs_hook=_r409.unique_pairs)
        manifest = json.loads(_r409.read_original(a.manifest).decode('utf-8'), object_pairs_hook=_r409.unique_pairs)
        exports, candidate_data = {}, {}
        for entry in original['original_articles']:
            slug = entry['slug']
            if not isinstance(slug, str) or not _r411._r410.SLUG.fullmatch(slug):
                raise ValueError('unsafe original slug')
            exports[slug] = (_r409.read_original(a.export_root/'wordpress'/(slug+'.html')),
                             _r409.read_original(a.export_root/'preview'/(slug+'.html')))
            for pin in set(entry['body_candidate_git_blobs']):
                if not isinstance(pin, str) or not HEX40.fullmatch(pin):
                    raise ValueError('unsafe Git blob pin')
                candidate_data[(slug,pin)] = checked_candidate_read(a.private_candidate_root/slug/(pin+'.txt'), root=a.private_candidate_root)
        result = check(original, manifest, exports, candidate_data, raw_original=raw)
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, OverflowError) as exc:
        result = {'release_state':'DRAFT_HARD_HOLD','eligible':False,'publication_approved':False,
                  'integrity_ok':False,'errors':[str(exc)],'candidate_compared':0}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
