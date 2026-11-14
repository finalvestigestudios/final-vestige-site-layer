"""Build deterministic archive of frozen source and QA outputs (fixed ZIP metadata)."""
import hashlib,zipfile,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]; work=root.parent.parent; qa=root/'QA'
files=[f for f in root.rglob('*') if f.is_file() and f.name!='Apollo_R365_Evidence.zip']
files=sorted(files,key=lambda f: str(f.relative_to(work)))
manifest={'sprint':'R365','scope':'isolated DRAFT staging, not live','files':{str(f.relative_to(work)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}}
manifest_path=work/'R365_MANIFEST.json';manifest_path.write_text(json.dumps(manifest,indent=2)+'\n');files.append(manifest_path)
out=work/'Apollo_R365_Evidence.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for f in sorted(files,key=lambda f:str(f.relative_to(work))):
  info=zipfile.ZipInfo(str(f.relative_to(work)),(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
  z.writestr(info,f.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'archive':str(out),'files':len(files),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2))
