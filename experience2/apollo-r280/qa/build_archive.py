#!/usr/bin/env python3
"""Create byte-repeatable offline review bundle. Never touch WordPress/production."""
import hashlib, json, sys, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
if len(sys.argv)!=5:
    raise SystemExit('Usage: build_archive.py GITHUB_HEAD QA_A QA_B OUTPUT_ZIP')
head, a, b, output=sys.argv[1:]
if len(head)!=40 or any(ch not in '0123456789abcdef' for ch in head):
    raise SystemExit('Expected exact lowercase 40-character GitHub HEAD')
a,b,output=Path(a),Path(b),Path(output)
assert (a/'receipt.json').read_bytes()==(b/'receipt.json').read_bytes(), 'non-deterministic receipts'
items=[]
for f in sorted((ROOT/'experience2').rglob('*')):
    if f.is_file() and '__pycache__' not in f.parts and f.suffix!='.pyc':
        items.append((f.relative_to(ROOT).as_posix(),f.read_bytes()))
for directory,label in ((a,'QA-A'),(b,'QA-B')):
    for f in sorted(directory.iterdir()):
        if f.is_file():items.append((label+'/'+f.name,f.read_bytes()))
assert len(set(name for name,_ in items))==len(items)
manifest={'github_head':head,'review_status':'DRAFT_HARD_HOLD',
          'qa_receipt_sha256':hashlib.sha256((a/'receipt.json').read_bytes()).hexdigest(),
          'not_verified':['installed WordPress','axe-core','screen readers','HTTP/CSP browser','field LCP/CLS','merchant settlements','founder release approval'],
          'files':{name:hashlib.sha256(data).hexdigest() for name,data in sorted(items)}}
items.append(('EVIDENCE-MANIFEST.json',(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()))
output.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_STORED) as z:
    for name,data in sorted(items):
        meta=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
        meta.external_attr=0o644<<16
        meta.compress_type=zipfile.ZIP_STORED
        z.writestr(meta,data)
print('R280 deterministic archive',len(items),'files sha256',hashlib.sha256(output.read_bytes()).hexdigest())
