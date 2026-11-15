#!/usr/bin/env python3
"""Reproducible R386 source+QA archive; fixed timestamps, order and compression."""
import hashlib, json, pathlib, zipfile
root=pathlib.Path(__file__).resolve().parents[2]
out=root/'apollo-r386'/'QA'/'Apollo_R386_Evidence.zip'
files=[root/'apollo-r384'/'document-gallery.php',root/'apollo-r384'/'assets'/'gallery.css',
       root/'apollo-r377'/'custody.json',root/'apollo-r386'/'README.md']
files+=sorted((root/'apollo-r386'/'qa').glob('*.py'))
files+=sorted((root/'apollo-r386'/'qa').glob('*.php'))
files+=sorted(p for p in (root/'apollo-r386'/'QA').iterdir()
              if p.is_file() and p.suffix.lower() in ('.png','.pdf','.html','.json') and p.name!='MANIFEST.json')
files.sort(key=lambda p:str(p.relative_to(root)))
manifest={'scope':'local Chromium fixture R386, not WordPress staging or live','files':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
mfile=root/'apollo-r386'/'QA'/'MANIFEST.json';mfile.write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
files.append(mfile)
def build(path):
 with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(files,key=lambda p:str(p.relative_to(root))):
   info=zipfile.ZipInfo(str(p.relative_to(root)),date_time=(1980,1,1,0,0,0))
   info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=(0o644<<16)
   z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
build(out)
check=out.with_suffix('.rebuild.zip');build(check)
assert out.read_bytes()==check.read_bytes(),'non-deterministic package'
check.unlink()
print(json.dumps({'archive':str(out),'entry_count':len(files),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'identical_rebuild':True},indent=2))
