#!/usr/bin/env python3
"""Check actual PHP fallback after missing or changed frozen source (temp copies only)."""
from pathlib import Path
import subprocess
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
plugin=(ROOT/'apollo-r277/apollo-review-shortcode.php').read_bytes()
source=(ROOT/'apollo-r273/review-custody.php').read_bytes()
php='''<?php
error_reporting(E_ALL);
define('ABSPATH','/mock/');
function add_action($a,$b,$c=10){}
function add_shortcode($a,$b){}
function plugins_url($a,$b){return '/assets/review-custody.css';}
function wp_style_is($a,$b){return false;}
require __DIR__.'/apollo-r277/apollo-review-shortcode.php';
echo fv_r277_render_shortcode(['state'=>'approved','merchant_url'=>'https://evil.invalid/']);
'''
for name,body in [('missing',None),('modified',source+b'\\n/* SHA drift / unreviewed */\\n'),('authentic',source)]:
    with tempfile.TemporaryDirectory(prefix='fv-r278-') as tmp:
        root=Path(tmp)
        (root/'apollo-r277').mkdir(); (root/'apollo-r273').mkdir()
        (root/'apollo-r277/apollo-review-shortcode.php').write_bytes(plugin)
        if body is not None: (root/'apollo-r273/review-custody.php').write_bytes(body)
        (root/'test.php').write_text(php)
        r=subprocess.run(['php',str(root/'test.php')],capture_output=True,text=True)
        assert r.returncode==0,(name,r.stderr)
        content=r.stdout
        assert 'evil.invalid' not in content
        if name=='authentic':
            assert 'data-fv-review-ready="false"' in content
            assert 'Editorial review remains open' in content
            assert 'The review panel is unavailable' not in content
        else:
            assert 'The review panel is unavailable' in content
            assert 'NASA Apollo 204 Review Board report' in content
            assert 'Free Apollo 1 investigation' in content
            assert '<script' not in content
            assert 'data-fv-review-ready="true"' not in content
        print('PASS',name,'actual PHP fail-open custody / no commercial activation')
print('R278 3/3 authentic/missing/tampered-source paths PASS; temporary files deleted.')
