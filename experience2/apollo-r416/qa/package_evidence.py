#!/usr/bin/env python3
"""Byte-for-byte repeatable ZIP of R416 QA. No timestamps, secrets or generated claims."""
from __future__ import annotations
import hashlib
import io
import json
import zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'QA'
SOURCE=['README.md','qa/journey_acceptance.py','qa/test_gate.py','qa/test_browser.py','qa/package_evidence.py']

def assemble() -> bytes:
    paths=sorted(SOURCE+[str(p.relative_to(ROOT)) for p in QA.rglob('*') if p.is_file()
                         and p.suffix in ('.json','.png')])
    manifest={'format':'Apollo-R416-static-QA-v1','files':{}}
    obj=io.BytesIO()
    with zipfile.ZipFile(obj,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in paths:
            raw=(ROOT/name).read_bytes()
            manifest['files'][name]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
            write(z,name,raw)
        write(z,'MANIFEST.json',(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode())
    return obj.getvalue()

def write(z:zipfile.ZipFile,name:str,content:bytes)->None:
    info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
    info.compress_type=zipfile.ZIP_DEFLATED
    info.external_attr=0o644 <<16
    z.writestr(info,content,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)

if __name__=='__main__':
    first=assemble();second=assemble();assert first==second
    target=QA/'Apollo_R416_Local_Evidence.zip'
    target.write_bytes(first)
    print('R416 zip:',len(first),'bytes; SHA256',hashlib.sha256(first).hexdigest())
