#!/usr/bin/env python3
"""Fail-closed FV image-transfer acceptance. Never writes to WordPress.
Fixture mode proves the browser probe works; it is NOT a live-media pass.
Staging mode requires an isolated, authorized localhost/Playground origin.
"""
import argparse, asyncio, hashlib, io, json, re, sys
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image
from playwright.async_api import async_playwright

SOURCE = 'FV_EX2_MEDIA_TRANSFER_GATE_V1'
WIDTHS = (320,390,768,1440,1920)
EXPECTED = ('s67-19766.webp','Franklinexpeditionnote.jpg')

def authorized(url):
    host = urlparse(url).hostname or ''
    return host in ('localhost','127.0.0.1','wpsandbox.wordpress.net') or host.endswith('.localhost')

def png(width=840, height=570):
    im=Image.new('RGB',(width,height)); px=im.load()
    for y in range(height):
        for x in range(width): px[x,y]=((x*19+y*7)%256,(x*3+y*11)%256,(x*5+y*17)%256)
    b=io.BytesIO(); im.save(b,format='PNG'); return b.getvalue()

def magic_matches(blob,mime):
    kind=mime.split(';')[0].lower().strip()
    return ((kind=='image/png' and blob.startswith(b'\x89PNG\r\n\x1a\n')) or
            (kind=='image/jpeg' and blob.startswith(b'\xff\xd8\xff')) or
            (kind=='image/webp' and blob[:4]==b'RIFF' and blob[8:12]==b'WEBP'))

def name_for(url):
    u=url.lower()
    if 's67-19766.webp' in u: return EXPECTED[0]
    if 'franklinexpeditionnote.jpg' in u: return EXPECTED[1]
    return None

async def check(page, scheme, fixture):
    responses={}; tasks=[]; seen=[]
    async def collect(resp):
        name=name_for(resp.url)
        if not name:return
        try: blob=await resp.body()
        except Exception: blob=b''
        responses[name]={'status':resp.status,'mime':resp.headers.get('content-type',''),
                         'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest() if blob else None,
                         'magic':magic_matches(blob,resp.headers.get('content-type',''))}
        seen.append(name)
    page.on('response',lambda resp:tasks.append(asyncio.create_task(collect(resp))))
    if fixture:
        proper=png(); tiny=png(1,1)
        async def intercept(route):
            name=name_for(route.request.url)
            if not name:return await route.abort()
            if scheme=='missing':return await route.abort()
            if scheme=='empty':return await route.fulfill(status=200,body=b'',content_type='image/png')
            if scheme=='html':return await route.fulfill(status=200,body=b'<html>broken</html>',content_type='text/html')
            if scheme=='corrupt':return await route.fulfill(status=200,body=b'not an image',content_type='image/png')
            if scheme=='tiny':return await route.fulfill(status=200,body=tiny,content_type='image/png')
            return await route.fulfill(status=200,body=proper,content_type='image/png')
        await page.route('**/*',intercept)
        content=Path(fixture).read_text()
        if scheme=='foreign':
            from bs4 import BeautifulSoup
            soup=BeautifulSoup(content,'html.parser')
            img=soup.find('img',src=re.compile('s67-19766'))
            img['src']='https://untrusted.example/s67-19766.webp'
            img['srcset']='https://untrusted.example/s67-19766.webp 840w'
            content=str(soup)
        await page.set_content(content,wait_until='domcontentloaded')
    else: await page.goto(scheme,wait_until='domcontentloaded',timeout=25000)
    imgs=page.locator('img[data-fv-archive-img]')
    count=await imgs.count()
    # Force retrieval of inactive-case images to catch hidden broken artwork.
    await page.evaluate('''() => document.querySelectorAll("img[data-fv-archive-img]").forEach(i=>{i.loading="eager";i.style.display="block"})''')
    for i in range(count):
        try:await imgs.nth(i).evaluate('(img)=>img.decode()',timeout=8000)
        except Exception:pass
    await page.wait_for_timeout(200)
    if tasks:await asyncio.gather(*tasks,return_exceptions=True)
    records=[]
    for i in range(count):
        info=await imgs.nth(i).evaluate('''i=>({src:i.currentSrc,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight,alt:i.alt,complete:i.complete})''')
        name=name_for(info['src']); net=responses.get(name or '',{})
        h=urlparse(info['src']).hostname or ''
        origin_ok=(h=='finalvestige.com' or (h=='i0.wp.com' and '/finalvestige.com/wp-content/uploads/' in info['src']))
        if not fixture: origin_ok=origin_ok or h==urlparse(scheme).hostname
        passed=(name in EXPECTED and origin_ok and bool(info['alt']) and info['complete'] and
                info['naturalWidth']>=256 and info['naturalHeight']>=128 and
                net.get('status')==200 and net.get('magic') and net.get('bytes',0)>=1000)
        records.append({'image':name,'source_host':h,'alt_present':bool(info['alt']),
                        'pixels':[info['naturalWidth'],info['naturalHeight']],**net,'pass':bool(passed)})
    return {'passed':count==2 and len({r['image'] for r in records})==2 and all(r['pass'] for r in records),
            'images':records,'image_count':count,'network_events':len(seen)}

