#!/usr/bin/env python3
"""Deterministic R56 STAGING-HOLD source/WordPress/Chromium review bundle.

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

STAMP = (2026,11,1,0,0,0)
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
    crosswalk=ROOT/'experience2/research-desk/sources/R37_PHOTO_CUSTODY_CROSSWALK.json'
    files[crosswalk.relative_to(ROOT).as_posix()]=crosswalk.read_bytes()
    with tempfile.TemporaryDirectory() as tmp:
        temp=Path(tmp)
        built=temp/'staging'
        stage=build_wordpress_stage.build(built)
        if stage['media_rights_unreviewed'] != 6 or stage['embedded_images'] != 0 or stage['geographic_pins'] != 0:
            raise ValueError('Unsafe staging build')
        for p in sorted(built.rglob('*')):
            if p.is_file():
                files['staging-r56/'+p.relative_to(built).as_posix()]=p.read_bytes()
    expected=('R56_CUSTODY_BROWSER_RECEIPT.json','r56-custody-390.png','r56-custody-1440.png')
    for name in expected:
        p=qa/name
        if not p.is_file():raise FileNotFoundError('Required local QA artifact missing: '+str(p))
        files['qa-r56/'+name]=p.read_bytes()
    receipt=json.loads(files['qa-r56/R56_CUSTODY_BROWSER_RECEIPT.json'])
    if len(receipt['cases'])!=16 or not all(row['pass'] for row in receipt['cases']):
        raise ValueError('Unsuccessful real-browser QA receipt')
    for name,digest in receipt['screenshots'].items():
        if hashlib.sha256(files['qa-r56/'+name]).hexdigest()!=digest:
            raise ValueError('Screenshot hash mismatch: '+name)
    manifest={'schema':'fv.ex2.apollo.r56.deterministic-review.v1',
        'release':'STAGING_HOLD','photo_binaries_embedded':0,'geographic_pins':0,
        'wordpress_installed':False,'actual_r38_cohost_tested':False,
        'files':{k:hashlib.sha256(files[k]).hexdigest() for k in sorted(files)}}
    files['R56_SHA256_MANIFEST.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
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
    parser.add_argument('--qa',type=Path,default=ROOT/'qa-r56')
    args=parser.parse_args();build(args.output,args.qa)
