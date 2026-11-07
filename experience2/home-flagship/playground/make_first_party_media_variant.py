#!/usr/bin/env python3
"""Derived non-release WordPress Playground variant; canonical EX2 Blueprint untouched.

This tests the cost/feasibility of same-origin image requests, NOT measured bytes.
"""
import argparse
import base64
import hashlib
import html
import json
import re
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED

BASE_BLOB = '137c74a476005684a28f5ff9a36e75c6b03268f7'
VARIANT_BLOB = 'f7091ba1383a5c9438ef893d62bf35d18a6e2462'
REGEX = r' srcset="[^"]+" sizes="[^"]+"(?= loading="lazy" decoding="async" data-fv-archive-img)'

def git_blob(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def derive(raw):
    if git_blob(raw)!=BASE_BLOB: raise ValueError('Exact source changed: refuse stale/mutated Blueprint')
    bp=json.loads(raw)
    assert len(bp['steps']) == 5 and bp['steps'][0]['step'] == 'installTheme'
    src=bp['steps'][2]['data']
    fixed,count=re.subn(REGEX,'',src)
    if count != 2 or len(re.findall(r'<img[^>]+data-fv-archive-img>',src))!=2:
        raise ValueError('Exactly two expected archival images not found')
    bp['steps'][2]['data']=fixed
    out=(json.dumps(bp,ensure_ascii=False,indent=2)+'\n').encode()
    if git_blob(out)!=VARIANT_BLOB: raise ValueError('Derived preview has unexpected bytes')
    return out

def build(raw,dest):
    generated=derive(raw)
    slug='FV_EX2_FIRST_PARTY_MEDIA_REVIEW_ONLY'
    manifest={'review':'not for release; independent CDN-versus-origin speed comparison required',
              'parent_blob':BASE_BLOB,'variant_blob':VARIANT_BLOB,'tested_wordpress':False,
              'tested_actual_transfer_bytes':False,'tested_cwv':False,
              'source_original_bytes':{'Apollo_473':78346,'Franklin_474':466043},
              'origin':'finalvestige.com','provenance':'WordPress media IDs 473 and 474; virtual CDN resized variants'}
    link='https://playground.wordpress.net/#'+base64.urlsafe_b64encode(generated).decode()
    doc=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FV Origin-Only Media — Private Review</title><style>body{{margin:0;display:grid;place-items:center;min-height:100vh;padding:1rem;background:#0b1011;color:#e8ddc8;font:18px/1.65 system-ui}}main{{max-width:680px;border:1px solid #bca16a;padding:clamp(1rem,5vw,3rem);background:#162323}}h1{{font:normal 2.6rem Georgia,serif}}a{{display:inline-block;min-height:44px;background:#ddb779;color:#151b19;padding:1rem;font-weight:bold;overflow-wrap:anywhere}}a:focus-visible{{outline:3px solid white;outline-offset:3px}}p{{overflow-wrap:anywhere}}</style><main><h1>Evidence, from the source.</h1><p>PRIVATE REVIEW VARIANT ONLY. This changes only archival image browser request selection to the original first-party URLs. It deliberately removes virtual CDN-responsive candidates, which may substantially increase mobile bytes. Not a release recommendation until network and Lighthouse comparison.</p><p><a target="_blank" rel="noreferrer noopener" href="{html.escape(link,quote=True)}">Open isolated WordPress Playground experiment ↗</a></p><p>Exact parent blob: <code>{BASE_BLOB}</code><br>Derived variant: <code>{VARIANT_BLOB}</code></p><p>No subscriber records, live CMS edits, affiliate scripts, paid services or deployments.</p></main></html>'''.encode()
    dest=Path(dest);dest.mkdir(parents=True,exist_ok=True)
    zip_path=dest/(slug+'.zip')
    with ZipFile(zip_path,'w') as z:
        for name,content in [('blueprint_first_party_variant.json',generated),('launch_review.html',doc),('source_manifest.json',(json.dumps(manifest,indent=2)+'\n').encode())]:
            info=ZipInfo(name,(2026,11,7,6,0,0));info.compress_type=ZIP_DEFLATED
            z.writestr(info,content)
    return {'zip':str(zip_path),'source_blob':BASE_BLOB,'variant_blob':VARIANT_BLOB,'output_bytes':zip_path.stat().st_size,
            'release_decision':'HOLD','actual_wordpress':False}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('canonical');ap.add_argument('output_dir');args=ap.parse_args()
    print(json.dumps(build(Path(args.canonical).read_bytes(),args.output_dir),indent=2))
