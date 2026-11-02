#!/usr/bin/env python3
"""Authentic disposable WordPress Playground/Assembler admission; R68 STAGING_HOLD.

Does not access production WordPress, import database/users, deploy or publish.
Produces an authentic local WordPress render gate only when CLI and axe are present.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, signal, stat, subprocess, sys, tempfile, time, urllib.request, zipfile
from pathlib import Path, PurePosixPath
# The exact-head/clean-tree admission runs AFTER imports; suppress local .pyc
# creation so the safety check is not invalidated by our own helper import.
sys.dont_write_bytecode = True
from wp_readiness_r69 import wait_for_wordpress, ReadinessFailure, diagnose_private_cli_log

BASE='http://127.0.0.1:9438/'
SLUG='fv-apollo-review-private'
WIDTHS=(320,360,390,768,1024,1440,1920)
PLUGINS=(
 ('fv-ex2-research-desk','final-vestige-ex2-research-desk.php'),
 ('fv-ex2-evidence-atlas','final-vestige-ex2-evidence-atlas.php'),
 ('fv-ex2-apollo-suite','fv-ex2-apollo-suite.php'),
)
def digest(b):return hashlib.sha256(b).hexdigest()

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
$slug = 'fv-apollo-review-private';
if (get_page_by_path($slug, OBJECT, 'page'))
    throw new RuntimeException('REFUSE_EXISTING_CONTENT');
$id = wp_insert_post(['post_type'=>'page','post_status'=>'private',
  'post_name'=>$slug,'post_title'=>'Apollo ephemeral test only',
  'post_content'=>'[fv_ex2_apollo_suite]','comment_status'=>'closed','ping_status'=>'closed'],true);
if (is_wp_error($id) || !$id) throw new RuntimeException('LOCAL_PAGE_CREATION_FAILED');
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
                page=context.new_page();errors=[];outbound=[]
                page.on('pageerror',lambda error:errors.append('JS_ERROR'))
                def route(req):
                    if req.request.url.startswith(BASE):req.continue_()
                    else:outbound.append('OUTBOUND_BLOCKED');req.abort()
                page.route('**/*',route)
                res=page.goto(BASE+'?pagename='+SLUG,wait_until='networkidle',timeout=45000)
                assert res is not None and res.status()==200,'LOCAL_HTTP_FAILED'
                assert page.locator('.fv-ex2-apollo-suite').count()==1
                assert page.locator('[data-fvx-record]').count()==6
                assert page.locator('[data-fva-record]').count()==6
                assert page.locator('.fv-ex2-ledger__custody dd').count()==30
                assert page.locator('[data-fva-drawer] dd').count()==54
                assert page.locator('[data-fva-cite-id]').count()==6
                assert page.locator('img').count()==0
                assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2')
                assert not outbound and not errors,(outbound,errors)
                if js:
                    assert page.locator('[data-fva-atlas]').get_attribute('data-fva-ready')=='yes'
                    assert page.locator('[data-fva-to-desk]:visible').count()==6
                    if w in (390,1440):
                        page.add_script_tag(path=str(axe))
                        a=page.evaluate("""async()=>{
                          const x=await axe.run(document.querySelector('.fv-ex2-apollo-suite'),{
                            runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
                          return {violations:x.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length})),passes:x.passes.length};
                        }""")
                        report['axe'].append({'width':w,**a})
                        assert not a['violations'],a
                        img=page.screenshot(full_page=True,animations='disabled')
                        filename=f'R68_AUTHENTIC_WP_{w}.png'
                        (out/filename).write_bytes(img)
                        report['screenshots'][filename]=digest(img)
                    metric=page.evaluate("""()=>({lcp:window.__apolloLab?.lcp??null,
                      cls:window.__apolloLab?.cls??null})""")
                    report['lab'].append({'width':w,**metric,'authentic_local_lab_not_field_cwv':True})
                    assert metric['lcp'] is not None and metric['lcp']<=2500
                    assert metric['cls'] is not None and metric['cls']<=0.1
                    page.emulate_media(media='print')
                    assert page.locator('[data-fvx-record]:visible').count()==6
                    assert page.locator('[data-fva-record]:visible').count()==6
                else:
                    assert page.locator('[data-fvx-record]:visible').count()==6
                    assert page.locator('[data-fva-record]:visible').count()==6
                report['cases'].append({'width':w,'js':js,'pass':True})
                context.close()
            browser.close()
        (out/'R68_AUTHENTIC_WP_RECEIPT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
        (out/'R69_REAL_WP_ADMISSION.json').write_text(json.dumps({
          'schema':'fv.apollo.r69.admission.v1','release':'STAGING_HOLD',
          'all_actual_wordpress_cases_passed':len(report['cases'])==14,
          'axe_passed_at_390_and_1440':len(report['axe'])==2,
          'actual_wordpress_browser_evidence':True,
          'local_lab_not_hosted_cwv':True,
          'public_wordpress_writes':False
        },indent=2,sort_keys=True)+'\n')
        return report
      except Exception as exc:
        # Preserve an actionable allowlisted failure receipt. The private
        # CLI log is destroyed on exit; no raw log, URL or auth may escape.
        phase = getattr(exc,'reason',type(exc).__name__)
        safe = phase if phase in ('PLAYGROUND_EXITED','WORDPRESS_LOCAL_READINESS_TIMEOUT') else type(exc).__name__
        (out/'R69_FAIL_CLOSED_RECEIPT.json').write_text(json.dumps({
          'schema':'fv.apollo.r69.failure.v1','release':'STAGING_HOLD',
          'real_wordpress_accepted':False,'axe_accepted':False,
          'failure_category':safe,
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
