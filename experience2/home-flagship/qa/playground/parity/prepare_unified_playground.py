#!/usr/bin/env python3
"""Bind the *existing* attested seven-chapter Playground kit to sanitized Assembler chrome.

Offline preparatory action only: never starts WordPress, contacts a site, or imports
production data. Refuses a dirty/wrong checkout, nonlocal kit, or unsafe parity.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import re
import shutil
import stat
import zipfile
from pathlib import PurePosixPath
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

# The upstream isolated-stage builder creates precisely this local-only private seed.
# A matching JSON digest alone is not an authorization boundary: the receipt is
# stored alongside the Blueprint and can be edited with it.
CANONICAL_LOCAL_SEED = '''<?php
require_once '/wordpress/wp-load.php';
$host = strtolower((string) parse_url(home_url('/'), PHP_URL_HOST));
if (wp_get_environment_type() !== 'local' || !in_array($host, ['127.0.0.1','localhost'], true)) {
    throw new RuntimeException('Refusing to seed a nonlocal WordPress host');
}
$slug = 'fv-ex2-playground-review';
$existing = get_page_by_path($slug, OBJECT, 'page');
if ($existing && $existing->post_content !== '[fv_ex2_homepage_preview_private]') {
    throw new RuntimeException('Refusing to overwrite a non-FV page');
}
if (!$existing) {
    $id = wp_insert_post(['post_type' => 'page', 'post_status' => 'private',
        'post_name' => $slug, 'post_title' => 'Experience 2.0 — local editor review only',
        'post_content' => '[fv_ex2_homepage_preview_private]',
        'comment_status' => 'closed', 'ping_status' => 'closed'], true);
    if (is_wp_error($id) || !$id) { throw new RuntimeException('Local preview page creation failed'); }
}
?>'''


def verified_mount_tree(stage: Path) -> None:
    """No mount ancestor/entry may redirect writes or read outside this local kit."""
    mounts = stage / 'mounts'
    if mounts.is_symlink() or not mounts.is_dir() or mounts.resolve() != mounts:
        raise ValueError('STAGE HOLD: unsafe mounts root/symlink')
    for name in ('assembler', 'fv-ex2-private-preview'):
        directory = mounts / name
        if directory.is_symlink() or not directory.is_dir() or directory.resolve() != directory:
            raise ValueError('STAGE HOLD: unsafe existing theme/plugin mount')
    for name in ('assembler/style.css', 'fv-ex2-private-preview/fv-ex2-private-preview.php'):
        f = mounts / name
        if f.is_symlink() or not f.is_file() or not f.resolve().is_relative_to(mounts):
            raise ValueError('STAGE HOLD: unsafe theme/plugin entry point')




MAX_THEME_UNPACKED_BYTES = 80 * 1024 * 1024
MAX_THEME_FILES = 4000
PLUGIN_NAME = 'fv-ex2-private-preview'
EXPECTED_PLUGIN = {'fv-ex2-private-preview.php', 'fv-ex2-private-payload.php',
                   'STAGING_MANIFEST.json', 'INSTALLATION_HOLD.txt'}


def expected_php_payload(assets: dict[str, bytes]) -> bytes:
    """Reconstruct the exact deterministic private PHP payload from canonical Git blobs."""
    hashes = {k: sha(v) for k, v in assets.items()}
    sha_rows = ",\n".join(f"    '{k}' => '{v}'" for k, v in hashes.items())
    data_rows = ",\n".join(
        f"    '{k}' => '{base64.b64encode(v).decode('ascii')}'" for k, v in assets.items()
    )
    return ("<?php\nif (!defined('ABSPATH')) { http_response_code(403); exit; }\n"
            "return [\n 'sha256' => [\n" + sha_rows + "\n ],\n 'data' => [\n"
            + data_rows + "\n ],\n];\n").encode('ascii')


def archive_file_map(raw: bytes, *, root: str, limit: int = MAX_THEME_UNPACKED_BYTES) -> dict[str, bytes]:
    """Strict ZIP contents: no zip-slip, symlinks, collisions or unbounded reads."""
    from io import BytesIO
    result: dict[str, bytes] = {}
    seen: set[str] = set()
    total = 0
    with zipfile.ZipFile(BytesIO(raw)) as archive:
        members = archive.infolist()
        if not members or len(members) > MAX_THEME_FILES:
            raise ValueError('MOUNT HOLD: archive member count')
        for member in members:
            if member.is_dir():
                continue
            name = member.filename
            parts = PurePosixPath(name).parts
            if (name.startswith('/') or '\\' in name or len(parts) < 2 or
                parts[0] != root or any(x in ('', '.', '..') for x in parts) or
                stat.S_ISLNK(member.external_attr >> 16) or
                not stat.S_ISREG(member.external_attr >> 16) and member.create_system == 3 and (member.external_attr >> 16) != 0):
                raise ValueError('MOUNT HOLD: unsafe archive entry')
            key = PurePosixPath(*parts[1:]).as_posix()
            if key.casefold() in seen:
                raise ValueError('MOUNT HOLD: duplicate/case-colliding entry')
            seen.add(key.casefold())
            total += member.file_size
            if member.file_size > limit or total > limit:
                raise ValueError('MOUNT HOLD: archive exceeds extracted byte limit')
            payload = archive.read(member)
            if len(payload) != member.file_size:
                raise ValueError('MOUNT HOLD: truncated archive entry')
            result[key] = payload
    if not result:
        raise ValueError('MOUNT HOLD: empty archive')
    return result


def compare_mount(directory: Path, expected: dict[str, bytes], label: str) -> dict[str, str]:
    """All extracted bytes and file paths must equal the verified archive, not just style.css."""
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError('MOUNT HOLD: missing or symlinked ' + label)
    actual: dict[str, str] = {}
    for p in directory.rglob('*'):
        if p.is_symlink() or not p.resolve().is_relative_to(directory):
            raise ValueError('MOUNT HOLD: symlink or path escape in ' + label)
        if p.is_dir():
            continue
        if not p.is_file():
            raise ValueError('MOUNT HOLD: unexpected special file in ' + label)
        rel = p.relative_to(directory).as_posix()
        if rel not in expected or p.read_bytes() != expected[rel]:
            raise ValueError('MOUNT HOLD: modified or unexpected ' + label + '/' + rel)
        actual[rel] = sha(expected[rel])
    if set(actual) != set(expected):
        raise ValueError('MOUNT HOLD: missing ' + label + ' extracted files')
    return actual


def verify_mount_contents(repo: Path, head: str, stage: Path, receipt: dict,
                          theme_zip: Path, theme_sha256: str) -> dict[str, object]:
    """Theme ZIP SHA must be provided independently, not taken from editable stage receipt."""
    if not re.fullmatch(r'[0-9a-f]{64}', theme_sha256):
        raise ValueError('MOUNT HOLD: independent 64-character Assembler SHA-256 required')
    if theme_zip.is_symlink() or not theme_zip.is_file() or stage in theme_zip.resolve().parents:
        raise ValueError('MOUNT HOLD: theme archive must be an external regular file')
    theme_raw = theme_zip.read_bytes()
    if sha(theme_raw) != theme_sha256 or receipt.get('assembler_zip_sha256') != theme_sha256:
        raise ValueError('MOUNT HOLD: independently pinned Assembler ZIP mismatch')
    theme_expected = archive_file_map(theme_raw, root='assembler')
    if (b'Theme Name: Assembler' not in theme_expected.get('style.css', b'') or
        b'Version: 0.0.126' not in theme_expected.get('style.css', b'') or
        'templates/index.html' not in theme_expected):
        raise ValueError('MOUNT HOLD: invalid Assembler 0.0.126 archive')
    theme_hashes = compare_mount(stage/'mounts'/'assembler', theme_expected, 'assembler')
    archive_path = stage/'private-preview-release-HOLD.zip'
    if archive_path.is_symlink() or not archive_path.is_file():
        raise ValueError('MOUNT HOLD: missing private-preview source archive')
    plugin_raw = archive_path.read_bytes()
    if receipt.get('plugin_sha256') != sha(plugin_raw):
        raise ValueError('MOUNT HOLD: private plugin ZIP changed after preparation')
    plugin_expected = archive_file_map(plugin_raw, root=PLUGIN_NAME, limit=12*1024*1024)
    if set(plugin_expected) != EXPECTED_PLUGIN:
        raise ValueError('MOUNT HOLD: unexpected private-plugin archive files')
    manifest = json.loads(plugin_expected['STAGING_MANIFEST.json'])
    if (manifest.get('release_status') != 'HOLD_UNPUBLISHED_STAGING_ONLY' or
        manifest.get('expected_git_head_given_by_caller') != head or
        manifest.get('payload_sha256') != sha(plugin_expected['fv-ex2-private-payload.php'])):
        raise ValueError('MOUNT HOLD: private-plugin source manifest mismatch')
    # Independently check the shipping PHP code against the exact tracked commit.
    php_path = 'experience2/home-flagship/qa/integration/private-preview/fv-ex2-private-preview.php'
    if git_bytes(repo, 'show', head + ':' + php_path) != plugin_expected['fv-ex2-private-preview.php']:
        raise ValueError('MOUNT HOLD: staged PHP differs from exact Git HEAD')
    asset_paths = ['index.html','flagship.css','chronicle.css','chronicle-lens.css',
                   'inquiry.css','observer-lab.css','reading-trail.css','flagship.js',
                   'observer-lab.js','chronicle-lens.js','reading-trail.js']
    source_hashes = manifest.get('source_hashes')
    if not isinstance(source_hashes, dict) or set(source_hashes) != set(asset_paths):
        raise ValueError('MOUNT HOLD: missing canonical source asset hashes')
    source_bytes: dict[str, bytes] = {}
    for rel in asset_paths:
        full = 'experience2/home-flagship/' + rel
        source_bytes[rel] = git_bytes(repo, 'show', head + ':' + full)
        if sha(source_bytes[rel]) != source_hashes[rel]:
            raise ValueError('MOUNT HOLD: plugin manifest differs from canonical asset ' + rel)
    if plugin_expected['fv-ex2-private-payload.php'] != expected_php_payload(source_bytes):
        raise ValueError('MOUNT HOLD: payload bytes differ from exact committed 11-asset source')
    plugin_hashes = compare_mount(stage/'mounts'/PLUGIN_NAME, plugin_expected, 'private-preview')
    return {'theme_files_matched':len(theme_hashes), 'plugin_files_matched':len(plugin_hashes),
            'theme_sha256':theme_sha256, 'private_plugin_sha256':sha(plugin_raw)}

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
    if (set(blueprint) != {'$schema', 'landingPage', 'login', 'steps'}
        or blueprint['$schema'] != 'https://playground.wordpress.net/blueprint-schema.json'
        or blueprint['landingPage'] != '/?pagename=fv-ex2-playground-review'
        or blueprint['login'] is not True):
        raise ValueError('STAGE HOLD: unexpected Blueprint top-level action or URL')
    if steps[0] != {'step':'defineWpConfigConsts', 'consts':{
        'WP_ENVIRONMENT_TYPE':'local', 'FV_EX2_ALLOW_PREVIEW':True,
        'WP_DEBUG':True, 'WP_DEBUG_DISPLAY':False}}:
        raise ValueError('STAGE HOLD: not a local-only private preview')
    if steps[1] != {'step':'activateTheme','themeFolderName':'assembler'}:
        raise ValueError('STAGE HOLD: unexpected theme action')
    if steps[2] != {'step':'activatePlugin','pluginPath':
                   '/wordpress/wp-content/plugins/fv-ex2-private-preview/fv-ex2-private-preview.php'}:
        raise ValueError('STAGE HOLD: unexpected private preview plugin action')
    if steps[3] != {'step':'runPHP', 'code':CANONICAL_LOCAL_SEED}:
        raise ValueError('STAGE HOLD: changed local-only preview seed PHP')
    verified_mount_tree(stage)
    if not isinstance(argv, list) or argv[:3] != ['npx', '@wp-playground/cli@latest', 'server'] or '--port=9400' not in argv:
        raise ValueError('STAGE HOLD: unexpected Playground CLI')
    mounts = [v for v in argv if isinstance(v, str) and v.startswith('--mount=')]
    expected = {
        '--mount=' + str(stage / 'mounts' / 'assembler') + ':/wordpress/wp-content/themes/assembler',
        '--mount=' + str(stage / 'mounts' / 'fv-ex2-private-preview') + ':/wordpress/wp-content/plugins/fv-ex2-private-preview',
    }
    # The CLI argument vector itself is executable configuration; forbid *all*
    # extra flags (remote site-url, insecure listener, auto-mount, DB mounts, etc.).
    other_flags = {'--blueprint=' + str(stage/'playground-blueprint.json'), '--port=9400'}
    if (set(mounts) != expected or len(mounts) != 2
        or len(argv) != 7 or set(argv[3:]) != expected | other_flags):
        raise ValueError('STAGE HOLD: unexpected CLI flag, mount or Blueprint path')
    if stage.joinpath('mounts', MOUNT).exists() or receipt.get('assembler_parity'):
        raise ValueError('STAGE HOLD: refuses to overwrite a prior parity import')
    return receipt, blueprint, argv


def bind(repo: Path, head: str, stage: Path, theme_zip: Path, theme_sha256: str) -> dict:
    repo = repo.resolve(strict=True)
    if stage.is_symlink():
        raise ValueError('STAGE HOLD: stage root cannot be a symlink')
    stage = stage.resolve(strict=True)
    if stage == repo or repo in stage.parents:
        raise ValueError('STAGE HOLD: no writes within the exact Git checkout')
    sources = verify_sources(repo, head)
    parity = verify_parity(repo)
    receipt, blueprint, argv = verify_stage(stage, head)
    mount_custody = verify_mount_contents(repo, head, stage, receipt, theme_zip, theme_sha256)
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
        'upstream_mount_custody': mount_custody,
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
    ap.add_argument('--assembler-zip', required=True, type=Path, help='Independently obtained official theme archive')
    ap.add_argument('--assembler-sha256', required=True, help='Out-of-band pinned SHA-256 of official theme archive')
    a = ap.parse_args()
    try:
        print(json.dumps(bind(a.repo, a.expected_head, a.prepared_stage, a.assembler_zip, a.assembler_sha256), indent=2))
        return 0
    except Exception as exc:
        print('UNIFIED LOCAL STAGING FAILED CLOSED: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
