#!/usr/bin/env python3
"""Build a LOCAL-ONLY WordPress Playground staging kit from exact Experience 2.0 Git HEAD.

No downloads, host writes, production database import, CMS API, or plugin activation
are performed by this program. Launching the generated CLI command is a separate,
explicitly non-production developer action; an actual WP Playground install is
required before browser QA claims can be made.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import stat
import sys
import zipfile

HOME = Path('experience2/home-flagship')
ATTESTER = HOME / 'qa/integration/private-preview/attest_private_preview.py'
PLUGIN = 'fv-ex2-private-preview'
LOCAL_HOSTS = {'localhost', '127.0.0.1'}
MAX_THEME_BYTES = 80 * 1024 * 1024
MAX_THEME_FILES = 4000
PREVIEW_SLUG = 'fv-ex2-playground-review'
STAGE_SOURCE = HOME / 'qa/playground'
STAGE_FILES = ('prepare_isolated_stage.py','test_prepare_isolated_stage.py','README.md')


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def safe_zip_contents(path: Path, *, strip_root: bool) -> dict[str, bytes]:
    """Reject zip-slip, links, file bombs, duplicate/case-colliding paths and large inputs."""
    files: dict[str, bytes] = {}
    with zipfile.ZipFile(path) as z:
        members = [i for i in z.infolist() if not i.is_dir()]
        if not members or len(members) > MAX_THEME_FILES:
            raise ValueError('Invalid ZIP file count')
        roots = {PurePosixPath(i.filename).parts[0] for i in members}
        if strip_root and (len(roots) != 1 or next(iter(roots)) != 'assembler'):
            raise ValueError('Theme ZIP must contain exactly one assembler/ root')
        total = 0
        for m in members:
            p = PurePosixPath(m.filename)
            parts = p.parts
            if m.filename.startswith('/') or '\\' in m.filename or not parts or any(x in ('', '.', '..') for x in parts):
                raise ValueError('Unsafe ZIP entry path')
            if re.match(r'^[A-Za-z]:', m.filename) or stat.S_ISLNK(m.external_attr >> 16):
                raise ValueError('Absolute or symlink ZIP entry forbidden')
            target = PurePosixPath(*parts[1:]) if strip_root else p
            if not target.parts or target.as_posix().startswith('.'):
                raise ValueError('Malformed ZIP root')
            key = target.as_posix()
            if key in files or key.casefold() in {k.casefold() for k in files}:
                raise ValueError('Duplicate/case-colliding ZIP entry')
            total += m.file_size
            if total > MAX_THEME_BYTES or m.file_size > MAX_THEME_BYTES:
                raise ValueError('Oversized ZIP contents')
            data = z.read(m)
            if len(data) != m.file_size:
                raise ValueError('ZIP entry truncated')
            files[key] = data
    return files


def validate_theme(files: dict[str, bytes]):
    css = files.get('style.css', b'').decode('utf-8', errors='replace')
    if not re.search(r'(?im)^\s*Theme Name:\s*Assembler\s*$', css):
        raise ValueError('Theme package is not verified as Assembler')
    if 'templates/index.html' not in files:
        raise ValueError('Assembler index block template missing')
    if any(name.endswith('.php') and b'<?php' not in raw for name, raw in files.items()):
        raise ValueError('Unexpected PHP payload in theme')


def validate_plugin(files: dict[str, bytes]):
    allowed = {'fv-ex2-private-preview.php', 'fv-ex2-private-payload.php', 'STAGING_MANIFEST.json', 'INSTALLATION_HOLD.txt'}
    if set(files) != allowed:
        raise ValueError('Unexpected executable or public preview source in ZIP')
    head = files['fv-ex2-private-preview.php']
    payload = files['fv-ex2-private-payload.php']
    if (b'FV_EX2_ALLOW_PREVIEW' not in head or b'fv_ex2_private_authorized' not in head or
            b"['staging', 'development', 'local']" not in head or b"wp_ajax_nopriv" in head.split(b'// Deliberately NO')[0]):
        raise ValueError('Private preview plugin authorization contract missing')
    if not payload.startswith(b'<?php') or b"!defined('ABSPATH')" not in payload.replace(b' ', b''):
        raise ValueError('Payload PHP direct-access guard missing')
    manifest = json.loads(files['STAGING_MANIFEST.json'])
    if manifest.get('release_status') != 'HOLD_UNPUBLISHED_STAGING_ONLY':
        raise ValueError('Staging artifact unexpectedly marks release ready')
    if not manifest.get('payload_in_php_executable_only'):
        raise ValueError('Package exposes source outside guarded PHP')
    if digest(payload) != manifest.get('payload_sha256'):
        raise ValueError('Tampered plugin payload')
    return manifest



def verify_stage_checkout(repo: Path, expected_sha: str) -> dict[str, str]:
    """Verify the STAGING BUILDER against Git; the existing attester checks homepage files.

    Without this check an attacker can alter the builder after checkout and still obtain
    a valid attested homepage ZIP. Read-only; never executes checkout shell scripts.
    """
    if not re.fullmatch(r'[0-9a-f]{40}', expected_sha):
        raise ValueError('Require full exact Git SHA')
    def git(*args: str) -> bytes:
        run = subprocess.run(['git','-C',str(repo),*args], capture_output=True)
        if run.returncode:
            raise ValueError('STAGING SOURCE HOLD: Git failed for '+ ' '.join(args))
        return run.stdout
    if git('rev-parse','HEAD').decode().strip() != expected_sha:
        raise ValueError('STAGING SOURCE HOLD: checkout HEAD does not match requested commit')
    verified = {}
    for name in STAGE_FILES:
        rel = STAGE_SOURCE/name
        path = repo/rel
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(repo):
            raise ValueError('STAGING SOURCE HOLD: missing/unsafe '+rel.as_posix())
        git('ls-files','--error-unmatch','--',rel.as_posix())
        blob = git('show',expected_sha+':'+rel.as_posix())
        on_disk = path.read_bytes()
        if blob != on_disk:
            raise ValueError('STAGING SOURCE HOLD: uncommitted/modified '+rel.as_posix())
        verified[rel.as_posix()] = digest(on_disk)
    return verified


def verify_theme_pin(raw: bytes, expected_sha: str | None) -> str:
    """Require a separate operator-reviewed, pinned archive digest.

    The ZIP's spoofable Theme Name header alone cannot authenticate theme provenance.
    The operator MUST acquire the checksum from a trusted, separate download/record.
    """
    if expected_sha is None or not re.fullmatch(r'[0-9a-f]{64}', expected_sha):
        raise ValueError('THEME PROVENANCE HOLD: require independently recorded 64-digit SHA-256')
    observed = digest(raw)
    if observed != expected_sha:
        raise ValueError('THEME PROVENANCE HOLD: Assembler archive SHA-256 mismatch')
    return observed

def create_blueprint() -> dict:
    # These WordPress mutations execute ONLY inside the isolated Playground, not here.
    php = '''<?php
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
    return {
        '$schema': 'https://playground.wordpress.net/blueprint-schema.json',
        'landingPage': '/?pagename=' + PREVIEW_SLUG,
        'login': True,
        'steps': [
            {'step':'defineWpConfigConsts','consts':{'WP_ENVIRONMENT_TYPE':'local','FV_EX2_ALLOW_PREVIEW':True,
                                                      'WP_DEBUG':True,'WP_DEBUG_DISPLAY':False}},
            {'step':'activateTheme','themeFolderName':'assembler'},
            {'step':'activatePlugin','pluginPath':'/wordpress/wp-content/plugins/'+PLUGIN+'/fv-ex2-private-preview.php'},
            {'step':'runPHP','code':php}
        ]
    }


def build_stage(repo: Path, head: str, theme_zip: Path, out: Path, *, expected_theme_sha256: str | None = None, attester=None) -> dict:
    repo = repo.resolve(strict=True)
    out = out.resolve()
    if out == repo or repo in out.parents:
        raise ValueError('Output must be outside the Git checkout; keep staging artifacts untracked')
    if not re.fullmatch(r'[0-9a-f]{40}', head):
        raise ValueError('Require full exact Git SHA')
    if out.exists() and any(out.iterdir()):
        raise ValueError('Output directory must be empty; refusing to overwrite staging artifacts')
    # Source custody includes the staging builder itself, not only the 11 homepage assets.
    stage_source_hashes = verify_stage_checkout(repo, head)
    theme_bytes = theme_zip.read_bytes()
    verified_theme_sha = verify_theme_pin(theme_bytes, expected_theme_sha256)
    theme = safe_zip_contents(theme_zip, strip_root=True)
    validate_theme(theme)
    if attester is None:
        path = repo / ATTESTER
        spec = importlib.util.spec_from_file_location('fv_ex2_playground_attester', path)
        if spec is None or spec.loader is None:
            raise ValueError('Cannot load exact-head attester')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        attester = module.attest
    out.mkdir(parents=True, exist_ok=True)
    artifact = out/'private-preview-release-HOLD.zip'
    report = attester(repo, head, artifact)
    if report.get('git_head') != head or report.get('canonical_source_gate') != 'PASS' or report.get('production_release') != 'HOLD':
        raise ValueError('Attestation receipt failed closed')
    plugin_zip = safe_zip_contents(artifact, strip_root=False)
    if any(not k.startswith(PLUGIN + '/') for k in plugin_zip):
        raise ValueError('Plugin archive root mismatch')
    plugin = {k[len(PLUGIN)+1:]:v for k,v in plugin_zip.items()}
    manifest = validate_plugin(plugin)
    if manifest.get('expected_git_head_given_by_caller') != head:
        raise ValueError('Plugin claims a different source Git HEAD')
    for base, mapping in ((out/'mounts'/'assembler', theme), (out/'mounts'/PLUGIN, plugin)):
        for name, data in mapping.items():
            dest = base/name
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(data)
    blueprint = create_blueprint()
    (out/'playground-blueprint.json').write_text(json.dumps(blueprint,indent=2)+'\n',encoding='utf-8')
    (out/'playground-cli-arguments.json').write_text(json.dumps([
        'npx','@wp-playground/cli@latest','server',
        '--blueprint='+str(out/'playground-blueprint.json'),
        '--mount='+str(out/'mounts'/'assembler')+':/wordpress/wp-content/themes/assembler',
        '--mount='+str(out/'mounts'/PLUGIN)+':/wordpress/wp-content/plugins/'+PLUGIN,
        '--port=9400'
    ],indent=2)+'\n',encoding='utf-8')
    receipt = {'status':'LOCAL_PLAYGROUND_PREPARED_NOT_EXECUTED',
        'exact_git_head':head, 'source_attestation':report['status'],
        'plugin_sha256':digest(artifact.read_bytes()), 'assembler_zip_sha256':verified_theme_sha,
        'assembler_sha256_out_of_band_pin_verified':True,
        'official_assembler_origin_independently_confirmed':False,
        'staging_source_files_verified':stage_source_hashes,
        'assembler_file_count':len(theme),'blueprint_sha256':digest((out/'playground-blueprint.json').read_bytes()),
        'wordpress_instance':'NOT_STARTED','host':'localhost_ONLY','preview_slug':PREVIEW_SLUG,
        'production_database_export':'NOT_USED','production_tokens_or_users':'NOT_COPIED',
        'media_fetched_bytes':'NOT_MEASURED', 'auth_browser':'NOT_RUN','axe':'NOT_RUN',
        'lighthouse':'NOT_RUN','wordpress_com_atomic_parity':'NOT_ESTABLISHED',
        'media_rights':'HOLD','ci_qd':'HOLD','release':'HOLD'}
    (out/'STAGING_PREP_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    return receipt


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,required=True)
    p.add_argument('--expected-head',required=True)
    p.add_argument('--assembler-zip',type=Path,required=True,
                   help='Official Assembler theme zip, acquired separately; no downloading performed')
    p.add_argument('--out',type=Path,required=True,help='New empty LOCAL staging directory outside repo')
    p.add_argument('--expected-theme-sha256',required=True,
                   help='SHA-256 of independently acquired official Assembler ZIP; never derive from the same untrusted ZIP during this run')
    a=p.parse_args()
    try:
        receipt=build_stage(a.repo,a.expected_head,a.assembler_zip,a.out,expected_theme_sha256=a.expected_theme_sha256)
        print(json.dumps(receipt,indent=2));return 0
    except Exception as e:
        print('LOCAL STAGING PREPARATION FAILED CLOSED: '+str(e),file=sys.stderr)
        return 2


if __name__=='__main__':raise SystemExit(main())
