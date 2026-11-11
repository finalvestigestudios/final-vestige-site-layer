#!/usr/bin/env python3
"""R296 review-only family-reunification source/claim custody gate.

Conservatively checks exact source custody, release holds, and presence of known
high-risk reader-facing claims. It never adjudicates emergency guidance, medical
safety, privacy, browser behavior or revenue. No network and NO WRITE operations.
Exit 2 = expected draft HARD HOLD; exit 1 = corrupt/missing evidence HARD HOLD.
There is deliberately no exit-zero path, and no QD PASS state.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from pathlib import Path

BODY = 'preparedness/content/tools/family-reunification-card.body.html'
META = 'preparedness/content/tools/family-reunification-card.meta.json'
JS = 'preparedness/tools/reunion_card.js'
R200 = 'preparedness/audits/r200_seven_cluster_35_article_frozen_custody.json'
EXPECTED = {
    BODY: 'be8698ac5d020476ff649d85813810e2000c6f98',
    META: '47da1e7e20e39f0ea85e26d54a8d58301f6e0a15',
    JS: 'b1a09b1eda1ae26f081de65b400a37bc19538035',
    R200: '5822f9dfde21d1f3bdfc26658769d852c639438c',
}
ARTICLE15_SLUG = 'family-communication-plan'

SOURCE_REVIEW = (
    {'id':'N911-EMERGENCY-DEFINITION', 'url':'https://www.911.gov/calling-911/',
     'role':'Official emergency = immediate police/fire/ambulance assistance, not just life threatening',
     'review':'human-claim-mapping-required'},
    {'id':'N911-TEXT-LIMITATIONS','url':'https://www.911.gov/calling-911/frequently-asked-questions/',
     'role':'Call 911 if you can; text if unable; text-to-911 varies by area',
     'review':'human-claim-mapping-required'},
    {'id':'CDC-STAY-CONNECTED','url':'https://www.cdc.gov/prepare-your-health/plan-ahead/stay-connected.html',
     'role':'Plan several ways to reach family; texts may get through when calls do not',
     'review':'human-claim-mapping-required'},
)
RISK_RULES = {
    '911-threshold-too-narrow': (r'call\s+911\s+for\s+anything\s+life[-\s]?threatening', 'independent emergency-communications reviewer'),
    'emergency-nonemergency-text-blended': (r'use\s+text\s+messages\s+rather\s+than\s+calls\s+for\s+everything\s+else', 'independent emergency-communications reviewer'),
    'unverified-local-storage-guarantee': (r'it\s+is\s+not\s+sent\s+or\s+saved', 'privacy + runtime/network QA'),
    'unverified-tab-close-guarantee': (r'closing\s+the\s+tab\s+clears\s+it', 'privacy + runtime QA'),
    'unverified-noscript-form-function': (r'form\s+below\s+still\s+works\s+and\s+prints', 'no-JS + print + accessibility QA'),
}


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def text_of(fragment: str) -> str:
    fragment = re.sub(r'(?is)<(script|style)\b[^>]*>.*?</\1\s*>', ' ', fragment)
    fragment = re.sub(r'(?is)<!--.*?-->', ' ', fragment)
    fragment = re.sub(r'(?s)<[^>]*>', ' ', fragment)
    fragment = html.unescape(fragment)
    fragment = re.sub(r'\{\{cite:([\w-]+)\}\}', ' ', fragment)
    return re.sub(r'\s+', ' ', fragment).strip()


def relevant_block(body: str, css_class: str) -> str | None:
    # Source-level HTML reader text only. This does NOT certify CSS/browser visibility.
    # Scan all paragraphs, not only the first one.
    for match in re.finditer(r'(?is)<p\b([^>]*)>(.*?)</p\s*>', body):
        attrs, content = match.groups()
        m = re.search(r'(?is)\bclass\s*=\s*(["\'])(.*?)\1', attrs)
        if m and css_class in m.group(2).split():
            return content
    return None


def _is_false(o, field):
    return o.get(field, False) is False


def examine(files: dict[str, bytes]) -> dict:
    errors, holds, confirmed = [], [], {}
    for path, expected in EXPECTED.items():
        data = files.get(path)
        if not isinstance(data, bytes):
            errors.append('MISSING_AUTHENTIC_WITNESS:' + path)
        elif git_blob(data) != expected:
            errors.append('WITNESS_BLOB_CHANGED_REVIEW_REQUIRED:' + path)
        else:
            confirmed[path] = expected
    # Never parse substituted files as if they were authenticated witnesses.
    if len(confirmed) != len(EXPECTED):
        return _receipt(errors, holds, confirmed, {}, None)
    try:
        meta = json.loads(files[META].decode('utf-8'))
        r200 = json.loads(files[R200].decode('utf-8'))
        body = files[BODY].decode('utf-8')
        files[JS].decode('utf-8')
    except (UnicodeError,ValueError,TypeError) as exc:
        return _receipt(['AUTHENTIC_WITNESS_PARSE_FAILED:' + type(exc).__name__], holds, confirmed, {}, None)
    if meta.get('kind') != 'tool' or meta.get('n') != 104 or meta.get('slug') != 'family-reunification-card':
        errors.append('TOOL104_IDENTITY_DRIFT')
    if meta.get('section') != 'field-tools' or meta.get('status',{}).get('publish') != 'draft':
        errors.append('TOOL104_PUBLICATION_STATE_INVALID')
    safety = meta.get('safety_review',{})
    if safety.get('state') != 'pending' or safety.get('reviewer') is not None or safety.get('date') is not None:
        errors.append('TOOL104_SAFETY_REVIEW_NOT_PENDING')
    for item in (meta,r200):
        if not all(_is_false(item,f) for f in ('publication_authorized','independent_qd_pass','medical_safety_verified','privacy_approved')):
            errors.append('UNAUTHORIZED_RELEASE_OR_SAFETY_FLAG')
    if (r200.get('state'),r200.get('artifact_count'),r200.get('export_target_count_with_six_tools')) != ('DRAFT_HARD_HOLD',35,41):
        errors.append('R200_SLATE_CUSTODY_INVALID')
    a15 = [a for a in r200.get('articles',[]) if a.get('n') == 15]
    if len(a15) != 1 or a15[0].get('slug') != ARTICLE15_SLUG or a15[0].get('route') != '/preparedness/family-communication/family-communication-plan/':
        errors.append('R200_ARTICLE15_CUSTODY_INVALID')
    if not isinstance(meta.get('source_use'),dict) or 'shelter-ready-tech' not in meta['source_use']:
        errors.append('TOOL104_CITED_SOURCE_METADATA_CHANGED')
    act_fragment = relevant_block(body,'pa-act-note')
    if act_fragment is None:
        errors.append('MISSING_ACT_NOTE')
        act_fragment = ''
    note = text_of(act_fragment)
    noscript_match = re.search(r'(?is)<noscript\b[^>]*>(.*?)</noscript\s*>',body)
    if not noscript_match:
        errors.append('MISSING_NOSCRIPT_WITNESS')
    noscript = text_of(noscript_match.group(1)) if noscript_match else ''
    checks = {'911-threshold-too-narrow':note,
              'emergency-nonemergency-text-blended':note,
              'unverified-local-storage-guarantee':note,
              'unverified-tab-close-guarantee':note,
              'unverified-noscript-form-function':noscript}
    hits = {}
    for key,(pattern,owner) in RISK_RULES.items():
        hit = bool(re.search(pattern, checks[key],re.I))
        hits[key] = hit
        if hit: holds.append({'code':key,'owner':owner,'state':'UNREVIEWED'})
        else: errors.append('SOURCE_RISK_WITNESS_NOT_REPRODUCED:'+key)
    marker_ids = sorted(re.findall(r'\{\{cite:([\w-]+)\}\}',act_fragment))
    if marker_ids != ['shelter-ready-tech']:
        errors.append('EMERGENCY_NOTE_SOURCE_ID_DRIFT')
    if not any('nothing is stored' in str(meta.get(k,'')).lower() for k in ('dek','description')):
        errors.append('UNVERIFIED_PRIVACY_METADATA_CLAIM_NOT_REPRODUCED')
    holds.append({'code':'child-data-printed-card-risk','owner':'privacy/accessibility independent QA','state':'UNREVIEWED'})
    holds.append({'code':'citation-support-not-adjudicated','owner':'source and emergency-communications independent QA','state':'UNREVIEWED'})
    return _receipt(errors,holds,confirmed,hits,marker_ids)


def _receipt(errors,holds,confirmed,hits,marker_ids):
    invalid=bool(errors)
    return {
        'schema':'fv-preparedness-r296-tool104-source-claim-risk-gate-v1',
        'state':'INVALID_HARD_HOLD' if invalid else 'DRAFT_HARD_HOLD',
        'mechanical_witness_consistent':not invalid,
        'publication_authorized':False,'independent_qd_pass':False,
        'medical_safety_verified':False,'privacy_approved':False,
        'revenue_verified':False,'paid_offer_approved':False,
        'source_context_is_source_level_not_browser_visibility':True,
        'source_support_reviewer_signoff_required':True,
        'authenticated_git_blobs':confirmed,'emergency_note_citation_ids':marker_ids,
        'detected_known_risks':hits,'hold_reasons':holds,'errors':sorted(set(errors)),
        'official_source_candidates_not_self_approving':list(SOURCE_REVIEW),
    }


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
    args=p.parse_args(argv)
    data={}
    for path in EXPECTED:
        try: data[path]=(args.repo_root/path).read_bytes()
        except OSError: pass
    r=examine(data)
    print(json.dumps(r,indent=2,sort_keys=True))
    return 1 if r['state']=='INVALID_HARD_HOLD' else 2


if __name__=='__main__':
    raise SystemExit(main())
