#!/usr/bin/env python3
"""Deterministically package frozen R360 evidence. Regenerating browsers is a separate step."""
import hashlib,json,zipfile
from pathlib import Path
E=Path(__file__).resolve().parents[2]
OUT=E/'apollo-r360/QA'
DEST=E.parent/'Apollo_R360_Evidence.zip'
sources=[
 'apollo-r339/assets/chronology-rail.css','apollo-r339/chronology-rail.php',
 'apollo-r340/apollo-accession-gallery.php','apollo-r340/assets/accession-gallery.css',
 'apollo-r345/evidence-plate.css','apollo-r345/evidence-plate.php',
 'apollo-r347/assets/source-index.css','apollo-r347/assets/source-index.js','apollo-r347/source-index.php',
 'apollo-r348/assets/source-custody.css','apollo-r348/source-custody.php',
 'apollo-r349/source-policy.php','apollo-r350/integrity.php',
 'apollo-r355/postfire-ledger.css','apollo-r355/postfire-ledger.php',
 'apollo-r356/asset-bridge.php','apollo-r356/assets/print-proof.css',
 'apollo-r357/template-asset-bridge.php','apollo-r358/explicit-template-prehead.php',
 'apollo-r359/resolved-block-template-prehead.php',
 'apollo-r360/README.md','apollo-r360/qa/php_custody.php',
 'apollo-r360/qa/compact_browser.py','apollo-r360/qa/browser_acceptance.py',
 'apollo-r360/qa/build_evidence.py',
]
files=sorted([E/x for x in sources]+[x for x in OUT.iterdir() if x.is_file()])
manifest={'type':'Frozen R360 source and executed test evidence, NOT a production build','sha256':{str(x.relative_to(E)):hashlib.sha256(x.read_bytes()).hexdigest() for x in files}}
entries=[('R360_MANIFEST.json',(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode())]+[('experience2/'+str(x.relative_to(E)),x.read_bytes()) for x in files]
with zipfile.ZipFile(DEST,'w',compression=zipfile.ZIP_STORED) as archive:
 for path,data in sorted(entries):
  info=zipfile.ZipInfo(path,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_STORED;info.external_attr=(0o644<<16)
  archive.writestr(info,data)
print(json.dumps({'path':str(DEST),'files':len(entries),'sha256':hashlib.sha256(DEST.read_bytes()).hexdigest()}))
