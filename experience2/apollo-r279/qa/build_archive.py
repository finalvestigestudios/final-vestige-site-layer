#!/usr/bin/env python3
"""Deterministic unapproved staging evidence archive, reproducible byte-for-byte."""
import hashlib, json, sys, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
if len(sys.argv)!=5:
    raise SystemExit('Usage: build_archive.py EXACT_GITHUB_HEAD QA_A QA_B OUTPUT_ZIP')
head, qa_a, qa_b, dest=sys.argv[1:]
if len(head)!=40 or any(c not in '0123456789abcdef' for c in head):
    raise SystemExit('40-char lowercase head SHA required')
qa_a=Path(qa_a);qa_b=Path(qa_b);dest=Path(dest)
assert (qa_a/'receipt.json').read_bytes()==(qa_b/'receipt.json').read_bytes(), 'nonreproducible receipts'
file_pairs=[]
for f in sorted((ROOT/'experience2').rglob('*')):
    if f.is_file() and '__pycache__' not in f.parts and f.suffix!='.pyc':
        file_pairs.append((str(f.relative_to(ROOT)),f.read_bytes()))
for qa,name in ((qa_a,'QA-A'),(qa_b,'QA-B')):
    for f in sorted(qa.iterdir()):
        if f.is_file():file_pairs.append((name+'/'+f.name,f.read_bytes()))
assert len(set(k for k,_ in file_pairs))==len(file_pairs)
manifest={'github_head':head,'release':'HARD_HOLD','suite':'Apollo R279 staged evidence',
 'not_verified':['WordPress install','axe-core','screen reader','browser HTTP/CSP','production field CWV','merchant','revenue','founder approval'],
 'files':{k:hashlib.sha256(v).hexdigest() for k,v in sorted(file_pairs)}}
file_pairs.append(('EVIDENCE-MANIFEST.json',(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()))
dest.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name,data in sorted(file_pairs):
        info=zipfile.ZipInfo(name,(1980,1,1,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        info.external_attr=0o644<<16
        z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print('files',len(file_pairs),'sha256',hashlib.sha256(dest.read_bytes()).hexdigest())
