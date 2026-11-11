#!/usr/bin/env python3
"""Deterministic R286 Apollo evidence bundle; usage build_archive.py QA_DIR OUT.zip."""
from pathlib import Path
import hashlib,json,sys,zipfile
ROOT=Path(__file__).resolve().parents[2]
QA=Path(sys.argv[1]).resolve()
DEST=Path(sys.argv[2]).resolve()
selected=[
 'experience2/apollo-r281/apollo-source-experience.php',
 'experience2/apollo-r281/assets/apollo-source-experience.css',
 'experience2/apollo-r281/qa/committed_gate.py',
 'experience2/apollo-r285/verify_preflight.php',
 'experience2/apollo-r285/verify_print_export.py',
 'experience2/apollo-r286/verify_bounded_preflight.php',
 'experience2/apollo-r286/README.md',
 'experience2/apollo-r286/build_archive.py',
]
files={name:(ROOT/name).read_bytes() for name in selected}
for p in sorted(QA.rglob('*')):
 if p.is_file() and p.suffix.lower() in ('.png','.pdf','.json','.txt'):
  files['QA/'+p.relative_to(QA).as_posix()]=p.read_bytes()
assert 'QA/Browser/receipt.json' in files and 'QA/Print/receipt.json' in files
manifest={
 'format':'apollo-r286-evidence-manifest/v1',
 'source_ref':'R285 draft PR #2047; parent f40ef90ac7961248542626b7c09914327c0a6369',
 'release':'STAGING_HARD_HOLD',
 'files':{name:hashlib.sha256(blob).hexdigest() for name,blob in sorted(files.items())},
}
files['EVIDENCE-MANIFEST.json']=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
DEST.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(DEST,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for name,blob in sorted(files.items()):
  i=zipfile.ZipInfo(name,date_time=(2026,11,11,0,0,0))
  i.compress_type=zipfile.ZIP_DEFLATED
  i.external_attr=(0o644<<16)
  z.writestr(i,blob,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print('files',len(files),'zip_sha256',hashlib.sha256(DEST.read_bytes()).hexdigest())
