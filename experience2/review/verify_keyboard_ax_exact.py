#!/usr/bin/env python3
"""Independent EX2 keyboard/touch/accessibility-tree acceptance on pinned PHP output.
Not WordPress core, axe WCAG certification, live media, Lighthouse, or release approval.
Requires the sibling verify_php_playground_renderer_browser.py from PR #1562.
Usage: python verify_keyboard_ax_exact.py --bundle PRIVATE.zip --out evidence-dir
"""
import argparse, asyncio, hashlib, json, subprocess, tempfile, zipfile
from pathlib import Path
from html.parser import HTMLParser
from playwright.async_api import async_playwright
from verify_php_playground_renderer_browser import PHP_STUB, PLUGIN, PIN

CHAPTERS=('fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry',
          'fv-hf-method-title','fv-hf-observer','fv-hf-mind-title')

class Contract(HTMLParser):
    def __init__(self):super().__init__();self.anchors=[];self.archive=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='a':self.anchors.append(d.get('href',''))
        if tag=='img' and 'data-fv-archive-img' in d:self.archive.append(d.get('alt',''))
    def valid(self):return (all('#'+i in self.anchors for i in CHAPTERS)
      and 'https://finalvestige.com/focus/' in self.anchors
      and len(self.archive)==2 and all(self.archive))

def contract(raw):
    p=Contract();p.feed(raw);return p.valid()

def negative_controls(raw):
    import re
    probes={
      'focus_removed':raw.replace('https://finalvestige.com/focus/','/invalid/'),
      'chapter_broken':raw.replace('href="#fv-hf-title"','href="#broken"'),
      'archival_alt_removed':re.sub(r'alt="Apollo 1 astronauts[^"]*"','alt=""',raw,count=1),
    }
    return {key:not contract(value) for key,value in probes.items()}

def add(rows,name,pass_condition,detail=None):
    row={'name':name,'pass':bool(pass_condition)}
    if detail is not None:row['detail']=detail
    rows.append(row)

