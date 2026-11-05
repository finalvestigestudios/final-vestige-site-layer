#!/usr/bin/env python3
"""R149 read-only candidate tool/source-use claim docket and exact-evidence custody.

A matching generated docket proves only deterministic accounting of *unreviewed*
source-use explanations. It does not verify a link, emergency advice, medical
claims, paid offer, QD, WordPress draft or publisher authorization.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re

CITE = re.compile(r'\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
SCHEMA = 'FV-PREP-R149-TOOL-CLAIM-CUSTODY-1'
CANDIDATES = {
    'water-planner': 'base',
    'home-fire-escape-worksheet': 'shelter',
    'power-outage-planner': 'shelter',
    'family-reunification-card': 'shelter',
    'reunification-plan': 'start',
    'kit-builder': 'start',
}

class Hold(ValueError):
    """Source provenance is uncertain: release must remain on HOLD."""

def require(condition, why):
    if not condition:
        raise Hold(why)

def read_bytes(root, relative):
    require(isinstance(relative, str) and not relative.startswith('/') and '..' not in Path(relative).parts, 'unsafe evidence path')
    path = root / relative
    require(path.is_file() and not path.is_symlink(), f'missing/linked evidence file {relative}')
    return path.read_bytes()

def blob_id(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\x00' + raw).hexdigest()

def read_json(root, relative):
    obj = json.loads(read_bytes(root, relative).decode('utf-8', errors='strict'))
    require(isinstance(obj, dict), f'expected object in {relative}')
    return obj

def source_index(root, paths):
    found = {}
    for origin, relative in paths.items():
        entries = read_json(root, relative).get('sources')
        require(isinstance(entries, list), f'source file has no rows: {relative}')
        for idx, rec in enumerate(entries):
            require(isinstance(rec, dict), f'invalid source row: {relative}#{idx}')
            sid, url = rec.get('id'), rec.get('url')
            require(isinstance(sid, str) and SLUG.fullmatch(sid) and
                    isinstance(url, str) and url.startswith('https://') and url == url.strip(),
                    f'invalid source identity {relative}#{idx}')
            require((origin, sid) not in found, f'duplicate origin/source identity {origin}/{sid}')
            found[(origin, sid)] = rec
    return found

def make_docket(root, *, candidates=None, expected_tool_count=6):
    root = Path(root).resolve(strict=True)
    candidates = dict(CANDIDATES if candidates is None else candidates)
    require(candidates and all(isinstance(k,str) and SLUG.fullmatch(k) and
             isinstance(v,str) and SLUG.fullmatch(v) for k,v in candidates.items()),
            'invalid candidate map')
    source_paths = {'base': 'sources/register.json',
                    'start': 'sources/fragments/start.json',
                    'shelter': 'sources/fragments/shelter.json'}
    sources = source_index(root, source_paths)
    crosswalk = read_json(root, 'sources/crosswalk.json')
    configured = crosswalk.get('article_origins')
    require(isinstance(configured, dict), 'missing article-origin crosswalk')
    meta_dir = root / 'content/tools'
    metas = sorted(meta_dir.glob('*.meta.json'))
    require(len(metas) == expected_tool_count and
            set(p.name.removesuffix('.meta.json') for p in metas) == set(candidates),
            'tool inventory/candidate mismatch')
    exact_paths = ['sources/crosswalk.json', *source_paths.values()]
    rows, summaries = [], []
    for meta_path in metas:
        slug = meta_path.name.removesuffix('.meta.json')
        rel_meta, rel_body = f'content/tools/{slug}.meta.json', f'content/tools/{slug}.body.html'
        meta = read_json(root, rel_meta)
        raw_body = read_bytes(root, rel_body)
        body = raw_body.decode('utf-8',errors='strict')
        use = meta.get('source_use')
        require(meta.get('slug') == slug and meta.get('status',{}).get('publish') == 'draft',
                f'{slug}: non-draft or mismatched tool metadata')
        require(isinstance(use,dict) and use and all(isinstance(k,str) and SLUG.fullmatch(k)
                and isinstance(v,str) and v.strip() for k,v in use.items()),
                f'{slug}: missing/invalid author source-use')
        cites = CITE.findall(body)
        require(body.count('{{cite:') == len(cites) and set(cites) == set(use),
                f'{slug}: body citations and author source use disagree')
        selected = candidates[slug]
        actual = configured.get(slug, 'base')
        require(isinstance(actual,str) and SLUG.fullmatch(actual), 'invalid recorded origin')
        unresolved = []
        for sid in sorted(use):
            active_source = sources.get((actual,sid)) or sources.get(('base',sid))
            if not active_source:
                unresolved.append(sid)
            preferred_origin = selected if (selected,sid) in sources else 'base'
            rec = sources.get((preferred_origin,sid))
            require(rec is not None and isinstance(rec.get('supports'),str) and rec['supports'].strip(),
                    f'{slug}/{sid}: candidate has no documented source support')
            note = use[sid]
            require(isinstance(note,str) and note.strip(), f'{slug}/{sid}: missing author explanation')
            rows.append({
                'tool': slug, 'source_id': sid, 'citation_occurrences': cites.count(sid),
                'current_origin': actual, 'candidate_origin': selected,
                'effective_source_origin': preferred_origin,
                'currently_resolvable': bool(active_source),
                'title': rec.get('title'), 'publisher': rec.get('publisher'),
                'literal_url': rec['url'], 'source_supports': rec['supports'],
                'author_specific_use': note,
                'source_verified_on_metadata': rec.get('verified_on'),
                'human_link_check_recorded': rec.get('human_link_check') is True,
                'human_source_scope_adjudicated': False, 'medical_safety_approved': False,
                'reviewer': None, 'review_decision': 'PENDING',
            })
        summaries.append({'tool':slug, 'current_origin':actual,'candidate_origin':selected,
                          'unique_cited_sources':len(use),'citation_occurrences':len(cites),
                          'currently_unresolved_source_ids':unresolved,
                          'publication_allowed':False})
        exact_paths.extend((rel_meta,rel_body))
    require(len(exact_paths)==len(set(exact_paths)), 'duplicate custody path')
    custody={p:blob_id(read_bytes(root,p)) for p in sorted(exact_paths)}
    return {'schema':SCHEMA, 'status':'CANDIDATE_ONLY_HUMAN_SOURCE_REVIEW_REQUIRED',
            'base_parent_sha':'1ff2ea77afba5e6fd0d0c11577235a5f36f6f92e',
            'immutable_git_blob_sha1':custody, 'candidate_tool_origins':dict(sorted(candidates.items())),
            'tool_summaries':summaries,'source_use_rows':rows,
            'source_use_row_count':len(rows),
            'currently_unresolved_source_ids':sum(len(t['currently_unresolved_source_ids']) for t in summaries),
            'human_link_checked_rows':sum(r['human_link_check_recorded'] for r in rows),
            'source_scope_human_review':'PENDING', 'independent_qd':'NOT_APPROVED',
            'publication_allowed':False, 'payment_offer_verified':False,
            'customer_conversion_verified':False}

def verify(root, reference, *, expected_tool_count=6):
    require(isinstance(reference, dict) and reference.get('schema')==SCHEMA,
            'missing or invalid immutable review docket')
    require(reference.get('candidate_tool_origins')==dict(sorted(CANDIDATES.items())) if expected_tool_count == 6
            else isinstance(reference.get('candidate_tool_origins'),dict), 'unapproved candidate map')
    live = make_docket(root,candidates=reference['candidate_tool_origins'],expected_tool_count=expected_tool_count)
    require(reference == live, 'SOURCE_CUSTODY_DRIFT: regenerate review-only docket and re-adjudicate; never auto-apply')
    return {'schema':SCHEMA,'status':'DRAFT_HOLD', 'matched_source_use_rows':len(live['source_use_rows']),
            'currently_unresolved_source_ids':live['currently_unresolved_source_ids'],
            'human_link_checked_rows':live['human_link_checked_rows'],
            'publication_allowed':False,'human_source_review':'PENDING',
            'independent_qd':'NOT_APPROVED','merchant_offer_verified':False}

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--preparedness',default='preparedness')
    ap.add_argument('--docket',default='preparedness/docs/r149/tool-source-use-review-docket.json')
    args=ap.parse_args(argv)
    try:
        ref=json.loads(Path(args.docket).read_text(encoding='utf-8'))
        out=verify(args.preparedness,ref)
        # Remain fail-closed even when the proposed origin mapping is fully accounted for.
        code=2 if out['currently_unresolved_source_ids'] or out['human_source_review']=='PENDING' else 0
    except (Hold,ValueError,TypeError,KeyError,OSError,UnicodeError, json.JSONDecodeError) as exc:
        out={'schema':SCHEMA,'status':'HOLD','error':str(exc),
             'publication_allowed':False,'independent_qd':'NOT_APPROVED'}
        code=2
    print(json.dumps(out,indent=2,sort_keys=True))
    return code

if __name__=='__main__':
    raise SystemExit(main())
