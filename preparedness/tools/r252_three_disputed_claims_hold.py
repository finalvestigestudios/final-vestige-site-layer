#!/usr/bin/env python3
"""R252: exact-source, three-occurrence editorial adjudication preflight.

Read-only. Authenticated presence of a cited source is NOT support for a claim.
Never converts pending human review into QD, health, publication or sales approval.
Operate on integrated draft snapshots only; do not alter author source files.
"""
from __future__ import annotations

from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path
import re

SCHEMA = 'fv-preparedness-r252-three-held-occurrence-review-v1'
STATE = 'DRAFT_HARD_HOLD'
DOCKET_BLOB = 'e3aca0a67d0cbbddb9a2bd84c591687d868d7392'  # Immutable editorial observations, no silent change
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
HEX40 = re.compile(r'[a-f0-9]{40}\Z')
START = 'homemade-water-filters'
HOUSE = 'preparedness-real-households'
# Blob identity differs for #20 because its integrated draft is a documented
# downstream amendment; neither Git identity establishes claim-level approval.
INPUTS = {
    START: {
        'n': 7, 'id': 'cdc-find-clean-water',
        'allowed_body_oids': ('67aa44e9a332f57fb70298a3867410d8f66c8c15',),
        'count': 2,
        'lead_ins': ('Look for other clean water in the house',
                     'Stop and ask what might be upstream.'),
    },
    HOUSE: {
        'n': 20, 'id': 'start-ready-plan',
        'allowed_body_oids': ('70d03c366e10db623929f118501becfa26c48bab',
                              '68344cf6c4022285fffb2a01f42027bf6f9ee95d'),
        'count': 1,
        'lead_ins': ('Ready.gov asks you to consider languages spoken in the household',),
    },
}
SOURCE_URLS = {
    'cdc-find-clean-water': 'https://www.cdc.gov/water-emergency/about/how-to-find-clean-water-in-an-emergency.html',
    'start-ready-plan': 'https://www.ready.gov/plan',
}
REQUIRED_REVIEW_TOPICS = (
    'tap-water heater versus household heating system and ice contamination',
    'microbial sewage/waste versus fuel or toxic chemical contamination',
    'Ready.gov language planning claim independently inaccessible on this run',
)
FALSE_FLAGS = ('human_claim_approved', 'human_source_approved', 'medical_safety_verified',
               'independent_qd_pass', 'commerce_approved', 'publication_authorized')


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def reject_duplicate_keys(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError('R252 HARD HOLD: duplicate JSON field ' + name)
        result[name] = value
    return result


def strict_json(raw: bytes):
    value = json.loads(raw.decode('utf-8', 'strict'), object_pairs_hook=reject_duplicate_keys,
                       parse_constant=lambda x: (_ for _ in ()).throw(ValueError('R252 nonfinite JSON ' + x)))
    if type(value) is not dict:
        raise ValueError('R252 HARD HOLD: nonobject evidence')
    return value


def safe_read(root: Path, relative: str) -> bytes:
    if not isinstance(relative, str) or not relative or relative.startswith('/') or '\\' in relative:
        raise ValueError('R252 HARD HOLD: unsafe path')
    path = root
    for segment in relative.split('/'):
        if segment in ('', '.', '..') or path.is_symlink():
            raise ValueError('R252 HARD HOLD: symlink or path traversal')
        path = path / segment
    if path.is_symlink() or not path.is_file():
        raise ValueError('R252 HARD HOLD: missing/symlinked input')
    return path.read_bytes()


def verify_docket(docket: dict) -> tuple:
    if type(docket) is not dict or docket.get('schema') != SCHEMA or docket.get('state') != STATE:
        raise ValueError('R252 HARD HOLD: invalid evidence schema or state')
    if docket.get('issue') != 136 or docket.get('conversion_issue') != 820:
        raise ValueError('R252 HARD HOLD: incorrect coordination scope')
    if docket.get('historical_shared_source_groups_still_unreviewed') != 32:
        raise ValueError('R252 HARD HOLD: silent shared-source approval')
    if docket.get('ready_gov_access') != 'HTTP_403_UNVERIFIED':
        raise ValueError('R252 HARD HOLD: unsupported Ready.gov verification claim')
    for f in FALSE_FLAGS:
        if docket.get(f) is not False:
            raise ValueError('R252 HARD HOLD: missing false approval flag: ' + f)
    rows = docket.get('occurrences')
    if type(rows) is not list or len(rows) != 3:
        raise ValueError('R252 HARD HOLD: three held occurrences required')
    keys = []
    for i, row in enumerate(rows):
        if type(row) is not dict:
            raise ValueError('R252 HARD HOLD: evidence row must be object')
        slug = row.get('article_slug')
        if slug not in INPUTS:
            raise ValueError('R252 HARD HOLD: unknown article')
        rule = INPUTS[slug]
        if type(row.get('occurrence')) is not int or row['occurrence'] not in range(1,rule['count']+1):
            raise ValueError('R252 HARD HOLD: bad occurrence ordinal')
        ordinal = row['occurrence']
        if row.get('n') != rule['n'] or row.get('citation_id') != rule['id']:
            raise ValueError('R252 HARD HOLD: citation/claim origin mismatch')
        if row.get('source_url') != SOURCE_URLS[rule['id']]:
            raise ValueError('R252 HARD HOLD: source URL changed')
        if row.get('lead_in') != rule['lead_ins'][ordinal-1] or row.get('review_topic') != REQUIRED_REVIEW_TOPICS[i]:
            raise ValueError('R252 HARD HOLD: review question changed')
        if (row.get('claim_verdict') != 'NOT_ADJUDICATED' or
                row.get('source_scope_verdict') != 'NOT_APPROVED' or
                row.get('human_review_required') is not True):
            raise ValueError('R252 HARD HOLD: unsanctioned claim approval')
        keys.append((slug, ordinal))
    if keys != [(START,1), (START,2), (HOUSE,1)]:
        raise ValueError('R252 HARD HOLD: origin/ordinal/order mismatch')
    return rows


def audit_bytes(blobs: dict[str, bytes], docket: dict, *, allowed_oids=None):
    """Refuse claim/URL/count drift. Test override is used only by in-memory unit tests;
    CLI always authenticates against production-frozen literal Git identities.
    """
    rows = verify_docket(docket)
    if type(blobs) is not dict or set(blobs) != set(INPUTS):
        raise ValueError('R252 HARD HOLD: exact article pair required')
    observations = []
    for slug, rule in INPUTS.items():
        raw = blobs[slug]
        if type(raw) is not bytes:
            raise ValueError('R252 HARD HOLD: nonbytes manuscript')
        blob = git_blob(raw)
        allowed = rule['allowed_body_oids'] if allowed_oids is None else allowed_oids.get(slug, ())
        if not allowed or blob not in allowed or not all(HEX40.fullmatch(v) for v in allowed):
            raise ValueError('R252 HARD HOLD: authored/integrated Git blob drift: ' + slug)
        content = raw.decode('utf-8', 'strict')
        marker = '{{cite:' + rule['id'] + '}}'
        positions = [m.start() for m in re.finditer(re.escape(marker), content)]
        if len(positions) != rule['count']:
            raise ValueError('R252 HARD HOLD: disputed citation count differs: ' + slug)
        for ordinal, (pos, lead) in enumerate(zip(positions, rule['lead_ins']), 1):
            # At most one cited claim per list item and no match inside attributes:
            # this is a frozen-blob contextual custody check, not HTML sanitization.
            beginning = content.rfind('<li', 0, pos)
            ending = content.find('</li>', pos)
            if beginning < 0 or ending < 0 or content.find('>', beginning, pos) < 0:
                raise ValueError('R252 HARD HOLD: claim context not a list item')
            clause = content[beginning:ending+5]
            if lead not in clause or clause.count(marker) != 1:
                raise ValueError('R252 HARD HOLD: displaced disputed claim: ' + slug)
            # If another <li> begins within this clause, source may be moved.
            if content.find('<li', beginning+3, pos) != -1:
                raise ValueError('R252 HARD HOLD: ambiguous nested list item')
            row = rows[0 if slug == START and ordinal==1 else 1 if slug==START else 2]
            observations.append({'n':rule['n'],'article_slug':slug,
                                 'citation_id':rule['id'], 'occurrence':ordinal,
                                 'body_git_blob':blob,'source_url':row['source_url'],
                                 'claim_fragment_sha256':hashlib.sha256(clause.encode()).hexdigest(),
                                 'claim_verdict':'NOT_ADJUDICATED','human_review_required':True})
    receipt = {'schema':SCHEMA,'state':STATE,'issue':136,'conversion_issue':820,
               'occurrences':observations,'observed_count':3,
               'shared_source_groups_still_unreviewed':32,
               'ready_gov_page_verified':False,
               'human_claim_approved':False,'human_source_approved':False,
               'medical_safety_verified':False,'independent_qd_pass':False,
               'commerce_approved':False,'publication_authorized':False}
    payload = json.dumps(receipt,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
    receipt['receipt_sha256']=hashlib.sha256(payload).hexdigest()
    return receipt


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',required=True,help='Preparedness folder in exact integration checkout')
    parser.add_argument('--docket',default='audits/r252_three_disputed_claims_hard_hold.json')
    args=parser.parse_args(argv)
    root=Path(args.root)
    docket_raw=safe_read(root,args.docket)
    if git_blob(docket_raw) != DOCKET_BLOB:
        raise ValueError('R252 HARD HOLD: review docket Git blob changed')
    docket=strict_json(docket_raw)
    blobs={slug:safe_read(root,f'content/articles/{slug}.body.html') for slug in INPUTS}
    print(json.dumps(audit_bytes(blobs,docket),indent=2,sort_keys=True))


if __name__=='__main__':
    main()
