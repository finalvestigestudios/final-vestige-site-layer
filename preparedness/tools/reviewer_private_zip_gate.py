#!/usr/bin/env python3
"""R44 private deterministic offline ZIP custody. No disk, network or CMS writes.

The archive merely transports R43's complete, inert HOLD dossier views.
An independently trusted R42 packet fingerprint and R43 manifest fingerprint
are needed for provenance. Self-hashes alone do not authenticate evidence.
"""
from __future__ import annotations

from io import BytesIO
import hashlib
import importlib.util
import json
from pathlib import Path
import re
from zipfile import BadZipFile, ZIP_DEFLATED, ZipFile, ZipInfo

R43 = Path(__file__).with_name('reviewer_offline_html_gate.py')
if not R43.is_file() or R43.is_symlink():
    raise ValueError('R43 exact non-symlinked offline renderer required')
_spec = importlib.util.spec_from_file_location('preparedness_r44_frozen_r43', R43)
if _spec is None or _spec.loader is None:
    raise ValueError('R43 frozen renderer cannot be loaded')
r43 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r43)

EXPECTED = (35, 1, 1959, 367, 43, 30)
COUNT_KEYS = ('articles', 'tools', 'claim_reviews', 'source_scope_reviews',
              'fallback_reviews', 'global_shared_url_reviews')
FLAGS = r43.FLAGS
AUTHORITY = 'PRIVATE_OFFLINE_ZIP_CUSTODY_NOT_EDITORIAL_OR_SAFETY_APPROVAL'
MAX_PLAINTEXT_BYTES = 48 * 1024 * 1024
HEX = re.compile(r'[0-9a-f]{64}\Z')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
FIXED_TIME = (1980, 1, 1, 0, 0, 0)
FILE_MODE = 0o100600 << 16

class PrivateZipHold(ValueError):
    """A private bundle cannot be trusted, opened safely, or approved."""

def need(condition, message):
    if not condition:
        raise PrivateZipHold(message)

def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def pin(value):
    return type(value) is str and HEX.fullmatch(value) is not None and value != '0' * 64

def count_contract(expected):
    need(type(expected) is tuple and len(expected) == 6 and
         all(type(n) is int and n >= 0 for n in expected), 'invalid frozen census')
    return dict(zip(COUNT_KEYS, expected))

def allowed(name):
    if name in ('index.html', 'global-source-variants.html', 'review-manifest.json'):
        return True
    if type(name) is not str or not name.startswith('articles/') or not name.endswith('.html'):
        return False
    return SLUG.fullmatch(name[len('articles/'):-len('.html')]) is not None

def _archive(members):
    """Canonical ZIP: ordered entries, fixed metadata, no added directories."""
    stream = BytesIO()
    with ZipFile(stream, mode='w', compression=ZIP_DEFLATED,
                 compresslevel=9, allowZip64=False) as z:
        for name in sorted(members):
            info = ZipInfo(filename=name, date_time=FIXED_TIME)
            info.compress_type = ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = FILE_MODE
            z.writestr(info, members[name], compress_type=ZIP_DEFLATED,
                       compresslevel=9)
    return stream.getvalue()

def build_private_zip(packet, *, trusted_r42_sha256,
                      expected=EXPECTED, max_plaintext_bytes=MAX_PLAINTEXT_BYTES):
    """Construct private HTML custody ZIP in RAM, never publish or write it.

    For genuine independent provenance, trusted_r42_sha256 must be pinned
    outside the packet. The mandatory CI machine stage only checks the
    internally frozen R37 -> R42 -> R43 -> R44 consistency chain.
    """
    counts = count_contract(expected)
    need(pin(trusted_r42_sha256), 'missing independently controlled R42 pin')
    need(type(max_plaintext_bytes) is int and max_plaintext_bytes > 0,
         'invalid private archive budget')
    try:
        desk = r43.build_offline_html(packet,
               trusted_r42_sha256=trusted_r42_sha256, expected=expected)
    except (r43.OfflineHold, TypeError, ValueError, KeyError) as exc:
        raise PrivateZipHold('upstream R43 dossier evidence is not frozen') from exc
    source_manifest = desk['manifest']
    need(type(source_manifest) is dict and
         source_manifest.get('counts') == counts and
         source_manifest.get('parent_R42_fingerprint_sha256') == trusted_r42_sha256
         and source_manifest.get('release_state') == 'HOLD'
         and all(source_manifest.get(flag) is False for flag in FLAGS),
         'R43 has lost its full private HOLD census')
    pages = desk['html_files']
    need(type(pages) is dict and len(pages) == expected[0] + expected[1] + 2
         and set(pages) == set(source_manifest['files'])
         and all(allowed(name) and name != 'review-manifest.json'
                 and type(content) is str for name, content in pages.items()),
         'unsafe private page path or missing dossier')
    manifest = {
        'schema_version': 1,
        'issue': 136,
        'release_state': 'HOLD',
        'machine_authority': AUTHORITY,
        'source_R43_manifest': source_manifest,
        'parent_R42_fingerprint_sha256': trusted_r42_sha256,
        'parent_R43_fingerprint_sha256': source_manifest['fingerprint_sha256'],
        'file_count_including_manifest': len(pages) + 1,
        'counts': counts,
        'privacy': 'PRIVATE_REVIEW_ONLY_NO_PUBLIC_LINKS_OR_CMS_UPLOAD',
        **{flag: False for flag in FLAGS},
    }
    manifest['fingerprint_sha256'] = sha(canonical(manifest))
    members = {name: body.encode('utf-8') for name, body in pages.items()}
    members['review-manifest.json'] = canonical(manifest) + b'\n'
    need(sum(map(len, members.values())) <= max_plaintext_bytes,
         'private archive exceeds absolute uncompressed byte limit')
    raw = _archive(members)
    checked = verify_private_zip(raw,
                trusted_r42_sha256=trusted_r42_sha256,
                trusted_r43_sha256=source_manifest['fingerprint_sha256'],
                expected=expected, max_plaintext_bytes=max_plaintext_bytes)
    need(checked == manifest, 'private ZIP failed exact readback')
    return {'zip_bytes': raw, 'sha256_zip': sha(raw),
            'manifest': manifest, 'member_count': len(members)}

