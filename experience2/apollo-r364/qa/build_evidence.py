#!/usr/bin/env python3
"""Deterministic freeze: checked source plus browser outputs, fixed metadata."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
EX=ROOT/'experience2'/'apollo-r364';OUT=EX/'QA';OUT.mkdir(exist_ok=True)
source=[EX/'README.md',EX/'custody-asset-bridge.php',EX/'qa'/'php_contract.php',EX/'qa'/'browser_gate.py',EX/'qa'/'build_evidence.py']
proof=sorted(x for x in OUT.iterdir() if x.is_file() and x.suffix in ('.png','.pdf','.json'))
paths=source+proof
manifest={'sprint':'R364','provenance':'local audited PHP/Chromium fixture, not WordPress, HTTP CSP or production','files':[{'path':str(x.relative_to(ROOT)),'sha256':hashlib.sha256(x.read_bytes()).hexdigest(),'bytes':x.stat().st_size} for x in paths]}
mdata=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode();payload={str(x.relative_to(ROOT)):x.read_bytes() for x in paths};payload['R364_MANIFEST.json']=mdata
archive=ROOT/'Apollo_R364_Evidence.zip'
for _ in range(2):
 with zipfile.ZipFile(archive,'w') as z:
  for name in sorted(payload):
   info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
   z.writestr(info,payload[name],compresslevel=9)
 digest=hashlib.sha256(archive.read_bytes()).hexdigest();print(archive,digest,len(payload))
