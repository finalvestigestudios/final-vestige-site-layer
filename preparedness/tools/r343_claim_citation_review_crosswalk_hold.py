#!/usr/bin/env python3
"""R343: read-only, paragraph-scoped citation-to-claim REVIEW packets.

NO automated claim approval is possible here. A verified_on in a source
register demonstrates an earlier research fetch, NOT a human link check,
claim support, qualified emergency review, or a commerce/publishing release.

Native operation REQUIRES R337's five source-depth witnesses and the original
41 Git-pinned body/metadata pairs. Output is a deterministic review queue,
not modified content. Usage from a full authenticated checkout:

  python -I preparedness/tools/r343_claim_citation_review_crosswalk_hold.py
  python -I preparedness/tools/r343_claim_citation_review_crosswalk_hold.py --output /tmp/r343-review.json

This tool never writes within the repository, never calls WordPress and
cannot set QD PASS, may_publish or may_merge to true.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

SCHEMA = 'fv-preparedness-r343-claim-source-review-crosswalk-v1'
TOKEN_RE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
TOKEN_SUSPECT = re.compile(r'\{\{cite:|\{\{\s*cite\s*:', re.I)
SLUG_RE = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
BLOCKS = frozenset({'p', 'li', 'td', 'th', 'dd', 'dt', 'blockquote', 'figcaption', 'caption'})
HEADINGS = frozenset({'h1', 'h2', 'h3', 'h4', 'h5', 'h6'})
RISK_PATTERNS = {
    'emergency-dispatch': r'\b(?:911|dispatch|police|fire department|life.threatening|emergency call)\b',
    'child-reunification': r'\b(?:child|children|school|reunif|custod|pickup|pick.up)\w*',
    'medicine-and-devices': r'\b(?:medicin|prescri|insulin|medical|oxygen|dose|refrigerat)\w*',
    'water-and-chemicals': r'\b(?:bleach|chlorin|water|contamin|boil|chemical|filter)\w*',
    'food-preservation': r'\b(?:canner|canning|jerky|preserv|ferment|salmonella|botulis)\w*',
    'fire-and-power': r'\b(?:fire|generator|smoke|carbon monoxide|electri|power outage)\w*',
    'evacuation-and-shelter': r'\b(?:evacuat|shelter|service animal|assistance animal)\w*',
    'privacy': r'\b(?:identif|password|address|contact card|medical information|personal data)\w*',
}
CITED_SOURCE_NOTE = 'CITATION_ADJACENCY_IS_NOT_PROOF_OF_CLAIM_SUPPORT'
HOLD_FIELDS = {
    'qualified_qd_pass': False,
    'source_claim_support_verified': False,
    'medical_or_emergency_advice_approved': False,
    'native_rendered_100_exports_verified': False,
    'may_merge': False, 'may_publish': False,
    'paid_sku_verified': False, 'paid_orders_verified': False,
    'realized_net_revenue_verified': False,
}


def fingerprint(data: str) -> str:
    return sha256(data.encode('utf-8')).hexdigest()


def tidy(s: str) -> str:
    return ' '.join(s.split())


class CitationBlocks(HTMLParser):
    """Map cite tokens to enclosing semantic blocks without guessing support.

    Tracks headings and nearest claim-bearing block; rejects tokens in markup,
    comments, scripts, or outside blocks. In nested blocks the nearest block
    owns the citation rather than duplicating it in an enclosing list item.
    """
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks: list[dict] = []
        self.problems: list[str] = []
        self._open: list[dict] = []
        self._blocks_open: list[dict] = []
        self._head: dict | None = None
        self.heading = 'unheaded'
        self.citations_seen = 0
        self._skip = 0
        self._body_line = 0

    def handle_starttag(self, tag: str, attrs):
        self._open.append({'tag': tag, 'heading': self.heading})
        for key, value in attrs:
            if value is not None and TOKEN_SUSPECT.search(value):
                self.problems.append('CITATION_TOKEN_IN_HTML_ATTRIBUTE')
        if tag in ('script', 'style', 'textarea'):
            self._skip += 1
        if tag in HEADINGS:
            self._head = {'tag': tag, 'id': dict(attrs).get('id'), 'text': []}
        if tag in BLOCKS:
            self._blocks_open.append({'tag': tag, 'text': [], 'cites': [],
                                      'line': self.getpos()[0], 'heading': self.heading,
                                      'position': len(self.blocks) + len(self._blocks_open)})

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_data(self, data: str):
        if self._skip:
            if TOKEN_SUSPECT.search(data):
                self.problems.append('CITATION_TOKEN_IN_SCRIPT_STYLE_OR_INPUT')
            return
        if self._head is not None:
            self._head['text'].append(TOKEN_RE.sub('', data))
        citations = TOKEN_RE.findall(data)
        self.citations_seen += len(citations)
        if TOKEN_SUSPECT.search(TOKEN_RE.sub('', data)):
            self.problems.append('MALFORMED_OR_SPLIT_CITATION_TOKEN')
        if not self._blocks_open and citations:
            self.problems.append('CITATION_NOT_IN_CLAIM_BLOCK')
        if self._blocks_open:
            target = self._blocks_open[-1]
            target['text'].append(TOKEN_RE.sub(' ', data))
            target['cites'].extend(citations)

    def handle_comment(self, data: str):
        if TOKEN_SUSPECT.search(data):
            self.problems.append('CITATION_HIDDEN_IN_HTML_COMMENT')

    def handle_endtag(self, tag: str):
        if tag in BLOCKS:
            if not self._blocks_open or self._blocks_open[-1]['tag'] != tag:
                self.problems.append('MALFORMED_CLAIM_BLOCK_NESTING')
            else:
                node = self._blocks_open.pop()
                node['text'] = tidy(''.join(node['text']))
                node['position'] = len(self.blocks)
                self.blocks.append(node)
        if tag in HEADINGS and self._head is not None:
            label = tidy(''.join(self._head['text']))
            self.heading = (self._head['id'] or label or 'unnamed-heading')
            self._head = None
        if tag in ('script', 'style', 'textarea') and self._skip:
            self._skip -= 1
        for i in range(len(self._open) - 1, -1, -1):
            if self._open[i]['tag'] == tag:
                del self._open[i:]
                break

    def close(self):
        super().close()
        if self._blocks_open:
            self.problems.append('UNCLOSED_CLAIM_BLOCK')


def parse_claim_blocks(html: str) -> CitationBlocks:
    if not isinstance(html, str):
        raise TypeError('HTML_STRING_REQUIRED')
    obj = CitationBlocks()
    obj.feed(html)
    obj.close()
    if html.count('{{cite:') != obj.citations_seen:
        obj.problems.append('CITATION_COUNT_NOT_CAPTURED_IN_VISIBLE_BLOCKS')
    return obj


def analyze_entry(kind: str, slug: str, body: str, meta: dict, source_ids: set[str] | None = None) -> dict:
    """Pure analysis; synthetic inputs yield hold-only tickets, not approvals."""
    errors: list[str] = []
    if kind not in ('articles', 'tools') or not isinstance(slug, str) or not SLUG_RE.fullmatch(slug):
        return {'errors': ['INVALID_KIND_OR_SLUG'], 'tickets': [], 'unused_source_use': []}
    if not isinstance(meta, dict) or not isinstance(meta.get('source_use'), dict):
        return {'errors': ['SOURCE_USE_DECLARATIONS_REQUIRED'], 'tickets': [], 'unused_source_use': []}
    if meta.get('slug') != slug or meta.get('status', {}).get('publish') != 'draft':
        errors.append('ORIGINAL_DRAFT_IDENTITY_OR_STATE_CHANGED:' + slug)
    if meta.get('safety_review', {}).get('state') not in ('pending', 'approved', 'not-required'):
        errors.append('UNRECOGNIZED_SAFETY_REVIEW_STATE:' + slug)
    try:
        blocks = parse_claim_blocks(body)
    except (TypeError, ValueError) as exc:
        return {'errors': ['INVALID_HTML:' + type(exc).__name__], 'tickets': [], 'unused_source_use': []}
    errors.extend(blocks.problems)
    declared = meta['source_use']
    tickets: list[dict] = []
    cited = set()
    block_keys = set()
    for block in blocks.blocks:
        claim = block['text']
        if not block['cites']:
            continue
        if not claim:
            errors.append('CITATION_WITHOUT_VISIBLE_CLAIM:' + slug)
        if len(claim) < 12:
            errors.append('CITED_BLOCK_TOO_SHORT_FOR_CONTEXT:' + slug)
        digest = fingerprint(claim)
        for local_index, source_id in enumerate(block['cites']):
            cited.add(source_id)
            if source_id not in declared:
                errors.append('CITED_SOURCE_NOT_DECLARED_IN_METADATA:' + slug + ':' + source_id)
            elif not isinstance(declared[source_id], str) or not tidy(declared[source_id]):
                errors.append('EMPTY_SOURCE_USE_RATIONALE:' + slug + ':' + source_id)
            if source_ids is not None and source_id not in source_ids:
                errors.append('CITED_SOURCE_NOT_IN_NATIVE_REGISTER:' + slug + ':' + source_id)
            ticket_seed = '|'.join((kind, slug, str(block['position']), str(local_index), source_id, digest))
            ticket_id = fingerprint(ticket_seed)[:24]
            if ticket_id in block_keys:
                errors.append('COLLIDING_CLAIM_TICKET_ID:' + slug)
            block_keys.add(ticket_id)
            risks = [label for label, rx in RISK_PATTERNS.items() if re.search(rx, claim, re.I)]
            tickets.append({
                'ticket_id': ticket_id, 'kind': kind, 'slug': slug,
                'block_ordinal': block['position'], 'html_line': block['line'],
                'heading': block['heading'], 'block_tag': block['tag'],
                'citation_ordinal': local_index, 'source_id': source_id,
                'claim_text_sha256': digest, 'excerpt': claim[:420],
                'full_text_utf8_length': len(claim.encode('utf-8')),
                'source_use_sha256': fingerprint(str(declared.get(source_id, ''))),
                'risk_hints_not_safety_findings': risks,
                'human_claim_source_adjudication': 'UNREVIEWED_REQUIRED',
                'citation_meaning': CITED_SOURCE_NOTE,
            })
    unused = sorted(set(declared) - cited)
    if not tickets:
        errors.append('NO_VISIBLE_CLAIM_CITATIONS:' + slug)
    return {'errors': sorted(set(errors)), 'tickets': tickets, 'unused_source_use': unused,
            'declared_sources': len(declared), 'distinct_cited_sources': len(cited),
            'citation_occurrences': blocks.citations_seen}


def report(errors: list[str], tickets: list[dict] | None = None, rows: int = 0,
           unused: dict | None = None, source_catalog: dict | None = None) -> dict:
    records = tickets or []
    return {
        'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
        'errors': sorted(set(errors)), 'entries_inspected': rows,
        'citation_claim_review_tickets': len(records), 'distinct_claim_ticket_ids': len({t['ticket_id'] for t in records}),
        'risk_hint_counts': dict(sorted(Counter(risk for t in records for risk in t['risk_hints_not_safety_findings']).items())),
        'source_catalog': source_catalog or {}, 'unused_metadata_source_use': unused or {},
        'review_tickets': records,
        'original_legacy_editorial_conflicts_remaining': 15,
        'original_article15_tool104_review_obligations_remaining': 17,
        'additional_accessibility_and_privacy_review_remains': True,
        'limitations': [
            CITED_SOURCE_NOTE, 'SOURCE_VERIFIED_ON_IS_NOT_A_HUMAN_LINK_CHECK_OR_CLAIM_SUPPORT',
            'RISK_HINTS_ARE_NOT_MEDICAL_OR_EMERGENCY_ADVICE_VALIDATIONS',
            'ORIGINAL_15_CONFLICTS_AND_17_SAFETY_OBLIGATIONS_NOT_ADJUDICATED',
            'WORDPRESS_NATIVE_100_EXPORT_AND_RENDERED_LINK_GATE_SEPARATE',
            'COMMERCIAL_TRANSACTIONS_AND_PAID_SKU_NOT_AUTHENTICATED',
        ], **HOLD_FIELDS,
    }


def _source_catalog(root: Path) -> tuple[dict, list[str]]:
    src = root / 'sources'
    errors = []
    sources = {}
    paths = [src / 'register.json'] + sorted((src / 'fragments').glob('*.json'))
    if len(paths) < 2:
        return {}, ['MISSING_NATIVE_SOURCE_REGISTER_OR_FRAGMENTS']
    for path in paths:
        if path.is_symlink() or not path.is_file():
            errors.append('SYMLINK_OR_MISSING_SOURCE_RECORD:' + path.name)
            continue
        try:
            data = json.loads(path.read_text('utf-8'))
            items = data['sources']
            if not isinstance(items, list):
                raise TypeError()
        except (OSError, ValueError, KeyError, TypeError, UnicodeError):
            errors.append('INVALID_SOURCE_REGISTER_FRAGMENT:' + path.name)
            continue
        for s in items:
            if not isinstance(s, dict) or not isinstance(s.get('id'), str) or not SLUG_RE.fullmatch(s['id']):
                errors.append('INVALID_SOURCE_CATALOG_ID:' + path.name)
                continue
            sid = s['id']
            old = sources.get(sid)
            if old is not None:
                if old.get('verified_on') is not None or s.get('verified_on') is None:
                    errors.append('UNSAFE_DUPLICATE_OR_DOWNGRADE_SOURCE:' + sid)
                else:
                    sources[sid] = s
            else:
                sources[sid] = s
    return sources, errors


def audit_native(root: Path) -> dict:
    """Read 41 source items after authentic R337 depth and Git-object validation."""
    prep = root / 'preparedness' if (root / 'preparedness').is_dir() else root
    try:
        from preparedness.tools import r337_measured_source_integrity as prior
    except ImportError:
        return report(['R337_MEASURED_FROZEN_SOURCE_GUARD_UNAVAILABLE'])
    custody = prior.audit(prep)
    if custody.get('state') != 'DRAFT_HARD_HOLD' or custody.get('entries_checked') != 41:
        return report(['R337_41_ENTRY_PINNED_GIT_AND_DEPTH_GATE_FAILED'] + custody.get('errors', []))
    catalog, errs = _source_catalog(prep)
    entries = []; unused = {}
    content = prep / 'content'
    for kind, count in (('articles', 35), ('tools', 6)):
        bodies = sorted((content / kind).glob('*.body.html'))
        metas = sorted((content / kind).glob('*.meta.json'))
        if len(bodies) != count or len(metas) != count:
            errs.append('EXACT_35_ARTICLES_6_TOOLS_REQUIRED:' + kind)
        body_ids = {p.name[:-10] for p in bodies}
        meta_ids = {p.name[:-10] for p in metas}
        if body_ids != meta_ids:
            errs.append('BODY_METADATA_PAIR_IDENTITY_DRIFT:' + kind)
        for slug in sorted(body_ids & meta_ids):
            bp = content / kind / (slug + '.body.html')
            mp = content / kind / (slug + '.meta.json')
            if bp.is_symlink() or mp.is_symlink():
                errs.append('SYMLINK_SOURCE_NOT_AUTHENTIC:' + slug)
                continue
            try:
                body = bp.read_text('utf-8'); meta = json.loads(mp.read_text('utf-8'))
            except (OSError, UnicodeError, ValueError):
                errs.append('UNREADABLE_NATIVE_CONTENT:' + slug)
                continue
            result = analyze_entry(kind, slug, body, meta, set(catalog))
            errs.extend(result['errors'])
            entries.extend(result['tickets'])
            if result['unused_source_use']:
                unused[kind + '/' + slug] = result['unused_source_use']
    if len({(r['kind'],r['slug']) for r in entries}) != 41:
        errs.append('CITED_41_SOURCE_ENTRIES_COVERAGE_FAILED')
    catalog_summary = {
        'distinct_native_source_ids': len(catalog),
        'research_fetch_date_present': sum(bool(x.get('verified_on')) for x in catalog.values()),
        'human_link_check_true_not_claim_approval': sum(x.get('human_link_check') is True for x in catalog.values()),
        'source_entries_with_unreviewed_links': sum(x.get('human_link_check') is not True for x in catalog.values()),
    }
    return report(errs, entries, 41, unused, catalog_summary)


def main() -> int:
    parser = argparse.ArgumentParser(description='R343 source-to-claim human review queue; NEVER publish or approve.')
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--output', type=Path, default=None, help='optional JSON report outside repo')
    args = parser.parse_args()
    result = audit_native(args.repo_root.resolve())
    if args.output:
        path = args.output.resolve()
        if str(path).startswith(str(args.repo_root.resolve()) + '/'):
            print(json.dumps({'state':'INVALID_HARD_HOLD','errors':['NO_WRITING_REPORT_IN_SOURCE_REPOSITORY']}))
            return 1
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), 'utf-8')
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if result['state'] == 'INVALID_HARD_HOLD' else 2


if __name__ == '__main__':
    raise SystemExit(main())
