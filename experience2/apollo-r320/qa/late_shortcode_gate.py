#!/usr/bin/env python3
"""R320 locally reproducible lifecycle and Chromium QA. Fixture, NOT WP or axe acceptance."""
import hashlib, json, os, re, subprocess, tempfile
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
PHP=ROOT/'apollo-r281/apollo-source-experience.php'
JS=ROOT/'apollo-r281/assets/apollo-cache-continuation.js'
CSS=ROOT/'apollo-r281/assets/apollo-source-experience.css'
FIX=ROOT/'apollo-r320/qa/wp_late_shortcodes.php'
OUT=ROOT/'apollo-r320/QA'
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
QUERY='utm_source=youtube&utm_medium=organic_social&utm_campaign=history_pilot_2026_11&utm_content=apollo1_yt_longform001'
def blob(b): return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def render(case='late-dynamic',source=None):
    env=os.environ.copy()
    if source: env['APOLLO_R320_PHP']=str(source)
    raw=subprocess.check_output(['php',str(FIX),case,'2'],text=True,env=env)
    m=re.search(r'<!--R320_QUEUE:(.*?)-->',raw)
    assert m,case
    return raw[:m.start()],json.loads(m.group(1))
def main():
    subprocess.run(['php','-l',str(PHP)],check=True,stdout=subprocess.DEVNULL)
    subprocess.run(['php','-l',str(FIX)],check=True,stdout=subprocess.DEVNULL)
    subprocess.run(['node','--check',str(JS)],check=True,stdout=subprocess.DEVNULL)
    assert blob(JS.read_bytes())=='a3c858b51005495ebebb326086badc155c1b7e5a'
    checks=[]
    for case,calls in [('preflight-hit',1),('late-dynamic',1),('already-queued',0),
                       ('footer-closed',0),('admin',0),('feed',0)]:
        html,q=render(case)
        assert q['calls']==calls,(case,q)
        assert len(q['scripts'])==(0 if case in ('footer-closed','admin','feed') else 1)
        assert html.count('data-fv-experience="apollo-1"')==2
        assert html.count('data-fv-cta="apollo-read-free-investigation"')==2
        assert html.count('data-fv-media-record=')==8
        assert 'utm_campaign' not in html and 'utm_content' not in html
        assert 'apollo-cache-continuation.js' not in html
        if case=='preflight-hit':
            assert len(q['styles'])==1 and '<link rel="stylesheet"' not in html
        else:
            assert len(q['styles'])==0 and html.count('<link rel="stylesheet"')==1
        checks.append({'case':case,'enqueue_calls':calls,'pass':True})
    source=PHP.read_text()
    assert source.count('    fv_r320_late_shortcode_script();')==1
    # Actual R319 regression: remove only the new R320 helper/call from the
    # reviewed PHP. The real old blob must match before using it as a control.
    start=source.index('/**\n * R320: WordPress may discover')
    end=source.index('/** No user content',start)
    old=source[:start]+source[end:]
    start=old.index('    // The normal wp_head preflight can miss')
    end=old.index('    static $sequence=0, $linked=false;',start)
    old=old[:start]+old[end:]
    assert blob(old.encode())=='9ff32d45b7e957e1d25724ab5fc55c467aaa55e2'
    with tempfile.TemporaryDirectory() as tmp:
        prior=Path(tmp)/'r319.php';prior.write_text(old)
        _,control=render('late-dynamic',prior)
        assert control['calls']==0 and not control['scripts']
    html,_=render('late-dynamic')
    html=html.replace('</head>','<style>'+CSS.read_text()+'</style></head>')
    results=[];perf=[];errors=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in (320,360,390,768,1024,1440,1920):
            for mode in ('js','nojs','forced'):
                enabled=mode!='nojs'
                ctx=browser.new_context(viewport={'width':width,'height':900},
                    java_script_enabled=enabled,has_touch=width<=390,
                    reduced_motion='reduce',forced_colors='active' if mode=='forced' else 'none')
                page=ctx.new_page()
                page.on('pageerror',lambda err:errors.append(str(err)))
                page.goto('about:blank?'+QUERY)
                page.set_content(html)
                if enabled: page.add_script_tag(content=JS.read_text())
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(width,mode)
                cta=page.locator('section.fv-r281 a[data-fv-cta]').first
                cta.focus();page.keyboard.press('Shift+F10')
                href=cta.get_attribute('href')
                assert dict(parse_qsl(urlsplit(href).query))==dict(parse_qsl(QUERY)) if enabled else href==FREE
                assert page.locator('section.fv-r281 a[data-fv-cta]').nth(1).get_attribute('href')==FREE
                link=page.locator('section.fv-r281 .fv-r281__source-jump a').first
                link.click()
                target=page.locator(page.evaluate('location.hash'))
                assert target.count()==1 and target.is_visible()
                assert target.evaluate('(x)=>x===document.activeElement')
                if mode=='js':
                    page.evaluate("""() => {
                        window.fvcls=0;window.fvlcp=null;
                        new PerformanceObserver(list=>{for(const e of list.getEntries())if(!e.hadRecentInput)fvcls+=e.value})
                          .observe({type:'layout-shift',buffered:true});
                        new PerformanceObserver(list=>{for(const e of list.getEntries())fvlcp=e.startTime})
                          .observe({type:'largest-contentful-paint',buffered:true});
                    }""")
                    page.wait_for_timeout(80)
                    result=page.evaluate('({lcp:fvlcp,cls:fvcls})')
                    assert result['cls']<=0.1
                    perf.append({'width':width,**result})
                if width in (390,1440) and mode in ('js','nojs'):
                    OUT.mkdir(parents=True,exist_ok=True)
                    page.screenshot(path=str(OUT/f'r320-{width}-{mode}-late.png'),full_page=True,animations='disabled')
                results.append({'width':width,'mode':mode,'pass':True})
                ctx.close()
        browser.close()
    assert not errors,errors
    OUT.mkdir(parents=True,exist_ok=True)
    receipt={'php_lifecycle':checks,'r319_negative':'PASS: missed late enqueue reproduced',
      'chromium_contexts':results,'count':len(results),'performance_offline_fixture_only':perf,
      'source_git_blob':blob(PHP.read_bytes()),'javascript_git_blob':blob(JS.read_bytes()),
      'axe_core':'NOT RUN','installed_WordPress':'NOT VERIFIED','native_browser_http':'NOT VERIFIED',
      'paid_orders':'NOT OBSERVED','production_release':'HARD HOLD'}
    (OUT/'r320-qa-receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print('PASS: 6 PHP lifecycle cases; R319 negative; 21 offline Chromium contexts')
if __name__=='__main__': main()
