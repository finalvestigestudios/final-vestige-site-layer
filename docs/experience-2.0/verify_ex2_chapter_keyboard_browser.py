#!/usr/bin/env python3
"""Read-only Chromium comparison: seven chapter anchors stay fully visible on keyboard focus.

Tests the exact protected parent and a derived review bundle; cannot certify
WordPress/Assembler, axe/WCAG, archival rights, Lighthouse, or release readiness.
"""
import argparse
import asyncio
import json
import re
from pathlib import Path
from zipfile import ZipFile
from playwright.async_api import async_playwright
from apply_ex2_chapter_trail_fix import PHP_PATH,PARENT_PHP,PARENT_ZIP,digest

WIDTHS=(320,390,768,1440,1920)

def load_html(path:Path,expected_parent:bool):
    with ZipFile(path) as z:
        source=z.read(PHP_PATH)
        custody=json.loads(z.read('SOURCE_CUSTODY.json'))
        if digest(source)!=custody['files_sha256'][PHP_PATH]:
            raise ValueError('SOURCE_SHA_MISMATCH')
        if expected_parent and (digest(path.read_bytes())!=PARENT_ZIP or digest(source)!=PARENT_PHP):
            raise ValueError('PARENT_SOURCE_DRIFT')
        if not expected_parent and (
            custody.get('parent_php_sha256')!=PARENT_PHP or
            custody.get('native_wordpress_tested') is not False or
            custody.get('release_authorized') is not False or
            custody.get('derived_review_patch')!='chapter-trail-keyboard-focus-2026-11-07'):
            raise ValueError('UNATTESTED_DERIVED_SOURCE')
        plugin=source.decode('utf-8')
    out={}
    for key in ('HTML','CSS','JS'):
        found=re.search(r"<<<'FVPG_"+key+r"_END'\n(.*?)\nFVPG_"+key+r"_END",plugin,re.S)
        if not found: raise ValueError('PLUGIN_HEREDOC_MISSING_'+key)
        out[key]=found.group(1)
    if out['HTML'].count('class="fv-margin-strip__item"')!=72:
        raise ValueError('MARGINS_DRIFT')
    if out['HTML'].count('href="https://finalvestige.com/focus/"')!=5:
        raise ValueError('FOCUS_LINK_DRIFT')
    if 'ARCHIVAL REFERENCE · IMAGE NOT REPRODUCED' not in out['HTML']:
        raise ValueError('NYPL_RIGHTS_RESTRICTION_REMOVED')
    return ('<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<style>'+out['CSS']+'</style></head><body>'+out['HTML']+'<script>'+out['JS']+'</script></body></html>')

AUDIT_JS=r'''() => {
  const link=document.activeElement;
  const nav=link.closest('.fv-hf__chapter-nav');
  if (!nav) return null;
  const r=link.getBoundingClientRect();
  const cx=r.left+r.width/2,cy=r.top+r.height/2;
  const center=document.elementFromPoint(cx,cy);
  return {label:(link.textContent||'').trim().replace(/\s+/g,' ').slice(0,65),
    fully_visible:r.left>=0&&r.right<=innerWidth&&r.top>=0&&r.bottom<=innerHeight,
    center_targetable:center===link||link.contains(center),
    focus_visible:link.matches(':focus-visible'),
    rect:[Math.round(r.left),Math.round(r.right)],scroll_left:nav.scrollLeft};
}'''

async def audit(source:Path,out:Path,parent:bool):
    html=load_html(source,parent)
    out.mkdir(parents=True,exist_ok=True)
    results=[]
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        try:
            for width in WIDTHS:
                for js in (False,True):
                  for zoom in ((1,2) if width in (320,390) and js else (1,)):
                    page=await browser.new_page(viewport={'width':width,'height':900},java_script_enabled=js,reduced_motion='reduce')
                    requests=[]
                    async def block(route):
                        requests.append(route.request.url)
                        await route.abort()
                    await page.route('**/*',block)
                    errors=[]
                    page.on('pageerror',lambda error:errors.append(str(error)))
                    await page.set_content(html)
                    if zoom==2: await page.evaluate('document.documentElement.style.zoom="2"')
                    focused=[]
                    for _ in range(85):
                        await page.keyboard.press('Tab')
                        item=await page.evaluate(AUDIT_JS)
                        if item is not None: focused.append(item)
                        if await page.evaluate('document.activeElement===document.body'): break
                    await page.evaluate('window.scrollTo(0,0)')
                    data=await page.evaluate(r'''() => {
                      const nav=document.querySelector('.fv-hf__chapter-nav');
                      const links=[...document.querySelectorAll('a[href="https://finalvestige.com/focus/"]')];
                      const hit=el=>{const r=el.getBoundingClientRect(),t=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);
                        return r.top>=0&&r.bottom<=innerHeight&&r.left>=0&&r.right<=innerWidth&&(t===el||el.contains(t))};
                      return {chapter_links:nav.querySelectorAll('a[href^="#fv-hf-"]').length,
                        nav_height:Math.round(nav.getBoundingClientRect().height),
                        margins:document.querySelectorAll('.fv-margin-strip__item').length,
                        focus_paths:links.length,firstscreen_focus:links.filter(hit).length,
                        overflow:document.documentElement.scrollWidth>innerWidth+1};}''')
                    bad=[x for x in focused if not(x['fully_visible'] and x['center_targetable'] and x['focus_visible'])]
                    results.append({'width':width,'javascript':js,'zoom':zoom,
                        'chapter_tabbable':len(focused),'bad_focus':bad,'bad_count':len(bad),
                        **data,'uncaught_errors':errors,'blocked_requests':len(requests)})
                    if width==390 and zoom==1:
                        await page.set_content(html)
                        await page.screenshot(path=str(out/f'{"parent" if parent else "patched"}_390_{"js" if js else "nojs"}.png'))
                    await page.close()
        finally:
            await browser.close()
    return results

def valid(records,expect_fix):
    stable=all(r['chapter_tabbable']==7 and r['chapter_links']==7 and
        r['margins']==72 and r['focus_paths']==5 and
        (r['firstscreen_focus']>=1 if r['zoom']==1 else True) and
        not r['overflow'] and not r['uncaught_errors'] for r in records)
    failing=any(r['bad_count']>0 for r in records)
    return stable and (not failing if expect_fix else failing)

async def main(a):
    before=await audit(a.parent,a.out,True)
    after=await audit(a.patched,a.out,False)
    report={'scope':'OFFLINE PROTECTED PHP PAYLOAD; NOT WordPress/Assembler',
       'parent_zip_sha256':digest(a.parent.read_bytes()),
       'patched_zip_sha256':digest(a.patched.read_bytes()),
       'configs':len(before)+len(after),'parent_bad':sum(r['bad_count'] for r in before),
       'patched_bad':sum(r['bad_count'] for r in after),
       'parent_expected_fail':valid(before,False),'patched_pass':valid(after,True),
       'before':before,'after':after,'release':'HOLD',
       'wordpress_assembler_tested':False,'axe_tested':False,'lighthouse_tested':False}
    (a.out/'chapter_keyboard_evidence.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('configs','parent_bad','patched_bad','parent_expected_fail','patched_pass','release')},indent=2))
    return 0 if report['parent_expected_fail'] and report['patched_pass'] else 1

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parent',type=Path,required=True)
    parser.add_argument('--patched',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    raise SystemExit(asyncio.run(main(parser.parse_args())))
