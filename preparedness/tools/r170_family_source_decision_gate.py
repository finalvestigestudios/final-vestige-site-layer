#!/usr/bin/env python3
"""R170: fail-closed, read-only Family Reunification Card source decision docket.

An accessible source page or syntactically valid URL is never approval of a
claim, child-safety instruction, medical advice, product, release, or revenue.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

SCHEMA = 'fv-preparedness-r170-family-source-docket-v1'
HOLD = 'DRAFT_HARD_HOLD'
SOURCE_PATH = 'preparedness/sources/fragments/shelter.json'
SOURCE_BLOB = '2a3f1a7ddeab2782add875be1e0e378513504aa1'
META_PATH = 'preparedness/review/r159/family-reunification-card.meta.json'
META_BLOB = '2bafef03a375b0156e2dcd7f1b913d119becad61'
HTML_PATH = 'preparedness/review/r163/family-reunification-card.body.html'
HTML_BLOB = '1b8a340c69b28280ae485a667da4564d9e849d70'
DOCKET_PATH = 'preparedness/review/r170/source-decision-docket.json'
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
ANY_CITE = re.compile(r'\{\{\s*cite\b[^}]*\}\}', re.I)
ALLOWED_OBSERVATIONS = {'CURRENT_PAGE_TEXT','SCOPE_LIMITED','ACCESS_RESTRICTED','ARCHIVED_UNCONFIRMED','PRIOR_RECORD_UNRECHECKED'}
SPECIAL = {'shelter-ready-tech':'ACCESS_RESTRICTED',
           'shelter-co-oss-reunification':'ACCESS_RESTRICTED',
           'shelter-fema-reunification':'ARCHIVED_UNCONFIRMED',
           'shelter-ncmec-hotline':'SCOPE_LIMITED'}


def must(condition, why):
    if not condition:
        raise ValueError(why)


def fields(obj, keys, name):
    must(type(obj) is dict and set(obj) == keys, name + ' keys drift')
    return obj


def git_blob(data: bytes):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def pinned(root: Path, rel: str, sha: str):
    p = root / rel
    must(p.is_file() and not p.is_symlink(), 'missing/symlink pinned source: ' + rel)
    b = p.read_bytes()
    must(git_blob(b) == sha, 'original evidence drift: ' + rel)
    return b


def url(value):
    must(type(value) is str and len(value) <= 400, 'untrusted URL type/length')
    p = urlsplit(value)
    must(p.scheme == 'https' and bool(p.hostname) and not p.username and
         not p.password and not p.query and not p.fragment and
         not any(c.isspace() for c in value) and chr(92) not in value,
         'untrusted source/evidence URL')
    return value


def evaluate(docket, fragment, meta, html, *, synthetic=True):
    fields(docket, {'schema','state','observed_on','scope','source_fragment_git_blob',
                   'card_meta_git_blob','staged_html_git_blob','decisions',
                   'independent_qd_pass','publication_authorized'}, 'docket')
    must(docket['schema'] == SCHEMA and docket['state'] == HOLD and
         docket['observed_on'] == '2026-11-06' and docket['scope'] == 'family-reunification-card' and
         docket['source_fragment_git_blob'] == SOURCE_BLOB and
         docket['card_meta_git_blob'] == META_BLOB and
         docket['staged_html_git_blob'] == HTML_BLOB and
         docket['independent_qd_pass'] is False and docket['publication_authorized'] is False,
         'false source/release authority or trust anchor')
    must(type(meta) is dict and meta.get('slug') == 'family-reunification-card' and
         meta.get('status',{}).get('publish') == 'draft' and
         meta.get('safety_review',{}).get('state') == 'pending',
         'original card draft/safety identity changed')
    uses = meta.get('source_use')
    must(type(uses) is dict and len(uses) == 11, '11 original interpretations missing')
    must(type(html) is str, 'invalid staged HTML')
    cites = CITE.findall(html)
    must(len(cites) == len(ANY_CITE.findall(html)) == 16 and set(cites) == set(uses),
         'citation occurrence/source-use mismatch')
    must(type(fragment) is dict and type(fragment.get('sources')) is list,
         'source register missing')
    source_entries = fragment['sources']
    ids = [s.get('id') for s in source_entries if type(s) is dict]
    must(len(ids) == len(set(ids)), 'duplicate ID in source register')
    sources = {s['id']:s for s in source_entries if type(s) is dict and 'id' in s}
    decisions = docket['decisions']
    must(type(decisions) is list and len(decisions) == 11, 'must reconcile all 11 source relationships')
    observed_ids = []
    for row in decisions:
        fields(row, {'id','original_url','observation','source_scope','review_state',
                     'human_link_check','qualified_safety_review','alternative_current_page'}, 'decision')
        identifier = row['id']
        must(type(identifier) is str and identifier in uses and identifier in sources,
             'unknown original citation identity')
        observed_ids.append(identifier)
        must(url(row['original_url']) == sources[identifier].get('url'),
             'source-identity substitution: ' + identifier)
        must(type(row['observation']) is str and row['observation'] in ALLOWED_OBSERVATIONS,
             'unfounded observation category')
        if identifier in SPECIAL:
            must(row['observation'] == SPECIAL[identifier],
                 'must preserve unresolved scope/access/archive warning: ' + identifier)
        must(type(row['source_scope']) is str and 24 <= len(row['source_scope']) <= 600 and
             not re.search(r'(?i)\b(qd pass|safe to publish|human approved|medical approval|independently verified)\b',row['source_scope']),
             'missing or overconfident source-scope note')
        must(row['review_state'] == 'PENDING' and row['human_link_check'] is False and
             row['qualified_safety_review'] is False,
             'unapproved reviewer disposition')
        alt = row['alternative_current_page']
        must(alt is None or (url(alt) in {
              'https://www.missingkids.org/contact',
              'https://www.cdc.gov/children-and-school-preparedness/keeping-safe/'}),
              'unauthorized proposed replacement URL')
        must(type(alt) is not bool, 'bad alternative page')
    must(len(set(observed_ids)) == 11 and set(observed_ids) == set(uses),
         'missing or duplicated source decision')
    return {'schema':SCHEMA, 'state':HOLD, 'synthetic_fixture':synthetic,
            'card_source_relationships':11,'card_citation_occurrences':16,
            'still_pending_qualified_human_decisions':11,
            'source_links_human_verified':False,
            'claim_adjudication_complete':False,'independent_qd_pass':False,
            'publication_authorized':False,'commerce_authorized':False}


def authentic(root):
    sys.path.insert(0, str(root/'preparedness'/'tools'))
    r161 = importlib.import_module('r161_body_custody_gate')
    custody = r161.verify(root)
    must(custody['state'] == HOLD and custody['articles'] == 35 and
         custody['citations'] == 2000 and custody['source_uses'] == 385,
         'original integrated corpus custody failed')
    fragment=json.loads(pinned(root,SOURCE_PATH,SOURCE_BLOB))
    meta=json.loads(pinned(root,META_PATH,META_BLOB))
    html=pinned(root,HTML_PATH,HTML_BLOB).decode('utf-8')
    path=root/DOCKET_PATH
    must(path.is_file() and not path.is_symlink(),'docket file missing')
    docket=json.loads(path.read_text(encoding='utf-8'),parse_constant=lambda x: (_ for _ in ()).throw(ValueError('invalid JSON number')))
    return evaluate(docket,fragment,meta,html,synthetic=False)


def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument('--repo',type=Path,default=Path('.'))
    args=parser.parse_args(argv)
    try:
        result=authentic(args.repo.resolve(strict=True))
    except Exception as exc:
        result={'schema':SCHEMA,'state':'INVALID_HARD_HOLD','error_kind':type(exc).__name__,
                'publication_authorized':False,'independent_qd_pass':False}
    print(json.dumps(result,sort_keys=True))
    return 2  # No release authority even when the complete 35-article custody passes.


if __name__=='__main__':
    raise SystemExit(main())
