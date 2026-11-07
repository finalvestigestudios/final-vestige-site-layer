#!/usr/bin/env python3
"""Read-only WP Page 6 vs pinned EX2 Blueprint drift admission; no CMS/network writes.

Use --live-json only with an authorized, locally saved pages.get response containing
public Page 6 data. For narrow evidence use --live-manifest (from a read-only
connector scan). Neither mode certifies WordPress staging, rights or paid sales.
"""
import argparse, hashlib, html, json, re, sys
from pathlib import Path

ANCHORS = ('fv-hf-evidence','fv-hf-title','fv-hf-chronicle','fv-hf-inquiry',
           'fv-hf-method-title','fv-hf-observer','fv-hf-mind-title')
MEDIA = ('s67-19766.webp','Franklinexpeditionnote.jpg',
         'edit-017-v02-nypl-5003296-original.jpg')
BLOB_SHA = '137c74a476005684a28f5ff9a36e75c6b03268f7'

def sha_blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def scan(markup):
    image_tags = re.findall(r'<img\b[^>]*>', markup, flags=re.I)
    image_srcs = [html.unescape((re.search(r'\bsrc=[\'\"]([^\'\"]+)', tag, re.I) or ('',''))[1]) for tag in image_tags]
    urls = re.findall(r'\bhref=[\'\"]([^\'\"]+)', markup, re.I)
    hero = markup.find('data-fv-home-flagship')
    margin = markup.find('class="fv-margin-strip fv-margin-strip--rotator"')
    return {
        'characters':len(markup),
        'chapters':{a:bool(re.search(r'\bid=[\'\"]'+re.escape(a)+r'[\'\"]',markup)) for a in ANCHORS},
        'margin_records':markup.count('class="fv-margin-strip__item"'),
        'margin_before_hero':margin>=0 and (hero<0 or margin<hero),
        'focus_hrefs':sum('/focus/' in html.unescape(u) for u in urls),
        'images_total':len(image_tags),
        'image_media':{name:sum(name in u for u in image_srcs) for name in MEDIA},
        'image_cdn':sum(u.startswith('https://i0.wp.com/') for u in image_srcs),
        'image_src_hosts':sorted(set(re.sub(r'^https?://([^/]+)/?.*',r'\1',u) for u in image_srcs if u.startswith('http'))),
    }

def blueprint_markup(raw):
    if sha_blob(raw)!=BLOB_SHA:
        raise ValueError('Candidate Git blob changed: refuse to compare unpinned source')
    steps=json.loads(raw)['steps']
    code=next(s['data'] for s in steps if s['step']=='writeFile' and 'FVPG_HTML_END' in s.get('data',''))
    return code.split("<<<'FVPG_HTML_END'\n",1)[1].split('\nFVPG_HTML_END;',1)[0]

def evaluate(live,candidate):
    diffs={key:{'live':live[key],'candidate':candidate[key]}
           for key in ('margin_before_hero','focus_hrefs','images_total','image_media','image_cdn')
           if live[key]!=candidate[key]}
    live_core=all(live['chapters'].values()) and live['margin_records']==72
    candidate_core=all(candidate['chapters'].values()) and candidate['margin_records']==72
    return {'gate':'RELEASE_HOLD_LIVE_CANDIDATE_DIFFER' if diffs else 'NO_CHECKED_DRIFT',
            'live_seven_chapter_core':live_core,'candidate_seven_chapter_core':candidate_core,
            'differences':diffs,
            'protection':'Read-only snapshot; no permissions to modify WordPress or merge PR #49',
            'limitations':'Page content and image metadata are not network-byte, WordPress Playground, axe, Lighthouse, Jetpack, QD or conversion acceptance'}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--blueprint',type=Path,required=True)
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--live-json',type=Path)
    g.add_argument('--live-manifest',type=Path)
    args=p.parse_args()
    candidate=scan(blueprint_markup(args.blueprint.read_bytes()))
    if args.live_manifest:
        doc=json.loads(args.live_manifest.read_text());live=doc['scan']
        if doc.get('page_id')!=6 or doc.get('status')!='publish':raise ValueError('Not a published Page 6 manifest')
    else:
        doc=json.loads(args.live_json.read_text());page=doc.get('data',doc)
        if page.get('id')!=6 or page.get('status')!='publish':raise ValueError('Not published WordPress Page 6')
        live=scan(page['content'])
    output={'live_page':{'id':6,'status':'publish','modified':doc.get('modified')},
            'candidate_blob':BLOB_SHA,'live':live,'candidate':candidate,'result':evaluate(live,candidate)}
    print(json.dumps(output,indent=2,sort_keys=True))
    return 2 if output['result']['gate'].startswith('RELEASE_HOLD') else 0

if __name__=='__main__':sys.exit(main())
