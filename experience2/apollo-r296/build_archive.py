#!/usr/bin/env python3
"""Build a byte-stable release-HOLD evidence archive from fixed local QA outputs."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEST=Path('/mnt/data/apollo_r296/Apollo_R296_A.zip')
FILES=[
 'apollo-r281/apollo-source-experience.php',
 'apollo-r281/assets/apollo-source-experience.css',
 'apollo-r294/qa/local_http_fixture.php',
 'apollo-r295/qa/memo_custody_contract.php',
 'apollo-r296/README.md',
 'apollo-r296/build_archive.py',
 'apollo-r296/qa/php_cache_gate.py',
 'apollo-r296/qa/compact_source_contract.php',
 'apollo-r296/qa/compact_browser_contract.py',
 'apollo-r296/qa/artifact_browser_qa.py',
 'QA/r296-390-compact-nojs.png',
 'QA/r296-1440-compact-nojs.png',
 'QA/r296-390-print.pdf',
 'QA/r296-artifact-receipt.json',
 'QA/r296-php-cache-receipt.json',
]
manifest={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in FILES}
manifest_bytes=(json.dumps({'status':'HARD_HOLD','files_sha256':manifest},indent=2,sort_keys=True)+'\n').encode()
DEST.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(DEST,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for name, data in [('EVIDENCE-MANIFEST.json',manifest_bytes)]+[(p,(ROOT/p).read_bytes()) for p in FILES]:
  info=zipfile.ZipInfo(name,(2026,11,11,0,0,0))
  info.compress_type=zipfile.ZIP_DEFLATED
  info.external_attr=0o100644<<16
  z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print('archive',DEST,'sha256',hashlib.sha256(DEST.read_bytes()).hexdigest(),'payload_files',len(FILES))
