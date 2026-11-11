#!/usr/bin/env python3
"""R292 source-controlled offline PHP/Chromium route and non-text contrast gate.
This does not certify axe-core, installed WordPress, HTTP/CSP or field CWV.
"""
import subprocess, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]/'apollo-r281'
php="""define('ABSPATH','/qa/');function add_action($x,$y,$z=10){}
function add_shortcode($x,$y){}function wp_style_is($x,$y){return true;}
function plugins_url($x,$y){return '/fake.css';}
require 'apollo-source-experience.php';echo fv_r281_render();echo fv_r281_render();"""
r=subprocess.run(['php','-r',php],cwd=ROOT,text=True,capture_output=True,check=True)
css=(ROOT/'assets/apollo-source-experience.css').read_text()
assert r.stdout.count('class="fv-r292__source-route"')==2
assert r.stdout.count('Read the free Apollo 1 investigation')==2
html='<html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+r.stdout+'</body></html>'
def lum(x):
    values=[int(v)/255 for v in re.findall(r'\d+',x)[:3]]
    linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values]
    return sum(v*w for v,w in zip(linear,[.2126,.7152,.0722]))
def contrast(a,b):
    x,y=sorted([lum(a),lum(b)]);return (y+.05)/(x+.05)
checks=0
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width in (320,390,768,1440,1920):
        for js in (False,True):
            ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,reduced_motion='reduce',has_touch=width<=390)
            pg=ctx.new_page();req=[];pg.on('request',lambda q:req.append(q.url));pg.set_content(html)
            routes=pg.locator('.fv-r292__source-route a');assert routes.count()==2
            for i in range(2):
                target=f'fv-r281-{i+1}-source-1'
                assert routes.nth(i).get_attribute('href')=='#'+target
                routes.nth(i).focus();routes.nth(i).press('Enter')
                assert pg.evaluate('document.activeElement.id')==target
                back=pg.locator('#'+target+' .fv-r281__source-return a');back.focus();back.press('Enter')
                assert pg.evaluate('document.activeElement.id')==f'fv-r281-{i+1}-event-1'
            for selector in ('.fv-r281__plate','.fv-r281__gallery','.fv-r281__source-list li','.fv-r281__authority-ledger li'):
                colors=pg.locator(selector).first.evaluate('e=>[getComputedStyle(e).borderTopColor,getComputedStyle(e).backgroundColor]')
                assert contrast(*colors)>=3,(selector,colors)
            assert pg.evaluate('document.documentElement.scrollWidth<=innerWidth+1') and not req
            assert pg.locator('.fv-r281__next a').count()==2
            checks+=1;ctx.close()
    browser.close()
assert contrast('rgb(102,91,73)','rgb(32,37,42)')<3 # R291 negative control
print(f'R292 source-controlled actual-PHP Chromium {checks}/10 PASS; prior border rejected; release HARD HOLD')
