"""Optional real hosted browser acceptance. Refuses live host or absent URL.
STAGING_APOLLO_URL=https://<approved-staging-host>/... python qa/staging_http_acceptance.py
Requires separately deployed authorized staging component; no WordPress writes.
"""
import os, json
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
url=os.environ.get('STAGING_APOLLO_URL','')
parsed=urlsplit(url)
assert parsed.scheme=='https' and parsed.hostname not in {'finalvestige.com','www.finalvestige.com'} and parsed.hostname, 'HOLD: approved HTTPS staging URL only'
results=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    for width in (320,390,768,1440,1920):
        context=b.new_context(viewport={'width':width,'height':900});page=context.new_page()
        resp=page.goto(url,wait_until='domcontentloaded',timeout=12000)
        assert resp and resp.status==200,(width,resp.status if resp else None)
        assert resp.headers.get('content-security-policy'), 'HOLD: actual HTTP CSP missing'
        assert page.locator('[data-fv-nasa-source]').count()==4,'NASA source trail missing'
        assert page.locator('[data-fv-free-cta]').count()==1,'one CTA violated'
        scroll=page.evaluate('document.documentElement.scrollWidth');assert scroll<=width+1,(width,scroll)
        results.append({'width':width,'status':resp.status,'cspHeader':True,'sourceLinks':4,'freeCTA':1})
        context.close()
    b.close()
print(json.dumps({'passed':True,'scope':'Actual approved staging HTTPS, CSP header and Chromium navigation; NOT production','cases':results},indent=2))
