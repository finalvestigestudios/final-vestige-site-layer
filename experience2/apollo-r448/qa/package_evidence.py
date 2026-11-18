"""Reproducible ZIP: stable timestamps and canonical relative paths, no transient interpreter files."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'QA'/'Apollo_R448_Deterministic_QA.zip'
NAMES=['manifest.json','crosswalk.php','README.md','assets/crosswalk.css','assets/crosswalk.js','qa/fixture.php','qa/test_contract.py','qa/browser_qa.py','qa/staging_gate.py','qa/package_evidence.py','QA/browser_results.json']
NAMES+=['QA/'+p.relative_to(ROOT/'QA').as_posix() for p in sorted((ROOT/'QA'/'screenshots').glob('*.png'))]
NAMES=sorted(set(NAMES));OUT.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as zipout:
    for rel in NAMES:
        data=(ROOT/rel).read_bytes();info=zipfile.ZipInfo(rel,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o644<<16);zipout.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'path':str(OUT),'entries':len(NAMES),'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest()}))
