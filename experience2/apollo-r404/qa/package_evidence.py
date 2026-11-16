#!/usr/bin/env python3
"""R404 deterministic local proof archive (never a release receipt)."""
from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
import json
ROOT=Path(__file__).resolve().parents[1]
FILES=[ROOT/n for n in ('README.md','assets/research-desk-resilient.js','assets/research-desk-resilient.css','qa/test_research_desk.py','qa/package_evidence.py')]
FILES+=sorted((ROOT/'QA').glob('*.png'))
FILES+=[ROOT/'QA/browser-results.json']
assert all(p.exists() for p in FILES)
result=json.loads((ROOT/'QA/browser-results.json').read_text())
assert result['status']=='PASS_LOCAL_FIXTURE_ONLY' and result['released'] is False
assert len(result['screens'])==8
manifest={'status':'LOCAL_FIXTURE_NOT_STAGING','files':{p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in FILES}}
manifest_bytes=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
entries={p.relative_to(ROOT).as_posix():p.read_bytes() for p in FILES}
entries['QA/MANIFEST.json']=manifest_bytes

def make():
    import io
    b=io.BytesIO()
    with ZipFile(b,'w',ZIP_DEFLATED,compresslevel=9) as z:
        for name,body in sorted(entries.items()):
            info=ZipInfo(name,date_time=(1980,1,1,0,0,0));info.compress_type=ZIP_DEFLATED
            info.external_attr=0o100644<<16
            z.writestr(info,body)
    return b.getvalue()
a=make();assert a==make()
out=ROOT/'QA/Apollo_R404_Local_Evidence.zip';out.write_bytes(a)
(ROOT/'QA/MANIFEST.json').write_bytes(manifest_bytes)
print(f'{out} {len(entries)} files sha256={sha256(a).hexdigest()}')
