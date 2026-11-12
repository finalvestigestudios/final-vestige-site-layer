#!/usr/bin/env python3
"""Read-only R313 visible-citation and editorial-state evidence guard.

Issue #136, commercial context #820. A citation inside a comment, hidden element,
script, style, template or attribute is NOT a visible claim-support citation.
No part of this audit approves the accuracy or safety of the cited material.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import re
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('r312_pinned', HERE / 'r312_article_citation_parity_hold.py')
r312 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r312)
r310 = r312.r310
SCHEMA = 'fv-preparedness-r315-html5-entity-visible-citation-v1'
PREDECESSOR = 'preparedness/tools/r312_article_citation_parity_hold.py'
PREDECESSOR_OID = '2ae6f2a8532c33c15e925166479e52f662b3f39f'
TAXONOMY = 'preparedness/taxonomy.json'
TAXONOMY_OID = r310.TAXONOMY_OID
CITE = re.compile(r'\{\{cite:([^{}]*)\}\}')
NON_PROSE = {'script', 'style', 'template', 'noscript', 'textarea', 'code', 'pre'}
HIDDEN_STYLE = re.compile(r'(?:^|;)\s*(?:display\s*:\s*none|visibility\s*:\s*(?:hidden|collapse))\s*(?:;|$)', re.I)
DANGEROUS_STATES = {'approved', 'passed', 'cleared', 'complete', 'published', 'live', 'verified', 'safe'}
R313_PIN = '209457045d1d44a18a26c1e2e31ddb8541bad49c'
R314_PIN = 'c46c5f7a9d1c691ba5f19268a3215ebd5ae85589'
R313_PATH = 'preparedness/tools/r313_article_visible_citation_state_hold.py'
R314_PATH = 'preparedness/tools/r314_family_contact_release_hold.py'
OTHER_INVISIBLE_CSS = re.compile(r'(?:^|;)\s*(?:opacity\s*:\s*0+(?:\.0+)?|font-size\s*:\s*0+(?:\.0+)?(?:px|rem|em|pt|%)?|content-visibility\s*:\s*hidden|color\s*:\s*transparent|clip-path\s*:\s*inset\(\s*100%\s*\)|transform\s*:\s*scale\(\s*0\s*\))\s*(?:!important\s*)?(?:;|$)',re.I)
ALLOWED_STATES = {'pending', 'not-required'}


class CitationVisibilityParser(HTMLParser):
    """Collect evidence positions, preserving ancestor visibility and tag context."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool]] = []
        self.visible: list[str] = []
        self.hidden: list[str] = []
        self.attribute: list[str] = []
        self.comment: list[str] = []
        self.invalid_attrs: list[str] = []
        self.open_nonprose: list[str] = []
        self.void = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        keys = [k.lower() for k, _ in attrs]
        if len(keys) != len(set(keys)):
            self.invalid_attrs.append('duplicate-attribute')
        for k, v in attrs:
            if v and CITE.search(v):
                self.attribute.extend(CITE.findall(v))
        d = dict(attrs)
        hidden = (tag.lower() in NON_PROSE or 'hidden' in d or 'inert' in d or
                  str(d.get('aria-hidden', '')).lower() == 'true' or
                  bool(HIDDEN_STYLE.search(d.get('style') or '')) or
                  bool(OTHER_INVISIBLE_CSS.search(re.sub(r'/\*.*?\*/', '', d.get('style') or '', flags=re.S))) or
                  any(hidden for _, hidden in self.stack))
        if tag.lower() not in self.void:
            self.stack.append((tag.lower(), hidden))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]):
        # The slash does NOT close a non-void HTML element in an HTML5 browser.
        # SVG/MathML foreign-content tags are allowed to self-close; HTML within
        # <foreignObject> resumes normal non-void handling.
        parents = [t for t, _ in self.stack]
        fi = max((i for i,t in enumerate(parents) if t in ('svg','math')),default=-1)
        hi = max((i for i,t in enumerate(parents) if t in ('foreignobject','annotation-xml')),default=-1)
        if tag.lower() not in self.void and tag.lower() not in ('svg','math') and not fi > hi:
            self.invalid_attrs.append('html5-nonvoid-self-closing')
        self.handle_starttag(tag, attrs)
        if tag.lower() not in self.void:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str):
        if tag.lower() in self.void:
            self.invalid_attrs.append('void-end-tag')
            return
        if not self.stack:
            self.invalid_attrs.append('unbalanced-end-tag')
            return
        if self.stack[-1][0] == tag.lower():
            self.stack.pop()
        else:
            # Fail closed, but recover to gather remaining citation evidence.
            self.invalid_attrs.append('mismatched-end-tag')
            for idx in range(len(self.stack)-1, -1, -1):
                if self.stack[idx][0] == tag.lower():
                    del self.stack[idx:]
                    break

    def handle_data(self, data: str):
        ids = CITE.findall(data)
        (self.hidden if any(hidden for _, hidden in self.stack) else self.visible).extend(ids)

    def handle_comment(self, data: str):
        self.comment.extend(CITE.findall(data))

    def finish(self):
        self.close()
        if self.stack:
            self.invalid_attrs.append('unclosed-element')


