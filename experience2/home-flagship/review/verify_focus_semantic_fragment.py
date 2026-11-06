#!/usr/bin/env python3
"""Chromium proof of a semantic #subscribe-blog target; synthetic Jetpack fixture ONLY.
Not WordPress, Jetpack, production, paid conversion, or WCAG certification.
Run: python experience2/home-flagship/review/verify_focus_semantic_fragment.py
Requires playwright + a local Chromium executable. Fails closed if unavailable.
"""
import json
import shutil
from playwright.sync_api import sync_playwright

STYLES = """<style>
*{box-sizing:border-box}body{margin:0;background:#090a0a;color:#f4efe6;font:18px/1.5 system-ui}
a{color:#d9ad73}a:focus-visible{outline:3px solid #f6cc86}
.lead{min-height:65vh;padding:24px 20px;background:#111b19}
.links{display:flex;flex-direction:column;gap:12px}
.signup{min-height:55vh;background:#141514;padding:22px 20px;border-top:1px solid #b8955e}
.screen-reader-text{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap}
h2.screen-reader-text:focus{clip-path:none;width:auto;height:auto;position:static;outline:3px solid #f6cc86}
footer{height:45vh}
</style>"""
LINKS = ''.join(f'<a href="#subscribe-blog">Get the free Fieldbook {i}</a>' for i in range(1, 6))
HEAD = ('<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        + STYLES + '<main><div class="lead"><h1>Free 52-page Fieldbook</h1>'
        + '<div class="links">' + LINKS + '</div></div><section class="signup">')
TAIL = ('<div class="wp-block-jetpack-subscriptions"><label for="email">Email address</label>'
        '<input id="email" type="email"><button type="button">Subscribe</button></div>'
        '</section></main><footer></footer></html>')
OLD = '<span id="subscribe-blog" style="display:block;scroll-margin-top:5rem" aria-hidden="true"></span>'
NEW = ('<h2 id="subscribe-blog" class="screen-reader-text" tabindex="-1" '
       'style="scroll-margin-top:5rem">Subscribe to receive the free Seven Day Focus Fieldbook</h2>')

def main():
    exe = shutil.which('chromium') or shutil.which('chromium-browser')
    if not exe:
        raise SystemExit('BLOCKED: local Chromium not available')
    cases = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path=exe, headless=True,
                                             args=['--no-sandbox'])
        for width in (320, 390, 1440):
            for js_enabled in (False, True):
                for name, anchor in (('old-scroll-only', OLD), ('new-semantic-focus', NEW)):
                    page = browser.new_page(viewport={'width':width,'height':800},
                                            java_script_enabled=js_enabled)
                    page.set_content(HEAD + anchor + TAIL)
                    page.locator('a[href="#subscribe-blog"]').first.focus()
                    page.keyboard.press('Enter')
                    data = page.evaluate("""() => {
                      const t=document.getElementById('subscribe-blog');
                      return {hash:location.hash, targetFocused:document.activeElement===t,
                        readable:t.getAttribute('aria-hidden')!=='true', tag:t.tagName,
                        scrollY:Math.round(window.scrollY),
                        overflow:document.documentElement.scrollWidth>innerWidth,
                        formCount:document.querySelectorAll('.wp-block-jetpack-subscriptions').length};
                    }""")
                    expected = name == 'new-semantic-focus'
                    assert data['hash']=='#subscribe-blog' and data['scrollY']>0, data
                    assert data['formCount']==1 and not data['overflow'], data
                    assert data['targetFocused']==expected and data['readable']==expected, data
                    if expected:
                        page.keyboard.press('Tab')
                        assert page.evaluate('document.activeElement.id')=='email'
                    cases.append({'width':width,'js':js_enabled,'state':name,'passed':True,
                                  'targetFocused':data['targetFocused']})
                    page.close()
        browser.close()
    assert len(cases)==12
    print(json.dumps({'cases':len(cases),'passed':12,'scope':'synthetic browser fixture',
                      'actual_jetpack_verified':False,'cases_detail':cases},indent=2))

if __name__=='__main__':
    main()
