#!/usr/bin/env python3
"""Read-only, exact-source admission audit of an AUTHORIZED private WP staging preview.

No deployment or WordPress writes. Not a WCAG 2.2 AA or field-CWV certificate.
If staging is absent, fail closed with an explicit blocker receipt instead of a pass.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit
from media_transfer_admission import audit_image_payloads

HOME = Path('experience2/home-flagship')
CHAPTERS = ('fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry',
            'fv-hf-method-title','fv-hf-observer','fv-hf-mind-title')
STYLES = ('flagship.css','chronicle.css','chronicle-lens.css','inquiry.css',
          'observer-lab.css','reading-trail.css')
SCRIPTS = ('flagship.js','observer-lab.js','chronicle-lens.js','reading-trail.js')
PRODUCTION = {'finalvestige.com','www.finalvestige.com'}
WIDTHS = (360,390,768,1440,1920)
PERF_INIT = """(() => {
 window.__fvLab = { lcp: null, cls: 0 };
 if (typeof PerformanceObserver === 'undefined') return;
 try { new PerformanceObserver((ls) => { for (const e of ls.getEntries())
   window.__fvLab.lcp = { startTime: e.startTime, size: e.size,
     tag: e.element ? e.element.tagName : null }; }).observe({type:'largest-contentful-paint',buffered:true}); } catch (_) {}
 try { new PerformanceObserver((ls) => { for (const e of ls.getEntries())
   if (!e.hadRecentInput) window.__fvLab.cls += e.value; }).observe({type:'layout-shift',buffered:true}); } catch (_) {}
})();"""


def check_url(url: str, allowed_host: str) -> str:
    p = urlsplit(url)
    host = (p.hostname or '').lower().rstrip('.')
    allow = allowed_host.lower().rstrip('.')
    if host in PRODUCTION or not host or host != allow or not allow:
        raise ValueError('RELEASE HOLD: target must be an explicitly allowed, separate staging hostname, never production')
    # WordPress Playground defaults to query-parameter page resolution when
    # rewrite permalinks have not been configured. Permit ONLY this constant,
    # token-free local preview selector on loopback; remote URLs, arbitrary
    # query parameters and credentials remain prohibited.
    local_page_selector = (host in {'localhost', '127.0.0.1'}
                           and p.path in {'', '/'}
                           and p.query == 'pagename=fv-ex2-playground-review')
    if p.username or p.password or p.fragment or (p.query and not local_page_selector):
        raise ValueError('RELEASE HOLD: preview URL must not contain credentials, tokens, nonces or unauthorized query parameters')
    if p.scheme != 'https' and not (p.scheme == 'http' and host in {'localhost','127.0.0.1'}):
        raise ValueError('RELEASE HOLD: require HTTPS on nonlocal staging')
    return host


def checkout(repo: Path, expected_sha: str) -> tuple[Path, dict]:
    if not re.fullmatch(r'[0-9a-f]{40}',expected_sha):
        raise ValueError('expected_sha must be a 40-character lowercase Git commit SHA')
    repo = repo.resolve(strict=True)
    result = subprocess.run(['git','-C',str(repo),'rev-parse','HEAD'],capture_output=True,text=True)
    if result.returncode or result.stdout.strip() != expected_sha:
        raise ValueError('RELEASE HOLD: checkout HEAD does not equal the expected source SHA')
    files = {}
    for name in ('index.html',)+STYLES+SCRIPTS:
        path = HOME/name
        p = repo/path
        if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(repo):
            raise ValueError('Missing/unsafe source: '+str(path))
        committed = subprocess.run(['git','-C',str(repo),'show',expected_sha+':'+path.as_posix()],capture_output=True)
        raw = p.read_bytes()
        if committed.returncode or committed.stdout != raw:
            raise ValueError('RELEASE HOLD: uncommitted staging source: '+str(path))
        files[name] = raw
    # Attest the executed QA code as well as the original eleven homepage assets.
    for name in ('verify_exact_staging.py', 'media_transfer_admission.py', 'test_media_transfer_admission.py', 'test_exact_staging.py'):
        rel = HOME/'qa/release-candidate'/name
        p = repo/rel
        if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(repo):
            raise ValueError('RELEASE HOLD: missing/unsafe staging QA file: '+str(rel))
        committed = subprocess.run(['git','-C',str(repo),'show',expected_sha+':'+rel.as_posix()],capture_output=True)
        if committed.returncode or committed.stdout != p.read_bytes():
            raise ValueError('RELEASE HOLD: modified staging QA code: '+str(rel))
    return repo, files


def margins_contract(raw: str) -> dict:
    numbers = [int(x) for x in re.findall(r'class="fv-margin-strip__item"\s+style="--i:(\d+)"',raw)]
    return {'present':len(numbers)==72 and set(numbers)==set(range(72)),
            'count':len(numbers), 'unique_count':len(set(numbers)),
            'focus_fieldbook':('href="/focus/"' in raw and 'Seven Day Focus Fieldbook' in raw),
            'jetpack_signup':'<!-- wp:jetpack/subscriptions' in raw}


def sha(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def inspect_frame(frame, files: dict, expected_index_hash: str, headers: dict, width: int, out: Path, axe_source: str | None = None, media_responses: list | None = None) -> dict:
    """Inspect browser-rendered bytes and behavior; all failures are explicit."""
    checks = {}
    def check(name,condition): checks[name] = bool(condition)
    header_hash = headers.get('x-fv-ex2-index-sha256','')
    check('server_exposes_exact_index_hash',header_hash==expected_index_hash)
    check('header_no_cache','no-store' in headers.get('cache-control',''))
    check('header_no_index','noindex' in headers.get('x-robots-tag',''))
    csp = headers.get('content-security-policy','')
    check('response_csp_nonces',"script-src 'nonce-" in csp and "default-src 'none'" in csp)
    check('exactly_one_heading',frame.locator('h1').count()==1)
    check('all_seven_chapters',all(frame.locator('#'+id).count()==1 for id in CHAPTERS))
    check('no_horizontal_root_overflow',frame.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'))
    check('source_galleries_survive',frame.locator('[data-fv-case]').count()==3)
    check('focus_link_present',frame.locator('a[href="https://finalvestige.com/focus/"]').count()>=1)
    delivered = {}
    for tag,name in [('style',n) for n in STYLES]+[('script',n) for n in SCRIPTS]:
        loc = frame.locator(f'{tag}[data-fv-private-asset="{name}"]')
        present = loc.count()==1
        check('asset_present_'+name,present)
        if present:
            content = loc.text_content() or ''
            # Composer adds exactly one leading and one trailing newline to source.
            actual = content[1:-1] if content.startswith('\n') and content.endswith('\n') else None
            check('asset_bytes_exact_'+name, actual==files[name].decode('utf-8'))
            delivered[name] = sha(actual.encode('utf-8')) if actual is not None else 'MISSING_WRAPPERS'
    images = frame.locator('img[data-fv-archive-img]').all()
    check('three_archival_images',len(images)==3)
    imagedata=[]
    for el in images:
        el.scroll_into_view_if_needed()
        image = el.evaluate("""async e => {
          if (!e.complete) await Promise.race([
            new Promise(r=>{e.addEventListener('load',r,{once:true});e.addEventListener('error',r,{once:true});}),
            new Promise(r=>setTimeout(r,8000))]);
          return {url:e.currentSrc||e.src,complete:e.complete,width:e.naturalWidth,height:e.naturalHeight};
        }""")
        imagedata.append(image)
    check('real_images_loaded',len(imagedata)==3 and all(i['complete'] and i['width']>0 for i in imagedata))
    # naturalWidth/metadata is insufficient: prove that Chromium received each
    # chosen currentSrc as a real HTTP 200 image response with a nonempty body.
    network_receipt = audit_image_payloads(imagedata, media_responses or [])
    check('actual_image_http_payloads', network_receipt['status']=='PASS')
    # Validate actual enhancement, rather than inferring from script tags.
    check('direction_visible',frame.locator('[data-fv-direction-choice="museum"]').is_visible())
    if width in (390,1440):
        frame.locator('body').screenshot(path=str(out/f'full-seven-chapter-{width}.png'))
    perf = frame.evaluate("() => ({observer:window.__fvLab||null,resources:performance.getEntriesByType('resource').filter(e=>e.initiatorType==='img').map(e=>({name:e.name,transferSize:e.transferSize,decodedBodySize:e.decodedBodySize}))})")
    axe = {'status':'NOT_RUN','findings':None}
    if axe_source is not None:
        try:
            frame.evaluate(axe_source)
            findings=frame.evaluate("async () => await window.axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})")
            axe = {'status':'RUN','violations':[{'id':v['id'],'impact':v['impact'],'nodes':len(v['nodes'])} for v in findings['violations']]}
            check('axe_no_aa_violations',not findings['violations'])
        except Exception as exc:
            axe = {'status':'ERROR','reason':type(exc).__name__}
            check('axe_no_aa_violations',False)
    return {'width':width,'checks':checks,'images':imagedata,'image_http_delivery':network_receipt,'asset_sha256':delivered,
            'lab_observations_not_field_CWV':perf,'axe':axe}


def run(url: str, allowed_host: str, expected_sha: str, repo: Path, output: Path,
        storage_state: Path, axe_script: Path | None = None) -> dict:
    check_url(url,allowed_host)
    repo,files=checkout(repo,expected_sha)
    if not storage_state.is_file(): raise ValueError('RELEASE HOLD: missing authorized private editor browser storage_state file')
    from playwright.sync_api import sync_playwright
    output.mkdir(parents=True,exist_ok=True)
    results=[]; failures=[]
    axe_code=axe_script.read_text() if axe_script and axe_script.is_file() else None
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        try:
            for width in WIDTHS:
                context=browser.new_context(storage_state=str(storage_state),viewport={'width':width,'height':900},reduced_motion='reduce',service_workers='block')
                context.add_init_script(PERF_INIT)
                page=context.new_page();errors=[];ajax=[];image_responses=[]
                page.on('response', lambda response:image_responses.append(response)
                        if response.request.resource_type=='image' else None)
                page.on('pageerror',lambda err:errors.append(str(err)[:250]))
                page.on('response',lambda response:ajax.append(response) if 'action=fv_ex2_private_render' in response.url else None)
                record={'width':width,'checks':{},'errors':[]}
                try:
                    page.goto(url,wait_until='domcontentloaded',timeout=30000)
                    preview=page.locator('iframe[title="Final Vestige Experience 2.0, unpublished editorial preview"]')
                    preview.wait_for(state='attached',timeout=15000)
                    frame=preview.element_handle().content_frame()
                    if not frame: raise RuntimeError('Authorized preview iframe inaccessible')
                    frame.locator('[data-fv-home-flagship]').wait_for(timeout=20000)
                    if not ajax: raise RuntimeError('Private AJAX response not captured')
                    headers={k.lower():v for k,v in ajax[-1].headers.items()}
                    if ajax[-1].status!=200: raise RuntimeError('Authenticated staging AJAX returned '+str(ajax[-1].status))
                    record=inspect_frame(frame,files,sha(files['index.html']),headers,width,output,axe_code,image_responses)
                    record['checks']['no_page_errors']=not errors
                    record['errors']=errors
                except Exception as exc:
                    record['checks']['staging_page_rendered']=False
                    record['errors'].append(type(exc).__name__+': '+str(exc)[:220])
                results.append(record)
                failures += [f'{width}:{k}' for k,v in record['checks'].items() if not v]
                context.close()
            # Explicit no-JS HTML meaning. No scripted observations permitted here.
            cx=browser.new_context(storage_state=str(storage_state),viewport={'width':390,'height':850},java_script_enabled=False,service_workers='block')
            pg=cx.new_page(); nojs={'checks':{},'errors':[]}
            try:
                pg.goto(url,wait_until='domcontentloaded',timeout=30000)
                f=pg.locator('iframe[title="Final Vestige Experience 2.0, unpublished editorial preview"]').element_handle().content_frame()
                f.locator('[data-fv-home-flagship]').wait_for(timeout=15000)
                nojs['checks']={'all_chapters':all(f.locator('#'+id).count()==1 for id in CHAPTERS),
                               'three_cases':f.locator('[data-fv-case]').count()==3,
                               'no_root_overflow':f.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')}
            except Exception as exc:
                nojs['checks']['no_js_available']=False;nojs['errors'].append(type(exc).__name__+': '+str(exc)[:220])
            failures += ['nojs:'+k for k,v in nojs['checks'].items() if not v]
            cx.close()
        finally: browser.close()
    if axe_code is None: failures.append('AXE_NOT_RUN')
    return {'status':'HOLD_INDEPENDENT_RELEASE_APPROVAL_REQUIRED','pass_for_measured_browser_gates':not failures,
            'source_git_head':expected_sha,'index_sha256':sha(files['index.html']),
            'screenshots_captured':[x.name for x in output.glob('*.png')],
            'viewports':results,'no_javascript':nojs,'failure_codes':failures,
            'axe':'REQUIRES_LOCAL_AXE_CORE_JS' if axe_code is None else 'EXECUTED_WHEN_POSSIBLE',
            'lighthouse':'NOT_RUN', 'field_CWV':'NOT_MEASURED',
            'historical_media_rights':'INDEPENDENT_SIGNOFF_REQUIRED',
            'wp_native':'REQUIRES_INDEPENDENT_APPROVAL',
            'production_mutations':0}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--url',required=True,help='Explicit authorized PRIVATE staging shortcode page only')
    p.add_argument('--allow-host',required=True,help='Exact private staging host; production domains hard-denied')
    p.add_argument('--expected-head',required=True)
    p.add_argument('--repo',type=Path,default=Path('.'))
    p.add_argument('--storage-state',type=Path,required=True,help='Private Playwright editor session JSON; never commit or attach')
    p.add_argument('--axe-script',type=Path)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    report={'status':'BLOCKED_NO_QA','failure_codes':[],'release':'HOLD','production_mutations':0}
    try:
        report=run(args.url,args.allow_host,args.expected_head,args.repo,args.out,args.storage_state,args.axe_script)
        code=0 if report['pass_for_measured_browser_gates'] else 2
    except Exception as exc:
        report['failure_codes'].append(type(exc).__name__+': '+str(exc)[:300]);code=2
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/'STAGING_ACCEPTANCE.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'failures':report.get('failure_codes',[]),'release':'HOLD'},indent=2))
    return code

if __name__=='__main__':raise SystemExit(main())
