#!/usr/bin/env python3
"""Deterministic R361 frozen-evidence bundle; screenshots/PDF are produced by browser_gate.py."""
import hashlib,json,zipfile,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
DEST=ROOT/'Apollo_R361_Evidence.zip'
paths=[
'experience2/apollo-r339/chronology-rail.php','experience2/apollo-r339/assets/chronology-rail.css',
'experience2/apollo-r340/apollo-accession-gallery.php','experience2/apollo-r340/assets/accession-gallery.css',
'experience2/apollo-r345/evidence-plate.php','experience2/apollo-r345/evidence-plate.css',
'experience2/apollo-r347/source-index.php','experience2/apollo-r347/assets/source-index.css','experience2/apollo-r347/assets/source-index.js',
'experience2/apollo-r348/source-custody.php','experience2/apollo-r348/assets/source-custody.css',
'experience2/apollo-r349/source-policy.php','experience2/apollo-r350/integrity.php',
'experience2/apollo-r355/postfire-ledger.php','experience2/apollo-r355/postfire-ledger.css',
'experience2/apollo-r356/asset-bridge.php','experience2/apollo-r356/assets/print-proof.css',
'experience2/apollo-r357/template-asset-bridge.php','experience2/apollo-r358/explicit-template-prehead.php',
'experience2/apollo-r359/resolved-block-template-prehead.php',
'experience2/apollo-r360/rights-audit.php','experience2/apollo-r360/assets/rights-audit.css'
]
paths += [p.relative_to(ROOT).as_posix() for p in sorted((ROOT/'experience2/apollo-r361').rglob('*')) if p.is_file() and '__pycache__' not in str(p)]
paths=sorted(set(paths))
manifest={'sprint':'R361','mode':'staging-only','qa_type':'WP API stubs plus actual Chromium fixture; no installed WP/axe/CSP','files':[]}
for path in paths:
    b=(ROOT/path).read_bytes()
    manifest['files'].append({'path':path,'size':len(b),'sha256':hashlib.sha256(b).hexdigest(),
        'git_blob':subprocess.check_output(['git','hash-object',str(ROOT/path)],text=True).strip()})
manifest_bytes=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
with zipfile.ZipFile(DEST,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for path in paths+['R361_MANIFEST.json']:
        b=manifest_bytes if path=='R361_MANIFEST.json' else (ROOT/path).read_bytes()
        i=zipfile.ZipInfo(path,date_time=(1980,1,1,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;i.external_attr=0o644<<16
        z.writestr(i,b,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'zip':str(DEST),'files':len(paths)+1,'zip_sha256':hashlib.sha256(DEST.read_bytes()).hexdigest(),'manifest_sha256':hashlib.sha256(manifest_bytes).hexdigest()}))
