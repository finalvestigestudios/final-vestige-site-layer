#!/usr/bin/env python3
"""Make deterministic, reproducible R46 staging ZIP with manifest and browser evidence.

This creates a review artifact, not an install instruction or release approval.
Source-only and compiled stage files have fixed ZIP metadata; QA screenshots are
captured by a separate real Playwright run and explicitly labeled fixture-only.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import zipfile

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
import build_atlas
import build_wordpress_stage

SOURCES=['README.md','R45_CUSTODY_NAVIGATION_HOLD.md','R46_SOURCE_PAIR_HOLD.md','atlas.css','atlas.js',
         'build_atlas.py','build_wordpress_stage.py','final-vestige-ex2-evidence-atlas.php',
         'test_atlas.py','tests/test_wordpress_stage.py','tests/test_chronology_r43.py',
         'tests/test_citations_r44.py','tests/test_citation_navigation_r45.py',
         'tests/browser_r45_navigation.py','tests/test_pair_inspector_r46.py','tests/browser_r46_pair_smoke.py','tests/browser_r46_capture.py','tests/browser_r44_review.py',
         'tests/browser_regression_r43.py','tests/wordpress_shortcode_probe.php',
         'tests/build_r46_bundle.py']
CROSSWALK=HERE.parent/'research-desk/sources/R37_PHOTO_CUSTODY_CROSSWALK.json'


def build(output,qa):
    files={}
    prefix='experience2/evidence-atlas/'
    for path in SOURCES:
        data=(HERE/path).read_bytes()
        files[prefix+path]=data
    files['experience2/research-desk/sources/'+CROSSWALK.name]=CROSSWALK.read_bytes()
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)
        preview=build_atlas.build(root/'preview')
        stage=build_wordpress_stage.build(root/'wordpress')
        for f in sorted(root.rglob('*')):
            if f.is_file():files['compiled/'+str(f.relative_to(root))]=f.read_bytes()
    for f in sorted(qa.glob('*')):
        if f.is_file() and (f.suffix=='.png' or f.name in {'R46_BROWSER_RECEIPT.json','R46_SCREENSHOT_MANIFEST.json','browser_r46_compare.py'}):
            files['qa/'+f.name]=f.read_bytes()
    manifest={
      'schema':'fv.ex2.apollo.r46.bundle.v1','release':'STAGING_HOLD',
      'crosswalk_git_blob':build_atlas.EXPECTED_BLOB,
      'readiness':'DO_NOT_DEPLOY','axe':'NOT_EXECUTED','navigated_wordpress':'NOT_TESTED',
      'source_sha256':{name:hashlib.sha256(data).hexdigest() for name,data in sorted(files.items())},
    }
    files['SHA256_MANIFEST.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name, data in sorted(files.items()):
            info=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o644<<16
            archive.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(output) as archived:
        assert all(hashlib.sha256(archived.read(k)).hexdigest()==v for k,v in manifest['source_sha256'].items())
    return {'file':str(output),'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
            'entries':len(files),'content_verified':len(manifest['source_sha256']),
            'fragment_sha256':stage['file_sha256']['fv-ex2-evidence-atlas/templates/atlas-fragment.html']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--qa',type=Path,required=True)
    args=p.parse_args();print(json.dumps(build(args.output,args.qa),indent=2,sort_keys=True))
