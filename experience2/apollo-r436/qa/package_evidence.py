"""Deterministic local evidence ZIP; no network, credentials or production writes."""
import json, hashlib, zipfile
from pathlib import Path
here=Path(__file__).resolve().parents[1]
qa=here/'QA';qa.mkdir(exist_ok=True)
source=[
 'README.md','OFFER_FUNNEL_QA.md','staging-source-proof.php','assets/source-proof.css',
 'qa/fixture.php','qa/test_contract.py','qa/browser_qa.py','qa/staging_acceptance.py','qa/package_evidence.py'
]
extras=['QA/contract.json','QA/browser.json','QA/fixture.html']
extras += sorted(str(p.relative_to(here)) for p in (qa/'screenshots').glob('*.png'))
paths=sorted(source+extras)
manifest={}
for rel in paths:
 payload=(here/rel).read_bytes()
 manifest[rel]={'sha256':hashlib.sha256(payload).hexdigest(),'bytes':len(payload)}
manifest_bytes=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
out=qa/'Apollo_R436_Local_QA_Evidence.zip'
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for rel in paths:
  info=zipfile.ZipInfo(rel,(1980,1,1,0,0,0))
  info.compress_type=zipfile.ZIP_DEFLATED
  info.external_attr=0o644<<16
  z.writestr(info,(here/rel).read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
 info=zipfile.ZipInfo('MANIFEST.json',(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
 z.writestr(info,manifest_bytes,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print('ZIP entries',len(paths)+1,'SHA-256',hashlib.sha256(out.read_bytes()).hexdigest())
