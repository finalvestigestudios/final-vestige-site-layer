#!/usr/bin/env python3
"""Pack exact FV EX2 private Playground receipt into a local-only Blueprint bundle.
Transport/package verification only; not WordPress, WCAG, Lighthouse or release QA.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

BP_HASH = '300c79f7936d7fdf58294bb96e7b0cd1ebc0b349cdf4d2c4d13e5ec52000b23f'
RECEIPT_HASH = 'a58e144fd8e9e584681b7edceb667a4a5b0ca303e49b6902299b941d0a95a9fc'
ASSEMBLER = '75faa8a1e0367a37c2638250a3c9ed0a0f8c0b7f'
CANONICAL_BLOB = '137c74a476005684a28f5ff9a36e75c6b03268f7'
# A Blueprint may otherwise activate Assembler and overwrite the site's front-page
# settings before any environment check. This read-only runPHP step MUST come first.
# It intentionally admits only loopback-hosted local development, NOT remote preview
# services, WordPress.com, production domains or publicly exposed tunnels.
LOCAL_PREFLIGHT = r'''<?php
require_once '/wordpress/wp-load.php';
$site = wp_parse_url(home_url('/'));
$host = strtolower(rtrim((string) ($site['host'] ?? ''), '.'));
$loopback = $host === 'localhost' || $host === '127.0.0.1' ||
    $host === '::1' || $host === '[::1]' ||
    (strlen($host) > 10 && substr($host, -10) === '.localhost');
if (!$loopback) {
    throw new RuntimeException('FV_EX2_REFUSE_NON_LOOPBACK_BEFORE_ANY_SITE_WRITE');
}
if (defined('WP_ENVIRONMENT_TYPE') && WP_ENVIRONMENT_TYPE === 'production') {
    throw new RuntimeException('FV_EX2_REFUSE_EXPLICIT_PRODUCTION_ENVIRONMENT');
}
'''

PATHS = {
    '/wordpress/wp-content/mu-plugins/fv-ex2-playground-review.php': '/mu-plugins/fv-ex2-playground-review.php',
    '/wordpress/wp-content/mu-plugins/fv-ex2-private-browser-receipt.php': '/mu-plugins/fv-ex2-private-browser-receipt.php',
}

def sha(b):
    return hashlib.sha256(b).hexdigest()

def pack(raw_zip):
    with ZipFile(io.BytesIO(raw_zip)) as z:
        original = z.read('blueprint_with_local_receipt.json')
        manifest = json.loads(z.read('source_manifest.json'))
    if sha(original) != BP_HASH or manifest.get('derived_blueprint_sha256') != BP_HASH:
        raise ValueError('SOURCE_DRIFT: candidate Blueprint changed')
    if manifest.get('source_blueprint_blob') != CANONICAL_BLOB or manifest.get('theme_commit') != ASSEMBLER or manifest.get('reviewer_plugin_sha256') != RECEIPT_HASH:
        raise ValueError('PIN_DRIFT: theme/BluePrint/reviewer version changed')
    bp = json.loads(original)
    if bp.get('landingPage') != '/' or bp.get('login') is not True:
        raise ValueError('UNEXPECTED_ENTRYPOINT')
    themes = [s for s in bp['steps'] if s.get('step') == 'installTheme']
    if len(themes) != 1 or themes[0].get('themeData', {}).get('ref') != ASSEMBLER or themes[0]['themeData'].get('path') != 'assembler':
        raise ValueError('UNPINNED_ASSEMBLER')
    write = [s for s in bp['steps'] if s.get('step') == 'writeFile']
    if len(write) != 2 or {s.get('path') for s in write} != set(PATHS) or len([s for s in bp['steps'] if s.get('step') == 'runPHP']) != 2:
        raise ValueError('UNEXPECTED_WORDPRESS_WRITE')
    rebuilt = json.loads(original)
    payloads = {}
    for s in write:
        if not isinstance(s.get('data'), str) or not s['data'].startswith('<?php'):
            raise ValueError('UNEXPECTED_PHP_PAYLOAD')
        path = PATHS[s['path']]
        blob = s['data'].encode('utf-8')
        if path.endswith('browser-receipt.php') and sha(blob) != RECEIPT_HASH:
            raise ValueError('RECEIPT_DRIFT')
        payloads[path.lstrip('/')] = blob
        s['data'] = {'resource': 'bundled', 'path': path}
    # Preserve original steps as an ordered suffix; prepend read-only safety admission.
    rehydrated = json.loads(json.dumps(bp))
    for s in rehydrated['steps']:
        if s.get('step') == 'writeFile':
            s['data'] = payloads[s['data']['path'].lstrip('/')].decode('utf-8')
    if rehydrated != rebuilt:
        raise ValueError('NON_PRESERVING_BUNDLE')
    bp['steps'].insert(0, {'step': 'runPHP', 'code': LOCAL_PREFLIGHT})
    if bp['steps'][0]['code'] != LOCAL_PREFLIGHT or len(bp['steps']) != len(rebuilt['steps']) + 1:
        raise ValueError('PREFLIGHT_NOT_FIRST')
    receipt = {'exact_source_sha256': BP_HASH, 'source_blueprint_blob': CANONICAL_BLOB,
               'assembler_commit': ASSEMBLER,'files_sha256': {k: sha(v) for k,v in payloads.items()},
               'php_and_import_steps_preserved': True, 'local_only_preflight_first': True,
               'extra_safety_step_changes_execution_before_theme_install': True,
               'native_wordpress_tested': False,
               'real_image_bytes_verified': False, 'release_authorized': False}
    guidance = ('FV EX2 PRIVATE LOCAL PLAYGROUND REVIEW ONLY. NOT a production clone.\n'
        'Requires Internet access to install the CLI and fetch the pinned Assembler theme.\n'
        'First read-only runPHP step refuses non-loopback sites before theme/site edits.\n'
        'Run: npx @wp-playground/cli --blueprint=./fv-ex2-local-cli-bundle.zip server\n'
        'Review on reported loopback port; inspect 7 chapters/72 Margins/5 Focus\n'
        'destinations, 2 authentic images, source responses, keyboard/no-JS, axe,\n'
        'Lighthouse and the viewport JSON receipt. Record FAIL where unavailable.\n'
        'No WordPress.com hosting, Jetpack delivery, paid orders, WCAG certification,\n'
        'or field CWV is established by this ZIP. Never install on production.\n')
    contents = {'blueprint.json': json.dumps(bp, ensure_ascii=False, separators=(',', ':')).encode(),
                'SOURCE_CUSTODY.json': json.dumps(receipt, sort_keys=True, indent=2).encode(),
                'REVIEW.txt': guidance.encode(), **payloads}
    output = io.BytesIO()
    with ZipFile(output, 'w', compression=ZIP_DEFLATED, compresslevel=9) as z:
        for path in sorted(contents):
            info = ZipInfo(path, date_time=(2026, 11, 7, 0, 0, 0))
            info.external_attr = 0o644 << 16
            info.compress_type = ZIP_DEFLATED
            z.writestr(info, contents[path], compress_type=ZIP_DEFLATED, compresslevel=9)
    return output.getvalue(), receipt

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    data, receipt = pack(args.input.read_bytes())
    args.output.write_bytes(data)
    print(json.dumps({'bundle_sha256': sha(data), 'bytes': len(data), **receipt}, indent=2))
