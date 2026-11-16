#!/usr/bin/env python3
"""Deterministic ZIP for local R412 QA. Exclude installed parent R411 dependencies."""
from pathlib import Path
import zipfile,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
INCLUDE=['README.md','qa/http_server.py','qa/test_http_acceptance.py','qa/test_source_guard.py','qa/test_release_gate.py','qa/release_gate.py','qa/package_evidence.py']
INCLUDE += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'QA').rglob('*')) if p.is_file() and p.name not in ('Apollo_R412_Local_Evidence.zip','sha256_manifest.json')]
OUT=ROOT/'QA/Apollo_R412_Local_Evidence.zip'
manifest={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(INCLUDE)}
(ROOT/'QA/sha256_manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
INCLUDE.append('QA/sha256_manifest.json')
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for name in sorted(INCLUDE):
  info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644 << 16
  z.writestr(info,(ROOT/name).read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'zip':str(OUT),'entries':len(INCLUDE),'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest()},sort_keys=True))
