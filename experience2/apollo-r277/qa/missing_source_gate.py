#!/usr/bin/env python3
"""Prove missing sibling PHP fails open to meaningful primary-source HTML, not approval."""
import shutil
import subprocess
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
code='''<?php
define('ABSPATH','/fixture/');
function add_action($hook,$callback,$priority=10) {}
function add_shortcode($name,$callback) {}
function wp_style_is($handle,$state) { return false; }
function plugins_url($name,$file) { return 'https://example.test/local.css'; }
require __DIR__.'/apollo-review-shortcode.php';
echo '<!doctype html><html lang="en"><meta charset="utf-8"><body>';
echo fv_r277_render_shortcode(['state'=>'approved','merchant_url'=>'https://evil.invalid/checkout']);
echo '</body></html>';
'''
with tempfile.TemporaryDirectory(prefix='apollo-r277-fallback-') as d:
    temp=Path(d)
    shutil.copyfile(root/'apollo-review-shortcode.php',temp/'apollo-review-shortcode.php')
    (temp/'render.php').write_text(code)
    html=subprocess.check_output(['php',str(temp/'render.php')],text=True)
    assert 'The review panel is unavailable' in html
    assert 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/' in html
    assert 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/' in html
    assert 'evil.invalid' not in html and 'approved' not in html and '<script' not in html
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=b.new_page(viewport={'width':320,'height':800},java_script_enabled=False)
        req=[];page.on('request',lambda r:req.append(r.url))
        page.set_content(html)
        assert page.get_by_role('complementary',name='Apollo 1 research custody').count()==1
        assert page.get_by_role('link',name='NASA Apollo 204 Review Board report').count()==1
        assert page.get_by_role('link',name='Free Apollo 1 investigation').count()==1
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
        assert not req
        b.close()
print('R277 missing-source no-JS fail-open: PHP + real Chromium PASS')
