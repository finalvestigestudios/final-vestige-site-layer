#!/usr/bin/env python3
"""Read-only, fail-closed custody intake for E395 Article #11 editorial export.

Purpose: bind an *external, unpublished* editorial ZIP and its WP-oriented HTML
to the immutable SHA-256 receipts reported in FV issue #136, without copying,
executing, publishing, or deeming any food-safety claim safe. An archive integrity
PASS is never qualified food-safety/QD approval. No extracted files are written.
"""
from __future__ import annotations

import argparse
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import unicodedata
from zipfile import BadZipFile, ZipFile

STATE = 'DRAFT_HARD_HOLD'
ISSUE = 'https://github.com/finalvestigestudios/final-vestige-site-layer/issues/136'
ARTICLE_MEMBER = 'E395_ARTICLE11_SOURCE_SCOPE_WORDPRESS_HARD_HOLD.html'
ARCHIVE_SHA256 = '21a2142c6050eb3bae020c67744ee82439d854525ba63915ea9092a0b7bba46b'
ARTICLE_SHA256 = 'bc0537e611d35b195e10ee49ceb9772a904b7c8fea0749a6203da38e835f8184'
MAX_ZIP = 32 * 1024 * 1024
MAX_FILES = 200
MAX_MEMBER = 8 * 1024 * 1024
MAX_TOTAL = 40 * 1024 * 1024
MAX_RATIO = 2000
_ALLOWED_EXTENSION = frozenset({'.html', '.htm', '.txt', '.md', '.json', '.csv', '.png', '.jpg', '.jpeg', '.webp', '.svg', '.pdf', '.sha256', '.css'})
_SHA = re.compile(r'[0-9a-f]{64}\Z')
_WINDOWS_DEVICES = frozenset({'CON', 'PRN', 'AUX', 'NUL'} |
                            {f'COM{i}' for i in range(1, 10)} |
                            {f'LPT{i}' for i in range(1, 10)})


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _safe_components(name: str, *, directory: bool) -> bool:
    """Accept only stable, portable POSIX member paths (no filesystem writes).

    ZIP parsers and future preview consumers may disagree about Unicode,
    directory entries and Windows device names. Reject such ambiguous names
    before an archive is admitted as a custody receipt.
    """
    if not isinstance(name, str) or not name or len(name) > 300:
        return False
    if name.endswith('/') != directory:
        return False
    body = name[:-1] if directory else name
    if not body or body.startswith('/') or unicodedata.normalize('NFC', body) != body:
        return False
    if any(c in body for c in ('\\', ':', '<', '>', '|', '?', '*', '"')):
        return False
    parts = body.split('/')
    if any(part in ('', '.', '..') or part.startswith('.') or
           part.endswith(('.', ' ')) or
           part.partition('.')[0].upper() in _WINDOWS_DEVICES
           for part in parts):
        return False
    if any(unicodedata.category(c) in ('Cc', 'Cf', 'Cs') for c in body):
        return False
    return True


def safe_name(name: str) -> bool:
    """Safely admit a *file* member with a passive preview extension."""
    return (_safe_components(name, directory=False) and
            PurePosixPath(name).suffix.lower() in _ALLOWED_EXTENSION)


def safe_directory_name(name: str) -> bool:
    """Check actual directory entries, not disguised .txt filenames."""
    return _safe_components(name, directory=True)


def canonical_member(name: str) -> str:
    """Normalize identity across Unicode compatibility and case differences."""
    return unicodedata.normalize('NFKC', name.rstrip('/')).casefold()


def report(failures: list[str], *, archive_size: int | None = None,
           article_present: bool = False, archive_matches_pin: bool = False,
           article_matches_pin: bool = False, members: int = 0) -> dict:
    return {
        'schema': 'r402.external-e395-custody.v1',
        'archive_integrity': 'FAIL' if failures else 'PASS',
        'release': STATE,
        'eligible': False,
        'qualified_food_safety_review': 'NOT_GRANTED',
        'human_content_review': 'NOT_PERFORMED',
        'origin': ISSUE,
        'archive_bytes': archive_size,
        'archive_sha256_matched': archive_matches_pin,
        'article_html_found': article_present,
        'article_sha256_matched': article_matches_pin,
        'archive_member_count': members,
        'failures': sorted(set(failures)),
    }


