#!/usr/bin/env python3
"""Stable-byte R399 evidence archive; no network, no WordPress content writes."""
from pathlib import Path
import hashlib,zipfile,json
root=Path(__file__).resolve().parents[2]
q=root/'apollo-r399'/'QA';q.mkdir(exist_ok=True)
rel=[
'apollo-r377/custody.json','apollo-r384/assets/gallery.css',
'apollo-r392/qa/semantic_custody.py','apollo-r393/QA/local-php-fixture.html',
'apollo-r393/qa/topology.py','apollo-r394/qa/visibility_custody.py',
'apollo-r395/assets/mobile-fit.css','apollo-r398/staging-canonical-delivery.php',
'apollo-r399/README.md','apollo-r399/staging-final-tag-guard.php',
'apollo-r399/qa/print_gate.php','apollo-r399/qa/enable_print_gate.php',
'apollo-r399/qa/reproduce_r398_gap.php','apollo-r399/qa/tag_fixture.php',
'apollo-r399/qa/browser.py','apollo-r399/qa/package.py',
'apollo-r399/QA/browser-results.json',
'apollo-r399/QA/320.png','apollo-r399/QA/1440.png',
'apollo-r399/QA/320-nojs.png','apollo-r399/QA/390-touch.png',
'apollo-r399/QA/320-text4x.png',
]
for f in rel:
 if not (root/f).is_file():raise SystemExit('HOLD missing '+f)
sha={f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in rel}
manifest={'scope':'LOCAL PHP+CHROMIUM FIXTURE ONLY, NO STAGING',
 'files_sha256':sha,'base_git_commit':'8ec7b42993bc22fa77de5e9cc33182a50848995a',
 'axe_core':'NOT RUN','installed_wordpress':'NOT RUN',
 'actual_http_csp_redirects':'NOT RUN','native_400_percent_browser_zoom':'NOT RUN',
 'hosted_ci':'NOT VERIFIED','commercial_conversion':'NOT COMPUTABLE',
 'release_allowed':False}
contents={f:(root/f).read_bytes() for f in rel}
contents['apollo-r399/QA/MANIFEST.json']=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
(q/'MANIFEST.json').write_bytes(contents['apollo-r399/QA/MANIFEST.json'])
out=q/'Apollo_R399_Local_Evidence.zip'
def build():
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name in sorted(contents):
   info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
   info.create_system=3;info.external_attr=0o100644<<16
   z.writestr(info,contents[name],compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
build();a=hashlib.sha256(out.read_bytes()).hexdigest();build();b=hashlib.sha256(out.read_bytes()).hexdigest();assert a==b
print(json.dumps({'entries':len(contents),'sha256':a,'double_build_identical':True,'artifact':str(out)}))
