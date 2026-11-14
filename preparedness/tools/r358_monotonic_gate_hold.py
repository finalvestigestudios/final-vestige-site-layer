#!/usr/bin/env python3
"""R358 Preparedness QA #157 safety-gate monotonicity; read-only HARD HOLD.

Preserves a reviewed safety *restriction*, never grants safety approval. A candidate
integrated taxonomy may add planned tools but cannot drop QA #157 restrictions.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

SCHEMA = 'fv-preparedness-r358-monotonic-safety-gate-v1'
QA_BASE = '10f58fed1ba808056813064ca5f9680589db8da1'
QA_HEAD = '7d1ae6b8ef93d10cfb6810987672360885e9c1aa'
INTEGRATION_BASE = '67dd810bc8498dfd36aa9a346182df1a360bda2d'
BASE_BLOB = 'bd9f8db8821bb0511f3e5b2a75a782373ccf415d'
QA_BLOB = 'd20ff18bc6f243e08796c0505981979a10fca2d9'
INTEGRATION_BLOB = '15c547bb3018ac182b12a51036389cfa39a59168'
ESCALATED = {
    'household-emergency-plan': 1,
    'three-day-kit': 2,
    'go-bags': 16,
    'preparedness-real-households': 20,
}
HOLD = {'may_merge': False, 'may_publish': False, 'qualified_qd_pass': False,
        'source_review_complete': False, 'safety_review_complete': False,
        'native_export_verified': False, 'paid_offer_verified': False}
SLUG = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
STATES = {'not-started', 'drafted-pending-safety-review', 'safety-approved-draft'}


def sha256(raw: str) -> str:
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def git_blob(raw: str) -> str:
    b = raw.encode('utf-8')
    return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()


def parse(raw: str, label: str):
    if not isinstance(raw, str) or len(raw) > 2_000_000:
        raise ValueError(label + ':INVALID_INPUT')
    data = json.loads(raw)
    if not isinstance(data, dict) or data.get('base_path') != '/preparedness/':
        raise ValueError(label + ':INVALID_BASE_PATH')
    sections = data.get('sections')
    articles = data.get('slate')
    tools = data.get('tools')
    if not isinstance(sections, list) or not isinstance(articles, list) or not isinstance(tools, list):
        raise ValueError(label + ':INVALID_COLLECTION')
    if len(sections) != 8 or len(articles) != 35 or not 6 <= len(tools) <= 9:
        raise ValueError(label + ':INVENTORY_DRIFT')
    section_slugs = [v.get('slug') for v in sections if isinstance(v, dict)]
    if len(section_slugs) != 8 or len(set(section_slugs)) != 8 or any(
        not isinstance(s, str) or not SLUG.fullmatch(s) for s in section_slugs):
        raise ValueError(label + ':INVALID_SECTIONS')
    routes = set()
    article_ids, article_numbers, tool_ids = set(), set(), set()
    for kind, rows in (('article', articles), ('tool', tools)):
        for entry in rows:
            if not isinstance(entry, dict):
                raise ValueError(label + ':NONOBJECT_ENTRY')
            slug = entry.get('slug')
            if not isinstance(slug, str) or not SLUG.fullmatch(slug):
                raise ValueError(label + ':UNSAFE_SLUG')
            if entry.get('status') not in STATES:
                raise ValueError(label + ':INVALID_PUBLICATION_STATE')
            if 'gate' in entry and type(entry['gate']) is not bool:
                raise ValueError(label + ':NONBOOLEAN_GATE')
            if kind == 'article':
                number = entry.get('n')
                if type(number) is not int or not 1 <= number <= 35 or number in article_numbers:
                    raise ValueError(label + ':DUPLICATE_OR_INVALID_ARTICLE_NUMBER')
                article_numbers.add(number)
                section = entry.get('section')
                if section not in section_slugs or section == 'field-tools':
                    raise ValueError(label + ':ARTICLE_SECTION_DRIFT')
                if slug in article_ids:
                    raise ValueError(label + ':DUPLICATE_ARTICLE_SLUG')
                article_ids.add(slug)
            else:
                section = 'field-tools'
                if slug in tool_ids:
                    raise ValueError(label + ':DUPLICATE_TOOL_SLUG')
                tool_ids.add(slug)
            route = '/preparedness/' + section + '/' + slug + '/'
            if route in routes:
                raise ValueError(label + ':DUPLICATE_CANONICAL_ROUTE')
            routes.add(route)
    if article_numbers != set(range(1, 36)):
        raise ValueError(label + ':ARTICLE_NUMBER_COVERAGE')
    return data, {r['slug']: r for r in articles}, {r['slug']: r for r in tools}, routes


def adjudicate(qa_before: str, qa_after: str, integrated: str, *,
              require_authentic_pins=False) -> dict:
    """Compare trusted QA before/after and proposed integration; no write or approval.

    `require_authentic_pins` must be True in native mode. Synthetic review is
    explicitly non-native; it cannot certify source identities or release.
    """
    errors = []
    docket = []
    try:
        before, a, at, aroutes = parse(qa_before, 'QA_BASE')
        after, b, bt, broutes = parse(qa_after, 'QA_HEAD')
        proposed, c, ct, croutes = parse(integrated, 'INTEGRATED')
        if require_authentic_pins and (
            git_blob(qa_before) != BASE_BLOB or
            git_blob(qa_after) != QA_BLOB or
            git_blob(integrated) != INTEGRATION_BLOB):
            errors.append('GIT_BLOB_PIN_MISMATCH')
        if set(a) != set(b) or set(a) != set(c):
            errors.append('ARTICLE_IDENTITY_REMOVED_OR_ADDED')
        if aroutes != broutes or not broutes.issubset(croutes):
            errors.append('ARTICLE_ROUTE_DRIFT')
        if not set(bt).issubset(set(ct)) or not set(at).issubset(set(bt)):
            errors.append('PLANNED_TOOL_REMOVED')
        # QA patch must be exactly four restrictions, no silent metadata edits.
        if any(before.get(k) != after.get(k) for k in set(before)|set(after) if k != 'slate'):
            errors.append('QA_NONSLATE_MUTATION')
        if len(before['slate']) != len(after['slate']):
            errors.append('QA_ARTICLE_COUNT_DRIFT')
        for slug in sorted(set(a)|set(b)|set(c)):
            old, new, merged = a.get(slug), b.get(slug), c.get(slug)
            if not old or not new or not merged:
                errors.append('MISSING_ARTICLE:'+slug)
                continue
            if {k:v for k,v in old.items() if k!='gate'} != {k:v for k,v in new.items() if k!='gate'}:
                errors.append('QA_UNEXPECTED_ARTICLE_MUTATION:'+slug)
            if old.get('gate') is True and new.get('gate') is not True:
                errors.append('QA_WEAKENED_EXISTING_GATE:'+slug)
            if slug in ESCALATED:
                if (old.get('n') != ESCALATED[slug] or old.get('gate') is not False
                    or new.get('gate') is not True):
                    errors.append('QA_ESCALATION_UNAUTHENTICATED:'+slug)
            elif old.get('gate') != new.get('gate'):
                errors.append('QA_UNEXPECTED_GATE_CHANGE:'+slug)
            if new.get('gate') is True and merged.get('gate') is not True:
                errors.append('INTEGRATION_GATE_DOWNGRADE:'+slug)
            if any(new.get(k) != merged.get(k) for k in ('n','slug','section','track','title')):
                errors.append('INTEGRATION_ARTICLE_IDENTITY_DRIFT:'+slug)
            # Status drift can be legitimate in contributor streams, but cannot silently count as review.
            if new.get('status') != merged.get('status'):
                docket.append('EDITORIAL_STATUS_REVIEW:'+slug)
        for slug in sorted(set(bt)&set(ct)):
            if bt[slug].get('gate') is True and ct[slug].get('gate') is not True:
                errors.append('INTEGRATION_TOOL_GATE_DOWNGRADE:'+slug)
            if bt[slug].get('title') != ct[slug].get('title'):
                docket.append('TOOL_TITLE_REVIEW:'+slug)
        for slug in sorted(set(ct)-set(bt)):
            docket.append('ADDED_PLANNED_TOOL_REVIEW:'+slug)
    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        errors.append('INVALID_SOURCE_SNAPSHOT:'+str(exc)[:120])
    return dict(schema=SCHEMA,
                status='INVALID_HARD_HOLD' if errors else 'SOURCE_REVIEW_REQUIRED_HARD_HOLD',
                native_pins_checked=bool(require_authentic_pins),
                qa_base=QA_BASE,qa_head=QA_HEAD,integration_base=INTEGRATION_BASE,
                qa_base_sha256=sha256(qa_before) if isinstance(qa_before,str) else None,
                qa_head_sha256=sha256(qa_after) if isinstance(qa_after,str) else None,
                integration_sha256=sha256(integrated) if isinstance(integrated,str) else None,
                escalations_expected=sorted(ESCALATED),
                errors=sorted(set(errors)),review_docket=sorted(set(docket)), **HOLD)


def git_show(repo: Path, ref: str, path='preparedness/taxonomy.json') -> str:
    out = subprocess.run(['git','-C',str(repo),'show',ref+':'+path],
                         capture_output=True,check=False,timeout=20)
    if out.returncode or len(out.stdout) > 2_000_000:
        raise ValueError('GIT_OBJECT_UNAVAILABLE')
    return out.stdout.decode('utf-8','strict')


def native_review(root: Path) -> dict:
    try:
        root = Path(root).resolve(strict=True)
        if not (root/'.git').exists():
            raise ValueError('AUTHENTIC_COMPLETE_CHECKOUT_REQUIRED')
        top = subprocess.run(['git','-C',str(root),'rev-parse','--show-toplevel'],
                             capture_output=True,check=False,timeout=20)
        if top.returncode or Path(top.stdout.decode().strip()).resolve() != root:
            raise ValueError('GIT_ROOT_MISMATCH')
        originals = [git_show(root, ref) for ref in (QA_BASE, QA_HEAD, INTEGRATION_BASE)]
        return adjudicate(*originals,require_authentic_pins=True)
    except (OSError, ValueError, UnicodeError, subprocess.TimeoutExpired) as exc:
        return dict(schema=SCHEMA,status='INVALID_HARD_HOLD',
                    errors=['NATIVE_SOURCE_UNAVAILABLE:'+type(exc).__name__],**HOLD)


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
    args = ap.parse_args()
    print(json.dumps(native_review(args.repo_root),indent=2,sort_keys=True))
    sys.exit(2)  # No reviewer, synthetic fixture or native code path can approve publication.
