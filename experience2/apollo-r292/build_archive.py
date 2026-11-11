#!/usr/bin/env python3
"""Byte-reproducible R292 staging evidence ZIP; never deploys or edits WordPress."""
from pathlib import Path
import hashlib, json, sys, zipfile
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/Apollo_R292.zip')
QA=Path(sys.argv[2] if len(sys.argv)>2 else '/tmp/apollo-r292-qa')
RELS=['experience2/apollo-r281/apollo-source-experience.php',
      'experience2/apollo-r281/assets/apollo-source-experience.css',
      'experience2/apollo-r290/qa/php_gate.php',
      'experience2/apollo-r290/qa/browser_gate.py',
      'experience2/apollo-r290/qa/http_axe_gate.py',
      'experience2/apollo-r291/qa/source_controlled_gate.py',
      'experience2/apollo-r292/qa/source_controlled_gate.py',
      'experience2/apollo-r292/README.md',
      'experience2/apollo-r292/build_archive.py']
files={p:(ROOT/p).read_bytes() for p in RELS}
for p in sorted(QA.iterdir()):
    if p.is_file() and p.suffix.lower() in ('.json','.png','.pdf','.py'):
        files['QA/'+p.name]=p.read_bytes()
manifest={'release':'R292 STAGING HARD HOLD',
          'scope':'Local source-controlled PHP/Playwright and independent offline browser QA only; NOT installed WordPress, genuine axe, HTTP/CSP, field CWV, commerce or editorial approval.',
          'file_sha256':{p:hashlib.sha256(v).hexdigest() for p,v in sorted(files.items())}}
files['EVIDENCE-MANIFEST.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
OUT.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for name,data in sorted(files.items()):
        info=zipfile.ZipInfo(name,date_time=(2026,11,11,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        info.external_attr=0o644<<16
        z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print('R292',len(files),'files',hashlib.sha256(OUT.read_bytes()).hexdigest(),str(OUT))
