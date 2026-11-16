#!/usr/bin/env python3
"""R416: citation accessible-name/keyboard/target anti-spoof gate (read-only).

A citation can preserve its original visible label, URL, source ID and position yet
expose a different screen-reader name through aria-label/aria-labelledby, or
silently force keyboard/navigation behavior. R415 did not compare these attributes.
This overlay fails closed and never approves source applicability, safety or release.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re

_spec = spec_from_file_location('r415_global_citation_alignment_gate', Path(__file__).with_name('r415_global_citation_alignment_gate.py'))
_r415 = module_from_spec(_spec)
_spec.loader.exec_module(_r415)
_r414 = _r415._r414
_r412 = _r414._r412

MAX_HTML_BYTES = 1_000_000
MAX_CITATIONS = 500
_COLLAPSE = re.compile(r'\s+', flags=re.UNICODE)


def canonical_name(value):
    if not isinstance(value, str):
        return None
    return _COLLAPSE.sub(' ', value).strip().casefold()


class CitationNameAudit(HTMLParser):
    """Conservative names/controls check for linked source anchors only."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.errors = []
        self.anchors = []
        self.active = None
        self.depth = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag != 'a':
            return
        if self.active is not None:
            self.errors.append('nested anchor in source citation')
        keys = [str(k).lower() for k, _ in attrs]
        if len(keys) != len(set(keys)):
            self.errors.append('duplicate citation attributes')
        attr = {str(k).lower(): v for k, v in attrs}
        is_source = 'data-source-id' in attr or 'href' in attr
        if not is_source:
            return
        if len(self.anchors) >= MAX_CITATIONS:
            raise ValueError('citation count exceeds conservative bound')
        if self.active is not None:
            return
        self.active = {'sid':attr.get('data-source-id'), 'href':attr.get('href'),
                       'text':[], 'attrs':attr}
        self.depth += 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.lower() == 'a':
            self.handle_endtag('a')

    def handle_data(self, data):
        if self.active is not None:
            self.active['text'].append(data)

    def handle_endtag(self, tag):
        if tag.lower() != 'a':
            return
        if self.active is None:
            return
        a = self.active
        self.active = None
        self.depth -= 1
        text = canonical_name(' '.join(a['text']))
        attr = a['attrs']
        # The HTML visible label is evidence, not merely a fallback accessible name.
        # Any name indirection requires independent user-facing, human browser review.
        if not text:
            self.errors.append('citation missing visible label')
        if 'aria-labelledby' in attr or 'aria-describedby' in attr:
            self.errors.append('citation accessible name/description references unverified outside text')
        if 'aria-label' in attr and canonical_name(attr['aria-label']) != text:
            self.errors.append('citation aria-label overrides visible source identity')
        if 'title' in attr and canonical_name(attr['title']) != text:
            self.errors.append('citation title overrides visible source identity')
        if 'role' in attr and (attr.get('role') or '').lower() != 'link':
            self.errors.append('citation HTML role overrides hyperlink semantics')
        if 'tabindex' in attr and attr['tabindex'] != '0':
            self.errors.append('citation custom tabindex changes keyboard access/order')
        if 'aria-current' in attr:
            self.errors.append('external citation falsely marks current page')
        if 'contenteditable' in attr and (attr['contenteditable'] or '').lower() != 'false':
            self.errors.append('citation link is editable')
        if 'draggable' in attr and (attr['draggable'] or '').lower() == 'true':
            self.errors.append('citation link unexpectedly draggable')
        target = (attr.get('target') or '').lower()
        if target and target not in {'_self','_blank'}:
            self.errors.append('citation opens arbitrary named browsing context')
        if target == '_blank':
            rel = set((attr.get('rel') or '').lower().split())
            if not {'noopener','noreferrer'}.issubset(rel):
                self.errors.append('citation new-window isolation missing')
        policy = (attr.get('referrerpolicy') or '').lower()
        if policy and policy not in {'no-referrer','strict-origin','strict-origin-when-cross-origin'}:
            self.errors.append('citation referrer policy not privacy-preserving')
        self.anchors.append((a['sid'], a['href'], text))

    def finish(self):
        self.close()
        if self.active is not None:
            self.errors.append('unclosed accessible source link')
        return self


