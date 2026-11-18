#!/usr/bin/env python3
"""Byte-identical R458 reproducible source and offline QA archive; no network or publication."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'QA/Apollo_R458_Deterministic_Proof.zip'
INCLUDE={'.php','.css','.js','.json','.py','.md','.png'}
files=sorted(p for p in ROOT.rglob('*') if p.is_file() and p.suffix.lower() in INCLUDE and p!=OUT and '__pycache__' not in p.parts)
manifest={'sprint':'R458','scope':'LOCAL_PHP_AND_CHROMIUM_ONLY','files':{p.relative_to(ROOT).as_posix():{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in files}}
def create(filename):
    with zipfile.ZipFile(filename,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        contents=[('MANIFEST_SHA256.json',(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode())]
        contents += [(p.relative_to(ROOT).as_posix(),p.read_bytes()) for p in files]
        for name,bytes_ in contents:
            item=zipfile.ZipInfo(name,(2026,11,18,0,0,0));item.external_attr=0o644<<16;item.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(item,bytes_,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
create(OUT)
probe=ROOT/'QA/.proof-second-run.zip'
create(probe)
assert OUT.read_bytes()==probe.read_bytes(),'Non-deterministic proof archive'
probe.unlink()
print(json.dumps({'entries':len(files)+1,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'file':str(OUT)},sort_keys=True))
