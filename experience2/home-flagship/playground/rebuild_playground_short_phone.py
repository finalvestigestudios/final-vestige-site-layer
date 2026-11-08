#!/usr/bin/env python3
"""Rebuild the *private* EX2 WordPress Playground ZIP with the PR #1601 mobile CSS.

Nothing is installed or published. Input ZIP + CSS are protected/custodied separately;
this source-only builder contains neither subscriber data nor private WordPress content.
"""
import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path

PARENT_ZIP_SHA256 = '8db20aac81deba544d057abfe28fe3baaf71639f74f421a210676fbb0b36e56b'
PARENT_PLUGIN_SHA256 = '7fe27aecc6f5f2b8033ab826dcb5146b6e31ae4dbcaf2a7825859b48dc5b51ee'
DELTA_SHA256 = 'dfa8d6c922ab066f5fde3e81b5d4fbb70f05978d4cade0eb0befcfd7e528308a'
PLUGIN = 'mu-plugins/fv-ex2-playground-review.php'
CUSTODY = 'SOURCE_CUSTODY.json'
REVIEW = 'REVIEW.txt'
END = b'\nFVPG_CSS_END'
FILES = (REVIEW, CUSTODY, 'blueprint.json', PLUGIN,
         'mu-plugins/fv-ex2-private-browser-receipt.php')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def build(parent_zip, css_delta):
    if sha(parent_zip) != PARENT_ZIP_SHA256:
        raise ValueError('HOLD: private parent Playground ZIP does not match pinned bytes')
    if sha(css_delta) != DELTA_SHA256:
        raise ValueError('HOLD: CSS differs from reviewed PR #1601 delta')
    if not css_delta.startswith(b'/* FV EX2') or b'@media (max-width: 360px) and (max-height: 700px)' not in css_delta:
        raise ValueError('HOLD: incorrect narrow-phone CSS payload')
    with zipfile.ZipFile(io.BytesIO(parent_zip)) as old:
        if tuple(old.namelist()) != FILES or len(set(old.namelist())) != len(FILES):
            raise ValueError('HOLD: unrecognized ZIP layout or duplicate paths')
        original = {n: old.read(n) for n in FILES}
        infos = {n: old.getinfo(n) for n in FILES}
    if sha(original[PLUGIN]) != PARENT_PLUGIN_SHA256:
        raise ValueError('HOLD: parent PHP renderer drift')
    if original[PLUGIN].count(END) != 1 or original[PLUGIN].count(b"<<<'FVPG_CSS_END'") != 1:
        raise ValueError('HOLD: expected unique scoped inline CSS marker missing')
    if b'@media (max-width: 360px) and (max-height: 700px)' in original[PLUGIN]:
        raise ValueError('HOLD: CSS already applied; refuse double injection')
    if b"$fv_ex2_review_websandbox = $fv_ex2_review_host === 'wpsandbox.wordpress.net';" not in original[PLUGIN]:
        raise ValueError('HOLD: isolated Playground host protection missing')
    injected = original[PLUGIN].replace(END, b'\n'+css_delta.rstrip(b'\n')+b'\n'+END, 1)
    assert injected.replace(b'\n'+css_delta.rstrip(b'\n')+b'\n'+END, END, 1) == original[PLUGIN]
    custody = json.loads(original[CUSTODY])
    if custody['files_sha256'][PLUGIN] != PARENT_PLUGIN_SHA256:
        raise ValueError('HOLD: source custody and parent renderer disagree')
    custody['files_sha256'][PLUGIN] = sha(injected)
    custody['short_phone_stylesheet_review'] = {
        'state': 'UNPUBLISHED PRIVATE PLAYGROUND CANDIDATE',
        'parent_zip_sha256': PARENT_ZIP_SHA256,
        'parent_plugin_sha256': PARENT_PLUGIN_SHA256,
        'css_delta_sha256': DELTA_SHA256,
        'rebuilt_plugin_sha256': sha(injected),
        'source_pr': 1601,
        'page_6_modified': False,
        'wordpress_core_executed': False,
        'field_cwv_measured': False,
        'jetpack_verified': False,
    }
    changed = dict(original)
    changed[PLUGIN] = injected
    changed[CUSTODY] = (json.dumps(custody, sort_keys=True, indent=2, ensure_ascii=False)+'\n').encode('utf-8')
    changed[REVIEW] = original[REVIEW] + b'\nSHORT PHONE REVIEW: PR #1601 CSS delta applied only to private shortcode inline stylesheet. No WP install, production approval, Jetpack certification or image rights clearance.\n'
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w') as new:
        for n in FILES:
            new.writestr(infos[n], changed[n])
    rebuilt = output.getvalue()
    with zipfile.ZipFile(io.BytesIO(rebuilt)) as z:
        assert z.read('blueprint.json') == original['blueprint.json']
        assert z.read('mu-plugins/fv-ex2-private-browser-receipt.php') == original['mu-plugins/fv-ex2-private-browser-receipt.php']
        assert sha(z.read(PLUGIN)) == custody['files_sha256'][PLUGIN]
        assert len(z.namelist()) == 5
    receipt = {'status':'OFFLINE_REBUILT_NOT_WORDPRESS_STAGED',
               'parent_zip_sha256':PARENT_ZIP_SHA256,
               'rebuilt_zip_sha256':sha(rebuilt),
               'parent_plugin_sha256':PARENT_PLUGIN_SHA256,
               'rebuilt_plugin_sha256':sha(injected),
               'delta_sha256':DELTA_SHA256,
               'changed_members':[REVIEW,CUSTODY,PLUGIN],
               'unchanged_members':['blueprint.json','mu-plugins/fv-ex2-private-browser-receipt.php'],
               'release':'HOLD'}
    return rebuilt, receipt


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--parent', type=Path, required=True)
    p.add_argument('--delta', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--receipt', type=Path, required=True)
    a = p.parse_args()
    payload, report = build(a.parent.read_bytes(), a.delta.read_bytes())
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_bytes(payload)
    a.receipt.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__ == '__main__':
    main()
