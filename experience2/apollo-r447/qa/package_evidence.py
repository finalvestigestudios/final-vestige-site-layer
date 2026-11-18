"""Deterministic, source-manifested ZIP; no unreviewed paid or site actions."""
from pathlib import Path
import hashlib
import json
import zipfile
BASE=Path(__file__).resolve().parents[1]
OUT=BASE/'QA'
FILES=sorted(p for p in BASE.rglob('*') if p.is_file() and p!=OUT/'Apollo_R447_QA.zip' and p!=OUT/'source_checksums.json' and not '__pycache__' in p.parts and not p.name.endswith('.pyc'))
manifest={str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in FILES}
(OUT/'source_checksums.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
FILES=sorted(set(FILES+[OUT/'source_checksums.json']))
zip_path=OUT/'Apollo_R447_QA.zip'
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for path in FILES:
        info=zipfile.ZipInfo(str(path.relative_to(BASE)),date_time=(1980,1,1,0,0,0))
        info.external_attr=(0o644&0xffff)<<16
        info.compress_type=zipfile.ZIP_DEFLATED
        z.writestr(info,path.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'entries':len(FILES),'path':str(zip_path),'sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest()}))
