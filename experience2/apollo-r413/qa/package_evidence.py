#!/usr/bin/env python3
"""Deterministic local QA ZIP; no network or third-party copies."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'QA'
FILES=['README.md','staging-evidence-plate.php','assets/evidence-plate.css','qa/render_fixture.php','qa/test_contract.php','qa/test_browser.py','qa/package_evidence.py','QA/fixture.html','QA/php_results.txt','QA/browser_log.txt','QA/browser_results.json']
FILES += sorted('QA/screenshots/'+p.name for p in (QA/'screenshots').glob('*.png'))
FILES=sorted(set(FILES))
SHA={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in FILES}
manifest=json.dumps({'file_sha256':SHA,'qa_scope':'local PHP output + Playwright set_content; no navigated HTTP/axe/LCP/CLS','release':'HARD HOLD'},sort_keys=True,indent=2).encode()+b'\n'
archive=QA/'Apollo_R413_Local_Evidence.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_STORED) as z:
    for p in FILES:
        meta=zipfile.ZipInfo('apollo-r413/'+p,date_time=(2026,11,16,0,0,0));meta.compress_type=zipfile.ZIP_STORED;meta.external_attr=0o644<<16
        z.writestr(meta,(ROOT/p).read_bytes())
    meta=zipfile.ZipInfo('apollo-r413/QA/SHA256_MANIFEST.json',date_time=(2026,11,16,0,0,0));meta.compress_type=zipfile.ZIP_STORED;meta.external_attr=0o644<<16
    z.writestr(meta,manifest)
(QA/'SHA256_MANIFEST.json').write_bytes(manifest)
print('files',len(FILES)+1,'sha256',hashlib.sha256(archive.read_bytes()).hexdigest())