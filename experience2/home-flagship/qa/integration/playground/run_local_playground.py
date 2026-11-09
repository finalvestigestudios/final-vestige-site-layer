#!/usr/bin/env python3
"""Launch the existing sealed EX2 package inside LOCAL WordPress Playground.

Does not build source, install plugins in WordPress.com, access production, or send
requests to finalvestige.com. Explicitly mount the generated PRIVATE plugin before
Blueprint activatePlugin; a Blueprint by itself never installs local files.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shlex
import subprocess
import sys

PLUGIN_DIR = 'fv-ex2-sealed-staging-preview'
PLUGIN_FILE = 'fv-ex2-sealed-preview.php'
VFS_DIR = '/wordpress/wp-content/plugins/' + PLUGIN_DIR

class AdmissionError(ValueError):
    pass

def prepare(out: Path, expected_head: str, executable=None):
    out = out.resolve(strict=True)
    if not (len(expected_head) == 40 and all(c in '0123456789abcdef' for c in expected_head)):
        raise AdmissionError('Expected exact 40-character source HEAD')
    receipt_path = out / 'receipt.json'
    blueprint_path = out / 'blueprint.json'
    plugin_path = out / 'plugin' / PLUGIN_DIR / PLUGIN_FILE
    plugin_dir = plugin_path.parent
    zip_path = out / 'sealed-review.zip'
    for f in (receipt_path, blueprint_path, plugin_path, zip_path):
        if not f.is_file() or f.is_symlink():
            raise AdmissionError('Missing or symlinked staging package: ' + str(f))
    for d in (plugin_dir, plugin_dir.parent):
        if d.is_symlink():
            raise AdmissionError('Symlinked plugin directory')
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    blueprint = json.loads(blueprint_path.read_text(encoding='utf-8'))
    if receipt.get('source_head') != expected_head or receipt.get('decision') != 'OFFLINE_PACKAGE_BUILT__NOT_WORDPRESS_ACCEPTED':
        raise AdmissionError('Untrusted or mismatched exact source receipt')
    for f, key in ((zip_path, 'sealed_zip_sha256'), (plugin_path, 'php_sha256'), (blueprint_path, 'blueprint_sha256')):
        if hashlib.sha256(f.read_bytes()).hexdigest() != receipt.get(key):
            raise AdmissionError('Package integrity failure: ' + key)
    if receipt.get('production_writes') is not False or receipt.get('hosted_equivalence') is not False:
        raise AdmissionError('Receipt must be explicitly nonproduction')
    if blueprint.get('login') is not True or blueprint.get('landingPage') != '/wp-admin/':
        raise AdmissionError('Missing private reviewer login')
    steps = blueprint.get('steps', [])
    if [s.get('step') for s in steps] != ['defineWpConfigConsts','activatePlugin','runPHP']:
        raise AdmissionError('Unexpected Blueprint execution plan')
    consts = steps[0].get('consts', {})
    if consts.get('WP_ENVIRONMENT_TYPE') != 'local' or consts.get('FV_EX2_ALLOW_PREVIEW') is not True or consts.get('DISALLOW_FILE_EDIT') is not True:
        raise AdmissionError('Playground must be local and explicitly preview-gated')
    if steps[1].get('pluginPath') != PLUGIN_DIR + '/' + PLUGIN_FILE:
        raise AdmissionError('Blueprint must activate the exact mounted plugin file')
    if "'post_status'=>'private'" not in steps[2].get('code',''):
        raise AdmissionError('Blueprint must create a private page')
    if executable is None:
        executable = ['npx','--no-install','@wp-playground/cli']
    cmd = list(executable) + ['server', '--port=9400', '--site-url=http://127.0.0.1:9400',
        '--blueprint='+str(blueprint_path), '--mount='+str(plugin_dir)+':'+VFS_DIR]
    return cmd

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',required=True,type=Path,help='Out directory from make_local_playground.py')
    p.add_argument('--expected-head',required=True)
    p.add_argument('--dry-run',action='store_true',help='Validate exact local package and print command; never launch')
    p.add_argument('--cli',nargs='+',help='Optional preinstalled Playground CLI executable + arguments')
    args=p.parse_args()
    try:
        cmd=prepare(args.out,args.expected_head,args.cli)
    except (AdmissionError,OSError,KeyError,ValueError) as exc:
        print('ADMISSION FAIL:',exc,file=sys.stderr)
        return 2
    print('LOCAL ONLY: no production access, Jetpack, subscriber or hosted equivalence.')
    print('Blueprint activates plugin after explicit --mount; mount is mandatory.')
    print(' '.join(shlex.quote(x) for x in cmd))
    if args.dry_run:
        return 0
    try:
        return subprocess.call(cmd, cwd=str(args.out.resolve()))
    except FileNotFoundError:
        print('Playground CLI missing. Install the free package locally before launch.',file=sys.stderr)
        return 3

if __name__=='__main__':
    sys.exit(main())
