#!/usr/bin/env python3
"""R390 no-network boundary contract: fake HTTP routes and CSS byte custody.

Chromium cannot navigate to even localhost in this runner (administrator block).
This deliberately NEVER reports true installed-stage network acceptance.
"""
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import urlparse

BASE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(BASE/'apollo-r389'/'qa'))
from staging_smoke import (guard, staging_resource_allowed,
                           install_network_boundary,inspect_stylesheet_responses,
                           REVIEWED_GALLERY_CSS_SHA256)

checks=0;outcomes=[]
def check(ok,label):
    global checks
    checks+=1
    if not ok: raise AssertionError(label)
    outcomes.append(label)

host='stage-review.example.test'
unsafe=['https://finalvestige.com/apollo/','https://www.finalvestige.com/x',
        'https://other.example.test/x','http://stage-review.example.test/a',
        'https://stage-review.example.test.evil.test/x',
        'https://evil@stage-review.example.test/x']
for url in unsafe:
    check(not staging_resource_allowed(url,host),'deny '+url)
for url in ['https://stage-review.example.test/',
            'https://STAGE-review.example.test/assets/gallery.css?v=1']:
    check(staging_resource_allowed(url,host),'allow '+url)
check(guard('https://stage-review.example.test/gallery/',host)==host,'explicit approved staging URL')

class FakeResponse:
    def __init__(self,url='',status=200,body=b'',headers=None):
        self.url=url;self.status=status;self.payload=body;self.headers=headers or {}
    def body(self):return self.payload

class FakeRequest:
    def __init__(self,url,kind='document'):
        self.url=url;self.resource_type=kind;self.method="GET"
    def is_navigation_request(self):return self.resource_type=='document'

class FakeRoute:
    def __init__(self,url,status=200,headers=None):
        self.request=FakeRequest(url)
        self.status=status;self.headers=headers or {}
        self.action=None;self.opts=None
    def abort(self,error_code):self.action=('abort',error_code)
    def fulfill(self,response):self.action=('fulfill',response.status)
    def fetch(self,**kwargs):
        self.opts=kwargs
        return FakeResponse(self.request.url,self.status,headers=self.headers)

class FakeWebSocket:
    def __init__(self,url):self.url=url;self.closed=None
    def close(self,**kwargs):self.closed=kwargs

class FakeContext:
    def route(self,pattern,callback):
        assert pattern=='**/*'
        self.callback=callback
    def route_web_socket(self,pattern,callback):
        assert pattern=='**/*'
        self.websocket_callback=callback

context=FakeContext();denied=[]
install_network_boundary(context,host,denied)
# R389 bug: an allowed initial URL 302 could redirect to live production.
redirect=FakeRoute('https://stage-review.example.test/apollo',302,
    {'location':'https://finalvestige.com/landing'})
context.callback(redirect)
check(redirect.action==('abort','blockedbyclient'),'302 rejected *before* redirect follow-through')
check(redirect.opts.get('max_redirects')==0,'fetch explicitly disables redirect following')
check(len(denied)==1 and denied[0].get('redirect_location')=='https://finalvestige.com/landing',
      'redirect target recorded as release blocker')
# Even same-host redirects must hold until separately reviewed.
same=FakeRoute('https://stage-review.example.test/apollo',301,
    {'location':'/apollo-new'})
context.callback(same)
check(same.action[0]=='abort','same-host redirects do not silently pass')
# External resources have no fetch side effect at all.
external=FakeRoute('https://finalvestige.com/style.css')
context.callback(external)
check(external.action==('abort','blockedbyclient') and external.opts is None,
      'production subresource denied before HTTP fetch')
http=FakeRoute('http://stage-review.example.test/style.css')
context.callback(http)
check(http.action[0]=='abort' and http.opts is None,'mixed-content asset denied before HTTP fetch')
# Same-origin, non-redirect responses can pass.
safe=FakeRoute('https://stage-review.example.test/assets/gallery.css',200)
context.callback(safe)
check(safe.action==('fulfill',200),'approved nonredirect response forwarded')
check(safe.opts.get('max_redirects')==0,'nonredirect response still fetches without redirects')

css=(BASE/'apollo-r384/assets/gallery.css').read_bytes()
check(hashlib.sha256(css).hexdigest()==REVIEWED_GALLERY_CSS_SHA256,'local sealed CSS digest identical')
url='https://stage-review.example.test/wp-content/plugins/apollo/assets/gallery.css?ver=r384'
for cases,expected,label in [
 ([FakeResponse(url,200,css)],True,'exact CSS bytes pass'),
 ([FakeResponse(url,200,css+b' ')],False,'modified CSS bytes fail'),
 ([FakeResponse(url,404,css)],False,'failed CSS HTTP response fails'),
 ([],False,'missing CSS response fails'),
 ([FakeResponse(url,200,css)]*2,False,'duplicate CSS responses fail')]:
    value,observed=inspect_stylesheet_responses(cases)
    check(value is expected,label)

# R391: no mutating HTTP request should ever reach staging, even same-origin.
for method in ('POST','PUT','PATCH','DELETE','TRACE','OPTIONS'):
    check(not staging_resource_allowed('https://'+host+'/wp-json/api',host,method),
          'deny non-readonly method '+method)
for url in ('https://'+host+':8443/a','https://'+host+':444/a',
            'https://'+host+':bogus/a','https://'+host+'/a#fragment'):
    check(not staging_resource_allowed(url,host),'deny alternate origin/fragment '+url)
from staging_smoke import scrub_url
check(scrub_url('https://user:secret@'+host+'/x?q=PRIVATE#token')=='https://'+host+'/x',
      'scrub credentials and query strings from output')
for method in ('POST','PUT','PATCH','DELETE'):
    r=FakeRoute('https://'+host+'/wp-admin/admin-ajax.php?token=PRIVATE')
    r.request.method=method
    context.callback(r)
    check(r.action==('abort','blockedbyclient') and r.opts is None,
          'mutation denied before fetch '+method)
    check('PRIVATE' not in json.dumps(denied),'mutating URL query redacted '+method)
ws=FakeWebSocket('wss://'+host+'/events?token=PRIVATE')
context.websocket_callback(ws)
check(ws.closed is not None and ws.closed.get('code')==1008,
      'WebSocket denied before handshake')
check(denied[-1]['kind']=='websocket' and 'PRIVATE' not in json.dumps(denied),
      'WebSocket query redacted')
# No-JS source custody must include actual delivered CSS and two NASA publishers.
staging_code=(BASE/'apollo-r389/qa/staging_smoke.py').read_text()
for token in ('nojs_gallery_css_verified','nojs_gallery_css_responses',
              'nojs_publication_links','nojs_nasa_question_links','nojs_free_ctas',
              "nojs.on('response'"):
    check(token in staging_code,'no-JS staging contract '+token)

report={'status':'PASS','assertions':checks,'checks':outcomes,
        'scope':'pure HTTP and WebSocket boundary mocks, read-only methods and no-JS CSS custody (no network)',
        'real_chromium_route':'NOT TESTED: browser administrator blocks even localhost HTTPS',
        'installed_wordpress':'NOT TESTED','genuine_axe':'NOT EXECUTED',
        'external_requests_sent':0,'real_axe':'NOT EXECUTED'}
qa=Path(__file__).resolve().parents[1]/'QA';qa.mkdir(exist_ok=True)
(qa/'network-boundary-results.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps({'status':'PASS','assertions':checks,'external_requests_sent':0,'real_axe':'NOT EXECUTED'},indent=2))
