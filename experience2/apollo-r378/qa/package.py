#!/usr/bin/env python3
"""Create reproducible local evidence ZIP; does not publish/upload/deploy anything."""
from pathlib import Path
import hashlib,json,zipfile
BASE=Path(__file__).resolve().parents[3]
R=BASE/'experience2/apollo-r378'
U=BASE/'experience2/apollo-r377'
assert R.is_dir() and U.is_dir()
paths=[p for p in R.rglob('*') if p.is_file() and p.suffix not in ('.zip','.pyc') and '__pycache__' not in p.parts]
paths += [U/'assets/source-role.css', U/'custody.json', U/'source-role-desk.php']
paths=sorted(set(paths), key=lambda p:p.relative_to(BASE).as_posix())
manifest={str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
manifest_bytes=(json.dumps({'schema':'fv.apollo.r378.artifact.v1','files_sha256':manifest},sort_keys=True,indent=2)+'\n').encode()
dest=R/'Apollo_R378_Evidence.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name,data in [('R378_MANIFEST.json',manifest_bytes)]+[(str(p.relative_to(BASE)),p.read_bytes()) for p in paths]:
        info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
        info.external_attr=0o100644 << 16
        z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'zip':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
                  'entries':len(paths)+1},sort_keys=True))
