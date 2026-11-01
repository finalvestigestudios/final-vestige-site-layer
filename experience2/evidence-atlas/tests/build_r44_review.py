#!/usr/bin/env python3
"""Deterministic, source-grounded R44 review ZIP; no network or CMS writes."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
import build_atlas
import build_wordpress_stage

SOURCE_FILES=(
    'experience2/research-desk/sources/R37_PHOTO_CUSTODY_CROSSWALK.json',
    'experience2/evidence-atlas/README.md',
    'experience2/evidence-atlas/R43_CHRONOLOGY_RAIL_HOLD.md',
    'experience2/evidence-atlas/R44_CITATION_REGISTER_HOLD.md',
    'experience2/evidence-atlas/atlas.css',
    'experience2/evidence-atlas/atlas.js',
    'experience2/evidence-atlas/build_atlas.py',
    'experience2/evidence-atlas/build_wordpress_stage.py',
    'experience2/evidence-atlas/final-vestige-ex2-evidence-atlas.php',
    'experience2/evidence-atlas/test_atlas.py',
    'experience2/evidence-atlas/tests/browser_regression_r42.py',
    'experience2/evidence-atlas/tests/browser_regression_r43.py',
    'experience2/evidence-atlas/tests/browser_r44_review.py',
    'experience2/evidence-atlas/tests/build_r44_review.py',
    'experience2/evidence-atlas/tests/wordpress_shortcode_probe.php',
    'experience2/evidence-atlas/tests/test_chronology_r43.py',
    'experience2/evidence-atlas/tests/test_citations_r44.py',
    'experience2/evidence-atlas/tests/test_wordpress_stage.py',
)

def digest(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()

def build(out:Path,qa:Path)->tuple[str,int]:
    data=json.loads((qa/'R44_BROWSER_RECEIPT.json').read_text(encoding='utf8'))
    if (data['transport']!='PLAYWRIGHT_SET_CONTENT_NO_HTTP'
        or data['authentic_wordpress']!='NOT_TESTED'
        or data['axe']!='NOT_EXECUTED'
        or data['hosted_CWV']!='NOT_MEASURED'
        or len(data['responsive'])!=14
        or not all(r['pass'] for r in data['responsive'])
        or len(data['adversarial'])!=4 or len(data['screenshots'])!=4):
        raise ValueError('R44 QA receipt does not satisfy controlled browser gates')
    files={name:(ROOT/name).read_bytes() for name in SOURCE_FILES}
    files['qa/R44_BROWSER_RECEIPT.json']=(qa/'R44_BROWSER_RECEIPT.json').read_bytes()
    for shot in data['screenshots']:
        name=shot['name']
        if name not in {'r44-390-js.png','r44-390-nojs.png','r44-1440-js.png','r44-1440-nojs.png'}:
            raise ValueError('unexpected screenshot name')
        buf=(qa/name).read_bytes()
        if digest(buf)!=shot['sha256']:
            raise ValueError('screenshot digest changed')
        files['qa/'+name]=buf
    with tempfile.TemporaryDirectory() as t:
        base=Path(t)
        build_atlas.build(base/'preview')
        build_wordpress_stage.build(base/'wordpress')
        for item in sorted(base.rglob('*')):
            if item.is_file():
                files['compiled/'+str(item.relative_to(base))]=item.read_bytes()
    manifest={'schema':'fv.ex2.apollo.r44.review_archive.v1','release':'STAGING_HOLD',
        'transport':'PHP-rendered Chromium set_content; NOT installed WordPress/HTTP/axe/hosted Core Web Vitals',
        'NASA_embedded_images':0,'geographic_pins':0,
        'file_sha256':{name:digest(buf) for name,buf in sorted(files.items())}}
    files['SHA256_MANIFEST.json']=(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode('utf8')
    out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,buf in sorted(files.items()):
            info=zipfile.ZipInfo(name,(1980,1,1,0,0,0))
            info.create_system=3
            info.external_attr=0o100644 << 16
            info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,buf,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return digest(out.read_bytes()),len(files)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--qa',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args()
    print('R44 deterministic review archive:',*build(args.out,args.qa))
