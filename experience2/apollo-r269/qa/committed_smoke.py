#!/usr/bin/env python3
"""R269 sealed NASA provenance and honest conversion browser smoke.
Offline R263 real-PHP WordPress shim, NOT installed WordPress, axe or live HTTP.
"""
import hashlib, importlib.util, json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
f,o,s,r,m,contract_file,out=map(lambda p:Path(p).resolve(),sys.argv[1:8])
source=Path(__file__).resolve().parents[2]/'apollo-r268/qa/cdp_accessibility.py'
spec=importlib.util.spec_from_file_location('r268_custody',source)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
contract=json.loads(contract_file.read_text())
assert contract['source_manifest_sha256']==mod.ORIGINAL_MANIFEST_SHA256
assert contract['approval_state']=='HARD_HOLD_NOT_LIVE'
assert contract['baseline_nasa_count']==55 and contract['baseline_distinct_nasa_urls']==10
atlas,card,css=mod.check_source(f,o,s,r,m)
html=mod.document(atlas,card,css)
JS='''() => {const t=e=>(e?.textContent||'').replace(/\\s+/g,' ').trim(),a=document.querySelector('.fv-apollo-atlas'),c=document.querySelector('.fv-apollo-postscript');
if(!a||!c)return {missing:true};const pairs=q=>[...a.querySelectorAll(q)].map(e=>[e.getAttribute('href'),t(e)]);
return {nasa:pairs('a[href^="https://www.nasa.gov/"]'),chronology:[...a.querySelectorAll('#fv-apollo-chronology time')].map(e=>[e.getAttribute('datetime'),t(e)]),
evidence:[...a.querySelectorAll('.plate')].map(e=>[e.id,t(e)]),gallery:[...a.querySelectorAll('.source-card')].map(e=>[e.id,t(e)]),drawer:t(a.querySelector('#fv-apollo-source-drawer')),
custody:t(a.querySelector('.fv-apollo-custody')),rights:t(a.querySelector('.fv-apollo-custody-rights')),free:pairs('a[href*="the-hatch-opened-inward"]'),
guide:[...c.querySelectorAll('a[href]')].map(e=>[e.getAttribute('href'),t(e)]),disclosure:t(c.querySelector('.fv-apollo-postscript__disclosure')),
order:a.compareDocumentPosition(c)&Node.DOCUMENT_POSITION_FOLLOWING?'atlas-before-card':'invalid',
geo:a.querySelectorAll('[data-lat],[data-lon],[data-lng],[data-latitude],[data-longitude],a[href*="google.com/maps"]').length,
externalMedia:document.querySelectorAll('img[src^="http"],iframe,script[src],form[action]').length,
allAtlasExternal:[...a.querySelectorAll('a[href^="http"]')].map(e=>e.getAttribute('href')),headlessCommerce:c.getAttribute('data-release')};}'''
canon=lambda v:hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def check(page):
 snap=page.evaluate(JS)
 assert canon(snap)==contract['snapshot_sha256'],'source URLs/labels/dates/rights/CTA drift'
 assert len(snap['nasa'])==55 and len(snap['chronology'])==6 and snap['geo']==snap['externalMedia']==0
 assert snap['order']=='atlas-before-card' and snap['headlessCommerce']=='REVIEW-ONLY'
 assert len(snap['free'])==len(snap['guide'])==1
 assert snap['free'][0][0]==mod.FREE_ARTICLE and snap['guide'][0][0]==mod.BUYING_GUIDE
 assert 'NASA does not endorse' in snap['disclosure'] and 'not been licensed or cleared' in snap['rights']
 assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
 assert page.locator('.fv-apollo-postscript__disclosure').evaluate('e=>e.getBoundingClientRect().height>0')
mutants={
 'NASA_same_host_record_swap':'''document.querySelector('.fv-apollo-atlas a[href^="https://www.nasa.gov/"]').href='https://www.nasa.gov/gallery/apollo-1/' ''',
 'false_date':'''document.querySelector('#fv-apollo-chronology time').dateTime='1968-01-03' ''',
 'wrong_photo_claim':'''document.querySelector('.source-card p').textContent='The ignition spark is shown.' ''',
 'missing_rights':'''document.querySelector('.fv-apollo-custody-rights').remove()''',
 'imaginary_geo':'''document.querySelector('.source-card').dataset.lat='28.5' ''',
 'commercial_insert':'''document.querySelector('.fv-apollo-atlas').insertAdjacentHTML('beforeend','<a href="https://merchant.invalid/">Buy</a>')''',
 'hidden_disclosure':'''document.querySelector('.fv-apollo-postscript__disclosure').style.display='none' ''',
 'redirected_free_cta':'''document.querySelector('.fv-apollo-atlas a[href*="the-hatch-opened-inward"]').href='https://merchant.invalid/' ''',
 'tracking_pixel':'''document.body.insertAdjacentHTML('beforeend','<img src="https://merchant.invalid/pixel">')''',
 'false_endorsement':'''document.querySelector('.fv-apollo-postscript__action').textContent='Official NASA merchandise' '''}
out.mkdir(parents=True,exist_ok=True)
count=0;rejected=[];screens={}
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for width in (320,390,768,1440,1920):
  for js in (False,True):
   ctx=b.new_context(viewport={'width':width,'height':900},java_script_enabled=js,is_mobile=width<=390,has_touch=width<=390,reduced_motion='reduce')
   page=ctx.new_page();requests=[];page.on('request',lambda rq:requests.append(rq.url))
   page.set_content(html)
   if js:page.add_script_tag(content=(o/'assets/source-drawer-focus.js').read_text())
   check(page);assert not requests
   drawer=page.locator('.fv-apollo-source-drawer');summary=drawer.locator('summary')
   if js:
    link=page.locator('a[href="#fv-apollo-source-drawer"]').first;link.focus();link.press('Enter')
    page.wait_for_function("document.activeElement===document.querySelector('.fv-apollo-source-drawer summary')",timeout=1600)
   else:summary.focus();summary.press('Enter')
   assert drawer.get_attribute('open') is not None
   if width<=390:summary.tap();assert drawer.get_attribute('open') is None
   page.evaluate('document.documentElement.style.fontSize="400%"')
   assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
   page.emulate_media(media='print')
   assert page.locator('.fv-apollo-postscript').evaluate('e=>getComputedStyle(e).display==="none"')
   if width in (390,1440):
    page.emulate_media(media='screen');page.set_content(html)
    shot=out/f'{width}-{"js" if js else "nojs"}.png';page.screenshot(path=str(shot),animations='disabled');screens[shot.name]=sha(shot)
   if width==390 and js:
    for name,script in mutants.items():
     page.set_content(html);page.evaluate(script)
     try:check(page)
     except AssertionError:rejected.append(name)
     else:raise AssertionError('unsafe mutation accepted: '+name)
   count+=1;ctx.close()
 b.close()
assert count==10 and len(rejected)==10
receipt={'status':'LOCAL_PASS_HARD_HOLD','contexts':count,'mutations_rejected':rejected,
 'source_manifest_sha256':mod.ORIGINAL_MANIFEST_SHA256,'contract_sha256':sha(contract_file),'screenshots':screens,
 'axe_core':'NOT_EXECUTED','installed_wordpress':'NOT_TESTED','real_http':'BLOCKED_BY_ADMINISTRATOR',
 'field_core_web_vitals':'NOT_MEASURED','commercial_sales':'NOT_VERIFIED'}
(out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
print(json.dumps({'contexts':count,'negative_controls':len(rejected),'receipt_sha256':sha(out/'receipt.json')},sort_keys=True))
