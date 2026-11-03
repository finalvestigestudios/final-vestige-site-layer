#!/usr/bin/env python3
"""R91: fail-closed local asset-custody gate for isolated Apollo review output.

The R90 R89 builder verifies evidence, chronology, NASA destinations and rights
hold. This independent wrapper also checks the ACTUAL shipped CSS/JS/HTML for
unexpected network-bearing dependencies before any review files are exported.
No photos, installation, WordPress writes or deployment are performed.
"""
from __future__ import annotations
import argparse
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PAGES = {
    'R89_REVIEW_HUB.html': 'review_hub_r89.css',
    'R88_READING_ROOM.html': 'reading_room_r88.css',
    'R87_PHOTOGRAPH_DATE_RAIL.html': 'chronology_r87.css',
    'R85_NASA_SOURCE_REVIEW.html': 'rights_board_r85.css',
}
SCRIPTS = {'R88_READING_ROOM.html': 'reading_room_r88.js'}
ALLOWED_ASSETS = set(PAGES.values()) | set(SCRIPTS.values())
SOURCE = (
    'experience2/evidence-atlas/tools/build_release_candidate_r91.py',
    'experience2/evidence-atlas/tests/test_release_candidate_r91.py',
    'experience2/evidence-atlas/tests/browser_release_candidate_r91.py',
    'experience2/evidence-atlas/R91_ASSET_BOUNDARY_STAGING_HOLD.md',
    '.github/workflows/ex2-apollo-r91-asset-boundary.yml',
)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