def verify_private_zip(archive, *, trusted_r42_sha256, trusted_r43_sha256,
                       expected=EXPECTED, max_plaintext_bytes=MAX_PLAINTEXT_BYTES):
    """Read-only adversarial verification against separately trusted pins.

    Reject noncanonical ZIP metadata, duplicate/extra/traversal paths,
    forged approval flags, changed pages, missing rows and unbounded expansion.
    No reviewer status or approval may be inferred from a valid ZIP.
    """
    counts = count_contract(expected)
    need(pin(trusted_r42_sha256) and pin(trusted_r43_sha256),
         'separately pinned source and rendered-manifest evidence required')
    need(type(max_plaintext_bytes) is int and max_plaintext_bytes > 0
         and type(archive) is bytes and 0 < len(archive) <= max_plaintext_bytes,
         'invalid or oversized private ZIP bytes')
    try:
        with ZipFile(BytesIO(archive), 'r', allowZip64=False) as z:
            infos = z.infolist()
            names = [item.filename for item in infos]
            need(len(names) == expected[0] + expected[1] + 3
                 and len(names) == len(set(names))
                 and all(allowed(name) for name in names)
                 and 'review-manifest.json' in names and 'index.html' in names
                 and 'global-source-variants.html' in names
                 and not z.comment, 'lost, duplicated, hidden or unsafe ZIP members')
            total = 0
            for item in infos:
                need(item.date_time == FIXED_TIME and item.create_system == 3
                     and item.external_attr == FILE_MODE and
                     item.compress_type == ZIP_DEFLATED
                     and item.flag_bits & 1 == 0 and not item.extra and not item.comment
                     and item.file_size <= max_plaintext_bytes
                     and item.file_size >= 0 and item.compress_size >= 0,
                     'unsafe ZIP metadata or encrypted member')
                total += item.file_size
                need(total <= max_plaintext_bytes,
                     'private ZIP would exceed uncompressed byte budget')
            members = {name: z.read(name) for name in names}
    except (BadZipFile, EOFError, OSError, RuntimeError, UnicodeError,
            NotImplementedError, OverflowError) as exc:
        raise PrivateZipHold('corrupt or unsupported private ZIP') from exc
    need(sum(len(v) for v in members.values()) <= max_plaintext_bytes
         and _archive(members) == archive,
         'noncanonical ZIP, appended payload or altered record')
    raw_manifest = members.pop('review-manifest.json')
    try:
        manifest = json.loads(raw_manifest.decode('utf-8'))
        need(type(manifest) is dict and
             raw_manifest == canonical(manifest) + b'\n',
             'manifest is not strict canonical UTF-8 JSON')
    except (ValueError, UnicodeError, TypeError, OverflowError) as exc:
        raise PrivateZipHold('invalid manifest data') from exc
    need(manifest.get('schema_version') == 1 and manifest.get('issue') == 136
         and manifest.get('release_state') == 'HOLD'
         and manifest.get('machine_authority') == AUTHORITY
         and manifest.get('privacy') == 'PRIVATE_REVIEW_ONLY_NO_PUBLIC_LINKS_OR_CMS_UPLOAD'
         and manifest.get('counts') == counts
         and manifest.get('file_count_including_manifest') == len(members) + 1
         and manifest.get('parent_R42_fingerprint_sha256') == trusted_r42_sha256
         and manifest.get('parent_R43_fingerprint_sha256') == trusted_r43_sha256
         and all(manifest.get(flag) is False for flag in FLAGS)
         and manifest.get('fingerprint_sha256') ==
             sha(canonical({k: v for k, v in manifest.items() if k != 'fingerprint_sha256'})),
         'altered, unpinned or falsely approved private bundle manifest')
    source = manifest.get('source_R43_manifest')
    need(type(source) is dict and source.get('fingerprint_sha256') == trusted_r43_sha256
         and source.get('parent_R42_fingerprint_sha256') == trusted_r42_sha256
         and source.get('release_state') == 'HOLD'
         and source.get('counts') == counts
         and source.get('machine_authority') ==
             'OFFLINE_UNVERIFIED_EVIDENCE_PRESENTATION_NOT_APPROVAL'
         and all(source.get(flag) is False for flag in FLAGS)
         and source.get('fingerprint_sha256') ==
             sha(canonical({k: v for k, v in source.items() if k != 'fingerprint_sha256'}))
         and type(source.get('files')) is dict
         and set(source['files']) == set(members),
         'R43 trusted source manifest was altered, lost or made public')
    for name, raw in members.items():
        expected_entry = source['files'][name]
        need(type(expected_entry) is dict
             and expected_entry == {'sha256_utf8': sha(raw), 'bytes_utf8': len(raw)},
             'missing, altered or collapsed source-reading HTML bytes')
        try:
            body = raw.decode('utf-8')
        except UnicodeError as exc:
            raise PrivateZipHold('non-UTF8 source HTML is not allowed') from exc
        need(body.startswith('<!doctype html>') and
             'PRIVATE / UNVERIFIED / HOLD' in body and
             "connect-src 'none'" in body and
             '<script' not in body.lower() and '<iframe' not in body.lower()
             and '<form' not in body.lower(),
             'private inert HTML HOLD evidence replaced or made interactive')
    return manifest
