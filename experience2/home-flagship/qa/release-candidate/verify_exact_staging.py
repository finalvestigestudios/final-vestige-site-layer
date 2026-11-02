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
from verify_release_content_parity import verify_repo, RIGHTS, MIND_NOTICE

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


def check_private_render_url(src: str, shortcode_page_url: str) -> str:
    """Authorize ONLY the nonce-bearing AJAX renderer found in WP shortcode.

    This is a same-origin, authenticated, read-only WordPress response.
    The nonce is NEVER logged, captured or serialized in a QA receipt.
    A direct top-level context supplies true 360/390/768/1440/1920 widths;
    the separate embedded shortcode remains an independently checked gate.
    """
    from urllib.parse import parse_qs
    if not isinstance(src,str) or not src or len(src)>1024:
        raise ValueError('Private renderer URL unavailable or invalid')
    p=urlsplit(src)
    outer=urlsplit(shortcode_page_url)
    if (p.scheme!=outer.scheme or p.hostname!=outer.hostname
        or p.port!=outer.port or p.username or p.password or p.fragment
        or p.path!='/wp-admin/admin-ajax.php'):
        raise ValueError('Private renderer must be exact same-origin AJAX path')
    try:
        params=parse_qs(p.query,strict_parsing=True,keep_blank_values=True)
    except ValueError:
        raise ValueError('Private renderer query invalid') from None
    if (set(params)!={'action','_wpnonce'}
        or params.get('action')!=['fv_ex2_private_render']
        or len(params.get('_wpnonce',[]))!=1
        or not re.fullmatch(r'[A-Za-z0-9]{10,16}',params['_wpnonce'][0])):
        raise ValueError('Private renderer action or nonce invalid')
    return src


