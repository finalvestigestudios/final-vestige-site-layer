#!/usr/bin/env python3
"""Build bitwise reproducible R469 source & QA evidence ZIP (no clock-derived fields)."""
from pathlib import Path
import json,hashlib,zipfile,sys
ROOT=Path(__file__).resolve().parents[1]
OUTPUT=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/mnt/data/Apollo_R469_Source_Custody_QA.zip')
FILES=['apollo_rights_gallery.php','evidence_plates.php','assets/gallery.css','assets/gallery.js',
       'qa/r466_integrity_gate.py','qa/r467_contract_gate.py','qa/r468_custody_gate.py','qa/r468_browser_gate.py',
       'qa/r469_claim_custody_gate.py','qa/r469_browser_gate.py','qa/r469_archive_gate.py',
       'R469_RELEASE_EVIDENCE.md',
       'QA/r469/390-js0.png','QA/r469/390-js1.png','QA/r469/1440-js0.png','QA/r469/1440-js1.png',
       'QA/r469/390-after-filter-print.pdf','QA/r469/results.json']
manifest={'release':'R469','status':'LOCAL_QA_PASS_HOSTED_HOLD','predecessor_sha':'1a0ad3ad08c818a8cd5ab28a66265e4a67529c58',
          'files':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in FILES}}
blobs={'MANIFEST.json':(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()}
blobs.update({name:(ROOT/name).read_bytes() for name in FILES})
OUTPUT.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(OUTPUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9,strict_timestamps=True) as z:
 for name,contents in sorted(blobs.items()):
  info=zipfile.ZipInfo(name,date_time=(2026,11,18,0,0,0))
  info.compress_type=zipfile.ZIP_DEFLATED
  info.external_attr=0o644<<16
  info.create_system=3
  z.writestr(info,contents,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
with zipfile.ZipFile(OUTPUT) as z:
 assert z.namelist()==sorted(blobs)
 for name,sha in manifest['files'].items():assert hashlib.sha256(z.read(name)).hexdigest()==sha
print(f'{OUTPUT} SHA256={hashlib.sha256(OUTPUT.read_bytes()).hexdigest()} entries={len(blobs)}')
