"""Deterministic local evidence zip; no recursive self-ingestion or runtime timestamps."""
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parents[1]
QA=HERE/'QA'
SOURCE=['README.md','OFFER_FUNNEL_QA.md','source_catalog.json','staging-photo-custody.php','assets/photo-custody.css','qa/fixture.php','qa/test_contract.py','qa/browser_qa.py','qa/staging_acceptance.py','qa/package_evidence.py']
ARTIFACTS=SOURCE+['QA/contract.json','QA/browser.json']+[str(x.relative_to(HERE)) for x in sorted((QA/'screenshots').glob('*.png'))]
manifest={x:sha256((HERE/x).read_bytes()).hexdigest() for x in ARTIFACTS}
manifest_data=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
contents={x:(HERE/x).read_bytes() for x in ARTIFACTS}
contents['QA/source-sha256.json']=manifest_data

def build(dest):
 with ZipFile(dest,'w',ZIP_DEFLATED,compresslevel=9) as z:
  for name in sorted(contents):
   info=ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=ZIP_DEFLATED;info.external_attr=0o644<<16
   z.writestr(info,contents[name],compress_type=ZIP_DEFLATED,compresslevel=9)
out=QA/'Apollo_R435_Reproducible_Evidence.zip';tmp=QA/'R435_check.zip'
build(out);build(tmp)
a=sha256(out.read_bytes()).hexdigest();b=sha256(tmp.read_bytes()).hexdigest();tmp.unlink()
assert a==b,'deterministic archive mismatch'
(QA/'archive-sha256.txt').write_text(a+'  '+out.name+'\n')
print('ZIP',len(contents),'entries SHA-256',a,'byte-identical double build')
