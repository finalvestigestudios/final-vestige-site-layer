#!/usr/bin/env python3
"""Deterministic local ZIP + sorted hash manifest, no network or staged writes."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'QA';QA.mkdir(exist_ok=True)
OUT=QA/'Apollo_R411_Local_Evidence.zip'
files=[ROOT/p for p in ('README.md','staging-source-drawer.php','assets/source-drawer.css','qa/render_fixture.php','qa/test_php.php','qa/test_browser.py','qa/package_evidence.py')]
files += sorted((QA/'screenshots').glob('*.png'))
files += [QA/p for p in ('browser_report.json','accessibility_roles.json','php_test_log.txt','browser_test_log.txt')]
assert all(p.is_file() for p in files)
manifest={'schema':1,'source':'Local real PHP + in-memory Chromium fixture; not installed WordPress','files':[
    {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(files)]}
manifest_bytes=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
(QA/'sha256_manifest.json').write_bytes(manifest_bytes)
def package():
    with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(files):
            i=zipfile.ZipInfo(str(p.relative_to(ROOT)),date_time=(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o644 << 16
            z.writestr(i,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
        i=zipfile.ZipInfo('QA/sha256_manifest.json',date_time=(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o644 << 16
        z.writestr(i,manifest_bytes,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
package();a=OUT.read_bytes();package();b=OUT.read_bytes();assert a==b
print('files',len(files)+1,'ZIP SHA256',hashlib.sha256(a).hexdigest(),'byte_identical',True)
