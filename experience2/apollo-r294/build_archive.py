#!/usr/bin/env python3
"""Deterministic local distribution of R294 tested bytes (no secrets/network)."""
import hashlib, json, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILES=[
 'apollo-r281/apollo-source-experience.php',
 'apollo-r281/assets/apollo-source-experience.css',
 'apollo-r294/README.md',
 'apollo-r294/build_archive.py',
 'apollo-r294/qa/verify_r294.py',
 'apollo-r294/qa/php_cache_gate.py',
 'apollo-r294/qa/local_http_fixture.php',
 'QA/r294-php-cache-receipt.json',
 'QA/r294-release-receipt.json',
 'QA/r294-390-nojs.png',
 'QA/r294-1440-nojs.png'
]
manifest={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in FILES}
payloads={'EVIDENCE-MANIFEST.json':(json.dumps({'files':manifest,'status':'HARD HOLD — local QA only'},sort_keys=True,indent=2)+'\n').encode()}
payloads.update({p:(ROOT/p).read_bytes() for p in FILES})
output=ROOT/'Apollo_R294_A.zip'
with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for path,data in sorted(payloads.items()):
  info=zipfile.ZipInfo(path,(2026,11,11,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
  info.external_attr=(0o100644<<16)
  z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(output,hashlib.sha256(output.read_bytes()).hexdigest(),len(payloads),'files')
