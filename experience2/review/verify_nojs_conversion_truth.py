#!/usr/bin/env python3
"""EX2 read-only seven-chapter no-JS meaning and conversion-path browser gate.
Pinned PHP preview plugin + WordPress callback stubs. This is NOT native WordPress,
Jetpack, axe, Lighthouse, media transfer, qualified human traffic, or release approval.
Usage: python verify_nojs_conversion_truth.py --bundle protected.zip --out evidence/
"""
import argparse
import asyncio
import hashlib
import json
import subprocess
import tempfile
import zipfile
from pathlib import Path
from playwright.async_api import async_playwright
from verify_php_playground_renderer_browser import PHP_STUB, PIN, PLUGIN

CASE_IDS = ('apollo', 'franklin', 'malbone')
CHAPTER_IDS = ('fv-hf-title','fv-hf-chronicle','fv-hf-evidence', 'fv-hf-inquiry',
               'fv-hf-method-title','fv-hf-observer','fv-hf-mind-title')

async def check_state(html, out):
    result=[]
    def record(name, verdict, observation=None):
        result.append({'check':name, 'pass':bool(verdict), 'observation':observation})
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        version=browser.version
        for width in (320,390,768,1440):
            for js in (False,True):
                tag=f'{width}/{"js" if js else "nojs"}'
                ctx=await browser.new_context(viewport={'width':width,'height':900},
                        java_script_enabled=js, reduced_motion='reduce')
                # No pretense of external image transfer: explicit off-network fixture.
                await ctx.route('**/*', lambda r:r.abort() if r.request.url.startswith(('http:','https:')) else r.continue_())
                page=await ctx.new_page(); errors=[]
                page.on('pageerror', lambda e:errors.append(str(e)))
                await page.set_content(html,wait_until='load');await page.wait_for_timeout(100)
                state=await page.evaluate('''() => {
                  const visible = e => !!e && !e.hidden && e.getClientRects().length>0 &&
                       getComputedStyle(e).visibility!=='hidden' && getComputedStyle(e).display!=='none';
                  const cases=[...document.querySelectorAll('[data-fv-case]')].map(e=>({
                    id:e.dataset.fvCase, visible:visible(e), title:e.querySelector('h3')?.textContent.trim(),
                    sources:e.querySelectorAll('a[href^="https://"]').length}));
                  const focus=[...document.querySelectorAll('a[href="https://finalvestige.com/focus/"]')];
                  const first=focus.filter(visible).map(e=>({text:e.textContent.trim(),y:e.getBoundingClientRect().top,h:e.getBoundingClientRect().height}));
                  const chapters=[...document.querySelectorAll('.fv-hf__chapter-nav a')].map(a=>({
                    hash:a.getAttribute('href'),target:!!document.querySelector(a.getAttribute('href'))}));
                  const chronicle=[...document.querySelectorAll('.fv-hf__chronicle-entry')].map(e=>({
                    visible:visible(e),text:e.textContent.trim().slice(0,110)}));
                  const observer=[...document.querySelectorAll('[data-fv-observer-frame]')].map(e=>({
                    visible:visible(e),text:e.textContent.trim().slice(0,90)}));
                  return {cases,first,chapters,chronicle,observer,
                    lensesVisible:visible(document.querySelector('[data-fv-chronicle-lens]')),
                    caseControlsVisible:visible(document.querySelector('[data-fv-case-buttons]')),
                    observerControlsVisible:visible(document.querySelector('[data-fv-observer-controls]')),
                    margins:document.querySelectorAll('.fv-margin-strip__item').length,
                    imageCount:document.querySelectorAll('[data-fv-archive-img]').length,
                    width:document.documentElement.scrollWidth}; }''')
                record(tag+'/all_chapter_links',len(state['chapters'])==7 and all(x['target'] for x in state['chapters']), state['chapters'])
                record(tag+'/72_margins',state['margins']==72,state['margins'])
                record(tag+'/two_rights_held_images',state['imageCount']==2,state['imageCount'])
                record(tag+'/focus_action_exists',len(state['first'])>=2, state['first'][:3])
                record(tag+'/overflow',state['width']<=width+2,state['width'])
                record(tag+'/no_script_error',not errors,errors)
                if not js:
                    record(tag+'/all_3_case_records_readable',
                        tuple(c['id'] for c in state['cases'])==CASE_IDS and
                        all(c['visible'] and c['title'] and c['sources'] for c in state['cases']),state['cases'])
                    record(tag+'/both_dated_entries_readable',
                        len(state['chronicle'])==2 and all(c['visible'] for c in state['chronicle']),state['chronicle'])
                    record(tag+'/both_observation_frames_readable',
                        len(state['observer'])==2 and all(c['visible'] for c in state['observer']),state['observer'])
                    record(tag+'/no_dead_enhancement_buttons',not state['lensesVisible'] and
                        not state['caseControlsVisible'] and not state['observerControlsVisible'])
                    if width==390:
                        summary=page.locator('#fv-hf-observer-answer summary')
                        await summary.click()
                        record('nojs/native_details_open',await page.locator('#fv-hf-observer-answer[open]').count()==1)
                        await page.screenshot(path=str(out/'nojs_390_details.png'))
                else:
                    record(tag+'/enhanced_case_controls',state['caseControlsVisible'])
                    record(tag+'/enhanced_chronicle_controls',state['lensesVisible'])
                    record(tag+'/enhanced_observer_controls',state['observerControlsVisible'])
                    record(tag+'/still_one_readable_case',sum(c['visible'] for c in state['cases'])==1,state['cases'])
                    if width==390:
                        for cid in CASE_IDS:
                            await page.locator(f'[data-fv-case-button="{cid}"]').click()
                            visible=await page.evaluate('''() => [...document.querySelectorAll('[data-fv-case]')].filter(e => !e.hidden).map(e=>e.dataset.fvCase)''')
                            record('js/case_switch/'+cid,visible==[cid],visible)
                        await page.screenshot(path=str(out/'js_390_case_selection.png'))
                await ctx.close()
        await browser.close()
        return version,result