async def browser_checks(raw,out):
    rows=[]
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        version=browser.version
        for width in (320,390,768,1440):
            for enabled in (True,False):
                tag=f'{width}/'+('js' if enabled else 'nojs')
                context=await browser.new_context(viewport={'width':width,'height':850},
                              java_script_enabled=enabled,reduced_motion='reduce')
                # External image responses blocked: never count metadata as transferred bytes.
                await context.route('**/*',lambda r:r.abort() if r.request.url.startswith(('http:','https:')) else r.continue_())
                page=await context.new_page();errors=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                await page.set_content(raw,wait_until='load');await page.wait_for_timeout(90)
                state=await page.evaluate('''() => ({width:innerWidth,scroll:document.documentElement.scrollWidth,
                  ids:[...document.querySelectorAll('.fv-hf__chapter-nav a')].map(a=>a.getAttribute('href')?.slice(1)),
                  margins:document.querySelectorAll('.fv-margin-strip__item').length,
                  images:[...document.querySelectorAll('img[data-fv-archive-img]')].map(i=>i.alt),
                  focus:!!document.querySelector('a[href="https://finalvestige.com/focus/"]'),
                  reduced:matchMedia('(prefers-reduced-motion: reduce)').matches})''')
                add(rows,tag+'/overflow',state['scroll']<=width+2,state['scroll'])
                add(rows,tag+'/chapters',state['ids']==list(CHAPTERS))
                add(rows,tag+'/margins',state['margins']==72)
                add(rows,tag+'/focus',state['focus'])
                add(rows,tag+'/archive_alt',len(state['images'])==2 and all(state['images']))
                add(rows,tag+'/reduced_motion',state['reduced'])
                add(rows,tag+'/no_js_exception',not errors,errors)
                client=await context.new_cdp_session(page)
                nodes=(await client.send('Accessibility.getFullAXTree'))['nodes']
                relevant=[n for n in nodes if not n.get('ignored') and
                     n.get('role',{}).get('value') in ('button','link','switch','slider','tab','checkbox')]
                unnamed=[n.get('role',{}).get('value') for n in relevant
                         if not n.get('name',{}).get('value','').strip()]
                add(rows,tag+'/accessible_names',len(relevant)>=10 and not unnamed,
                    {'exposed':len(relevant),'unnamed':unnamed})
                for ident in CHAPTERS:
                    link=page.locator(f'.fv-hf__chapter-nav a[href="#{ident}"]')
                    await link.focus();await page.keyboard.press('Enter');await page.wait_for_timeout(40)
                    target=await page.evaluate('''i => {let e=document.getElementById(i),r=e.getBoundingClientRect();
                      return {hash:location.hash,focused:document.activeElement===e,top:r.top,bottom:r.bottom}}''',ident)
                    add(rows,tag+'/keyboard_nav/'+ident,
                        target['hash']=='#'+ident and target['focused'] and target['bottom']>45 and target['top']<850,target)
                if width==390:
                    if enabled:
                        for selector in ('[data-fv-case-button="franklin"]',
                                         '[data-fv-chronicle-view="addition"]',
                                         '[data-fv-observer-switch="b"]'):
                            el=page.locator(selector)
                            await el.focus();await page.keyboard.press('Enter')
                            add(rows,tag+'/keyboard_toggle/'+selector,
                                await el.get_attribute('aria-pressed')=='true')
                    else:add(rows,tag+'/nojs_three_cases',await page.locator('[data-fv-case]').count()==3)
                    await page.screenshot(path=str(out/f'chapter_{tag.replace("/","_")}.png'))
                await context.close()
        touch=await browser.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True)
        await touch.route('**/*',lambda r:r.abort() if r.request.url.startswith(('http:','https:')) else r.continue_())
        page=await touch.new_page();await page.set_content(raw,wait_until='load')
        for selector in ('[data-fv-case-button="franklin"]','[data-fv-chronicle-view="addition"]',
                         '[data-fv-observer-switch="b"]'):
            el=page.locator(selector);await el.tap()
            add(rows,'touch/'+selector,await el.get_attribute('aria-pressed')=='true')
        await page.screenshot(path=str(out/'touch_390.png'))
        await touch.close()
        zoom=await browser.new_page(viewport={'width':390,'height':844})
        await zoom.set_content(raw,wait_until='load')
        for z in (1,2):
            await zoom.evaluate('(x)=>document.documentElement.style.zoom=x',z)
            result=await zoom.evaluate('''() => ({w:innerWidth,scroll:document.documentElement.scrollWidth,
              undersized:[...document.querySelectorAll('.fv-hf a[href],.fv-hf button,.fv-hf summary')]
                .filter(e=>{let r=e.getBoundingClientRect(),s=getComputedStyle(e);return
                  r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden'
                  &&(r.width<24||r.height<24)}).map(e=>e.outerHTML.slice(0,90))})''')
            add(rows,f'css_zoom{z}00/no_overflow',result['scroll']<=result['w']+2,result)
            add(rows,f'css_zoom{z}00/target_min_24',not result['undersized'],result['undersized'])
            await zoom.screenshot(path=str(out/f'css_zoom{z}00_390.png'))
        await browser.close()
    return version,rows

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--bundle',required=True,type=Path)
    ap.add_argument('--out',required=True,type=Path);args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(args.bundle) as z:source=z.read(PLUGIN)
    source_sha=hashlib.sha256(source).hexdigest()
    if source_sha!=PIN:raise SystemExit('HOLD: renderer source SHA mismatch')
    with tempfile.TemporaryDirectory() as d:
        d=Path(d);(d/'source.php').write_bytes(source);(d/'stub.php').write_text(PHP_STUB)
        p=subprocess.run(['php',str(d/'stub.php'),str(d/'source.php'),str(d/'result.html')],capture_output=True,text=True)
        if p.returncode:raise SystemExit('HOLD: PHP renderer failure: '+p.stderr[:500])
        html=(d/'result.html').read_text()
    mutations=negative_controls(html)
    version,rows=asyncio.run(browser_checks(html,args.out))
    result={'scope':'Exact pinned PHP output / WordPress-function stubs / real Chromium accessibility tree. Not WP core.',
      'source_sha256':source_sha,'rendered_sha256':hashlib.sha256(html.encode()).hexdigest(),
      'chromium':version,'passed':sum(r['pass'] for r in rows),'failed':sum(not r['pass'] for r in rows),
      'negative_controls':mutations,'checks':rows,'release':'HOLD',
      'still_unverified':['WordPress core/Assembler','axe WCAG 2.2 AA','real media bytes',
        'hosted Lighthouse/CWV','Jetpack signup','realized net revenue','CI/QD/founder approval']}
    (args.out/'results.json').write_text(json.dumps(result,indent=2))
    print(json.dumps({k:result[k] for k in ('source_sha256','rendered_sha256','chromium','passed','failed','negative_controls','release')},indent=2))
    if result['failed'] or not all(mutations.values()):raise SystemExit(1)
if __name__=='__main__':main()
