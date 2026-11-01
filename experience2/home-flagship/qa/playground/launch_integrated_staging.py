#!/usr/bin/env python3
"""Run the *existing*, complete FV Gutenberg release candidate in isolated WP Playground.

No WordPress.com API, deployment, CMS writes, or external non-loopback staging.
Blueprint must have been independently built by the exact PR #414 assembler;
this runner never constructs an alternative homepage or establishes image rights.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
import socket
import uuid
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
from urllib.parse import urlsplit
from datetime import datetime, timezone
from urllib.request import build_opener, HTTPRedirectHandler

THEME_URL = 'https://public-api.wordpress.com/rest/v1/themes/download/assembler.zip'
SITE_PREFIX = '/wordpress/wp-content/plugins/fv-ex2-playground/'
MEDIA_SOURCES = {
    'apollo.webp': ('https://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp', 78346),
    'franklin.jpg': ('https://finalvestige.com/wp-content/uploads/2026/08/Franklinexpeditionnote.jpg', 466043),
    'nypl.jpg': ('https://finalvestige.com/wp-content/uploads/2026/08/edit-017-v02-nypl-5003296-original.jpg', 5553669),
}
EXPECTED_SCRIPT = 'verify_playground_browser.py'
DIGEST = re.compile(r'^[a-f0-9]{64}$')

class Hold(RuntimeError):
    pass

def require(condition, message):
    if not condition:
        raise Hold('STAGING ADMISSION HOLD: '+message)

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def regular_private(path: Path, label: str) -> bytes:
    require(path.is_file() and not path.is_symlink(), label+' must be a regular, non-symlink file')
    require(path.stat().st_size > 0, label+' must not be empty')
    if os.name == 'posix':
        require(not (path.stat().st_mode & 0o077), label+' has group/other access; chmod 600 first')
    return path.read_bytes()

def check_blueprint(path: Path, supplied_sha: str) -> dict:
    require(bool(DIGEST.fullmatch(supplied_sha or '')), 'independent reviewed Blueprint SHA-256 required')
    raw=regular_private(path, 'private integrated Blueprint')
    require(sha(raw)==supplied_sha, 'Blueprint changed since approved hash')
    data=json.loads(raw)
    steps=data.get('steps')
    require(isinstance(steps,list) and len(steps)==19,'exact 19-step integrated Blueprint required')
    require(steps[0].get('step')=='defineWpConfigConsts' and
            steps[0].get('consts')=={'WP_ENVIRONMENT_TYPE':'local','FV_EX2_ALLOW_LOCAL_REVIEW':True},
            'not an exact local-only WordPress environment')
    require(steps[1].get('step')=='installTheme' and
            steps[1].get('themeData')=={'resource':'url','url':THEME_URL} and
            steps[1].get('options',{}).get('activate') is True,
            'not the reviewed official Assembler theme')
    require(steps[17].get('step')=='activatePlugin' and
            steps[17].get('pluginPath')=='fv-ex2-playground/fv-ex2-playground.php',
            'unreviewed stage plugin activation')
    require(all(s.get('step')=='writeFile' for s in steps[2:17]),'unreviewed WordPress writes or DB imports')
    paths=[s.get('path') for s in steps[2:17]]
    require(len(paths)==len(set(paths)) and all(isinstance(p,str) and p.startswith(SITE_PREFIX) and '..' not in p for p in paths),
            'plugin media/source path traversal or duplicate')
    require(set(paths)==({SITE_PREFIX+'fv-ex2-playground.php'} |
            {SITE_PREFIX+'assets/'+n for n in ('wordpress-page-fragment.review-only.html','flagship.css','chronicle.css','chronicle-lens.css','inquiry.css','observer-lab.css','reading-trail.css','flagship.js','observer-lab.js','chronicle-lens.js','reading-trail.js')} |
            {SITE_PREFIX+'media/'+n for n in MEDIA_SOURCES}),
            'source, style, script or media payload inventory drift')
    for s in steps[2:17]:
        p=s['path']
        if '/media/' in p:
            n=p.rsplit('/',1)[-1]
            require(s.get('data')=={'resource':'url','url':MEDIA_SOURCES[n][0]},n+': expected original download URL, no CDN derivative')
        else:
            require(isinstance(s.get('data'),str) and len(s['data'])>30,p+': source content absent')
    plugin=next(s['data'] for s in steps if s.get('path')==SITE_PREFIX+'fv-ex2-playground.php')
    require('fv_ex2_ready()' in plugin and 'render_block' in plugin and 'fv_ex2_integrity()' in plugin,
            'local plugin does not guard exact Gutenberg renderer and original media')
    require(steps[18].get('step')=='runPHP' and isinstance(steps[18].get('code'),str),'real WordPress bootstrap missing')
    php=steps[18]['code']
    for token in ('wp_insert_post(',"get_stylesheet() !== 'assembler'", "wp_get_environment_type() !== 'local'",
                  'page_on_front',"$raw=base64_decode('","substr_count($raw,'--i:') !== 72",
                  "substr_count($raw,'<!-- wp:jetpack/subscriptions') !== 1",'data-fv-home-flagship'):
        require(token in php,'integrated Gutenberg identity guard missing: '+token[:40])
    require('finalvestige.com' not in php and 'https://' not in php,
            'bootstrap unexpectedly references production/external destination')
    return {'blueprint_sha256':sha(raw),'blueprint_bytes':len(raw),'steps':len(steps),'media_count':3,
            'source_asset_count':11,'integrated_gutenberg_guard':'PRESENT',
            'blueprint_is_public_url':'NO', 'environment':'local'}

def check_manifest(path: Path) -> dict:
    x=json.loads(regular_private(path,'independently attested media manifest'))
    require(isinstance(x,dict) and x.get('purpose')=='isolated-staging-media-review' and
            isinstance(x.get('images'),dict) and set(x['images'])==set(MEDIA_SOURCES),
            'original-media manifest incomplete')
    for name,(url,size) in MEDIA_SOURCES.items():
        r=x['images'][name]
        require(isinstance(r,dict) and r.get('source_url')==url and type(r.get('bytes')) is int
                and r['bytes']==size and bool(DIGEST.fullmatch(r.get('sha256',''))),
                name+': original-image source, byte length or independently reviewed digest absent')
    return {'original_manifest_schema':'PASS','images':list(MEDIA_SOURCES),'rights_clearance':'UNVERIFIED'}

def check_axe(path: Path, expected_sha: str) -> dict:
    require(bool(DIGEST.fullmatch(expected_sha or '')),'independent axe-core JS SHA-256 required')
    raw=regular_private(path,'local axe-core JS')
    require(len(raw)>10000 and sha(raw)==expected_sha,'axe-core source incomplete or SHA-256 mismatch')
    return {'axe_local_bytes':len(raw),'axe_sha256':sha(raw),'axe_executed':False}

def check_runner(path: Path, approved_sha: str) -> dict:
    require(bool(DIGEST.fullmatch(approved_sha or '')),
            'independent reviewed browser-runner SHA-256 required')
    require(path.name==EXPECTED_SCRIPT and path.is_file() and not path.is_symlink(),
            'existing verified WordPress browser acceptance harness required')
    raw=path.read_bytes()
    require(sha(raw)==approved_sha, 'browser runner differs from independently approved SHA-256')
    require(b'from integrated_admission_checks import' in raw and b'audit_archive_gallery' in raw
            and b'BrowserEvidencePage' in raw and b'axe.run' in raw,
            'browser harness does not include integrated, image-byte and axe admission')
    return {'browser_runner_sha256':sha(raw),'browser_runner':str(path),'source':'independent exact PR checkout must be verified separately'}

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        raise Hold('HTTP redirect disallowed during local stage readiness')

def port_vacant(port: int) -> None:
    """Refuse already-bound localhost; a 200 from a different service is not WP proof."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.bind(('127.0.0.1', port))
    except OSError as exc:
        raise Hold('STAGING ADMISSION HOLD: stage port occupied or unavailable; '+str(exc)) from exc

