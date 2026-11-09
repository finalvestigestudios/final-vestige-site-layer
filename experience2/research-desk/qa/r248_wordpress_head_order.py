#!/usr/bin/env python3
"""R248: exact original NASA Research Desk source, simulated WP head lifecycle.
Run in a full checkout: python experience2/research-desk/qa/r248_wordpress_head_order.py
This is NOT an installed WordPress, browser, axe, or licensing certification.
"""
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from bs4 import BeautifulSoup
from r243_core import SHIM

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    'templates/ledger.html': '403d128c57b9bc82dac7c619651689070edef86c',
    'assets/source-ledger.css': 'db531213e6f8dbaa44fba2885eefdd016dab93e3',
    'assets/source-ledger.js': '32e757cc4dc8708397ff65ac21e89dd319781d78',
}

def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

def php_call(root, phase):
    p = subprocess.run(['php', str(root/'shim.php'), phase],
                       capture_output=True, text=True, check=True)
    return json.loads(p.stdout)

def check_records(result, phase, expected_inline):
    first, second = result['first'], result['second']
    assert first.count('fv-ex2-research-desk-late-style') == expected_inline, phase
    assert 'fv-ex2-research-desk-late-style' not in second, phase
    soup = BeautifulSoup(first + second, 'html.parser')
    assert len(soup.select('[data-fvx-record]')) == 12, phase
    ids = [e['id'] for e in soup.select('[id]')]
    assert len(ids) == len(set(ids)), ('duplicate IDs', phase)
    for attr in ('for', 'aria-labelledby', 'aria-controls'):
        for e in soup.select('['+attr+']'):
            assert all(ref in ids for ref in e[attr].split()), (attr, phase)
    assert result['queued'].count('fv-ex2-research-desk') >= 2, phase

def main():
    original_php = (ROOT/'final-vestige-ex2-research-desk.php').read_text()
    assert "did_action('wp_head')" in original_php, 'lifecycle fix absent'
    for path, expected in PINS.items():
        assert expected in original_php
        assert git_blob((ROOT/path).read_bytes()) == expected, ('drift', path)
    with tempfile.TemporaryDirectory(prefix='apollo-r248-exact-') as d:
        root = Path(d)
        for path in ['final-vestige-ex2-research-desk.php', *PINS]:
            dst = root/path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT/path, dst)
        shim = SHIM.replace(
            "function wp_style_is($h,$s){return $_SERVER['argv'][1]==='early';}",
            "function wp_style_is($h,$s){return $_SERVER['argv'][1]==='printed';}\n"
            "function did_action($name){return $_SERVER['argv'][1]==='beforehead'?0:1;}"
        ).replace(
            "if($_SERVER['argv'][1]==='early')fv_ex2_rd_assets();",
            "if($_SERVER['argv'][1]==='beforehead')fv_ex2_rd_assets();"
        )
        assert 'function did_action($name)' in shim
        (root/'shim.php').write_text(shim)
        for phase, inline in [('beforehead',0), ('afterhead',1), ('printed',0)]:
            check_records(php_call(root, phase), phase, inline)
        for path in PINS:
            target = root/path
            data = target.read_bytes()
            target.write_bytes(data + b'\nUNREVIEWED_MUTATION')
            result = php_call(root, 'afterhead')
            if path.endswith('ledger.html'):
                assert 'data-fvx-record' not in result['first']
                assert 'Read the original Apollo 1 investigation' in result['first']
            elif path.endswith('.css'):
                assert 'fv-ex2-research-desk-late-style' not in result['first']
                assert result['queued'].count('fv-ex2-research-desk') >= 2
            else:
                assert 'data-fvx-record' in result['first']
                assert 'fv-ex2-research-desk-late-style' in result['first']
            target.write_bytes(data)
        print(json.dumps({
            'status':'PASS','scope':'EXACT_ORIGINAL_NASA_ASSETS',
            'php_lifecycle':['pre-head-no-inline','post-head-once','printed-no-inline'],
            'unsafe_mutations_rejected':list(PINS),'php_source_pins':PINS,
            'installed_wordpress':False,'browser':False,'axe_core':False
        },sort_keys=True))

if __name__=='__main__':
    main()
