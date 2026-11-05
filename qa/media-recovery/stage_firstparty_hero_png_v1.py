#!/usr/bin/env python3
"""Offline, fail-closed WordPress first-party hero derivative staging.

Default is read-only planning; --execute writes a *new* local file only after
an independently supplied SHA-256 and explicit item-specific derivative clearance.
Never fetches URLs, updates WordPress, or edits HTML/Gutenberg blocks.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
from urllib.parse import urlsplit

TARGET_WIDTH = 960
SCHEMA = 'fv-firstparty-hero5-live-v1'
EXPECTED = {(34, 39), (35, 40), (36, 41), (37, 42), (38, 43)}


def validate_manifest(manifest):
    if not isinstance(manifest, dict) or manifest.get('schema') != SCHEMA:
        raise ValueError('unexpected manifest schema')
    rows = manifest.get('assets')
    if not isinstance(rows, list) or len(rows) != 5:
        raise ValueError('expected five pinned original assets')
    pairs = set()
    for a in rows:
        post, media = a.get('post_id'), a.get('media_id')
        if (post, media) not in EXPECTED or (post, media) in pairs:
            raise ValueError('unknown or repeated media mapping')
        pairs.add((post, media))
        url = urlsplit(a.get('source_url', ''))
        if (url.scheme, url.netloc) != ('https', 'finalvestige.com'):
            raise ValueError('not a first-party HTTPS original')
        if not url.path.startswith('/wp-content/uploads/2026/08/') or not url.path.endswith('.png') or url.query or url.fragment:
            raise ValueError('source must be a stable PNG upload URL')
        if a.get('mime') != 'image/png' or a.get('width') != 1672 or a.get('height') != 941:
            raise ValueError('unexpected binary metadata')
        if not isinstance(a.get('original_bytes'), int) or a['original_bytes'] <= 1572864:
            raise ValueError('original size missing or outside selected queue')
        if a.get('stored_html_width') != 1024 or a.get('stored_html_height') != 576:
            raise ValueError('stored HTML display geometry changed: re-audit')
        if a.get('registered_subsizes') != 0 or a.get('stored_html_has_srcset') is not False:
            raise ValueError('responsive sizing state changed: re-audit')
        if a.get('browser_http_status') is not None or a.get('browser_transfer_bytes') is not None:
            raise ValueError('invented browser evidence in source inventory')
        if a.get('target_width') != TARGET_WIDTH or a.get('target_height') != 540:
            raise ValueError('target must be exact 960x540 without upscaling')
        rights = a.get('derivative_permission')
        if not isinstance(rights, dict) or rights.get('status') not in ('hold', 'approved'):
            raise ValueError('permission state must be explicit')
        if rights['status'] == 'approved':
            if not rights.get('approved_by') or not rights.get('evidence'):
                raise ValueError('derivative clearance requires accountable evidence')
        elif rights.get('approved_by') or rights.get('evidence'):
            raise ValueError('unapproved item must not imply clearance')
        sha = a.get('approved_source_sha256')
        if sha is not None and (not isinstance(sha, str) or len(sha) != 64 or any(c not in '0123456789abcdef' for c in sha)):
            raise ValueError('invalid pinned input SHA-256')
    if pairs != EXPECTED:
        raise ValueError('incomplete selected asset coverage')
    return rows


def plan(manifest):
    rows = validate_manifest(manifest)
    return {'status': 'SOURCE_ONLY_NO_BROWSER_BYTES', 'total_original_stored_bytes': sum(x['original_bytes'] for x in rows),
            'target_width': TARGET_WIDTH, 'no_upscale': True, 'production_changes': 0,
            'assets': [{'media_id': x['media_id'], 'post_id': x['post_id'], 'source_url': x['source_url'],
                        'expected_target': [x['target_width'], x['target_height']],
                        'derivative_permission': x['derivative_permission']['status'],
                        'browser_http_status': None, 'browser_transfer_bytes': None} for x in rows]}


def stage(manifest, media_id, local_source, output_directory):
    rows = validate_manifest(manifest)
    matched = [a for a in rows if a['media_id'] == media_id]
    if len(matched) != 1:
        raise ValueError('unknown media ID')
    a = matched[0]
    if a['derivative_permission']['status'] != 'approved' or not a['approved_source_sha256']:
        raise ValueError('HOLD: missing rights approval and pinned original hash')
    src = Path(local_source)
    outdir = Path(output_directory)
    if not src.is_file() or src.is_symlink() or not outdir.is_dir() or outdir.is_symlink():
        raise ValueError('local regular source and existing output directory are required')
    if src.suffix.lower() != '.png' or src.name != Path(urlsplit(a['source_url']).path).name:
        raise ValueError('source filename must match approved WordPress original URL')
    if src.resolve().parent == outdir.resolve():
        raise ValueError('source and output directories must differ')
    binary = src.read_bytes()
    if len(binary) != a['original_bytes'] or not binary.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError('original byte length or PNG signature mismatch')
    original_sha = hashlib.sha256(binary).hexdigest()
    if original_sha != a['approved_source_sha256']:
        raise ValueError('original SHA-256 mismatch')
    from PIL import Image, ImageOps
    with Image.open(io.BytesIO(binary)) as original:
        original.load()
        if original.format != 'PNG' or original.size != (a['width'], a['height']):
            raise ValueError('decoded source identity/dimensions changed')
        normalized = ImageOps.exif_transpose(original)
        if normalized.size != original.size:
            raise ValueError('EXIF rotation changed dimensions; manual review required')
        resized = normalized.resize((a['target_width'], a['target_height']), Image.Resampling.LANCZOS)
        if resized.mode not in ('RGB', 'RGBA'):
            resized = resized.convert('RGBA' if 'A' in resized.getbands() else 'RGB')
        buffer = io.BytesIO()
        save_args = {'format': 'WEBP', 'quality': 88, 'method': 6}
        if original.info.get('icc_profile'):
            save_args['icc_profile'] = original.info['icc_profile']
        resized.save(buffer, **save_args)
    converted = buffer.getvalue()
    with Image.open(io.BytesIO(converted)) as test:
        test.load()
        if test.size != (960, 540) or test.format != 'WEBP':
            raise ValueError('encoded derivative verification failed')
    if len(converted) >= len(binary):
        raise ValueError('no smaller derivative; do not stage')
    dest = outdir / f"fv-media-{media_id}-{original_sha[:12]}-960x540.webp"
    with dest.open('xb') as handle:  # exclusive: no destructive overwrites
        handle.write(converted)
    return {'stage_file': str(dest), 'original_sha256': original_sha,
            'derivative_sha256': hashlib.sha256(converted).hexdigest(),
            'original_bytes': len(binary), 'derivative_bytes': len(converted),
            'staged_byte_difference': len(binary) - len(converted),
            'derivative_dimensions': [960, 540], 'editorial_visual_qa': 'HOLD',
            'wordpress_upload_authorized': False, 'post_rewrite_authorized': False,
            'visitor_transfer_reduction_percent': None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--execute', action='store_true', help='stage a new local derivative; never publish')
    parser.add_argument('--media-id', type=int)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--output-directory', type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
    if args.execute:
        if args.media_id is None or args.source is None or args.output_directory is None:
            parser.error('--execute requires --media-id, --source and --output-directory')
        result = stage(manifest, args.media_id, args.source, args.output_directory)
    else:
        if any(x is not None for x in (args.media_id, args.source, args.output_directory)):
            parser.error('staging arguments require --execute')
        result = plan(manifest)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
