#!/usr/bin/env python3
"""Deterministic R42 source/QA ZIP. No WordPress writes or network calls.

Build twice with the same source and browser QA input; zip bytes must match.
The optional printed PDF is excluded because Chromium embeds generation time.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

HERE = Path(__file__).resolve().parents[3]
PATHS = (
    'experience2/research-desk/sources/R37_PHOTO_CUSTODY_CROSSWALK.json',
    'experience2/evidence-atlas/README.md',
    'experience2/evidence-atlas/atlas.css',
    'experience2/evidence-atlas/atlas.js',
    'experience2/evidence-atlas/build_atlas.py',
    'experience2/evidence-atlas/build_wordpress_stage.py',
    'experience2/evidence-atlas/final-vestige-ex2-evidence-atlas.php',
    'experience2/evidence-atlas/tests/browser_regression_r42.py',
    'experience2/evidence-atlas/tests/build_r42_review.py',
    'experience2/evidence-atlas/R42_SOURCE_INDEX_ASSET_LOADING_HOLD.md',
    'experience2/evidence-atlas/tests/wordpress_shortcode_probe.php',
    'experience2/evidence-atlas/tests/test_wordpress_stage.py',
    'experience2/evidence-atlas/test_atlas.py',
)

def digest(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()

def build(out:Path,qa:Path):
    receipt=json.loads((qa/'R42_QA_RECEIPT.json').read_text())
    assert receipt['release']=='STAGING_HOLD' and len(receipt['cases'])==14
    assert all(case['status']=='PASS' for case in receipt['cases'])
    assert len(receipt['regression_checks'])==3
    files={path:(HERE/path).read_bytes() for path in PATHS}
    files['qa/R42_QA_RECEIPT.json']=(qa/'R42_QA_RECEIPT.json').read_bytes()
    files['qa/STAGING-MANIFEST.json']=(qa/'stage/STAGING-MANIFEST.json').read_bytes()
    for name in ('r42-evidence-390-js.png','r42-evidence-390-nojs.png',
                 'r42-evidence-1440-js.png','r42-evidence-1440-nojs.png'):
        files['qa/'+name]=(qa/name).read_bytes()
    manifest={'schema':'fv.ex2.apollo.r42.review_archive.v1','release':'STAGING_HOLD',
        'source':'R37/R39 pinned NASA custody via compiled PHP adapter',
        'caveat':'No WordPress staging, axe, HTTP navigation or hosted CWV certification',
        'file_sha256':{name:digest(data) for name,data in sorted(files.items())}}
    files['SHA256_MANIFEST.json']=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()
    out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(files.items()):
            entry=zipfile.ZipInfo(name,(1980,1,1,0,0,0))
            entry.create_system=3
            entry.external_attr=(0o100644<<16)
            entry.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(entry,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    print(out,digest(out.read_bytes()),len(files),'files')

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--qa',required=True,type=Path)
    ap.add_argument('--out',required=True,type=Path)
    args=ap.parse_args();build(args.out,args.qa)
