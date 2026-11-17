#!/usr/bin/env python3
"""Deterministic local evidence bundle; snapshots are offline fixture evidence only."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[1]
keep=['README.md','staging-research-desk-bridge.php','assets/bridge.css','qa/render_fixture.php','qa/test_contract.php','qa/test_browser.py','qa/package_evidence.py','QA/fixture.html','QA/browser-results.json','QA/php-test.log','QA/php-lint.log','QA/navigation-blocker.txt']
keep += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'QA/screenshots').glob('*.png'))]
manifest={key:hashlib.sha256((ROOT/key).read_bytes()).hexdigest() for key in keep}
(ROOT/'QA/sha256-manifest.json').write_text(json.dumps({'schema':'r423-offline-v1','files':manifest,'release':'HARD_HOLD'},indent=2)+'\n')
keep.append('QA/sha256-manifest.json')
zip_path=ROOT/'QA/Apollo_R423_Local_Evidence.zip'
with ZipFile(zip_path,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
    for key in sorted(keep):
        info=ZipInfo(key,date_time=(1980,1,1,0,0,0))
        info.external_attr=0o644<<16
        info.compress_type=ZIP_DEFLATED
        z.writestr(info,(ROOT/key).read_bytes(),compress_type=ZIP_DEFLATED,compresslevel=9)
print(f'{len(keep)} entries; sha256={hashlib.sha256(zip_path.read_bytes()).hexdigest()}')
