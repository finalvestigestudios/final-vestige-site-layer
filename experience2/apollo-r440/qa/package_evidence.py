"""Deterministic, self-excluding archive of source, reports and image evidence."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];QA=ROOT/'QA';QA.mkdir(exist_ok=True)
inputs=sorted(p for p in ROOT.rglob('*') if p.is_file() and 'QA/' not in p.relative_to(ROOT).as_posix() and '__pycache__' not in str(p))
inputs+=sorted(p for p in QA.rglob('*') if p.is_file() and p.suffix in ('.json','.png') and p.name!='manifest.json')
manifest={'files':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}}
(QA/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
inputs.append(QA/'manifest.json');out=QA/'Apollo_R440_Reproducible_Local_QA.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(inputs):
  arc=p.relative_to(ROOT).as_posix();info=zipfile.ZipInfo(arc,(1980,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
  z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'archive':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'entries':len(inputs)}))
