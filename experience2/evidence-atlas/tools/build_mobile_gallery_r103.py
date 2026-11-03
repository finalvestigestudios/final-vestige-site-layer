#!/usr/bin/env python3
"""R103 isolated, rights-safe mobile comparison enhancement over sealed R99 staging.

Never modifies source or WordPress. R99 receipt is retained as a historic INPUT receipt;
R103 receipt is the authoritative manifest of the derived output.
"""
import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

OLD_GALLERY = 'review/R97_SOURCE_GALLERY.html'
OLD_CSS = 'review/source_gallery_r97.css'
OLD_JS = 'review/source_gallery_r97.js'
PHP = 'fv-apollo-r99-private-preview.php'
R99_RECEIPT = 'R99_PRIVATE_PREVIEW_RECEIPT.json'
R103_RECEIPT = 'R103_MOBILE_GALLERY_RECEIPT.json'

CSS_ADD = '''\n/* R103: keyboard- and touch-scrollable comparison at 320–650px. */
.compare-viewport{max-width:100%;overflow-x:auto;overscroll-behavior-inline:contain}
.compare-viewport:focus-visible{outline:3px solid #ffe5a9;outline-offset:2px}
.compare-jump{display:inline-flex;min-height:44px;align-items:center;border:1px solid #f7d18b;padding:.35rem .65rem}
@media(max-width:650px){.compare-viewport table{min-width:680px}.compare-hint{font-size:.9rem;color:#e7d8bf}}
@media(min-width:651px){.compare-hint{display:none}}
@media print{.compare-hint,.compare-jump{display:none!important}}
'''
JS_ADD = '''\n/* R103 enhancement only: native jump links appear after a valid two-source choice. */
(()=>{'use strict';const root=document.querySelector('[data-gallery]');if(!root)return;
const choices=[...root.querySelectorAll('[data-select]')];
const jumps=[...root.querySelectorAll('[data-jump-compare]')];
if(choices.length!==6||jumps.length!==6||!root.querySelector('#comparison'))return;
const refresh=()=>{const ready=choices.filter(x=>x.checked).length===2;
jumps.forEach(x=>{x.hidden=!ready});};
choices.forEach(x=>x.addEventListener('change',()=>queueMicrotask(refresh)));
root.querySelector('#compare-reset')?.addEventListener('click',()=>queueMicrotask(refresh));
refresh();})();
'''


def digest(data):
    return hashlib.sha256(data).hexdigest()


def validate(src):
    if not src.is_dir() or src.is_symlink():
        raise ValueError('R103_SOURCE_DIRECTORY')
    manifest = src / R99_RECEIPT
    if not manifest.is_file() or manifest.is_symlink():
        raise ValueError('R103_NO_R99_RECEIPT')
    receipt = json.loads(manifest.read_bytes())
    if (receipt.get('schema') != 'fv.apollo.r99.private-preview.v1'
        or receipt.get('release') != 'STAGING_HOLD'
        or receipt.get('publication_approved') is not False
        or receipt.get('rights_cleared') != 0
        or receipt.get('images_embedded') != 0
        or receipt.get('geographic_pins') != 0
        or receipt.get('view_count') != 7):
        raise ValueError('R103_RELEASE_BOUNDARY')
    expected = set(receipt['files']) | {R99_RECEIPT}
    actual = {p.relative_to(src).as_posix() for p in src.rglob('*') if p.is_file() or p.is_symlink()}
    if expected != actual:
        raise ValueError('R103_ASSET_INVENTORY')
    for name in sorted(expected):
        if name.startswith('/') or '..' in Path(name).parts or not re.fullmatch(r'[A-Za-z0-9_./-]+', name):
            raise ValueError('R103_INVALID_PATH')
        item = src / name
        if not item.is_file() or item.is_symlink() or any(p.is_symlink() for p in item.parents if p != item.anchor):
            raise ValueError('R103_SYMLINK')
        if name in receipt['files'] and digest(item.read_bytes()) != receipt['files'][name]:
            raise ValueError('R103_INPUT_HASH_MISMATCH:' + name)
    php = (src / PHP).read_text()
    if "current_user_can('edit_others_posts')" not in php or "current_user_can('edit_posts')" in php:
        raise ValueError('R103_EDITOR_CAPABILITY_REGRESSION')
    gallery = (src / OLD_GALLERY).read_text()
    if (gallery.count('https://www.nasa.gov/image-detail/') != 12
        or gallery.count('INDIVIDUAL RIGHTS REVIEW PENDING') != 6
        or gallery.count('data-select') != 6
        or '<img' in gallery or 'data-lat=' in gallery or 'data-geo-edge=' in gallery):
        raise ValueError('R103_SOURCE_CUSTODY_REGRESSION')
    return receipt


