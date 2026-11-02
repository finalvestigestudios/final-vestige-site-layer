#!/usr/bin/env python3
"""Deterministic R65 staging artifact: original sources, test code, QA screenshots."""
import argparse
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
HERE=ROOT/'experience2/evidence-atlas'
sys.path.insert(0,str(HERE/'tests'))
from build_full_staging_r65 import build as build_stage
from test_desk_profiles_r52 import EXPECTED,blob
STAMP=(2026,11,2,0,0,0)

def build(output:Path,qa:Path):
    result=json.loads((qa/'R65_ALL_TARGETS_BROWSER_RECEIPT.json').read_text())
    assert len(result['cases'])==32 and all(r['pass'] for r in result['cases'])
    assert min(r['minimum_target_height_px'] for r in result['cases'])>=43.5
    assert result['wordpress']=='NOT_INSTALLED' and result['axe'].startswith('NOT_EXECUTED')
    files={}
    for root in (HERE,ROOT/'experience2/research-desk'):
        for f in sorted(root.rglob('*')):
            if f.is_file() and f.suffix in ('.md','.py','.php','.html','.css','.js','.json') and '__pycache__' not in f.parts:
                files[f.relative_to(ROOT).as_posix()]=f.read_bytes()
    for relative,pin in EXPECTED['r38-custody-search'].items():
        assert blob((ROOT/'experience2/research-desk'/relative).read_bytes())==pin
    for name,digest in result['screenshots'].items():
        data=(qa/name).read_bytes();assert hashlib.sha256(data).hexdigest()==digest
        files['qa-r65/'+name]=data
    files['qa-r65/R65_ALL_TARGETS_BROWSER_RECEIPT.json']=(qa/'R65_ALL_TARGETS_BROWSER_RECEIPT.json').read_bytes()
    with tempfile.TemporaryDirectory() as scratch:
        stage=Path(scratch)/'staging';manifest=build_stage(stage)
        assert len(manifest['files'])==11 and manifest['media_rights_unreviewed']==6
        assert manifest['embedded_images']==0 and manifest['geographic_pins']==0
        for f in sorted(stage.rglob('*')):
            if f.is_file(): files['staging-r65/'+f.relative_to(stage).as_posix()]=f.read_bytes()
    sha={n:hashlib.sha256(b).hexdigest() for n,b in sorted(files.items())}
    files['R65_SHA256_MANIFEST.json']=(json.dumps({'schema':'fv.apollo.r65.archive.v1','release':'STAGING_HOLD','wordpress_installed':False,'axe_certified':False,'files':sha},indent=2,sort_keys=True)+'\n').encode()
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w') as z:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo(name,STAMP);info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16;info.create_system=3
            z.writestr(info,data,compresslevel=9)
    with zipfile.ZipFile(output) as z:
        assert z.testzip() is None
        assert all(hashlib.sha256(z.read(n)).hexdigest()==v for n,v in sha.items())
    return {'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'files':len(files),'release':'STAGING_HOLD'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path)
    p.add_argument('--qa',required=True,type=Path)
    print(json.dumps(build(**vars(p.parse_args())),sort_keys=True))
