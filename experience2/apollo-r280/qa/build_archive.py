#!/usr/bin/env python3
"""Deterministic R280 source + QA archive; no file modification or network."""
import hashlib,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
DEST=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/apollo-r280-evidence.zip')
QA=Path(sys.argv[2]) if len(sys.argv)>2 else None
SRC=['experience2/apollo-r277/apollo-review-shortcode.php',
     'experience2/apollo-r273/review-custody.php',
     'experience2/apollo-r273/assets/review-custody.css',
     'experience2/apollo-r277/qa/wp_contract_gate.php',
     'experience2/apollo-r280/README.md',
     'experience2/apollo-r280/qa/pending_contract_gate.php',
     'experience2/apollo-r280/qa/browser_pending_gate.py',
     'experience2/apollo-r280/qa/build_archive.py']
files={name:(ROOT/name).read_bytes() for name in SRC}
if QA:
 for name in ['browser_receipt.json','php_receipt.json','390-nojs.png','1440-nojs.png']:
  files['QA/'+name]=(QA/name).read_bytes()
DEST.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(DEST,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for name,data in sorted(files.items()):
  info=zipfile.ZipInfo(name,(1980,1,1,0,0,0))
  info.compress_type=zipfile.ZIP_DEFLATED
  info.external_attr=0o100644<<16
  z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print('R280 archive',len(files),'files sha256',hashlib.sha256(DEST.read_bytes()).hexdigest())
