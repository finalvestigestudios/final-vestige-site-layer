"""Deterministic source-and-QA archive; never claims CI or installed WP QA."""
from pathlib import Path
import hashlib, json, zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'QA'
SOURCES=['README.md','staging-evidence-notebook.php','assets/evidence-notebook.css','assets/evidence-notebook.js','qa/fixture.php','qa/test_contract.py','qa/browser_qa.py','qa/staging_acceptance.py','qa/package_evidence.py']
ARTIFACTS=['QA/fixture.html','QA/browser-report.json','QA/notes-test-output.txt']
ARTIFACTS += [str(p.relative_to(ROOT)) for p in sorted((OUT/'screenshots').glob('*.png'))]
FILES=sorted(SOURCES+ARTIFACTS)
assert all((ROOT/path).is_file() for path in FILES)
manifest={path:hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in FILES}
(OUT/'manifest.json').write_text(json.dumps({'source_sha256':{k:manifest[k] for k in SOURCES},'artifact_sha256':{k:manifest[k] for k in ARTIFACTS},'axe':'HOLD','staging':'HOLD','field_cwv':'NOT MEASURED'},indent=2,sort_keys=True)+'\n')
FILES.append('QA/manifest.json')
archive=OUT/'Apollo_R431_Local_Evidence.zip'

def pack(path):
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in sorted(FILES):
            info=zipfile.ZipInfo('apollo-r431/'+name,date_time=(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o644<<16
            z.writestr(info,(ROOT/name).read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
pack(archive)
second=OUT/'check-second.zip'
pack(second)
assert archive.read_bytes()==second.read_bytes(),'non-deterministic QA packaging'
second.unlink()
print(f'PASS: {len(FILES)} entries deterministic double build; SHA-256 {hashlib.sha256(archive.read_bytes()).hexdigest()}')
