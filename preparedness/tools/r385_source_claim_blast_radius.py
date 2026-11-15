"""R385: review-only original claim/source conflict blast-radius custody (#136).

Combines the R384 immutable 35-article review packet, R375 contributor source
variants, and BASE register. Every output is an *unreviewed review docket*.
Never selects a conflicting source, changes original advice, or authorizes QD.
Requires original Git blobs when run against an authentic checkout.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
SOURCE_ID = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
CITATION = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
HEX = re.compile(r'^[a-f0-9]{40}$')
OBJECT_BLOB = '5e7d9a8972872c82b4bc46ac13aab18883d8149a'
SOURCE_BLOB = '24b49f0a423119c2f612455f021669709a3f22b5'
BASE_BLOB = 'b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77'
EXPECTED_COLLISIONS = {'fsis-power-failure', 'loc-pioneer-diaries', 'loc-prairie-traveler',
                       'nchfp-home', 'nchfp-jerky'}
RELEASE_STATUS = 'DRAFT_HARD_HOLD'


def _load_module(filename, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def stable_sha(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data,
                        usedforsecurity=False).hexdigest()


def clean_source(s, origin):
    if not isinstance(s, dict) or not isinstance(s.get('id'), str) or not SOURCE_ID.fullmatch(s['id']):
        raise ValueError('MALFORMED_SOURCE_RECORD')
    return {'source_id': s['id'], 'origin': origin,
            'evidence_hash': stable_sha({k: s.get(k) for k in ('url', 'publisher', 'kind', 'verified_on',
                       'human_link_check', 'supports', 'notes')}),
            'link_human_checked': s.get('human_link_check') is True}


def source_index(crosswalk: dict, base: dict, branch_names: set[str]) -> tuple[dict, list[str]]:
    errors = []
    rows = defaultdict(list)
    base_rows = base.get('sources') if isinstance(base, dict) else None
    if not isinstance(base_rows, list):
        return {}, ['BASE_REGISTRY_INVALID']
    own_base = set()
    for src in base_rows:
        try:
            rec = clean_source(src, 'BASE')
            if rec['source_id'] in own_base: errors.append('DUPLICATE_BASE_ID:' + rec['source_id'])
            own_base.add(rec['source_id'])
            rows[rec['source_id']].append(rec)
        except ValueError as e:
            errors.append(str(e))
    groups = crosswalk.get('source_id_variants') if isinstance(crosswalk, dict) else None
    if not isinstance(groups, list):
        return dict(rows), sorted(set(errors + ['SOURCE_CROSSWALK_INVALID']))
    seen_ids = set()
    for group in groups:
        if not isinstance(group, dict) or not isinstance(group.get('id'), str):
            errors.append('SOURCE_GROUP_INVALID'); continue
        sid = group['id']
        if not SOURCE_ID.fullmatch(sid) or sid in seen_ids:
            errors.append('DUPLICATE_OR_INVALID_SOURCE_GROUP:' + sid); continue
        seen_ids.add(sid)
        vs = group.get('variants')
        if not isinstance(vs, list) or not vs:
            errors.append('EMPTY_SOURCE_GROUP:' + sid); continue
        seen_origins = set()
        for v in vs:
            if not isinstance(v, dict) or v.get('id') != sid:
                errors.append('SOURCE_VARIANT_ID_MISMATCH:' + sid); continue
            branch = v.get('branch'); fragment = v.get('fragment')
            if branch not in branch_names or not isinstance(fragment, str) or not fragment.startswith('preparedness/sources/fragments/'):
                errors.append('SOURCE_VARIANT_ORIGIN_INVALID:' + sid); continue
            key = (branch, fragment)
            if key in seen_origins: errors.append('DUPLICATE_SOURCE_VARIANT_ORIGIN:' + sid)
            seen_origins.add(key)
            rec = clean_source(v, branch)
            rec.update({'fragment': fragment, 'source_blob': v.get('source_blob')})
            if not HEX.fullmatch(str(rec['source_blob'])):
                errors.append('SOURCE_BLOB_INVALID:' + sid)
            rows[sid].append(rec)
    return {k: sorted(v, key=lambda row: (row['origin'], row['evidence_hash']))
            for k,v in sorted(rows.items())}, sorted(set(errors))


def claim_impact(packet: dict, index: dict, collision_ids: set[str], *, original_enforcement=True) -> dict:
    """Pure, deterministic impact inventory. Explicitly not a source judgement.

    All citation occurrences retain branch, original body blob, ordinal, paragraph
    hash and article-specific source_use digest so human reviewers can find them.
    No claim text or personal data is exported.
    """
    errors = []
    if packet.get('status') != 'REVIEW_PACKET_HARD_HOLD' or packet.get('publication_approved') is not False:
        errors.append('ORIGINAL_REVIEW_PACKET_INVALID')
    articles = packet.get('articles', [])
    if original_enforcement and len(articles) != 35:
        errors.append('ORIGINAL_ARTICLE_COUNT_INVALID')
    if original_enforcement and len(packet.get('unselected_conflicts', [])) != 9:
        errors.append('ORIGINAL_FORK_CUSTODY_INVALID')
    impact = defaultdict(list)
    ledger = []
    missing = []
    seen = set()
    for art in articles:
        if not isinstance(art, dict) or not isinstance(art.get('slug'), str):
            errors.append('ARTICLE_ROW_INVALID'); continue
        slug = art['slug']
        for v in art.get('variants', []):
            if not isinstance(v, dict): errors.append('ARTICLE_VARIANT_INVALID'); continue
            branch, body_sha = v.get('branch'), v.get('body_sha')
            if not isinstance(branch, str) or not HEX.fullmatch(str(body_sha)):
                errors.append('ARTICLE_PROVENANCE_INVALID:' + slug); continue
            if (slug, branch) in seen: errors.append('DUPLICATE_ARTICLE_VARIANT:' + slug)
            seen.add((slug, branch))
            scopes = v.get('source_use')
            if not isinstance(scopes, dict):
                errors.append('SOURCE_USE_NOT_DICT:' + slug); continue
            occurrence = 0
            for block_number, block in enumerate(v.get('blocks', []), 1):
                if not isinstance(block, dict): errors.append('BLOCK_INVALID:' + slug); continue
                block_hash = block.get('prose_sha256')
                if not isinstance(block_hash, str) or not re.fullmatch(r'[a-f0-9]{64}', block_hash):
                    errors.append('BLOCK_FINGERPRINT_INVALID:' + slug); continue
                for sid in block.get('citations', []):
                    occurrence += 1
                    if not isinstance(sid, str) or not SOURCE_ID.fullmatch(sid):
                        errors.append('INVALID_CITATION_ID:' + slug); continue
                    candidates = index.get(sid, [])
                    scopestring = scopes.get(sid)
                    status = 'SOURCE_REVIEW_REQUIRED'
                    if not candidates: status = 'UNRESOLVED_SOURCE_ID'
                    elif sid in collision_ids: status = 'CONFLICTING_SOURCE_EVIDENCE'
                    elif not isinstance(scopestring, str) or not scopestring.strip():
                        status = 'MISSING_ARTICLE_SCOPE'
                    elif any(x['origin'] == branch for x in candidates):
                        status = 'OWN_BRANCH_OR_BASE_CUSTODY_ONLY'
                    elif any(x['origin'] == 'BASE' for x in candidates):
                        status = 'BASE_FALLBACK_CUSTODY_ONLY'
                    else: status = 'OTHER_BRANCH_SOURCE_UNVERIFIED'
                    row = {'article': slug, 'branch': branch, 'body_blob': body_sha,
                           'claim_sha256': block_hash, 'block': block_number, 'citation_ordinal': occurrence,
                           'source_id': sid, 'source_use_sha256': stable_sha(scopestring) if isinstance(scopestring,str) else None,
                           'candidate_origins': sorted(set(c['origin'] for c in candidates)),
                           'source_variant_fingerprints': sorted(set(c['evidence_hash'] for c in candidates)),
                           'review_status': status, 'human_adjudicated': False}
                    ledger.append(row)
                    if sid in collision_ids: impact[sid].append(row)
                    if status in {'UNRESOLVED_SOURCE_ID','MISSING_ARTICLE_SCOPE','OTHER_BRANCH_SOURCE_UNVERIFIED'}:
                        missing.append({'article': slug, 'branch': branch, 'source_id': sid,
                                        'citation_ordinal': occurrence, 'reason': status})
    ledger.sort(key=lambda x: (x['article'], x['branch'], x['citation_ordinal']))
    unresolved = []
    for sid in sorted(collision_ids):
        candidates = index.get(sid, [])
        all_hashes = sorted(set(c['evidence_hash'] for c in candidates if c['origin'] != 'BASE'))
        if len(all_hashes) < 2:
            errors.append('COLLISION_EVIDENCE_MISSING_OR_CONVERGED:' + sid)
        refs = impact.get(sid, [])
        unresolved.append({'source_id': sid, 'original_variant_hashes': all_hashes,
                           'impacted_citation_occurrences': len(refs),
                           'impacted_articles': sorted(set(x['article'] for x in refs)),
                           'affected_original_bodies': sorted(set(x['body_blob'] for x in refs)),
                           'qualified_review_required': True, 'human_adjudicated': False})
    statuses = dict(sorted(Counter(x['review_status'] for x in ledger).items()))
    if not ledger: errors.append('EMPTY_CITATION_LEDGER')
    if any(x.get('human_adjudicated') for x in ledger): errors.append('UNAUTHORIZED_HUMAN_REVIEW_STATE')
    result = {'schema': 1, 'release_state': RELEASE_STATUS,
              'status': 'INVALID_HARD_HOLD' if errors else 'SOURCE_IMPACT_REVIEW_HARD_HOLD',
              'errors': sorted(set(errors)), 'claims': ledger, 'source_collisions': unresolved,
              'source_gaps': sorted(missing, key=lambda x:(x['article'],x['branch'],x['citation_ordinal'])),
              'counts': {'original_articles': len(articles), 'manuscript_variants': len(seen),
                         'citation_occurrences': len(ledger), 'source_collision_groups': len(unresolved),
                         'impacted_collision_occurrences': sum(x['impacted_citation_occurrences'] for x in unresolved),
                         'source_gaps': len(missing), 'review_states': statuses},
              'qualified_safety_approved': False, 'publication_approved': False,
              'merchant_offer_verified': False, 'live_release_allowed': False}
    result['claim_ledger_sha256'] = stable_sha(ledger)
    return result


def build_original_docket(objects: dict, sources: dict, base: dict, reader) -> dict:
    """Use earlier R384/R375 strict custody gates; never call a publisher."""
    r384 = _load_module('r384_variant_review_packet.py','r384_dependency')
    r375 = _load_module('r375_source_collision_integrity_gate.py','r375_dependency')
    checked = r375.check_crosswalk(objects, sources)
    if checked.get('status') != 'SOURCE_REVIEW_HARD_HOLD':
        return {'status':'INVALID_HARD_HOLD','errors':['R375_SOURCE_CUSTODY_FAILURE'] + checked.get('issues', []),
                'publication_approved':False}
    if {r['id'] for r in checked['divergent_source_review_queue']} != EXPECTED_COLLISIONS:
        return {'status':'INVALID_HARD_HOLD','errors':['ORIGINAL_FIVE_COLLISIONS_CHANGED'],
                'publication_approved':False}
    packet = r384.build_packet(objects, reader)
    if packet.get('status') != 'REVIEW_PACKET_HARD_HOLD':
        return {'status':'INVALID_HARD_HOLD','errors':['R384_BLOB_CUSTODY_FAILURE'] + packet.get('errors', []),
                'publication_approved':False}
    branches = {p['branch'] for p in objects['branch_pins']}
    index, errors = source_index(sources, base, branches)
    if errors:
        return {'status':'INVALID_HARD_HOLD','errors':errors,'publication_approved':False}
    result = claim_impact(packet, index, EXPECTED_COLLISIONS)
    result['source_manifest_sha256'] = stable_sha(sources)
    result['object_manifest_sha256'] = stable_sha(objects)
    result['base_register_sha256'] = stable_sha(base)
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', default='.')
    args = ap.parse_args()
    def read(sha):
        return subprocess.run(['git','-C',args.repo,'cat-file','blob',sha], check=True,
                              capture_output=True,timeout=20).stdout
    try:
        objects, sources, base = [] , [] , []
        for oid in (OBJECT_BLOB,SOURCE_BLOB,BASE_BLOB):
            raw = read(oid)
            if git_blob(raw) != oid: raise ValueError('INPUT_GIT_BLOB_SHA_MISMATCH')
            objects.append(json.loads(raw))
        doc = build_original_docket(*objects, read)
    except (ValueError, TypeError, OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        doc={'status':'INVALID_HARD_HOLD','errors':['AUTHENTIC_ORIGINAL_OBJECTS_UNAVAILABLE:'+type(exc).__name__],
             'publication_approved':False,'qualified_safety_approved':False}
    print(json.dumps(doc,sort_keys=True,indent=2))
    return 2 # Even a valid review packet is never publication clearance.


if __name__ == '__main__':
    raise SystemExit(main())
