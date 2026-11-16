"""Deterministic, offline ZIP for reviewed source and executed QA evidence. Never contacts WordPress."""
from pathlib import Path
import hashlib, json, zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'QA'
FILES=['README.md','staging-provenance-guide.php','assets/provenance.css',
       'qa/render_fixture.php','qa/test_provenance.py','qa/test_browser.py','qa/package_evidence.py']
ARCHIVE=OUT/'Apollo_R417_Local_Evidence.zip'

def build():
    paths=[ROOT/p for p in FILES]
    paths += sorted((OUT/'screenshots').glob('*.png'))
    paths += [p for p in (OUT/'native_tests.log',OUT/'browser_tests.log',OUT/'browser_results.json') if p.exists()]
    assert all(p.exists() for p in paths),[str(p) for p in paths if not p.exists()]
    OUT.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(ARCHIVE,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for f in sorted(paths):
            data=f.read_bytes()
            item=zipfile.ZipInfo(str(f.relative_to(ROOT)).replace('\\','/'),date_time=(2026,11,16,0,0,0))
            item.compress_type=zipfile.ZIP_DEFLATED
            item.external_attr=0o100644<<16
            z.writestr(item,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return {'archive':str(ARCHIVE),'entries':len(paths),'sha256':hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()}

if __name__=='__main__':
    first=build();second=build()
    assert first==second
    print(json.dumps({'reproducible':True,**first},indent=2))
