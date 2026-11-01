#!/usr/bin/env python3
"""Admit and launch a sealed seven-chapter WordPress Playground ZIP (never production).

Companion to exact-source PR #459. Strictly compares the four permitted bundled
resources with the *original, independently pinned* 19-step WordPress Blueprint;
passes the already-verified local ZIP directly to the original staging launcher.
No content changes, no network downloads of archive assets, no CMS writes.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from types import SimpleNamespace
import zipfile

from launch_integrated_staging import (
    DIGEST, Hold, MEDIA_SOURCES, THEME_URL, check_axe, check_blueprint,
    check_manifest, check_runner, regular_private, require, run,
    sha, write_receipt,
)
from make_offline_private_bundle import ENTRIES, FILES, validate_theme

# Closed inventory, not arbitrary extracted files. 100 MB cap leaves reasonable
# headroom for a real Assembler theme and the three original archive images.
MAX_TOTAL_UNCOMPRESSED = 100_000_000
MAX_BLUEPRINT_BYTES = 5_000_000


def assert_pin(pin: str, label: str) -> None:
    require(bool(DIGEST.fullmatch(pin or '')), label + ': independently reviewed SHA-256 required')


def inspect_offline_bundle(
    bundle: Path, bundle_sha256: str, original_blueprint: Path,
    original_blueprint_sha256: str, manifest: Path,
    manifest_sha256: str, theme_sha256: str,
) -> dict:
    """Fail closed unless ZIP == the approved Blueprint with FOUR substitutions."""
    for pin, label in (
        (bundle_sha256, 'bundle'), (original_blueprint_sha256, 'source blueprint'),
        (manifest_sha256, 'media manifest'), (theme_sha256, 'Assembler ZIP'),
    ):
        assert_pin(pin, label)

    raw = regular_private(bundle, 'sealed private Playground bundle')
    require(sha(raw) == bundle_sha256, 'sealed bundle bytes changed since independent approval')
    require(bundle.suffix.lower() == '.zip', 'Playground bundle must be a local ZIP')
    original_raw = regular_private(original_blueprint, 'approved integrated Blueprint')
    require(sha(original_raw) == original_blueprint_sha256,
            'original source Blueprint no longer matches independently reviewed SHA-256')
    approved_blueprint = check_blueprint(original_blueprint, original_blueprint_sha256)
    manifest_bytes = regular_private(manifest, 'approved original-image manifest')
    require(sha(manifest_bytes) == manifest_sha256, 'media manifest changed since independent review')
    check_manifest(manifest)
    rights = json.loads(manifest_bytes)['images']
    original = json.loads(original_raw)
    require(isinstance(original, dict), 'invalid approved source Blueprint')

    with zipfile.ZipFile(bundle) as archive:
        infos = archive.infolist()
        names = [entry.filename for entry in infos]
        require(names == list(ENTRIES), 'bundle entries, ordering, duplicates or private path changed')
        require(all(not entry.is_dir() and not entry.filename.startswith('/') and
                    '..' not in Path(entry.filename).parts and not
                    ((entry.external_attr >> 16) & 0o170000) == 0o120000
                    for entry in infos), 'bundle contains unsafe path, directory or symlink')
        require(all(entry.compress_type in (zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED)
                    and entry.file_size > 0 for entry in infos),
                'bundle contains unsupported compression or empty file')
        require(sum(x.file_size for x in infos) <= MAX_TOTAL_UNCOMPRESSED,
                'bundle uncompressed size exceeds 100 MB admission budget')
        require(infos[0].file_size <= MAX_BLUEPRINT_BYTES,
                'integrated Blueprint exceeds 5 MB review budget')
        with archive.open('blueprint.json') as stream:
            actual_blueprint_bytes = stream.read(MAX_BLUEPRINT_BYTES + 1)
        assembled = json.loads(actual_blueprint_bytes)
        expected = deepcopy(original)
        expected['steps'][1]['themeData'] = {'resource': 'bundled', 'path': '/assembler.zip'}
        for step in expected['steps']:
            p = step.get('path', '')
            for filename in FILES:
                if p.endswith('/media/' + filename):
                    url, _length = MEDIA_SOURCES[filename]
                    require(step['data'] == {'resource': 'url', 'url': url},
                            filename + ': original source URL was modified')
                    step['data'] = {'resource': 'bundled', 'path': '/media/' + filename}
        serialized = json.dumps(expected, sort_keys=True, separators=(',', ':'),
                                ensure_ascii=False).encode('utf-8')
        require(actual_blueprint_bytes == serialized,
                'offline Blueprint differs from exact four approved resource substitutions')
        require(assembled == expected, 'offline Blueprint changed protected Gutenberg content')
        require(expected['steps'][1]['themeData'] == {'resource':'bundled', 'path':'/assembler.zip'},
                'not the expected local-only Assembler archive')
        original_theme = archive.read('assembler.zip')
        theme = validate_theme(original_theme, theme_sha256)
        image_receipt = {}
        for filename in FILES:
            data = archive.read('media/' + filename)
            url, expected_size = MEDIA_SOURCES[filename]
            approval = rights[filename]
            require(approval['source_url'] == url and len(data) == expected_size and
                    approval['bytes'] == expected_size and sha(data) == approval['sha256'],
                    filename + ': original image bytes differ from reviewed manifest')
            if filename.endswith('.jpg'):
                require(data.startswith(b'\xff\xd8\xff'), filename + ': wrong JPEG signature')
            else:
                require(data.startswith(b'RIFF') and data[8:12] == b'WEBP',
                        filename + ': wrong WebP signature')
            image_receipt[filename] = {'sha256': sha(data), 'bytes': len(data),
                                       'source_url': url, 'rights_approved': False}
        # A failed CRC or corrupt member must fail before a browser starts.
        require(archive.testzip() is None, 'ZIP integrity/CRC failure')
    return {
        'bundle_sha256': sha(raw), 'bundle_bytes': len(raw),
        'original_blueprint_sha256': approved_blueprint['blueprint_sha256'],
        'media_manifest_sha256': sha(manifest_bytes), 'theme': theme,
        'images': image_receipt, 'bundle_entries': list(ENTRIES),
        'protected_steps': 19, 'permitted_source_substitutions': 4,
        'source_content_changed': False, 'network_asset_fetches_required': False,
        'actual_wp_rendered': False, 'rights_verified': False,
        'hosted_equivalence': False,
    }


def stage(args, receipt):
    require(args.bundle.resolve().is_relative_to(args.private_dir.resolve()),
            'bundle must remain inside private staging workspace')
    require(args.original_blueprint.resolve().is_relative_to(args.private_dir.resolve()),
            'original Blueprint must remain in private workspace')
    require(args.media_manifest.resolve().is_relative_to(args.private_dir.resolve()),
            'media review manifest must remain in private workspace')
    receipt.update(inspect_offline_bundle(
        args.bundle, args.bundle_sha256, args.original_blueprint,
        args.original_blueprint_sha256, args.media_manifest,
        args.media_manifest_sha256, args.assembler_sha256,
    ))
    if args.execute:
        receipt.update(check_axe(args.axe_js, args.axe_sha256))
        receipt.update(check_runner(args.browser_runner, args.browser_runner_sha256))
        # Delegate port safety, local HTTP, real Chromium/axe, genuine measured
        # Lighthouse, process isolation and cleanup to the EXISTING launcher.
        launch_args = SimpleNamespace(**vars(args))
        launch_args.blueprint = args.bundle
        run(launch_args, receipt)
    else:
        receipt['status'] = 'SEALED_BUNDLE_PREFLIGHT_PASS_NOT_WORDPRESS_EXECUTED'


def main(argv=None):
    p = argparse.ArgumentParser(description='Admit and optionally execute exact approved local WordPress Playground ZIP')
    p.add_argument('--bundle', type=Path, required=True)
    p.add_argument('--bundle-sha256', required=True)
    p.add_argument('--original-blueprint', type=Path, required=True)
    p.add_argument('--original-blueprint-sha256', required=True)
    p.add_argument('--media-manifest', type=Path, required=True)
    p.add_argument('--media-manifest-sha256', required=True)
    p.add_argument('--assembler-sha256', required=True)
    p.add_argument('--private-dir', type=Path, required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    p.add_argument('--execute', action='store_true')
    p.add_argument('--axe-js', type=Path)
    p.add_argument('--axe-sha256')
    p.add_argument('--browser-runner', type=Path)
    p.add_argument('--browser-runner-sha256')
    p.add_argument('--playground-cli', type=Path)
    p.add_argument('--playground-cli-sha256')
    p.add_argument('--lighthouse-cli', type=Path)
    p.add_argument('--lighthouse-cli-sha256')
    p.add_argument('--port', type=int, default=19400)
    p.add_argument('--ready-timeout', type=int, default=75)
    p.add_argument('--browser-timeout', type=int, default=240)
    args = p.parse_args(argv)
    report = {
        'status': 'FAILED_CLOSED', 'mode': 'LOCAL_EXECUTION' if args.execute else 'PREFLIGHT_ONLY',
        'run_utc': datetime.now(timezone.utc).isoformat(), 'wordpress_rendered': False,
        'axe_verified': False, 'lighthouse_measured': False, 'rights_verified': False,
        'jetpack_delivery_verified': False, 'hosted_wpcom_equivalence': False,
        'field_cwv_measured': False, 'ci_qd_approved': False,
    }
    try:
        require(args.private_dir.is_dir() and not args.private_dir.is_symlink(),
                'pre-existing private workspace required; no auto-created output for untrusted paths')
        if os.name == 'posix':
            require(not (args.private_dir.stat().st_mode & 0o077),
                    'private workspace must be chmod 700')
        stage(args, report)
    except Exception as exc:
        report.update({'error_type': type(exc).__name__, 'reason': str(exc)[:450],
                       'status': 'FAILED_CLOSED'})
    if args.private_dir.is_dir() and not args.private_dir.is_symlink():
        write_receipt(args.private_dir, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report['status'] in (
        'SEALED_BUNDLE_PREFLIGHT_PASS_NOT_WORDPRESS_EXECUTED',
        'ISOLATED_WORDPRESS_LAB_EVIDENCE_COLLECTED_RELEASE_HOLD',
    ) else 1


if __name__ == '__main__':
    raise SystemExit(main())