def inspect_visible_evidence(slug: str, body: str, meta: dict, taxonomy_row: dict) -> tuple[list[str], dict]:
    """Pure synthetic-testable audit. Original body and metadata remain untouched."""
    errs: list[str] = []
    parser = CitationVisibilityParser()
    try:
        parser.feed(body)
        parser.finish()
    except (TypeError, ValueError, AssertionError):
        errs.append('ARTICLE_HTML_PARSE_ERROR:' + slug)
    all_ids = CITE.findall(body)
    if parser.invalid_attrs:
        errs.append('ARTICLE_HTML_STRUCTURE_OR_ATTRIBUTES:' + slug)
    # HTML entities can materialize cite tokens that were NOT present as literal
    # builder inputs. Compare decoded occurrence multiset against original bytes.
    from collections import Counter
    if Counter(parser.visible + parser.hidden + parser.attribute) - Counter(CITE.findall(body)):
        errs.append('ARTICLE_ENTITY_DECODED_CITATION_NOT_SOURCE_TOKEN:' + slug)
    if parser.hidden or parser.attribute or parser.comment or len(parser.visible) != len(all_ids):
        errs.append('ARTICLE_NONVISIBLE_OR_UNRENDERED_CITATION:' + slug)
    if not isinstance(meta, dict) or not isinstance(taxonomy_row, dict):
        return errs + ['ARTICLE_METADATA_OR_TAXONOMY_MISSING:' + slug], {}
    if meta.get('status') != {'editorial': 'drafted', 'publish': 'draft'}:
        errs.append('ARTICLE_EDITORIAL_RELEASE_STATE_CHANGED:' + slug)
    safety = meta.get('safety_review')
    state = safety.get('state') if isinstance(safety, dict) else None
    if not isinstance(state, str) or state.lower() not in ALLOWED_STATES or state != state.lower():
        errs.append('ARTICLE_UNKNOWN_OR_APPROVED_SAFETY_STATE:' + slug)
    if state == 'not-required' and taxonomy_row.get('gate') is True:
        errs.append('GATED_ARTICLE_DECLARED_SAFETY_NOT_REQUIRED:' + slug)
    if not isinstance(taxonomy_row.get('gate'), bool) or taxonomy_row.get('slug') != slug:
        errs.append('ARTICLE_TAXONOMY_GATE_OR_IDENTITY_INVALID:' + slug)
    if meta.get('section') != taxonomy_row.get('section') or meta.get('track') != taxonomy_row.get('track'):
        errs.append('ARTICLE_TAXONOMY_SECTION_OR_TRACK_DRIFT:' + slug)
    return sorted(set(errs)), {
        'slug': slug, 'visible_citation_occurrences': len(parser.visible),
        'nonvisible_citation_occurrences': len(parser.hidden) + len(parser.attribute) + len(parser.comment),
        'safety_state': state, 'taxonomy_gate': taxonomy_row.get('gate'),
        'publication_authorized': False, 'claim_safety_verified': False
    }


