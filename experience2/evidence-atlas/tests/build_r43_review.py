#!/usr/bin/env python3
"""Deterministic R43 source / real-Chromium evidence archive (no network or WP writes)."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
HERE=Path(__file__).resolve().parents[3]
FILES=(
 'experience2/research-desk/sources/R37_PHOTO_CUSTODY_CROSSWALK.json',
 'experience2/evidence-atlas/R43_CHRONOLOGY_RAIL_HOLD.md',
 'experience2/evidence-atlas/README.md',
 'experience2/evidence-atlas/atlas.css',
 'experience2/evidence-atlas/atlas.js',
 'experience2/evidence-atlas/build_atlas.py',
 'experience2/evidence-atlas/build_wordpress_stage.py',
 'experience2/evidence-atlas/final-vestige-ex2-evidence-atlas.php',
 'experience2/evidence-atlas/tests/browser_regression_r42.py',
 'experience2/evidence-atlas/tests/browser_regression_r43.py',
 'experience2/evidence-atlas/tests/build_r43_review.py',
 'experience2/evidence-atlas/tests/wordpress_shortcode_probe.php',
 'experience2/evidence-atlas/tests/test_chronology_r43.py',
 'experience2/evidence-atlas/tests/test_wordpress_stage.py',
 'experience2/evidence-atlas/test_atlas.py',
)
def digest(data:bytes)->str:return hashlib.sha256(data).hexdigest()

def build(destination:Path,qa:Path)->tuple[str,int]:
 receipt=json.loads((qa/'R43_QA_RECEIPT.json').read_text())
 assert receipt['release']=='STAGING_HOLD' and len(receipt['cases'])==14
 assert len(receipt['adversarial'])==3 and all(x['status']=='PASS' for x in receipt['cases'])
 assert receipt['axe'].startswith('NOT_EXECUTED_') and receipt['authentic_wordpress']=='NOT_TESTED'
 files={name:(HERE/name).read_bytes() for name in FILES}
 files['qa/R43_QA_RECEIPT.json']=(qa/'R43_QA_RECEIPT.json').read_bytes()
 for name in ('r43-chronology-390-js.png','r43-chronology-390-nojs.png',
              'r43-chronology-1440-js.png','r43-chronology-1440-nojs.png'):
  files['qa/'+name]=(qa/name).read_bytes()
 manifest={'schema':'fv.ex2.apollo.r43.review_archive.v1','release':'STAGING_HOLD',
  'caveat':'Synthetic page.set_content with real PHP template, not installed WP, HTTP, axe, or hosted CWV',
  'file_sha256':{name:digest(data) for name,data in sorted(files.items())}}
 files['SHA256_MANIFEST.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
 destination.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name,data in sorted(files.items()):
   info=zipfile.ZipInfo(name,(1980,1,1,0,0,0))
   info.create_system=3; info.external_attr=0o100644 << 16
   info.compress_type=zipfile.ZIP_DEFLATED
   z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
 return digest(destination.read_bytes()),len(files)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--qa',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
 args=ap.parse_args();print('R43 deterministic archive:',*build(args.out,args.qa))
