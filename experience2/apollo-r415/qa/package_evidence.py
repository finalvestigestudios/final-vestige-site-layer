#!/usr/bin/env python3
"""Create a deterministic artifact with no timestamps, screenshots, or source modifications."""
from pathlib import Path
import zipfile,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
files=[p for p in ROOT.rglob('*') if p.is_file() and p.suffix in ('.php','.py','.css','.md','.json','.png','.txt') and p.name!='sha256-manifest.json']
files.sort(key=lambda x:x.relative_to(ROOT).as_posix())
manifest={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
receipt=ROOT/'QA/sha256-manifest.json';receipt.write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
files.append(receipt);files.sort(key=lambda x:x.relative_to(ROOT).as_posix())
out=ROOT/'QA/Apollo_R415_Local_Evidence.zip'
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in files:
  item=zipfile.ZipInfo(p.relative_to(ROOT).as_posix(),date_time=(1980,1,1,0,0,0));item.external_attr=0o644<<16;item.compress_type=zipfile.ZIP_DEFLATED
  z.writestr(item,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(f'{len(files)} entries; sha256 {hashlib.sha256(out.read_bytes()).hexdigest()}')
