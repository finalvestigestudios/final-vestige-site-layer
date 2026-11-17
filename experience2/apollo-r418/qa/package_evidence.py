"""Create reproducible, hash-manifested QA ZIP from fixed source/log/screenshot inputs."""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'QA'
OUTPUT=QA/'Apollo_R418_Local_Evidence.zip'
SOURCES=['README.md','staging-chronology-bridge.php','assets/chronology-bridge.css',
         'qa/render_fixture.php','qa/test_contract.py','qa/test_browser.py',
         'qa/release_gate.py','qa/test_release_gate.py','qa/package_evidence.py']
RESULTS=['QA/php_contract.log','QA/release_gate_tests.log','QA/browser_test.log',
         'QA/browser_results.json','QA/release_gate_result.json']

def build():
    candidates=[ROOT/p for p in SOURCES+RESULTS]+sorted((QA/'screenshots').glob('*.png'))
    files={str(p.relative_to(ROOT)):p.read_bytes() for p in candidates}
    manifest={key:{'sha256':hashlib.sha256(value).hexdigest(),'bytes':len(value)} for key,value in sorted(files.items())}
    files['QA/manifest.json']=(json.dumps({'schema':1,'notice':'Offline local fixtures only; staging/axe/LCP/CLS unverified',
         'files':manifest},indent=2,sort_keys=True)+'\n').encode()
    def output():
        with zipfile.ZipFile(OUTPUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for name,data in sorted(files.items()):
                info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED
                info.external_attr=0o644<<16
                z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
        return hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    a=output();b=output();assert a==b
    print(json.dumps({'sha256':a,'entries':len(files),'byte_identical_double_build':True,'size':OUTPUT.stat().st_size}))
    return a

if __name__=='__main__':build()
