"""Reproducible ZIP: fixed timestamps, sorted paths, SHA-256 catalog and no timestamps inside payload."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]; QA=ROOT/'QA'
OUT=QA/'Apollo_R420_Local_Evidence.zip'
SOURCES=['README.md','staging-educator-source-lab.php','assets/educator-lab.css','qa/render_fixture.php','qa/test_contract.py','qa/browser_qa.py','qa/release_gate.py','qa/test_release_gate.py','qa/package_evidence.py']
RESULTS=['QA/source_tests.log','QA/browser_tests.log','QA/gate_tests.log','QA/browser_results.json','QA/chrome_accessibility_extract.json','QA/release_gate_result.json']
def build():
 data={n:(ROOT/n).read_bytes() for n in SOURCES+RESULTS}
 for p in sorted((QA/'screenshots').glob('*.png')):data[str(p.relative_to(ROOT))]=p.read_bytes()
 manifest={k:hashlib.sha256(v).hexdigest() for k,v in sorted(data.items())}
 data['QA/sha256_manifest.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
 with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name in sorted(data):
   inf=zipfile.ZipInfo(name,(1980,1,1,0,0,0));inf.compress_type=zipfile.ZIP_DEFLATED;inf.external_attr=(0o644<<16)
   z.writestr(inf,data[name],compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
 return hashlib.sha256(OUT.read_bytes()).hexdigest(),len(data)
if __name__=='__main__':print('sha256,entries',build())
