#!/usr/bin/env python3
"""Deterministic local evidence ZIP: read-only artifacts and SHA-256 manifest."""
import hashlib,json,zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[2]; q=root/'apollo-r398'/'QA'
files=[
 'apollo-r377/custody.json',
 'apollo-r384/assets/gallery.css',
 'apollo-r392/qa/semantic_custody.py',
 'apollo-r393/QA/local-php-fixture.html',
 'apollo-r393/qa/topology.py',
 'apollo-r394/qa/visibility_custody.py',
 'apollo-r395/assets/mobile-fit.css',
 'apollo-r397/staging-delivery-guard.php',
 'apollo-r398/staging-canonical-delivery.php',
 'apollo-r398/qa/contract.php',
 'apollo-r398/qa/enable.php',
 'apollo-r398/qa/reproduce_r397_gap.php',
 'apollo-r398/qa/browser.py',
 'apollo-r398/qa/package.py',
 'apollo-r398/README.md',
 'apollo-r398/QA/browser-results.json',
 'apollo-r398/QA/320.png','apollo-r398/QA/1440.png',
 'apollo-r398/QA/320-nojs.png','apollo-r398/QA/390-touch.png',
 'apollo-r398/QA/320-text4x.png',
]
for f in files:
 if not (root/f).is_file(): raise SystemExit(f'FAIL missing {f}')
manifest={'scope':'LOCAL QA ONLY; NOT INSTALLED WORDPRESS','source_files':{
 f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in files},
 'reviewed_github_base':'2268a2bcd4c6a07f3e1d423be2bfe44f4056bcdf',
 'genuine_axe':'NOT_RUN_NETWORK_UNAVAILABLE',
 'hosted_ci':'NOT_RUN','network_navigation':'BLOCKED_BY_ADMINISTRATOR',
 'release_allowed':False}
manifest_text=json.dumps(manifest,sort_keys=True,indent=2,ensure_ascii=False)+'\n';(q/'MANIFEST.json').write_text(manifest_text)
contents={f:(root/f).read_bytes() for f in files};contents['apollo-r398/QA/MANIFEST.json']=manifest_text.encode()
output=q/'Apollo_R398_Local_Evidence.zip'
def pack():
 with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name in sorted(contents):
   info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
   info.external_attr=0o100644<<16;info.create_system=3
   z.writestr(info,contents[name],compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
pack();first=hashlib.sha256(output.read_bytes()).hexdigest();pack();second=hashlib.sha256(output.read_bytes()).hexdigest()
assert first==second
print(json.dumps({'archive':str(output),'entries':len(contents),'sha256':first,'byte_identical_rebuild':True}))
