#!/usr/bin/env python3
"""R329 read-only *review docket*, not a medical, emergency, privacy, or QD approval.

Detect seven specific claim/source context requirements in exact held Article #15 and
Tool #104. Official URLs are independent-review starting points, not endorsements.
No source, CMS, merchant, queue, or analytics writes are implemented here.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
from preparedness.tools import r319_three_way_custody_hold as custody
from preparedness.tools import r328_article15_tool104_claim_holds as previous

SCHEMA = 'fv-preparedness-r329-cross-agency-service-claim-hold-v1'
# (id, role, exact original anchor, attached original cite id or None, risk, reviewer source)
# Source labels are cited in the original text and are NOT verification of today's service eligibility.
CLAIMS = (
    ('A15-CORDED-SERVICE', 'a_body', 'keep at least one corded telephone that does not depend on electricity',
     'shelter-fcc-comms', 'P0_OUTAGE_PHONE_SERVICE', 'https://www.cpuc.ca.gov/consumer-support/psps/potential-impacts-on-telephone-service-during-de-energization'),
    ('A15-REDCROSS-ARCHIVE', 'a_body', 'Red Cross takes welfare-check requests at 1-800-RED CROSS',
     'shelter-fema-reunification', 'P0_RED_CROSS_ELIGIBILITY', 'https://www.redcross.org/get-help/disaster-relief-and-recovery-services/contact-and-locate-loved-ones.html'),
    ('A15-NCMEC-ORDER', 'a_body', 'If a child is missing after a disaster',
     'shelter-ncmec-hotline', 'P0_MISSING_CHILD_FIRST_REPORT', 'https://us.missingkids.org/gethelpnow/isyourchildmissing'),
    ('T104-NCMEC-ORDER', 't_body', 'If a child is missing after a disaster',
     'shelter-ncmec-hotline', 'P0_MISSING_CHILD_FIRST_REPORT', 'https://us.missingkids.org/gethelpnow/isyourchildmissing'),
    ('A15-SCHOOL-LOCALITY', 'a_body', 'Colorado\'s Office of School Safety describes reunification as "not a normal pick-up"',
     'shelter-co-oss-reunification', 'P0_SCHOOL_LOCAL_POLICY', 'https://www.cdc.gov/children-and-school-preparedness/before-during-after/reunification.html'),
    ('T104-SCHOOL-LOCALITY', 't_body', "Colorado's Office of School Safety, as one state's example",
     'shelter-co-oss-reunification', 'P0_SCHOOL_LOCAL_POLICY', 'https://www.cdc.gov/children-and-school-preparedness/before-during-after/reunification.html'),
    ('A15-RESEARCH-NOT-OPENED', 'a_body', "We did not open the Ready.gov fillable PDF card, the Red Cross's Reconnecting Families program",
     None, 'P0_SOURCE_CUSTODY_GAP', 'https://www.redcross.org/get-help/disaster-relief-and-recovery-services/contact-and-locate-loved-ones.html'),
)
RELEASE = {'public_release_authorized':False, 'medical_or_emergency_safety_approved':False,
           'independent_qd_pass':False, 'privacy_review_complete':False,
           'paid_offer_verified':False, 'merchant_sale_confirmed':False}
BLOCK = re.compile(r'<(?P<tag>p|li)\b[^>]*>.*?</(?P=tag)>', re.I | re.S)
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')


def inspect(docs: dict) -> dict:
    """Classify synthetic or provided bytes; NOT authenticated until audit() pins Git blobs."""
    errors, review, content, metadata = [], [], {}, {}
    if type(docs) is not dict or set(docs) != set(previous.DOCS):
        errors.append('FOUR_REQUIRED_DOCUMENT_ROLES'); docs = {}
    for key in previous.DOCS:
        raw = docs.get(key)
        if type(raw) is not bytes:
            errors.append('MISSING_OR_NONBYTE_' + key.upper())
            continue
        try:
            if key.endswith('meta'):
                metadata[key] = previous.strict_json(raw)
            else:
                content[key] = raw.decode('utf-8', 'strict')
        except (UnicodeError, ValueError, TypeError):
            errors.append('BAD_UTF8_OR_JSON_' + key.upper())
    for role, expect_n, expect_slug in (('a_meta',15,'family-communication-plan'),
                                        ('t_meta',104,'family-reunification-card')):
        data = metadata.get(role)
        if (type(data) is not dict or type(data.get('n')) is not int or data.get('n') != expect_n
                or data.get('slug') != expect_slug or data.get('status') != {'editorial':'drafted','publish':'draft'}
                or type(data.get('safety_review')) is not dict
                or data['safety_review'].get('state') != 'pending'
                or data['safety_review'].get('reviewer') is not None
                or data['safety_review'].get('date') is not None
                or type(data.get('source_use')) is not dict):
            errors.append('UNSAFE_OR_DRIFTED_IDENTITY_' + role.upper())
            continue
        body = content.get('a_body' if role == 'a_meta' else 't_body','')
        declared = set(data['source_use'])
        cited = set(CITE.findall(body))
        if declared != cited or any(type(x) is not str for x in data['source_use'].values()):
            errors.append('CITATION_REGISTRY_DRIFT_' + role.upper())
        if '{{cite:' in body and body.count('{{cite:') != len(CITE.findall(body)):
            errors.append('MALFORMED_CITATION_' + role.upper())
    if len({x[0] for x in CLAIMS}) != len(CLAIMS):
        errors.append('DUPLICATE_CLAIM_ID')
    for ident,role,needle,expected_cite,risk,url in CLAIMS:
        body = content.get(role,'')
        positions = [m.start() for m in re.finditer(re.escape(needle), body)]
        if len(positions) != 1:
            errors.append('ANCHOR_MISSING_OR_DUPLICATED_' + ident)
            continue
        # The original source citation must occur in the SAME rendered <p> or <li>
        # containing the claim; an unrelated later paragraph is not adequate.
        matches = [m for m in BLOCK.finditer(body) if m.start() <= positions[0] < m.end()]
        if len(matches) != 1:
            errors.append('CLAIM_HAS_NO_UNIQUE_BLOCK_' + ident)
            continue
        block = matches[0].group(0)
        block_cites = set(CITE.findall(block))
        if expected_cite is not None:
            if expected_cite not in block_cites:
                errors.append('CITATION_NOT_ADJACENT_' + ident)
            meta = metadata.get('a_meta' if role == 'a_body' else 't_meta')
            if not isinstance(meta,dict) or expected_cite not in (meta.get('source_use') or {}):
                errors.append('SOURCE_USE_NOT_DECLARED_' + ident)
        # Explicitly do not say that citation id, source date, or reviewer URL proves claim support.
        byte_offset = len(body[:positions[0]].encode('utf-8'))
        review.append({'claim_id':ident,'doc':previous.DOCS[role][0],
                       'source_pinned_git_sha':previous.DOCS[role][1],
                       'byte_offset':byte_offset, 'exact_claim_utf8_sha256':hashlib.sha256(needle.encode()).hexdigest(),
                       'attached_original_source_id':expected_cite,
                       'adjacent_original_citation_ids':sorted(block_cites),
                       'risk':risk,'official_human_review_start':url,
                       'current_claim_support_proven':False,
                       'review_status':'UNRESOLVED_QUALIFIED_REVIEW'})
    if len(review) != len(CLAIMS):
        errors.append('REVIEW_WITNESS_COVERAGE_INCOMPLETE')
    return {'schema':SCHEMA,'state':'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
            'errors':sorted(set(errors)),'claim_review_count':len(review),
            'independently_approved_count':0,'claims':review,'release':RELEASE.copy(),
            'source_notes':'Archived FEMA/FCC citations and current agency pages require human claim-level comparison; not service guarantees.'}


def audit(loader) -> dict:
    docs, errors = {}, []
    for key,(path,sha) in previous.DOCS.items():
        try:
            raw = loader(path)
            if type(raw) is not bytes or custody.blob(raw) != sha:
                raise ValueError('Git object drift')
            docs[key] = raw
        except (OSError,ValueError,TypeError):
            errors.append('PINNED_GIT_OBJECT_MISSING_OR_CHANGED_' + key.upper())
    old = previous.inspect(docs)
    report = inspect(docs)
    report['r328_claim_gate_state'] = old['state']
    if old['errors'] or errors:
        report['errors'] = sorted(set(report['errors']+['R328_PREDECESSOR_NOT_CLEAR'] * bool(old['errors'])+errors))
        report['state'] = 'INVALID_HARD_HOLD'
    report['authenticated_git_objects'] = len(docs)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);args=parser.parse_args()
    root = args.root.resolve()
    try:
        manifest_raw = custody.safe_bytes(root,custody.MANIFEST_PATH)
        docket_raw = custody.safe_bytes(root,'preparedness/audits/r320_conflict_adjudication_docket.json')
        if type(manifest_raw) is not bytes or type(docket_raw) is not bytes:
            raise OSError('Missing canonical custody manifest or unresolved conflict docket')
        manifest=previous.strict_json(manifest_raw)
        docket=previous.strict_json(docket_raw)
        if custody.validate_manifest(manifest,root)['errors'] or len(docket.get('records',[])) != 15 or any(
            r.get('status')!='UNRESOLVED_HOLD' or r.get('automatic_selection') is not False for r in docket['records']):
            raise ValueError('R319/R320 complete custody or 15 conflict holds not satisfied')
        out=audit(lambda p: custody.safe_bytes(root,p))
    except (ValueError,TypeError,OSError,UnicodeError,KeyError):
        out={'schema':SCHEMA,'state':'INVALID_HARD_HOLD',
             'errors':['COMPLETE_NATIVE_SOURCE_AND_DOCKET_REQUIRED'],
             'authenticated_git_objects':0,'claims':[],'release':RELEASE.copy()}
    print(json.dumps(out,indent=2,sort_keys=True))
    return 2 if out['state']=='DRAFT_HARD_HOLD' else 1

if __name__=='__main__':
    raise SystemExit(main())
