#!/usr/bin/env python3
"""Pack reviewed local R381 evidence deterministically; not a release artifact."""
from pathlib import Path
import hashlib, json, zipfile
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'experience2/apollo-r381'
SOURCE=[
 'experience2/apollo-r381/atlas.php',
 'experience2/apollo-r381/assets/atlas.css',
 'experience2/apollo-r381/assets/atlas.js',
 'experience2/apollo-r381/qa/php_contract.php',
 'experience2/apollo-r381/qa/fixture.php',
 'experience2/apollo-r381/qa/browser.py',
 'experience2/apollo-r381/qa/package.py',
 'experience2/apollo-r381/README.md',
 'experience2/apollo-r377/source-role-desk.php',
 'experience2/apollo-r377/custody.json',
]
CAPTURES=['320-mobile','390-mobile','768-tablet','1440-desktop','1920-wide','320-nojs','390-touch','390-reduced','320-forced','320-root4x']
EVIDENCE=['experience2/apollo-r381/QA/'+n+'.png' for n in CAPTURES]+[
 'experience2/apollo-r381/QA/browser-results.json',
 'experience2/apollo-r381/QA/Apollo_R381_Print_Source_Dossier.pdf',
]
files=sorted(SOURCE+EVIDENCE)
checks={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files}
manifest={'schema':'fv.apollo.r381.local-evidence.v1','source_reference':'R377 SHA256-sealed 6-record custody','boundary':'LOCAL CHROMIUM FIXTURE; NOT STAGING / axe-core / deployed','files_sha256':checks}
manifest_bytes=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
output=BASE/'QA/Apollo_R381_Evidence.zip'
with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
 for name, data in [('MANIFEST.json',manifest_bytes)]+[(p,(ROOT/p).read_bytes()) for p in files]:
  item=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED;item.external_attr=0o644<<16
  archive.writestr(item,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'zip':str(output),'entries':len(files)+1,'sha256':hashlib.sha256(output.read_bytes()).hexdigest()}))
