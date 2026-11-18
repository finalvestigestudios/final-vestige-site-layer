#!/usr/bin/env python3
"""Byte-stable QA ZIP with fixed timestamps; never self-include output."""
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
import hashlib
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'QA/Apollo_R443_Local_QA.zip'
def assemble():
    paths=sorted(p for p in ROOT.rglob('*') if p.is_file() and p!=OUT and not p.name.endswith('.pyc') and '__pycache__' not in p.parts)
    with ZipFile(OUT,'w') as archive:
        for p in paths:
            z=ZipInfo(p.relative_to(ROOT).as_posix(),date_time=(2026,11,17,0,0,0))
            z.compress_type=ZIP_DEFLATED;z.external_attr=0o644<<16
            archive.writestr(z,p.read_bytes())
    return len(paths),hashlib.sha256(OUT.read_bytes()).hexdigest()
if __name__=='__main__':
    n,h=assemble();print(f'{n} entries SHA256 {h}');n2,h2=assemble();assert(n,h)==(n2,h2)
