"""Package reproducible frozen R368 source + local Chromium evidence (staging only).
This freezes existing browser artifacts. Re-rendering screenshots/PDF may change bytes.
"""
from pathlib import Path
import hashlib, json, zipfile
ROOT=Path(__file__).resolve().parents[3]
DEST=ROOT/'Apollo_R368_Evidence.zip'
paths=[
    'experience2/apollo-r365/chrono-rail.php',
    'experience2/apollo-r365/assets/chrono-rail.css',
    'experience2/apollo-r367/sealed-chronology.php',
    'experience2/apollo-r367/assets/sequence-gate.css',
]
paths += [p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'experience2/apollo-r368').rglob('*'))
          if p.is_file() and p.suffix in ('.css','.php','.py','.md','.json','.png','.pdf')]
paths=sorted(set(paths))
manifest={'scope':'R368 read-only staged Apollo root-font/reflow fix; not production or rights clearance',
   'paths':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
   'qa':'11 local Playwright Chromium contexts; genuine axe, installed WordPress, HTTP/CSP and CI pending'}
entries={'R368_MANIFEST.json':(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()}
for p in paths: entries[p]=(ROOT/p).read_bytes()
with zipfile.ZipFile(DEST,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name,raw in sorted(entries.items()):
        info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
        info.external_attr=0o644 << 16
        z.writestr(info,raw,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'archive':str(DEST),'files':len(entries),'sha256':hashlib.sha256(DEST.read_bytes()).hexdigest()}))