def inspect(raw: bytes, *, expected_zip_sha: str = ARCHIVE_SHA256,
            expected_article_sha: str = ARTICLE_SHA256) -> dict:
    """Pure in-memory review; SHA overrides exist for synthetic tests ONLY."""
    f: list[str] = []
    if not isinstance(raw, bytes) or len(raw) > MAX_ZIP or not raw:
        return report(['missing_or_oversized_zip'], archive_size=len(raw) if isinstance(raw, bytes) else None)
    if not (isinstance(expected_zip_sha, str) and _SHA.fullmatch(expected_zip_sha) and
            isinstance(expected_article_sha, str) and _SHA.fullmatch(expected_article_sha)):
        return report(['invalid_expected_sha256'], archive_size=len(raw))
    zip_match = sha256(raw) == expected_zip_sha
    if not zip_match:
        f.append('zip_sha256_mismatch')
    found: list[bytes] = []
    member_count = 0
    try:
        with ZipFile(BytesIO(raw)) as zf:
            infos = zf.infolist()
            member_count = len(infos)
            # Fail before member reads if a central-directory flood is detected.
            if not infos or len(infos) > MAX_FILES:
                return report(f + ['zip_member_count'], archive_size=len(raw),
                              archive_matches_pin=zip_match, members=member_count)
            seen: set[str] = set()
            files: set[str] = set()
            directories: set[str] = set()
            total = 0
            for info in infos:
                name = info.filename
                directory = info.is_dir()
                if not (safe_directory_name(name) if directory else safe_name(name)):
                    f.append('unsafe_directory_name' if directory else 'unsafe_member_name')
                    continue
                comparable = canonical_member(name)
                if comparable in seen:
                    f.append('duplicate_canonical_member')
                    continue
                seen.add(comparable)
                mode = (info.external_attr >> 16) & 0xffff
                kind = stat.S_IFMT(mode)
                if directory:
                    # For ZIPs, directory spelling is not proof of a directory
                    # inode type: a symlink can masquerade as a trailing-slash
                    # entry. Check metadata before ignoring its payload.
                    if kind not in (0, stat.S_IFDIR):
                        f.append('non_directory_member')
                    if info.file_size != 0:
                        f.append('nonempty_directory_member')
                    directories.add(comparable)
                    continue
                files.add(comparable)
                if (stat.S_IFMT(mode) not in (0, stat.S_IFREG)):
                    f.append('non_regular_member')
                    continue
                if info.flag_bits & 0x1:
                    f.append('encrypted_member')
                    continue
                total += info.file_size
                if info.file_size > MAX_MEMBER or total > MAX_TOTAL:
                    f.append('unbounded_member_size')
                    continue
                if info.file_size > MAX_RATIO * max(1, info.compress_size):
                    f.append('suspicious_compression_ratio')
                    continue
                # Decompress only bounded, safe members; never extract to disk.
                try:
                    with zf.open(info, 'r') as fh:
                        chunk = fh.read(MAX_MEMBER + 1)
                    if len(chunk) != info.file_size:
                        f.append('member_byte_count_mismatch')
                        continue
                except (RuntimeError, BadZipFile, OSError, EOFError, ValueError):
                    f.append('unreadable_member')
                    continue
                if PurePosixPath(name).name == ARTICLE_MEMBER:
                    found.append(chunk)
            # Distinct spellings of a parent file and a child path must not be
            # interpreted as separate safe identities by a later extractor.
            for path in files | directories:
                parts = path.split('/')
                if any('/'.join(parts[:j]) in files for j in range(1, len(parts))):
                    f.append('file_directory_path_collision')
                    break
            if files & directories:
                f.append('file_directory_identity_collision')
    except (BadZipFile, OSError, RuntimeError, EOFError, ValueError, OverflowError):
        return report(f + ['invalid_zip'], archive_size=len(raw), archive_matches_pin=zip_match)
    if len(found) != 1:
        f.append('article_identity_cardinality')
    article_match = len(found) == 1 and sha256(found[0]) == expected_article_sha
    if len(found) == 1 and not article_match:
        f.append('article_sha256_mismatch')
    return report(f, archive_size=len(raw), article_present=bool(found),
                  archive_matches_pin=zip_match, article_matches_pin=article_match,
                  members=member_count)



def read_bounded_original(path: Path) -> bytes:
    """Open only a single-link regular ZIP without following symlinks, bounded in RAM.

    This protects the integration runner from an attacker-supplied enormous path;
    immutable SHA pins in inspect() separately catch content replacement.
    """
    if not hasattr(os, 'O_NOFOLLOW'):
        raise ValueError('safe_nofollow_open_unsupported')
    flags = os.O_RDONLY | os.O_NOFOLLOW
    if hasattr(os, 'O_CLOEXEC'):
        flags |= os.O_CLOEXEC
    fd = os.open(path, flags)
    try:
        before = os.fstat(fd)
        if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or
                before.st_size < 1 or before.st_size > MAX_ZIP):
            raise ValueError('unsafe_original_archive_file')
        with os.fdopen(fd, 'rb') as fh:
            fd = -1
            data = fh.read(MAX_ZIP + 1)
            after = os.fstat(fh.fileno())
            if (len(data) != before.st_size or len(data) > MAX_ZIP or
                    fh.read(1) or after.st_size != before.st_size or
                    after.st_ino != before.st_ino or after.st_dev != before.st_dev):
                raise ValueError('changed_or_unbounded_original_archive')
            return data
    finally:
        if fd >= 0:
            os.close(fd)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--e395-zip', type=Path, required=True,
                   help='Original local E395 editorial ZIP; read-only, never extracted')
    args = p.parse_args(argv)
    try:
        raw = read_bounded_original(args.e395_zip)
    except (OSError, ValueError):
        print(json.dumps(report(['missing_original_e395_zip']), sort_keys=True))
        return 2
    print(json.dumps(inspect(raw), sort_keys=True))
    return 2  # IMPORTANT: even cryptographic custody PASS never grants QD/publish.


if __name__ == '__main__':
    raise SystemExit(main())
