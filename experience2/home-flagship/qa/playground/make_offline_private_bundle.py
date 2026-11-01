#!/usr/bin/env python3
"""Build a private, self-contained WordPress Playground bundle from APPROVED sources.

Fixes network-dependent theme/media loading at stage time. Bundles ONLY
public-facing Gutenberg content, the reviewed Assembler theme ZIP, and three
locally reviewed archival images. Never downloads, deploys, or writes production.
Does not establish reproduction rights, certify WordPress, or bypass the existing
integrated Blueprint integrity gate.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import zipfile
from launch_integrated_staging import check_blueprint, check_manifest, MEDIA_SOURCES, SITE_PREFIX, THEME_URL, require

FILES = ('apollo.webp', 'franklin.jpg', 'nypl.jpg')
ENTRIES = ('blueprint.json', 'assembler.zip', *(f'media/{name}' for name in FILES))


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def private_read(path: Path, label: str) -> bytes:
    require(path.is_file() and not path.is_symlink(), f'{label}: regular file required')
    if os.name == 'posix':
        require(not (path.stat().st_mode & 0o077), f'{label}: file must be chmod 600')
    return path.read_bytes()


def validate_theme(raw: bytes, expected_sha: str) -> dict:
    """Admit an unambiguous, fully readable Assembler archive before stage install.

    An independently reviewed whole-ZIP SHA is necessary but not sufficient:
    duplicate, platform-ambiguous, or corrupt members leave uncertainty about
    which bytes a ZIP consumer will actually extract. Fail closed on ambiguity.
    """
    require(len(expected_sha) == 64 and all(x in '0123456789abcdef' for x in expected_sha),
            'independently approved theme ZIP SHA-256 required')
    require(digest(raw) == expected_sha, 'Assembler theme ZIP SHA-256 mismatch')
    with zipfile.ZipFile(__import__('io').BytesIO(raw)) as archive:
        info = archive.infolist()
        require(1 <= len(info) <= 2500 and sum(x.file_size for x in info) < 100_000_000,
                'theme ZIP entry count/uncompressed size exceeds review budget')
        seen = set()
        for entry in info:
            name = entry.filename
            require(name and not any(c in name for c in ('\\', '\x00', ':')),
                    'theme ZIP platform-ambiguous or invalid member name')
            require(not name.startswith('/') and not name.startswith('//') and
                    all(part not in ('', '.', '..') for part in name.rstrip('/').split('/')),
                    'theme ZIP noncanonical path or traversal')
            require(name == str(PurePosixPath(name)) + ('/' if entry.is_dir() else ''),
                    'theme ZIP noncanonical member spelling')
            parts = PurePosixPath(name).parts
            require(parts and parts[0] == 'assembler', 'theme ZIP path outside assembler/')
            require(not stat.S_ISLNK(entry.external_attr >> 16),
                    'theme ZIP symbolic link forbidden')
            require(not (entry.flag_bits & 1), 'theme ZIP encrypted member forbidden')
            require(entry.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED),
                    'theme ZIP unsupported member compression')
            key = name.rstrip('/').casefold()
            require(key not in seen, 'theme ZIP duplicate or case-colliding member')
            seen.add(key)
            if entry.is_dir():
                require(entry.file_size == 0, 'theme ZIP directory contains bytes')
        names = {x.filename for x in info}
        require({'assembler/style.css', 'assembler/theme.json', 'assembler/templates/index.html'} <= names,
                'theme ZIP does not contain required Assembler block-theme files')
        require(archive.testzip() is None, 'theme ZIP member CRC/decompression failure')
        require('Theme Name: Assembler' in archive.read('assembler/style.css').decode('utf-8'),
                'theme style.css does not identify Assembler')
    return {'sha256': digest(raw), 'bytes': len(raw), 'archive_entries': len(info),
            'all_member_crcs_verified': True, 'names_unique_casefold': True,
            'reviewed_origin': THEME_URL}


def package(blueprint: Path, blueprint_sha: str, media_manifest: Path,
            media_directory: Path, theme_zip: Path, theme_sha: str, output_zip: Path) -> dict:
    require(output_zip.suffix == '.zip', 'private output must be a ZIP bundle')
    require(output_zip.parent.is_dir() and not output_zip.parent.is_symlink(),
            'private output directory must already exist')
    if os.name == 'posix':
        require(not (output_zip.parent.stat().st_mode & 0o077),
                'private output directory needs chmod 700')
    require(not output_zip.exists() and not output_zip.is_symlink(),
            'refuse overwrite or symlink output')
    require(media_directory.is_dir() and not media_directory.is_symlink(),
            'private image directory required')
    # Reuse the EXACT parent PR #451 staging admission code, not an alternative verifier.
    original = check_blueprint(blueprint, blueprint_sha)
    check_manifest(media_manifest)
    trusted = json.loads(private_read(media_manifest, 'independent original-image manifest'))['images']
    source = json.loads(private_read(blueprint, 'exact original integrated Blueprint'))
    theme_raw = private_read(theme_zip, 'official reviewed Assembler theme')
    theme_identity = validate_theme(theme_raw, theme_sha)
    images = {}
    identity = {}
    for name in FILES:
        raw = private_read(media_directory / name, name)
        approved = trusted[name]
        url, expected_bytes = MEDIA_SOURCES[name]
        require(approved['source_url'] == url and len(raw) == expected_bytes
                and digest(raw) == approved['sha256'], name + ': original SHA/length mismatch')
        if name.endswith('.jpg'):
            require(raw.startswith(b'\xff\xd8\xff'), name + ': invalid JPEG signature')
        else:
            require(raw[:4] == b'RIFF' and raw[8:12] == b'WEBP',
                    name + ': invalid WebP signature')
        images[name] = raw
        identity[name] = {'sha256': digest(raw), 'bytes': len(raw),
                          'source_url': url, 'reproduction_rights': 'NOT_CLEARED_BY_THIS_TOOL'}
    rewritten = deepcopy(source)
    steps = rewritten['steps']
    require(steps[1]['themeData'] == {'resource': 'url', 'url': THEME_URL},
            'unexpected theme source before offline substitution')
    steps[1]['themeData'] = {'resource': 'bundled', 'path': '/assembler.zip'}
    for step in steps:
        dest = step.get('path', '')
        for name in FILES:
            if dest.endswith('/media/' + name):
                require(step.get('data') == {'resource': 'url', 'url': MEDIA_SOURCES[name][0]},
                        name + ': unexpected source before offline substitution')
                step['data'] = {'resource': 'bundled', 'path': '/media/' + name}
    bundle = json.dumps(rewritten, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    parts = {'blueprint.json': bundle, 'assembler.zip': theme_raw,
             **{f'media/{name}': images[name] for name in FILES}}
    require(tuple(parts) == ENTRIES and len(steps) == 19,
            'unexpected bundle inventory or step drift')
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, 'O_NOFOLLOW'):
        flags |= os.O_NOFOLLOW
    fd = os.open(output_zip, flags, 0o600)
    try:
        with os.fdopen(fd, 'wb') as stream, zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_DEFLATED) as result:
            for name in ENTRIES:
                meta = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
                meta.compress_type = zipfile.ZIP_DEFLATED
                meta.external_attr = 0o600 << 16
                result.writestr(meta, parts[name])
    except Exception:
        output_zip.unlink(missing_ok=True)
        raise
    with zipfile.ZipFile(output_zip) as result:
        require(result.namelist() == list(ENTRIES) and
                all(result.read(name) == parts[name] for name in ENTRIES),
                'ZIP did not round-trip all reviewed bytes')
    return {'status': 'PRIVATE_OFFLINE_BUNDLE_BUILT_NOT_WORDPRESS_EXECUTED',
            'source_blueprint': original, 'bundle_sha256': digest(output_zip.read_bytes()),
            'bundle_bytes': output_zip.stat().st_size,
            'rewritten_steps': [1, 14, 15, 16],
            'private_bundle_entries': list(ENTRIES),
            'theme': theme_identity, 'images': identity,
            'wordpress_rendered': False, 'axe_tested': False,
            'lighthouse_measured': False, 'rights_cleared': False,
            'hosted_equivalence': False, 'ci_qd_passed': False}


def main():
    parser = argparse.ArgumentParser(description='Create offline private WordPress Playground Blueprint bundle')
    parser.add_argument('--blueprint', type=Path, required=True)
    parser.add_argument('--blueprint-sha256', required=True)
    parser.add_argument('--media-manifest', type=Path, required=True)
    parser.add_argument('--media-dir', type=Path, required=True)
    parser.add_argument('--assembler-zip', type=Path, required=True)
    parser.add_argument('--assembler-sha256', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    receipt = {'status': 'FAILED_CLOSED', 'run_utc': datetime.now(timezone.utc).isoformat()}
    try:
        receipt.update(package(args.blueprint, args.blueprint_sha256, args.media_manifest,
                               args.media_dir, args.assembler_zip, args.assembler_sha256, args.out))
    except Exception as exc:
        receipt.update({'error_type': type(exc).__name__, 'reason': str(exc)[:500]})
    dest = args.out.with_suffix('.receipt.json')
    if dest.exists():
        raise SystemExit('Refuse overwrite existing receipt')
    fd = os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as output:
        json.dump(receipt, output, indent=2)
        output.write('\n')
    print(json.dumps({'status': receipt['status'], 'bundle_sha256': receipt.get('bundle_sha256'),
                      'error': receipt.get('reason')}, indent=2))
    return 0 if receipt['status'] == 'PRIVATE_OFFLINE_BUNDLE_BUILT_NOT_WORDPRESS_EXECUTED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
