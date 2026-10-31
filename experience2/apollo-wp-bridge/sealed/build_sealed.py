#!/usr/bin/env python3
"""Produce private staging-only single-PHP plugin from *exact* PR215 source.

No WordPress writes, no network, no static unpublished source files under
wp-content/plugins. Files are zlib-compressed, per-asset SHA256-verified PHP
constants. All content and downloads are served only via authenticated Ajax.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile
import zlib

from qa.custody_integrity import check_directory
from qa.nasa_editorial_gate import audit_files
from qa.source_concordance import build_concordance, build_context_index

HERE = Path(__file__).resolve().parent
BRIDGE = HERE.parent
UPSTREAM = BRIDGE.parent / 'apollo-casefile'
FILES = ('fragment.html', 'apollo.css', 'apollo.js',
         'evidence-export.csv', 'evidence-export.json',
         'response-export.csv', 'response-export.json')
MARKER = '/* FV_EX2_APOLLO_SEALED_CONSTANTS */'
ROOT = 'fv-ex2-apollo-private-review'
PIN = '74375657f2cdaac0710f94c6de6c24534ee06858'


def build(out: Path) -> dict:
    pin = json.loads((BRIDGE / 'upstream-pr215-blobs.json').read_text(encoding='utf-8'))
    if pin.get('pinned_head') != PIN or len(pin.get('expected_blob_sha1', {})) != 12:
        raise ValueError('Apollo upstream pinset is missing or altered')
    if any(not isinstance(h, str) or len(h) != 40 or any(c not in '0123456789abcdef' for c in h)
           for h in pin['expected_blob_sha1'].values()):
        raise ValueError('Apollo SHA-1 pin must contain EXACTLY 40 lowercase hex characters')
    # Do not permit the fixture bypass in this installer-quality artifact path.
    clean_env = dict(os.environ)
    clean_env.pop('FV_EX2_ALLOW_UNPINNED_FIXTURE', None)
    b = subprocess.run([sys.executable, str(BRIDGE / 'build.py')], cwd=BRIDGE,
                       env=clean_env, capture_output=True, text=True, timeout=60)
    if b.returncode:
        raise RuntimeError('Canonical upstream build refused: ' + b.stdout + b.stderr)
    src = json.loads((BRIDGE / 'generated/manifest.json').read_text(encoding='utf-8'))
    if (src.get('pinned_head') != PIN or src.get('source_matches_pr215') is not True
            or src.get('source_pin_mismatches') != []
            or sorted(src.get('outputs_sha256', [])) != sorted(FILES)):
        raise ValueError('Source custody and generated output manifest disagree')
    # Historical claim/source parity, active HTML injection and data export integrity
    # are mandatory, not optional QA invoked after packaging.
    custody_receipt = check_directory(BRIDGE / 'generated')
    nasa_receipt = audit_files(UPSTREAM, BRIDGE / 'generated')
    concordance_html, concordance_css, concordance_receipt = build_concordance(UPSTREAM, BRIDGE / 'generated')
    context_index = build_context_index(UPSTREAM, BRIDGE / 'generated')
    if hashlib.sha256(context_index.encode('utf-8')).hexdigest() != concordance_receipt['context_index_sha256']:
        raise ValueError('Derived context-index and concordance receipt mismatch')
    payload = {}
    hashes = {}
    sizes = {}
    for name in FILES:
        raw = (BRIDGE / 'generated' / name).read_bytes()
        assert len(raw) > 0 and len(raw) <= 500_000
        sha = hashlib.sha256(raw).hexdigest()
        if sha != src['outputs_sha256'][name]:
            raise ValueError('Output artifact mutated: ' + name)
        sizes[name] = len(raw)
        hashes[name] = sha
        payload[name] = base64.b64encode(zlib.compress(raw, 9)).decode('ascii')
    for name, text in (('source-concordance.html', concordance_html), ('source-concordance.css', concordance_css),
                       ('source-context.json', context_index)):
        raw = text.encode('utf-8')
        sizes[name] = len(raw)
        hashes[name] = hashlib.sha256(raw).hexdigest()
        payload[name] = base64.b64encode(zlib.compress(raw, 9)).decode('ascii')
    template = (HERE / 'fv-ex2-apollo-sealed-template.php').read_text(encoding='utf-8')
    if template.count(MARKER) != 1:
        raise ValueError('PHP template marker not unique')
    data = (
        "define('FV_EX2_APOLLO_PACKED', json_decode('" + json.dumps(payload, sort_keys=True, separators=(',', ':')) + "', true));\n"
        + "define('FV_EX2_APOLLO_SHA256', json_decode('" + json.dumps(hashes, sort_keys=True, separators=(',', ':')) + "', true));\n"
        + "define('FV_EX2_APOLLO_LENGTHS', json_decode('" + json.dumps(sizes, sort_keys=True, separators=(',', ':')) + "', true));\n"
        + "define('FV_EX2_APOLLO_SOURCE_HEAD', '" + PIN + "');"
    )
    php = template.replace(MARKER, data)
    if 'add_action(\'wp_ajax_nopriv_' in php or 'add_action(\"wp_ajax_nopriv_' in php:
        raise ValueError('Public AJAX route prohibited')
    manifest = {
        'purpose': 'PRIVATE_APOLLO_CASEFILE_STAGING_PREVIEW_ONLY',
        'source_pr215_head': PIN,
        'source_match_all_12_blob_pins': True,
        'nasa_catalog_witness': nasa_receipt,
        'source_concordance': concordance_receipt,
        'research_desk_pr158_readonly_witness': concordance_receipt['research_desk_crosswalk'],
        'custody_lint': {k: custody_receipt[k] for k in ('status','pinned_head','dom_ids',
                         'source_drawers','anchors','external_source_links',
                         'evidence_records','response_records','csv_json_parity')},
        'outputs_sha256': hashes,
        'outputs_bytes': sizes,
        'plugin_sha256': hashlib.sha256(php.encode('utf-8')).hexdigest(),
        'routes': ['authorized staging editor shortcode', 'authorized nonce-checked Ajax HTML',
                   'authorized nonce-checked CSV/JSON downloads including source context index'],
        'generated_public_static_assets': [],
        'non_waivable_holds': ['No WordPress installation or activation performed',
                               'Requires WP_ENVIRONMENT_TYPE=staging and FV_EX2_APOLLO_STAGING_ALLOW=true',
                               'axe-core and screen-reader testing not yet certified',
                               'Exact WordPress staging HTTP/cookies and real-user CWV needed',
                               'NASA media rights per item and independent QD',
                               'PR158 catalog identifier-label mismatch for crew portrait must be independently reviewed',
                               'No main or homepage merges without separate approval'],
    }
    members = {
        ROOT + '/fv-ex2-apollo-sealed.php': php.encode('utf-8'),
        ROOT + '/SEALED_SOURCE_MANIFEST.json': (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode('utf-8'),
        ROOT + '/INSTALLATION_HOLD.txt': (
            'STAGING INSTALL REQUIRES SEPARATE APPROVAL. NO PRODUCTION INSTALL.\n'
            'WP_ENVIRONMENT_TYPE=staging, FV_EX2_APOLLO_STAGING_ALLOW=true and logged-in edit_pages role are mandatory.\n'
            'Shortcode: [fv_ex2_apollo_sealed_preview]. No static artifacts in plugin directory.\n'
            'Review source rights, accessibility, independent QA and release gates.\n'
        ).encode('utf-8'),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, content in sorted(members.items()):
            info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    m = build(args.out)
    print(json.dumps({'package': str(args.out), 'bytes': args.out.stat().st_size,
                      'source': m['source_pr215_head'], 'outputs': len(m['outputs_sha256']),
                      'plugin_sha256': m['plugin_sha256']}, indent=2))
