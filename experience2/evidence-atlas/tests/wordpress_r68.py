#!/usr/bin/env python3
"""Authentic disposable WordPress Playground/Assembler admission; R68 STAGING_HOLD.

Does not access production WordPress, import database/users, deploy or publish.
Produces an authentic local WordPress render gate only when CLI and axe are present.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, signal, stat, subprocess, sys, tempfile, time, urllib.request, zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit
# The exact-head/clean-tree admission runs AFTER imports; suppress local .pyc
# creation so the safety check is not invalidated by our own helper import.
sys.dont_write_bytecode = True
from wp_readiness_r69 import wait_for_wordpress, ReadinessFailure, diagnose_private_cli_log
from wp_case_ledger_r72 import CaseLedger
from wp_pdf_custody_r74 import verify_wordpress_print_page
from wp_accessibility_r74 import verify_installed_controls
from wp_pdf_pagination_r75 import prepare_review_pdf
from wp_native_print_r76 import verify_native_apollo_print
from wp_reusable_r77 import accept_synced_patterns, REUSABLE_SLUG, NEGATIVE_SLUG

BASE='http://127.0.0.1:9438/'
SLUG='fv-apollo-review-private'
WIDTHS=(320,360,390,768,1024,1440,1920)
PLUGINS=(
 ('fv-ex2-research-desk','final-vestige-ex2-research-desk.php'),
 ('fv-ex2-evidence-atlas','final-vestige-ex2-evidence-atlas.php'),
 ('fv-ex2-apollo-suite','fv-ex2-apollo-suite.php'),
)
def digest(b):return hashlib.sha256(b).hexdigest()

def is_strict_loopback_request(address):
    """Avoid prefix-confused origins and all remote/HTTPS/credentialed URLs."""
    try:
        parsed=urlsplit(address)
        return (parsed.scheme=='http' and parsed.hostname=='127.0.0.1'
                and parsed.port==9438 and not parsed.username
                and not parsed.password)
    except (ValueError, TypeError):
        return False

def unpack_assembler(source,dest):
    names=set();total=0
    with zipfile.ZipFile(source) as zipfile_:
        items=[i for i in zipfile_.infolist() if not i.is_dir()]
        roots={PurePosixPath(i.filename).parts[0] for i in items}
        if len(roots)!=1 or roots.pop() not in ('assembler','assembler-wpcom'):
            raise ValueError('THEME_ROOT_NOT_ASSEMBLER')
        for item in items:
            p=PurePosixPath(item.filename)
            if (item.filename.startswith('/') or '\\' in item.filename or len(p.parts)<2 or
                any(s in ('','.','..') for s in p.parts) or
                stat.S_ISLNK(item.external_attr>>16)):
                raise ValueError('UNSAFE_THEME_ARCHIVE')
            relative=PurePosixPath(*p.parts[1:])
            if str(relative).lower() in names:raise ValueError('DUPLICATE_THEME_FILE')
            names.add(str(relative).lower());total+=item.file_size
            if total>80_000_000 or len(names)>4000:raise ValueError('THEME_SIZE_LIMIT')
            target=dest/str(relative)
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(zipfile_.read(item))
    css=(dest/'style.css').read_text(errors='replace')
    if not re.search(r'(?im)^\s*Theme Name:\s*Assembler\s*$',css) or not (dest/'templates/index.html').exists():
        raise ValueError('THEME_NOT_ASSEMBLER')
    return len(names)

def blueprint():
    # All WordPress database mutations are confined to freshly created, local Playground.
    php="""<?php
require_once '/wordpress/wp-load.php';
$host = strtolower((string) parse_url(home_url('/'), PHP_URL_HOST));
if (wp_get_environment_type() !== 'local' ||
    !in_array($host, ['127.0.0.1','localhost'], true))
    throw new RuntimeException('NONLOCAL_WORDPRESS_REFUSED');
