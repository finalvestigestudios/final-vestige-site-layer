#!/usr/bin/env python3
"""Fail-closed actual WordPress Playground/Assembler admission; NEVER test production.
Run only against a separately launched local/Playground URL with explicit axe-core JS.
No URL is assumed and unavailable axe, HTTP, image transfers or browser tests are failures.
"""
import argparse, json, shutil
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
from integrated_admission_checks import (
    validate_stage_url, read_trusted_media_manifest,
    verify_integrated_dom, verify_media_payload)
from archive_gallery_transfer import audit_archive_gallery
from browser_consumed_media import BrowserEvidencePage


WIDTHS=(320,360,390,768,1024,1440,1920)
MEDIA={'apollo.webp':(78346,1041,810),'franklin.jpg':(466043,960,1526),'nypl.jpg':(5553669,5667,3831)}
def require(flag,reason):
    if not flag: raise RuntimeError('PLAYGROUND ADMISSION CLOSED: '+reason)
def metrics(page):
    return page.evaluate("""() => ({
      sw:document.documentElement.scrollWidth,
      cw:document.documentElement.clientWidth,
      h1:document.querySelectorAll('h1').length,
      main:document.querySelectorAll('main').length,
      links:[...document.querySelectorAll('.fv-hf__chapter-nav a')].length,
      panels:[...document.querySelectorAll('[data-fv-case]')].length,
      theme:[...document.body.classList].filter(c=>c.includes('assembler')),
      body_classes:[...document.body.classList],
      flagship_roots:document.querySelectorAll('[data-fv-home-flagship]').length,
      legacy_hero:document.querySelectorAll('.fv-studios-hero').length,
      dev_controls:document.querySelectorAll('.fv-hf__studio-controls').length,
      margins:document.querySelectorAll('.fv-margin-strip__item').length,
      focus_links:[...document.querySelectorAll('a[href]')].filter(e=>{
        try { return new URL(e.href,location.href).pathname.replace(/\/$/,'')==='/focus'; }
        catch { return false; }
      }).length
    })""")