def sanitized_page_error(err) -> str:
    """Keep only a bounded JS exception CLASS; no private AJAX URL or nonce."""
    message=str(err)
    for kind in ('ReferenceError','TypeError','SyntaxError','SecurityError',
                 'NetworkError','RangeError'):
        if kind in message:
            return 'PAGE_JS_' + kind.upper()
    return 'PAGE_JS_UNCLASSIFIED_ERROR'


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
    for name in ('verify_exact_staging.py', 'media_transfer_admission.py', 'test_media_transfer_admission.py', 'test_exact_staging.py',
                 'verify_release_content_parity.py', 'test_release_content_parity.py'):
        rel = HOME/'qa/release-candidate'/name
        p = repo/rel
        if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(repo):
            raise ValueError('RELEASE HOLD: missing/unsafe staging QA file: '+str(rel))
        committed = subprocess.run(['git','-C',str(repo),'show',expected_sha+':'+rel.as_posix()],capture_output=True)
        if committed.returncode or committed.stdout != p.read_bytes():
            raise ValueError('RELEASE HOLD: modified staging QA code: '+str(rel))
    # The proposed page-6 replacement is pinned to the release author's
    # exact #604 blob. Never use a mutated private fixture to certify release.
    rel = HOME/'qa/release-candidate/fixtures/proposed-production-block-pr604.html'
    pp = repo/rel
    if pp.is_symlink() or not pp.is_file() or not pp.resolve().is_relative_to(repo):
        raise ValueError('RELEASE HOLD: missing/unsafe proposed production fixture')
    committed = subprocess.run(['git','-C',str(repo),'show',expected_sha+':'+rel.as_posix()],capture_output=True)
    if committed.returncode or committed.stdout != pp.read_bytes():
        raise ValueError('RELEASE HOLD: uncommitted proposed production fixture')
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
    check('mind_no_unverified_commercial_claims',frame.locator('.fv-hf__mind small').filter(has_text=MIND_NOTICE).count()==1)
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
    # Genuine founder first-screen visual: capture the browser viewport at
    # scroll=0 BEFORE selecting distant archive cases. An element screenshot
    # taken after scrolling can misleadingly composite the fixed skip link
    # and sticky chapter bar over the hero, especially on mobile.
    if width in (390,1440):
        try:
            frame.page.evaluate('window.scrollTo(0,0)')
            frame.page.screenshot(path=str(out/f'first-screen-{width}.png'),
                                  full_page=False,timeout=15000)
            check('real_hero_screenshot',True)
        except Exception:
            check('real_hero_screenshot',False)

    # Archive exhibits are mutually exclusive ONLY after JS enhancement.
    # An inactive case image is intentionally hidden, so Playwright cannot
    # scroll it into view. Activate its REAL visible selector before testing
    # lazy loading and actual HTTP payloads; never remove [hidden] in QA.
    case_ids = ('apollo', 'franklin', 'malbone')
    images = frame.locator('img[data-fv-archive-img]').all()
    check('three_archival_images',len(images)==len(case_ids))
    chooser = frame.locator('[data-fv-case-buttons]')
    try:
        chooser.wait_for(state='visible', timeout=7000)
        check('archive_chooser_enhanced',True)
    except Exception:
        check('archive_chooser_enhanced',False)

    imagedata=[]
    for case_id in case_ids:
        unknown = {'url':'','complete':False,'width':0,'height':0}
        button = frame.locator(f'[data-fv-case-button="{case_id}"]')
        panel = frame.locator(f'[data-fv-case="{case_id}"]')
        check('archive_button_present_'+case_id,button.count()==1)
        check('archive_panel_present_'+case_id,panel.count()==1)
        if button.count()!=1 or panel.count()!=1:
            imagedata.append(unknown)
            continue
        case_img=panel.locator('img[data-fv-archive-img]')
        check('archive_image_present_'+case_id,case_img.count()==1)
        is_button_visible=button.is_visible()
        check('archive_button_visible_'+case_id,is_button_visible)
        if not is_button_visible or case_img.count()!=1:
            imagedata.append(unknown)
            continue
        try:
            # Real user click proves the enhanced case chooser is operable.
            button.click(timeout=6000)
            # Verify credit/rights language in actual WordPress DOM and that
            # a keyboard/touch-operable native <details> can reveal it.
            credit=panel.locator('.fv-hf__case-source p').filter(has_text=RIGHTS[case_id])
            check('archival_credit_present_'+case_id, credit.count()==1)
            note=panel.locator('details').first
            if note.count()==1 and credit.count()==1:
                note.locator('summary').click(timeout=6000)
                check('archival_credit_revealed_'+case_id,credit.is_visible())
                note.locator('summary').click(timeout=6000)
            else:
                check('archival_credit_revealed_'+case_id,False)
            activated=panel.is_visible() and button.get_attribute('aria-pressed')=='true'
            check('archive_case_activated_'+case_id,activated)
            visible=activated and case_img.is_visible()
            check('archive_image_visible_'+case_id,visible)
            if visible:
                case_img.scroll_into_view_if_needed(timeout=6000)
                unknown=case_img.evaluate("""async e => {
                  if (!e.complete) await Promise.race([
                    new Promise(r=>{e.addEventListener('load',r,{once:true});e.addEventListener('error',r,{once:true});}),
                    new Promise(r=>setTimeout(r,8000))]);
                  return {url:e.currentSrc||e.src,complete:e.complete,width:e.naturalWidth,height:e.naturalHeight};
                }""")
        except Exception:
            # A broken interaction/image becomes an explicit per-case HOLD,
            # not a 30-second hidden-element timeout that erases all evidence.
            check('archive_case_interaction_'+case_id,False)
        imagedata.append(unknown)
    if width in (390,1440):
        # Capture representative real WordPress-rendered previews, with the
        # first archive active again; screenshot failures remain release holds.
        first=frame.locator('[data-fv-case-button="apollo"]')
        try:
            first.click(timeout=6000)
            check('archive_first_case_restored',first.get_attribute('aria-pressed')=='true')
            frame.page.evaluate('window.scrollTo(0,0)')
            frame.page.screenshot(path=str(out/f'full-seven-chapter-{width}.png'),
                                  full_page=True,timeout=20000)
            check('real_fullpage_screenshot',True)
        except Exception:
            check('real_screenshot_capture',False)
    check('real_images_loaded',len(imagedata)==3 and all(i['complete'] and i['width']>0 for i in imagedata))
    # naturalWidth/metadata is insufficient: prove that Chromium received each
    # chosen currentSrc as a real HTTP 200 image response with a nonempty body.
    network_receipt = audit_image_payloads(imagedata, media_responses or [])
    check('actual_image_http_payloads', network_receipt['status']=='PASS')
    # Validate actual enhancement, rather than inferring from script tags.
    # PR #550 locked the approved blended identity and removed its direction picker.
    # Require the actual folio and cited editorial disclaimer; do not demand retired controls.
    check('locked_visual_identity', frame.locator('[data-fv-direction-choice]').count()==0
          and frame.locator('.fv-hf__studio-controls').count()==0)
    # Canonical proposed production source uses a named group, not an aside
    # landmark. Do not require a staging-only wrapper/semantic deviation.
    folio = frame.locator('div.fv-hf__folio-arrival[role="group"][aria-label]')
    check('franklin_folio_primary_date', folio.count()==1
          and folio.locator('time[datetime="1847-05-28"]').count()==1)
    check('franklin_folio_editorial_disclosure', folio.count()==1
          and folio.get_by_text('EDITORIAL TYPESETTING · NOT A FACSIMILE').count()==1)
    check('franklin_folio_primary_record_link', folio.count()==1
          and folio.locator('a[href="https://www.rmg.co.uk/collections/objects/rmgc-object-504898"]').count()==1)
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
    # Cross-PR custody must be proven before spending time on Chromium.
    # Only inner chapter markup is parity-scoped; standalone study chrome
    # must never leak into the native WordPress replacement block.
    content_parity=verify_repo(repo)
    if not storage_state.is_file(): raise ValueError('RELEASE HOLD: missing authorized private editor browser storage_state file')
    from playwright.sync_api import sync_playwright
    output.mkdir(parents=True,exist_ok=True)
    results=[]; failures=[]
    axe_code=axe_script.read_text() if axe_script and axe_script.is_file() else None
    # WordPress's editor shortcode embeds a deliberately sandboxed iframe in
    # the THEME'S text column (~744px at desktop). That is a legitimate
    # authorization/integration gate, but NOT a 1440px visual viewport.
    # Open ONLY its validated, nonce-protected same-origin WordPress AJAX HTML
    # in a separate top-level browser page for real full-width composition.
    # Do not loosen the original iframe sandbox or claim WP.com host parity.
    sandbox_warning = ("Failed to read the 'serviceWorker' property from 'Navigator': "
                       "Service worker is disabled because the context is sandboxed "
                       "and lacks the 'allow-same-origin' flag.")
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        try:
            for width in WIDTHS:
                context=browser.new_context(storage_state=str(storage_state),viewport={'width':width,'height':900},reduced_motion='reduce',service_workers='block')
                context.add_init_script(PERF_INIT)
                parent=context.new_page()
                parent_errors=[]
                parent.on('pageerror',lambda err:parent_errors.append(str(err)[:250]))
                record={'width':width,'checks':{},'errors':[]}
                try:
                    parent.goto(url,wait_until='domcontentloaded',timeout=30000)
                    preview=parent.locator('iframe[title="Final Vestige Experience 2.0, unpublished editorial preview"]')
                    preview.wait_for(state='attached',timeout=15000)
                    if set((preview.get_attribute('sandbox') or '').split())!={'allow-scripts','allow-popups'}:
                        raise RuntimeError('Private shortcode iframe security boundary changed')
                    embedded=preview.element_handle().content_frame()
                    if not embedded: raise RuntimeError('Authorized WordPress shortcode iframe unavailable')
                    embedded.locator('[data-fv-home-flagship]').wait_for(timeout=20000)
                    embedded_width=embedded.evaluate('window.innerWidth')
                    # The private AJAX action and nonce come ONLY from the
                    # authenticated shortcode; never synthesize or disclose it.
                    render_url=check_private_render_url(preview.get_attribute('src'),url)
                    visual=context.new_page()
                    visual_errors=[];image_responses=[]
                    visual.on('pageerror',lambda err:visual_errors.append(sanitized_page_error(err)))
                    visual.on('response',lambda response:image_responses.append(response)
                              if response.request.resource_type=='image' else None)
                    actual_response=visual.goto(render_url,wait_until='domcontentloaded',timeout=30000)
                    if actual_response is None or actual_response.status!=200:
                        raise RuntimeError('Authenticated WordPress private renderer did not return HTTP 200')
                    rendered=visual.main_frame
                    rendered.locator('[data-fv-home-flagship]').wait_for(timeout=20000)
                    headers={k.lower():v for k,v in actual_response.headers.items()}
                    record=inspect_frame(rendered,files,sha(files['index.html']),headers,width,output,axe_code,image_responses)
                    actual_width=rendered.evaluate('window.innerWidth')
                    record['embedded_wordpress_shortcode_width']=embedded_width
                    record['authenticated_render_viewport_width']=actual_width
                    record['render_context']='AUTHENTICATED_WORDPRESS_AJAX_FULL_VIEWPORT_NOT_THEME_PARITY'
                    record['checks']['private_wordpress_shortcode_iframe_renders']=True
                    record['checks']['secure_preview_iframe_sandbox_preserved']=True
                    record['checks']['true_rendered_viewport_width']=actual_width==width
                    record['checks']['no_page_errors']=not visual_errors
                    # WordPress Playground can access navigator.serviceWorker
                    # inside an intentionally opaque-origin iframe. The exact
                    # sandbox warning is documented, never reclassified as a
                    # homepage JS success; all other WP shortcode errors fail.
                    known=sum(e==sandbox_warning for e in parent_errors)
                    record['preview_sandbox_serviceworker_warnings']=known
                    record['checks']['no_unclassified_preview_errors']=known==len(parent_errors)
                    record['errors']=visual_errors
                except Exception as exc:
                    record['checks']['staging_page_rendered']=False
                    record['errors'].append(type(exc).__name__+': PRIVATE_WORDPRESS_BROWSER_GATE_BLOCKED')
                results.append(record)
                failures += [f'{width}:{k}' for k,v in record['checks'].items() if not v]
                context.close()
            # Verify no-JS meaning in BOTH the real WP shortcode and its
            # protected renderer at an actual 390px top-level viewport.
            cx=browser.new_context(storage_state=str(storage_state),viewport={'width':390,'height':850},java_script_enabled=False,service_workers='block')
            pg=cx.new_page(); nojs={'checks':{},'errors':[]}
            try:
                pg.goto(url,wait_until='domcontentloaded',timeout=30000)
                preview=pg.locator('iframe[title="Final Vestige Experience 2.0, unpublished editorial preview"]')
                preview.wait_for(state='attached',timeout=15000)
                if set((preview.get_attribute('sandbox') or '').split())!={'allow-scripts','allow-popups'}:
                    raise RuntimeError('No-JS WordPress preview sandbox changed')
                iframe=preview.element_handle().content_frame()
                if not iframe: raise RuntimeError('No-JS preview iframe missing')
                iframe.locator('[data-fv-home-flagship]').wait_for(timeout=15000)
                private_render=check_private_render_url(preview.get_attribute('src'),url)
                direct=cx.new_page()
                response=direct.goto(private_render,wait_until='domcontentloaded',timeout=30000)
                if response is None or response.status!=200:
                    raise RuntimeError('No-JS authenticated WordPress renderer failed')
                rendered=direct.main_frame
                rendered.locator('[data-fv-home-flagship]').wait_for(timeout=15000)
                nojs['checks']={
                    'private_shortcode_renders':iframe.locator('[data-fv-home-flagship]').count()==1,
                    'all_chapters':all(rendered.locator('#'+id).count()==1 for id in CHAPTERS),
                    'three_cases':rendered.locator('[data-fv-case]').count()==3,
                    'no_root_overflow':rendered.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),
                    'true_390px_viewport':rendered.evaluate('window.innerWidth')==390,
                    'no_js_case_panels_visible':all(rendered.locator('[data-fv-case="'+id+'"]').is_visible()
                                                   for id in ('apollo','franklin','malbone'))
                }
            except Exception as exc:
                nojs['checks']['no_js_available']=False;nojs['errors'].append(type(exc).__name__+': PRIVATE_WORDPRESS_NO_JS_GATE_BLOCKED')
            failures += ['nojs:'+k for k,v in nojs['checks'].items() if not v]
            cx.close()
        finally: browser.close()
    if axe_code is None: failures.append('AXE_NOT_RUN')
    return {'status':'HOLD_INDEPENDENT_RELEASE_APPROVAL_REQUIRED','pass_for_measured_browser_gates':not failures,
            'source_git_head':expected_sha,'index_sha256':sha(files['index.html']),
            'proposed_production_content_parity':content_parity,
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
