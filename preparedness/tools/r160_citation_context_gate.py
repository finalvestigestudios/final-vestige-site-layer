#!/usr/bin/env python3
"""Preparedness R160: deterministic claim-to-source context inventory, never a safety approval.

Read-only for a trusted checkout. Candidate / article metadata remain DRAFT / HOLD.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

MANIFEST = 'preparedness/docs/r151/contributor-three-way.json'
MANIFEST_BLOB = '9cf386519eda970209ff6be4ff0243661cd9d996'
STAGE_BODY = 'preparedness/review/r159/family-reunification-card.body.html'
STAGE_META = 'preparedness/review/r159/family-reunification-card.meta.json'
STAGE_BODY_BLOB = '7a7b6cffbc75cb6c9a0c13ad5002ccf0f5d22ef0'
STAGE_META_BLOB = '2bafef03a375b0156e2dcd7f1b913d119becad61'
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
ANY_CITE = re.compile(r'\{\{\s*cite\b[^}]*\}\}', re.I)
ID = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
WORD = re.compile(r"[A-Za-z0-9_’\-]+")
TAG = re.compile(r'<[^>]*>')
SPACE = re.compile(r'\s+')


def need(test, message):
    if not test:
        raise ValueError(message)


def blob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\x00' + raw).hexdigest()


def load(root, relative, expected_blob=None):
    path = root / relative
    need(path.is_file() and not path.is_symlink(), 'missing or symlink: ' + relative)
    raw = path.read_bytes()
    if expected_blob:
        need(blob(raw) == expected_blob, 'Git blob changed: ' + relative)
    return raw


def clean(html):
    return SPACE.sub(' ', TAG.sub(' ', CITE.sub('', html))).strip()


def article(slug, meta, html, meta_blob, body_blob):
    need(ID.fullmatch(slug), 'invalid slug: ' + slug)
    need(meta.get('slug') == slug and meta.get('status', {}).get('publish') == 'draft', 'publication/slug drift: ' + slug)
    state = meta.get('safety_review', {}).get('state')
    need(state in ('pending', 'not-required', 'approved'), 'unknown safety state: ' + slug)
    section = meta.get('section')
    need(isinstance(section, str) and ID.fullmatch(section), 'invalid section: ' + slug)
    uses = meta.get('source_use')
    need(isinstance(uses, dict) and uses, 'missing source interpretations: ' + slug)
    need(all(isinstance(k, str) and ID.fullmatch(k) and isinstance(v, str) and len(v.strip()) >= 8 for k,v in uses.items()), 'malformed source interpretation: ' + slug)
    marks = list(CITE.finditer(html))
    need(len(marks) >= 20, 'citation depth floor: ' + slug)
    need(len(WORD.findall(clean(html))) >= 1500, 'reading depth floor: ' + slug)
    need(len(marks) == len(ANY_CITE.findall(html)), 'malformed citation markup: ' + slug)
    need(set(m.group(1) for m in marks) == set(uses), 'citation/source-use mismatch: ' + slug)
    entries = []
    for i,mark in enumerate(marks,1):
        source_id = mark.group(1)
        before = clean(html[max(0, mark.start() - 175):mark.start()])[-130:]
        after = clean(html[mark.end():mark.end()+175])[:130]
        context = SPACE.sub(' ', before + ' [SOURCE] ' + after).strip()
        entries.append({'article':slug, 'ordinal':i, 'source_id':source_id,
                        'interpretation':uses[source_id], 'context':context,
                        'context_sha256':hashlib.sha256(context.encode('utf-8')).hexdigest()})
    return {'slug':slug, 'route':f'/preparedness/{section}/{slug}/',
            'safety_recorded':state, 'meta_blob':meta_blob, 'body_blob':body_blob,
            'words':len(WORD.findall(clean(html))), 'citations':len(entries),
            'unique_sources':len(uses), 'contexts':entries}


def review_card(meta, html):
    need(meta.get('kind') == 'tool' and meta.get('slug') == 'family-reunification-card', 'staged tool identity changed')
    need(meta.get('status', {}).get('publish') == 'draft', 'staged tool is not draft')
    need(meta.get('safety_review', {}).get('state') == 'pending', 'staged tool safety forged')
    need(len(CITE.findall(html)) == 16 and len(meta.get('source_use', {})) == 11, 'staged source/citation drift')
    need(set(CITE.findall(html)) == set(meta['source_use']), 'staged references not mapped')
    need('Independent browser privacy checks remain pending.' in html, 'privacy qualifier removed')
    need('browser privacy and print behavior remain unverified' in meta.get('description',''), 'unverified print/privacy caveat removed')
    return {'slug':meta['slug'], 'route':'/preparedness/field-tools/family-reunification-card/',
            'safety_recorded':'pending', 'review_only':True, 'citations':16, 'unique_sources':11}


def census(root):
    manifest = json.loads(load(root, MANIFEST, MANIFEST_BLOB))
    need(manifest.get('schema') == 'fv-preparedness-r151-v1' and manifest.get('decision') == 'DRAFT_HARD_HOLD', 'manifest release gate changed')
    pins = manifest.get('metadata_blobs')
    need(isinstance(pins,dict) and len(pins) == 35, '35 immutable metadata IDs required')
    folder = root/'preparedness/content/articles'
    metas = {x.name[:-10] for x in folder.glob('*.meta.json') if x.is_file() and not x.is_symlink()}
    bodies = {x.name[:-10] for x in folder.glob('*.body.html') if x.is_file() and not x.is_symlink()}
    need(metas == bodies == set(pins), 'original 35 article pairs changed')
    records = []
    for slug in sorted(pins):
        m=load(root, f'preparedness/content/articles/{slug}.meta.json', pins[slug])
        b=load(root, f'preparedness/content/articles/{slug}.body.html')
        records.append(article(slug,json.loads(m),b.decode('utf-8'),blob(m),blob(b)))
    raw=load(root,STAGE_BODY,STAGE_BODY_BLOB)
    mraw=load(root,STAGE_META,STAGE_META_BLOB)
    stage=review_card(json.loads(mraw),raw.decode('utf-8'))
    routes=[x['route'] for x in records]+[stage['route']]
    need(len(set(routes)) == 36, 'duplicate publication route')
    states={key:sum(1 for x in records if x['safety_recorded']==key) for key in ('pending','not-required','approved')}
    need(states == {'pending':29,'not-required':4,'approved':2}, 'frozen metadata safety distribution changed')
    contexts=[y for x in records for y in x['contexts']]
    digest=hashlib.sha256(json.dumps(contexts,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode('utf-8')).hexdigest()
    return {'schema':'fv-preparedness-r160-context-review-v1','state':'DRAFT_HARD_HOLD',
            'article_count':35,'unique_routes':36,'recorded_safety_states_not_approvals':states,
            'citation_contexts':len(contexts),'article_source_occurrences':sum(x['unique_sources'] for x in records),
            'context_docket_sha256':digest,'tool_review':stage,'qualified_human_source_review':False,
            'independent_qd_pass':False,'live_publication_authorized':False,
            'verified_paid_offer':False,'records':records}


def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,default=Path('.'))
    p.add_argument('--details',action='store_true',help='include source-use contexts for human reviewers (stdout only)')
    args=p.parse_args(argv)
    try:
        report=census(args.repo.resolve(strict=True))
        if not args.details:
            report.pop('records')
    except (ValueError,KeyError,TypeError,OSError,UnicodeError,json.JSONDecodeError) as exc:
        report={'state':'INVALID_HARD_HOLD','error':str(exc),'live_publication_authorized':False}
    print(json.dumps(report,sort_keys=True,ensure_ascii=False))
    return 2  # Always an unpublished review artifact, even if all structural checks pass.

if __name__ == '__main__':
    raise SystemExit(main())
