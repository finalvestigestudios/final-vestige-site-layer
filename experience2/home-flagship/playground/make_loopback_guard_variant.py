#!/usr/bin/env python3
"""Derive a local-only FV EX2 WordPress Playground review ZIP.

The canonical, unpublished seven-chapter bundle remains immutable. This creates an
isolated experimental variant whose BOTH MU plugins refuse non-loopback WordPress
hosts, even when the local-only option marker is accidentally copied into prod.
No public CMS or GitHub writes occur from this script.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import zipfile

SOURCE_ZIP_SHA256 = '9833800a112027b17dfec154358d7b630e258feb581820b749ca26ab88ffe69d'
CANONICAL = {
    'mu-plugins/fv-ex2-playground-review.php': '91adf4e42a711bf253370a706b29d1428131051333e470af4a841948d1e97b04',
    'mu-plugins/fv-ex2-private-browser-receipt.php': 'a58e144fd8e9e584681b7edceb667a4a5b0ca303e49b6902299b941d0a95a9fc',
}
REQUIRED_FILES = {'REVIEW.txt', 'SOURCE_CUSTODY.json', 'blueprint.json', *CANONICAL}
INSERT_AFTER = b"if (!defined('ABSPATH')) { exit; }\n"
# WordPress MU plugins are executed before normal plugins. The marker alone
# guards an option value, not the identity of the actual site requesting PHP.
# The first blueprint step already rejects non-loopback imports before writes;
# this additional guard works independently at every plugin inclusion.
GUARD = b"""// INDEPENDENT LOCAL-RUNTIME GUARD: never register preview code on a mapped host.
// Protect both preview MU plugins even if an activation option is copied.
if (!function_exists('home_url') || !function_exists('wp_parse_url')) { return; }
$fv_ex2_review_host = strtolower(rtrim((string) wp_parse_url(home_url('/'), PHP_URL_HOST), '.'));
$fv_ex2_review_loopback = in_array($fv_ex2_review_host, array('localhost','127.0.0.1','::1','[::1]'), true)
    || (strlen($fv_ex2_review_host) > 10 && substr($fv_ex2_review_host, -10) === '.localhost');
if (!$fv_ex2_review_loopback || (defined('WP_ENVIRONMENT_TYPE') && WP_ENVIRONMENT_TYPE === 'production')) { return; }
unset($fv_ex2_review_host, $fv_ex2_review_loopback);
"""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def derive(blob: bytes) -> tuple[bytes, dict]:
    if digest(blob) != SOURCE_ZIP_SHA256:
        raise ValueError('REFUSE: canonical source ZIP SHA-256 mismatch')
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        if set(z.namelist()) != REQUIRED_FILES or len(z.namelist()) != len(REQUIRED_FILES):
            raise ValueError('REFUSE: unexpected, duplicate or missing source files')
        payload = {name: z.read(name) for name in REQUIRED_FILES}
    custody = json.loads(payload['SOURCE_CUSTODY.json'])
    if not custody.get('local_only_preflight_first') or not custody.get('extra_safety_step_changes_execution_before_theme_install'):
        raise ValueError('REFUSE: first-step WordPress preflight not attested')
    for name, expected in CANONICAL.items():
        if digest(payload[name]) != expected or custody['files_sha256'].get(name) != expected:
            raise ValueError('REFUSE: protected MU plugin differs from documented source')
        if payload[name].count(INSERT_AFTER) != 1:
            raise ValueError('REFUSE: uncertain plugin insertion point')
        payload[name] = payload[name].replace(INSERT_AFTER, INSERT_AFTER + GUARD, 1)
    # Structural constraints: no change to the actual seven-chapter content.
    full = payload['mu-plugins/fv-ex2-playground-review.php']
    if full.count(b'class="fv-margin-strip__item"') != 72 or full.count(b'https://finalvestige.com/focus/') != 5:
        raise ValueError('REFUSE: 72 Margins / five Fieldbook links not preserved')
    if full.count(b'data-fv-archive-img') < 2:
        raise ValueError('REFUSE: expected image evidence missing')
    custody['files_sha256'] = {**custody['files_sha256'], **{key:digest(payload[key]) for key in CANONICAL}}
    custody['guarded_local_variant'] = {
        'kind': 'EXPERIMENTAL_LOCAL_ONLY_NOT_WORDPRESS_ACCEPTANCE',
        'canonical_bundle_sha256': SOURCE_ZIP_SHA256,
        'canonical_plugin_hashes_sha256': CANONICAL,
        'host_constraint': 'loopback/localhost AND no explicit production WP_ENVIRONMENT_TYPE',
        'binary_archive_media_verified': False,
        'wp_core_executed': False,
        'production_approved': False,
    }
    payload['SOURCE_CUSTODY.json'] = (json.dumps(custody, indent=2, sort_keys=True) + '\n').encode()
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w') as z:
        for name in sorted(REQUIRED_FILES):
            info=zipfile.ZipInfo(name, date_time=(2026, 11, 7, 0, 0, 0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o644 << 16
            z.writestr(info,payload[name],compresslevel=9)
    out=output.getvalue()
    report={
        'result': 'DERIVED_ONLY_NOT_WORDPRESS_CORE',
        'canonical_bundle_sha256': SOURCE_ZIP_SHA256,
        'derived_bundle_sha256': digest(out),
        'changed_paths': sorted(CANONICAL) + ['SOURCE_CUSTODY.json'],
        'plugins_sha256': {name: digest(payload[name]) for name in CANONICAL},
        'blueprint_sha256_unchanged': digest(payload['blueprint.json']),
        'original_html_css_js_unchanged': True,
        'release': 'HOLD',
    }
    return out,report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('canonical_zip', type=Path)
    p.add_argument('--out', type=Path, required=True)
    args=p.parse_args()
    blob, report=derive(args.canonical_zip.read_bytes())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(blob)
    print(json.dumps(report,indent=2))

if __name__ == '__main__': main()
