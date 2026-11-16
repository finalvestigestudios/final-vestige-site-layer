#!/usr/bin/env python3
"""R403 deterministic QA evidence bundle, offline fixture provenance only."""
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'QA'
FILES=[ROOT/p for p in ('README.md','qa/css_effect_custody.py','qa/test_css_effect_custody.py',
                         'qa/package_evidence.py','QA/QA-RESULTS.json','QA/browser-measurements.json')]
FILES+=sorted(QA.glob('*.png'))
for path in FILES:
    if not path.is_file():raise SystemExit('HOLD missing QA artifact: '+str(path))
results=json.loads((QA/'QA-RESULTS.json').read_text())
if results.get('status')!='PASS_LOCAL_CSS_EFFECT_ONLY' or results.get('release_allowed') is not False:
    raise SystemExit('HOLD invalid source QA scope')
manifest={'scope':'LOCAL_OFFLINE_APOLLO_CHROMIUM_NOT_INSTALLED_WORDPRESS',
          'release_allowed':False,'axe':'NOT_RUN','lcp_cls':'NOT_MEASURED',
          'file_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in sorted(FILES,key=lambda p:p.as_posix())}}
manifest_bytes=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
(QA/'MANIFEST.json').write_bytes(manifest_bytes)
entries=sorted([(str(p.relative_to(ROOT)),p.read_bytes()) for p in FILES]+[('QA/MANIFEST.json',manifest_bytes)])

def build(path):
    with ZipFile(path,'w',compression=ZIP_DEFLATED,compresslevel=9) as zipf:
        for name,data in entries:
            info=ZipInfo(name,date_time=(1980,1,1,0,0,0))
            info.compress_type=ZIP_DEFLATED;info.external_attr=0o644<<16
            zipf.writestr(info,data,compress_type=ZIP_DEFLATED,compresslevel=9)
    return hashlib.sha256(path.read_bytes()).hexdigest()

first=QA/'Apollo_R403_Local_Evidence.zip';other=QA/'_repeat.zip'
a=build(first);b=build(other)
if a!=b or first.read_bytes()!=other.read_bytes():raise SystemExit('HOLD nondeterministic bundle')
other.unlink()
print(json.dumps({'archive':str(first),'sha256':a,'entries':len(entries),'double_build_equal':True},sort_keys=True))
