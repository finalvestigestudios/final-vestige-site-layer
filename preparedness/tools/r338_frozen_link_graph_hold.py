#!/usr/bin/env python3
"""R338 private-only, read-only cross-document link graph and route custody gate.

No link targets are classified as published or safe by this validator.  The
41-entry graph is expressly a *draft* editorial inventory, not an index ready
for CMS insertion, live navigation, sales or audience attribution.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from urllib.parse import unquote
from preparedness.tools import r336_frozen_archive_integrity as r336
from preparedness.tools import r337_measured_source_integrity as r337

SCHEMA = 'fv-preparedness-r338-frozen-link-graph-v1'
# Authenticated R337 JSON objects in PR #2323 at a5ae1396f19cbf04d3e9160babf7a6f386c714ab.
PART_BLOBS = (
    'cbb5abe7142639c61fdbeebd6fdf94c05bcadf35',
    '0b2d8b0ef385fec973a97170cc02581cada5798a',
    '29b3ca21a6d6fab0917f1060a85b53d4350c9cc6',
    '260d3a8e727059770fa40b9d56632ba90b76799d',
    '7255cf3ed71f01e029250e761c1ee599c4c79a9b',
)
SOURCE_PR_HEAD = 'a5ae1396f19cbf04d3e9160babf7a6f386c714ab'
EXPECTED = {'rows':41, 'articles':35, 'tools':6, 'links':159, 'targets':37}


def result(errors: list[str], *, rows=0, links=0, targets=0, tool_links=0) -> dict:
    return {'schema':SCHEMA,'state':'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
            'errors':sorted(set(errors)), 'entries_checked':rows,
            'internal_link_occurrences':links, 'distinct_link_targets':targets,
            'internal_links_to_unpublished_tools':tool_links,
            'source_head':SOURCE_PR_HEAD, 'all_41_items_draft_only':True,
            'independent_claim_source_support_verified':False,
            'tool_104_emergency_privacy_approved':False,
            'native_wordpress_preview_build_verified':False,
            'paid_preparedness_sku_verified':False,
            'qualified_qd_pass':False, 'may_merge':False, 'may_publish':False,
            'may_activate_commerce':False}


def graph(rows: list[dict], *, require_authentic_counts: bool = False) -> dict:
    """Pure deterministic graph audit; synthetic fixtures cannot authorize release."""
    errors=[]; by_slug={}; routes={}; links=0; targets=set(); tool_links=0
    if not isinstance(rows,list) or len(rows)!=41:
        return result(['GRAPH_REQUIRES_EXACTLY_41_ROWS'],rows=len(rows) if isinstance(rows,list) else 0)
    for i,row in enumerate(rows):
        if not isinstance(row,dict):
            errors.append(f'INVALID_ROW:{i}');continue
        kind=row.get('kind');slug=row.get('slug');route=row.get('route')
        if kind not in ('articles','tools') or not isinstance(slug,str) or not r336.SLUG.fullmatch(slug):
            errors.append(f'INVALID_KIND_OR_SLUG:{i}');continue
        if slug in by_slug: errors.append('DUPLICATE_CROSS_KIND_SLUG:'+slug)
        by_slug[slug]=row
        if not isinstance(route,str) or not route.startswith('/preparedness/') or not route.endswith('/') or any(x in route for x in ('?', '#', '%', '//', '\\')):
            errors.append('INVALID_CANONICAL_ROUTE:'+slug)
        else:
            key=unquote(route).casefold()
            if key in routes: errors.append('DUPLICATE_ROUTE:'+slug)
            routes[key]=slug
            if route.split('/')[-2]!=slug or len(route.split('/'))!=5:
                errors.append('ROUTE_SLUG_OR_SECTION_DRIFT:'+slug)
        counts=row.get('links')
        if not isinstance(counts,dict):
            errors.append('INVALID_LINK_COUNTER:'+slug);continue
        for target,count in counts.items():
            if not isinstance(target,str) or not r336.SLUG.fullmatch(target):
                errors.append('INVALID_LINK_TARGET:'+slug);continue
            if type(count) is not int or count < 1:
                errors.append('INVALID_LINK_OCCURRENCE_COUNT:'+slug+':'+target);continue
            links+=count;targets.add(target)
    for slug,row in by_slug.items():
        if not isinstance(row.get('links'),dict):continue
        for target,count in row['links'].items():
            if not isinstance(target,str) or not r336.SLUG.fullmatch(target):continue
            if target not in by_slug:errors.append('UNRESOLVED_INTERNAL_LINK:'+slug+':'+target)
            elif by_slug[target]['kind']=='tools' and type(count) is int and count>0:tool_links+=count
    if len([r for r in by_slug.values() if r['kind']=='articles'])!=35 or len([r for r in by_slug.values() if r['kind']=='tools'])!=6:
        errors.append('35_ARTICLE_6_TOOL_INVENTORY_DRIFT')
    a=by_slug.get('family-reunification-card');b=by_slug.get('reunification-plan')
    if not a or not b or a is b or a.get('kind')!='tools' or b.get('kind')!='tools' or a.get('route')==b.get('route'):
        errors.append('TOOL_104_AND_102_IDENTITY_NOT_DISTINCT')
    if require_authentic_counts:
        for field,actual in [('rows',len(rows)),('articles',sum(r.get('kind')=='articles' for r in by_slug.values())),
                             ('tools',sum(r.get('kind')=='tools' for r in by_slug.values())),
                             ('links',links),('targets',len(targets))]:
            if actual!=EXPECTED[field]:errors.append('AUTHENTIC_GRAPH_'+field.upper()+'_DRIFT')
    return result(errors,rows=len(rows),links=links,targets=len(targets),tool_links=tool_links)


def audit(root: Path, *, synthetic_witness: dict|None = None, enforce_frozen_pins: bool = True) -> dict:
    """Fail closed unless all previous source-custody gates and the graph pass."""
    previous=r337.audit(root,prior_witness=synthetic_witness)
    if previous['state']!='DRAFT_HARD_HOLD':
        return result(['R337_SOURCE_DEPTH_AND_CITATION_CUSTODY_FAILED']+previous['errors'])
    all_rows=[];errors=[]
    for n,start,end in r337.PARTS:
        p=root/'audits'/f'r337_source_metrics_part_{n:02d}.json'
        try:
            raw=p.read_bytes();part=json.loads(raw.decode('utf-8'))
        except (OSError,ValueError,UnicodeError):
            errors.append(f'MISSING_OR_UNREADABLE_GRAPH_SOURCE_PART:{n:02d}');continue
        if enforce_frozen_pins and r336.git_blob(raw)!=PART_BLOBS[n-1]:
            errors.append(f'FROZEN_GRAPH_SOURCE_PART_CHANGED:{n:02d}')
        if part.get('schema')!=r337.SCHEMA or part.get('source_commit')!=r337.SOURCE_COMMIT or part.get('r336_witness_blob')!=r337.PRIOR_WITNESS_BLOB or part.get('part')!=n or part.get('range')!=[start,end]:
            errors.append(f'GRAPH_SOURCE_PART_IDENTITY_DRIFT:{n:02d}')
        if not isinstance(part.get('rows'),list) or len(part['rows'])!=end-start:
            errors.append(f'GRAPH_SOURCE_PART_LENGTH_DRIFT:{n:02d}')
        else:all_rows.extend(part['rows'])
    r=graph(all_rows,require_authentic_counts=enforce_frozen_pins)
    return result(errors+r['errors'],rows=r['entries_checked'],links=r['internal_link_occurrences'],
                  targets=r['distinct_link_targets'],tool_links=r['internal_links_to_unpublished_tools'])


def main()->int:
    parser=argparse.ArgumentParser(description='Read-only draft-only FV internal link and held-tool crosswalk')
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);args=parser.parse_args()
    print(json.dumps(audit(args.root.resolve()),indent=2,sort_keys=True))
    return 2  # even a clean inventory is DRAFT / HARD HOLD, never publish authorization


if __name__=='__main__':raise SystemExit(main())
