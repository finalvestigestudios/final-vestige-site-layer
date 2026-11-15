#!/usr/bin/env python3
"""Deterministic R373 offline fixture evidence pack, no network or uploads."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[3]
STAGE = ROOT / 'experience2/apollo-r373'
FILES = [
 'experience2/apollo-r365/chrono-rail.php',
 'experience2/apollo-r367/sealed-chronology.php',
 'experience2/apollo-r371/source-gallery.php',
 'experience2/apollo-r372/evidence-path.php',
 'experience2/apollo-r372/assets/evidence-path.css',
 'experience2/apollo-r372/qa/fixture.php',
 'experience2/apollo-r373/README.md',
 'experience2/apollo-r373/qa/staging_acceptance.py',
 'experience2/apollo-r373/qa/preflight_test.py',
 'experience2/apollo-r373/qa/package.py',
]

def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

def build(destination):
    photos = sorted(str(p.relative_to(ROOT)) for p in (STAGE/'QA').glob('*.png'))
    evidence = sorted(str(p.relative_to(ROOT)) for p in (STAGE/'QA').glob('*.pdf'))
    report = 'experience2/apollo-r373/QA/results.json'
    paths = sorted(FILES + photos + evidence + [report])
    items = {}
    for name in paths:
        data = (ROOT/name).read_bytes()
        items[name] = {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(), 'git_blob_sha1':git_blob(data)}
    summary = json.loads((ROOT/report).read_text())
    manifest = {
        'artifact':'Apollo R373 local fixture evidence, NOT WordPress staging',
        'test_status':summary['status'],
        'axe':'NOT EXECUTED — local fixture only',
        'http_csp':'NOT EXECUTED — local fixture only',
        'source_review':'NASA URLs checked; image/media commercial clearance NOT granted',
        'source_files':items,
    }
    payload = {'R373_MANIFEST.json':(json.dumps(manifest,indent=2,sort_keys=True,ensure_ascii=False)+'\n').encode()}
    payload.update({k:(ROOT/k).read_bytes() for k in paths})
    with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in sorted(payload):
            meta = zipfile.ZipInfo(name,(1980,1,1,0,0,0))
            meta.compress_type = zipfile.ZIP_DEFLATED
            meta.external_attr = 0o100644 << 16
            z.writestr(meta,payload[name],compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return hashlib.sha256(Path(destination).read_bytes()).hexdigest(),len(payload)

if __name__=='__main__':
    a=sys.argv[1] if len(sys.argv)>1 else str(STAGE/'Apollo_R373_Evidence.zip')
    b=a+'.rebuild'
    first,n=build(a)
    second,_=build(b)
    Path(b).unlink()
    if first!=second: raise RuntimeError('NONDETERMINISTIC evidence rebuild')
    print('R373 deterministic ZIP PASS',n,'files SHA256',first)
