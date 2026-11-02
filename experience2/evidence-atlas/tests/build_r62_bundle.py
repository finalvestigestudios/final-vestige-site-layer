#!/usr/bin/env python3
"""Deterministic staging-only R62 date-custody/real-R38/browser review artifact."""
import argparse
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
ATLAS=ROOT/'experience2/evidence-atlas'
sys.path.insert(0,str(ATLAS))
sys.path.insert(0,str(ATLAS/'tests'))
import build_wordpress_stage
from test_desk_profiles_r52 import EXPECTED,blob

STAMP=(2026,11,2,0,0,0)

def build(output,qa):
    receipt=json.loads((qa/'R62_DATE_CUSTODY_BROWSER_RECEIPT.json').read_text())
    assert receipt['release']=='STAGING_HOLD' and len(receipt['cases'])==16 and len(receipt['adversarial_gate_cases'])==24
    assert all(row['passed'] for row in receipt['cases']) and all(row['blocked'] for row in receipt['adversarial_gate_cases'])
    assert receipt['wordpress']=='SIMULATED_NOT_INSTALLED'
    assert receipt['axe']=='NOT_EXECUTED_NO_VERIFIED_OFFLINE_BUNDLE'
    files={}
    for root in (ATLAS, ROOT/'experience2/research-desk'):
        for p in sorted(root.rglob('*')):
            if p.is_file() and p.suffix in ('.md','.py','.php','.html','.css','.js','.json') and '__pycache__' not in p.parts:
                files[p.relative_to(ROOT).as_posix()]=p.read_bytes()
    for name,expected in EXPECTED['r38-custody-search'].items():
        f=ROOT/'experience2/research-desk'/name
        assert blob(f.read_bytes())==expected,('R38 source drift',name)
    for name,sha in receipt['screenshots'].items():
        data=(qa/name).read_bytes();assert hashlib.sha256(data).hexdigest()==sha
        files['qa-r62/'+name]=data
    files['qa-r62/R62_DATE_CUSTODY_BROWSER_RECEIPT.json']=(qa/'R62_DATE_CUSTODY_BROWSER_RECEIPT.json').read_bytes()
    with tempfile.TemporaryDirectory() as temp:
        stage=Path(temp)/'staging'
        result=build_wordpress_stage.build(stage)
        assert result['media_rights_unreviewed']==6
        assert result['embedded_images']==result['geographic_pins']==0
        for p in sorted(stage.rglob('*')):
            if p.is_file():files['staging-r62/'+p.relative_to(stage).as_posix()]=p.read_bytes()
    manifest={'schema':'fv.apollo.r62.package.v1','release':'STAGING_HOLD',
              'wordpress_tested':False,'axe_executed':False,
              'files':{name:hashlib.sha256(data).hexdigest() for name,data in sorted(files.items())}}
    files['R62_SHA256_MANIFEST.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w') as z:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo(name,STAMP)
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16
            info.create_system=3
            z.writestr(info,data,compresslevel=9)
    with zipfile.ZipFile(output) as z:
        assert z.testzip() is None
        assert all(hashlib.sha256(z.read(n)).hexdigest()==s for n,s in manifest['files'].items())
    sha=hashlib.sha256(output.read_bytes()).hexdigest()
    return {'sha256':sha,'files':len(files),'status':'STAGING_HOLD'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--qa',type=Path,required=True)
    print(json.dumps(build(**vars(ap.parse_args())),sort_keys=True))