class Dependencies(HTMLParser):
    """Inspect every dependency-bearing element, not merely clickable links."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.scripts = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if len(a) != len(attrs):
            self.errors.append('DUPLICATE_ATTRIBUTE')
        if any(k.startswith('on') or k in ('style', 'srcset', 'data-src', 'poster')
               for k in a):
            self.errors.append('INLINE_HANDLER_OR_MEDIA_ATTRIBUTE')
        if tag == 'link':
            self.links.append(a)
        elif tag == 'script':
            self.scripts.append(a)
        elif tag in ('style', 'base', 'object', 'embed', 'iframe', 'img',
                     'video', 'audio', 'source', 'picture', 'svg', 'canvas'):
            self.errors.append('UNAPPROVED_ASSET_ELEMENT')
        elif tag == 'meta' and a.get('http-equiv', '').lower() == 'refresh':
            self.errors.append('UNAPPROVED_META_REFRESH')
        if 'src' in a and tag != 'script':
            self.errors.append('UNAPPROVED_SRC_ATTRIBUTE')


def audit_asset_boundary(folder: Path) -> dict:
    """Network/rights-safe asset allowlist. Browser network monitoring is required too."""
    names = {p.name for p in folder.iterdir() if p.is_file()}
    required = set(PAGES) | ALLOWED_ASSETS | {
        'R89_INTEGRITY_RECEIPT.json', 'R88_READING_ROOM_RECEIPT.json',
        'R87_RAIL_RECEIPT.json', 'R85_RIGHTS_RECEIPT.json',
    }
    if names != required:
        raise ValueError('R91_UNEXPECTED_OR_MISSING_ASSET')
    checks = {}
    for page, css in PAGES.items():
        parser = Dependencies()
        parser.feed((folder / page).read_text(encoding='utf8'))
        parser.close()
        expected_scripts = [SCRIPTS[page]] if page in SCRIPTS else []
        actual_scripts = [s.get('src', '') for s in parser.scripts]
        if parser.errors or parser.links != [{'rel':'stylesheet','href':css}] or actual_scripts != expected_scripts:
            raise ValueError('R91_HTML_ASSET_BOUNDARY:' + page)
        if any(set(s) - {'src','defer'} or 'defer' not in s
               for s in parser.scripts):
            raise ValueError('R91_SCRIPT_ATTRIBUTES:' + page)
        checks[page] = {'css': css, 'script': expected_scripts,
                        'sha256': digest((folder/page).read_bytes())}
    for name in sorted(ALLOWED_ASSETS):
        raw = (folder / name).read_text('utf8')
        if name.endswith('.css'):
            plain = re.sub(r'/\*.*?\*/', '', raw, flags=re.S)
            if (re.search(r'@import\b|url\s*\(|image-set\s*\(|expression\s*\(',
                          plain, re.I) or '\' in plain):
                raise ValueError('R91_CSS_MEDIA_OR_REMOTE_IMPORT:' + name)
        else:
            if re.search(r'\b(?:fetch|XMLHttpRequest|WebSocket|EventSource|Worker|'
                         r'sendBeacon|serviceWorker)\b|\bimport\s*\(', raw, re.I):
                raise ValueError('R91_UNREVIEWED_SCRIPT_NETWORK:' + name)
        checks[name] = {'sha256': digest((folder/name).read_bytes())}
    previous = json.loads((folder/'R89_INTEGRITY_RECEIPT.json').read_text('utf8'))
    if (previous.get('release') != 'STAGING_HOLD' or
        previous.get('publication_approved') is not False or
        previous.get('photo_rights_cleared') != 0 or
        len(previous.get('record_source_bindings', {})) != 24):
        raise ValueError('R91_INHERITED_SOURCE_GATE_MISSING')
    return {'schema':'fv.apollo.r91.asset-boundary.v1', 'release':'STAGING_HOLD',
            'deployment_allowed':False, 'photographic_rights_cleared':0,
            'hosted_wordpress_verified':False,'assets_allowlisted':len(ALLOWED_ASSETS),
            'source_bindings_inherited':24,'network_asset_dependencies':0,
            'files': dict(sorted(checks.items()))}


def builder():
    path = HERE / 'build_review_hub_r89.py'
    spec = importlib.util.spec_from_file_location('apollo_r90_existing', path)
    instance = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = instance
    spec.loader.exec_module(instance)
    return instance


def build(out: Path, archive: Path | None = None) -> dict:
    if out.exists() and any(out.iterdir()):
        raise ValueError('R91_OUTPUT_MUST_BE_EMPTY')
    if archive and archive.exists():
        raise ValueError('R91_ARCHIVE_MUST_BE_NEW')
    with tempfile.TemporaryDirectory(prefix='apollo-r91-') as t:
        stage = Path(t)/'stage'
        parent = builder()
        parent.build(stage)
        receipt = audit_asset_boundary(stage)
        (stage/'R91_ASSET_BOUNDARY_RECEIPT.json').write_text(
            json.dumps(receipt,sort_keys=True,indent=2)+'\n',encoding='utf8')
        out.mkdir(parents=True,exist_ok=True)
        for file in sorted(stage.iterdir()):
            shutil.copyfile(file, out/file.name)
    if archive:
        payload = {'built/'+p.name:p.read_bytes() for p in sorted(out.iterdir())}
        for name in SOURCE:
            payload['source/'+name] = (ROOT/name).read_bytes()
        payload['SHA256_MANIFEST.json'] = (json.dumps({
            'release':'STAGING_HOLD','deployment_allowed':False,
            'files':{k:digest(v) for k,v in sorted(payload.items())},
        },sort_keys=True,indent=2)+'\n').encode('utf8')
        archive.parent.mkdir(parents=True,exist_ok=True)
        with ZipFile(archive,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
            for name, data in sorted(payload.items()):
                info = ZipInfo(name,date_time=(1980,1,1,0,0,0))
                info.compress_type=ZIP_DEFLATED
                info.external_attr=0o100644 << 16
                info.create_system=3
                z.writestr(info,data)
    return receipt


if __name__=='__main__':
    args=argparse.ArgumentParser()
    args.add_argument('out',type=Path)
    args.add_argument('archive',type=Path,nargs='?')
    a=args.parse_args()
    try:
        print(json.dumps(build(a.out,a.archive),sort_keys=True))
    except Exception:
        print('R91_STAGING_HOLD: asset/custody verification failed',file=sys.stderr)
        raise SystemExit(1)
