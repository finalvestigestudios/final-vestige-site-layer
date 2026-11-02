#!/usr/bin/env python3
"""Admit a PRIVATE verified WordPress Playground bundle to existing exact-stage browser QA.

This adapter does not construct content, fetch assets, talk to WordPress.com, or
publish. On --execute it delegates to the existing source-controlled launcher,
which runs only a loopback Playground followed by Chromium/axe and Lighthouse.
"""
from __future__ import annotations
import argparse
import copy
import io
import json
import os
from pathlib import Path
import stat
import sys
import zipfile

from package_offline_playground_bundle import (MEDIA, PREFIX, THEME_URL, check_theme,
                                              seal, sha)
import launch_integrated_staging as launcher

ZIP_MEMBERS = {'blueprint.json', 'assets/assembler.zip'} | {'assets/' + n for n in MEDIA}
MAX_ZIP_BYTES = 20_000_000
MAX_UNCOMPRESSED = 60_000_000


def admit_bundle(path: Path, pinned_sha: str, manifest_path: Path,
                 theme_sha: str, original_source_sha: str) -> dict:
    """Verify bundle, each media byte, code and steps before launching WordPress."""
    launcher.require(bool(launcher.DIGEST.fullmatch(pinned_sha or '')),
                     'independently reviewed offline bundle SHA-256 required')
    launcher.require(bool(launcher.DIGEST.fullmatch(original_source_sha or '')),
                     'independently reviewed original source semantic SHA-256 required')
    launcher.require(bool(launcher.DIGEST.fullmatch(theme_sha or '')),
                     'independently reviewed Assembler theme SHA-256 required')
    launcher.require(path.stat().st_size <= MAX_ZIP_BYTES,
                     'offline bundle exceeds reviewed size ceiling')
    raw = launcher.regular_private(path, 'private offline WordPress bundle')
    launcher.require(sha(raw) == pinned_sha,
                     'offline bundle differs from independently reviewed SHA-256')
    manifest_raw = launcher.regular_private(manifest_path, 'independently reviewed media manifest')
    manifest = json.loads(manifest_raw)
    launcher.check_manifest(manifest_path)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        info = z.infolist()
        names = [i.filename for i in info]
        launcher.require(len(names) == len(ZIP_MEMBERS) and set(names) == ZIP_MEMBERS,
                         'unexpected, duplicate or missing private bundle member')
        launcher.require(sum(i.file_size for i in info) < MAX_UNCOMPRESSED and
                         all(i.file_size and not i.is_dir() and i.flag_bits & 1 == 0 and
                             (i.external_attr >> 16 & 0o170000) != stat.S_IFLNK
                             for i in info),
                         'unsafe or oversized bundle member')
        contents = {name: z.read(name) for name in names}
    blueprint = json.loads(contents['blueprint.json'])
    launcher.require(type(blueprint) is dict and type(blueprint.get('steps')) is list and
                     len(blueprint['steps']) == 19, 'expected exact 19-step WordPress bundle')
    steps = blueprint['steps']
    launcher.require(steps[1].get('themeData') ==
                     {'resource': 'bundled', 'path': '/assets/assembler.zip'},
                     'Assembler bundled reference substituted')
    for item in steps[2:17]:
        if item.get('path','').startswith(PREFIX):
            name = item['path'].rsplit('/', 1)[-1]
            launcher.require(name in MEDIA and item.get('data') ==
                             {'resource': 'bundled', 'path': '/assets/' + name},
                             'unexpected offline media reference')
    theme = contents['assets/assembler.zip']
    check_theme(theme, theme_sha)
    media = {n: contents['assets/' + n] for n in MEDIA}
    # Reconstruct the original strictly reviewed URL-resource Blueprint in
    # memory, then rerun the exact upstream packager's 19-step security gates.
    # The expected rebuilt bundle must match EVERY member byte, including the
    # complete plugin, CSS, JS and post-save PHP. No alternative assembly.
    original = copy.deepcopy(blueprint)
    original['steps'][1]['themeData'] = {'resource': 'url', 'url': THEME_URL}
    for step in original['steps'][2:17]:
        if step.get('path','').startswith(PREFIX):
            name = step['path'].rsplit('/', 1)[-1]
            step['data'] = {'resource': 'url', 'url': MEDIA[name][0]}
    fingerprint = sha(json.dumps(original,sort_keys=True,separators=(',', ':'),
                                 ensure_ascii=False).encode('utf-8'))
    launcher.require(fingerprint == original_source_sha,
                     'integrated 19-step original source differs from independent reviewed digest')
    expected = seal(original, theme, media, manifest, theme_sha)
    launcher.require(set(expected) == ZIP_MEMBERS and
                     all(contents[k] == expected[k] for k in ZIP_MEMBERS),
                     'offline bundle is not the deterministic reviewed 19-step package')
    return {'status': 'PRIVATE_OFFLINE_BUNDLE_PREFLIGHT_PASSED_NOT_WORDPRESS_EXECUTED',
            'bundle_sha256': sha(raw), 'bundle_size_bytes': len(raw),
            'assembler_sha256': sha(theme), 'media_sha256': {n: sha(media[n]) for n in MEDIA},
            'blueprint_sha256': sha(contents['blueprint.json']),
            'independently_pinned_original_source_sha256': fingerprint,
            'integrated_gutenberg_gate': 'INHERITED_19_STEP_SEAL_VERIFIED',
            'image_rights_cleared': False, 'production_writes': False,
            'wordpress_rendered': False}


