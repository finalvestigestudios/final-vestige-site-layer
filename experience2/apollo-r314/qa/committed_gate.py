#!/usr/bin/env python3
"""R314 reproducible input parity: real offline Chromium, NOT HTTP, axe, or WP."""
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import subprocess
ROOT = Path(__file__).resolve().parents[2]
PHP = ROOT / 'apollo-r281/apollo-source-experience.php'
JS = ROOT / 'apollo-r281/assets/apollo-cache-continuation.js'
CSS = ROOT / 'apollo-r281/assets/apollo-source-experience.css'
FIX = ROOT / 'apollo-r301/qa/local_http_fixture.php'
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
VALID = 'utm_source=youtube&utm_medium=organic_social&utm_campaign=apollo1_pilot_2026_11&utm_content=apollo1_yt_alpha001'
INVALID = VALID.replace('alpha001','person%40example.com')
subprocess.run(['php','-l',str(PHP)],check=True,stdout=subprocess.PIPE)
subprocess.run(['node','--check',str(JS)],check=True)
def render(query):
    return subprocess.check_output(['php','-r','parse_str($argv[2],$_GET);include $argv[1];',str(FIX),'instances=2&queue=0&'+query],text=True)
html = render(VALID)
assert render(INVALID)==html
assert len(BeautifulSoup(html,'lxml').select('section.fv-r281'))==2
js,css = JS.read_text(),CSS.read_text()
assert "document.addEventListener('auxclick', handleActivation, true)" in js
cases = 0
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width in [320,390,768,1440,1920]:
        for enabled in [False,True]:
            ctx = browser.new_context(viewport={'width':width,'height':900},java_script_enabled=enabled,reduced_motion='reduce')
            page = ctx.new_page()
            page.goto('about:blank?'+VALID)
            page.set_content(html.replace('</head>','<style>'+css+'</style></head>'))
            if enabled:
                page.add_script_tag(content=js)
                page.evaluate("""() => document.addEventListener('auxclick',e=>{if(e.target.closest('a[data-fv-cta]'))e.preventDefault()})""")
            link = page.locator('section.fv-r281 a[data-fv-cta]').first
            assert link.get_attribute('href')==FREE
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            if enabled:
                link.scroll_into_view_if_needed()
                box=link.bounding_box()
                page.mouse.click(box['x']+box['width']/2,box['y']+box['height']/2,button='middle')
                assert dict(parse_qsl(urlsplit(link.get_attribute('href')).query))==dict(parse_qsl(VALID))
            else:
                assert link.get_attribute('href')==FREE
            assert page.locator('section.fv-r281 a[data-fv-cta]').nth(1).get_attribute('href')==FREE
            cases += 1
            ctx.close()
    ctx=browser.new_context();page=ctx.new_page();page.goto('about:blank?'+INVALID)
    page.set_content(html);page.add_script_tag(content=js)
    page.evaluate("""() => document.addEventListener('auxclick',e=>{if(e.target.closest('a[data-fv-cta]'))e.preventDefault()})""")
    link=page.locator('section.fv-r281 a[data-fv-cta]').first
    link.scroll_into_view_if_needed();box=link.bounding_box()
    page.mouse.click(box['x']+box['width']/2,box['y']+box['height']/2,button='middle')
    assert link.get_attribute('href')==FREE
    cases+=1;ctx.close();browser.close()
print('PASS R314: '+str(cases)+' offline Chromium contexts; trusted middle activation, invalid rejection, cache-stable PHP and no-JS; axe/HTTP/WP not verified.')
