#!/usr/bin/env python3
"""Normalize Automattic's official assembler-wpcom ZIP into the reviewed local assembler mount.

Never downloads, installs or activates a theme. Rejects unsafe and unexpected ZIP entries.
A re-rooted archive is a derived, byte-content-preserving local *test fixture*, not an
independently signed official package. Preserve both SHA-256 values in a receipt.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import stat
import zipfile
from pathlib import Path, PurePosixPath

MAX_FILES = 4000
MAX_BYTES = 80 * 1024 * 1024
ORIGINAL_ROOT = 'assembler-wpcom'
CANONICAL_ROOT = 'assembler'


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(source: Path, destination: Path, receipt_path: Path) -> dict:
    if (source.is_symlink() or not source.is_file() or destination.is_symlink()
            or receipt_path.is_symlink() or source.resolve() == destination.resolve()):
        raise ValueError('HOLD: unsafe Assembler inputs or target')
    upstream_sha = sha256(source)
    extracted: dict[str, bytes] = {}
    names: set[str] = set()
    total = 0
    with zipfile.ZipFile(source) as archive:
        info = archive.infolist()
        if not info or len(info) > MAX_FILES:
            raise ValueError('HOLD: unexpected theme ZIP entry count')
        for member in info:
            name = member.filename
            parts = PurePosixPath(name).parts
            if (name.startswith('/') or '\\' in name or not parts
                    or parts[0] != ORIGINAL_ROOT or
                    any(p in ('.', '..', '') for p in parts)):
                raise ValueError('HOLD: unexpected unsafe theme ZIP path ' + name[:120])
            if member.is_dir():
                continue
            if len(parts) < 2:
                raise ValueError('HOLD: unexpected root member')
            mode = member.external_attr >> 16
            if stat.S_ISLNK(mode) or (mode and not stat.S_ISREG(mode) and member.create_system == 3):
                raise ValueError('HOLD: unexpected theme entry file type')
            rel = PurePosixPath(*parts[1:]).as_posix()
            folded = rel.casefold()
            if folded in names:
                raise ValueError('HOLD: case-folding theme entry collision')
            names.add(folded)
            total += member.file_size
            if total > MAX_BYTES or member.file_size > MAX_BYTES:
                raise ValueError('HOLD: excessive theme archive contents')
            if member.compress_size == 0 and member.file_size > 0:
                raise ValueError('HOLD: impossible ZIP file size')
            payload = archive.read(member)
            if len(payload) != member.file_size:
                raise ValueError('HOLD: truncated theme entry')
            extracted[rel] = payload
    if not {'style.css', 'templates/index.html'}.issubset(extracted):
        raise ValueError('HOLD: theme lacks canonical style.css or index template')
    style = extracted['style.css'].decode('utf-8', errors='strict')
    if not re.search(r'(?mi)^\s*Theme Name:\s*Assembler\s*$', style):
        raise ValueError('HOLD: not the official Assembler theme identity')
    if not re.search(r'(?mi)^\s*Version:\s*0\.0\.126\s*$', style):
        raise ValueError('HOLD: site Assembler 0.0.126 version parity not proven')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, mode='w') as out:
        for rel, raw in sorted(extracted.items()):
            entry = zipfile.ZipInfo(CANONICAL_ROOT + '/' + rel, (1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.create_system = 3
            entry.external_attr = (stat.S_IFREG | 0o644) << 16
            out.writestr(entry, raw)
    # The theme ZIP original SHA proves which bytes were downloaded, not authorship,
    # licensing, or compatibility with WordPress.com Atomic infrastructure.
    result = {
        'source_zip_sha256': upstream_sha,
        'derived_canonical_zip_sha256': sha256(destination),
        'source_root': ORIGINAL_ROOT,
        'derived_root': CANONICAL_ROOT,
        'files': len(extracted),
        'unpacked_bytes': total,
        'file_contents_byte_preserved': True,
        'theme_version': '0.0.126',
        'official_authorship_independent_signoff': 'NOT_VERIFIED',
        'wordpress_rendered': 'NOT_YET',
        'release': 'HOLD'
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--derived', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    a = parser.parse_args()
    print(json.dumps(normalize(a.source, a.derived, a.receipt), indent=2))
