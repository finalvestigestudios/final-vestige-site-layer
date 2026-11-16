#!/usr/bin/env python3
"""R414: read-only original inline-citation position / provenance escrow.

Protects source-to-text adjacency across each original Git-blob-pinned article
variant and both offline exports. A source that still appears in a bibliography
but was detached from its original surrounding text cannot silently pass.
This is NOT proof of claim support, safety, accessibility, or publication approval.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from difflib import SequenceMatcher
from html.parser import HTMLParser
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re

_spec = spec_from_file_location('r413_warning_heading_escrow_gate', Path(__file__).with_name('r413_warning_heading_escrow_gate.py'))
_r413 = module_from_spec(_spec)
_spec.loader.exec_module(_r413)
_r412 = _r413._r412
WORD = _r413.TOKEN
SLUG = _r412._r411._r410.SLUG
MARKER = re.compile(r'\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}')
LOOKAROUND = 9
MIN_MATCH = .83


class CitationPositions(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.words = []
        self.markers = []
        self.labels = []
        self._active_anchor = None

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'a':
            ids = [v for k, v in attrs if k.lower() == 'data-source-id']
            if len(ids) > 1:
                raise ValueError('duplicated source-id attribute')
            if ids:
                if self._active_anchor is not None:
                    raise ValueError('nested original citation anchor')
                self._marker(ids[0])
                self._active_anchor = len(self.labels) - 1
                self.labels[self._active_anchor] = []

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_data(self, data):
        if self._active_anchor is not None:
            self.labels[self._active_anchor].extend(w.casefold() for w in WORD.findall(data))
        self.append_text(data)

    def handle_endtag(self, tag):
        if tag.lower() == 'a':
            self._active_anchor = None

    def _marker(self, sid):
        if not isinstance(sid, str) or not SLUG.fullmatch(sid):
            raise ValueError('malformed inline source marker')
        self.markers.append((sid, len(self.words)))
        self.labels.append(None)

    def append_text(self, data):
        last = 0
        for match in MARKER.finditer(data):
            self.words.extend(w.casefold() for w in WORD.findall(data[last:match.start()]))
            self._marker(match.group(1))
            last = match.end()
        self.words.extend(w.casefold() for w in WORD.findall(data[last:]))


def positions(data, *, candidate=False):
    if isinstance(data, bytes):
        data = data.decode('utf-8', 'strict')
    if not isinstance(data, str) or not 0 < len(data.encode('utf-8')) <= 1_000_000:
        raise ValueError('missing/invalid/big source or draft HTML')
    p = CitationPositions()
    if candidate and not re.search(r'<(?:article|section|p|h[1-6]|div)\b', data[:2000], re.I):
        # Original Markdown candidate: tolerate plain Markdown syntax, but not
        # alternative unverifiable citation syntaxes. Each {{cite:id}} is pinned.
        data = re.sub(r'\A---\s*\n.*?\n---\s*\n', '', data, flags=re.S)
        data = re.sub(r'!\[[^]]*]\([^)]*\)', ' ', data)
        data = re.sub(r'\[([^]]+)]\([^)]*\)', r'\1', data)
        p.append_text(data)
    else:
        p.feed(data)
        p.close()
    return p


def nearby(words, index):
    return (tuple(words[max(0, index-LOOKAROUND):index]),
            tuple(words[index:index+LOOKAROUND]))


def match_context(src, dst):
    """Require both independent surrounding spans to match, not just citation IDs."""
    return (SequenceMatcher(None, src[0], dst[0], autojunk=False).ratio() >= MIN_MATCH
            and SequenceMatcher(None, src[1], dst[1], autojunk=False).ratio() >= MIN_MATCH)


def check(original, manifest, exports, candidates, *, raw_original=None, test_only=False):
    parent = _r413.check(original, manifest, exports, candidates,
                         raw_original=raw_original, test_only=test_only)
    errors = list(parent.get('errors', []))
    details = []
    try:
        if not isinstance(original, dict) or not isinstance(manifest, dict) or not isinstance(exports, dict) or not isinstance(candidates, dict):
            raise ValueError('missing original/manifest/export/candidate mappings')
        permitted = {a['slug']: set(a['sources']) for a in manifest['articles']}
        for entry in original['original_articles']:
            slug = entry['slug']
            pair = exports[slug]
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                raise ValueError('missing paired export')
            renders = [positions(x) for x in pair]
            if renders[0].markers != renders[1].markers or renders[0].words != renders[1].words or renders[0].labels != renders[1].labels:
                errors.append('R414 private/WordPress citation/text position parity changed: ' + slug)
            if not renders[0].markers:
                errors.append('R414 missing reader-visible inline citation markers: ' + slug)
            for pin in set(entry['body_candidate_git_blobs']):
                data = candidates[(slug, pin)]
                if not isinstance(data, bytes) or _r412._r409.blob(data) != pin:
                    errors.append('R414 unverified original Git source: ' + slug); continue
                original_positions = positions(data, candidate=True)
                if not original_positions.markers:
                    errors.append('R414 no authentic original inline citation anchors; human mapping required: ' + slug + ' @ ' + pin)
                    continue
                src_ids = [sid for sid, _ in original_positions.markers]
                dst_ids = [sid for sid, _ in renders[0].markers]
                if any(sid not in permitted[slug] for sid in src_ids):
                    errors.append('R414 original citation source not present in source crosswalk: ' + slug + ' @ ' + pin)
                if src_ids == dst_ids:
                    for original_label, draft_label in zip(original_positions.labels, renders[0].labels):
                        if original_label is not None and original_label != draft_label:
                            errors.append('R414 original reader-facing source label changed: ' + slug + ' @ ' + pin)
                if src_ids != dst_ids:
                    errors.append('R414 original citation order/multiplicity changed: ' + slug + ' @ ' + pin)
                moved = 0
                if src_ids == dst_ids:
                    for (_, s_at), (_, d_at) in zip(original_positions.markers, renders[0].markers):
                        if not match_context(nearby(original_positions.words, s_at), nearby(renders[0].words, d_at)):
                            moved += 1
                else:
                    moved = len(original_positions.markers)
                if moved:
                    errors.append('R414 original inline citation detached from source-adjacent text: ' + slug + ' @ ' + pin)
                details.append({'slug':slug, 'original_blob':pin, 'inline_citations_compared':len(original_positions.markers),
                                'citation_locality_mismatches':moved, 'human_claim_source_review_required':True})
    except (ValueError, TypeError, KeyError, UnicodeError, OverflowError, AttributeError, IndexError) as exc:
        errors.append('R414 missing/malformed citation-placement evidence: ' + str(exc))
    return {'release_state':'DRAFT_HARD_HOLD', 'eligible':False, 'publication_approved':False,
            'qualified_safety_approved':False, 'integrity_ok':bool(parent.get('integrity_ok')) and not errors,
            'errors':sorted(set(errors)), 'candidates_compared':len(details), 'details':details,
            'warnings':list(parent.get('warnings', []))+[
                'Citation locality is NOT source support; evidence does not authorize medical, food or emergency advice',
                'Original fork and source-scope adjudication, genuine previews, mobile/keyboard QA and qualified QD remain HARD HOLD']}


def main():
    parser = argparse.ArgumentParser(description='R414 original citation locality; ALWAYS DRAFT HARD HOLD')
    for name in ('original','manifest','export_root','private_candidate_root'):
        parser.add_argument(name,type=Path)
    args = parser.parse_args()
    try:
        raw = _r412._r409.read_original(args.original)
        original = json.loads(raw.decode('utf-8'), object_pairs_hook=_r412._r409.unique_pairs)
        manifest = json.loads(_r412._r409.read_original(args.manifest).decode('utf-8'),object_pairs_hook=_r412._r409.unique_pairs)
        exports,candidates = {},{}
        for entry in original['original_articles']:
            slug = entry['slug']
            if not isinstance(slug,str) or not SLUG.fullmatch(slug):
                raise ValueError('unsafe article slug')
            exports[slug] = (_r412._r409.read_original(args.export_root/'wordpress'/(slug+'.html')),
                             _r412._r409.read_original(args.export_root/'preview'/(slug+'.html')))
            for pin in set(entry['body_candidate_git_blobs']):
                if not isinstance(pin,str) or not _r412.HEX40.fullmatch(pin):
                    raise ValueError('unsafe original SHA')
                candidates[(slug,pin)] = _r412.checked_candidate_read(args.private_candidate_root/slug/(pin+'.txt'),root=args.private_candidate_root)
        result = check(original,manifest,exports,candidates,raw_original=raw)
    except (OSError,ValueError,TypeError,KeyError,AttributeError,UnicodeError,OverflowError) as exc:
        result = {'release_state':'DRAFT_HARD_HOLD','eligible':False,'publication_approved':False,
                  'qualified_safety_approved':False,'integrity_ok':False,'errors':[str(exc)]}
    print(json.dumps(result,sort_keys=True,indent=2))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
