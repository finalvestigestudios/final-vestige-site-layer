#!/usr/bin/env python3
"""R77 exact-head, deterministic, non-deploying Apollo source archive."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path

FILES = (
    '.github/workflows/ex2-apollo-real-wp.yml',
    'experience2/evidence-atlas/R77_SYNCED_PATTERN_STAGING_HOLD.md',
    'experience2/evidence-atlas/integration/fv-ex2-apollo-suite.php',
    'experience2/evidence-atlas/tests/build_review_r77.py',
    'experience2/evidence-atlas/tests/test_build_review_r77.py',
    'experience2/evidence-atlas/tests/test_nested_reusable_r77.php',
    'experience2/evidence-atlas/tests/test_wp_loopback_r72.py',
    'experience2/evidence-atlas/tests/wordpress_r68.py',
    'experience2/evidence-atlas/tests/wp_reusable_r77.py',
)

def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(('git', '-C', str(root), *args), stderr=subprocess.DEVNULL)

def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()

def build(root: Path, head: str, destination: Path, files=FILES) -> dict:
    root = root.resolve(strict=True)
    destination = destination.resolve()
    if not re.fullmatch(r'[0-9a-f]{40}', head):
        raise ValueError('R77_INVALID_HEAD')
    if git(root, 'rev-parse', 'HEAD').decode().strip() != head or git(root, 'status', '--porcelain').strip():
        raise ValueError('R77_DIRTY_OR_DIFFERENT_HEAD')
    if destination == root or root in destination.parents:
        raise ValueError('R77_OUTPUT_INSIDE_REPOSITORY')
    if tuple(files) != tuple(sorted(set(files))) or not files:
        raise ValueError('R77_FILE_ALLOWLIST_INVALID')
    entries = {}
    for name in files:
        path = root / name
        if not path.is_file() or path.is_symlink() or '..' in Path(name).parts:
            raise ValueError('R77_MISSING_OR_UNSAFE_FILE')
        observed = path.read_bytes()
        if observed != git(root, 'show', head + ':' + name):
            raise ValueError('R77_NOT_EXACT_HEAD_BYTES')
        entries[name] = {'sha256': hashlib.sha256(observed).hexdigest(),
                         'git_blob_sha1': blob_sha(observed), 'bytes': len(observed)}
    manifest = {'schema': 'fv.apollo.r77.deterministic-source.v1',
                'head': head, 'release': 'STAGING_HOLD',
                'production_deployed': False, 'hosted_wp_verified': False,
                'photo_rights_cleared': 0, 'files': entries}
    canonical = (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_STORED) as archive:
        for name in sorted(entries):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (root / name).read_bytes())
        info = zipfile.ZipInfo('R77_SOURCE_MANIFEST.json', date_time=(1980, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_STORED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, canonical)
    return {'sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
            'bytes': destination.stat().st_size, 'entries': len(entries),
            'head': head, 'production_deployed': False}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--repo',required=True,type=Path)
    parser.add_argument('--head',required=True)
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args()
    print(json.dumps(build(args.repo,args.head,args.out),sort_keys=True))

if __name__ == '__main__':
    main()