def transform(gallery):
    start = '<div id="comparison" hidden><table>'
    new = ('<div id="comparison" hidden>'
           '<p class="compare-hint">Swipe sideways to read both records; keyboard users can focus the table and use arrow keys.</p>'
           '<div class="compare-viewport" role="region" aria-label="Scrollable source comparison" tabindex="0">'
           '<table>')
    if gallery.count(start) != 1:
        raise ValueError('R103_COMPARISON_MARKUP_CHANGED')
    gallery = gallery.replace(start, new)
    end = '</table><p>No photographic reuse has been cleared.</p>'
    if gallery.count(end) != 1:
        raise ValueError('R103_COMPARISON_END_CHANGED')
    gallery = gallery.replace(end, '</table></div><p>No photographic reuse has been cleared.</p>')
    pattern = r'(<label for="compare-(\d{2})">Compare source \2</label>)'
    gallery, count = re.subn(pattern, r'\1<a class="compare-jump" data-jump-compare hidden href="#comparison">View comparison</a>', gallery)
    if count != 6:
        raise ValueError('R103_SIX_JUMPS_REQUIRED')
    return gallery


def build(src, out, archive=None):
    receipt = validate(src)
    if out.exists():
        raise ValueError('R103_OUTPUT_EXISTS')
    if archive is not None and archive.exists():
        raise ValueError('R103_ARCHIVE_EXISTS')
    original_gallery = (src / OLD_GALLERY).read_text()
    gallery = transform(original_gallery)
    css = (src / OLD_CSS).read_text() + CSS_ADD
    js = (src / OLD_JS).read_text() + JS_ADD
    # Current R99 PHP contains compiled-in SHA-256 pins; update exactly two
    # pinned values, never disable checks or make a dynamic resource loader.
    php = (src / PHP).read_text()
    updates = {OLD_GALLERY: gallery.encode(), OLD_CSS: css.encode(), OLD_JS: js.encode()}
    for name, content in updates.items():
        old = receipt['files'][name]
        if php.count("'" + old + "'") != 1:
            raise ValueError('R103_MISSING_COMPILED_PIN:' + name)
        php = php.replace("'" + old + "'", "'" + digest(content) + "'")
    updates[PHP] = php.encode()
    out.mkdir(parents=True)
    for name in sorted(receipt['files']):
        p = out / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(updates.get(name, (src / name).read_bytes()))
    # Preserved as a historical R99 input record, not the current R103 manifest.
    (out / R99_RECEIPT).write_bytes((src / R99_RECEIPT).read_bytes())
    new_receipt = dict(schema='fv.apollo.r103.mobile-gallery.v1', release='STAGING_HOLD',
        publication_approved=False, nasa_photo_rights_cleared=0, images_embedded=0,
        geo_pins=0, inferred_edges=0, records=6, historical_r99_input_receipt_sha256=digest((src / R99_RECEIPT).read_bytes()),
        files={name: digest((out / name).read_bytes()) for name in sorted(receipt['files'])},
        note='Original R99 receipt retained for provenance only; R103 files map is authoritative.')
    (out / R103_RECEIPT).write_text(json.dumps(new_receipt, sort_keys=True, indent=2) + '\n')
    if archive:
        archive.parent.mkdir(parents=True, exist_ok=True)
        with ZipFile(archive, 'w', compression=ZIP_DEFLATED, compresslevel=9) as z:
            for p in sorted(out.rglob('*')):
                if not p.is_file():
                    continue
                info = ZipInfo(p.relative_to(out).as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
                info.create_system = 3; info.external_attr = 0o100644 << 16
                info.compress_type = ZIP_DEFLATED
                z.writestr(info, p.read_bytes())
    return new_receipt


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--src', type=Path, required=True)
    a.add_argument('--out', type=Path, required=True)
    a.add_argument('--archive', type=Path)
    args = a.parse_args()
    print(json.dumps(build(args.src, args.out, args.archive), sort_keys=True))
