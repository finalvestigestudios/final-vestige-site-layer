#!/usr/bin/env python3
"""R298 deterministic release-evidence archive (not deployment package)."""
import hashlib, json, zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
files=[
 'apollo-r281/apollo-source-experience.php',
 'apollo-r281/assets/apollo-source-experience.css',
 'apollo-r296/qa/php_cache_gate.py',
 'apollo-r294/qa/local_http_fixture.php',
 'apollo-r295/qa/memo_custody_contract.php',
 'apollo-r296/qa/compact_source_contract.php',
 'apollo-r296/qa/compact_browser_contract.py',
 'apollo-r298/qa/disclosure_contract.py',
 'apollo-r298/qa/artifact_qa.py',
 'apollo-r298/README.md',
 'apollo-r298/build_archive.py',
 'QA/r298-320-nojs.png','QA/r298-390-nojs.png','QA/r298-768-nojs.png',
 'QA/r298-1440-nojs.png','QA/r298-1920-nojs.png',
 'QA/r298-390-evidence-print.pdf','QA/r298-receipt.json',
 'QA/r297-negative-control.txt',
]
manifest={f:{'sha256':hashlib.sha256((root/f).read_bytes()).hexdigest(),'bytes':(root/f).stat().st_size} for f in files}
manifest_bytes=(json.dumps({'release':'R298','scope':'staging, no production authorization','files':manifest},indent=2,sort_keys=True)+'\n').encode()
out=root.parent/'Apollo_R298_Evidence.zip'
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for name in sorted(files):
  data=(root/name).read_bytes()
  arcname='experience2/'+name
  info=zipfile.ZipInfo(arcname,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
  z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
 info=zipfile.ZipInfo('EVIDENCE-MANIFEST.json',(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
 z.writestr(info,manifest_bytes,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
with zipfile.ZipFile(out) as z:
 for filename,meta in manifest.items():
  arcname='experience2/'+filename
  assert hashlib.sha256(z.read(arcname)).hexdigest()==meta['sha256']
print(json.dumps({'archive':str(out),'payload_files':len(files),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'manifest_verified':True},sort_keys=True))
