#!/usr/bin/env python3
"""Fail-closed offline QA of PR #1601 CSS rebuilt in a real private PHP shortcode.

PHP executes with WordPress function *stubs*. Chromium is real, but this is not
WordPress Core, the Assembler theme, Jetpack, or production staging.
"""
import argparse
import asyncio
import hashlib
import io
import json
import runpy
import subprocess
import tempfile
import zipfile
from pathlib import Path
from playwright.async_api import async_playwright
from rebuild_playground_short_phone import build, sha, PLUGIN, PARENT_PLUGIN_SHA256

CASES = [(320,568),(360,640),(390,667),(768,1024),(1440,900),(1920,1080)]


def render(data, stub):
    with tempfile.TemporaryDirectory(prefix='fv-ex2-stub-') as folder:
        path=Path(folder)
        source=path/'plugin.php';source.write_bytes(data)
        bootstrap=path/'bootstrap.php';bootstrap.write_text(stub)
        html=path/'test.html'
        proc=subprocess.run(['php',str(bootstrap),str(source),str(html)],capture_output=True,text=True)
        if proc.returncode: raise RuntimeError(proc.stderr or proc.stdout)
        return html.read_text(), json.loads(proc.stdout)


async def browser_accept(old, new, out):
    checks=[];captures=[]
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        version=browser.version
        for width,height in CASES:
            for js in (True,False):
                snapshots=[]
                for label,html in (('before',old),('after',new)):
                    ctx=await browser.new_context(viewport={'width':width,'height':height},java_script_enabled=js,reduced_motion='reduce')
                    await ctx.route('**/*',lambda route:route.abort() if route.request.url.startswith(('https:','http:')) else route.continue_())
                    page=await ctx.new_page();errors=[]
                    page.on('pageerror',lambda error:errors.append(str(error)))
                    await page.set_content(html,wait_until='load');await page.wait_for_timeout(90)
                    state=await page.evaluate('''() => {
                      const el=document.querySelector('.fv-hf__opening-actions .fv-hf__button');
                      const r=el?.getBoundingClientRect();
                      return {cta:r&&{top:Math.round(r.top),bottom:Math.round(r.bottom)},
                      focus:!!document.querySelector('.fv-hf__text-link--focus'),
                      headerFocus:!!document.querySelector('.fv-hf__mast-cta'),
                      width:innerWidth,scroll:document.documentElement.scrollWidth,
                      chapterAnchors:[...document.querySelectorAll('.fv-hf__chapter-nav a')].every(a=>document.querySelector(a.getAttribute('href'))!==null),
                      chapters:document.querySelectorAll('.fv-hf__chapter-nav a').length,
                      margins:document.querySelectorAll('.fv-margin-strip__item').length,
                      archives:document.querySelectorAll('[data-fv-archive-img]').length,
                      deltaCSS:([...document.querySelectorAll('style')].some(s=>s.textContent.includes('compact short-phone first-screen composition'))),
                      noScript:document.querySelectorAll('noscript').length};}''')
                    state['errors']=errors;state['label']=label;snapshots.append(state)
                    if width in (320,360,390,1440) and (width not in (320,360) or js):
                        target=out/f'{label}_{width}x{height}_{"js" if js else "nojs"}.png'
                        await page.screenshot(path=str(target));captures.append(str(target.name))
                    await ctx.close()
                a,b=snapshots
                key=f'{width}x{height}/{"js" if js else "nojs"}'
                def check(k,passed,detail=None):checks.append({'name':key+'/'+k,'pass':bool(passed),'detail':detail})
                check('new_css_wired_into_real_php',not a['deltaCSS'] and b['deltaCSS'])
                check('no_document_overflow',b['scroll']<=width+2,{'scroll':b['scroll']})
                check('7_chapters_72_margins',b['chapters']==7 and b['chapterAnchors'] and b['margins']==72)
                check('keep_focus_and_rights_hold',b['focus'] and b['headerFocus'] and b['archives']==2)
                check('no_js_errors',not b['errors'],b['errors'])
                if width<=360:
                    check('cta_original_below_fold',a['cta']['bottom']>height if width==320 else a['cta']['top']>b['cta']['top'],a['cta'])
                    check('cta_new_fully_in_first_screen',b['cta']['bottom']<=height and b['cta']['top']>=0,b['cta'])
                    check('cta_shift_at_least_45px',a['cta']['top']-b['cta']['top']>=45,
                          {'old':a['cta']['top'],'new':b['cta']['top']})
                else:
                    check('non_target_no_cta_shift',abs(a['cta']['top']-b['cta']['top'])<=1,
                          {'old':a['cta']['top'],'new':b['cta']['top']})
                check('no_extra_scripts',b['noScript']==a['noScript'])
        await browser.close()
    return version,checks,captures


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--parent',required=True,type=Path)
    ap.add_argument('--delta',required=True,type=Path)
    ap.add_argument('--out',required=True,type=Path)
    ap.add_argument('--runner',required=True,type=Path,
                    help='Existing source-controlled verify_php_playground_renderer_browser.py')
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    parent=args.parent.read_bytes();delta=args.delta.read_bytes()
    rebuilt,receipt=build(parent,delta)
    if rebuilt!=build(parent,delta)[0]:raise RuntimeError('Non-deterministic ZIP')
    with zipfile.ZipFile(io.BytesIO(parent)) as z:old_plugin=z.read(PLUGIN)
    with zipfile.ZipFile(io.BytesIO(rebuilt)) as z:new_plugin=z.read(PLUGIN)
    assert sha(old_plugin)==PARENT_PLUGIN_SHA256
    bad=[]
    for label,par,css in [('tampered parent',parent+b'\n',delta),('tampered CSS',parent,delta+b'X')]:
        try:build(par,css)
        except ValueError:bad.append(label)
        else:raise RuntimeError('Fail-open negative control: '+label)
    for plugin,label in [(old_plugin,'old'),(new_plugin,'new')]:
        tmp=args.out/(label+'.php');tmp.write_bytes(plugin)
        proc=subprocess.run(['php','-l',str(tmp)],capture_output=True,text=True)
        if proc.returncode:raise RuntimeError('PHP lint failure: '+proc.stderr)
        tmp.unlink()
    runner=runpy.run_path(str(args.runner));stub=runner['PHP_STUB']
    old_html,old_meta=render(old_plugin,stub)
    new_html,new_meta=render(new_plugin,stub)
    for new_host in ['https://finalvestige.com/','https://wpsandbox.wordpress.net.evil/']:
        dangerous=stub.replace('http://localhost:9913/',new_host)
        try:render(new_plugin,dangerous)
        except RuntimeError:bad.append('host blocked:'+new_host)
        else:raise RuntimeError('Fail-open public host guard: '+new_host)
    prod=stub.replace("define('WP_ENVIRONMENT_TYPE', 'development');","define('WP_ENVIRONMENT_TYPE', 'production');")
    try:render(new_plugin,prod)
    except RuntimeError:bad.append('explicit production blocked')
    else:raise RuntimeError('Fail-open WP_ENVIRONMENT_TYPE gate')
    chromium,checks,captures=asyncio.run(browser_accept(old_html,new_html,args.out))
    results={'scope':'OFFLINE actual PHP shortcode with WP stubs + real Chromium, NOT native WordPress staging',
             'builder_receipt':receipt,'renderer_html_sha256_before':sha(old_html.encode()),
             'renderer_html_sha256_after':sha(new_html.encode()),
             'chromium':chromium,'tests_passed':sum(c['pass'] for c in checks),
             'tests_failed':sum(not c['pass'] for c in checks),
             'negative_controls_rejected':bad,'checks':checks,'screenshots':captures,
             'hold':['WordPress core and Assembler not executed','Image network transfers not verified',
                     'Jetpack signup not verified','axe/manual WCAG 2.2 AA unverified',
                     'Lighthouse and field CWV unmeasured','independent CI/QD and founder approval absent']}
    (args.out/'verification.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps({k:results[k] for k in ('chromium','tests_passed','tests_failed','negative_controls_rejected','screenshots')},indent=2))
    if results['tests_failed']:raise SystemExit('HOLD: browser acceptance failed')

if __name__ == '__main__':main()
