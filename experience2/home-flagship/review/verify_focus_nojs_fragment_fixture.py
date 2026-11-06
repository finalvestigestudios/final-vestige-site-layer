#!/usr/bin/env python3
"""Representative no-JS fragment behavior; NOT WordPress/Jetpack certification."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json

out = Path(__file__).resolve().parent
style = ('<style>*{box-sizing:border-box}body{background:#0a0b0b;color:#e7dcc6;'
         'font:18px/1.5 system-ui;margin:0}main{max-width:750px;margin:auto;'
         'padding:20px}a{display:inline-block;min-height:48px;color:#f4cb8d;'
         'padding:10px}section{padding:18px;border-bottom:1px solid #665740}'
         '.spacer{height:1050px}.wp-block-jetpack-subscriptions{border:2px solid'
         ' #d2ad7a;padding:24px}a:focus-visible{outline:3px solid gold}</style>')
start = '<main><h1>Representation only: simulated Focus signup anchor</h1>'
for n in range(5):
    start += (f'<section><p>Repeated CTA {n+1}</p>'
              '<a href="#subscribe-blog">Get the free fieldbook</a></section>')
start += '<div class="spacer" aria-hidden="true"></div>'
end = ('<div class="wp-block-jetpack-subscriptions">Native Jetpack block placement '
       '(placeholder; no functioning form)</div></main>')
anchor = ('<span id="subscribe-blog" style="display:block;scroll-margin-top:5rem" '
          'aria-hidden="true"></span>')

results = []
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    for width in (320, 390, 1440):
        for name, fragment in (("before", ""), ("after", anchor)):
            html = ('<!doctype html><html lang="en"><meta charset="utf-8">'
                    '<meta name="viewport" content="width=device-width,initial-scale=1">'
                    + style + start + fragment + end + '</html>')
            context = browser.new_context(viewport={'width':width,'height':840},
                                          java_script_enabled=False,reduced_motion='reduce')
            page = context.new_page()
            page.set_content(html)
            page.locator('a[href="#subscribe-blog"]').first.click()
            result = page.evaluate("""() => ({
              anchor: !!document.getElementById('subscribe-blog'),
              hash: location.hash, scrollY: scrollY,
              scrollWidth: document.documentElement.scrollWidth, width: innerWidth
            })""")
            expected = name == "after"
            passed = (result['anchor'] is expected
                      and result['hash'] == '#subscribe-blog'
                      and (result['scrollY'] > 400) == expected
                      and result['scrollWidth'] <= result['width'] + 1)
            results.append(dict(width=width,mode=name,passed=passed,**result))
            context.close()
    browser.close()
print(json.dumps({'cases':len(results),'passed':sum(x['passed'] for x in results),
                  'representation':'not WordPress; no live Jetpack or commerce'},indent=2))
if not all(x['passed'] for x in results):
    raise SystemExit(1)
