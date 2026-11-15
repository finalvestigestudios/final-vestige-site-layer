#!/usr/bin/env python3
"""R381 source + test evidence with deterministic timestamps, order and hashes."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'experience2/apollo-r381'
FILES=[
'experience2/apollo-r377/source-role-desk.php',
'experience2/apollo-r377/custody.json',
'experience2/apollo-r381/README.md',
'experience2/apollo-r381/evidence-to-investigation.php',
'experience2/apollo-r381/assets/evidence-to-investigation.css',
'experience2/apollo-r381/qa/wp_stub.php',
'experience2/apollo-r381/qa/browser_qa.py',
'experience2/apollo-r381/qa/http_qa.py',
'experience2/apollo-r381/qa/package.py',
'experience2/apollo-r381/QA/results.json',
'experience2/apollo-r381/QA/http_gate.json',
'experience2/apollo-r381/QA/R381_Evidence_Path_Print.pdf',
]
FILES+=['experience2/apollo-r381/QA/'+p.name for p in sorted((BASE/'QA').glob('*.png'))]
FILES=sorted(set(FILES))
OUT=BASE/'QA/Apollo_R381_Evidence.zip'
def build():
 hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in FILES}
 manifest=json.dumps({'schema':'fv.apollo.r381.evidence.v1','files':hashes},indent=2,sort_keys=True).encode()+b'\n'
 with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as zip:
  for f in sorted(FILES+['R381_MANIFEST.json']):
   raw=manifest if f=='R381_MANIFEST.json' else (ROOT/f).read_bytes()
   item=zipfile.ZipInfo(f,date_time=(1980,1,1,0,0,0));item.external_attr=0o100644<<16;item.compress_type=zipfile.ZIP_DEFLATED
   zip.writestr(item,raw,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
 return hashlib.sha256(OUT.read_bytes()).hexdigest(),len(FILES)+1
if __name__=='__main__':
 first,n=build();second,_=build();assert first==second
 print('DETERMINISTIC_PASS',n,'entries','SHA256',first)
