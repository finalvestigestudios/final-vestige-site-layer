#!/usr/bin/env python3
from pathlib import Path
import hashlib, zipfile

ROOT = Path(__file__).resolve().parent
PLUGIN = ROOT / 'final-vestige-deployment-bridge'
OUT = ROOT.parent.parent / 'final-vestige-deployment-bridge-0.3.0.zip'
FIXED = (1980, 1, 1, 0, 0, 0)

entries = sorted(p for p in PLUGIN.rglob('*') if p.is_file())
with zipfile.ZipFile(OUT, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for p in entries:
        rel = Path('final-vestige-deployment-bridge') / p.relative_to(PLUGIN)
        info = zipfile.ZipInfo(str(rel).replace('\\', '/'), FIXED)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        info.create_system = 3
        z.writestr(info, p.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

print(OUT)
print('sha256=' + hashlib.sha256(OUT.read_bytes()).hexdigest())
print('bytes=' + str(OUT.stat().st_size))
