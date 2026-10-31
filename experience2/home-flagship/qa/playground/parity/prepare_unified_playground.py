#!/usr/bin/env python3
"""Bind the *existing* attested seven-chapter Playground kit to sanitized Assembler chrome.

Offline preparatory action only: never starts WordPress, contacts a site, or imports
production data. Refuses a dirty/wrong checkout, nonlocal kit, or unsafe parity.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path('experience2/home-flagship/qa/playground')
PARITY = HOME / 'parity'
INPUTS = ('prepare_unified_playground.py', 'test_prepare_unified_playground.py',
          'apply_local_parity.php',
          'sanitize_theme_parity.py', 'blueprint.local.json', 'assembler-public-safe.json')
MOUNT = 'fv-ex2-parity'
TARGET = '/wordpress/wp-content/uploads/' + MOUNT
HEX40 = re.compile(r'^[0-9a-f]{40}$')
REJECT = re.compile(r'<\s*(script|iframe|object|embed|form|link|meta)\b|\bon[a-z]{3,}\s*=|javascript\s*:|posthog|googletagmanager|gtag\s*\(|phc_[A-Za-z0-9_]+', re.I)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_bytes(repo: Path, *args: str) -> bytes:
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True)
    if result.returncode:
        raise ValueError('CUSTODY HOLD: Git ' + ' '.join(args) + ' failed')
    return result.stdout


def verify_sources(repo: Path, head: str) -> dict[str, str]:
    if not HEX40.fullmatch(head) or git_bytes(repo, 'rev-parse', 'HEAD').decode().strip() != head:
        raise ValueError('CUSTODY HOLD: exact checkout SHA mismatch')
    hashes = {}
    for name in INPUTS:
        rel = PARITY / name
        path = repo / rel
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(repo):
            raise ValueError('CUSTODY HOLD: unsafe or absent ' + str(rel))
        git_bytes(repo, 'ls-files', '--error-unmatch', '--', rel.as_posix())
        actual = path.read_bytes()
        if git_bytes(repo, 'show', head + ':' + rel.as_posix()) != actual:
            raise ValueError('CUSTODY HOLD: uncommitted parity source ' + str(rel))
        hashes[rel.as_posix()] = sha(actual)
    return hashes


def verify_parity(repo: Path) -> dict:
    data = json.loads((repo / PARITY / 'assembler-public-safe.json').read_text())
    if set(data) != {'schema', 'release', 'source_theme', 'local_only', 'template_content', 'global_styles'}:
        raise ValueError('PARITY HOLD: unexpected public presentation fields')
    if data['schema'] != 'fv-local-assembler-parity-v1' or data['release'] != 'HOLD' or data['local_only'] is not True:
        raise ValueError('PARITY HOLD: source is not local-only HOLD')
    if data['source_theme'] != {'stylesheet': 'assembler', 'version': '0.0.126'}:
        raise ValueError('PARITY HOLD: Assembler 0.0.126 source required')
    content = data['template_content']
    if not isinstance(content, dict) or set(content) != {'page', 'header', 'footer', 'overlay'}:
        raise ValueError('PARITY HOLD: missing page/header/footer/overlay')
    sys.path.insert(0, str(repo / PARITY))
    try:
        from sanitize_theme_parity import safe_css, safe_markup
    finally:
        sys.path.pop(0)
    for name, markup in content.items():
        if not isinstance(markup, str) or REJECT.search(markup):
            raise ValueError('PARITY HOLD: executable, tracker, or personal data in ' + name)
        clean, removed = safe_markup(markup)
        if removed or clean != markup:
            raise ValueError('PARITY HOLD: changed or unsanitized block in ' + name)
    gs = data['global_styles']
    if not isinstance(gs, dict) or set(gs) != {'settings', 'styles'} or gs['settings'] != {'layout': {'contentSize': '760px', 'wideSize': '1440px'}}:
        raise ValueError('PARITY HOLD: layout mismatch')
    css = gs['styles'].get('css') if isinstance(gs['styles'], dict) and set(gs['styles']) == {'css'} else None
    if not isinstance(css, str) or len(css) < 500 or REJECT.search(css) or safe_css(css) != css:
        raise ValueError('PARITY HOLD: missing or unsafe global CSS')
    return data


def verify_stage(stage: Path, head: str) -> tuple[dict, dict, list[str]]:
    if not stage.is_dir() or stage.is_symlink():
        raise ValueError('STAGE HOLD: missing/unsafe local kit')
    receipt = json.loads((stage / 'STAGING_PREP_RECEIPT.json').read_text())
    blueprint = json.loads((stage / 'playground-blueprint.json').read_text())
    argv = json.loads((stage / 'playground-cli-arguments.json').read_text())
    if receipt.get('status') != 'LOCAL_PLAYGROUND_PREPARED_NOT_EXECUTED' or receipt.get('release') != 'HOLD' or receipt.get('exact_git_head') != head:
        raise ValueError('STAGE HOLD: wrong source receipt or release state')
    if receipt.get('assembler_sha256_out_of_band_pin_verified') is not True or receipt.get('wordpress_instance') != 'NOT_STARTED':
        raise ValueError('STAGE HOLD: missing theme pin or already-started kit')
    bpbytes = (stage / 'playground-blueprint.json').read_bytes()
    if receipt.get('blueprint_sha256') != sha(bpbytes):
        raise ValueError('STAGE HOLD: original Blueprint was modified')
    steps = blueprint.get('steps')
    if not isinstance(steps, list) or [s.get('step') for s in steps] != ['defineWpConfigConsts', 'activateTheme', 'activatePlugin', 'runPHP']:
        raise ValueError('STAGE HOLD: unexpected Blueprint execution path')
    if steps[0].get('consts', {}).get('WP_ENVIRONMENT_TYPE') != 'local' or steps[0]['consts'].get('FV_EX2_ALLOW_PREVIEW') is not True:
        raise ValueError('STAGE HOLD: not a local-only private preview')
    if steps[1].get('themeFolderName') != 'assembler' or 'fv-ex2-private-preview' not in steps[2].get('pluginPath', ''):
        raise ValueError('STAGE HOLD: unexpected theme or preview plugin')
    if 'fv-ex2-playground-review' not in steps[3].get('code', '') or not stage.joinpath('mounts', 'assembler', 'style.css').is_file() or not stage.joinpath('mounts', 'fv-ex2-private-preview', 'fv-ex2-private-preview.php').is_file():
        raise ValueError('STAGE HOLD: theme/plugin/preview missing')
    if not isinstance(argv, list) or argv[:3] != ['npx', '@wp-playground/cli@latest', 'server'] or '--port=9400' not in argv:
        raise ValueError('STAGE HOLD: unexpected Playground CLI')
    mounts = [v for v in argv if isinstance(v, str) and v.startswith('--mount=')]
    expected = {
        '--mount=' + str(stage / 'mounts' / 'assembler') + ':/wordpress/wp-content/themes/assembler',
        '--mount=' + str(stage / 'mounts' / 'fv-ex2-private-preview') + ':/wordpress/wp-content/plugins/fv-ex2-private-preview',
    }
    if set(mounts) != expected or len(mounts) != 2 or '--blueprint=' + str(stage/'playground-blueprint.json') not in argv:
        raise ValueError('STAGE HOLD: paths point outside this isolated kit')
    if stage.joinpath('mounts', MOUNT).exists() or receipt.get('assembler_parity'):
        raise ValueError('STAGE HOLD: refuses to overwrite a prior parity import')
    return receipt, blueprint, argv


def bind(repo: Path, head: str, stage: Path) -> dict:
    repo = repo.resolve(strict=True)
    stage = stage.resolve(strict=True)
    if stage == repo or repo in stage.parents:
        raise ValueError('STAGE HOLD: no writes within the exact Git checkout')
    sources = verify_sources(repo, head)
    parity = verify_parity(repo)
    receipt, blueprint, argv = verify_stage(stage, head)
    import_step = json.loads((repo / PARITY / 'blueprint.local.json').read_text())['steps'][-1]
    if import_step.get('step') != 'runPHP' or "require '/wordpress/wp-content/uploads/fv-ex2-parity/apply_local_parity.php';" not in import_step.get('code', ''):
        raise ValueError('PARITY HOLD: unexpected importer step')
    php = repo / PARITY / 'apply_local_parity.php'
    lint = subprocess.run(['php', '-l', str(php)], capture_output=True, text=True)
    if lint.returncode:
        raise ValueError('PARITY HOLD: PHP syntax check failed')
    # Import presentation *after* theme activation, *before* editor preview page seed.
    blueprint['steps'].insert(2, import_step)
    argv.insert(argv.index('--port=9400'), '--mount=' + str(stage / 'mounts' / MOUNT) + ':' + TARGET)
    mount = stage / 'mounts' / MOUNT
    mount.mkdir()
    for filename in ('assembler-public-safe.json', 'apply_local_parity.php'):
        shutil.copyfile(repo / PARITY / filename, mount / filename)
    new_bp = json.dumps(blueprint, indent=2) + '\n'
    (stage / 'playground-blueprint.json').write_text(new_bp)
    (stage / 'playground-cli-arguments.json').write_text(json.dumps(argv, indent=2)+'\n')
    receipt.update({
        'assembler_parity': 'MOUNTED_NOT_IMPORTED',
        'parity_source_sha256': sources,
        'parity_manifest_sha256': sha((mount / 'assembler-public-safe.json').read_bytes()),
        'parity_importer_sha256': sha((mount / 'apply_local_parity.php').read_bytes()),
        'blueprint_sha256': sha((stage / 'playground-blueprint.json').read_bytes()),
        'local_wp_import': 'NOT_EXECUTED', 'actual_wordpress_render': 'NOT_TESTED',
        'production_user_or_subscriber_import': 'NONE', 'telemetry': 'OMITTED_FROM_PARITY',
        'wordpress_com_host_equivalence': 'NOT_ESTABLISHED', 'release': 'HOLD',
    })
    (stage / 'STAGING_PREP_RECEIPT.json').write_text(json.dumps(receipt, indent=2)+'\n')
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', required=True, type=Path)
    ap.add_argument('--expected-head', required=True)
    ap.add_argument('--prepared-stage', required=True, type=Path)
    a = ap.parse_args()
    try:
        print(json.dumps(bind(a.repo, a.expected_head, a.prepared_stage), indent=2))
        return 0
    except Exception as exc:
        print('UNIFIED LOCAL STAGING FAILED CLOSED: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
