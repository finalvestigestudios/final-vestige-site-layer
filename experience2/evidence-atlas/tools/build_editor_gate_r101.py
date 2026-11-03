#!/usr/bin/env python3
"""R101: seal editor-only private Apollo preview from byte-verified R99 input.
Staging only. Never writes WordPress content/settings or alters NASA source assets.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

RECEIPT_NAME = 'R99_PRIVATE_PREVIEW_RECEIPT.json'
PLUGIN = 'fv-apollo-r99-private-preview.php'
R99_RECEIPT_SHA256 = '6373994e3254e4f3153e042466a37f06385cb468cbfed74ff2458abe2bbaebb3'
R99_PLUGIN_SHA256 = 'cd817f705cccfb7dea896d31dee5b2635588d1ae1e4bb57f1e95b494e7be8511'
OLD = "current_user_can('edit_posts')"
NEW = "current_user_can('edit_others_posts')"

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def verified_source(root: Path) -> tuple[dict, dict[str, bytes]]:
    if not root.is_dir() or root.is_symlink():
        raise ValueError('R101_INVALID_R99_ROOT')
    receipt_file = root / RECEIPT_NAME
    if receipt_file.is_symlink() or not receipt_file.is_file() or sha(receipt_file.read_bytes()) != R99_RECEIPT_SHA256:
        raise ValueError('R101_R99_RECEIPT_MISMATCH')
    receipt = json.loads(receipt_file.read_text('utf-8'))
    required = {'schema': 'fv.apollo.r99.private-preview.v1', 'release': 'STAGING_HOLD',
                'publication_approved': False, 'content_or_settings_writes': 0,
                'rights_cleared': 0, 'images_embedded': 0, 'geographic_pins': 0,
                'view_count': 7}
    for name, value in required.items():
        if type(receipt.get(name)) is not type(value) or receipt.get(name) != value:
            raise ValueError('R101_R99_RELEASE_GUARD_' + name)
    file_hashes = receipt.get('files', {})
    if not isinstance(file_hashes, dict) or len(file_hashes) != 22 or file_hashes.get(PLUGIN) != R99_PLUGIN_SHA256:
        raise ValueError('R101_R99_ASSET_COUNT_OR_PLUGIN_PIN')
    allowed = set(file_hashes) | {RECEIPT_NAME}
    observed = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() or p.is_symlink()}
    if observed != allowed:
        raise ValueError('R101_EXTRA_OR_MISSING_ASSET')
    payload = {}
    for name, expected in file_hashes.items():
        if not re.fullmatch(r'(?:review/)?[A-Za-z0-9_\-]+\.(?:html|css|js|json|txt|php)', name):
            raise ValueError('R101_UNSAFE_RESOURCE_PATH')
        f = root / name
        if f.is_symlink() or not f.is_file() or not f.resolve().is_relative_to(root.resolve()):
            raise ValueError('R101_SYMLINK_OR_NONFILE')
        raw = f.read_bytes()
        if sha(raw) != expected:
            raise ValueError('R101_R99_SOURCE_TAMPER_' + name)
        payload[name] = raw
    return receipt, payload

def build(source: Path, output: Path, archive: Path | None = None) -> dict:
    parent, payload = verified_source(source)
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError('R101_OUTPUT_NOT_EMPTY')
    if archive and archive.exists():
        raise ValueError('R101_ARCHIVE_EXISTS')
    php = payload[PLUGIN].decode('utf-8')
    if php.count(OLD) != 1 or php.count(NEW) or php.count('function fv_apollo_r99_permitted()') != 1:
        raise ValueError('R101_PERMISSION_PATCH_ANCHOR_FAILED')
    payload[PLUGIN] = php.replace(OLD, NEW).encode('utf-8')
    receipt = {
        'schema': 'fv.apollo.r101.editor-gate.v1', 'release': 'STAGING_HOLD',
        'publication_approved': False, 'photo_rights_cleared': 0,
        'images_embedded': 0, 'geo_pins': 0, 'inferred_edges': 0,
        'cms_content_or_settings_writes': 0, 'editor_capability': 'edit_others_posts',
        'rejected_roles': ['anonymous', 'subscriber', 'contributor', 'author'],
        'allowed_roles_to_test': ['editor', 'administrator'],
        'original_r99_receipt_sha256': R99_RECEIPT_SHA256,
        'original_r99_plugin_sha256': R99_PLUGIN_SHA256,
        'source_r98_receipt_sha256': parent['source_r98_receipt_sha256'],
        'files': {name: sha(data) for name, data in sorted(payload.items())},
    }
    payload['R101_EDITOR_GATE_RECEIPT.json'] = (json.dumps(receipt, indent=2, sort_keys=True)+'\n').encode()
    output.mkdir(parents=True, exist_ok=True)
    for name, data in sorted(payload.items()):
        file = output / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(data)
    if archive:
        archive.parent.mkdir(parents=True, exist_ok=True)
        with ZipFile(archive, 'w', compression=ZIP_DEFLATED, compresslevel=9) as z:
            for name, data in sorted(payload.items()):
                info = ZipInfo(name, date_time=(1980,1,1,0,0,0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                info.compress_type = ZIP_DEFLATED
                z.writestr(info, data)
    return receipt

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--archive', type=Path)
    opt = parser.parse_args()
    print(json.dumps(build(opt.src, opt.out, opt.archive), sort_keys=True))
