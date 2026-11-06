#!/usr/bin/env python3
"""R159 review-only custody for a proposed, unpublished Family Card correction.

Never publishes, writes CMS or approves a source/safety claim. CLI exits 2.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path

R158 = 'preparedness/tools/r158_family_card_candidate.py'
R158_BLOB = '2efbf2d20ed0c5f31b1e00db949a1b3ebf33ab1f'
MANIFEST = 'preparedness/docs/r151/contributor-three-way.json'
MANIFEST_BLOB = '9cf386519eda970209ff6be4ff0243661cd9d996'
ORIG_BODY = 'preparedness/content/tools/family-reunification-card.body.html'
ORIG_META = 'preparedness/content/tools/family-reunification-card.meta.json'
CAND_BODY = 'preparedness/review/r159/family-reunification-card.body.html'
CAND_META = 'preparedness/review/r159/family-reunification-card.meta.json'
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
WORD = re.compile(r'[A-Za-z0-9_’\-]+')


def require(ok, why):
    if not ok:
        raise ValueError(why)


def git_blob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\x00' + raw).hexdigest()


def source(root, path, expected_blob=None):
    p = root / path
    require(p.is_file() and not p.is_symlink(), 'missing or symlink: ' + path)
    raw = p.read_bytes()
    if expected_blob is not None:
        require(git_blob(raw) == expected_blob, 'Git blob identity mismatch: ' + path)
    return raw


def validate_pair(orig_html, orig_meta, expected_html, expected_meta, candidate_html, candidate_meta):
    """Byte equality is mandatory; approvals cannot be earned by a valid diff."""
    require(candidate_html == expected_html, 'staged HTML deviates from pinned correction')
    require(candidate_meta == expected_meta, 'staged metadata deviates from pinned correction')
    before = json.loads(orig_meta)
    after = json.loads(candidate_meta)
    require(before['slug'] == after['slug'] == 'family-reunification-card', 'slug drift')
    require(before['status']['publish'] == after['status']['publish'] == 'draft', 'publish state drift')
    require(before['safety_review']['state'] == after['safety_review']['state'] == 'pending', 'safety state drift')
    require(before['source_use'] == after['source_use'] and len(after['source_use']) == 11, 'source-use scope drift')
    orig_cites = CITE.findall(orig_html.decode('utf-8'))
    new_cites = CITE.findall(candidate_html.decode('utf-8'))
    require(len(orig_cites) == 16 and orig_cites == new_cites, 'citation sequence changed')
    require(len(candidate_html) >= .98 * len(orig_html), 'lost reading depth')
    return {'status':'DRAFT_HARD_HOLD', 'corrected_html_bytes':len(candidate_html),
            'citation_occurrences':len(new_cites),'source_relationships':11,
            'original_html_blob':git_blob(orig_html),'staged_html_blob':git_blob(candidate_html),
            'original_metadata_blob':git_blob(orig_meta),'staged_metadata_blob':git_blob(candidate_meta),
            'qualified_source_review':False,'independent_qd_pass':False,
            'public_release_allowed':False,'paid_checkout_enabled':False}


def census(root, manifest):
    require(manifest['schema'] == 'fv-preparedness-r151-v1' and manifest['decision'] == 'DRAFT_HARD_HOLD', 'frozen manifest changed')
    pinned = manifest['metadata_blobs']
    require(isinstance(pinned, dict) and len(pinned) == 35, '35 metadata required')
    folder = root/'preparedness/content/articles'
    metas = {p.name[:-10]:p for p in folder.glob('*.meta.json')}
    bodies = {p.name[:-10]:p for p in folder.glob('*.body.html')}
    require(set(metas) == set(bodies) == set(pinned), '35 article body/metadata census differs')
    urls = set()
    counts = {'pending':0,'not-required':0,'approved':0}
    for slug in sorted(pinned):
        require(bool(SLUG.fullmatch(slug)), 'malformed article slug')
        data = json.loads(source(root, 'preparedness/content/articles/'+slug+'.meta.json', pinned[slug]))
        require(data['slug'] == slug and data['status']['publish'] == 'draft', 'article no longer draft')
        state = data['safety_review']['state']
        require(state in counts, 'unknown safety state')
        counts[state] += 1
        route='/preparedness/'+data['section']+'/'+slug+'/'
        require(route not in urls, 'duplicate route')
        urls.add(route)
        html=source(root,'preparedness/content/articles/'+slug+'.body.html').decode('utf-8')
        words=len(WORD.findall(re.sub(r'<[^>]+>|\{\{cite:[^}]+\}\}',' ',html)))
        require(words>=1500 and len(CITE.findall(html)) >= 20, 'article depth/citation floor: '+slug)
    return {'article_pairs':len(urls),'unique_routes':len(urls),'metadata_safety_states':counts,
            'original_articles_unchanged_by_review_files':True,'independent_safety_approval':False}


def audit(root):
    root=root.resolve(strict=True)
    r158_raw=source(root,R158,R158_BLOB)
    source(root,MANIFEST,MANIFEST_BLOB)
    spec=importlib.util.spec_from_file_location('r158_pinned_for_r159',root/R158)
    require(spec is not None and spec.loader is not None, 'R158 import unavailable')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    orig_html=source(root,ORIG_BODY,mod.BODY_BLOB)
    orig_meta=source(root,ORIG_META,mod.META_BLOB)
    exp_html, exp_meta, proof=mod.correction(orig_html.decode('utf-8'),orig_meta.decode('utf-8'))
    require(proof['state']=='DRAFT_HARD_HOLD' and proof['public_publishing_allowed'] is False,
            'R158 failed to preserve hard hold')
    candidate=validate_pair(orig_html,orig_meta,exp_html.encode('utf-8'),exp_meta.encode('utf-8'),
                            source(root,CAND_BODY),source(root,CAND_META))
    candidate['corpus']=census(root,json.loads(source(root,MANIFEST)))
    candidate['r158_source_blob']=git_blob(r158_raw)
    return candidate


def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('--repo',type=Path,default=Path('.'))
    args=parser.parse_args(argv)
    try:
        print(json.dumps(audit(args.repo),sort_keys=True))
    except (OSError,ValueError,KeyError,TypeError,UnicodeError,json.JSONDecodeError) as err:
        print(json.dumps({'status':'INVALID_HARD_HOLD','reason':str(err),'public_release_allowed':False}))
    return 2  # mandatory, even when every structural check succeeds

if __name__ == '__main__':
    raise SystemExit(main())
