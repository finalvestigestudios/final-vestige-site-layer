#!/usr/bin/env python3
"""Deterministic evidence ZIP, no source writes or external services."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / 'QA'
QA.mkdir(parents=True, exist_ok=True)
FILES = [ROOT / p for p in ('README.md','qa/network_custody.py','qa/test_network_custody.py','qa/pack_evidence.py')]
FILES.extend(sorted(p for p in QA.iterdir() if p.is_file() and p.suffix in ('.png','.json') and p.name not in ('MANIFEST.json',)))
FILES = sorted(FILES, key=lambda p:p.relative_to(ROOT).as_posix())
MANIFEST = {p.relative_to(ROOT).as_posix():{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in FILES}
manifest = json.dumps({'status':'LOCAL_SHADOW_ONLY_NOT_STAGING','files':MANIFEST},indent=2,sort_keys=True).encode()+b'\n'
entries = [(p.relative_to(ROOT).as_posix(),p.read_bytes()) for p in FILES] + [('QA/MANIFEST.json',manifest)]
entries.sort()

def build(filename):
    with ZipFile(filename,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in entries:
            info=ZipInfo(name,date_time=(1980,1,1,0,0,0));info.compress_type=ZIP_DEFLATED;info.external_attr=0o644<<16
            z.writestr(info,data,compress_type=ZIP_DEFLATED,compresslevel=9)

p=QA/'Apollo_R402_Local_Evidence.zip';q=QA/'_rebuild_check.zip'
build(p);build(q)
assert p.read_bytes()==q.read_bytes(),'non-deterministic evidence archive'
q.unlink()
print(json.dumps({'entries':len(entries),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'archive':str(p)},sort_keys=True))
