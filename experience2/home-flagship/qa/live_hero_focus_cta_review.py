#!/usr/bin/env python3
"""Offline proposal only: exact-source Page 6 secondary hero CTA to /focus/.
No network, WordPress writes, tracking, subscriber actions or automatic release.
"""
import argparse
import hashlib
import json
from pathlib import Path

PIN='685911178ae68ca9dfbd8f47f5903ef57f76ac4b52e886d8287416304c98794b'
OLD='<a class="fv-hf__text-link" href="https://finalvestige.com/blog/">Read the investigations <span aria-hidden="true">↗</span></a>'
NEW='<a class="fv-hf__text-link" href="https://finalvestige.com/focus/">Explore the free 52-page Focus Fieldbook <span aria-hidden="true">↗</span></a>'
CHAPTERS=('title','chronicle','evidence','inquiry','method-title','observer','mind-title')

def digest(b): return hashlib.sha256(b).hexdigest()
def count(s,x): return s.count(x)
def inventory(s):
    return {'margins':count(s,'class="fv-margin-strip__item"'),
            'chapters':{x:count(s,'href="#fv-hf-'+x+'"') for x in CHAPTERS},
            'focus':count(s,'https://finalvestige.com/focus/')+count(s,'href="/focus/"'),
            'images':count(s,'<img '),'scripts':count(s,'<script'),
            'blocks':count(s,'<!-- wp:'),
            'archive':{x:count(s,x) for x in ('s67-19766.webp','Franklinexpeditionnote.jpg','nypl-5003296-original.jpg')}}

def propose(payload, expected_sha=PIN):
    if digest(payload)!=expected_sha: raise ValueError('HOLD: changed/unpinned Page 6')
    s=payload.decode('utf-8')
    if count(s,OLD)!=1 or NEW in s: raise ValueError('HOLD: unexpected hero action')
    a=inventory(s)
    if a['margins']!=72 or any(v<1 for v in a['chapters'].values()) or a['focus']!=4 or a['images']!=4 or any(v<1 for v in a['archive'].values()):
        raise ValueError('HOLD: page structure differs from published inventory')
    t=s.replace(OLD,NEW,1)
    b=inventory(t)
    for k in ('margins','chapters','images','scripts','blocks','archive'):
        if a[k]!=b[k]: raise ValueError('HOLD: unrelated page content changed')
    if b['focus']!=5 or t.replace(NEW,OLD,1)!=s: raise ValueError('HOLD: non-atomic change')
    return t.encode(),{'release':'HOLD','page_id':6,'source_sha256':digest(payload),'proposal_sha256':digest(t.encode()),'before':a,'after':b,'claim':'CTA placement hypothesis only; no subscribers or paid orders measured'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('page6_raw',type=Path);p.add_argument('--out',type=Path,required=True);v=p.parse_args()
    proposed,receipt=propose(v.page6_raw.read_bytes())
    v.out.write_bytes(proposed);v.out.with_suffix(v.out.suffix+'.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'status':'REVIEW_ONLY','release':'HOLD','receipt':str(v.out)+'.json'}))
