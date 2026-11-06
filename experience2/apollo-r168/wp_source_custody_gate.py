"""R168 immutable-page attestation and high-contrast Gutenberg staging wrapper.

This module only transforms caller-supplied editor content into an *offline* preview.
It never opens a network connection or writes to WordPress, GitHub or a merchant.
A new published revision MUST cause a HOLD until independently reviewed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from wp_block_pack import package as package_r167, START, END, TAG as R167_TAG
from build_offline import REQUIRED_NASA

# Read-only WordPress pages_get(context=edit) witness, November 6, 2026 PT.
# Hash is for UTF-8 bytes of the *raw edit-context content* (not JSON-escaped).
WITNESS = {
    'wp_page_id': 2017,
    'slug': 'apollo-1-evidence-atlas',
    'modified': '2026-11-05T18:19:45',
    'source_sha256': '6948f3d62d91d08c27a3a4b71122fef6ef37bdd333c31f81c27db4ad95ce5e4c',
    'source_bytes_utf8': 96302,
    'wp_custom_html_blocks': 9,
    'editor_scripts': 1,
}
R168_TAG = 'FV_APOLLO_R168_CUSTODY_A11Y_V1'
HERE = Path(__file__).resolve().parent
CONTRACT_CSS = (HERE / 'archive-accessibility.r168.css')


def digest(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def validate_source(source: str, witness: dict = WITNESS) -> dict:
    """Reject wrong post, changed source, lost citations, ambiguous Gutenberg edits."""
    if not isinstance(source, str) or not source:
        raise ValueError('HOLD: missing raw WordPress editor content')
    if len(source.encode('utf-8')) != witness['source_bytes_utf8']:
        raise ValueError('HOLD: WordPress page size changed; renew read-only witness')
    if digest(source) != witness['source_sha256']:
        raise ValueError('HOLD: WordPress page SHA-256 changed; renew read-only witness')
    if source.count(START) != witness['wp_custom_html_blocks'] or source.count(END) != witness['wp_custom_html_blocks']:
        raise ValueError('HOLD: WordPress block boundaries changed')
    if source.count('<script>') != witness['editor_scripts']:
        raise ValueError('HOLD: source script count changed')
    if R167_TAG in source or R168_TAG in source:
        raise ValueError('HOLD: source already contains a staging marker')
    marker = 'class="fvx-chrono-gallery" data-fvx-chrono-gallery'
    if source.count(marker) != 1:
        raise ValueError('HOLD: original gallery missing or duplicated')
    start = source.index(marker)
    stop = source.find('data-fvx-chrono-position', start)
    if stop < start:
        raise ValueError('HOLD: gallery provenance boundary missing')
    region = source[start:stop]
    for record in REQUIRED_NASA:
        if region.count(record) != 1:
            raise ValueError('HOLD: archival NASA source changed or duplicated: ' + record)
    if source.count('const index = t < 6 ? 0 : (t < 11.3 ? 1 : 2);') != 1:
        raise ValueError('HOLD: historical conflation signature has drifted')
    return {'source_sha256': digest(source), 'source_bytes_utf8': len(source.encode('utf-8')),
            'gutenberg_blocks': source.count(START), 'archival_nasa_sources': list(REQUIRED_NASA)}


def stage(source: str, witness: dict = WITNESS) -> tuple[str, dict]:
    custody = validate_source(source, witness)
    result, r167_manifest = package_r167(source)
    last = result.rfind(END)
    if last < 0 or R167_TAG not in result[result.rfind(START):last]:
        raise AssertionError('HOLD: R167 packaging no longer inside Gutenberg final block')
    supplement = '\n<!-- ' + R168_TAG + ' -->\n<style>\n' + CONTRACT_CSS.read_text(encoding='utf-8') + '\n</style>\n'
    result = result[:last] + supplement + result[last:]
    # Preserve original source/external hrefs, CTA and every existing block boundary.
    if result.count(START) != custody['gutenberg_blocks'] or result.count(END) != custody['gutenberg_blocks']:
        raise AssertionError('HOLD: block boundaries changed during staging')
    if result.count('<a ') != source.count('<a '):
        raise AssertionError('HOLD: original outgoing or internal link count changed')
    for record in REQUIRED_NASA:
        if result.count(record) != source.count(record):
            raise AssertionError('HOLD: NASA citation count changed')
    if result.count(R167_TAG) != 1 or result.count(R168_TAG) != 1:
        raise AssertionError('HOLD: staging marker missing or duplicated')
    if 'const index = t < 6 ? 0 : (t < 11.3 ? 1 : 2);' in result:
        raise AssertionError('HOLD: archival images still tied to fire seconds')
    return result, {
        'status': 'OFFLINE_STAGING_HOLD', 'approved_for_publish': False,
        'wordpress_writes': 0, 'merchant_activations': 0, 'social_posts': 0,
        'source_witness': witness, 'preflight': custody,
        'r167_preview_sha256': r167_manifest['out_sha256'],
        'r168_preview_sha256': digest(result),
        'r168_marker': R168_TAG, 'report_kind': 'controlled_source-derived_preview_not_wordpress_acceptance',
    }


def main() -> None:
    cli = argparse.ArgumentParser(description='Stage exactly attested raw WP editor content OFFLINE; never publish.')
    cli.add_argument('editor_source', type=Path)
    cli.add_argument('preview_output', type=Path)
    args = cli.parse_args()
    source = args.editor_source.read_text(encoding='utf-8')
    html, receipt = stage(source)
    args.preview_output.parent.mkdir(parents=True, exist_ok=True)
    args.preview_output.write_text(html, encoding='utf-8')
    args.preview_output.with_suffix('.manifest.json').write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, sort_keys=True))

if __name__ == '__main__':
    main()