def local_ready(port,timeout,proc=None):
    url=f'http://127.0.0.1:{port}/'
    require(urlsplit(url).hostname=='127.0.0.1','only loopback server permitted')
    op=build_opener(NoRedirect)
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        if proc is not None and proc.poll() is not None:
            raise Hold('STAGING ADMISSION HOLD: Playground process exited before ready')
        try:
            with op.open(url, timeout=1) as res:
                if res.status==200: return url
        except Exception:
            pass
        time.sleep(.5)
    raise Hold('actual local WordPress HTTP root never reached 200; server did not become ready')

def check_executable(path: Path | None, approved_sha: str, label: str) -> Path:
    require(path is not None and path.is_file() and not path.is_symlink()
            and os.access(path, os.X_OK), label+' executable missing, symlinked or not permitted')
    require(bool(DIGEST.fullmatch(approved_sha or '')), label+' independent reviewed SHA-256 required')
    require(sha(path.read_bytes()) == approved_sha, label+' executable differs from approved SHA-256')
    return path.resolve()

def measured_lighthouse(path: Path, requested_url: str, label: str) -> dict:
    """A JSON file alone is not evidence of a successful Lighthouse run."""
    report=json.loads(path.read_text(encoding='utf-8'))
    require(isinstance(report,dict) and isinstance(report.get('lighthouseVersion'),str)
            and not report.get('runtimeError'),label+': Lighthouse report incomplete or runtime failed')
    require(report.get('requestedUrl')==requested_url,label+': Lighthouse audited unexpected URL')
    final=report.get('finalDisplayedUrl')
    a,b=urlsplit(final or ''),urlsplit(requested_url)
    require((a.scheme,a.netloc,a.path)==(b.scheme,b.netloc,b.path),
            label+': Lighthouse navigated away from exact local stage URL')
    audits=report.get('audits')
    require(isinstance(audits,dict),label+': Lighthouse audits missing')
    vals={}
    for key,alias in [('largest-contentful-paint','lcp_ms'),('cumulative-layout-shift','cls'),
                      ('total-blocking-time','tbt_ms')]:
        item=audits.get(key)
        v=item.get('numericValue') if isinstance(item,dict) else None
        require(type(v) in (int,float) and math.isfinite(v) and v>=0,
                label+': Lighthouse '+key+' missing/invalid')
        vals[alias]=v
    perf=report.get('categories',{}).get('performance',{}).get('score')
    require(type(perf) in (int,float) and math.isfinite(perf) and 0<=perf<=1,
            label+': Lighthouse performance score missing')
    vals['performance_score']=perf
    vals['good_lab_lcp']=vals['lcp_ms']<=2500
    vals['good_lab_cls']=vals['cls']<=0.1
    vals['lab_not_field']=True
    return vals

