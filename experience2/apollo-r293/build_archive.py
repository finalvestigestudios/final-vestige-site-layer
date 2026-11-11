#!/usr/bin/env python3
"""Build immutable deterministic local QA ZIP. No network or CMS writes."""
from pathlib import Path
import hashlib, zipfile, json, sys
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/Apollo_R293.zip')
qa=Path(sys.argv[2] if len(sys.argv)>2 else '/tmp/apollo-r293-gate')
items=[
  ROOT/'apollo-r281/apollo-source-experience.php',
  ROOT/'apollo-r281/assets/apollo-source-experience.css',
  ROOT/'apollo-r293/qa/release_gate.py',
  ROOT/'apollo-r293/README.md',
  ROOT/'apollo-r293/build_archive.py'
]
items+=sorted(p for p in qa.rglob('*') if p.is_file())
data={('QA/'+p.relative_to(qa).as_posix() if p.is_relative_to(qa) else str(p.relative_to(ROOT))):p.read_bytes() for p in items}
manifest={'files':{k:hashlib.sha256(v).hexdigest() for k,v in sorted(data.items())},'release':'HARD_HOLD','field_metrics':'UNVERIFIED'}
data['EVIDENCE-MANIFEST.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
OUT.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name,blob in sorted(data.items()):
        info=zipfile.ZipInfo(name,date_time=(2026,11,11,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o644<<16)
        z.writestr(info,blob,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(OUT,hashlib.sha256(OUT.read_bytes()).hexdigest(),len(data))
