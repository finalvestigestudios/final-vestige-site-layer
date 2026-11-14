#!/usr/bin/env python3
"""Deterministically package frozen R362 real-browser QA & source code for independent replay.
Does not regenerate browser PDFs/screenshots; those differ by browser timestamps and environment.
"""
from pathlib import Path
import hashlib, json, zipfile
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'experience2/apollo-r362'
DEST=ROOT.parent/'Apollo_R362_Evidence.zip'
FILES=[p for p in (ROOT/'experience2').rglob('*') if p.is_file() and (
    'experience2/apollo-r362/' in p.as_posix() or p.as_posix().endswith((
    'experience2/apollo-r339/chronology-rail.php',
    'experience2/apollo-r340/apollo-accession-gallery.php',
    'experience2/apollo-r345/evidence-plate.php',
    'experience2/apollo-r349/source-policy.php',
    'experience2/apollo-r350/integrity.php',
    'experience2/apollo-r355/postfire-ledger.php',
    'experience2/apollo-r360/rights-audit.php',
    'experience2/apollo-r359/resolved-block-template-prehead.php',
    'experience2/apollo-r361/rights-asset-bridge.php')))]
FILES.sort(key=lambda p:p.relative_to(ROOT).as_posix())
manifest={'sprint':'Apollo R362','frozen_artifacts':True,'source_control_scope':'experience2/apollo-r362/','files':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in FILES]}
blob=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
with zipfile.ZipFile(DEST,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    def write(name,data):
        info=zipfile.ZipInfo(name,(1980,1,1,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
        z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    for p in FILES: write(p.relative_to(ROOT).as_posix(),p.read_bytes())
    write('R362_MANIFEST.json',blob)
print(json.dumps({'file':str(DEST),'sha256':hashlib.sha256(DEST.read_bytes()).hexdigest(),'file_count':len(FILES)},indent=2))
