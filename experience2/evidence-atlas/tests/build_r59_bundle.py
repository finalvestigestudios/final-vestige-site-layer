#!/usr/bin/env python3
"""Deterministic R59 ORIGINAL R38 PHP cohost, printed custody and browser evidence bundle.

Build requires the exact reviewed R37 crosswalk and R55 NASA page audit.
No remote requests, NASA image binaries, WordPress writes, or deployment.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
import tempfile
import zipfile
from pathlib import Path

ATLAS = Path(__file__).resolve().parents[1]
ROOT = ATLAS.parents[1]
sys.path.insert(0, str(ATLAS))
import build_wordpress_stage

STAMP = (2026,11,2,0,0,0)
EXTS = {'.py','.js','.css','.php','.json','.md','.html'}


def archive_file(archive, name, contents):
    info=zipfile.ZipInfo(name,STAMP)
    info.compress_type=zipfile.ZIP_DEFLATED
    info.external_attr=0o100644<<16
    info.create_system=3
    archive.writestr(info,contents,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)


def build(output:Path, qa:Path):
    files={}
    for p in sorted(ATLAS.rglob('*')):
        if not p.is_file() or p.suffix not in EXTS or '__pycache__' in p.parts:
            continue
        files[p.relative_to(ROOT).as_posix()]=p.read_bytes()
    desk=ROOT/'experience2/research-desk'
    from test_desk_profiles_r52 import EXPECTED,blob
    for relative,expected_sha in EXPECTED['r38-custody-search'].items():
        source=desk/relative
        if not source.is_file() or blob(source.read_bytes())!=expected_sha:
            raise ValueError('Missing or altered original R38 source: '+relative)
        files[source.relative_to(ROOT).as_posix()]=source.read_bytes()
    with tempfile.TemporaryDirectory() as tmp:
        temp=Path(tmp)
        built=temp/'staging'
        stage=build_wordpress_stage.build(built)
        if stage['media_rights_unreviewed'] != 6 or stage['embedded_images'] != 0 or stage['geographic_pins'] != 0:
            raise ValueError('Unsafe staging build')
        for p in sorted(built.rglob('*')):
            if p.is_file():
                files['staging-r59/'+p.relative_to(built).as_posix()]=p.read_bytes()
    expected=('R59_REAL_R38_BROWSER_RECEIPT.json','r59-real-r38-390.png','r59-real-r38-1440.png')
    for name in expected:
        p=qa/name
        if not p.is_file():raise FileNotFoundError('Required local QA artifact missing: '+str(p))
        files['qa-r59/'+name]=p.read_bytes()
    receipt=json.loads(files['qa-r59/R59_REAL_R38_BROWSER_RECEIPT.json'])
    if len(receipt['tests'])!=16 or len(receipt['print_regressions'])!=8 or not all(row['pass'] for row in receipt['tests']):
        raise ValueError('Unsuccessful real-browser QA receipt')
    for name,digest in receipt['screenshots'].items():
        if hashlib.sha256(files['qa-r59/'+name]).hexdigest()!=digest:
            raise ValueError('Screenshot hash mismatch: '+name)
    manifest={'schema':'fv.ex2.apollo.r59.deterministic-review.v1',
        'release':'STAGING_HOLD','photo_binaries_embedded':0,'geographic_pins':0,
        'wordpress_installed':False,'actual_r38_php_cohost_in_wp_api_mock':True,'axe_executed':False,'hosted_cwv_measured':False,
        'files':{k:hashlib.sha256(files[k]).hexdigest() for k in sorted(files)}}
    files['R59_SHA256_MANIFEST.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w') as archive:
        for name in sorted(files):archive_file(archive,name,files[name])
    digest=hashlib.sha256(output.read_bytes()).hexdigest()
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        for name, sha in manifest['files'].items():
            assert hashlib.sha256(archive.read(name)).hexdigest()==sha,name
    print(json.dumps({'output':str(output),'sha256':digest,'files':len(files),'status':'STAGING_HOLD'},sort_keys=True))
    return digest

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--qa',type=Path,default=ROOT/'qa-r59')
    args=parser.parse_args();build(args.output,args.qa)
