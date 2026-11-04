#!/usr/bin/env python3
"""R129: immutable three-way contributor drift worklist; NEVER a release/safety approval.

Run from a trusted full Git checkout containing frozen and current contributor commits.
No network, modifications, publishing, PR merge, or CMS operations are performed.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

CANDIDATE = 'ddb3528ba6494dada1fa1c3a142ce746e3a67706'
# Each tuple is (old integrated-evidence commit, observed 2026-11-04 current commit, branch).
BRANCHES = {
 'start': ('2122d856fce9f64887c16df3d52e64be9f59a55b','2122d856fce9f64887c16df3d52e64be9f59a55b','claude/prep-start-bbfeb8'),
 'shelter': ('5daeaf2dd5ab71806a6b73c91edfb1d8df5da976','5daeaf2dd5ab71806a6b73c91edfb1d8df5da976','claude/prep-shelter-5e1e0e'),
 'food': ('e9cd7766dac59d47ab467d8945269b9146c2aef5','f911ff7a655de8d81535ea86ec3d65a49ee76648','claude/prep-food-ccdc55'),
 'health': ('d2212d0ca0750817d3929865d3069835980faf20','d5ef5bafd68361434dd1cc9209915b8e8a4eaf17','claude/prep-health-837444'),
 'hist-food': ('2acf65ca3efa9b4b5db7976f379b9ea693be43a4','67e116e536c7410bed30f8f3b1bb8c166f3c223d','claude/prep-hist-food-b81f19'),
 'hist-home': ('f654e600f89c321a480dd8f055be4d13d0673490','7504a5f099594d635e3dd7332a33a2e1346c43a2','claude/prep-hist-home-0e0e38'),
 'hist-field': ('a5ce8a62f168db05c95232e3eb385dccd0d19e7f','4e5caf812727953aa45e3bda2d382f2c67b6a09c','claude/prep-hist-field-9db767'),
}
# Actual compare-commits file lists against old head; no inferred files or synthetic branch heads.
DIFF_PATHS = {
 'start': [], 'shelter': [],
 'food': ['preparedness/docs/CLUSTER-food.md','preparedness/tests/test_preparedness.py'],
 'health': ['preparedness/docs/CLUSTER-health.md'],
 'hist-food': ['preparedness/content/articles/pemmican-and-dried-meats.body.html','preparedness/content/articles/pemmican-and-dried-meats.meta.json',
               'preparedness/content/articles/pioneer-travel-rations.body.html','preparedness/content/articles/pioneer-travel-rations.meta.json',
               'preparedness/docs/CLUSTER-hist-food.md','preparedness/sources/fragments/hist-food.json','preparedness/tests/test_preparedness.py'],
 'hist-home': ['preparedness/content/articles/pickling-fermentation-old-recipes.body.html','preparedness/content/articles/pickling-fermentation-old-recipes.meta.json',
               'preparedness/content/articles/root-cellars-cool-storage.body.html','preparedness/content/articles/root-cellars-cool-storage.meta.json',
               'preparedness/content/articles/sanitation-before-germ-theory.body.html','preparedness/content/articles/sanitation-before-germ-theory.meta.json',
               'preparedness/docs/CLUSTER-hist-home.md','preparedness/sources/fragments/hist-home.json'],
 'hist-field': ['preparedness/content/articles/navigation-before-gps.body.html',
                'preparedness/content/articles/pioneer-supply-chains-failed.body.html','preparedness/content/articles/pioneer-supply-chains-failed.meta.json',
                'preparedness/docs/CLUSTER-hist-field.md','preparedness/sources/fragments/hist-field.json'],
}
CITE = re.compile(rb'\{\{cite:([a-z][a-z0-9-]*)\}\}')
BAD_CITE = re.compile(rb'\{\{cite:')
SLUG = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
SHA = re.compile(r'^[0-9a-f]{40}$')
class Hold(ValueError): pass

def need(ok, reason):
    if not ok: raise Hold(reason)

def pairs_no_duplicates(items):
    data={}
    for k,v in items:
        need(k not in data,'DUPLICATE_JSON_KEY:'+k)
        data[k]=v
    return data

def parse_json(raw):
    try:return json.loads(raw.decode('utf-8'),object_pairs_hook=pairs_no_duplicates)
    except (UnicodeError,TypeError,json.JSONDecodeError) as e:raise Hold('CORRUPT_JSON') from e

def blob_sha(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode('ascii')+b'\0'+data).hexdigest()

def classify(path):
    if path.startswith('preparedness/content/articles/'):
        if path.endswith('.body.html'):return 'article_body'
        if path.endswith('.meta.json'):return 'article_metadata'
    if path.startswith('preparedness/sources/') and path.endswith('.json'):return 'source_register'
    if path.startswith('preparedness/tests/'):return 'test'
    if path.startswith('preparedness/docs/'):return 'documentation'
    raise Hold('UNEXPECTED_CHANGED_PATH:'+path)

def source_record(raw):
    d=parse_json(raw)
    need(isinstance(d,dict) and isinstance(d.get('sources'),list),'SOURCE_REGISTER_SHAPE')
    sources=d['sources'];ids={}
    for item in sources:
        need(isinstance(item,dict) and isinstance(item.get('id'),str) and isinstance(item.get('url'),str),'INVALID_SOURCE_ROW')
        sid=item['id'];url=item['url']
        need(sid not in ids,'DUPLICATE_SOURCE_ID_IN_FILE:'+sid)
        need(url.startswith('https://') or url.startswith('http://'),'INVALID_SOURCE_URL:'+sid)
        ids[sid]={'url':url,'supports':item.get('supports'),'notes':item.get('notes'),
                  'verified_on':item.get('verified_on'),'human_link_check':item.get('human_link_check')}
    return ids

def describe(raw, kind):
    if raw is None:return {'exists':False}
    data={'exists':True,'git_blob_sha':blob_sha(raw),'bytes':len(raw)}
    if kind=='article_body':
        need(raw.count(b'{{cite:')==len(CITE.findall(raw)),'MALFORMED_CITATION_IN_BODY')
        tokens=[x.decode('ascii') for x in CITE.findall(raw)]
        need(bool(tokens),'CITATIONS_MISSING')
        text=re.sub(rb'<[^>]*>',b' ',raw)
        text=CITE.sub(b'',text)
        data.update(citation_occurrences=len(tokens),unique_citation_ids=sorted(set(tokens)),
                    approximate_words=len(text.split()))
    elif kind=='article_metadata':
        m=parse_json(raw)
        need(isinstance(m,dict),'INVALID_META')
        notes=m.get('source_use')
        need(isinstance(notes,dict) and bool(notes),'EMPTY_AUTHOR_SOURCE_USE')
        need(all(isinstance(k,str) and isinstance(v,str) and bool(v.strip()) for k,v in notes.items()),'BLANK_AUTHOR_SOURCE_USE')
        state=m.get('safety_review',{})
        need(isinstance(state,dict) and state.get('state') in ('pending','approved','not-required'),'SAFETY_REVIEW_STATE_INVALID')
        need(m.get('status',{}).get('publish')=='draft','PUBLISH_STATUS_NOT_DRAFT')
        data.update(slug=m.get('slug'),publish_state='draft',
                    safety_state=state['state'],author_source_use=notes)
    elif kind=='source_register':
        ids=source_record(raw)
        data.update(source_rows=len(ids),sources=ids)
    return data

def compare_three_way(path,old_blob,new_blob,rc_blob):
    kind=classify(path)
    old,new,rc=[describe(blob,kind) for blob in (old_blob,new_blob,rc_blob)]
    # Fail if historical or new blobs disappear unexpectedly; never silently infer a deletion.
    need(old['exists'] and new['exists'] and rc['exists'],'MISSING_PROTECTED_PATH:'+path)
    if rc_blob==new_blob:relation='CANDIDATE_MATCHES_NEW_HEAD'
    elif rc_blob==old_blob:relation='CANDIDATE_MATCHES_OLD_HEAD'
    else:relation='CANDIDATE_IS_THIRD_VERSION'
    out={'path':path,'kind':kind,'comparison':relation,'review_state':'OPEN_HUMAN_ADJUDICATION',
         'old':old,'new':new,'rc':rc}
    if kind=='article_body':
        old_ids,new_ids=set(old['unique_citation_ids']),set(new['unique_citation_ids'])
        out.update(approx_word_delta=new['approximate_words']-old['approximate_words'],
                   citation_delta=new['citation_occurrences']-old['citation_occurrences'],
                   removed_citation_ids=sorted(old_ids-new_ids),added_citation_ids=sorted(new_ids-old_ids))
    if kind=='article_metadata':
        need(new['slug']==old['slug']==rc['slug'],'ARTICLE_SLUG_DRIFT')
        old_notes,new_notes=old['author_source_use'],new['author_source_use']
        out.update(added_source_explanations=sorted(set(new_notes)-set(old_notes)),
                   removed_source_explanations=sorted(set(old_notes)-set(new_notes)),
                   changed_source_explanations=sorted(k for k in set(old_notes)&set(new_notes) if old_notes[k]!=new_notes[k]),
                   changed_safety_state=old['safety_state']!=new['safety_state'])
        # An existing 'approved' source state does NOT authorize new branch text.
        if new['safety_state']!=old['safety_state']:
            out['review_state']='BLOCKED_SAFETY_STATE_TRANSITION'
    if kind=='source_register':
        o,n=old['sources'],new['sources'];common=set(o)&set(n)
        out.update(added_source_ids=sorted(set(n)-set(o)),removed_source_ids=sorted(set(o)-set(n)),
                   source_url_changes=sorted(k for k in common if o[k]['url']!=n[k]['url']),
                   interpretation_changes=sorted(k for k in common if any(o[k][f]!=n[k][f] for f in ('supports','notes','verified_on','human_link_check'))))
    return out

def validate_header(frozen,heads,candidate,paths):
    need(candidate==CANDIDATE,'CANDIDATE_SHA_DRIFT')
    need(set(frozen)==set(BRANCHES)==set(heads)==set(DIFF_PATHS),'INCOMPLETE_CLUSTER_ROSTER')
    need(set(paths)==set(DIFF_PATHS),'INCOMPLETE_CHANGED_PATHS')
    for k,(old,new,branch) in BRANCHES.items():
        need(frozen[k]==old and heads[k]==new,'BRANCH_HEAD_DRIFT:'+k)
        need(SHA.fullmatch(old) and SHA.fullmatch(new),'INVALID_PINNED_SHA')
        need(len(paths[k])==len(set(paths[k])),'DUPLICATE_CHANGED_PATH:'+k)
        need(paths[k]==DIFF_PATHS[k],'CHANGED_PATH_INVENTORY_DRIFT:'+k)
        need(all(classify(p) for p in paths[k]),'INVALID_CHANGED_PATH:'+k)

def make_docket(reader,*,frozen=None,heads=None,candidate=CANDIDATE,paths=None):
    frozen=frozen if frozen is not None else {k:v[0] for k,v in BRANCHES.items()}
    heads=heads if heads is not None else {k:v[1] for k,v in BRANCHES.items()}
    paths=paths if paths is not None else DIFF_PATHS
    validate_header(frozen,heads,candidate,paths)
    rows=[]
    for cluster,(old,new,branch) in BRANCHES.items():
        for path in paths[cluster]:
            blobs=[]
            for commit in (old,new,candidate):
                try:blobs.append(reader(commit,path))
                except (OSError,subprocess.CalledProcessError) as e:raise Hold('GIT_OBJECT_UNAVAILABLE:'+path) from e
            record=compare_three_way(path,*blobs)
            rows.append({'cluster':cluster,'old_sha':old,'new_sha':new,'branch_name':branch,**record})
    return {'release_state':'DRAFT_HOLD','may_merge':False,'may_publish':False,'independent_QD_PASS':False,
            'medical_safety_verified':False,'commercial_conversion_verified':False,
            'candidate_commit':CANDIDATE,'branch_frozen_and_current':BRANCHES,
            'changed_path_observations':len(rows),'distinct_paths':len({r['path'] for r in rows}),
            'outstanding_review_paths':len(rows),'rows':rows,
            'warning':'Git-object custody and citation counts are structural signals; they never verify a source reading, emergency advice, product sale or QD approval.'}

def git_reader(repo):
    repo=Path(repo)
    def read(commit,path):
        return subprocess.check_output(['git','-C',str(repo),'show',f'{commit}:{path}'],stderr=subprocess.DEVNULL)
    return read

def verify_refs(repo):
    for cluster,(old,new,branch) in BRANCHES.items():
        try:
            actual=subprocess.check_output(['git','-C',str(repo),'rev-parse',f'refs/heads/{branch}'],
                                           text=True,stderr=subprocess.DEVNULL).strip()
        except (OSError,subprocess.CalledProcessError) as e:raise Hold('BRANCH_REFERENCE_UNAVAILABLE:'+cluster) from e
        need(actual==new,'LIVE_BRANCH_HEAD_CHANGED:'+cluster)
    # No need to demand a clean working tree: this reads exact immutable Git objects only.

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository',type=Path,required=True)
    p.add_argument('--check-current-branch-refs',action='store_true')
    args=p.parse_args(argv)
    try:
        if args.check_current_branch_refs:verify_refs(args.repository)
        result=make_docket(git_reader(args.repository))
        print(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False))
        return 0
    except (Hold,OSError,ValueError,TypeError,UnicodeError) as e:
        print('HOLD: '+str(e),file=sys.stderr)
        return 2
if __name__=='__main__':raise SystemExit(main())
