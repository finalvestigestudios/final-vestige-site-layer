#!/usr/bin/env python3
"""Derived review-only WordPress Playground Blueprint with in-page evidence export.

Never modifies canonical homepage, stored WordPress content or WordPress.com production.
An actual Playground runtime and real media are NOT tested by packaging.
"""
import argparse
import base64
import hashlib
import html
import json
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

SOURCE_BLOB = '137c74a476005684a28f5ff9a36e75c6b03268f7'
ASSEMBLER_SHA = '75faa8a1e0367a37c2638250a3c9ed0a0f8c0b7f'
PLUGIN_SHA256 = 'a58e144fd8e9e584681b7edceb667a4a5b0ca303e49b6902299b941d0a95a9fc'
PLUGIN_PATH = '/wordpress/wp-content/mu-plugins/fv-ex2-private-browser-receipt.php'
MARKER = 'FV_EX2_LOCAL_PLAYGROUND_2026_11_05_V1'


def git_blob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def derive(original, plugin):
    if git_blob(original) != SOURCE_BLOB:
        raise ValueError('Canonical Blueprint blob not pinned: release HOLD')
    if hashlib.sha256(plugin).hexdigest() != PLUGIN_SHA256:
        raise ValueError('Isolated reviewer plugin not pinned: release HOLD')
    obj = json.loads(original)
    steps = list(obj.get('steps', []))
    if [x.get('step') for x in steps] != ['installTheme','mkdir','writeFile','runPHP','runPHP']:
        raise ValueError('Unexpected WordPress operations; never overwrite a site')
    theme = steps[0].get('themeData', {})
    if (theme.get('resource'),theme.get('path'),theme.get('ref')) != ('git:directory','assembler',ASSEMBLER_SHA):
        raise ValueError('Wrong Assembler source')
    if steps[2].get('path') != '/wordpress/wp-content/mu-plugins/fv-ex2-playground-review.php':
        raise ValueError('Original MU plugin not isolated')
    source = steps[2].get('data','')
    if source.count('class="fv-margin-strip__item"') != 72 or source.count('href="https://finalvestige.com/focus/"') != 5:
        raise ValueError('Required narrative records or Focus paths absent')
    if MARKER not in steps[3].get('code','') or 'FV_EX2_WORDPRESS_IMPORT_ADMISSION_PASS' not in steps[4].get('code',''):
        raise ValueError('Original admission gate absent')
    if PLUGIN_PATH in original.decode() or b'wp_remote_post' in plugin or b'sendBeacon' in plugin:
        raise ValueError('Unsafe or duplicated review receipt')
    obj['steps'].insert(3, {'step':'writeFile','path':PLUGIN_PATH,'data':plugin.decode('utf-8')})
    # No change to original 5 steps; only add isolated MU file.
    assert all(obj['steps'][i+(i>=3)] == steps[i] for i in range(5))
    return (json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()


def write_bundle(source_path, plugin_path, output):
    original = Path(source_path).read_bytes(); plugin = Path(plugin_path).read_bytes()
    raw = derive(original,plugin)
    manifest = {
      'source_blueprint_blob':SOURCE_BLOB,'reviewer_plugin_sha256':PLUGIN_SHA256,
      'derived_blueprint_blob':git_blob(raw),'derived_blueprint_sha256':hashlib.sha256(raw).hexdigest(),
      'theme_commit':ASSEMBLER_SHA,'native_wordpress_tested':False,'image_transfer_bytes_verified':False,
      'release_authorized':False,'origin':'isolated WordPress Playground only',
      'excluded_private_data':['user tables','subscribers','production database','secrets'],
      'instrumentation':'none; one click local JSON receipt; first-screen Focus pointer obstruction probe; no telemetry or sales claims'}
    url='https://playground.wordpress.net/#'+base64.b64encode(raw).decode('ascii')
    launch = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>FV EX2 WordPress review + browser receipt</title><style>body{{background:#0b1212;color:#e9dcca;margin:0;padding:1rem;min-height:100vh;display:grid;place-items:center;font:17px/1.6 system-ui}}main{{max-width:700px;border:1px solid #c2a371;padding:clamp(1rem,4vw,3rem)}}h1{{font:normal 2.4rem Georgia,serif}}a{{display:inline-block;max-width:100%;min-height:44px;padding:.9rem 1rem;background:#d4ad73;color:#111;font-weight:bold;overflow-wrap:anywhere}}a:focus-visible{{outline:3px solid white;outline-offset:3px}}</style><main><h1>Experience the evidence. Verify the experience.</h1><p>This <strong>private review-only</strong> package imports the exact-source seven-chapter candidate into an isolated WordPress Playground and adds an on-page evidence receipt at the bottom. It cannot certify WordPress.com hosting, actual image transfer bytes, WCAG 2.2 AA, Lighthouse, Jetpack signups or paid orders.</p><p><a href="{html.escape(url,quote=True)}" target="_blank" rel="noopener noreferrer">Open isolated WordPress review ↗</a></p><p>After WordPress starts, scroll to the bottom and select <strong>Capture this viewport</strong>, then <strong>Download JSON receipt</strong>. Repeat at mobile and desktop widths. If the page fails to load or the receipt is absent, report FAIL—not PASS.</p><small>Not for public hosting · no production changes · no paid services · no account or subscriber data.</small></main></html>'''
    output = Path(output)
    with ZipFile(output,'w') as z:
        for name, content in [('blueprint_with_local_receipt.json',raw),('launch_review.html',launch.encode()),('source_manifest.json',(json.dumps(manifest,indent=2)+'\n').encode())]:
            info=ZipInfo(name,(2026,11,7,7,0,0));info.compress_type=ZIP_DEFLATED
            z.writestr(info,content)
    return manifest


if __name__ == '__main__':
    cli=argparse.ArgumentParser();cli.add_argument('canonical_blueprint');cli.add_argument('review_plugin');cli.add_argument('output_zip');a=cli.parse_args()
    print(json.dumps(write_bundle(a.canonical_blueprint,a.review_plugin,a.output_zip),indent=2))
