"""Reproducible archive with file hashes and no wall-clock timestamps."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'QA'
OUTPUT=QA/'Apollo_R419_Local_Evidence.zip'
SOURCE=['README.md','staging-evidence-concordance.php','assets/concordance.css','qa/render_fixture.php','qa/test_contract.py','qa/browser_qa.py','qa/release_gate.py','qa/test_release_gate.py','qa/package_evidence.py']
RESULTS=['QA/php_contract.log','QA/release_gate_tests.log','QA/browser_test.log','QA/browser_results.json','QA/chrome_accessibility_extract.json','QA/release_gate_result.json']
def build():
    files={rel:(ROOT/rel).read_bytes() for rel in SOURCE+RESULTS}
    for p in sorted((QA/'screenshots').glob('*.png')):files[str(p.relative_to(ROOT))]=p.read_bytes()
    manifest={'schema':1,'boundary':'Local PHP-built fixture, not installed WordPress; no axe, navigated LCP/CLS or verified revenue',
              'files':{rel:{'sha256':hashlib.sha256(content).hexdigest(),'bytes':len(content)} for rel,content in sorted(files.items())}}
    files['QA/manifest.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
    with zipfile.ZipFile(OUTPUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for rel,content in sorted(files.items()):
            info=zipfile.ZipInfo(rel,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
            z.writestr(info,content,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),len(files)
if __name__=='__main__':print(build())
