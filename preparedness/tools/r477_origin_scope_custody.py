#!/usr/bin/env python3
"""R477: immutable original article/source reading-scope audit; always HARD HOLD.

This is a structural custody check, not a safety, release or commerce approval.
Run after authentic original files are available; no files are written.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

REPO = 'finalvestigestudios/final-vestige-site-layer'
PARENT = '1d4d885c0b427d4b1bfbb77cf2ecf0c10a0dc070'
CROSSWALK_BLOB = 'd62e493a67dedd23e04cfdf3cce762ef933c6bf9'
MANIFEST_BLOB = '2adcffe48fcbb3ac3aa9eb2fc18b048f032fcc0c'
INDEX_BLOB = 'f6e505331a3f66c27e4ccde38dd6ca8709993b75'
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')

class Hold(ValueError):
    pass

def require(ok, message):
    if not ok:
        raise Hold(message)

def blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

def strict_json(raw: bytes):
    def obj(pairs):
        d = {}
        for k, v in pairs:
            require(k not in d, 'duplicate JSON key: '+k)
            d[k] = v
        return d
    return json.loads(raw.decode('utf-8'), object_pairs_hook=obj,
                      parse_constant=lambda x: (_ for _ in ()).throw(Hold('illegal JSON number')))

def native_file(root: Path, path: str, sha: str) -> bytes:
    require(path and not path.startswith('/') and '..' not in Path(path).parts,
            'unsafe relative file path '+path)
    root = root.resolve()
    p = root / path
    require(p.is_file() and not p.is_symlink() and p.resolve().is_relative_to(root),
            'original file missing or unsafe '+path)
    raw = p.read_bytes()
    require(blob(raw) == sha, 'original Git blob changed '+path)
    return raw

def audit(root: Path, manifest: dict, crosswalk: dict, index: dict, batches: list,
          expected=(35, 244, 202, 32, 2000, 385),
          expected_manifest_blob=MANIFEST_BLOB, expected_crosswalk_blob=CROSSWALK_BLOB,
          expected_index_blob=INDEX_BLOB) -> dict:
    articles_n, source_n, urls_n, duplicates_n, cites_n, memberships_n = expected
    require(index.get('schema') == 'fv-r477-authentic-244-source-row-index-v1', 'source index schema')
    require(index.get('repo') == REPO and index.get('candidate_ref') == PARENT, 'source index origin')
    require(index.get('crosswalk_blob') == expected_crosswalk_blob, 'crosswalk blob pin')
    require(index.get('release') == 'DRAFT_HARD_HOLD' and
            index.get('qualified_qd_pass') is False and
            index.get('publication_authorized') is False and
            index.get('review_required') is True, 'fabricated source release')
    require(index.get('raw_source_rows') == source_n and
            index.get('unique_literal_urls') == urls_n and
            index.get('shared_literal_url_groups') == duplicates_n,
            'source counts changed')
    require(crosswalk.get('raw_source_rows') == source_n and
            crosswalk.get('unique_source_urls') == urls_n and
            crosswalk.get('duplicate_url_groups') == duplicates_n,
            'native crosswalk counts changed')
    require(index.get('source_file_blobs') == [
        {'origin': f['origin'], 'path': f['path'], 'blob': f['git_blob_sha'], 'count': f['count']}
        for f in crosswalk['source_files']], 'source file inventory changed')
    require(len(index['records']) == source_n, 'lost source records')
    expected_records = []
    for f in crosswalk['source_files']:
        path = f['path'].removeprefix('preparedness/')
        require(path.startswith('sources/'), 'source outside archive')
        raw = native_file(root, path, f['git_blob_sha'])
        entries = strict_json(raw)['sources']
        require(len(entries) == f['count'], 'source file row count drift')
        expected_records.extend({'origin':f['origin'], 'source_file':f['path'],
             'source_file_git_blob':f['git_blob_sha'], 'source':s} for s in entries)
    require(index['records'] == expected_records, 'source rows/original claims changed')
    url_map = {}
    lookup = {}
    for row in expected_records:
        s = row['source']
        require(type(s.get('id')) is str and type(s.get('url')) is str and
                s['url'].startswith('https://'), 'invalid original source identity')
        url_map.setdefault(s['url'], []).append({'origin':row['origin'], 'id':s['id']})
        key = (row['origin'], s['id'])
        require(key not in lookup, 'source ID redefined within contributor origin')
        lookup[key] = s
    shared = [{'url':u, 'source_origin_id_memberships':members,
               'human_reading_scope_review':'PENDING'}
              for u, members in url_map.items() if len(members)>1]
    require(len(url_map)==urls_n and len(shared)==duplicates_n and
            index.get('shared_urls') == shared,
            'duplicate source URLs / reading-scope groups changed')
    require(manifest.get('schema') == 'fv-preparedness-r476-35-candidate-pair-snapshot-v1' and
            manifest.get('candidate_parent_sha') == '1f8261505202ccd3def3c10b34853da21868acf2' and
            manifest.get('release') == 'DRAFT_HARD_HOLD', 'R476 manifest provenance')
    frozen = manifest.get('articles')
    require(type(frozen) is list and len(frozen)==articles_n, '35-article coverage lost')
    require(type(batches) is list and len(batches)==5, 'five source-use batches required')
    expected_routes = {a['slug']:a for a in frozen}
    require(len(expected_routes)==articles_n, 'duplicate article route')
    actual_rows=[]
    for i, docket in enumerate(batches, 1):
        require(docket.get('schema') == 'fv-r477-authentic-35-article-scope-custody-batch-v1'
                and docket.get('repo') == REPO and docket.get('candidate_ref') == PARENT
                and docket.get('candidate_manifest_blob') == expected_manifest_blob
                and docket.get('crosswalk_blob') == expected_crosswalk_blob
                and docket.get('authenticated_source_index_blob') == expected_index_blob,
                'article scope batch original provenance changed')
        require(docket.get('batch') == i and docket.get('total_batches') == 5
                and docket.get('release') == 'DRAFT_HARD_HOLD'
                and docket.get('review_state') == 'ALL_CLAIM_SCOPES_UNADJUDICATED'
                and docket.get('qualified_qd_pass') is False
                and docket.get('publication_authorized') is False, 'batch review status escalated')
        require(type(docket.get('articles')) is list and len(docket['articles']) == 7,
                'missing article from source-use batch')
        actual_rows.extend(docket['articles'])
    require(len(actual_rows)==articles_n and
            [x['slug'] for x in actual_rows]==[a['slug'] for a in frozen],
            'article batch order, duplication or route drift')
    total_cites=total_memberships=0
    for row in actual_rows:
        slug=row['slug']
        pinned=expected_routes[slug]
        require(row['body_git_blob']==pinned['body']['git_blob'] and
                row['metadata_git_blob']==pinned['meta']['git_blob'],
                'changed original article Git identities '+slug)
        body=native_file(root, pinned['body']['path'], row['body_git_blob']).decode('utf-8')
        meta=strict_json(native_file(root, pinned['meta']['path'],row['metadata_git_blob']))
        require(meta['slug']==slug and row['n']==meta['n'], 'article ID drift '+slug)
        require(row['origin']==crosswalk['article_origins'][slug], 'article source origin changed '+slug)
        require(row['authored_publish']==meta['status']['publish']=='draft' and
                row['authored_safety_state']==meta['safety_review']['state'] and
                row['qualified_safety_approval_verified'] is False,
                'false approval or historical safety state changed '+slug)
        citations=[m.group(1) for m in CITE.finditer(body)]
        order=list(dict.fromkeys(citations))
        require(row['citation_sequence']==citations and
                row['citation_occurrences']==len(citations) and
                row['distinct_citation_ids']==len(order),
                'citation order or occurrences changed '+slug)
        require(set(meta['source_use'])==set(order), 'article source-use memberships changed '+slug)
        require([s['sid'] for s in row['source_claims']]==order,
                'article-source reading-scope order changed '+slug)
        for item in row['source_claims']:
            sid=item['sid']
            require(item['source_use_exact']==meta['source_use'][sid] and
                    type(item['source_use_exact']) is str and item['source_use_exact'].strip(),
                    'original reading-scope wording changed '+slug+'/'+sid)
            require(item['occurrences']==citations.count(sid), 'citation count changed '+slug+'/'+sid)
            # Authoritative Git blob and citation sequence protect the full
            # paragraph; excerpt is navigation only and never proof of safety.
            require('{{cite:'+sid+'}}' in item['first_context'],
                    'citation context evidence missing '+slug+'/'+sid)
            require((row['origin'],sid) in lookup or ('base',sid) in lookup,
                    'citation borrowed from unrelated contributor '+slug+'/'+sid)
        total_cites += len(citations)
        total_memberships += len(order)
    require(total_cites==cites_n and total_memberships==memberships_n,
            'full-original source/citation totals changed')
    return {'release':'DRAFT_HARD_HOLD', 'original_article_pairs':articles_n,
            'source_rows':source_n,'distinct_literal_urls':urls_n,
            'shared_url_review_groups':duplicates_n,'literal_citations':total_cites,
            'article_source_use_memberships':total_memberships,
            'qualified_qd_pass':False,'native_build_pass':False,
            'wordpress_export_parity_pass':False, 'publication_authorized':False,
            'verified_commercial_conversion':False}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    args=p.parse_args(argv)
    try:
        root=args.root
        m=strict_json(native_file(root,'reviews/r476_35_article_candidate_custody.json',MANIFEST_BLOB))
        c=strict_json(native_file(root,'sources/crosswalk.json',CROSSWALK_BLOB))
        s=strict_json(native_file(root,'reviews/r477_authenticated_source_register_index.json',INDEX_BLOB))
        batches=[strict_json((root/f'reviews/r477_article_scope_batch_{i}.json').read_bytes()) for i in range(1,6)]
        result=audit(root,m,c,s,batches)
    except (Hold, KeyError, OSError, TypeError, ValueError, UnicodeError) as exc:
        result={'release':'R477_NATIVE_INPUT_OR_EVIDENCE_HARD_HOLD','reason':str(exc),
                'qualified_qd_pass':False,'publication_authorized':False}
    print(json.dumps(result,sort_keys=True))
    return 2  # no structural gate is authorized to publish or claim safety

if __name__=='__main__':
    sys.exit(main())
