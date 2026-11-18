#!/usr/bin/env python3
"""Deterministic, stable-timestamp archive of R452 source+locally produced evidence."""
from pathlib import Path
import hashlib, zipfile, json
base=Path(__file__).resolve().parents[1]
files=[x for x in base.rglob('*') if x.is_file() and x.name!='Apollo_R452_Local_QA.zip' and '__pycache__' not in x.parts]
files.sort(key=lambda p:p.relative_to(base).as_posix())
out=base/'QA/Apollo_R452_Local_QA.zip'
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as zipf:
    for p in files:
        zi=zipfile.ZipInfo(p.relative_to(base).as_posix(),date_time=(1980,1,1,0,0,0))
        zi.external_attr=(0o644<<16);zi.compress_type=zipfile.ZIP_DEFLATED
        zipf.writestr(zi,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'entries':len(files),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'path':str(out)},sort_keys=True))
