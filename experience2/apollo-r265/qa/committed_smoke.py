#!/usr/bin/env python3
"""R265 exact-source offline Chromium smoke; staging only, no live HTTP or axe claim."""
import hashlib, json, subprocess, sys
from pathlib import Path
from urllib.parse import urlencode
from playwright.sync_api import sync_playwright

root=Path(sys.argv[1]).resolve()
over=Path(sys.argv[2]).resolve()
stage=Path(__file__).resolve().parent.parent
mock=Path(sys.argv[3]).resolve()
seal='f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68'
free='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha((root/'manifest.json').read_bytes())==seal
for name,digest in json.loads((root/'manifest.json').read_text())['files'].items():
    assert sha((root/name).read_bytes())==digest, name
js=(stage/'assets/campaign-continuity.js').read_text()
assert sha(js.encode()) in (stage/'fv-apollo-campaign-staging.php').read_text()
state=json.loads(subprocess.check_output(['php',str(mock),str(root/'fv-ex2-apollo-r224.php'),str(over/'fv-apollo-staging-overlay.php'),'direct']))
assert state['atlas_present'] and not state['fallback']
html='<html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+ (root/'assets/atlas-scoped.css').read_text()+(over/'assets/apollo-overlays.css').read_text()+'</style>'+state['html']+'</html>'
valid=dict(utm_source='youtube',utm_medium='organic_social',utm_campaign='apollo_pilot_2026_11',utm_content='Yt_Apollo_001')
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    count=0
    for enabled in (False,True):
        context=browser.new_context(viewport={'width':320,'height':900},java_script_enabled=enabled,has_touch=True,is_mobile=True,reduced_motion='reduce')
        page=context.new_page()
        for width in (320,390,768,1440,1920):
            page.set_viewport_size({'width':width,'height':900})
            for source in ('youtube','unverified'):
                args=dict(valid,utm_source=source)
                page.goto('about:blank?'+urlencode(args))
                page.set_content(html)
                if enabled: page.add_script_tag(content=js)
                link=page.locator('#fv-apollo-reading-bridge a.cta').get_attribute('href')
                expected=free+('?' + urlencode(valid) if enabled and source=='youtube' else '')
                assert link==expected,(width,enabled,source,link)
                assert page.locator('a[href^="https://www.nasa.gov/"]').count()==55
                assert page.locator('a[href^="#"]').count()==31
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
                count+=1
        context.close()
    browser.close()
print(json.dumps({'passed':True,'contexts':count,'source_seal':seal,'script_sha256':sha(js.encode()),'live':False}))