def negative_controls(html):
    """Fail closed if the contract loses a genuine route or archival section."""
    import re
    probes={
      'focus_link_lost':html.replace('https://finalvestige.com/focus/','/wrong/'),
      'third_case_lost':re.sub(r'data-fv-case="malbone"','data-fv-case="missing"',html,count=1),
      'one_chapter_lost':html.replace('href="#fv-hf-mind-title"','href="#incorrect"'),
    }
    return {name:{'focus':v.count('href="https://finalvestige.com/focus/"')>=2,
      'cases':all(f'data-fv-case="{x}"' in v for x in CASE_IDS),
      'chapter':all('href="#'+c+'"' in v for c in CHAPTER_IDS)} for name,v in probes.items()}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--bundle',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(args.bundle) as z:src=z.read(PLUGIN)
    actual=hashlib.sha256(src).hexdigest()
    if actual!=PIN:raise SystemExit('HOLD: exact PHP source SHA mismatch')
    with tempfile.TemporaryDirectory(prefix='fv-nojs-') as temp:
        t=Path(temp);(t/'plugin.php').write_bytes(src);(t/'stub.php').write_text(PHP_STUB)
        cp=subprocess.run(['php',str(t/'stub.php'),str(t/'plugin.php'),str(t/'page.html')],capture_output=True,text=True)
        if cp.returncode:raise SystemExit('HOLD: PHP rendering failed: '+cp.stderr[:350])
        html=(t/'page.html').read_text()
    control=negative_controls(html)
    control_pass=(not control['focus_link_lost']['focus'] and
                  not control['third_case_lost']['cases'] and
                  not control['one_chapter_lost']['chapter'])
    version,rows=asyncio.run(check_state(html,args.out))
    output={'scope':'Exact PHP callback-rendered HTML in Chromium, not native WordPress or live website',
      'protected_php_sha256':actual,'rendered_html_sha256':hashlib.sha256(html.encode()).hexdigest(),
      'chromium':version,'checks_passed':sum(r['pass'] for r in rows),
      'checks_failed':sum(not r['pass'] for r in rows),'negative_controls':control,
      'negative_controls_passed':control_pass,'checks':rows,'decision':'HOLD',
      'missing':['native WordPress/Assembler','actual first-party archival image transfers',
                 'Jetpack confirmed leads','axe plus manual WCAG 2.2 AA','Lighthouse/field CWV',
                 'merchant-confirmed sales and revenue','CI/QD and founder approval']}
    (args.out/'results.json').write_text(json.dumps(output,indent=2))
    print(json.dumps({k:output[k] for k in ('protected_php_sha256','rendered_html_sha256','chromium','checks_passed','checks_failed','negative_controls_passed','decision')},indent=2))
    if output['checks_failed'] or not control_pass:raise SystemExit('FAIL CLOSED')
if __name__=='__main__':main()
