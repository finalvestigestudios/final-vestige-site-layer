#!/usr/bin/env python3
"""Quarantine PUBLIC source files needed for isolated FV WordPress QA.

Output is a CANDIDATE inventory, never rights clearance or an approved hash
manifest. No CMS API, production writes, secrets, subscribers, or user data.
Use a networked developer machine and an existing chmod-700 private directory.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from launch_integrated_staging import MEDIA_SOURCES, THEME_URL, require
from make_offline_private_bundle import validate_theme

MAX_THEME_BYTES = 20_000_000
ALLOWED_HOSTS = {'public-api.wordpress.com', 'finalvestige.com'}
ACCEPT = {'image/jpeg', 'image/webp', 'application/zip',
          'application/x-zip-compressed', 'application/octet-stream'}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def fetch_binary(url: str, limit: int, *, opener=None) -> tuple[bytes, str]:
    target = urlsplit(url)
    require(target.scheme == 'https' and target.hostname in ALLOWED_HOSTS and
            not target.username and not target.password and not target.fragment and
            target.port in (None, 443), 'unapproved transport/source hostname')
    request = Request(url, headers={'Accept': 'application/octet-stream,image/jpeg,image/webp',
                                   'User-Agent': 'FinalVestigeStagingCustody/1.0'}, method='GET')
    client = opener if opener is not None else build_opener(NoRedirect())
    with client.open(request, timeout=25) as response:
        require(response.status == 200 and response.geturl() == url,
                'non-200 response or redirect/substituted host')
        ctype = response.headers.get('Content-Type', '').split(';', 1)[0].strip().lower()
        require(ctype in ACCEPT, 'unexpected MIME type (possible error page)')
        declared = response.headers.get('Content-Length')
        if declared is not None:
            require(declared.isdigit() and 0 < int(declared) <= limit,
                    'declared transfer size outside approved limit')
        data = response.read(limit + 1)
    require(0 < len(data) <= limit and (declared is None or len(data) == int(declared)),
            'short, empty, or oversized transfer')
    return data, ctype


def stage_candidates(private_dir: Path, *, opener=None) -> dict:
    require(private_dir.is_dir() and not private_dir.is_symlink(),
            'existing private workspace required')
    if os.name == 'posix':
        require(private_dir.stat().st_mode & 0o077 == 0, 'workspace must be chmod 700')
    output = private_dir / 'fv-source-quarantine'
    require(not output.exists() and not output.is_symlink(), 'refuse overwrite of candidates')
    # Fetch and check ALL responses before writing any files.
    theme_bytes, theme_mime = fetch_binary(THEME_URL, MAX_THEME_BYTES, opener=opener)
    theme_sha = hashlib.sha256(theme_bytes).hexdigest()
    theme_check = validate_theme(theme_bytes, theme_sha)
    media = {}
    for filename, (url, expected_bytes) in MEDIA_SOURCES.items():
        raw, mime = fetch_binary(url, expected_bytes, opener=opener)
        require(len(raw) == expected_bytes, filename + ': original byte-length mismatch')
        if filename.endswith('.webp'):
            require(mime == 'image/webp' and raw[:4] == b'RIFF' and raw[8:12] == b'WEBP',
                    filename + ': unexpected WebP response')
        else:
            require(mime == 'image/jpeg' and raw.startswith(b'\xff\xd8\xff'),
                    filename + ': unexpected JPEG response')
        media[filename] = {'raw': raw, 'url': url, 'mime': mime,
                           'sha256': hashlib.sha256(raw).hexdigest()}
    candidate = {'status': 'UNREVIEWED_CANDIDATES_NOT_RELEASE_ADMITTED',
                 'collected_utc': datetime.now(timezone.utc).isoformat(),
                 'source_policy': 'fixed HTTPS official/public originals; redirects forbidden',
                 'rights_cleared': False, 'sha_independently_approved': False,
                 'wordpress_rendered': False, 'production_changes': False,
                 'theme': {'source_url': THEME_URL, 'sha256': theme_sha,
                           'bytes': len(theme_bytes), 'mime': theme_mime,
                           'structure_checked': bool(theme_check['all_member_crcs_verified']),
                           'rights_review': 'Theme appears distributed by Automattic; exact WP.com deployed revision not confirmed'},
                 'images': {name: {'source_url': item['url'], 'sha256': item['sha256'],
                                   'bytes': len(item['raw']), 'mime': item['mime'],
                                   'reproduction_rights': 'NOT_CLEARED'}
                            for name, item in media.items()}}
    temp = Path(tempfile.mkdtemp(prefix='.fv-quarantine-', dir=private_dir))
    try:
        image_dir = temp / 'media'
        image_dir.mkdir(mode=0o700)
        files = {'assembler.zip': theme_bytes,
                 **{'media/' + name: item['raw'] for name, item in media.items()},
                 'UNREVIEWED_SOURCE_CANDIDATES.json':
                     (json.dumps(candidate, indent=2, sort_keys=True) + '\n').encode()}
        for relative, raw in files.items():
            dest = temp / relative
            fd = os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, 'wb') as f:
                f.write(raw)
        require(not output.exists(), 'quarantine path unexpectedly occupied')
        temp.rename(output)
    finally:
        if temp.exists():
            shutil.rmtree(temp)
    return {'status': candidate['status'], 'path': str(output),
            'files': list(files), 'theme_sha256': theme_sha,
            'source_sha256': {name: item['sha256'] for name, item in media.items()},
            'next_gate': 'Independent media provenance/rights and theme version review; DO NOT pass this as an approved manifest'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-dir', required=True, type=Path)
    args = parser.parse_args()
    result = stage_candidates(args.private_dir)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
