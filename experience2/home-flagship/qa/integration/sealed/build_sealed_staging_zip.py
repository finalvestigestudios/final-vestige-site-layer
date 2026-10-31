#!/usr/bin/env python3
"""Build a byte-reproducible editor-only WordPress prototype, with NO directly served HTML/CSS/JS.

Inputs are the exact source-controlled EX2 flagship files. The generated plugin embeds
all source bytes as compressed PHP constants; it exposes one editor-only nonce-checked
Ajax renderer, not any public static source path. This NEVER installs/activates a plugin.
"""
import argparse, base64, hashlib, json, re, zlib, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSS = ("flagship.css", "chronicle.css", "chronicle-lens.css", "inquiry.css", "observer-lab.css", "reading-trail.css")
JS = ("flagship.js", "observer-lab.js", "chronicle-lens.js", "reading-trail.js")
FILES = ("index.html", *CSS, *JS)
MARKER = '/* FV_EX2_SEALED_ASSET_DEFINITIONS */'
ZIPROOT = 'fv-ex2-sealed-staging-preview'


def build(root: Path, dest: Path, head: str) -> dict:
    if not re.fullmatch('[a-f0-9]{40}', head):
        raise ValueError('Need exact 40-hex Git commit SHA, not a branch name or an invented receipt')
    raw = {}
    for name in FILES:
        p = root/name
        if not p.is_file(): raise ValueError(f'missing source file: {name}')
        raw[name] = p.read_bytes()
        if len(raw[name]) > 1_000_000: raise ValueError(f'asset unexpectedly large: {name}')
    document = raw['index.html'].decode('utf-8')
    for n in CSS:
        if document.count(f'<link rel="stylesheet" href="./{n}">') != 1:
            raise ValueError(f'exact stylesheet link missing/duplicated: {n}')
    for n in JS:
        if document.count(f'<script src="./{n}" defer></script>') != 1:
            raise ValueError(f'exact script tag missing/duplicated: {n}')
    if not all(token in document for token in (
        'DO NOT DEPLOY AS THE WORDPRESS HOME PAGE','data-fv-home-flagship',
        'fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry',
        'fv-hf-observer','fv-hf-mind-title','/focus/','/free-resources/puysegurs-animal-magnetism-files/'
    )): raise ValueError('homepage source preservation contract not met')
    sha = {name: hashlib.sha256(data).hexdigest() for name,data in raw.items()}
    encoded = {name: base64.b64encode(zlib.compress(data, 9)).decode('ascii') for name,data in raw.items()}
    tpl = (HERE/'fv-ex2-sealed-preview.php').read_text(encoding='utf-8')
    if tpl.count(MARKER) != 1:raise ValueError('sealed template marker missing/duplicated')
    php = tpl.replace(MARKER,
        "define('FV_EX2_PACKED_ASSETS', json_decode('"+json.dumps(encoded,separators=(',',':'))+"', true));\n"
        +"define('FV_EX2_ASSET_SHA256', json_decode('"+json.dumps(sha,separators=(',',':'))+"', true));")
    if 'wp_ajax_nopriv_' in php or 'wp_insert_post(' in php or 'wp_update_post(' in php:
        raise ValueError('found unexpected production side effect / public handler')
    manifest = {
        'status':'PRIVATE_STAGING_ONLY_NO_PRODUCTION_INSTALL',
        'expected_commit':head,
        'expected_commit_note':'Caller-supplied identifier, not verified by this local builder',
        'asset_sha256':sha,
        'plugin_sha256':hashlib.sha256(php.encode('utf-8')).hexdigest(),
        'browser_visible_asset_paths':[],
        'shortcode':'[fv_ex2_sealed_homepage_preview]',
        'staging_flags':['WP_ENVIRONMENT_TYPE=staging','FV_EX2_ALLOW_PREVIEW=true','user is logged in with edit_pages'],
        'release_holds':['No production CMS writes','No QD or CI PASS','No media-rights clearance','No WordPress Assembler integration certification']
    }
    hold = 'DO NOT INSTALL ON PUBLIC PRODUCTION.\nPrivate staging only; requires explicit approval, WP_ENVIRONMENT_TYPE=staging, FV_EX2_ALLOW_PREVIEW=true and authenticated editor. No WordPress writes performed by build.\n'
    members = {
        ZIPROOT+'/fv-ex2-sealed-preview.php':php.encode('utf-8'),
        ZIPROOT+'/STAGING_MANIFEST.json':(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode('utf-8'),
        ZIPROOT+'/INSTALLATION_HOLD.txt':hold.encode('utf-8'),
    }
    dest.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(dest, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for filename,data in sorted(members.items()):
            info=zipfile.ZipInfo(filename,date_time=(2020,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=(0o100644<<16)
            z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--expected-head',required=True)
    args=p.parse_args()
    m=build(args.root,args.out,args.expected_head)
    print(json.dumps({'path':str(args.out),'bytes':args.out.stat().st_size,'members':3,'source_sha256':m['asset_sha256']},indent=2))
