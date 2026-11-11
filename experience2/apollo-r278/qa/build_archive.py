#!/usr/bin/env python3
"""Deterministic R278 local evidence archive builder; exact SHA passed on command line."""
from pathlib import Path
from zipfile import ZipInfo, ZipFile, ZIP_DEFLATED
import hashlib, json, sys
root=Path(__file__).resolve().parents[3]
sha=sys.argv[1] if len(sys.argv)>1 else ''
if len(sha)!=40 or any(c not in '0123456789abcdef' for c in sha):
    raise SystemExit('provide exact 40-char HEAD commit SHA')
folders=[root/'experience2',root/'QA-A',root/'QA-B']
files=sorted((p for d in folders for p in d.rglob('*') if p.is_file() and p.suffix!='.pyc' and '__pycache__' not in p.parts), key=lambda p:p.relative_to(root).as_posix())
manifest={'repo':'finalvestigestudios/final-vestige-site-layer','pr':2006,'head':sha,'parent':'77c80117d591aa0482f16062b9d6b375c0d44193',
 'adapter_git_blob':'c54e693dfc0d88967e91e7bb3a6714f8971d9e97',
 'status':'staging only; hard hold; not installed',
 'local_test_evidence':{'PHP_6':'PASS x2','Chromium_offline_30':'PASS x2','PHP_HTTP_response_CSP_headers_6':'PASS (Python client only)',
                        'Chromium_real_HTTP_CSP':'BLOCKED_BY_ADMINISTRATOR','axe_core':'NOT_EXECUTED','installed_wordpress':'NOT_TESTED'},
 'scope':'R278 adapter+historical-source fallback and source custody; no homepage, WP or commerce write',
 'files_sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
(root/'EVIDENCE-MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
files.append(root/'EVIDENCE-MANIFEST.json');files.sort(key=lambda p:p.relative_to(root).as_posix())
for suffix in ('A','B'):
    out=root/f'Apollo_R278_Failopen_HTTP_CSP_Source_Custody_HARD_HOLD_{suffix}.zip'
    with ZipFile(out,'w',ZIP_DEFLATED,compresslevel=9) as z:
        for p in files:
            info=ZipInfo(p.relative_to(root).as_posix(),date_time=(1980,1,1,0,0,0))
            info.compress_type=ZIP_DEFLATED
            info.external_attr=0o100644<<16
            z.writestr(info,p.read_bytes(),compress_type=ZIP_DEFLATED,compresslevel=9)
    print(out.name,len(files),'files',hashlib.sha256(out.read_bytes()).hexdigest())
