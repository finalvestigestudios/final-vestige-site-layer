#!/usr/bin/env python3
"""R285 deterministic review bundle builder. Usage: python build_archive.py QA_DIR output.zip"""
import hashlib,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
QA=Path(sys.argv[1]).resolve()
DEST=Path(sys.argv[2]).resolve()
selected=[
 'experience2/apollo-r281/apollo-source-experience.php',
 'experience2/apollo-r281/assets/apollo-source-experience.css',
 'experience2/apollo-r281/qa/committed_gate.py',
 'experience2/apollo-r285/verify_preflight.php',
 'experience2/apollo-r285/verify_print_export.py',
 'experience2/apollo-r285/build_archive.py',
]
files={name:(ROOT/name).read_bytes() for name in selected}
for p in sorted(QA.rglob('*')):
 if p.is_file() and p.suffix in ('.png','.pdf','.json','.txt'):
  files['QA/'+p.relative_to(QA).as_posix()]=p.read_bytes()
assert 'QA/Browser/receipt.json' in files
assert 'QA/Print/receipt.json' in files
manifest={'format':'apollo-r285-evidence-manifest/v1',
 'source_ref':'R284 draft PR #2041, exact head 1acd3c652254d2f25486112796f307bc55a76503',
 'files':{name:hashlib.sha256(content).hexdigest() for name,content in sorted(files.items())},
 'release':'STAGING_HARD_HOLD'}
files['EVIDENCE-MANIFEST.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
DEST.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(DEST,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as out:
 for name,content in sorted(files.items()):
  i=zipfile.ZipInfo(name,date_time=(2026,11,11,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED
  i.external_attr=0o644<<16
  out.writestr(i,content,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print('Files:',len(files),'ZIP SHA256:',hashlib.sha256(DEST.read_bytes()).hexdigest())
