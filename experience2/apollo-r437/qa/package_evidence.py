"""Deterministic evidence and reviewed source ZIP, no transient metadata or secrets."""
import hashlib, json, zipfile
from pathlib import Path
here=Path(__file__).resolve().parents[1]
qa=here/'QA';qa.mkdir(exist_ok=True)
source=['README.md','OFFER_FUNNEL_QA.md','staging-chronology-audit.php','assets/chronology-audit.css','assets/chronology-audit.js','qa/fixture.php','qa/test_contract.py','qa/browser_qa.py','qa/staging_acceptance.py','qa/package_evidence.py']
evidence=['QA/contract.json','QA/browser.json']+[str(p.relative_to(here)) for p in sorted((qa/'screenshots').glob('*.png'))]
files=source+evidence
assert all((here/p).is_file() for p in files)
manifest={p:hashlib.sha256((here/p).read_bytes()).hexdigest() for p in files}
(qa/'sha256-manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
archive=qa/'Apollo_R437_Reproducible_Local_QA.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(files+['QA/sha256-manifest.json']):
  info=zipfile.ZipInfo(p,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
  z.writestr(info,(here/p).read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'source_files':len(source),'entries':len(files)+1,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'size_bytes':archive.stat().st_size}))