async def run(args):
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        tests=[]
        for width in WIDTHS:
            for js in (True,False):
                context=await browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,reduced_motion='reduce')
                page=await context.new_page()
                result=await check(page, 'good' if args.fixture else args.url,args.fixture)
                tests.append({'case':'media_happy_path','width':width,'js':js,**result})
                if width==390 and js:await page.screenshot(path=str(out/'fixture_390.png'))
                await context.close()
        if args.fixture:
            for invalid in ('missing','empty','html','corrupt','tiny','foreign'):
                context=await browser.new_context(viewport={'width':390,'height':900})
                page=await context.new_page();result=await check(page,invalid,args.fixture)
                tests.append({'case':'negative_'+invalid,'width':390,'js':True,**result})
                await context.close()
        await browser.close()
    positives=[t for t in tests if t['case']=='media_happy_path']
    negatives=[t for t in tests if t['case'].startswith('negative_')]
    fixture_ok=bool(positives) and all(t['passed'] for t in positives) and all(not t['passed'] for t in negatives)
    report={'runner':SOURCE,'mode':'SYNTHETIC_FIXTURE' if args.fixture else 'ISOLATED_STAGING',
            'is_real_archival_media_transfer':not bool(args.fixture),'positive':sum(t['passed'] for t in positives),
            'positive_total':len(positives),'rejected_negative_controls':sum(not t['passed'] for t in negatives),
            'negative_total':len(negatives),'gate':'FIXTURE_PASS_RELEASE_HOLD' if fixture_ok and args.fixture else
                    'STAGING_MEDIA_PASS_OTHER_GATES_HOLD' if fixture_ok else 'FAIL_CLOSED',
            'tests':tests,'outstanding':['true WordPress/Assembler staging','production image transfer bytes','rights derivative review','axe/manual WCAG','Lighthouse/CWV','Jetpack verified lead','merchant paid conversion','CI/QD/founder approval']}
    (out/'media_gate.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:report[k] for k in ('mode','positive','positive_total','rejected_negative_controls','negative_total','gate')}))
    if not fixture_ok:sys.exit(2)

def main():
    p=argparse.ArgumentParser();p.add_argument('--fixture');p.add_argument('--url');p.add_argument('--out',default='media_evidence')
    a=p.parse_args()
    if bool(a.fixture)==bool(a.url):p.error('Supply exactly one of --fixture (synthetic only) or --url (staging)')
    if a.url and not authorized(a.url):p.error('FAIL CLOSED: only isolated localhost or exact official WP Playground sandbox is permitted')
    asyncio.run(run(a))
if __name__=='__main__':main()
