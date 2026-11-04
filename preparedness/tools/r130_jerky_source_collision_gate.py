#!/usr/bin/env python3
"""Read-only, pinned source-ID retarget collision dossier. NEVER an approval.

Requires a trusted Git clone containing frozen contributor, newer contributor and
candidate commits. Exits nonzero if custody or historical invariants drift.
A successful run still means HOLD_HUMAN_SOURCE_ID_COLLISION, not QD PASS.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import re
import subprocess
import sys
from urllib.parse import urlsplit

REPO_COMMITS = {
    'old': '2acf65ca3efa9b4b5db7976f379b9ea693be43a4',
    'new': '67e116e536c7410bed30f8f3b1bb8c166f3c223d',
    'rc': 'ddb3528ba6494dada1fa1c3a142ce746e3a67706',
}
BASE = 'preparedness/content/articles/'
HIST = 'preparedness/sources/fragments/hist-food.json'
FOOD = 'preparedness/sources/fragments/food.json'
SLUGS = ('pemmican-and-dried-meats', 'pioneer-travel-rations')
OLD = 'hist-food-nchfp-jerky'
NEW = 'nchfp-jerky'
CITE = re.compile(r'\{\{cite:([a-z][a-z0-9-]*)\}\}')
# Independently retrieved through GitHub's exact-ref Contents API (Nov 4, 2026).
PINS = {
    ('old', HIST): 'd10628342fea5f177a8d1be00dd906d0c9c7850e',
    ('new', HIST): 'c1856c998c6c728f0de72221e5654a238df994a9',
    ('rc', HIST): 'd10628342fea5f177a8d1be00dd906d0c9c7850e',
    ('rc', FOOD): 'a1f73c8170932d6b3192e9cd506686d516d23d30',
    ('old', BASE+'pemmican-and-dried-meats.body.html'): '0b3319cc85ea2bc6d069b46d13a40e12ddbd5bc5',
    ('new', BASE+'pemmican-and-dried-meats.body.html'): '1febc8929f8b90c81a3fcef1e46a2811778b7e06',
    ('rc', BASE+'pemmican-and-dried-meats.body.html'): '0b3319cc85ea2bc6d069b46d13a40e12ddbd5bc5',
    ('old', BASE+'pemmican-and-dried-meats.meta.json'): '03d3824e07fe51931671d0ddc7aa8c85eda58435',
    ('new', BASE+'pemmican-and-dried-meats.meta.json'): 'c19f68f2ac0988a8d0959e2d05b8ace8f9511348',
    ('rc', BASE+'pemmican-and-dried-meats.meta.json'): '03d3824e07fe51931671d0ddc7aa8c85eda58435',
    ('old', BASE+'pioneer-travel-rations.body.html'): '058c90b763d8cd6dec0731a7b0a9cee4dd5a57c7',
    ('new', BASE+'pioneer-travel-rations.body.html'): 'a658481d828dc4c5ba85f296adbfbee0514f0611',
    ('rc', BASE+'pioneer-travel-rations.body.html'): '058c90b763d8cd6dec0731a7b0a9cee4dd5a57c7',
    ('old', BASE+'pioneer-travel-rations.meta.json'): '7191acba55d63dc405ad9c2003d66193276da89f',
    ('new', BASE+'pioneer-travel-rations.meta.json'): '521e56a3f18d8b211920529a88a3c3b86eb332d7',
    ('rc', BASE+'pioneer-travel-rations.meta.json'): '7191acba55d63dc405ad9c2003d66193276da89f',
}
class Hold(ValueError):
    pass

def require(condition, code):
    if not condition:
        raise Hold(code)

def blob_hash(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode('ascii')+b'\x00'+raw).hexdigest()

def no_duplicate_keys(pairs):
    d = {}
    for k, v in pairs:
        require(k not in d, 'DUPLICATE_JSON_KEY:'+k)
        d[k] = v
    return d

def parse(raw):
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=no_duplicate_keys)
    except (UnicodeError, json.JSONDecodeError) as e:
        raise Hold('INVALID_JSON') from e

def source_map(fragment):
    require(isinstance(fragment, dict) and isinstance(fragment.get('sources'), list), 'INVALID_SOURCE_FRAGMENT')
    result = {}
    for item in fragment['sources']:
        require(isinstance(item, dict), 'INVALID_SOURCE_ROW')
        sid = item.get('id')
        require(isinstance(sid, str) and re.fullmatch(r'[a-z][a-z0-9-]*', sid), 'INVALID_SOURCE_ID')
        require(sid not in result, 'DUPLICATE_SOURCE_ID:'+sid)
        require(isinstance(item.get('supports'), str) and item['supports'].strip(), 'BLANK_SUPPORTS:'+sid)
        require(isinstance(item.get('notes'), str) and item['notes'].strip(), 'BLANK_NOTES:'+sid)
        result[sid] = item
    return result

def normalized_url(url):
    require(isinstance(url, str), 'INVALID_URL_TYPE')
    p = urlsplit(url)
    require(p.scheme == 'https' and bool(p.netloc) and not p.username and not p.password, 'INSECURE_OR_INVALID_URL')
    require(not p.query and not p.fragment, 'UNEXPECTED_URL_QUERY_OR_FRAGMENT')
    return p.scheme+'://'+p.netloc.lower()+p.path.rstrip('/')

def normalize_line_endings(s):
    return s.replace('\r\n', '\n')

def source_id_counts(body):
    require(isinstance(body,str), 'INVALID_BODY')
    require(body.count('{{cite:') == len(CITE.findall(body)), 'MALFORMED_CITATION')
    return Counter(CITE.findall(body))

def inspect(data):
    """Pure fail-closed audit. Expects decoded snapshots; works with synthetic tests."""
    require(set(data)=={'old','new','rc'}, 'INCOMPLETE_SNAPSHOT_ROSTER')
    for version in data:
        need={'hist'}|{s+'_body' for s in SLUGS}|{s+'_meta' for s in SLUGS}
        if version=='rc': need.add('food')
        require(set(data[version])==need, 'INCOMPLETE_SNAPSHOT:'+version)
    old, new, rc = (data[x] for x in ('old','new','rc'))
    a,b,c,food = (source_map(old['hist']),source_map(new['hist']),source_map(rc['hist']),source_map(rc['food']))
    require(a==c, 'RC_HIST_SOURCE_NOT_FROZEN')
    require(OLD in a and NEW not in a, 'OLD_SOURCE_ID_IDENTITY')
    require(NEW in b and OLD not in b, 'NEW_SOURCE_ID_IDENTITY')
    require(NEW in food, 'SHARED_FOOD_SOURCE_NOT_FOUND')
    unchanged_old={k:v for k,v in a.items() if k!=OLD}
    unchanged_new={k:v for k,v in b.items() if k!=NEW}
    require(unchanged_old==unchanged_new, 'UNRELATED_SOURCE_REGISTER_CHANGED')
    prev, successor, shared = a[OLD], b[NEW], food[NEW]
    require(normalized_url(prev.get('url'))==normalized_url(successor.get('url'))
            ==normalized_url(shared.get('url')), 'DIFFERENT_SOURCE_URLS')
    require(prev['supports']==successor['supports'], 'HIST_SOURCE_SCOPE_CHANGED')
    require(prev.get('verified_on')==successor.get('verified_on'), 'SOURCE_VERIFICATION_DATE_CHANGED')
    require(prev.get('human_link_check') is False and successor.get('human_link_check') is False
            and shared.get('human_link_check') is False, 'HUMAN_LINK_APPROVAL_UNEXPECTED')
    require(bool(prev.get('verified_on')) and bool(shared.get('verified_on')), 'SOURCE_UNVERIFIED')
    counts = {}
    for slug, expected in zip(SLUGS, (7,1)):
        body_key, meta_key = slug+'_body', slug+'_meta'
        old_body, new_body, rc_body = [normalize_line_endings(x[body_key]) for x in (old,new,rc)]
        require(old_body==rc_body, 'RC_BODY_NOT_FROZEN:'+slug)
        o_count,n_count,r_count = [source_id_counts(x) for x in (old_body,new_body,rc_body)]
        require(o_count[OLD]==expected and o_count[NEW]==0, 'OLD_CITATION_COUNT:'+slug)
        require(n_count[NEW]==expected and n_count[OLD]==0, 'NEW_CITATION_COUNT:'+slug)
        require(r_count==o_count, 'RC_CITATION_DRIFT:'+slug)
        require(sum(o_count.values())==sum(n_count.values()), 'CITATION_CENSUS_DRIFT:'+slug)
        require(old_body.replace('{{cite:'+OLD+'}}','{{cite:'+NEW+'}}')==new_body,
                'NON_RETARGET_ARTICLE_CONTENT_CHANGE:'+slug)
        old_meta,new_meta,rc_meta = [x[meta_key] for x in (old,new,rc)]
        require(old_meta==rc_meta, 'RC_METADATA_NOT_FROZEN:'+slug)
        for item in (old_meta,new_meta,rc_meta):
            require(isinstance(item,dict) and item.get('slug')==slug, 'SLUG_CHANGED:'+slug)
            require(item.get('status',{}).get('publish')=='draft', 'PUBLISH_STATE_CHANGED:'+slug)
            safety=item.get('safety_review',{})
            require(isinstance(safety,dict) and safety.get('state')=='pending', 'SAFETY_GATE_CHANGED:'+slug)
            notes=item.get('source_use')
            require(isinstance(notes,dict) and bool(notes) and all(isinstance(v,str) and v.strip() for v in notes.values()),
                    'AUTHOR_SOURCE_SCOPE_MISSING:'+slug)
            require(set(source_id_counts({'old':old_body,'new':new_body,'rc':rc_body}[
                'new' if item is new_meta else 'old'])) <= set(notes), 'UNEXPLAINED_CITATION:'+slug)
        require(OLD in old_meta['source_use'] and NEW not in old_meta['source_use'],
                'OLD_AUTHOR_SCOPE_KEY:'+slug)
        require(NEW in new_meta['source_use'] and OLD not in new_meta['source_use'],
                'NEW_AUTHOR_SCOPE_KEY:'+slug)
        shifted=dict(old_meta['source_use']);shifted[NEW]=shifted.pop(OLD)
        comparable=dict(old_meta);comparable['source_use']=shifted
        require(comparable==new_meta, 'NON_RETARGET_METADATA_CHANGE:'+slug)
        counts[slug]={'old_id_citations':o_count[OLD], 'new_id_citations':n_count[NEW],
                      'all_citations':sum(o_count.values()),'content_except_id_unchanged':True,
                      'review_state':'OPEN_HUMAN_ADJUDICATION'}
    return {'status':'HOLD_HUMAN_SOURCE_ID_COLLISION', 'may_merge':False,
            'may_publish':False,'independent_QD_PASS':False,'medical_safety_verified':False,
            'source_collision':{'id':NEW,'fragments':['food.json','hist-food.json (proposed newer contributor)'],
                'same_url_after_trailing_slash_normalization':True,
                'identical_supports':successor['supports']==shared['supports'],
                'identical_notes':successor['notes']==shared['notes'],
                'source_interpretations_require_human_review':True,
                'hist_old_url':prev['url'],'hist_new_url':successor['url'],'shared_food_url':shared['url']},
            'articles':counts,'citation_retarget_occurrences':sum(c['old_id_citations'] for c in counts.values()),
            'warning':'Structural retarget isolation is not evidence of scientific validity, safety, editorial or commercial approval.'}

def git_reader(repo):
    def read(commit, path):
        try:
            return subprocess.check_output(['git','-C',str(repo),'show',commit+':'+path],stderr=subprocess.DEVNULL)
        except (OSError,subprocess.CalledProcessError) as e:
            raise Hold('GIT_OBJECT_UNAVAILABLE:'+commit[:12]+':'+path) from e
    return read

def audit(reader):
    require(len(PINS)==16, 'INCOMPLETE_GIT_CUSTODY_INVENTORY')
    snapshots={'old':{},'new':{},'rc':{}}
    for (version,path), expected in PINS.items():
        raw=reader(REPO_COMMITS[version],path)
        require(isinstance(raw,bytes) and blob_hash(raw)==expected,
                'GIT_BLOB_IDENTITY_CHANGED:'+version+':'+path)
        key = ('hist' if path==HIST else 'food' if path==FOOD else
               path[len(BASE):].replace('.body.html','_body').replace('.meta.json','_meta'))
        snapshots[version][key]=raw.decode('utf-8') if key.endswith('_body') else parse(raw)
    result=inspect(snapshots)
    result['pinned_commits']=REPO_COMMITS
    result['verified_git_blobs']=len(PINS)
    return result

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository',required=True,help='Trusted full Git clone containing historical commits')
    args=p.parse_args(argv)
    try:
        result=audit(git_reader(args.repository))
        print(json.dumps(result,sort_keys=True,indent=2))
        return 0  # A generated HOLD dossier is successful; it never means release approved.
    except (Hold,OSError,UnicodeError,TypeError,KeyError,AttributeError) as e:
        print('BLOCKED: '+str(e),file=sys.stderr)
        return 2

if __name__=='__main__':
    raise SystemExit(main())
