#!/usr/bin/env python3
"""R353 source-controlled Chromium regression: PHP-rendered fixture, NOT WordPress/axe certification."""
import json, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[3]/'experience2'
render = 'define("ABSPATH",true);require '+json.dumps(str(root/'apollo-r348/source-custody.php'))+';echo fv_apollo_r348_experience_shortcode();'
html = subprocess.check_output(['php','-r',render], text=True)
script = (root/'apollo-r347/assets/source-index.js').read_text()
styles = '\n'.join((root/p).read_text() for p in (
    'apollo-r339/assets/chronology-rail.css','apollo-r340/assets/accession-gallery.css',
    'apollo-r345/evidence-plate.css','apollo-r347/assets/source-index.css',
    'apollo-r348/assets/source-custody.css'))
assert html.count('data-fv-apollo-entry=') == 13

def load(page):
    page.set_content('<html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+styles+'</style><body>'+html+'</body></html>')

with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for width,enabled in ((320,True),(390,False),(768,True),(1440,True),(1920,True)):
        context = browser.new_context(viewport={'width':width,'height':900},java_script_enabled=enabled)
        page = context.new_page(); load(page)
        if enabled: page.add_script_tag(content=script)
        if width==320: page.evaluate('document.documentElement.style.fontSize="64px"')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        assert page.locator('[data-fv-apollo-entry]:visible').count() == 13
        assert page.locator('summary').count() == 21
        if enabled:
            assert page.locator('[data-fv-apollo-filters] button').count() == 5
            page.locator('[data-fv-apollo-filters] button').last.click()
            assert page.locator('[data-fv-apollo-group]:visible').count() == 1
            assert page.locator('[data-fv-apollo-status]').inner_text() == 'Showing 4 of 13 evidence entries.'
            page.locator('[data-fv-apollo-filters] button').first.click()
            assert page.locator('[data-fv-apollo-entry]:visible').count() == 13
        else:
            assert page.locator('[data-fv-apollo-filters]:visible').count() == 0
        context.close()
    for mode in ('listener','bar','mid-filter'):
        context=browser.new_context(viewport={'width':390,'height':900})
        page=context.new_page();load(page)
        if mode=='listener':
            page.evaluate("""() => {let n=0;const old=Element.prototype.addEventListener;Element.prototype.addEventListener=function(t,...a){if(t==='click'&&this.tagName==='BUTTON'&&++n===3)throw Error('test');return old.call(this,t,...a)}}""")
        elif mode=='bar':
            page.evaluate("""() => {const old=Element.prototype.appendChild;Element.prototype.appendChild=function(n){if(this.hasAttribute('data-fv-apollo-filters'))throw Error('test');return old.call(this,n)}}""")
        else:
            page.evaluate("""() => {let n=0;const d=Object.getOwnPropertyDescriptor(HTMLElement.prototype,'hidden');Object.defineProperty(HTMLElement.prototype,'hidden',{configurable:true,get(){return d.get.call(this)},set(v){if(this.hasAttribute('data-fv-apollo-group')&&++n===2)throw Error('test');return d.set.call(this,v)}})}""")
        page.add_script_tag(content=script)
        if mode=='mid-filter': page.locator('[data-fv-apollo-filters] button').last.click()
        assert page.locator('[data-fv-apollo-entry]:visible').count()==13,mode
        assert page.locator('[data-fv-apollo-filters]:visible').count()==0,mode
        assert page.locator('[data-fv-apollo-source-index]').get_attribute('data-fv-apollo-index-ready') is None,mode
        context.close()
    browser.close()
print('PASS R353: 5 viewport/no-JS/400%-text contexts + 3 injected failures; axe-core/WordPress NOT tested')
