#!/usr/bin/env python3
"""Stable ZIP bytes; archive never includes itself or incidental filesystem metadata."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'QA/Apollo_R444_Local_QA.zip'
FILES=['README.md','CONVERSION_GATE.md','source_manifest.json','review_panel.php','assets/review-panel.css','assets/review-panel.js','qa/fixture.php','qa/test_contract.py','qa/browser_qa.py','qa/package_evidence.py','QA/browser_results.json']
FILES += ['QA/screenshots/'+p.name for p in sorted((ROOT/'QA/screenshots').glob('*.png'))]
assert len(set(FILES))==len(FILES)
manifest={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in FILES}
manifest_data=(json.dumps({'source_hashes':manifest,'important':'Local PHP-rendered Chromium. WordPress staging, axe, LCP/CLS NOT RUN.'},sort_keys=True,indent=2)+'\n').encode()
OUT.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for f in sorted(FILES):
    zi=zipfile.ZipInfo(f,date_time=(1980,1,1,0,0,0));zi.external_attr=(0o100644<<16);zi.compress_type=zipfile.ZIP_DEFLATED
    z.writestr(zi,(ROOT/f).read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
  zi=zipfile.ZipInfo('QA/hash_manifest.json',date_time=(1980,1,1,0,0,0));zi.external_attr=(0o100644<<16);zi.compress_type=zipfile.ZIP_DEFLATED
  z.writestr(zi,manifest_data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'path':str(OUT),'entries':len(FILES)+1,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'bytes':OUT.stat().st_size}))
