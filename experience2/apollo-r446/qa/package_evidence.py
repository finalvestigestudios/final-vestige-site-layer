#!/usr/bin/env python3
"""Deterministic ZIP of real local source and offline Chromium QA (not staging certification)."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
Q=ROOT/'QA';Q.mkdir(exist_ok=True)
files=[ROOT/'handoff.php', ROOT/'registry.json', ROOT/'README.md', ROOT/'CONVERSION_GATE.md',
       ROOT/'qa/fixture.php', ROOT/'qa/test_contract.py', ROOT/'qa/browser_qa.py',
       ROOT/'qa/package_evidence.py', Q/'browser_results.json']
files+=sorted((Q/'screenshots').glob('*.png'))
for f in files:
    if not f.is_file(): raise SystemExit('MISSING required source or QA: '+str(f))
report=json.loads((Q/'browser_results.json').read_text())
if len(report['cases'])!=14 or not all(c['pass'] for c in report['cases']):
    raise SystemExit('Browser verification is not a pass')
results=subprocess.run(['python',str(ROOT/'qa/test_contract.py')],capture_output=True,text=True)
if results.returncode!=0 or 'Ran 28 tests' not in results.stderr or 'OK' not in results.stderr:
    raise SystemExit('Contract regression failed: '+results.stderr[-500:])
summary={
 'scope':'Apollo R446 local offline QA; no claim of installed WordPress staging',
 'php_contract':'28/28 PASS', 'chromium_cases':'14/14 PASS',
 'screenshots':len(list((Q/'screenshots').glob('*.png'))),
 'axe':'NOT RUN', 'navigated_lcp_cls':'NOT RUN — Chromium policy blocks navigation',
 'independent_qd':'PENDING', 'paid_sku':'NOT VERIFIED',
 'source_file_hashes':{f.relative_to(ROOT).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
}
(Q/'qa_summary.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n')
files.append(Q/'qa_summary.json')
target=Q/'Apollo_R446_Offline_QA.zip'
with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
    for f in sorted(files,key=lambda f:f.relative_to(ROOT).as_posix()):
        name=f.relative_to(ROOT).as_posix()
        info=zipfile.ZipInfo(name,date_time=(2026,1,1,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        info.external_attr=(0o100644<<16)
        archive.writestr(info,f.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
print(json.dumps({'archive':str(target),'files':len(files),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()},sort_keys=True))