// Ephemeral-only privacy fixture: default WP admin-bar Gravatar images
// otherwise attempt secure.gravatar.com external requests on EVERY case.
// Disable remote avatars in this disposable VM, never in production.
update_option('show_avatars', 0);
$slug = 'fv-apollo-review-private';
if (get_page_by_path($slug, OBJECT, 'page'))
    throw new RuntimeException('REFUSE_EXISTING_CONTENT');
$id = wp_insert_post(['post_type'=>'page','post_status'=>'private',
  'post_name'=>$slug,'post_title'=>'Apollo ephemeral test only',
  'post_content'=>'[fv_ex2_apollo_suite]','comment_status'=>'closed','ping_status'=>'closed'],true);
if (is_wp_error($id) || !$id) throw new RuntimeException('LOCAL_PAGE_CREATION_FAILED');
// R77: real two-level synced-pattern fixtures. Every database write is inside
// the short-lived LOCAL Playground VM; never WordPress.com or production.
if (get_page_by_path('fv-apollo-synced-review-private', OBJECT, 'page') ||
    get_page_by_path('fv-apollo-unrelated-review-private', OBJECT, 'page'))
    throw new RuntimeException('REFUSE_EXISTING_R77_CONTENT');
$r77_insert = function(array $data, string $failure) {
    $newid=wp_insert_post($data,true);
    if (is_wp_error($newid) || !$newid) throw new RuntimeException($failure);
    return $newid;
};
$inner = $r77_insert(['post_type'=>'wp_block','post_status'=>'publish',
  'post_title'=>'Apollo ephemeral inner pattern',
  'post_content'=>'<!-- wp:shortcode -->[fv_ex2_apollo_suite]<!-- /wp:shortcode -->'],
  'LOCAL_INNER_PATTERN_FAILED');
$outer = $r77_insert(['post_type'=>'wp_block','post_status'=>'publish',
  'post_title'=>'Apollo ephemeral outer pattern',
  'post_content'=>'<!-- wp:block {"ref":'.$inner.'} /-->'],
  'LOCAL_OUTER_PATTERN_FAILED');
$r77_insert(['post_type'=>'page','post_status'=>'private',
  'post_name'=>'fv-apollo-synced-review-private','post_title'=>'Apollo ephemeral test only',
  'post_content'=>'<!-- wp:block {"ref":'.$outer.'} /-->',
  'comment_status'=>'closed','ping_status'=>'closed'],
  'LOCAL_NESTED_PAGE_FAILED');
$unrelated = $r77_insert(['post_type'=>'wp_block','post_status'=>'publish',
  'post_title'=>'Unrelated ephemeral synced pattern',
  'post_content'=>'<!-- wp:paragraph --><p>No Apollo shortcode.</p><!-- /wp:paragraph -->'],
  'LOCAL_NEGATIVE_PATTERN_FAILED');
$r77_insert(['post_type'=>'page','post_status'=>'private',
  'post_name'=>'fv-apollo-unrelated-review-private',
  'post_title'=>'Unrelated local page',
  'post_content'=>'<!-- wp:block {"ref":'.$unrelated.'} /-->',
  'comment_status'=>'closed','ping_status'=>'closed'],
  'LOCAL_NEGATIVE_PAGE_FAILED');
