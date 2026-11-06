"""R167: safe Gutenberg Custom HTML block packaging of the R166 Apollo gallery.

Offline only. Never writes to WordPress, never modifies a GitHub branch during build.
Reject drift instead of guessing; an output preview is not permission to publish.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from build_offline import build

START = '<!-- wp:html -->'
END = '<!-- /wp:html -->'
TAG = 'FV_APOLLO_R167_BLOCK_PACK_V1'
HERE = Path(__file__).resolve().parent


def sha(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def payload() -> str:
    names = ('gallery-independent.css', 'gallery-fallback.css', 'gallery-independent.js', 'gallery-fallback.js')
    contents = [(HERE / name).read_text(encoding='utf-8') for name in names]
    css = '\n'.join(contents[:2])
    js = '\n'.join(contents[2:])
    return '\n<!-- ' + TAG + ' -->\n<style>\n' + css + '\n</style>\n<script>\n' + js + '\n</script>\n'


def package(source: str) -> tuple[str, dict]:
    if not source or not source.rstrip().endswith(END):
        raise ValueError('HOLD: WordPress editor must end with a closed Custom HTML block')
    if TAG in source:
        raise ValueError('HOLD: R167 staging payload already present; no duplicate insertion')
    count = source.count(START)
    if count < 2 or count != source.count(END):
        raise ValueError('HOLD: unexpected Gutenberg Custom HTML block count')
    if source.count('<script>') != 1 or source.count('</script>') != 1:
        raise ValueError('HOLD: expected exactly one existing WordPress behavior script')
    last_start = source.rfind(START)
    last_end = source.rfind(END)
    if last_start < 0 or last_end <= last_start or START in source[last_start + len(START):last_end]:
        raise ValueError('HOLD: last Gutenberg block is not well-formed')
    if '<script>' not in source[last_start:last_end]:
        raise ValueError('HOLD: final Custom HTML block is not the existing behavior module')

    # R166 verifies source custody and deletes *only* the old fire-second photo switch.
    r166 = build(source)
    addition = '\n<style>\n' + '\n'.join((HERE / name).read_text(encoding='utf-8') for name in ('gallery-independent.css', 'gallery-fallback.css')) + '\n</style>\n<script>\n' + '\n'.join((HERE / name).read_text(encoding='utf-8') for name in ('gallery-independent.js', 'gallery-fallback.js')) + '\n</script>\n'
    if not r166.endswith(addition):
        raise ValueError('HOLD: R166 append contract has changed')
    clean = r166[:-len(addition)]
    if not clean.rstrip().endswith(END):
        raise ValueError('HOLD: WordPress block tail has drifted')
    last = clean.rfind(END)
    output = clean[:last] + payload() + clean[last:]
    if output.count(START) != count or output.count(END) != count:
        raise AssertionError('HOLD: WordPress block structure changed')
    if output.count(TAG) != 1 or output.count('<script>') != 2:
        raise AssertionError('HOLD: missing/duplicate staged payload')
    if output.count('const index = t < 6 ? 0 : (t < 11.3 ? 1 : 2);'):
        raise AssertionError('HOLD: the conflated photo/chronology switch survived')
    if output.count('data-fvx-chrono-gallery') < 1:
        raise AssertionError('HOLD: gallery lost')
    manifest = {
        'status': 'OFFLINE_STAGING_HOLD', 'wordPress_writes': 0,
        'src_sha256': sha(source), 'out_sha256': sha(output),
        'gutenberg_custom_html_blocks': count,
        'source_nasa_records': 3,
        'js_script_blocks_before': 1, 'js_script_blocks_after': 2,
        'payload_marker': TAG,
        'approved_for_publish': False,
    }
    return output, manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('editor_source', type=Path)
    parser.add_argument('preview_output', type=Path)
    options = parser.parse_args()
    output, manifest = package(options.editor_source.read_text(encoding='utf-8'))
    options.preview_output.write_text(output, encoding='utf-8')
    options.preview_output.with_suffix('.manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(manifest, sort_keys=True))


if __name__ == '__main__':
    main()
