#!/usr/bin/env python3
"""Real Chromium routed-image smoke test, SYNTHETIC ONLY (not WordPress QA).

Uses Page.on('response') and intercepted in-memory WebP/JPEG to prove that the
same browser response bytes the image decoded are those attested. No localhost,
external network, production site or authenticated archival image is involved.
Requires Playwright, Chromium and Pillow; missing tools are a hard failure.
"""
from io import BytesIO
import shutil
from hashlib import sha256
from PIL import Image
from playwright.sync_api import sync_playwright
from archive_gallery_transfer import audit_archive_gallery
from browser_consumed_media import BrowserEvidencePage

HOST='https://fv-stage.invalid'
NAMES=('apollo.webp','franklin.jpg','nypl.jpg')
MEDIA_TYPES={'apollo.webp':'WEBP','franklin.jpg':'JPEG','nypl.jpg':'JPEG'}
CONTENT_TYPES={'apollo.webp':'image/webp','franklin.jpg':'image/jpeg','nypl.jpg':'image/jpeg'}
CASES=(('apollo','apollo.webp'),('franklin','franklin.jpg'),('malbone','nypl.jpg'))

def fake_image(name, color):
    bio=BytesIO()
    Image.new('RGB',(1,1),color).save(bio,format=MEDIA_TYPES[name])
    return bio.getvalue()

def assert_require(ok, message):
    if not ok:raise AssertionError('CHROMIUM BROWSER RESPONSE GATE: '+message)

def run(corrupt=False):
    originals={name:fake_image(name,(44,84,128)) for name in NAMES}
    served=dict(originals)
    if corrupt:served['apollo.webp']=fake_image('apollo.webp',(240,12,44))
    manifest={name:sha256(data).hexdigest() for name,data in originals.items()}
    media={name:(len(data),1,1) for name,data in originals.items()}
    html='<div class="fv-hf"><div data-fv-case-buttons>'
    for case,name in CASES:
        html+=f'<button data-fv-case-button="{case}" type="button">{case}</button>'
    html+='</div>'
    for case,name in CASES:
        hide=' hidden' if case!='apollo' else ''
        html+=f'<section style="min-height: 70px; min-width: 150px" data-fv-case="{case}"{hide}><img data-fv-archive-img alt="Synthetic {case} test image" src="{HOST}/media/{name}" width="1" height="1" loading="lazy"></section>'
    html+='</div><script>document.querySelectorAll("[data-fv-case-button]").forEach(b=>b.onclick=()=>{document.querySelectorAll("[data-fv-case]").forEach(p=>p.hidden=p.dataset.fvCase!==b.dataset.fvCaseButton);});</script>'
    with sync_playwright() as p:
        executable=shutil.which('chromium') or shutil.which('chromium-browser')
        browser=p.chromium.launch(executable_path=executable if executable else None,headless=True,args=['--no-sandbox'])
        try:
            page=browser.new_page(viewport={'width':390,'height':900})
            responses=[]
            page.on('response',lambda response:responses.append(response))
            def route_media(route):
                name=route.request.url.rsplit('/',1)[-1]
                assert_require(name in served, 'unexpected routed image')
                route.fulfill(status=200,content_type=CONTENT_TYPES[name],body=served[name])
            page.route('**/media/*',route_media)
            page.set_content(html,wait_until='load')
            def attest(name, body, dims, trusted):
                assert_require(sha256(body).hexdigest()==trusted,'wrong bytes loaded by real browser')
                return {'sha256':trusted,'bytes':len(body),'dimensions':dims}
            adapter=BrowserEvidencePage(page,responses,('https','fv-stage.invalid'))
            if corrupt:
                try:
                    audit_archive_gallery(adapter,('https','fv-stage.invalid'),manifest,media,assert_require,attest)
                except (AssertionError,RuntimeError):return {'result':'REJECTED_CORRUPT_BROWSER_TRANSFER','browser_response_count':len(responses)}
                raise AssertionError('corrupted image was incorrectly accepted')
            receipt=audit_archive_gallery(adapter,('https','fv-stage.invalid'),manifest,media,assert_require,attest)
            return {'result':'PASS_ACTUAL_CHROMIUM_ROUTED_SYNTHETIC_BYTES','verified':sorted(receipt),'browser_response_count':len(responses)}
        finally:browser.close()
if __name__=='__main__':
    print(run(False))
    print(run(True))
