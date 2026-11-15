#!/usr/bin/env python3
"""Byte-stable source + review-evidence ZIP; does not deploy, publish or mutate WordPress."""
import hashlib, json, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
REVIEW=ROOT/'experience2/apollo-r382'
files=[
 'experience2/apollo-r377/custody.json',
 'experience2/apollo-r381/assets/atlas.js',
 'experience2/apollo-r382/README.md',
 'experience2/apollo-r382/qa/smoke.py',
 'experience2/apollo-r382/qa/package.py'
]
# Extended QA is opt-in and exists in the separately supplied review artifact, not required in a Git clone.
for p in ('qa/run.py','QA/results.json','QA/source-fixture.html'):
 if (REVIEW/p).is_file():files.append('experience2/apollo-r382/'+p)
files += ['experience2/apollo-r382/QA/'+p.name for p in sorted((REVIEW/'QA').glob('*.png'))]
files=sorted(set(files))
checks={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}
manifest=(json.dumps({'schema':'fv.apollo.r382.evidence.v1','files':checks},indent=2,sort_keys=True)+'\n').encode()
archive=REVIEW/'QA/Apollo_R382_Evidence.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for path in sorted(files+['R382_MANIFEST.json']):
  data=manifest if path=='R382_MANIFEST.json' else (ROOT/path).read_bytes()
  info=zipfile.ZipInfo(path,date_time=(1980,1,1,0,0,0))
  info.compress_type=zipfile.ZIP_DEFLATED
  info.external_attr=0o644<<16
  z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'files':len(files),'sha256_zip':hashlib.sha256(archive.read_bytes()).hexdigest(),'archive':str(archive)},indent=2))
