"""Deterministic, auditable R430 local artifact. No network access or GitHub mutations."""
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo
ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'QA'
OUTPUT=QA/'Apollo_R430_Local_Evidence.zip'
SOURCES=['README.md','staging-educator-case-lab.php','assets/educator-case-lab.css','qa/fixture.php','qa/test_contract.py','qa/browser_qa.py','qa/staging_acceptance.py','qa/package_evidence.py']
ARTIFACTS=['QA/contract_results.json','QA/browser_results.json']+['QA/screenshots/'+p.name for p in sorted((QA/'screenshots').glob('*.png'))]
files=sorted(SOURCES+ARTIFACTS)
manifest={'scope':'OFFLINE actual PHP source, not installed WP staging','parent_r429':{'php_git_blob':'c604bccf9873688ec1d9b64187d1a9a7fdcf89ac','css_git_blob':'15942f8ef27d82695c8d2af8bdc8a807396da33e'},'files':[{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),'bytes':(ROOT/p).stat().st_size} for p in files]}
items={'manifest.json':(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()}
items.update({p:(ROOT/p).read_bytes() for p in files})
def build(path):
    with ZipFile(path,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
        for name,body in sorted(items.items()):
            info=ZipInfo(name,date_time=(2026,11,17,0,0,0))
            info.compress_type=ZIP_DEFLATED;info.external_attr=0o644<<16
            z.writestr(info,body,compress_type=ZIP_DEFLATED,compresslevel=9)
build(OUTPUT)
proof=OUTPUT.with_name('Apollo_R430_Local_Evidence.second.zip')
build(proof)
assert OUTPUT.read_bytes()==proof.read_bytes(),'Determinism gate failed'
proof.unlink()
print('ZIP',OUTPUT,'entries',len(items),'bytes',OUTPUT.stat().st_size,'SHA256',hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),'double-build equal')
