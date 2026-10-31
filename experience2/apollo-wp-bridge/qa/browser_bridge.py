#!/usr/bin/env python3
"""Real Chromium smoke of PHP-generated WP-content mock over loopback HTTP.
No actual WordPress, NASA assets or network required. No axe-core installed.
"""
from __future__ import annotations
import hashlib
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
import subprocess
import threading
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

BASE=Path(__file__).resolve().parents[2]
BRIDGE=BASE/'bridge'
QA=BASE/'qa'
SHOTS=QA/'screenshots'
SHOTS.mkdir(parents=True,exist_ok=True)

class NoExternal(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(BASE),**kwargs)
    def end_headers(self):
        # A stringent same-origin-only CSP tests that the bridge needs no
        # inline script/CSS, external assets or remote network dependencies.
        self.send_header('Content-Security-Policy',"default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'none'; font-src 'none'; object-src 'none'; base-uri 'none'")
        self.send_header('X-Content-Type-Options','nosniff')
        super().end_headers()
    def log_message(self,fmt,*args):pass

def preview():
    rendered=subprocess.run(['php',str(BRIDGE/'qa/php_shortcode_harness.php'),'html'],capture_output=True,check=True,text=True).stdout
    rendered=rendered.replace('https://staging.invalid/wp-content/plugins/fv-ex2-apollo-casefile/','./bridge/')
    # Simulates an existing site main + real theme content + a shortcode, not a live WP server.
    html='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>WordPress Staging Mock: Apollo Experience 2.0</title><link rel="stylesheet" href="./qa/theme-mock.css"></head><body>
    <header class="wp-theme-header"><a href="/">Final Vestige / Wordpress theme mock</a></header><main id="site-main"><p class="wp-theme-identity">Theme heading is separate from Apollo component.</p>'''+rendered+'''</main><footer class="wp-theme-footer">WordPress footer unaffected by casefile</footer></body></html>'''
    (BASE/'preview.html').write_text(html,encoding='utf-8')
    (QA/'theme-mock.css').write_text('body{background:rgb(235,230,218);color:rgb(20,28,30);margin:0;font:16px system-ui}.wp-theme-header,.wp-theme-footer{padding:16px;background:rgb(235,230,218);color:rgb(20,28,30)}.wp-theme-identity{margin:18px}.fv-ex2-apollo{min-width:0}\n',encoding='utf-8')
    return html


def inline_for_browser(html):
    # Browser policy in this sandbox blocks all navigation, even localhost and file://.
    # Test the *actual PHP-rendered HTML/CSS/JS* via set_content as an in-memory fixture.
    # This is NOT a test of HTTP routing, WordPress, CSP or deployment.
    sheet=(BRIDGE/'generated/apollo.css').read_text()
    script=(BRIDGE/'generated/apollo.js').read_text()
    theme=(QA/'theme-mock.css').read_text()
    html=html.replace('<link rel="stylesheet" href="./qa/theme-mock.css">','<style>'+theme+'</style>')
    html=html.replace('<link rel="stylesheet" href="./bridge/generated/apollo.css" media="all" data-fv-ex2-staging-style>', '<style>'+sheet+'</style>')
    html=html.replace('<script defer src="./bridge/generated/apollo.js" data-fv-ex2-staging-script></script>', '<script>'+script+'</script>')
    assert '<script defer src=' not in html and 'href="./bridge/generated/apollo.css"' not in html
    return html


def run():
    html=preview()
    fixture=inline_for_browser(html)
    metrics_script='''(() => {
      window.__fv_lcp=0;window.__fv_cls=0;
      try{new PerformanceObserver(l=>{for(const e of l.getEntries())window.__fv_lcp=Math.max(window.__fv_lcp,e.startTime)}).observe({type:'largest-contentful-paint',buffered:true})}catch(_){ }
      try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__fv_cls+=e.value}).observe({type:'layout-shift',buffered:true})}catch(_){ }
    })();'''
    report={'lcp_reading_note':'Null means Chromium did not emit an LCP event for in-memory set_content; this is NOT an LCP=0 claim','tool':'real system Chromium + Playwright using PHP shortcode and actual generated CSS/JS in a local in-memory browser fixture','csp':'NOT_TESTED — browser admin policy blocks localhost/file/http navigation','viewports':[],'axe_core':'NOT_RUN — pinned audited axe-core bundle unavailable','wcag_certified':False,'real_wordpress':False,'production_cwv':False,'actual_asset_delivery':False,'source_head':'PR215 module parity except original response source files as documented'}
    try:
      with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width in (320,360,390,768,1024,1440,1920):
          ctx=browser.new_context(viewport={'width':width,'height':960},reduced_motion='reduce' if width==320 else 'no-preference',device_scale_factor=1)
          page=ctx.new_page();page.add_init_script(metrics_script)
          errors=[];offsite=[];csp=[]
          page.on('pageerror',lambda error: errors.append(str(error)))
          page.on('request',lambda request:offsite.append(request.url))
          page.on('console',lambda msg:csp.append(msg.text) if 'Content Security Policy' in msg.text else None)
          page.set_content(fixture,wait_until='load')
          assert page.locator('#site-main').count()==1 and page.locator('main').count()==1
          assert page.locator('.fv-ex2-apollo h1').count()==0
          assert page.locator('.fv-ex2-apollo h2#case-title').count()==1
          assert page.locator('[data-ex2-stage]').count()==6
          assert page.locator('[data-ex2-trail-card]').count()==6
          assert page.locator('[data-ex2-atlas-item]').count()==6
          assert page.locator('[data-ex2-response-item]').count()==6
          assert page.locator('a[href*="evidence-export.csv"]').count()==1
          assert page.locator('a[href*="response-export.json"]').count()==1
          assert page.locator('[data-ex2-trail-controls]').is_visible(),(width,'script missing')
          before=page.locator('.wp-theme-header').evaluate('(e)=>getComputedStyle(e).backgroundColor')
          assert before=='rgb(235, 230, 218)',(width,before,'CSS leaked')
          assert page.locator('.fv-ex2-apollo').evaluate('(e)=>getComputedStyle(e).color')!='rgb(20, 28, 30)'
          width_data=page.evaluate('''() => ({viewport:innerWidth,documentWidth:document.documentElement.scrollWidth,mainWidth:document.querySelector('#site-main').scrollWidth})''')
          assert width_data['documentWidth']<=width+1,(width,width_data)
          sel=page.locator('[data-ex2-trail-select]');sel.select_option('05')
          assert page.locator('[data-ex2-trail-card]:visible').count()==1,(width,'route filter')
          page.locator('#trail-05 summary').click()
          assert page.locator('#trail-05 details').evaluate('(e)=>e.open')
          page.locator('[data-ex2-trail-reset]').click()
          assert page.locator('[data-ex2-trail-card]:visible').count()==6,(width,'reset')
          sel.select_option('06');page.evaluate("location.hash='#trail-04'")
          page.wait_for_timeout(60)
          assert page.locator('#trail-04').is_visible()
          assert page.evaluate('document.activeElement.id')=='trail-04'
          page.evaluate("location.hash='#source-03'")
          page.wait_for_timeout(60)
          assert page.locator('#source-03').evaluate('(e)=>e.open')
          if width in (390,1440):
            page.locator('.fv-ex2-apollo .ex2-trail').screenshot(path=str(SHOTS/f'apollo-wordpress-mock-trails-{width}.png'))
          if width==390:
            page.locator('.fv-ex2-apollo .ex2-hero').screenshot(path=str(SHOTS/'apollo-wordpress-mock-hero-390.png'))
          if width==1440:
            page.locator('.fv-ex2-apollo .ex2-hero').screenshot(path=str(SHOTS/'apollo-wordpress-mock-hero-1440.png'))
          # Sanity-check the actual browser AX tree; not a replacement for axe.
          cdp=ctx.new_cdp_session(page)
          ax=cdp.send('Accessibility.getFullAXTree')
          unnamed=[x.get('role',{}).get('value') for x in ax['nodes'] if x.get('role',{}).get('value') in ('button','combobox') and not x.get('name',{}).get('value')]
          assert not unnamed,(width,unnamed)
          page.wait_for_timeout(180)
          report['viewports'].append({'width':width,'doc_width':width_data['documentWidth'],'six_stage_records':True,'six_trails':True,'six_atlas_items':True,'route_filters':True,'deep_link_focus':True,'source_opens':True,'csp_failures':csp,'page_errors':errors,'offsite_requests':offsite,'ax_unnamed_buttons_or_comboboxes':len(unnamed),'lab_observed_lcp_ms':round(page.evaluate('window.__fv_lcp || 0'),1) if page.evaluate('window.__fv_lcp || 0') > 0 else None,'lab_cls':round(page.evaluate('window.__fv_cls || 0'),5)})
          assert not errors and not offsite and not csp,(width,errors,offsite,csp)
          ctx.close()
        # No-JS: all cards, native details, no enhancement-dependent hiding.
        ctx=browser.new_context(viewport={'width':390,'height':900},java_script_enabled=False)
        page=ctx.new_page();page.set_content(fixture,wait_until='load')
        assert page.locator('[data-ex2-trail-card]:visible').count()==6
        assert not page.locator('[data-ex2-trail-controls]').is_visible()
        assert page.locator('[data-ex2-response-item]:visible').count()==6
        assert page.locator('[data-ex2-atlas-item]:visible').count()==6
        page.locator('#trail-02 summary').click()
        assert page.locator('#trail-02 details').evaluate('(e)=>e.open')
        ctx.close()
        report['no_js_full_sources']=True
        # 200%-equivalent zoom reflow is measured separately, not confused with viewport alone.
        ctx=browser.new_context(viewport={'width':640,'height':900})
        page=ctx.new_page();page.set_content(fixture,wait_until='load')
        page.evaluate("document.documentElement.style.zoom = '200%'")
        page.wait_for_timeout(70)
        report['zoom_200_percent']={'viewport':640,'document_width':page.evaluate('document.documentElement.scrollWidth')}
        assert report['zoom_200_percent']['document_width']<=641,report['zoom_200_percent']
        ctx.close()
        browser.close()
    finally:pass
    (QA/'BRIDGE_BROWSER_RESULTS.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('WP_BRIDGE_BROWSER_PASS',len(report['viewports']),'viewports, noJS, generated CSS/JS, AX smoke, 200% zoom; screenshots captured; HTTP/CSP untested')
    return report

if __name__=='__main__':run()
