#!/usr/bin/env python3
"""Deterministic, exact-R38-source Apollo R60 STAGING HOLD package; never deploy."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
import tempfile
import zipfile
from pathlib import Path

ATLAS=Path(__file__).resolve().parents[1]
ROOT=ATLAS.parents[1]
sys.path.insert(0,str(ATLAS))
sys.path.insert(0,str(ATLAS/'tests'))
from test_desk_profiles_r52 import EXPECTED,blob
import build_wordpress_stage

STAMP=(2026,11,2,0,0,0)
EXTS={'.py','.js','.css','.php','.json','.md','.html'}

def build(output:Path,qa:Path):
    files={}
    for p in sorted(ATLAS.rglob('*')):
        if p.is_file() and p.suffix in EXTS and '__pycache__' not in p.parts:
            files[p.relative_to(ROOT).as_posix()]=p.read_bytes()
    desk=ROOT/'experience2/research-desk'
    for rel,sha in EXPECTED['r38-custody-search'].items():
        p=desk/rel
        if not p.is_file() or blob(p.read_bytes())!=sha:
            raise ValueError('original R38 source pin failure: '+rel)
        files[p.relative_to(ROOT).as_posix()]=p.read_bytes()
    with tempfile.TemporaryDirectory() as tmp:
        built=Path(tmp)/'stage'
        result=build_wordpress_stage.build(built)
        if result['media_rights_unreviewed']!=6 or result['embedded_images']!=0 or result['geographic_pins']!=0:
            raise ValueError('media/atlas release gate failed')
        for p in sorted(built.rglob('*')):
            if p.is_file():files['staging-r60/'+p.relative_to(built).as_posix()]=p.read_bytes()
    receipt_name='R60_ACCESSIBILITY_BROWSER_RECEIPT.json'
    receipt=json.loads((qa/receipt_name).read_text())
    if len(receipt['runs'])!=16 or not all(row['pass'] and row['min_target_height']>=44 for row in receipt['runs']):
        raise ValueError('R60 accessibility browser matrix incomplete')
    for name in [receipt_name,*receipt['screenshots']]:
        files['qa-r60/'+name]=(qa/name).read_bytes()
    for name,digest in receipt['screenshots'].items():
        if hashlib.sha256(files['qa-r60/'+name]).hexdigest()!=digest:
            raise ValueError('screenshot hash mismatch: '+name)
    manifest={'schema':'fv.ex2.apollo.r60.deterministic-review.v1',
        'release':'STAGING_HOLD','genuine_wp':False,'axe_core_executed':False,
        'real_r38_php_wordpress_mock':True,'hosted_cwv':False,
        'media_rights_unreviewed':6,'photos_embedded':0,'geo_pins':0,
        'files':{name:hashlib.sha256(value).hexdigest() for name,value in sorted(files.items())}}
    files['R60_SHA256_MANIFEST.json']=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w') as archive:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo(name,STAMP)
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16
            info.create_system=3
            archive.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        for name,digest in manifest['files'].items():
            assert hashlib.sha256(archive.read(name)).hexdigest()==digest,name
    digest=hashlib.sha256(output.read_bytes()).hexdigest()
    print(json.dumps({'zip':str(output),'sha256':digest,'files':len(files),'release':'STAGING_HOLD'},sort_keys=True))
    return digest

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--qa',type=Path,required=True)
    args=parser.parse_args()
    build(args.output,args.qa)
