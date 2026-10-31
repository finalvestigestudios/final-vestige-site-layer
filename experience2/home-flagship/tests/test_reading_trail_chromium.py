#!/usr/bin/env python3
"""Offline Chromium regression for exact Reading Trail JS in a REPRESENTATIVE layout.

This tests the browser's actual fragment, focus, scroll and CSSOM behavior, but
NOT full Experience 2.0 HTML, Assembler, WordPress or Lighthouse acceptance.
Run from any complete checkout: python experience2/home-flagship/tests/test_reading_trail_chromium.py
Requires Playwright and a Chromium executable (FV_CHROMIUM path overrides default).
"""
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

JS = (Path(__file__).resolve().parent.parent / 'reading-trail.js').read_text(encoding='utf-8')
IDS = ['fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry',
       'fv-hf-method-title','fv-hf-observer','fv-hf-mind-title']
HEIGHTS = [1400,1500,1100,1100,1500,1400,1800]

def html():
    nav = ''.join('<a href="#'+a+'">'+a+'</a>' for a in IDS)
    sections = ''.join('<section style="height:'+str(height)+'px"><h2 id="'+id+'">'+id+'</h2><p>Representative geometry, not archival content.</p></section>'
                       for height,id in zip(HEIGHTS,IDS))
    style = ('<style>*{box-sizing:border-box}body{margin:0;background:#090a0a;color:#f4efe6}'
             '.fv-hf__chapter-nav{height:55px;display:flex;overflow-x:auto;position:sticky;top:0;z-index:2;background:#111}'
             '.fv-hf__chapter-nav a{flex:none;display:inline-flex;padding:10px;align-items:center;color:#f4efe6}'
             'section{padding:70px 22px;border-bottom:1px solid #444}'
             '@media(prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}</style>')
    assert '</script>' not in JS.lower(), 'Untrusted script boundary'
    return '<!doctype html><html lang="en"><head>'+style+'</head><body><div data-fv-home-flagship class="fv-hf"><nav class="fv-hf__chapter-nav">'+nav+'</nav><main>'+sections+'</main></div><script>'+JS+'</script></body></html>'

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.environ.get('FV_CHROMIUM','/usr/bin/chromium'), args=['--no-sandbox'])
        for width in (320,360,390,768,1024,1440,1920):
            context = browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce')
            page = context.new_page(); page.set_content(html())
            page.evaluate('window.scrollTo(0,7400)'); page.wait_for_timeout(100)
            data = page.evaluate('''() => ({p:Number(document.querySelector('nav').style.getPropertyValue('--fv-trail-progress')),
             active:[...document.querySelectorAll('nav a')].findIndex(a=>a.getAttribute('aria-current')==='location'),
             horizontal:document.documentElement.scrollWidth>innerWidth+1,
             chapters:document.querySelectorAll('main h2').length})''')
            assert 0.78 < data['p'] < 0.89, (width,data)
            assert data['active'] == 5 and data['chapters'] == 7 and not data['horizontal'],(width,data)
            print('PASS',width,'progress',round(data['p'],4),'active',data['active'])
            context.close()
        context = browser.new_context(viewport={'width':390,'height':900},reduced_motion='reduce')
        page=context.new_page();page.set_content(html());page.locator('nav a').nth(3).focus();page.keyboard.press('Enter');page.wait_for_timeout(100)
        data=page.evaluate('() => ({hash:location.hash,focused:document.activeElement?.id})')
        assert data == {'hash':'#fv-hf-inquiry','focused':'fv-hf-inquiry'},data
        print('PASS keyboard-native-anchor',data)
        context.close()
        nojs=browser.new_context(viewport={'width':390,'height':900},java_script_enabled=False)
        page=nojs.new_page();page.set_content(html())
        data=page.evaluate('''() => ({chapterCount:document.querySelectorAll('main h2').length,
        navLinks:document.querySelectorAll('nav a').length,
        enhanced:document.querySelector('nav').hasAttribute('data-fv-trail-enhanced')})''')
        assert data == {'chapterCount':7,'navLinks':7,'enhanced':False},data
        print('PASS no-JS-native-links',data)
        nojs.close();browser.close()
    return 0

if __name__=='__main__':
    sys.exit(main())