?>"""
    return {'$schema':'https://playground.wordpress.net/blueprint-schema.json',
      'landingPage':'/?pagename='+SLUG,'login':True,'steps':[
        {'step':'defineWpConfigConsts','consts':{'WP_ENVIRONMENT_TYPE':'local',
          'WP_DEBUG':True,'WP_DEBUG_DISPLAY':False}},
        {'step':'activateTheme','themeFolderName':'assembler'},
        *[{'step':'activatePlugin','pluginPath':
           '/wordpress/wp-content/plugins/'+slug+'/'+php_name} for slug,php_name in PLUGINS],
        {'step':'runPHP','code':php}]}

def prepare(repo,theme_zip,stage,theme_sha,head):
    repo=repo.resolve(strict=True);stage=stage.resolve()
    if not re.fullmatch('[a-f0-9]{64}',theme_sha) or digest(theme_zip.read_bytes())!=theme_sha:
        raise ValueError('THEME_HASH_MISMATCH')
    if stage==repo or repo in stage.parents or (stage.exists() and any(stage.iterdir())):
        raise ValueError('STAGE_DESTINATION_UNSAFE')
    if not re.fullmatch('[0-9a-f]{40}',head):raise ValueError('EXACT_HEAD_REQUIRED')
    git=lambda *a:subprocess.check_output(['git','-C',str(repo),*a])
    if git('rev-parse','HEAD').decode().strip()!=head or git('status','--porcelain').strip():
        raise ValueError('GIT_HEAD_DIRTY_OR_MISMATCHED')
    # Verify runner bytes are identical to the requested Git commit.
    relative='experience2/evidence-atlas/tests/wordpress_r68.py'
    if (repo/relative).is_symlink() or git('show',head+':'+relative)!=(repo/relative).read_bytes():
        raise ValueError('RUNNER_NOT_EXACT_HEAD')
    stage.mkdir(parents=True)
    n=unpack_assembler(theme_zip,stage/'mounts/assembler')
    sys.path.insert(0,str(repo/'experience2/evidence-atlas/tests'))
    from build_full_staging_r67 import build
    package=build(stage/'plugins')
    if package['release']!='STAGING_HOLD' or len(package['files'])!=11:
        raise ValueError('PLUGIN_STAGING_CUSTODY_FAILED')
    for name,expected in package['files'].items():
        if digest((stage/'plugins'/name).read_bytes())!=expected:
            raise ValueError('PLUGIN_SOURCE_CHANGED')
    b=blueprint()
    (stage/'blueprint.json').write_text(json.dumps(b,indent=2,sort_keys=True)+'\n')
    argv=['npx','--yes','@wp-playground/cli@3.1.61','server',
      '--blueprint='+str(stage/'blueprint.json'),
      '--mount='+str(stage/'mounts/assembler')+':/wordpress/wp-content/themes/assembler',
      *['--mount='+str(stage/'plugins'/name)+':/wordpress/wp-content/plugins/'+name
        for name,_ in PLUGINS],'--port=9438']
    (stage/'argv.json').write_text(json.dumps(argv,indent=2)+'\n')
    r={'schema':'fv.apollo.r68.prepared.v1','release':'STAGING_HOLD',
       'head':head,'theme_download_sha256':theme_sha,'theme_independently_signed':False,
       'theme_file_count':n,'plugin_sha256':package['files'],
       'wordpress_executed':False,'public_wordpress_writes':False,
       'axe_executed':False,'hosted_cwv':False,'rights_cleared':False}
    (stage/'PREP_RECEIPT.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    return r

def accept(stage,axe,out):
    from playwright.sync_api import sync_playwright
    if not axe.is_file() or axe.stat().st_size<100000:
        raise ValueError('AXE_BUNDLE_NOT_AVAILABLE')
    argv=json.loads((stage/'argv.json').read_text())
    if (argv[:4]!=['npx','--yes','@wp-playground/cli@3.1.61','server'] or
        argv[-1]!='--port=9438' or sum(s.startswith('--mount=') for s in argv)!=4):
        raise ValueError('UNEXPECTED_PLAYGROUND_COMMAND')
    out.mkdir(parents=True,exist_ok=True)
    # This atomic, allowlist-only receipt survives any later browser failure.
    # It never treats an incomplete run, or a no-JS measurement, as a pass.
    ledger=CaseLedger(out/'R72_CASE_LEDGER.json')
    report={'schema':'fv.apollo.r68.actual-wp-browser.v1',
      'environment':'AUTHENTIC_EPHEMERAL_WORDPRESS_PLAYGROUND',
      'release':'STAGING_HOLD','public_wordpress_writes':False,
      'wp_com_host_parity':False,'manual_screen_reader':False,'field_cwv':False,
      'image_rights_cleared':False,'cases':[],'axe':[],'lab':[],'screenshots':{}}
    # Safe artifact preflight: no URL, storage state, cookie, CLI output or nonce.
    (out/'R69_PREPARED_GATE.json').write_text(json.dumps({
      'schema':'fv.apollo.r69.stage-gate.v1','release':'STAGING_HOLD',
      'prepared_source_verified':True,'real_wordpress_accepted':False,
      'axe_accepted':False,'public_wordpress_writes':False
    },indent=2,sort_keys=True)+'\n')
    last_browser_case={}
    with tempfile.TemporaryDirectory(prefix='fv-apollo-wp-private-') as secret:
      child=None
      try:
        with (Path(secret)/'private-cli.log').open('w') as logfile:
          child=subprocess.Popen(argv,stdout=logfile,stderr=subprocess.STDOUT,
             start_new_session=True,env={**os.environ,'CI':'true','npm_config_audit':'false'})
          # WordPress Playground may redirect / to a Blueprint landing page;
          # readiness must honor that local cookie handshake without ever
          # following an arbitrary Location header or external URL.
          endpoint, observations = wait_for_wordpress(child, seconds=180)
          (out/'R69_LOCAL_WORDPRESS_READINESS.json').write_text(json.dumps({
            'schema':'fv.apollo.r69.readiness.v1','release':'STAGING_HOLD',
            'positive_fixed_endpoint':endpoint,
            'allowlisted_probe_counts':observations,
            'wordpress_identified_not_browser_accepted':True,
            'off_origin_redirects_never_followed':True
          },indent=2,sort_keys=True)+'\n')
          with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
            auth=browser.new_context()
            login=auth.new_page()
            login.goto(BASE+'wp-admin/',wait_until='domcontentloaded',timeout=45000)
            if login.locator('#user_login').count() and login.locator('#user_pass').count():
              login.locator('#user_login').fill('admin')
              login.locator('#user_pass').fill('password')
              login.locator('#wp-submit').click()
            login.goto(BASE+'?pagename='+SLUG,wait_until='domcontentloaded',timeout=45000)
            assert login.locator('.fv-ex2-apollo-suite').count()==1,'AUTHENTIC_WP_RENDER_NOT_FOUND'
            state=auth.storage_state();auth.close()
            for w in WIDTHS:
              for js in (False,True):
                context=browser.new_context(viewport={'width':w,'height':900},
                  storage_state=state,java_script_enabled=js,
                  reduced_motion='reduce',is_mobile=w<=390,has_touch=w<=390)
                if js:
                  context.add_init_script("""(()=>{
                    window.__apolloLab={lcp:null,cls:0};
                    try{new PerformanceObserver(x=>{
                       const a=x.getEntries();if(a.length)window.__apolloLab.lcp=a[a.length-1].startTime;
                    }).observe({type:'largest-contentful-paint',buffered:true});}catch(e){}
                    try{new PerformanceObserver(x=>{
                       for(const e of x.getEntries())if(!e.hadRecentInput)window.__apolloLab.cls+=e.value;
                    }).observe({type:'layout-shift',buffered:true});}catch(e){}
                  })();""")
                ledger.begin(w,js)
                page=context.new_page();errors=[];outbound=[]
                page.on('pageerror',lambda error:errors.append('JS_ERROR'))
                def route(req):
                    if is_strict_loopback_request(req.request.url):req.continue_()
                    else:outbound.append(req.request.resource_type);req.abort()
                page.route('**/*',route)
                res=page.goto(BASE+'?pagename='+SLUG,wait_until='networkidle',timeout=45000)
                assert res is not None and res.status==200,'LOCAL_HTTP_FAILED'
                # Admission is for an actual top-level browser, not a shrunk
                # editor/iframe preview: the viewport must be the requested CSS width.
                assert page.evaluate('window.top===window.self && window.innerWidth')==w,'NOT_TOP_LEVEL_REQUESTED_WIDTH'
                ledger.advance('HTTP_200')
                assert page.locator('.fv-ex2-apollo-suite').count()==1
                assert page.locator('[data-fvx-record]').count()==6
                assert page.locator('[data-fva-record]').count()==6
                assert page.locator('.fv-ex2-ledger__custody dd').count()==30
                assert page.locator('[data-fva-drawer] dd').count()==54
                assert page.locator('[data-fva-cite-id]').count()==6
                # Same six reviewed NASA catalog destinations used by the
                # independently green R70 editorial browser suite. No images,
                # geographic points, or unreviewed source substitutions.
                expected_nasa_links=(
                  'https://www.nasa.gov/image-detail/apollo-1-crew-honored/',
                  'https://www.nasa.gov/image-detail/amf-s67-15717/',
                  'https://www.nasa.gov/image-detail/amf-s66-58038/',
                  'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/',
                  'https://www.nasa.gov/image-detail/amf-s67-21294/',
                  'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/',
                )
                assert tuple(x.get_attribute('href') for x in page.locator('.fva-card__external').all())==expected_nasa_links,'NASA_LINK_CUSTODY_HOLD'
                assert page.locator('.fv-ex2-apollo-suite [data-lat],[data-lon],[data-geo-edge]').count()==0,'UNREVIEWED_GEO_HOLD'
                assert page.locator('.fv-ex2-apollo-suite img').count()==0
                ledger.advance('SOURCE_CUSTODY')
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2')
                # Only boolean/count/type diagnostics, never raw URLs or JS
                # messages. Theme-initiated requests remain blocked and
                # uncertified until reviewed; do not silently weaken gate.
                last_browser_case={'width':w,'javascript_enabled':js,
                  'blocked_external_request_count':len(outbound),
                  'blocked_resource_types':sorted(set(outbound)),
                  'page_javascript_error_count':len(errors)}
                assert not outbound and not errors,'NETWORK_OR_JAVASCRIPT_GATE_HOLD'
                ledger.advance('NETWORK_CLEAN')
                if js:
                    assert page.locator('[data-fva-atlas]').get_attribute('data-fva-ready')=='yes'
                    assert page.locator('[data-fva-to-desk]:visible').count()==6
                    # Exercise native keyboard and real touch/mouse interactions
                    # in INSTALLED WordPress, rather than checking selectors only.
                    summary=page.locator('[data-fva-drawer] summary').first
                    summary.focus()
                    assert summary.evaluate('e=>document.activeElement===e')
                    was_open=summary.evaluate('e=>e.parentElement.open')
                    page.keyboard.press('Enter')
                    assert summary.evaluate('e=>e.parentElement.open')!=was_open
                    page.keyboard.press('Enter')
                    assert summary.evaluate('e=>e.parentElement.open')==was_open
                    provisional=page.locator('[data-fva-proof-filter="provisional"]')
                    (provisional.tap() if w<=390 else provisional.click())
                    assert page.locator('[data-fva-record]:visible').count()==1
                    reset=page.locator('[data-fva-proof-filter="all"]')
                    (reset.tap() if w<=390 else reset.click())
                    assert page.locator('[data-fva-record]:visible').count()==6
                    # The source register is generated in-browser from the six
                    # reviewed NASA records, with explicit reuse limitations.
                    # Read it inside the disposable runner; never upload the
                    # downloaded text or leak local browser file paths.
                    with page.expect_download(timeout=15000) as download_event:
                        export=page.locator('[data-fva-export]')
                        (export.tap() if w<=390 else export.click())
                    source_download=download_event.value
                    assert source_download.suggested_filename=='apollo-1-nasa-source-register.txt','SOURCE_REGISTER_FILENAME_CHANGED'
                    register=Path(source_download.path()).read_text(encoding='utf-8')
                    assert register.count('Catalog reference:')==6,'INCOMPLETE_SOURCE_REGISTER'
                    assert register.count('Reuse status:')==6,'SOURCE_REGISTER_RIGHTS_MISSING'
                    assert 'rights reviews are outstanding' in register,'FALSE_RIGHTS_ASSURANCE'
                    assert 'NASA does not endorse this publication.' in register,'ENDORSEMENT_NOTICE_MISSING'
                    assert all(link in register for link in expected_nasa_links),'NASA_REGISTER_CROSSWALK_MISMATCH'
                    ledger.advance('INTERACTION')
                    if w in (390,1440):
                        # R74: installed WordPress source-label and forced-color gate.
                        report.setdefault('r74_a11y',[]).append(
                            verify_installed_controls(page,w,out))
                    if w in (390,1440):
                        page.add_script_tag(path=str(axe))
                        a=page.evaluate("""async()=>{
                          const x=await axe.run(document.querySelector('.fv-ex2-apollo-suite'),{
                            runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
                          return {violations:x.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length})),passes:x.passes.length};
                        }""")
                        report['axe'].append({'width':w,**a})
                        # Axe failure used to vanish when the full 14-case
                        # report was withheld. Store ONLY rule IDs, impact and
                        # numeric counts before admission; no DOM snippets,
                        # CSS targets, text, private URLs, or credentials.
                        (out/'R72_INCREMENTAL_AXE_RECEIPT.json').write_text(
                            json.dumps({'schema':'fv.apollo.r72.axe-progress.v1',
                              'release':'STAGING_HOLD','human_review_required':True,
                              'scope':'ORIGINAL_APOLLO_COMPONENT_INSIDE_REAL_LOCAL_WORDPRESS',
                              'observations':report['axe']},indent=2,sort_keys=True))
                        assert not a['violations'],a
                        ledger.advance('AXE')
                        img=page.screenshot(full_page=True,animations='disabled')
                        filename=f'R68_AUTHENTIC_WP_{w}.png'
                        (out/filename).write_bytes(img)
                        report['screenshots'][filename]=digest(img)
                    # LCP PerformanceObserver is asynchronous: do not read
                    # immediately and misdiagnose a healthy WordPress render.
                    # A missing entry after a bounded wait still fails closed.
                    page.wait_for_function("window.__apolloLab && Number.isFinite(window.__apolloLab.lcp)",timeout=10000)
                    metric=page.evaluate("""()=>({lcp:window.__apolloLab?.lcp??null,
                      cls:window.__apolloLab?.cls??null})""")
                    report['lab'].append({'width':w,**metric,'authentic_local_lab_not_field_cwv':True})
                    assert metric['lcp'] is not None and metric['lcp']<=2500
                    assert metric['cls'] is not None and metric['cls']<=0.1
                    ledger.advance('LAB_METRICS')
                    page.emulate_media(media='print')
                    assert page.locator('[data-fvx-record]:visible').count()==6
                    assert page.locator('[data-fva-record]:visible').count()==6
                    ledger.advance('PRINT')
                else:
                    assert page.locator('[data-fvx-record]:visible').count()==6
                    assert page.locator('[data-fva-record]:visible').count()==6
                    page.emulate_media(media='print')
                    assert page.locator('.fv-ex2-ledger__custody dd:visible').count()==30
                    assert page.locator('[data-fva-drawer] dd:visible').count()==54
                    if w==1440:
                        # Chromium's actual PDF can omit CLOSED source details
                        # despite passing DOM print-media visibility checks.
                        report['r74_print_pdf']=verify_wordpress_print_page(
                            page,out/'R74_AUTHENTIC_WP_PRINT_1440.pdf')
                        (out/'R74_PRINT_CUSTODY_RECEIPT.json').write_text(
                            json.dumps(report['r74_print_pdf'],indent=2,sort_keys=True)+'\n')
                        # R76: native print must NOT need R75's PDF normalization.
                        # Audit the unchanged browser PDF, its terminal page,
                        # exact NASA custody and site/footer print isolation.
                        raw_native_pdf = (out/'R74_AUTHENTIC_WP_PRINT_1440.pdf').read_bytes()
                        report['r76_native_print'] = verify_native_apollo_print(
                            page, raw_native_pdf, out/'R76_NATIVE_PRINT_LAST_PAGE.png')
                        (out/'R76_NATIVE_PRINT_RECEIPT.json').write_text(
                            json.dumps(report['r76_native_print'],indent=2,sort_keys=True)+'\n')
                        # R75: a *separate* source-reverified PDF copy removes
                        # proven decorative-only terminal paper pages. Preserve
                        # the original Chromium PDF unmodified for forensic QA.
                        original_pdf = (out/'R74_AUTHENTIC_WP_PRINT_1440.pdf').read_bytes()
                        _, report['r75_pagination'] = prepare_review_pdf(
                            original_pdf, out/'R75_SOURCE_SAFE_PRINT_REVIEW.pdf')
                        (out/'R75_PAGINATION_RECEIPT.json').write_text(
                            json.dumps(report['r75_pagination'],indent=2,sort_keys=True)+'\n')
                    ledger.advance('NO_JS_CONTENT')
                ledger.pass_case()
                report['cases'].append({'width':w,'js':js,'pass':True})
                context.close()
            report['r77_synced_patterns'] = accept_synced_patterns(
                browser, state, out, BASE, is_strict_loopback_request, axe,
                verify_wordpress_print_page, verify_native_apollo_print)
            browser.close()
        ledger.require_complete()
        (out/'R68_AUTHENTIC_WP_RECEIPT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        (out/'R69_REAL_WP_ADMISSION.json').write_text(json.dumps({
          'schema':'fv.apollo.r69.admission.v1','release':'STAGING_HOLD',
          'all_actual_wordpress_cases_passed':len(report['cases'])==14,
          'r77_synced_pattern_cases_passed':len(report['r77_synced_patterns']['cases'])==5,
          'axe_passed_at_390_and_1440':len(report['axe'])==2,
          'actual_wordpress_browser_evidence':True,
          'local_lab_not_hosted_cwv':True,
          'public_wordpress_writes':False
        },indent=2,sort_keys=True)+'\n')
        return report
      except Exception as exc:
        # Preserve only a classification, never the exception text/URL or
        # private Playground credentials. The last completed milestone stays
        # durable even if the process exits before its full 14-case receipt.
        failure_class=('NETWORK' if last_browser_case.get('blocked_external_request_count',0) else
                       'ASSERTION' if isinstance(exc,AssertionError) else
                       'BROWSER' if type(exc).__name__ in ('TimeoutError','Error','TargetClosedError') else
                       'UNKNOWN')
        ledger.hold(failure_class)
        # Preserve an actionable allowlisted failure receipt. The private
        # CLI log is destroyed on exit; no raw log, URL or auth may escape.
        phase = getattr(exc,'reason',type(exc).__name__)
        safe = phase if phase in ('PLAYGROUND_EXITED','WORDPRESS_LOCAL_READINESS_TIMEOUT') else type(exc).__name__
        # Only source-controlled function/line locations are allowed into
        # review artifacts; no traceback values, path, locals, URLs or cookies.
        site=[]
        tb=exc.__traceback__
        while tb is not None:
          frame=tb.tb_frame
          basename=Path(frame.f_code.co_filename).name
          if basename in ('wordpress_r68.py','wp_readiness_r69.py'):
            site.append({'module':basename,
                         'function':frame.f_code.co_name,
                         'line':tb.tb_lineno})
          tb=tb.tb_next
        (out/'R69_FAIL_CLOSED_RECEIPT.json').write_text(json.dumps({
          'schema':'fv.apollo.r69.failure.v1','release':'STAGING_HOLD',
          'real_wordpress_accepted':False,'axe_accepted':False,
          'failure_category':safe,
          'source_location_only':site[-4:],
          'last_browser_case_safe_counts':last_browser_case,
          'private_cli_log_class':diagnose_private_cli_log(Path(secret)/'private-cli.log'),
          'allowlisted_probe_counts':getattr(exc,'states',{}),
          'public_wordpress_writes':False,'raw_log_or_auth_material_uploaded':False
        },indent=2,sort_keys=True)+'\n')
        raise
      finally:
        if child is not None and child.poll() is None:
          try:os.killpg(child.pid,signal.SIGTERM)
          except ProcessLookupError:pass
          try:child.wait(timeout=8)
          except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL)

def main():
    p=argparse.ArgumentParser();p.add_argument('--repo',required=True,type=Path)
    p.add_argument('--theme-zip',required=True,type=Path)
    p.add_argument('--theme-sha256',required=True)
    p.add_argument('--head',required=True);p.add_argument('--stage',required=True,type=Path)
    p.add_argument('--axe',type=Path);p.add_argument('--out',type=Path)
    a=p.parse_args()
    # Bootstrap evidence even if exact-head validation fails before Playground
    # is launched. Never make a write inside the review checkout.
    if a.axe and a.out:
        repo_root=a.repo.resolve(strict=True)
        output_root=a.out.resolve()
        if output_root==repo_root or repo_root in output_root.parents:
            raise ValueError('ARTIFACT_DESTINATION_INSIDE_REPO')
        output_root.mkdir(parents=True,exist_ok=True)
        (output_root/'R69_BOOTSTRAP_RECEIPT.json').write_text(json.dumps({
            'schema':'fv.apollo.r69.bootstrap.v1','release':'STAGING_HOLD',
            'preparation_attempted':True,'real_wordpress_accepted':False,
            'public_wordpress_writes':False
        },indent=2,sort_keys=True)+'\n')
    try:
        prepare(a.repo,a.theme_zip,a.stage,a.theme_sha256,a.head)
    except Exception as exc:
        if a.axe and a.out:
            allowed={'THEME_HASH_MISMATCH','STAGE_DESTINATION_UNSAFE',
                     'EXACT_HEAD_REQUIRED','GIT_HEAD_DIRTY_OR_MISMATCHED',
                     'RUNNER_NOT_EXACT_HEAD','PLUGIN_STAGING_CUSTODY_FAILED',
                     'PLUGIN_SOURCE_CHANGED','THEME_ROOT_NOT_ASSEMBLER',
                     'THEME_NOT_ASSEMBLER','UNSAFE_THEME_ARCHIVE'}
            category=str(exc) if type(exc) is ValueError and str(exc) in allowed else type(exc).__name__
            (a.out/'R69_PREPARE_HOLD.json').write_text(json.dumps({
                'schema':'fv.apollo.r69.prepare-failed.v1','release':'STAGING_HOLD',
                'category':category,'real_wordpress_accepted':False,
                'raw_logs_uploaded':False,'public_wordpress_writes':False
            },indent=2,sort_keys=True)+'\n')
        raise
    if a.axe:
        if not a.out:p.error('--out required with --axe')
        accept(a.stage,a.axe,a.out)
    else:print('PREPARED_ONLY_NOT_AUTHENTIC_WP_ACCEPTED')
if __name__=='__main__':
    try:main()
    except Exception as exc:
        # Never include private CLI output or auth material in CI logs.
        print('APOLLO_R69_HOLD '+type(exc).__name__,file=sys.stderr)
        sys.exit(2)
