#!/usr/bin/env python3
"""Read-only rendered Focus-page acceptance. No form submission, cookies, or WP writes.
Offline by default; --live-readonly requires exact approved host/path.
Synthetic fixtures are never evidence of WordPress or Jetpack success.
"""
import argparse
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

APPROVED = 'https://finalvestige.com/focus/'
VIEWPORTS = ((320, 700), (360, 780), (390, 844), (768, 1024), (1440, 900))

async def inspect(page, width, height, mode):
    result = await page.evaluate('''() => {
      const visible = el => {
        if (!el) return false;
        const s=getComputedStyle(el), r=el.getBoundingClientRect();
        return s.display!=='none' && s.visibility!=='hidden' && Number(s.opacity)!==0 && r.width>0 && r.height>0;
      };
      const centerHits = el => {
        if(!visible(el)) return false;
        const r=el.getBoundingClientRect(), x=Math.max(0,Math.min(innerWidth-1,r.left+r.width/2)), y=Math.max(0,Math.min(innerHeight-1,r.top+r.height/2));
        if(r.top<0 || r.bottom>innerHeight || r.left<0 || r.right>innerWidth) return false;
        const hit=document.elementFromPoint(x,y);
        return !!hit && (hit===el || el.contains(hit));
      };
      const emails=[...document.querySelectorAll('input[type="email"]')].filter(visible);
      const forms=[...document.querySelectorAll('form')].filter(visible);
      const realForm=forms.find(f=>emails.some(e=>f.contains(e)) && [...f.querySelectorAll('button,input[type="submit"]')].some(b=>visible(b) && (b.type==='submit' || b.tagName==='BUTTON' && b.type!=='button')));
      const submit=realForm && [...realForm.querySelectorAll('button,input[type="submit"]')].find(b=>visible(b) && (b.type==='submit' || b.tagName==='BUTTON' && b.type!=='button'));
      const gift=document.querySelector('#fvf-gift');
      const fallback=[...document.querySelectorAll('.wp-block-jetpack-subscriptions a')].filter(a=>a.href.split('#')[0].split('?')[0].replace(/\\/$/,'')===location.href.split('#')[0].split('?')[0].replace(/\\/$/,''));
      return {visible_emails: emails.length, native_forms: forms.length, usable_native_form:!!realForm,
        email_hit:emails.some(centerHits), submit_hit:!!submit && centerHits(submit),
        gift_visible:visible(gift), self_link_fallback:fallback.length,
        horizontal_overflow:document.documentElement.scrollWidth>innerWidth+1,
        headings:[...document.querySelectorAll('h1')].map(x=>x.textContent.trim()).filter(Boolean).slice(0,3),
        form_action:realForm ? new URL(realForm.action||location.href).origin : null};
    }''')
    result.update(width=width,height=height,mode=mode)
    result['pass'] = bool(result['usable_native_form'] and result['email_hit'] and result['submit_hit'] and not result['gift_visible'] and not result['horizontal_overflow'])
    return result

async def run(source: str, live: bool, screenshots: str | None):
    if live:
        if source != APPROVED: raise ValueError('Live acceptance restricted to exact /focus/ URL; no arbitrary production endpoints')
    else:
        path=Path(source).resolve(strict=True)
        if path.suffix.lower() != '.html': raise ValueError('Offline input must be an HTML fixture')
        source=path.as_uri()
    records=[]
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        try:
            for js in (False,True):
                for width,height in VIEWPORTS:
                    context=await browser.new_context(viewport={'width':width,'height':height},java_script_enabled=js,service_workers='block')
                    try:
                        if not live:
                            await context.route('**/*',lambda route: route.abort())
                        if live:
                            # Fail closed against form submissions and automatic non-GET network calls.
                            await context.route('**/*',lambda route: route.continue_() if route.request.method in ('GET','HEAD') else route.abort())
                        page=await context.new_page()
                        if live:
                            await page.goto(source+'?subscribe=made_up_value',wait_until='domcontentloaded',timeout=15000)
                        else:
                            # In this sandbox file:// navigation is blocked: render exact fixture text in-memory.
                            await page.set_content(Path(source.removeprefix('file://')).read_text(),wait_until='domcontentloaded')
                        await page.wait_for_timeout(100 if js else 0)
                        record=await inspect(page,width,height,'js' if js else 'nojs')
                        records.append(record)
                        if screenshots and width in (390,1440) and js:
                            out=Path(screenshots);out.mkdir(parents=True,exist_ok=True)
                            await page.screenshot(path=str(out/f'focus_{width}_{"live" if live else "fixture"}.png'),full_page=True)
                    finally: await context.close()
        finally: await browser.close()
    return {'source_type':'live-public-render' if live else 'synthetic-fixture', 'no_form_submissions':True,
            'tests':len(records),'passed':sum(x['pass'] for x in records),'records':records,
            'warning':'Rendered DOM checks cannot independently prove Jetpack confirmation, WCAG AA, or paid conversion.'}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('source',help='Local .html fixture, or exact https://finalvestige.com/focus/ with --live-readonly')
    p.add_argument('--live-readonly',action='store_true')
    p.add_argument('--screenshots')
    p.add_argument('--out',default='focus-render-results.json')
    args=p.parse_args()
    try:
        report=asyncio.run(run(args.source,args.live_readonly,args.screenshots))
        Path(args.out).write_text(json.dumps(report,indent=2)+'\n')
        print(f"{report['source_type']}: {report['passed']}/{report['tests']} checks pass")
        raise SystemExit(0 if report['passed']==report['tests'] else 1)
    except Exception as err:
        print(f'HOLD: {type(err).__name__}: {err}')
        raise SystemExit(2)