def audit_visibility(root: Path, *, ledger: dict, taxonomy: dict, require_pins: bool = True) -> dict:
    errors: list[str] = []
    articles = ledger.get('articles') if isinstance(ledger, dict) else None
    slate = taxonomy.get('slate') if isinstance(taxonomy, dict) else None
    if not isinstance(articles, list) or len(articles) != 35 or not isinstance(slate, list) or len(slate) != 35:
        errors.append('EXPECTED_35_ARTICLES_AND_TAXONOMY_ROWS')
        articles = articles if isinstance(articles, list) else []
        slate = slate if isinstance(slate, list) else []
    tax = {x.get('slug'): x for x in slate if isinstance(x, dict) and isinstance(x.get('slug'), str)}
    if len(tax) != 35 or {x.get('slug') for x in articles if isinstance(x, dict)} != set(tax):
        errors.append('TAXONOMY_ARTICLE_SLATE_MISMATCH')
    entries = []
    for row in articles:
        slug = row.get('slug') if isinstance(row, dict) else None
        if not isinstance(slug, str) or not r312.SOURCE_ID.fullmatch(slug):
            errors.append('INVALID_LEDGER_SLUG')
            continue
        pair = []
        for suffix, key in (('body.html','integrated_body_blob'), ('meta.json','integrated_meta_blob')):
            path = f'preparedness/content/articles/{slug}.{suffix}'
            data = r310.file_bytes(root, path)
            if data is None:
                errors.append('ARTICLE_SOURCE_MISSING_OR_SYMLINK:' + slug)
            elif require_pins and r310.oid(data) != row.get(key):
                errors.append('ARTICLE_SOURCE_BLOB_DRIFT:' + slug)
            pair.append(data)
        if None in pair:
            continue
        try:
            body = pair[0].decode('utf-8')
            # Reject duplicate JSON object keys so editorial state cannot be ambiguous.
            def unique_pairs(items):
                result = {}
                for key, value in items:
                    if key in result:
                        raise ValueError('duplicate JSON key: ' + key)
                    result[key] = value
                return result
            meta = json.loads(pair[1].decode('utf-8'), object_pairs_hook=unique_pairs)
        except (UnicodeError, json.JSONDecodeError, ValueError):
            errors.append('ARTICLE_DUPLICATE_METADATA_KEY_OR_ENCODING:' + slug)
            continue
        problems, witness = inspect_visible_evidence(slug, body, meta, tax.get(slug))
        errors.extend(problems)
        if witness:
            entries.append(witness)
    return {'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
            'errors': sorted(set(errors)), 'article_count': len(entries),
            'visible_citations': sum(e['visible_citation_occurrences'] for e in entries),
            'nonvisible_citations': sum(e['nonvisible_citation_occurrences'] for e in entries),
            'citation_visibility_crosswalk': entries,
            'publication_authorized': False, 'medical_safety_verified': False,
            'independent_qd_pass': False, 'all_41_wordpress_draft_exports_verified': False,
            'merchant_paid_orders_verified': False}


def run(root: Path) -> dict:
    for file, pin in ((R313_PATH, R313_PIN), (R314_PATH, R314_PIN)):
        data = r310.file_bytes(root, file)
        if data is None or r310.oid(data) != pin:
            raise ValueError('INHERITED_SOURCE_GATE_UNVERIFIED:' + file)
    predecessor = r310.file_bytes(root, PREDECESSOR)
    if predecessor is None or r310.oid(predecessor) != PREDECESSOR_OID:
        raise ValueError('R312_PREDECESSOR_MISSING_OR_MODIFIED')
    ledger_bytes = r310.file_bytes(root, r312.LEDGER)
    taxonomy_bytes = r310.file_bytes(root, TAXONOMY)
    if (ledger_bytes is None or r310.oid(ledger_bytes) != r312.LEDGER_OID or
        taxonomy_bytes is None or r310.oid(taxonomy_bytes) != TAXONOMY_OID):
        raise ValueError('AUTHENTIC_LEDGER_OR_TAXONOMY_MISSING_OR_MODIFIED')
    prior = r312.run(root)
    current = audit_visibility(root, ledger=json.loads(ledger_bytes), taxonomy=json.loads(taxonomy_bytes))
    current['inherited_r312_state'] = prior['state']
    current['inherited_r312_errors'] = prior['errors']
    if prior['errors']:
        current['errors'].extend('INHERITED_R312:' + e for e in prior['errors'])
        current['errors'] = sorted(set(current['errors']))
        current['state'] = 'INVALID_HARD_HOLD'
    return current


def main():
    p = argparse.ArgumentParser(description='Read-only article citation-visibility and safety-state gate')
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    args = p.parse_args()
    try:
        result = run(args.root)
    except (OSError, ValueError, TypeError, KeyError, UnicodeError) as e:
        result = {'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD',
                  'errors': ['AUTHENTIC_INPUTS_UNAVAILABLE:' + type(e).__name__],
                  'publication_authorized': False, 'independent_qd_pass': False,
                  'medical_safety_verified': False}
    print(json.dumps(result, sort_keys=True, indent=2))
    return 1 if result['state'] == 'INVALID_HARD_HOLD' else 2

if __name__ == '__main__':
    raise SystemExit(main())
