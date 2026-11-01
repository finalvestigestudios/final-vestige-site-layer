#!/usr/bin/env python3
"""Build a deterministic, review-only WordPress shortcode distribution from R39 custody.

Requires the reviewed R37 crosswalk; never downloads or embeds NASA images.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
import shutil
import build_atlas

HERE = Path(__file__).resolve().parent
SOURCE_FILES = ('final-vestige-ex2-evidence-atlas.php', 'atlas.css', 'atlas.js')

class AuditParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.tags=[]
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def build(destination: Path):
    custody = build_atlas.validate_custody()
    full = build_atlas.make_html(custody, '', '')
    lead, sep, tail = full.partition('<main class="fva"')
    inside, end, rest = tail.partition('</main>')
    if not sep or not end or '<main' in inside or '</section>' not in inside:
        raise ValueError('R39 template landmarks changed: refuse WordPress stage build')
    # A shortcode must not inject a second <main> landmark into a WordPress document.
    fragment = '<section class="fva"' + inside + '</section>\n'
    parsed = AuditParser(); parsed.feed(fragment)
    tags=parsed.tags
    records=[a for t,a in tags if t=='article' and 'data-fva-record' in a]
    links=[a['href'] for t,a in tags if t=='a' and 'href' in a]
    ids=[a['id'] for _,a in tags if 'id' in a]
    if ([a.get('data-fva-id') for a in records] != list(build_atlas.IDS)
        or len(ids)!=len(set(ids))
        or not all(url in links for url in build_atlas.EXPECTED_URLS.values())
        or fragment.count('Individual review required. No photograph is reproduced here.') != 6
        or any(t in {'script','style','main','img','picture','video','iframe','canvas','svg','form'} for t,_ in tags)
        or any(any(k in a for k in ('data-lat','data-lng','data-fva-geo')) for _,a in tags)):
        raise ValueError('Unsafe or incomplete Atlas template: refuse WordPress stage build')
    dest=destination / 'fv-ex2-evidence-atlas'
    assets=dest / 'assets'; templates=dest/'templates'
    assets.mkdir(parents=True,exist_ok=True); templates.mkdir(parents=True,exist_ok=True)
    (templates/'atlas-fragment.html').write_text(fragment,encoding='utf-8',newline='\n')
    shutil.copyfile(HERE/SOURCE_FILES[0], dest/SOURCE_FILES[0])
    for fn in SOURCE_FILES[1:]: shutil.copyfile(HERE/fn, assets/fn)
    outputs={str(p.relative_to(destination)):sha256(p) for p in sorted(dest.rglob('*')) if p.is_file()}
    manifest={'schema':'fv.ex2.apollo.wp-stage.r49.v1','release':'STAGING_HOLD',
       'source_crosswalk_blob':build_atlas.EXPECTED_BLOB,'source_records':list(build_atlas.IDS),
       'media_rights_unreviewed':6,'embedded_images':0,'geographic_pins':0,
       'physical_wordpress_install':'NOT_TESTED','file_sha256':outputs}
    (destination/'STAGING-MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',type=Path,required=True)
    args=p.parse_args(); print(json.dumps(build(args.output),indent=2,sort_keys=True))
