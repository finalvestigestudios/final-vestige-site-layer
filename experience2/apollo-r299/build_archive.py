#!/usr/bin/env python3
"""R299 deterministic staging QA archive, never a deployment artifact."""
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
files=[
 'apollo-r281/apollo-source-experience.php',
 'apollo-r281/assets/apollo-source-experience.css',
 'apollo-r294/qa/local_http_fixture.php',
 'apollo-r295/qa/memo_custody_contract.php',
 'apollo-r296/qa/compact_source_contract.php',
 'apollo-r296/qa/php_cache_gate.py',
 'apollo-r296/qa/compact_browser_contract.py',
 'apollo-r298/qa/disclosure_contract.py',
 'apollo-r299/qa/continue_cta_gate.py',
 'apollo-r299/README.md',
 'apollo-r299/build_archive.py',
]
# Independently executed QA adds images/PDF/measurement receipts if present.
files += sorted('QA/'+p.name for p in (root/'QA').glob('r299-*') if p.is_file())
manifest={p:{'bytes':(root/p).stat().st_size,'sha256':hashlib.sha256((root/p).read_bytes()).hexdigest()} for p in files}
out=root.parent.parent/'Apollo_R299_Evidence.zip'
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(files):
  info=zipfile.ZipInfo('experience2/'+p,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
  z.writestr(info,(root/p).read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
 info=zipfile.ZipInfo('EVIDENCE-MANIFEST.json',(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
 z.writestr(info,(json.dumps({'release':'R299','scope':'staging only','files':manifest},sort_keys=True,indent=2)+'\n').encode(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
with zipfile.ZipFile(out) as z:
 for p,d in manifest.items():assert hashlib.sha256(z.read('experience2/'+p)).hexdigest()==d['sha256']
print(json.dumps({'archive':str(out),'payload_files':len(files),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'manifest_verified':True},sort_keys=True))
