#!/usr/bin/env python3
"""Seal a verified FV 19-step local WordPress Playground Blueprint into an offline ZIP.

No downloader, WordPress API, CMS writes, subscriber/credential exports or
rights determination. The resulting bundle is PRIVATE; never publish it.
WordPress Playground supports bundled resources for installTheme/writeFile.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import zipfile

THEME_URL = 'https://public-api.wordpress.com/rest/v1/themes/download/assembler.zip'
MEDIA = {
    'apollo.webp': ('https://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp', 78346),
    'franklin.jpg': ('https://finalvestige.com/wp-content/uploads/2026/08/Franklinexpeditionnote.jpg', 466043),
    'nypl.jpg': ('https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg', 5553669),
}
PREFIX = '/wordpress/wp-content/plugins/fv-ex2-playground/media/'
ASSET_DIR = '/wordpress/wp-content/plugins/fv-ex2-playground/assets/'
STYLES_AND_SCRIPTS = ('wordpress-page-fragment.review-only.html', 'flagship.css', 'chronicle.css', 'chronicle-lens.css', 'inquiry.css', 'observer-lab.css', 'reading-trail.css', 'flagship.js', 'observer-lab.js', 'chronicle-lens.js', 'reading-trail.js')
PLUGIN_FILE = '/wordpress/wp-content/plugins/fv-ex2-playground/fv-ex2-playground.php'
HEX = set('0123456789abcdef')

class Hold(ValueError):
    pass

def require(ok, message):
    if not ok:
        raise Hold('OFFLINE PLAYGROUND HOLD: ' + message)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def digest(s):
    return isinstance(s, str) and len(s) == 64 and set(s) <= HEX

def read_private(path, label, max_bytes):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), label + ': regular non-symlink file required')
    if os.name == 'posix':
        require(not (path.stat().st_mode & 0o077), label + ': chmod 600 required')
    require(0 < path.stat().st_size <= max_bytes, label + ': unexpected size')
    return path.read_bytes()

def check_theme(data, approved_sha):
    require(digest(approved_sha) and sha(data) == approved_sha,
            'Assembler ZIP does not match separately reviewed SHA-256')
    import io
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            files = z.infolist()
            require(len(files) < 1000 and sum(f.file_size for f in files) < 100_000_000,
                    'theme archive capacity exceeded')
            names = {f.filename for f in files}
            require({'assembler/style.css', 'assembler/templates/index.html'} <= names,
                    'wrong theme structure')
            for f in files:
                parts = f.filename.split('/')
                require(not f.filename.startswith('/') and '..' not in parts and not (f.external_attr >> 16 & 0o170000) == stat.S_IFLNK,
                        'unsafe ZIP member')
            style = z.read('assembler/style.css', pwd=None)
            require(b'Theme Name:' in style and b'Assembler' in style[:8192],
                    'theme identity header absent')
    except (zipfile.BadZipFile, KeyError) as exc:
        raise Hold('OFFLINE PLAYGROUND HOLD: malformed Assembler theme') from exc

def seal(blueprint, theme, sources, manifest, theme_sha):
    require(type(blueprint) is dict and type(blueprint.get('steps')) is list and len(blueprint['steps']) == 19,
            'exact 19-step candidate required')
    steps = blueprint['steps']
    require(steps[0] == {'step':'defineWpConfigConsts','consts':{'WP_ENVIRONMENT_TYPE':'local','FV_EX2_ALLOW_LOCAL_REVIEW':True}},
            'must remain local WordPress only')
    require(steps[1].get('step') == 'installTheme' and
            steps[1].get('themeData') == {'resource':'url','url':THEME_URL} and
            steps[1].get('options',{}).get('activate') is True,
            'expected official Assembler theme URL absent')
    require(all(s.get('step') == 'writeFile' for s in steps[2:17]) and
            steps[17].get('step') == 'activatePlugin' and
            steps[17].get('pluginPath') == 'fv-ex2-playground/fv-ex2-playground.php' and
            steps[18].get('step') == 'runPHP', 'unsafe/unexpected staging steps')
    paths = [s.get('path') for s in steps[2:17]]
    require(len(paths) == len(set(paths)) and set(paths) == ({PLUGIN_FILE} | {ASSET_DIR + n for n in STYLES_AND_SCRIPTS} | {PREFIX + n for n in MEDIA}), 'missing, replaced or repeated source payload')
    require(all(isinstance(p,str) and p.startswith('/wordpress/wp-content/plugins/fv-ex2-playground/') and '..' not in p.split('/') for p in paths),
            'unapproved writeFile path')
    require(set(p.rsplit('/',1)[-1] for p in paths if p.startswith(PREFIX)) == set(MEDIA),
            'not the reviewed three image originals')
    require(sum(p.startswith(PREFIX) for p in paths) == 3 and
            all(type(s.get('data')) is str and len(s['data']) > 30 for s in steps[2:17] if not s['path'].startswith(PREFIX)),
            'source payload missing')
    plugin = next(s['data'] for s in steps if s.get('path') == PLUGIN_FILE)
    require(all(t in plugin for t in ('fv_ex2_ready()', 'fv_ex2_integrity()', 'render_block')), 'missing isolated plugin safety gates')
    code = steps[18].get('code','')
    require(all(token in code for token in ('wp_insert_post(', 'wp_slash($raw)',
            "get_post_field('post_content',$id,'raw')", "get_stylesheet() !== 'assembler'",
            "wp_get_environment_type() !== 'local'", 'fv_ex2_ready()',
            "substr_count($raw,'--i:') !== 72")),
            'post-save integrity or local-only guard absent')
    require('https://' not in code and 'finalvestige.com' not in code, 'PHP may not reference production host')
    require(manifest.get('purpose') == 'isolated-staging-media-review' and
            type(manifest.get('images')) is dict and set(manifest['images']) == set(MEDIA),
            'separately reviewed media manifest required')
    check_theme(theme, theme_sha)
    for step in steps[2:17]:
        if not step['path'].startswith(PREFIX):
            continue
        name = step['path'].rsplit('/',1)[-1]
        url, size = MEDIA[name]
        expected = {'resource':'url','url':url}
        require(step['data'] == expected, 'image source substitution for ' + name)
        att = manifest['images'][name]
        require(att.get('source_url') == url and type(att.get('bytes')) is int and att['bytes'] == size and
                digest(att.get('sha256')) and len(sources[name]) == size and sha(sources[name]) == att['sha256'],
                'byte identity mismatch for ' + name)
        magic = sources[name][:16]
        require((name.endswith('.webp') and magic[:4] == b'RIFF' and magic[8:12] == b'WEBP') or
                (name.endswith('.jpg') and magic[:3] == b'\xff\xd8\xff'),
                'image format signature mismatch for ' + name)
        step['data'] = {'resource':'bundled','path':'/assets/' + name}
    steps[1]['themeData'] = {'resource':'bundled','path':'/assets/assembler.zip'}
    require(not any(isinstance(s.get('data'),dict) and s['data'].get('resource') == 'url' for s in steps),
            'remote media still present')
    return {'blueprint.json': (json.dumps(blueprint, indent=2, ensure_ascii=False) + '\n').encode(),
            'assets/assembler.zip': theme, **{'assets/'+n: sources[n] for n in sorted(MEDIA)}}

def package(blueprint_path, theme_path, media_dir, manifest_path, theme_sha, blueprint_sha, output):
    out = Path(output)
    require(out.parent.is_dir() and not out.parent.is_symlink(), 'preexisting private output directory required')
    if os.name == 'posix':
        require(not out.parent.stat().st_mode & 0o077, 'output directory must be chmod 700')
    require(not out.exists() and not out.is_symlink(), 'never overwrite an existing bundle')
    raw = read_private(blueprint_path, 'integrated Blueprint', 1_000_000)
    require(digest(blueprint_sha) and sha(raw) == blueprint_sha, 'independently reviewed original 19-step Blueprint SHA-256 mismatch')
    original = json.loads(raw)
    manifest = json.loads(read_private(manifest_path, 'reviewed media manifest', 100_000))
    media = {n: read_private(Path(media_dir)/n,n,10_000_000) for n in MEDIA}
    theme = read_private(theme_path, 'Assembler theme', 50_000_000)
    contents = seal(original,theme,media,manifest,theme_sha)
    entries = sorted(contents)
    try:
        fd = os.open(out,os.O_WRONLY | os.O_CREAT | os.O_EXCL | (getattr(os,'O_NOFOLLOW',0)),0o600)
        with os.fdopen(fd,'wb') as dest:
            with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
                for name in entries:
                    info = zipfile.ZipInfo(name, (2026, 10, 30, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o600 << 16
                    z.writestr(info,contents[name])
    except BaseException:
        out.unlink(missing_ok=True)
        raise
    return {'status':'OFFLINE_BUNDLE_SEALED_NOT_WORDPRESS_EXECUTED_RELEASE_HOLD',
            'bundle_sha256':sha(out.read_bytes()),'blueprint_original_sha256':sha(raw),
            'bundled_resources':entries,'size_bytes':out.stat().st_size,
            'wordpress_runtime_executed':False,'rights_verified':False,
            'wpcom_hosted_parity_verified':False}

def main():
    p=argparse.ArgumentParser(description='Create a PRIVATE fully bundled 19-step WordPress Playground stage; no CMS writes.')
    for key in ('blueprint','theme','media-dir','media-manifest','theme-sha256','blueprint-sha256','output'):
        p.add_argument('--'+key, required=True)
    a=p.parse_args()
    try:
        result=package(a.blueprint,a.theme,a.media_dir,a.media_manifest,a.theme_sha256,a.blueprint_sha256,a.output)
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as e:
        p.exit(2,str(e)+'\n')
    print(json.dumps(result,indent=2))

if __name__ == '__main__':
    main()
