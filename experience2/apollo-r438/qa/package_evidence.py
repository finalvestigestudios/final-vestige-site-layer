"""Deterministic archive: source, reports, captures, no self-inclusion and no timestamps."""
import hashlib,zipfile,json
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];QA=HERE/'QA';QA.mkdir(exist_ok=True)
source=sorted([p for p in HERE.rglob('*') if p.is_file() and 'QA/' not in p.relative_to(HERE).as_posix() and '__pycache__' not in str(p)])
evidence=sorted(p for p in QA.rglob('*') if p.is_file() and p.suffix in ('.json','.png') and p.name!='manifest.json')
paths=source+evidence
manifest={'files':{p.relative_to(HERE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
(QA/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
paths.append(QA/'manifest.json')
out=QA/'Apollo_R438_Reproducible_QA.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(paths):
  name=p.relative_to(HERE).as_posix();info=zipfile.ZipInfo(name,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'archive':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'entries':len(paths)}))
