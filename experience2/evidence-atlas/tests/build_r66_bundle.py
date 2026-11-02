#!/usr/bin/env python3
"""Fully deterministic R66 staging review ZIP, no WordPress writes or remote fetch."""
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
from build_full_staging_r66 import build as build_stage
from test_desk_profiles_r52 import EXPECTED,blob
STAMP=(2026,11,2,0,0,0)

def build(output:Path,qa:Path):
    report=json.loads((qa/'R66_CUSTODY_MATRIX_BROWSER_RECEIPT.json').read_text())
    assert len(report['responsive_cases'])==32
    assert len(report['tampering_cases'])==54
    assert len(report['structural_mutations'])==3
    assert report['installed_wordpress'] is False
    assert report['verified_axe'] is False
    assert report['copyright_assessments_pending']==6
    files={}
    for root in (HERE,ROOT/'experience2/research-desk'):
        for path in sorted(root.rglob('*')):
            if path.is_file() and path.suffix in ('.md','.py','.php','.html','.css','.js','.json') and '__pycache__' not in path.parts:
                files[path.relative_to(ROOT).as_posix()]=path.read_bytes()
    for path,sha in EXPECTED['r38-custody-search'].items():
        assert blob((ROOT/'experience2/research-desk'/path).read_bytes())==sha
    for filename,sha in report['screenshots'].items():
        data=(qa/filename).read_bytes()
        assert hashlib.sha256(data).hexdigest()==sha
        files['qa-r66/'+filename]=data
    files['qa-r66/R66_CUSTODY_MATRIX_BROWSER_RECEIPT.json']=(qa/'R66_CUSTODY_MATRIX_BROWSER_RECEIPT.json').read_bytes()
    with tempfile.TemporaryDirectory() as scratch:
        stage=Path(scratch)/'staging'
        manifest=build_stage(stage)
        assert manifest['custody_fields_verified']==54
        assert manifest['embedded_images']==0 and manifest['geographic_pins']==0
        for f in sorted(stage.rglob('*')):
            if f.is_file():files['staging-r66/'+f.relative_to(stage).as_posix()]=f.read_bytes()
    sha={name:hashlib.sha256(data).hexdigest() for name,data in sorted(files.items())}
    files['R66_SHA256_MANIFEST.json']=(json.dumps({
      'schema':'fv.apollo.r66.archive.v1','release':'STAGING_HOLD',
      'wordpress_installed':False,'axe_certified':False,'files':sha},
      indent=2,sort_keys=True)+'\n').encode()
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w') as archive:
        for filename,data in sorted(files.items()):
            info=zipfile.ZipInfo(filename,STAMP)
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16;info.create_system=3
            archive.writestr(info,data,compresslevel=9)
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        assert all(hashlib.sha256(archive.read(n)).hexdigest()==v for n,v in sha.items())
    return {'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
      'files':len(files),'release':'STAGING_HOLD'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path)
    p.add_argument('--qa',required=True,type=Path)
    print(json.dumps(build(**vars(p.parse_args())),sort_keys=True))
