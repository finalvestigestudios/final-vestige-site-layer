#!/usr/bin/env python3
"""Deterministic local QA archive: fixed timestamps, sorted manifest, no account/credentials."""
from pathlib import Path
import hashlib, json, zipfile
ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'QA'
OUTPUT=QA/'Apollo_R414_Local_Evidence.zip'
FILES=[ROOT/p for p in ['README.md','staging-archive-gallery.php','assets/archive-gallery.css','qa/render_fixture.php','qa/test_php.php','qa/test_browser.py','qa/package_evidence.py']]
FILES+=sorted((QA/'screenshots').glob('*.png'))
FILES.append(QA/'browser_results.json')
manifest={'run':'R414','fixture_kind':'PHP-rendered, Playwright set_content (not navigated HTTP)', 'axe':'NOT RUN', 'LCP':'NOT MEASURED', 'CLS':'NOT MEASURED', 'WordPress':'NOT INSTALLED', 'release':'HARD HOLD', 'entries':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in FILES}}
content=(json.dumps(manifest,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
for _ in range(2):
    with zipfile.ZipFile(OUTPUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for f in FILES:
            info=zipfile.ZipInfo(str(f.relative_to(ROOT)),date_time=(2026,11,16,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(0o644 << 16)
            z.writestr(info,f.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
        info=zipfile.ZipInfo('QA/MANIFEST.json',date_time=(2026,11,16,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o644<<16)
        z.writestr(info,content,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    digest=hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    if _==0:first=digest
    else:assert digest==first,'ZIP is nondeterministic'
print('Archive:',OUTPUT,'entries',len(FILES)+1,'SHA256',digest)