def stage_check(url,outdir,axe_file,media_manifest,approved_stage_host=None):
    host=validate_stage_url(url,approved_stage_host)
    expected_origin=urlsplit(url)
    trusted_media=read_trusted_media_manifest(media_manifest)
    require(axe_file.is_file() and axe_file.stat().st_size>10000,'axe-core JS file missing')
    outdir.mkdir(parents=True,exist_ok=True)
    receipt={'url_host':host,'status':'FAILED_CLOSED','widths':[],'media':{},
             'interactions':{},'axe':{},'no_js':None,'performance':'NOT_LIGHTHOUSE',
             'source':'WordPress/Assembler Playground — exact source required'}
    with sync_playwright() as p:
        executable=shutil.which('chromium') or shutil.which('chromium-browser')
        browser=p.chromium.launch(headless=True,executable_path=executable if executable else None,args=['--no-sandbox'])
        try:
            for w in WIDTHS:
                context=browser.new_context(viewport={'width':w,'height':900},reduced_motion='reduce')
                page=context.new_page()
                errors=[];browser_responses=[]
                page.on('pageerror',lambda err: errors.append(str(err)))
                # Capture browser image responses BEFORE navigation, including Apollo.
                # A separate APIRequestContext GET cannot prove pixels actually loaded.
                page.on('response',lambda event: browser_responses.append(event))
                response=page.goto(url,wait_until='load',timeout=30000)
                require(response and response.status==200,str(w)+': WordPress HTTP status not 200')
                observed_origin=urlsplit(page.url)
                require((observed_origin.scheme,observed_origin.netloc)==
                        (expected_origin.scheme,expected_origin.netloc),
                        str(w)+': off-stage redirect or scheme/port change denied')
                page.wait_for_timeout(200)
                m=metrics(page)
                verify_integrated_dom(m)  # never accept a seven-chapter-only mock without the protected WP content
                require(not errors,str(w)+': JavaScript exception '+str(errors))
                require(page.locator('[data-fv-case-buttons]').is_visible(),str(w)+': enhancement not loaded')
                require(page.locator('[data-fv-chronicle-lens]').is_visible(),str(w)+': lens missing')
                require(page.locator('[data-fv-observer-controls]').is_visible(),str(w)+': observer control missing')
                if w in (320,390,768,1440,1920):
                    page.screenshot(path=str(outdir/f'playground-first-{w}.png'))
                if w in (390,1440):
                    page.screenshot(path=str(outdir/f'playground-full-{w}.png'),full_page=True)
                receipt['widths'].append({'width':w,'metrics':m,'exceptions':errors,'status':'PASS'})
                if w in (390,1440):
                    page.add_script_tag(path=str(axe_file))
                    axe=page.evaluate("""async () => {
                        if(!window.axe || typeof window.axe.run!=='function') throw new Error('axe not loaded');
                        const r=await window.axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});
                        return {violations:r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>n.target)})),
                            incomplete:r.incomplete.map(v=>v.id), passes:r.passes.length};
                    }""")
                    receipt['axe'][str(w)]=axe
                    require(len(axe['violations'])==0,f'{w}: axe WCAG violations: {axe["violations"]}')
                    require(len(axe['incomplete'])==0,f'{w}: axe incomplete requires manual resolution: {axe["incomplete"]}')
                if w==390:
                    # The actual source has loading=lazy photos inside JS-hidden case
                    # panels. Select and scroll each case before requiring decode.
                    receipt['media']=audit_archive_gallery(
                        BrowserEvidencePage(page,browser_responses,
                            (expected_origin.scheme,expected_origin.netloc)),
                        (expected_origin.scheme,expected_origin.netloc),
                        trusted_media, MEDIA, require, verify_media_payload)
                    page.locator('[data-fv-case-button="franklin"]').click()
                    require(page.locator('[data-fv-case="franklin"]').is_visible(),'case chooser Franklin')
                    receipt['interactions']['case']='PASS'
                    page.locator('[data-fv-chronicle-view="original"]').click()
                    require(page.locator('.fv-hf__chronicle').get_attribute('data-fv-chronicle-mode')=='original','chronicle lens')
                    receipt['interactions']['lens']='PASS'
                    page.locator('[data-fv-observer-switch="b"]').click()
                    require(page.locator('[data-fv-observer-frame="b"]').is_visible(),'observer switch')
                    receipt['interactions']['observer']='PASS'
                    link=page.locator('.fv-hf__chapter-nav a[href="#fv-hf-inquiry"]')
                    link.focus(); link.press('Enter')
                    require(page.evaluate('location.hash')=='#fv-hf-inquiry','keyboard chapter trail')
                    receipt['interactions']['trail']='PASS'
                    page.evaluate('document.documentElement.style.zoom="200%"')
                    z=metrics(page)
                    require(z['sw']<=z['cw']+1,'CSS 200 percent zoom overflow')
                    receipt['zoom_200']='PASS'
                context.close()
            noctx=browser.new_context(viewport={'width':390,'height':900},java_script_enabled=False)
            nopage=noctx.new_page();nopage.goto(url,wait_until='load',timeout=30000)
            no_origin=urlsplit(nopage.url)
            require((no_origin.scheme,no_origin.netloc)==
                    (expected_origin.scheme,expected_origin.netloc),
                    'no-JS page redirected away from isolated stage')
            require(all(nopage.locator(f'[data-fv-case="{x}"]').is_visible() for x in ('apollo','franklin','malbone')),
                    'no-JS original evidence not visible')
            require(nopage.locator('.fv-hf__chapter-nav a').count()==7,'no-JS chapter nav not present')
            verify_integrated_dom(metrics(nopage))
            receipt['no_js']='PASS';noctx.close()
            receipt['status']='STAGING_BROWSER_PASSED_AWAITING_HOSTED_QD'
        finally: browser.close()
    (outdir/'PLAYGROUND_ADMISSION.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps({'status':receipt['status'],'widths':len(receipt['widths']),
       'axe':list(receipt['axe']),'media':receipt['media'],'interactions':receipt['interactions']},indent=2))
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--url',required=True,help='isolated Playground/localhost preview only')
    ap.add_argument('--axe-js',type=Path,required=True,help='verified, local axe-core distributable JS')
    ap.add_argument('--trusted-media-manifest',type=Path,required=True,
                    help='independent three-original SHA-256 manifest created before this browser run')
    ap.add_argument('--approved-stage-host',default=None,
                    help='explicit exact HTTPS hostname for a separately authorized isolated host')
    ap.add_argument('--output-dir',type=Path,required=True)
    args=ap.parse_args()
    try:
        stage_check(args.url,args.output_dir,args.axe_js,
                    args.trusted_media_manifest,args.approved_stage_host)
    except Exception as exc:
        args.output_dir.mkdir(parents=True,exist_ok=True)
        (args.output_dir/'PLAYGROUND_ADMISSION_FAILURE.json').write_text(json.dumps({
          'status':'FAILED_CLOSED','stage_host':urlsplit(args.url).hostname,
          'error_type':type(exc).__name__,'reason':str(exc)[:400],
          'wordPressRendered':False,'axeVerified':False,'lighthouseVerified':False
        },indent=2))
        raise
if __name__=='__main__': main()