def parse(data):
    if isinstance(data, bytes):
        data = data.decode('utf-8','strict')
    if not isinstance(data, str) or not 10 <= len(data.encode('utf-8')) <= MAX_HTML_BYTES:
        raise ValueError('missing or oversized HTML')
    p = CitationNameAudit()
    p.feed(data)
    return p.finish()


def check(original, manifest, exports, candidates, *, raw_original=None, test_only=False):
    base = _r415.check(original, manifest, exports, candidates,
                       raw_original=raw_original, test_only=test_only)
    errors = list(base.get('errors', []))
    details = []
    try:
        if not isinstance(exports, dict):
            raise ValueError('paired exports must be a mapping')
        for slug in sorted(exports):
            if not isinstance(slug, str) or not _r414.SLUG.fullmatch(slug):
                raise ValueError('malformed article key')
            pair = exports[slug]
            if not isinstance(pair,(tuple,list)) or len(pair)!=2:
                raise ValueError('missing paired export: '+slug)
            parsed = [parse(part) for part in pair]
            for index, p in enumerate(parsed):
                errors.extend('R416 '+slug+(' WordPress: ' if index == 0 else ' preview: ')+e for e in p.errors)
            if parsed[0].anchors != parsed[1].anchors:
                errors.append('R416 citation accessible-name/source parity changed: '+slug)
            details.append({'slug':slug, 'citation_accessible_names_inspected':len(parsed[0].anchors),
                            'human_a11y_source_review_required':True})
    except (TypeError, ValueError, UnicodeError, KeyError, IndexError, OverflowError, AttributeError) as exc:
        errors.append('R416 malformed or unavailable accessible-source evidence: '+str(exc))
    return {'release_state':'DRAFT_HARD_HOLD', 'eligible':False,
            'publication_approved':False, 'qualified_safety_approved':False,
            'integrity_ok':bool(base.get('integrity_ok')) and not errors,
            'errors':sorted(set(errors)), 'articles_inspected':len(details),
            'details':details, 'warnings':list(base.get('warnings',[]))+[
                'Exact name parity is not browser/assistive-technology accessibility QA',
                'Neither citation accuracy nor emergency, medical or food advice is safety-approved',
                'No original candidate selected, genuine private export accepted, QD PASS or publication authorized']}


def main():
    p=argparse.ArgumentParser(description='R416 citation accessible-name safety review; NEVER RELEASE')
    for key in ('original','manifest','export_root','private_candidate_root'):
        p.add_argument(key,type=Path)
    args=p.parse_args()
    try:
        raw=_r412._r409.read_original(args.original)
        original=json.loads(raw.decode('utf-8'),object_pairs_hook=_r412._r409.unique_pairs)
        manifest=json.loads(_r412._r409.read_original(args.manifest).decode('utf-8'),
                            object_pairs_hook=_r412._r409.unique_pairs)
        exports,candidates={},{}
        for article in original['original_articles']:
            slug=article['slug']
            if not isinstance(slug,str) or not _r414.SLUG.fullmatch(slug):
                raise ValueError('unsafe source slug')
            exports[slug]=(_r412._r409.read_original(args.export_root/'wordpress'/(slug+'.html')),
                           _r412._r409.read_original(args.export_root/'preview'/(slug+'.html')))
            for pin in set(article['body_candidate_git_blobs']):
                if not isinstance(pin,str) or not _r412.HEX40.fullmatch(pin):
                    raise ValueError('unsafe source pin')
                candidates[(slug,pin)] = _r412.checked_candidate_read(
                    args.private_candidate_root/slug/(pin+'.txt'),root=args.private_candidate_root)
        out=check(original,manifest,exports,candidates,raw_original=raw)
    except (OSError,ValueError,TypeError,KeyError,IndexError,UnicodeError,OverflowError) as exc:
        out={'release_state':'DRAFT_HARD_HOLD','eligible':False,'publication_approved':False,
             'qualified_safety_approved':False,'integrity_ok':False,'errors':[str(exc)]}
    print(json.dumps(out,sort_keys=True,indent=2));return 2


if __name__=='__main__':
    raise SystemExit(main())