def write_receipt(private_dir: Path, report: dict) -> Path:
    """Append an immutable per-run report; never reuse a stale success/failure file."""
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    name=f'FV_STAGE_LAUNCH_RECEIPT_{stamp}_{uuid.uuid4().hex[:10]}.json'
    path=private_dir/name
    report['receipt_file']=name
    payload=json.dumps(report,indent=2,sort_keys=True)+'\n'
    flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL
    if hasattr(os,'O_NOFOLLOW'):flags|=os.O_NOFOLLOW
    fd=os.open(path,flags,0o600)
    with os.fdopen(fd,'w',encoding='utf-8') as output:output.write(payload)
    return path

def run(args, receipt: dict) -> None:
    require(1025<=args.port<=65535,'nonprivileged local TCP port required')
    playground=check_executable(args.playground_cli,args.playground_cli_sha256,'Playground CLI')
    lighthouse=check_executable(args.lighthouse_cli,args.lighthouse_cli_sha256,'Lighthouse CLI')
    port_vacant(args.port)
    require(Path(args.output_dir).resolve().is_relative_to(Path(args.private_dir).resolve()),
            'output receipts/screenshots must remain inside private workspace')
    require(not args.output_dir.is_symlink(),'output workspace symlink refused')
    args.output_dir.mkdir(parents=True,exist_ok=True,mode=0o700)
    if os.name=='posix':
        require(not (args.output_dir.stat().st_mode & 0o077),'output workspace is group/other accessible')
    launch=[str(playground),'server',f'--blueprint={str(args.blueprint.resolve())}',
            f'--port={args.port}','--php=8.3']
    receipt['launch_argv_no_secrets']=launch[1:]
    log=args.output_dir/'WORDPRESS_PLAYGROUND_STARTUP.log'
    with log.open('xb') as output:
        os.chmod(log,0o600)
        proc=subprocess.Popen(launch,cwd=str(args.private_dir),stdin=subprocess.DEVNULL,
                               stdout=output,stderr=subprocess.STDOUT,start_new_session=(os.name=='posix'))
        try:
            url=local_ready(args.port,args.ready_timeout,proc)
            receipt['actual_local_http_200']=True
            cmd=[sys.executable,str(args.browser_runner.resolve()),'--url',url,
                 '--axe-js',str(args.axe_js.resolve()),'--trusted-media-manifest',str(args.media_manifest.resolve()),
                 '--output-dir',str(args.output_dir.resolve())]
            verdict=subprocess.run(cmd,cwd=str(args.browser_runner.parent),timeout=args.browser_timeout,
                                   stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            receipt['chromium_wordpress_exit_code']=verdict.returncode
            (args.output_dir/'BROWSER_RUN_OUTPUT.log').write_text((verdict.stdout+'\n'+verdict.stderr)[:18000])
            require(verdict.returncode==0,'actual WordPress/Assembler Chromium+axe admission did not pass')
            receipt['wordpress_rendered']=True
            receipt['axe_verified']=True
            receipt['browser_image_custody_verified']=True
            receipt['interactive_stage_verified']=True
            for label, extra in [('mobile',[]),('desktop',['--preset=desktop'])]:
                out=args.output_dir/f'LIGHTHOUSE_{label.upper()}.json'
                lh=[str(lighthouse),url,'--output=json',f'--output-path={out}',
                    '--quiet','--chrome-flags=--headless --no-sandbox',*extra]
                v=subprocess.run(lh,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=180)
                require(v.returncode==0 and out.is_file(),label+': Lighthouse did not produce measured lab evidence')
                receipt.setdefault('lighthouse',{})[label]=measured_lighthouse(out,url,label)
            receipt['lighthouse_measured']=True
            require(all(r['good_lab_lcp'] and r['good_lab_cls'] for r in receipt['lighthouse'].values()),
                    'one or more Lighthouse lab LCP/CLS budgets exceeded; release remains on HOLD')
            receipt['status']='ISOLATED_WORDPRESS_LAB_EVIDENCE_COLLECTED_RELEASE_HOLD'
        finally:
            if proc.poll() is None:
                try:
                    if os.name=='posix':os.killpg(proc.pid,signal.SIGTERM)
                    else:proc.terminate()
                except ProcessLookupError:pass
                try:proc.wait(timeout=8)
                except subprocess.TimeoutExpired:proc.kill();proc.wait()

def main(argv=None):
    p=argparse.ArgumentParser(description='Safe local-only integrated seven-chapter WordPress stage and measured browser gate')
    p.add_argument('--blueprint',type=Path,required=True)
    p.add_argument('--blueprint-sha256',required=True)
    p.add_argument('--media-manifest',type=Path,required=True)
    p.add_argument('--axe-js',type=Path,required=True)
    p.add_argument('--axe-sha256',required=True)
    p.add_argument('--browser-runner',type=Path,required=True)
    p.add_argument('--browser-runner-sha256',required=True,help='independently reviewed exact browser harness fingerprint')
    p.add_argument('--private-dir',type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--execute',action='store_true',help='run installed Playground CLI and actual WordPress/Chromium/axe/Lighthouse')
    p.add_argument('--playground-cli',type=Path)
    p.add_argument('--playground-cli-sha256',help='independently reviewed executable fingerprint')
    p.add_argument('--lighthouse-cli',type=Path)
    p.add_argument('--lighthouse-cli-sha256',help='independently reviewed executable fingerprint')
    p.add_argument('--port',type=int,default=19400)
    p.add_argument('--ready-timeout',type=int,default=75)
    p.add_argument('--browser-timeout',type=int,default=240)
    args=p.parse_args(argv)
    report={'status':'FAILED_CLOSED','mode':'EXECUTE' if args.execute else 'PREFLIGHT_ONLY',
            'wordpress_rendered':False,'rights_verified':False,'jetpack_delivery_verified':False,
            'hosted_wpcom_equivalence':False,'field_cwv_measured':False,'ci_qd_approved':False}
    try:
        require(args.private_dir.is_dir() and not args.private_dir.is_symlink(),'private workspace required')
        if os.name=='posix':
            require(not (args.private_dir.stat().st_mode & 0o077),'private workspace is group/other accessible')
        require(args.blueprint.resolve().is_relative_to(args.private_dir.resolve()),'Blueprint must remain in private workspace')
        report.update(check_blueprint(args.blueprint,args.blueprint_sha256))
        report.update(check_manifest(args.media_manifest))
        report.update(check_axe(args.axe_js,args.axe_sha256))
        report.update(check_runner(args.browser_runner,args.browser_runner_sha256))
        if args.execute:run(args,report)
        else:report['status']='PRIVATE_BLUEPRINT_PREFLIGHT_PASSED_NOT_WORDPRESS_EXECUTED'
    except Exception as exc:
        report['error_type']=type(exc).__name__
        report['reason']=str(exc)[:450]
        report['status']='FAILED_CLOSED'
    finally:
        args.private_dir.mkdir(parents=True,exist_ok=True)
        write_receipt(args.private_dir,report)
        print(json.dumps(report,indent=2))
    return 0 if report['status'].startswith('PRIVATE_BLUEPRINT_PREFLIGHT_') or report['status']=='ISOLATED_WORDPRESS_LAB_EVIDENCE_COLLECTED_RELEASE_HOLD' else 1

if __name__=='__main__':sys.exit(main())
