#!/usr/bin/env python3
"""Fail-closed source-exact STATIC Chromium review; NOT WordPress/Assembler or WCAG certification.

Run: python3 experience2/home-flagship/playground/verify_short_viewport_browser.py
Requires Python Playwright and Chromium. No network, CMS writes, subscribers, or claims of CWV.
"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

BLUEPRINT = Path(__file__).with_name('FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json')
blueprint = json.loads(BLUEPRINT.read_text(encoding='utf-8'))
php = blueprint['steps'][2]['data']

def segment(name):
    opening = "<<<'FVPG_%s_END'\n" % name
    closing = '\nFVPG_%s_END' % name
    assert php.count(opening) == php.count(closing) == 1, name
    return php.split(opening, 1)[1].split(closing, 1)[0]

markup, css, js = [segment(x) for x in ('HTML','CSS','JS')]
assert 'short-viewport conversion-first composition' in css
assert markup.count('class="fv-margin-strip__item"') == 72
assert markup.count('https://finalvestige.com/focus/') == 5
assert markup.count('class="fv-hf__chapter-nav"') == 1
assert 'DESIGN CANDIDATE · NOT LIVE' in markup
html = ('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<style>' + css + '</style><body><main>' + markup + '</main><script>' + js + '</script>')
widths = [(320,568),(360,640),(390,667),(600,900),(768,900),(1440,900),(1920,900)]
results=[]
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for width,height in widths:
        for enable_js in (True,False):
            page = browser.new_page(viewport={'width':width,'height':height},java_script_enabled=enable_js)
            page.route('**/*',lambda route:route.abort())
            errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.set_content(html,wait_until='domcontentloaded')
            result=page.evaluate('''() => {
              const box=s=>{const e=document.querySelector(s),r=e.getBoundingClientRect();return {y:r.y,bottom:r.bottom,h:r.height}};
              return {docWidth:document.documentElement.scrollWidth,width:innerWidth,
                focus:box('.fv-hf__text-link--focus'),mast:box('.fv-hf__mast-cta'),
                evidence:box('.fv-hf__button--gold'),trail:box('.fv-hf__chapter-nav a'),
                chapters:document.querySelectorAll('.fv-hf__chapter-nav a').length,
                margins:document.querySelectorAll('.fv-margin-strip__item').length,
                focusLinks:document.querySelectorAll('a[href="https://finalvestige.com/focus/"]').length};}''')
            assert not errors,(width,height,errors)
            assert (result['chapters'],result['margins'],result['focusLinks']) == (7,72,5)
            assert result['docWidth'] <= width+1,(width,'horizontal overflow')
            for key in ('mast','evidence','focus','trail'):
                assert result[key]['h']>=44,(width,key,'target too short')
            if width==390:
                assert result['focus']['bottom'] <=667,('390x667 contextual CTA clipped',result['focus'])
                assert page.locator('.fv-hf__studio-note').is_visible()
                if enable_js:
                    page.locator('[data-fv-chronicle-view="addition"]').click()
                    assert page.locator('[data-fv-chronicle-view="addition"]').get_attribute('aria-pressed')=='true'
                    page.locator('[data-fv-case-button="franklin"]').click()
                    assert page.locator('[data-fv-case-button="franklin"]').get_attribute('aria-pressed')=='true'
                else:
                    assert page.locator('.fv-margin-strip__item').count()==72
            results.append({'w':width,'h':height,'js':enable_js,'pass':True,'metrics':result})
            page.close()
    for motion in ('reduce','no-preference'):
        page=browser.new_page(viewport={'width':390,'height':667},reduced_motion=motion)
        page.route('**/*',lambda route:route.abort())
        page.set_content(html)
        if motion=='reduce':
            assert page.locator('.fv-margin-strip__motion-toggle').is_hidden()
            assert page.locator('.fv-margin-strip__item').first.evaluate('(e)=>getComputedStyle(e).animationName')=='none'
        results.append({'motion':motion,'pass':True})
        page.close()
    for width in (390,768):
        page=browser.new_page(viewport={'width':width,'height':900})
        page.route('**/*',lambda route:route.abort())
        page.set_content(html)
        page.evaluate('document.documentElement.style.zoom="200%"')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),('CSS 200% zoom overflow',width)
        results.append({'zoom200':width,'pass':True})
        page.close()
    browser.close()
print(json.dumps({'result':'PASS','count':len(results),'scope':'source-exact local static Chromium, NOT WordPress, axe or Lighthouse',
                  'mobile_focus_390x667':next(r['metrics']['focus'] for r in results if r.get('w')==390 and r.get('js'))},indent=2))
