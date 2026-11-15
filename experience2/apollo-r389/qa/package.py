#!/usr/bin/env python3
"""Deterministic source + executed local evidence ZIP, kept out of Git PR."""
from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
import json
root = Path(__file__).resolve().parents[2]
folder = root / 'apollo-r389'
paths = sorted([root/'apollo-r384/document-gallery.php',root/'apollo-r384/assets/gallery.css',root/'apollo-r377/custody.json'] + list(folder.glob('README.md')) + list((folder/'qa').glob('*.py')) + list((folder/'qa').glob('*.php')) + [x for x in (folder/'QA').iterdir() if x.is_file() and x.name != 'MANIFEST.json' and x.suffix in ('.png','.pdf','.json','.html')])
manifest = {x.relative_to(root).as_posix():sha256(x.read_bytes()).hexdigest() for x in paths}
(folder/'QA/MANIFEST.json').write_text(json.dumps({'schema':'apollo.r389.local-evidence.v1','files':manifest,'limits':['Not installed WP','Not genuine axe-core','Not hosted CWV','Not merchant/payment validation']},indent=2,sort_keys=True)+'\n')
paths.append(folder/'QA/MANIFEST.json')
zip_path = folder/'QA/Apollo_R389_Evidence.zip'
with ZipFile(zip_path,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
 for x in sorted(paths):
  item=ZipInfo(x.relative_to(root).as_posix(),date_time=(1980,1,1,0,0,0))
  item.compress_type=ZIP_DEFLATED
  item.external_attr=0o644 << 16
  z.writestr(item,x.read_bytes(),compress_type=ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'archive':str(zip_path),'files':len(paths),'sha256':sha256(zip_path.read_bytes()).hexdigest()},indent=2))
