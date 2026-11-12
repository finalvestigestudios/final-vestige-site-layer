#!/usr/bin/env python3
"""Deterministic evidence ZIP for reviewed R300 bytes, no network or WP writes."""
import hashlib, json, zipfile
from pathlib import Path
here=Path(__file__).resolve()
root=here.parents[2]
site=here.parents[1]
qa=root/'QA'
out=root/'Apollo_R300_Evidence.zip'
sources=[site/'apollo-r281/apollo-source-experience.php',
         site/'apollo-r281/assets/apollo-source-experience.css',
         site/'apollo-r300/README.md', site/'apollo-r300/build_archive.py',
         site/'apollo-r300/qa/region_landmark_contract.py']
outputs=[qa/f'r300-{w}-nojs.png' for w in (320,390,768,1440,1920)]
outputs += [qa/'r300-390-print.pdf',qa/'r300-browser-receipt.json']
files=sorted(sources+outputs,key=lambda p: str(p.relative_to(root)))
for f in files:
 if not f.is_file(): raise SystemExit('MISSING '+str(f))
manifest={'sprint':'R300','scope':'LOCAL staging; not live or hosted',
          'files':{str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},
          'release_gate':'HARD HOLD: axe, WP, actual browser HTTP/CSP, screen reader, production CWV, editorial, founder'}
files_bytes={str(f.relative_to(root)):f.read_bytes() for f in files}
files_bytes['EVIDENCE-MANIFEST.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
 for name in sorted(files_bytes):
  info=zipfile.ZipInfo(name,(1980,1,1,0,0,0))
  info.compress_type=zipfile.ZIP_DEFLATED
  info.external_attr=0o644<<16
  archive.writestr(info,files_bytes[name],compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print('archive',out,'sha256',hashlib.sha256(out.read_bytes()).hexdigest(),'payloads',len(files))
