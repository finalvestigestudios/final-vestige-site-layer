#!/usr/bin/env python3
"""Build a self-contained, LOCAL WordPress Playground review of one scoped Page 6 edit.

This prepares an OFFLINE review ZIP. It does not connect to WordPress or install,
publish, deploy, send emails, or touch the production database. Never commit a
bundle containing real production page HTML into public GitHub.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile

THIS = Path(__file__).resolve()
COMPOSER = THIS.with_name('compose_page6_flagship.py')
SOURCE_ROOT = THIS.parents[2] / 'experience2' / 'home-flagship'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True, stderr=subprocess.PIPE).strip()


def verify_source(repo: Path, source_dir: Path, expected_head: str, pins: dict[str, str]):
    if not re.fullmatch(r'[a-f0-9]{40}', expected_head):
        raise ValueError('Expected HEAD must be a complete lowercase Git SHA-1')
    if git(repo, 'rev-parse', 'HEAD') != expected_head:
        raise ValueError('Exact checkout HEAD mismatch: no bundle produced')
    for file, known_sha in pins.items():
        actual = source_dir / file
        if actual.is_symlink() or not actual.is_file() or repo not in actual.resolve().parents:
            raise ValueError('Missing, symlinked or foreign tracked source: '+file)
        relative = actual.relative_to(repo).as_posix()
        blob = git(repo, 'rev-parse', f'HEAD:{relative}')
        worktree = git(repo, 'hash-object', '--', relative)
        if blob != known_sha or worktree != known_sha:
            raise ValueError('Source or tracked Git blob identity changed: '+file)
    if COMPOSER.is_symlink() or not COMPOSER.is_file():
        raise ValueError('Composer missing or symlinked')
    rel = COMPOSER.relative_to(repo).as_posix()
    if git(repo, 'rev-parse', f'HEAD:{rel}') != git(repo, 'hash-object', '--', rel):
        raise ValueError('Composer differs from exact source HEAD')


def module():
    spec = importlib.util.spec_from_file_location('fv_page6_composer', COMPOSER)
    result = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(result)
    return result


def guarded_php(sha: str, synthetic: bool, expected_top: int, expected_html: int) -> str:
    # WordPress Playground's own PHP runtime must independently parse the actual
    # Gutenberg block stream; this cannot be certified by a Python string check.
    assert re.fullmatch(r'[0-9a-f]{64}', sha)
    assert 3 <= expected_html <= 12 and expected_top >= expected_html
    source_type = 'SYNTHETIC TEST RECORDS ONLY' if synthetic else 'PUBLIC PAGE 6 CONTENT ONLY'
    return r'''<?php
require_once '/wordpress/wp-load.php';
if (wp_get_environment_type() !== 'local' || !defined('FV_EX2_LOCAL_ONLY') || FV_EX2_LOCAL_ONLY !== true) {
    throw new RuntimeException('Not a verified isolated LOCAL WordPress Playground');
}
$path = '/tmp/fv-ex2-page6-review.blocks.html';
$raw = file_get_contents($path);
if (!is_string($raw) || hash('sha256', $raw) !== 'EXPECTED_HASH') {
    throw new RuntimeException('Page 6 scoped source transfer digest mismatch');
}
$blocks = parse_blocks($raw);
$names = array();
$scan = function($blocks) use (&$scan, &$names) {
    foreach ($blocks as $block) {
        $names[] = $block['blockName'];
        if (!empty($block['innerBlocks'])) { $scan($block['innerBlocks']); }
    }
};
$scan($blocks);
// Fail closed on the original Focus CTA in a NON-FLAGSHIP Gutenberg HTML
// block. The standalone seven-chapter payload must never satisfy this gate.
preg_match_all('~<!-- wp:html -->(.*?)<!-- /wp:html -->~s', $raw, $chunk_matches);
$outside_chunks = array();
$flagship_count = 0;
foreach ($chunk_matches[1] as $chunk) {
    if (strpos($chunk, 'data-fv-home-flagship') !== false) {
        $flagship_count++;
    } else {
        $outside_chunks[] = $chunk;
    }
}
$outside = implode("\n", $outside_chunks);
$focus_sections = array();
preg_match_all('~<section\b[^>]*class="(?=[^"]*\bfv-focus-cta\b)[^"]+"[^>]*>(.*?)</section>~is', $outside, $focus_sections);
$focus_action_valid = false;
if (count($chunk_matches[1]) === EXPECTED_HTML && $flagship_count === 1 && count($focus_sections[1]) === 1) {
    $focus_actions = array();
    preg_match_all('~<a\b(?=[^>]*\bclass="[^"]*\bfv-focus-cta__button\b)[^>]*\bhref="([^"]+)"[^>]*>~is', $focus_sections[1][0], $focus_actions);
    $focus_href = count($focus_actions[1]) === 1 ? html_entity_decode($focus_actions[1][0], ENT_QUOTES, 'UTF-8') : '';
    $focus_action_valid = $focus_href === '/focus/' || $focus_href === 'https://finalvestige.com/focus/';
}
if (count($blocks) !== EXPECTED_TOP || count(array_filter($names, fn($x) => $x === 'core/html')) !== EXPECTED_HTML ||
    count(array_filter($names, fn($x) => $x === 'jetpack/subscriptions')) !== 1 ||
    substr_count($raw, 'class="fv-margin-strip__item') !== 72 ||
    substr_count($raw, 'data-fv-home-flagship') < 1 ||
    !$focus_action_valid) {
    throw new RuntimeException('Gutenberg, 72 Margins or native Jetpack/Focus custody failed');
}
if (get_page_by_path('fv-ex2-integrated-review')) {
    throw new RuntimeException('Refusing to overwrite an existing local review page');
}
$id = wp_insert_post(array(
    'post_title' => 'FV EX2 ISOLATED REVIEW — SOURCE_TYPE',
    'post_name' => 'fv-ex2-integrated-review', 'post_status' => 'private',
    'post_type' => 'page', 'post_content' => wp_slash($raw)
), true);
if (is_wp_error($id) || !$id) {
    throw new RuntimeException('WordPress rejected isolated review page');
}
$saved = get_post($id);
if (!$saved || hash('sha256', $saved->post_content) !== 'EXPECTED_HASH') {
    wp_delete_post($id, true); // Deletes only the newly created LOCAL review page.
    throw new RuntimeException('WordPress changed the Gutenberg source during insertion');
}
update_post_meta($id, '_fv_ex2_review_only', 'LOCAL_NO_PRODUCTION');
// Deliberately no activation of Jetpack, no emails, no public homepage replacement.
// Native Jetpack serialized block is preserved but may not render without Jetpack.
'''.replace('EXPECTED_HASH',sha).replace('SOURCE_TYPE',source_type).replace('EXPECTED_TOP',str(expected_top)).replace('EXPECTED_HTML',str(expected_html))


def blueprint(sha: str, synthetic: bool, expected_top: int, expected_html: int) -> dict:
    return {
        '$schema':'https://playground.wordpress.net/blueprint-schema.json',
        'meta':{'title':'Final Vestige EX2 — private integrated Page 6 review',
                'description':'Local, non-production Gutenberg layout check. Not Jetpack or Assembler acceptance.'},
        'preferredVersions':{'php':'8.3','wp':'latest'},
        'landingPage':'/wp-admin/edit.php?post_type=page',
        'login':True,
        'steps':[
            {'step':'defineWpConfigConsts','consts':{'WP_ENVIRONMENT_TYPE':'local','FV_EX2_LOCAL_ONLY':True,'DISALLOW_FILE_EDIT':True}},
            {'step':'writeFile','path':'/tmp/fv-ex2-page6-review.blocks.html','data':{'resource':'bundled','path':'/page6-review.blocks.html'}},
            {'step':'runPHP','code':guarded_php(sha,synthetic,expected_top,expected_html)},
        ],
    }


def zwrite(z: zipfile.ZipFile, name: str, data: bytes):
    info=zipfile.ZipInfo(name, date_time=(1980,1,1,0,0,0))
    info.compress_type=zipfile.ZIP_DEFLATED
    info.external_attr=0o600 << 16
    z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)


def build(repo: Path, source_dir: Path, page6: Path, out: Path, head: str, page_digest: str, synthetic: bool=False) -> dict:
    repo=repo.resolve(strict=True)
    source_dir=source_dir.resolve(strict=True)
    if page6.is_symlink() or not page6.is_file():
        raise ValueError('Missing or symlinked page content source')
    if out.is_symlink() or out.exists() or repo == out.resolve() or repo in out.resolve().parents or {'wp-content','public_html'} & set(out.parts):
        raise ValueError('Output must be a new file outside the repository or WordPress webroot')
    if not re.fullmatch('[0-9a-f]{64}', page_digest):
        raise ValueError('Explicit page source SHA-256 required')
    cm=module()
    verify_source(repo,source_dir,head,cm.PINNED_GIT_BLOBS)
    data=page6.read_bytes()
    if digest(data)!=page_digest:
        raise ValueError('Page 6 source digest mismatch; stop on drift')
    raw=data.decode('utf-8')
    if synthetic and 'FV-SYNTHETIC-FIXTURE' not in raw:
        raise ValueError('Synthetic test bundle must be unmistakably labeled')
    if not synthetic and 'FV-SYNTHETIC-FIXTURE' in raw:
        raise ValueError('Refusing synthetic Gutenberg content as real Page 6')
    composed,receipt=cm.compose(raw,cm.stage_payload(source_dir))
    payload=composed.encode('utf-8')
    expected_html=composed.count('<!-- wp:html -->')
    if composed.count('<!-- wp:group') != 1 or expected_html not in (4,5):
        raise ValueError('Unexpected Gutenberg review fixture block composition')
    expected_top=expected_html+1
    php=guarded_php(digest(payload),synthetic,expected_top,expected_html)
    if 'wp_insert_post' not in php or 'parse_blocks' not in php:
        raise ValueError('Required genuine WordPress integration gates absent')
    bp=json.dumps(blueprint(digest(payload),synthetic,expected_top,expected_html),indent=2,ensure_ascii=False).encode('utf-8')+b'\n'
    localbp=blueprint(digest(payload),synthetic,expected_top,expected_html)
    localbp['steps'][1]['data']=composed  # WordPress Playground writeFile accepts inline UTF-8 text.
    local_bytes=json.dumps(localbp,indent=2,ensure_ascii=False).encode('utf-8')+b'\n'
    source_manifest={
        'release':'HOLD','kind':'ISOLATED_WORDPRESS_PLAYGROUND_BLUEPRINT_BUNDLE',
        'real_page6':not synthetic,'verified_source_head':head,
        'public_page_sha256':page_digest,'composed_content_sha256':digest(payload),
        'blueprint_sha256':digest(bp),'local_cli_blueprint_sha256':digest(local_bytes),'composer_git_blobs':cm.PINNED_GIT_BLOBS,
        'gutenberg_native_jetpack_record_retained':True,
        'jetpack_operational_confirmation':'NOT_TESTED',
        'assembler_theme_equivalence':'NOT_TESTED',
        'wordpress_runtime_execution':'NOT_TESTED',
        'production_site_modified':False,
        'image_transfer_bytes':'NOT_MEASURED',
        'wcag_lighthouse_qd_ci':'NOT_ACCEPTED',
        'scoped_editor_only':receipt,
    }
    warning=('FINAL VESTIGE — OFFLINE WORDPRESS PLAYGROUND REVIEW ONLY\n'
             'THIS ZIP IS NOT A DEPLOYABLE SITE OR PRODUCTION INSTALLER.\n'
             'WordPress Playground is a new temporary, isolated WordPress database.\n'
             'All 72 Margins and serialized Jetpack block are preserved, but\n'
             'Jetpack cannot be claimed functional in Playground. Assembler and\n'
             'WordPress.com Atomic differences remain. No release approval.\n'
             'Do not upload a real-public-Page6 bundle to public GitHub, Drive\n'
             'or a public web host. Avoid sharing subscriber or private data.\n').encode('utf-8')
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for file,content in sorted({
            'blueprint.json':bp,'blueprint.local-cli.json':local_bytes,'page6-review.blocks.html':payload,
            'MANIFEST.json':(json.dumps(source_manifest,indent=2,sort_keys=True)+'\n').encode(),
            'DO_NOT_DEPLOY.txt':warning,
        }.items()):
            zwrite(z,file,content)
    return {'bundle':str(out),'bundle_sha256':digest(out.read_bytes()),
            'composed_sha256':digest(payload), 'blueprint_sha256':digest(bp),'local_cli_blueprint_sha256':digest(local_bytes),
            'source_head':head,'real_page6':not synthetic,
            'release':'HOLD','runtime_tested':False,
            'out_of_scope_untouched_bytes':receipt['untouched_external_bytes']}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,required=True)
    p.add_argument('--source-dir',type=Path,required=True)
    p.add_argument('--page6-raw',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--expected-head',required=True)
    p.add_argument('--expected-page-sha256',required=True)
    p.add_argument('--synthetic-fixture',action='store_true')
    a=p.parse_args()
    try:
        receipt=build(a.repo,a.source_dir,a.page6_raw,a.out,a.expected_head,a.expected_page_sha256,a.synthetic_fixture)
        print(json.dumps(receipt,indent=2))
    except (OSError,ValueError,subprocess.CalledProcessError) as exc:
        print('ADMISSION HOLD:',str(exc),file=sys.stderr)
        raise SystemExit(2) from exc

if __name__=='__main__':
    main()
