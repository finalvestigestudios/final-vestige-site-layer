#!/usr/bin/env python3
"""Deterministically archive R393 exact source + local QA; no network or WP writes."""
import hashlib
import json
import zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'apollo-r393'
selected=[ROOT/'apollo-r377/custody.json', ROOT/'apollo-r392/qa/semantic_custody.py',
          ROOT/'apollo-r389/qa/staging_smoke.py', BASE/'README.md',
          BASE/'qa/topology.py', BASE/'qa/test_topology.py',
          BASE/'qa/staging_gate.py', BASE/'qa/package.py',
          BASE/'QA/local-php-fixture.html', BASE/'QA/topology-results.json',
          BASE/'QA/320-mobile.png',BASE/'QA/320-nojs.png',BASE/'QA/1440-desktop.png']
if not all(p.is_file() for p in selected):
    raise SystemExit('HOLD: missing source or executed browser evidence; no partial archive')
manifest={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in selected}
manifest_bytes=(json.dumps({'kind':'R393_LOCAL_NOT_INSTALLED_STAGING',
                            'files_sha256':manifest,'release_allowed':False},
                            sort_keys=True,indent=2)+'\n').encode('utf8')
out=BASE/'QA/Apollo_R393_Local_Evidence.zip'

def add(archive,name,data):
    entry=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
    entry.create_system=3
    entry.external_attr=(0o100644<<16)
    entry.compress_type=zipfile.ZIP_DEFLATED
    archive.writestr(entry,data)

def build(path):
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(selected,key=lambda p:p.relative_to(ROOT).as_posix()):
            add(z,p.relative_to(ROOT).as_posix(),p.read_bytes())
        add(z,'apollo-r393/QA/manifest.json',manifest_bytes)
build(out)
check=BASE/'QA/_rebuild_verify.zip'
build(check)
assert out.read_bytes()==check.read_bytes(),'HOLD: nondeterministic output'
check.unlink()
print(json.dumps({'file':str(out),'entries':len(manifest)+1,
                  'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
                  'repeat_build_identical':True},indent=2))
