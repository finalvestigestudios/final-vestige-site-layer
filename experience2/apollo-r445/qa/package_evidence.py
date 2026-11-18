#!/usr/bin/env python3
"""Deterministic, local-only evidence ZIP: no wall clock metadata or network uploads."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT.parent/'apollo-r444'
OUT=ROOT/'QA';OUT.mkdir(exist_ok=True)
source_paths=[ROOT/'README.md',ROOT/'CONVERSION_CONTRACT.md',ROOT/'bridge.php',ROOT/'qa/fixture.php',ROOT/'qa/test_bridge.py',ROOT/'qa/browser_qa.py',ROOT/'qa/package_evidence.py']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest={'stage':'LOCAL_PHP_AND_CHROMIUM_ONLY','release':'HARD_HOLD','source_files':{str(p.relative_to(ROOT)):sha(p) for p in source_paths},'upstream_R444':{str(p.relative_to(PARENT)):sha(p) for p in [PARENT/'review_panel.php',PARENT/'source_manifest.json',PARENT/'assets/review-panel.css',PARENT/'assets/review-panel.js']},'screenshots':{p.name:sha(p) for p in sorted((OUT/'screenshots').glob('*.png'))},'axe':'NOT_RUN','staging':'NOT_RUN','lcp_cls':'NOT_RUN'}
(OUT/'custody.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
files=source_paths+[OUT/'custody.json',OUT/'browser_results.json']+sorted((OUT/'screenshots').glob('*.png'))
zip_path=OUT/'Apollo_R445_Deterministic_Local_QA.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for f in sorted(files,key=lambda f:str(f.relative_to(ROOT))):
        item=zipfile.ZipInfo(str(f.relative_to(ROOT)).replace('\\','/'),(1980,1,1,0,0,0))
        item.compress_type=zipfile.ZIP_DEFLATED;item.external_attr=0o644<<16
        z.writestr(item,f.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(f'{len(files)} files, sha256={sha(zip_path)} {zip_path}')