def main(argv=None):
    p = argparse.ArgumentParser(description='PRIVATE offline WordPress Playground bundle QA; no production writes')
    for k in ('bundle','media-manifest','axe-js','browser-runner','private-dir','output-dir'):
        p.add_argument('--'+k, type=Path, required=True)
    for k in ('bundle-sha256','theme-sha256','original-source-sha256','axe-sha256','browser-runner-sha256'):
        p.add_argument('--'+k, required=True)
    p.add_argument('--execute', action='store_true', help='run local WordPress and measured browser gates')
    for k in ('playground-cli','lighthouse-cli'):
        p.add_argument('--'+k, type=Path)
    for k in ('playground-cli-sha256','lighthouse-cli-sha256'):
        p.add_argument('--'+k)
    p.add_argument('--port', type=int, default=19400)
    p.add_argument('--ready-timeout', type=int, default=75)
    p.add_argument('--browser-timeout', type=int, default=240)
    a = p.parse_args(argv)
    result = {'status':'FAILED_CLOSED', 'mode':'EXECUTE' if a.execute else 'PREFLIGHT_ONLY',
              'wordpress_rendered':False, 'image_rights_cleared':False,
              'hosted_wpcom_equivalence':False,'field_cwv_measured':False,
              'ci_qd_approved':False,'production_writes':False}
    try:
        launcher.require(a.private_dir.is_dir() and not a.private_dir.is_symlink(),
                         'existing private workspace required')
        if os.name == 'posix':
            launcher.require(not a.private_dir.stat().st_mode & 0o077,
                             'workspace is not chmod 700')
        root = a.private_dir.resolve()
        for file,label in ((a.bundle,'bundle'),(a.media_manifest,'manifest')):
            launcher.require(file.resolve().is_relative_to(root),
                             label+' must remain in private workspace')
        result.update(admit_bundle(a.bundle, a.bundle_sha256, a.media_manifest,
                                   a.theme_sha256, a.original_source_sha256))
        result.update(launcher.check_axe(a.axe_js,a.axe_sha256))
        result.update(launcher.check_runner(a.browser_runner,a.browser_runner_sha256))
        if a.execute:
            # Reuse native stage launcher: the CLI accepts the ZIP --blueprint
            # path; Chrome/axe/Lighthouse and fail-closed checks are unchanged.
            a.blueprint = a.bundle
            launcher.run(a,result)
    except Exception as exc:
        result['status'] = 'FAILED_CLOSED'
        result['reason'] = str(exc)[:450]
        result['error_type'] = type(exc).__name__
    finally:
        if a.private_dir.is_dir() and not a.private_dir.is_symlink():
            launcher.write_receipt(a.private_dir,result)
        print(json.dumps(result,indent=2,sort_keys=True))
    return 0 if result['status'] in (
        'PRIVATE_OFFLINE_BUNDLE_PREFLIGHT_PASSED_NOT_WORDPRESS_EXECUTED',
        'ISOLATED_WORDPRESS_LAB_EVIDENCE_COLLECTED_RELEASE_HOLD') else 1

if __name__ == '__main__':
    sys.exit(main())
