#!/usr/bin/env python3
"""Deterministic R51 staging QA archive; never an approved WordPress release."""
from __future__ import annotations
import argparse,hashlib,json,tempfile,zipfile
from pathlib import Path
from browser_r51_provenance import make_document
HERE=Path(__file__).resolve().parents[1]
FIXED=(1980,1,1,0,0,0)

def build(output:Path,qa:Path):
    assert (qa/'R51_BROWSER_RECEIPT.json').is_file(), 'R51 browser QA must run first'
    source={}
    for item in sorted(HERE.rglob('*')):
        if (not item.is_file() or '__pycache__' in item.parts or item.suffix=='.pyc'
            or item.name.startswith('.') or 'qa-r51' in item.parts):continue
        source['source/'+str(item.relative_to(HERE)).replace('\\','/')]=item.read_bytes()
    source['preview/combined-php-rendered-synthetic-desk.html']=make_document().encode()
    for item in sorted(qa.glob('*')):
        if item.is_file() and item.suffix in ('.png','.json'):
            source['qa/'+item.name]=item.read_bytes()
    manifest={'schema':'fv.apollo.r51.archive.v1','release':'STAGING_HOLD',
      'status':'NO_WORDPRESS_NO_AXE_NO_PHOTO_RIGHTS_NO_PRODUCTION',
      'parent_pr':'505','photos_embedded':0,
      'source_sha256':{name:hashlib.sha256(data).hexdigest() for name,data in sorted(source.items())}}
    source['SHA256_MANIFEST.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(source.items()):
            info=zipfile.ZipInfo(name,FIXED)
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(0o100644<<16)
            z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(output) as z:
        check=json.loads(z.read('SHA256_MANIFEST.json'))['source_sha256']
        for name,digest in check.items():
            assert hashlib.sha256(z.read(name)).hexdigest()==digest,name
    return {'files':len(source),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
            'bytes':output.stat().st_size}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--qa-dir',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(build(args.output,args.qa_dir),sort_keys=True))
