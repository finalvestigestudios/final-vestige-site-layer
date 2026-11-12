#!/usr/bin/env python3
"""Build a deterministic Apollo R297 staging evidence zip after the browser QA run."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'Apollo_R297_Staging.zip'
FILES=[
 'apollo-r281/apollo-source-experience.php',
 'apollo-r281/assets/apollo-source-experience.css',
 'apollo-r294/qa/local_http_fixture.php',
 'apollo-r295/qa/memo_custody_contract.php',
 'apollo-r296/qa/php_cache_gate.py',
 'apollo-r296/qa/compact_source_contract.php',
 'apollo-r296/qa/compact_browser_contract.py',
 'apollo-r297/README.md',
 'apollo-r297/qa/deterministic_qa.py',
 'apollo-r297/build_archive.py',
 'QA/r297-390-double-nojs.png',
 'QA/r297-1440-double-nojs.png',
 'QA/r297-390-double-print.pdf',
 'QA/r297-deterministic-receipt.json',
]
manifest={'release':'HARD_HOLD','file_sha256':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in FILES}}
meta=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
with zipfile.ZipFile(DEST,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for name,data in [('EVIDENCE-MANIFEST.json',meta)]+[(n,(ROOT/n).read_bytes()) for n in FILES]:
  zi=zipfile.ZipInfo(name,(2026,11,11,0,0,0))
  zi.external_attr=0o100644<<16;zi.compress_type=zipfile.ZIP_DEFLATED
  z.writestr(zi,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(DEST,hashlib.sha256(DEST.read_bytes()).hexdigest(),len(FILES),'files')
