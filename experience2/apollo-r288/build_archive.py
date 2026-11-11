#!/usr/bin/env python3
"""Create a deterministic source+QA ZIP from fixed input bytes; never deploys."""
from pathlib import Path
import hashlib,json,sys,zipfile
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/apollo-r288.zip')
QA=Path(sys.argv[2] if len(sys.argv)>2 else '/tmp/fv-r288-browser')
RELS=['experience2/apollo-r281/apollo-source-experience.php',
      'experience2/apollo-r281/assets/apollo-source-experience.css',
      'experience2/apollo-r288/README.md',
      'experience2/apollo-r288/build_archive.py',
      'experience2/apollo-r288/qa/committed_browser_gate.py',
      'experience2/apollo-r288/qa/committed_php_gate.php']
files={rel:(ROOT/rel).read_bytes() for rel in RELS}
for path in sorted(QA.glob('*')):
    if path.is_file() and path.suffix.lower() in {'.json','.png','.pdf'}:
        files['QA/'+path.name]=path.read_bytes()
manifest={'release':'R288 staging HOLD', 'files':{p:hashlib.sha256(v).hexdigest() for p,v in sorted(files.items())},'claims':'Source-controlled staging and synthetic browser QA only; not installed WordPress or live conversion evidence'}
files['EVIDENCE-MANIFEST.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
OUT.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name,data in sorted(files.items()):
        info=zipfile.ZipInfo(name,date_time=(2026,11,11,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
        z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(f'R288 deterministic ZIP {OUT} sha256={hashlib.sha256(OUT.read_bytes()).hexdigest()} files={len(files)}')
