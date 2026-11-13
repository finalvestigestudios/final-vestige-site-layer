#!/usr/bin/env python3
"""R336 read-only frozen 35+6 source, citation, route and reading-depth gate.

An identity/custody gate, not a medical, emergency, historical, source-support,
privacy, commerce or Qualified-Domain review. No WordPress or filesystem writes.
Every authentic source change remains HUMAN_REVIEW_REQUIRED until re-pinned.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import html
import json
from pathlib import Path
import re
from urllib.parse import unquote

SCHEMA = 'fv-preparedness-r336-41-entry-frozen-custody-v1'
CITATIONS = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
LINKS = re.compile(r'\{\{link:([a-z0-9-]+)(?:\|[^}]*)?\}\}')
HEADINGS = re.compile(r'<h[1-6]\b[^>]*\bid=["\']([^"\']+)["\'][^>]*>', re.I)
WORDS = re.compile(r"\b[\w]+(?:[-'][\w]+)*\b", re.U)
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
FROZEN_HOLDS = ('15_contributor_conflicts', '17_article15_tool104_claims',
                'independent_qualified_safety_review', '50_wp_50_preview_native_exports',
                'real_paid_sku_checkout_and_net_revenue')


def git_blob(content: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()


def metrics(body: str) -> dict:
    text = re.sub(r'<[^>]+>', ' ', body)
    text = CITATIONS.sub(' ', LINKS.sub(' ', html.unescape(text)))
    return {'words': len(WORDS.findall(text)),
            'citations': dict(sorted(Counter(CITATIONS.findall(body)).items())),
            'headings': HEADINGS.findall(body), 'links': dict(sorted(Counter(LINKS.findall(body)).items()))}


def canonical(base: str, section: str, slug: str) -> str:
    if base != '/preparedness/' or not SLUG.fullmatch(section) or not SLUG.fullmatch(slug):
        raise ValueError('NONCANONICAL_SEGMENT_OR_BASE')
    return f'{base}{section}/{slug}/'


def snapshot_from_tree(root: Path, *, evidence_sha: str, source_heads: dict) -> dict:
    """Build a candidate inventory only. Requires independent authenticated Git pins.

    Not a release approval. Do not use the output to self-approve changed source.
    """
    taxonomy = json.loads((root / 'taxonomy.json').read_text('utf-8'))
    entries = []
    for kind in ('articles', 'tools'):
        for mp in sorted((root / 'content' / kind).glob('*.meta.json')):
            bp = mp.with_name(mp.name.replace('.meta.json', '.body.html'))
            raw = mp.read_bytes(); body_raw = bp.read_bytes(); meta = json.loads(raw)
            slug = mp.name[:-len('.meta.json')]
            m = metrics(body_raw.decode('utf-8'))
            entries.append({'kind': kind, 'slug': slug, 'meta_blob': git_blob(raw),
                            'body_blob': git_blob(body_raw), 'route': canonical(taxonomy['base_path'], meta['section'], slug),
                            'words': m['words'], 'citations': m['citations'], 'headings': m['headings'],
                            'links': m['links'], 'source_use_ids': sorted(meta.get('source_use', {}))})
    return {'schema': SCHEMA, 'source_ref': evidence_sha, 'source_heads': source_heads,
            'release_state': 'DRAFT_HARD_HOLD', 'qualified_qd_pass': False,
            'historical_and_emergency_safety_approved': False, 'source_claim_support_verified': False,
            'published_or_live': False, 'commercial_sku_verified': False,
            'unresolved_holds': list(FROZEN_HOLDS), 'entries': entries}


def audit(root: Path, witness: dict) -> dict:
    errors = []
    if not isinstance(witness, dict) or witness.get('schema') != SCHEMA:
        return result(['INVALID_MANIFEST_SCHEMA'])
    if (witness.get('release_state') != 'DRAFT_HARD_HOLD' or
        any(witness.get(k) is not False for k in ('qualified_qd_pass','historical_and_emergency_safety_approved',
                                                  'source_claim_support_verified','published_or_live','commercial_sku_verified')) or
        witness.get('unresolved_holds') != list(FROZEN_HOLDS)):
        errors.append('FORGED_RELEASE_OR_REVENUE_EVIDENCE')
    entries = witness.get('entries')
    if not isinstance(entries, list) or len(entries) != 41:
        return result(errors + ['MANIFEST_MUST_HAVE_41_ENTRIES'])
    if not re.fullmatch(r'[a-f0-9]{40}', str(witness.get('source_ref', ''))):
        errors.append('MISSING_AUTHENTIC_SOURCE_COMMIT')
    heads = witness.get('source_heads')
    if not isinstance(heads, dict) or len(heads) != 9 or any(not re.fullmatch(r'[a-f0-9]{40}', str(v)) for v in heads.values()):
        errors.append('NINE_HEAD_PINS_MISSING')
    try:
        tax = json.loads((root / 'taxonomy.json').read_text('utf-8'))
    except (OSError, ValueError, UnicodeError):
        return result(errors + ['TAXONOMY_UNREADABLE'])
    rows = tax.get('slate', []); sections = tax.get('sections', []); tools = tax.get('tools', [])
    if len(rows) != 35 or sorted(a.get('n') for a in rows) != list(range(1,36)):
        errors.append('SLATE_35_IDENTITIES_CHANGED')
    allowed_sections = {s.get('slug') for s in sections if isinstance(s,dict)}
    if len(allowed_sections) != 8 or len(sections) != 8:
        errors.append('EIGHT_SECTION_IDENTITY_CHANGED')
    expected_slugs = [row.get('slug') for row in rows]
    if len(set(expected_slugs)) != 35:
        errors.append('DUPLICATE_TAXONOMY_SLUG')
    seen_slugs = set(); seen_routes = set(); n_article = n_tool = 0
    for row in entries:
        if not isinstance(row,dict):errors.append('INVALID_ENTRY');continue
        kind = row.get('kind'); slug = row.get('slug')
        if kind not in ('articles','tools') or not isinstance(slug,str) or not SLUG.fullmatch(slug):
            errors.append('INVALID_KIND_OR_SLUG');continue
        n_article += kind == 'articles'; n_tool += kind == 'tools'
        if slug in seen_slugs:errors.append('DUPLICATE_MANIFEST_SLUG')
        seen_slugs.add(slug)
        mpath = root / 'content' / kind / f'{slug}.meta.json'
        bpath = root / 'content' / kind / f'{slug}.body.html'
        try:
            mb = mpath.read_bytes(); bb = bpath.read_bytes()
            meta = json.loads(mb.decode('utf-8')); body = bb.decode('utf-8')
        except (OSError, UnicodeError, ValueError):
            errors.append('MISSING_OR_UNPARSEABLE_ENTRY:' + slug);continue
        if meta.get('slug') != slug:errors.append('META_SLUG_MISMATCH:' + slug)
        if meta.get('section') not in allowed_sections:errors.append('UNKNOWN_SECTION:' + slug)
        if kind == 'articles':
            taxrow = next((r for r in rows if r.get('slug') == slug), None)
            if not taxrow or taxrow.get('section') != meta.get('section') or taxrow.get('n') != meta.get('n'):
                errors.append('TAXONOMY_ARTICLE_MISMATCH:' + slug)
        if meta.get('status', {}).get('publish') != 'draft':errors.append('PUBLISH_STATE_NOT_DRAFT:' + slug)
        if meta.get('safety_review', {}).get('state') not in ('pending', 'not-required', 'approved'):
            errors.append('UNRECOGNIZED_SAFETY_STATE:' + slug)
        if row.get('meta_blob') != git_blob(mb):errors.append('METADATA_SOURCE_DRIFT_REQUIRES_REVIEW:' + slug)
        if row.get('body_blob') != git_blob(bb):errors.append('BODY_SOURCE_DRIFT_REQUIRES_REVIEW:' + slug)
        try: route = canonical(tax['base_path'], meta['section'], slug)
        except (ValueError, KeyError):route = ''; errors.append('INVALID_CANONICAL_ROUTE:' + slug)
        if row.get('route') != route: errors.append('CANONICAL_ROUTE_DRIFT:' + slug)
        key = unquote(route).casefold()
        if key in seen_routes: errors.append('DUPLICATE_CANONICAL_ROUTE:' + slug)
        seen_routes.add(key)
        m = metrics(body)
        if m['words'] < row.get('words',0):errors.append('READING_DEPTH_LOSS:' + slug)
        if 'body_min_bytes' in row and len(bb) < row['body_min_bytes']:errors.append('SOURCE_BYTE_DEPTH_LOSS:' + slug)
        if row.get('citations') is not None and m['citations'] != row['citations']:errors.append('CITATION_WITNESS_DRIFT:' + slug)
        if row.get('headings') is not None and m['headings'] != row['headings']:errors.append('SECTION_HEADINGS_DRIFT:' + slug)
        if row.get('links') is not None and m['links'] != row['links']:errors.append('INTERNAL_LINK_WITNESS_DRIFT:' + slug)
        source_ids = sorted(meta.get('source_use', {})) if isinstance(meta.get('source_use'),dict) else []
        if row.get('source_use_ids') is not None and source_ids != row['source_use_ids']:errors.append('SOURCE_USE_INVENTORY_DRIFT:' + slug)
        if not set(m['citations']).issubset(source_ids):errors.append('CITED_SOURCE_NOT_IN_SOURCE_USE:' + slug)
        if len(set(m['headings'])) != len(m['headings']):errors.append('DUPLICATE_HEADING_ID:' + slug)
    if (n_article,n_tool)!=(35,6) or set(expected_slugs) != {x.get('slug') for x in entries if isinstance(x,dict) and x.get('kind')=='articles'}:
        errors.append('35_ARTICLES_6_TOOLS_IDENTITY_MISMATCH')
    for kind in ('articles','tools'):
        for ext in ('*.meta.json','*.body.html'):
            actual = list((root / 'content' / kind).glob(ext))
            if len(actual) != (35 if kind == 'articles' else 6):
                errors.append('UNTRACKED_OR_MISSING_CONTENT_FILE:' + kind + ':' + ext)
    # Source crosswalk is a separate and deliberately unresolved adjudication ledger.
    p = root / 'audits' / 'r334_frozen_nine_head_source_object_crosswalk.json'
    try:
        cross = json.loads(p.read_text('utf-8'))
        if cross['source_heads'] != heads or cross['distinct_source_divergence_count'] != 14 or cross['unresolved_legacy_adjudication_conflict_count_from_issue136'] != 15:
            errors.append('NINE_HEAD_CROSSWALK_OR_15_CONFLICT_LEDGER_DRIFT')
        if any(cross.get(k) is not False for k in ('word_depth_verified','canonical_url_uniqueness_verified',
                                                   'citation_claim_support_verified','source_conflict_human_signoff','qualified_qd_pass','may_merge','may_publish')):
            errors.append('CROSSWALK_FORGED_APPROVAL')
    except (OSError,ValueError,KeyError,TypeError):errors.append('AUTHENTIC_NINE_HEAD_CROSSWALK_REQUIRED')
    return result(errors, n_article,n_tool)


def result(errors: list[str],articles=0,tools=0) -> dict:
    return {'schema':SCHEMA, 'state':'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
            'errors':sorted(set(errors)), 'articles_checked': articles, 'tools_checked':tools,
            'native_build_export_verified':False, 'qualified_qd_pass':False,
            'citations_independently_adjudicated':False, 'all_original_claim_holds_resolved':False,
            'verified_paid_preparedness_sku':False, 'may_merge':False, 'may_publish':False}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);
    ap.add_argument('--witness',type=Path);ns=ap.parse_args()
    root=ns.root.resolve();p=ns.witness or root/'audits'/'r336_frozen_41_entry_witness.json'
    try:report=audit(root,json.loads(p.read_text('utf-8')))
    except (OSError,ValueError,UnicodeError):report=result(['AUTHENTIC_WITNESS_REQUIRED'])
    print(json.dumps(report,indent=2,sort_keys=True));return 2 if report['state']=='DRAFT_HARD_HOLD' else 1

if __name__=='__main__':raise SystemExit(main())
