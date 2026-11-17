"""Stable evidence manifest and ZIP; stable file ordering, timestamps, compression metadata."""
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
import hashlib, json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'QA'/'Apollo_R428_Local_Evidence.zip'
files=[p for p in ROOT.rglob('*') if p.is_file() and p != OUT and '__pycache__' not in p.parts]
files=sorted(files, key=lambda p:p.relative_to(ROOT).as_posix())
manifest=[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in files]
(ROOT/'QA'/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
files=sorted([*files,ROOT/'QA'/'manifest.json'],key=lambda p:p.relative_to(ROOT).as_posix())
with ZipFile(OUT,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
    for file in files:
        info=ZipInfo(file.relative_to(ROOT).as_posix(),date_time=(2026,11,17,0,0,0))
        info.compress_type=ZIP_DEFLATED
        info.external_attr=(0o644<<16)
        z.writestr(info,file.read_bytes(),compress_type=ZIP_DEFLATED,compresslevel=9)
print('archive',OUT,'sha256',hashlib.sha256(OUT.read_bytes()).hexdigest(),'entries',len(files))
