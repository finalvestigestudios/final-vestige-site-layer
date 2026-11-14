#!/usr/bin/env python3
"""Create deterministic R358 evidence bundle from local source and existing upstream modules.
   NOT a production build, hosted CI receipt or assurance of live WordPress behavior."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'Apollo_R358_Evidence.zip'
EX=ROOT/'experience2'
paths=[p for p in (EX/'apollo-r358').rglob('*') if p.is_file() and not p.name.endswith('.zip') and p.name!='R358_MANIFEST.json']
for d in ('apollo-r339','apollo-r340','apollo-r345','apollo-r347','apollo-r348','apollo-r349','apollo-r350','apollo-r354','apollo-r355','apollo-r356','apollo-r357'):
 paths += [p for p in (EX/d).rglob('*') if p.is_file() and ('/QA/' not in str(p)) and ('/qa/' not in str(p))]
paths=sorted(set(paths),key=lambda p:p.relative_to(ROOT).as_posix())
files={p.relative_to(ROOT).as_posix():p.read_bytes() for p in paths}
manifest={'scope':'LOCAL reproducible R358 source and QA; not installed WordPress or production','files':{k:{'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()} for k,v in files.items()}}
files['R358_MANIFEST.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for name,data in sorted(files.items()):
  i=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o644<<16
  z.writestr(i,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'zip':str(OUT),'files':len(files),'zip_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest()},indent=2))
