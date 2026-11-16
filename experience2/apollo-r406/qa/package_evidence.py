#!/usr/bin/env python3
"""Deterministic local QA archive, explicitly not a reviewed WordPress release."""
import hashlib
import io
import json
from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/'QA/Apollo_R406_Local_Evidence.zip'
FILES=['README.md','staging-shortcode.php','assets/research-desk-r406.js',
       'qa/render_fixture.php','qa/test_adapter.php','qa/test_browser.py','qa/assemble.py','qa/test_assemble.py',
       'QA/browser-results.json','QA/final-test.log']
FILES += ['QA/'+p for p in sorted(x.name for x in (ROOT/'QA').glob('*.png'))]

def build():
    content={name:(ROOT/name).read_bytes() for name in FILES}
    manifest={'status':'LOCAL_FIXTURE_ONLY_NOT_APPROVED_FOR_STAGING_INSTALL',
              'scope':'R406 source and synthetic-fixture Playwright evidence',
              'files':{p:hashlib.sha256(b).hexdigest() for p,b in sorted(content.items())},
              'gaps':['installed WordPress','real HTTP/CSP','axe-core','LCP/CLS','native zoom',
                      'screen readers','exact PR CI','QD/founder approval','merchant verification']}
    content['QA/SHA256_MANIFEST.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
    data=io.BytesIO()
    with zipfile.ZipFile(data,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for path,b in sorted(content.items()):
            info=zipfile.ZipInfo(path,date_time=(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16
            z.writestr(info,b,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return data.getvalue()
if __name__=='__main__':
    a=build();b=build();assert a==b
    OUTPUT.write_bytes(a)
    print(json.dumps({'zip':str(OUTPUT),'sha256':hashlib.sha256(a).hexdigest(),
                      'entries':len(FILES)+1,'byte_identical_double_build':True}))
