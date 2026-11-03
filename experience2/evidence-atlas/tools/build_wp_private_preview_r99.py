#!/usr/bin/env python3
"""R99: deterministic, read-only, private WordPress review adapter for sealed Apollo R98.

No WordPress API calls, DB mutations, deployment or NASA image reproduction.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

R98_RECEIPT_SHA256 = '7cd85cbf273ebf406cb7e156c01a32b0558e3506a9c219a9b9c8f2099f4fe530'
VIEWS = ('R85_NASA_SOURCE_REVIEW.html','R87_PHOTOGRAPH_DATE_RAIL.html',
         'R88_READING_ROOM.html','R89_REVIEW_HUB.html',
         'R93_SOURCE_PASSPORTS.html','R94_CURATED_ATLAS.html',
         'R97_SOURCE_GALLERY.html')
RESOURCE = re.compile(r'\b(href|src)="([^"]+)"')

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def verify(src: Path) -> dict:
    if not src.is_dir() or src.is_symlink():
        raise ValueError('R99_SOURCE_ROOT')
    manifest = src/'R98_ROUNDTRIP_RECEIPT.json'
    if manifest.is_symlink() or not manifest.is_file() or digest(manifest.read_bytes()) != R98_RECEIPT_SHA256:
        raise ValueError('R99_EXACT_R98_RECEIPT_REQUIRED')
    receipt = json.loads(manifest.read_text(encoding='utf-8'))
    for key, value in [('release','STAGING_HOLD'),('publication_approved',False),
                       ('photo_rights_cleared',0),('images_embedded',0),
                       ('geo_pins',0),('inferred_edges',0),('records',6),('views',7)]:
        if type(receipt.get(key)) is not type(value) or receipt[key] != value:
            raise ValueError('R99_RELEASE_CUSTODY_'+key)
    expected = set(receipt['files']) | {manifest.name}
    if {p.name for p in src.iterdir()} != expected:
        raise ValueError('R99_EXTRA_OR_MISSING_FILES')
    for name, sha in receipt['files'].items():
        if not re.fullmatch(r'[A-Za-z0-9_]+\.(?:css|js|json|html|txt)',name):
            raise ValueError('R99_UNSAFE_FILE_NAME')
        file = src/name
        if file.is_symlink() or not file.is_file() or digest(file.read_bytes()) != sha:
            raise ValueError('R99_SOURCE_HASH:'+name)
    if len(receipt['files']) != 30 or set(VIEWS)-set(receipt['files']):
        raise ValueError('R99_SOURCE_SET')
    return receipt

def review_html(source: str, allowed: set[str]) -> str:
    """Replace ONLY relative resource references, preserving NASA sources and fragments."""
    if source.count('<html') != 1 or source.count('</html>') != 1 or '<img' in source.lower():
        raise ValueError('R99_NON_STANDALONE_OR_IMAGE')
    if re.search(r'<(?:iframe|base|object|embed)\b|\bon\w+\s*=',source,re.I):
        raise ValueError('R99_UNREVIEWED_EXECUTABLE_MARKUP')
    def sub(m: re.Match) -> str:
        attr, ref = m.groups()
        if attr == 'href' and ref.startswith('#') and re.fullmatch(r'#[\w-]+',ref):
            return m.group(0)
        if attr == 'href' and ref.startswith('https://www.nasa.gov/'):
            return m.group(0)
        name, sep, fragment = ref.partition('#')
        if name not in allowed or (fragment and not re.fullmatch(r'[A-Za-z0-9_-]+',fragment)):
            raise ValueError('R99_FORBIDDEN_REFERENCE:'+ref)
        if attr == 'src' and not name.endswith('.js'):
            raise ValueError('R99_FORBIDDEN_SRC:'+ref)
        if attr == 'href' and not name.endswith(('.css','.html','.txt','.json')):
            raise ValueError('R99_FORBIDDEN_HREF:'+ref)
        return attr+'="?fv_apollo_r99='+html.escape(name,quote=True)+('#'+fragment if sep else '')+'"'
    result = RESOURCE.sub(sub,source)
    if re.search(r'\b(?:href|src)="(?:[A-Za-z0-9_]+\.html|[A-Za-z0-9_]+\.(?:css|js))',result):
        raise ValueError('R99_UNROUTED_LOCAL_LINK')
    return result

def build(src: Path, output: Path, php_template: Path, archive: Path | None = None) -> dict:
    original = verify(src)
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError('R99_OUTPUT_NOT_EMPTY')
    if archive and archive.exists():
        raise ValueError('R99_ARCHIVE_EXISTS')
    allowed = {name for name in original['files'] if name.endswith(('.html','.css','.js'))}
    allowed.update({'R93_SOURCE_PASSPORTS.json','R93_NASA_REFERENCES.txt'})
    if any(re.search(r'@import\b|url\s*\(', (src/name).read_text(),re.I) for name in allowed if name.endswith('.css')):
        raise ValueError('R99_CSS_EXTERNAL_ASSET')
    if any(re.search(r'\b(?:fetch|XMLHttpRequest|WebSocket)\s*\(', (src/name).read_text()) for name in allowed if name.endswith('.js')):
        raise ValueError('R99_JS_NETWORK')
    payload: dict[str,bytes] = {}
    for name in sorted(allowed):
        raw=(src/name).read_text(encoding='utf-8')
        if name.endswith('.html'):
            raw=review_html(raw,allowed)
        payload['review/'+name]=raw.encode('utf-8')
    pins = {name.removeprefix('review/'):digest(bytes_) for name,bytes_ in sorted(payload.items())}
    php = php_template.read_text(encoding='utf-8')
    if php.count('/*R99_PIN_MANIFEST*/') != 1:
        raise ValueError('R99_PHP_TEMPLATE_MARKER')
    entries=',\n'.join("        '"+name+"' => '"+sha+"'" for name,sha in pins.items())
    php=php.replace('/*R99_PIN_MANIFEST*/','array(\n'+entries+'\n    )')
    payload['fv-apollo-r99-private-preview.php']=php.encode('utf-8')
    receipt={'schema':'fv.apollo.r99.private-preview.v1','release':'STAGING_HOLD',
             'publication_approved':False,'content_or_settings_writes':0,
             'rights_cleared':0,'images_embedded':0,'geographic_pins':0,
             'source_r98_receipt_sha256':R98_RECEIPT_SHA256,
             'view_count':len(VIEWS),'files':{n:digest(v) for n,v in sorted(payload.items())}}
    payload['R99_PRIVATE_PREVIEW_RECEIPT.json']=(json.dumps(receipt,indent=2,sort_keys=True)+'\n').encode()
    output.mkdir(parents=True,exist_ok=True)
    for name,data in sorted(payload.items()):
        destination=output/name
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes(data)
    if archive:
        archive.parent.mkdir(parents=True,exist_ok=True)
        with ZipFile(archive,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
            for name,data in sorted(payload.items()):
                info=ZipInfo(name,date_time=(1980,1,1,0,0,0))
                info.create_system=3
                info.external_attr=0o100644<<16
                info.compress_type=ZIP_DEFLATED
                z.writestr(info,data)
    return receipt

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--src',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--php-template',type=Path,default=Path(__file__).resolve().parent.parent/'integration/r99-private-preview-template.php')
    parser.add_argument('--archive',type=Path)
    opt=parser.parse_args()
    print(json.dumps(build(opt.src,opt.out,opt.php_template,opt.archive),sort_keys=True))
