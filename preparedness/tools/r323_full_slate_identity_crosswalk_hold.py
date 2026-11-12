#!/usr/bin/env python3
"""R323: read-only 35-article/6-tool crosswalk; verified bytes are NOT safety approval.

Runs only against the pinned R319 tree and R320 review docket. All 15 disputes
stay held; neither variant selection nor CMS/commerce mutation is possible.
"""
from __future__ import annotations
import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from preparedness.tools import r319_three_way_custody_hold as custody
from preparedness.tools import r320_conflict_adjudication_docket_hold as review
from preparedness.tools import r321_conflict_content_delta_hold as delta

SCHEMA = 'fv-preparedness-r323-41-source-identity-depth-crosswalk-v1'
CITE = re.compile(r'\{\{cite:([a-z0-9][a-z0-9-]{1,99})\}\}')
RELEASE = dict(publication_authorized=False, independent_qd_pass=False,
               qualified_safety_approved=False, automatic_merge_permitted=False,
               paid_conversion_verified=False)

class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.text = []
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'template'): self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'template'): self.skip = max(0, self.skip-1)
    def handle_data(self, data):
        if not self.skip: self.text.append(data)

def strict_json(data: bytes):
    return delta.strict_json(data)

def audit(manifest: dict, docket: dict, taxonomy: dict, loader) -> dict:
    """loader(path)->raw bytes, never writes source. Every file must match a pinned blob."""
    errors, warnings, entries = [], [], []
    if custody.validate_manifest(manifest)['errors']:
        errors.append('R319_INTEGRATED_INVENTORY_INVALID')
    if review.validate_docket(manifest, docket)['errors']:
        errors.append('R320_CONFLICT_REVIEW_DOCKET_INVALID')
    if not isinstance(taxonomy, dict) or taxonomy.get('base_path') != '/preparedness/':
        errors.append('TAXONOMY_BASE_PATH_DRIFT'); taxonomy = {}
    sections = {r.get('slug') for r in taxonomy.get('sections', []) if isinstance(r, dict)}
    slate = taxonomy.get('slate', [])
    tools = taxonomy.get('tools', [])
    if not isinstance(slate, list) or len(slate) != 35 or not isinstance(tools, list):
        errors.append('TAXONOMY_ARTICLE_OR_TOOL_MAP_INVALID'); slate = []; tools = []
    article_index = {r.get('slug'): r for r in slate if isinstance(r, dict)}
    tool_index = {r.get('slug'): r for r in tools if isinstance(r, dict)}
    if len(article_index) != 35 or len(slate) != len(article_index):
        errors.append('TAXONOMY_DUPLICATE_OR_MISSING_ARTICLES')
    source_map = {r['path']:r for r in manifest.get('records', []) if isinstance(r, dict) and isinstance(r.get('path'), str)}
    identities, numbers, urls, sources = set(), {'articles':set(), 'tools':set()}, set(), {}
    for family, count in (('articles', 35), ('tools', 6)):
        prefix = 'preparedness/content/' + family + '/'
        paths = sorted(p for p in source_map if p.startswith(prefix) and p.endswith('.meta.json'))
        if len(paths) != count: errors.append('MISSING_AUTHORED_META_SET:' + family)
        for meta_path in paths:
            slug = meta_path[len(prefix):-len('.meta.json')]
            body_path = prefix + slug + '.body.html'
            try:
                meta_bytes, body_bytes = loader(meta_path), loader(body_path)
                for path, raw in ((meta_path, meta_bytes), (body_path, body_bytes)):
                    pin = source_map[path]['integrated']
                    if not isinstance(raw, bytes) or len(raw) != pin['size'] or custody.blob(raw) != pin['sha']:
                        raise ValueError('AUTHORED_SOURCE_BLOB_DRIFT')
                meta = strict_json(meta_bytes)
                body = body_bytes.decode('utf-8', 'strict')
                if not isinstance(meta, dict): raise ValueError('NONOBJECT_METADATA')
            except (KeyError, ValueError, UnicodeError, TypeError, OSError) as exc:
                errors.append('MISSING_OR_CHANGED_PINNED_PAIR:' + slug + ':' + type(exc).__name__)
                continue
            if meta.get('slug') != slug: errors.append('METADATA_SLUG_DRIFT:' + slug)
            kind = ('articles' if family == 'articles' else 'tools')
            if meta.get('kind', 'article') != ('article' if kind == 'articles' else 'tool'):
                errors.append('METADATA_KIND_DRIFT:' + slug)
            index = article_index if kind == 'articles' else tool_index
            node = index.get(slug)
            if not node: errors.append('TAXONOMY_MISSING_SOURCE_IDENTITY:' + slug)
            else:
                if family == 'articles' and any(meta.get(k) != node.get(k) for k in ('n','section','track')):
                    errors.append('ARTICLE_TAXONOMY_IDENTITY_DRIFT:' + slug)
                if family == 'tools' and meta.get('section') != 'field-tools':
                    errors.append('TOOL_SECTION_DRIFT:' + slug)
            number = meta.get('n')
            if type(number) is not int or number in numbers[kind]:
                errors.append('MISSING_OR_DUPLICATE_NUMBER:' + slug)
            else: numbers[kind].add(number)
            section = meta.get('section')
            if not isinstance(section, str) or section not in sections:
                errors.append('INVALID_SOURCE_SECTION:' + slug)
                section = 'INVALID'
            canonical = 'https://finalvestige.com/preparedness/' + section + '/' + slug + '/'
            if canonical in urls or slug in identities: errors.append('DUPLICATE_CANONICAL_OR_SLUG:' + slug)
            urls.add(canonical); identities.add(slug)
            status = meta.get('status')
            if not isinstance(status, dict) or status.get('publish') != 'draft':
                errors.append('NON_DRAFT_AUTHORED_SOURCE:' + slug)
            sr = meta.get('safety_review')
            if not isinstance(sr, dict) or sr.get('state') not in ('pending','approved','not-required','not_required','not required'):
                errors.append('UNKNOWN_SAFETY_REVIEW_STATE:' + slug)
            elif sr['state'] == 'approved':
                warnings.append('APPROVED_LABEL_NOT_INDEPENDENT_QD_PASS:' + slug)
            uses = meta.get('source_use')
            cited = set(CITE.findall(body))
            if not isinstance(uses, dict) or any(not isinstance(k,str) or not isinstance(v,str) for k,v in uses.items()):
                errors.append('MISSING_SOURCE_USE_EVIDENCE:' + slug)
            else:
                if set(uses) != cited: errors.append('CITATION_DECLARATION_MISMATCH:' + slug)
            if '{{cite:' in body and len(CITE.findall(body)) != body.count('{{cite:'):
                errors.append('MALFORMED_CITATION_TOKEN:' + slug)
            visible = VisibleText(); visible.feed(body); visible.close()
            words = len(re.findall(r"\b[\w'-]+\b", ' '.join(visible.text)))
            if words < 1: errors.append('MISSING_READING_DEPTH:' + slug)
            sources[slug] = meta
            entries.append({'slug':slug,'type':kind,'number':number,'canonical':canonical,
                            'source_count':len(cited),'visible_words':words,'publication':'draft',
                            'safety_state':sr.get('state') if isinstance(sr,dict) else None,
                            'body_git_blob':source_map[body_path]['integrated']['sha'],
                            'metadata_git_blob':source_map[meta_path]['integrated']['sha']})
    for slug, meta in sources.items():
        rel = meta.get('related', [])
        if not isinstance(rel, list) or any(not isinstance(x,str) or x not in identities for x in rel):
            errors.append('BROKEN_INTERNAL_RELATED_ROUTE:' + slug)
    if len(entries) != 41: errors.append('NOT_ALL_41_AUTHORED_GUIDES_PRESENT')
    for slug, n in (('reunification-plan',102),('family-reunification-card',104)):
        row = next((x for x in entries if x['slug']==slug and x['type']=='tools'),None)
        if not row or row['number'] != n: errors.append('REUNIFICATION_TOOL_IDENTITY_COLLISION:' + slug)
    if set(x['slug'] for x in entries if x['type']=='articles') != set(article_index):
        errors.append('ARTICLE_SLATE_COVERAGE_LOST')
    return {'schema':SCHEMA,'state':'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
            'errors':sorted(set(errors)), 'independent_review_flags':sorted(set(warnings)),
            'guides_audited':len(entries), 'source_conflicts_held':15,
            'entries':sorted(entries,key=lambda x:(x['type'],x['number'] if type(x['number']) is int else -1)),
            'release':RELEASE.copy()}

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]); args=ap.parse_args()
    root=args.root.resolve()
    try:
        def read(rel):
            if rel in (custody.MANIFEST_PATH, 'preparedness/audits/r320_conflict_adjudication_docket.json', 'preparedness/taxonomy.json'):
                p=root
                for part in Path(rel).parts:
                    p=p/part
                    if p.is_symlink(): raise OSError('linked audit input')
                return p.read_bytes()
            b = custody.safe_bytes(root,rel)
            if b is None: raise OSError('missing or symlinked authored file')
            return b
        m = strict_json(read(custody.MANIFEST_PATH))
        d = strict_json(read('preparedness/audits/r320_conflict_adjudication_docket.json'))
        t = strict_json(read('preparedness/taxonomy.json'))
        result = audit(m,d,t,read)
        if custody.validate_manifest(m,root)['errors']:
            result['state']='INVALID_HARD_HOLD';result['errors'].append('NATIVE_CHECKOUT_LINEAGE_DRIFT')
    except (OSError,ValueError,KeyError,TypeError,UnicodeError):
        result={'schema':SCHEMA,'state':'INVALID_HARD_HOLD','errors':['AUTHENTIC_COMPLETE_CHECKOUT_REQUIRED'],
                'release':RELEASE.copy(),'guides_audited':0,'source_conflicts_held':15}
    print(json.dumps(result,indent=2,sort_keys=True))
    return 2 if result['state']=='DRAFT_HARD_HOLD' else 1

if __name__ == '__main__':raise SystemExit(main())
