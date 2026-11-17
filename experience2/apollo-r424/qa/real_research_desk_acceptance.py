#!/usr/bin/env python3
"""R424: exact reviewed PR158 + R423 real-template integration QA. No WordPress writes.

Fails closed when real GitHub-reviewed source files are not locally available. Chromium
set_content tests real PHP-rendered output, NOT site navigation or field CWV.
"""
from __future__ import annotations
import argparse, hashlib, json, os, pathlib, re, shutil, subprocess, sys, tempfile
from html.parser import HTMLParser

PR158 = {
    'templates/ledger.html': '403d128c57b9bc82dac7c619651689070edef86c',
    'assets/source-ledger.css': 'b8cf00afeceba115a9e9d19044fc11dcf2890cbe',
    'assets/source-ledger.js': '32e757cc4dc8708397ff65ac21e89dd319781d78',
}
R423_SOURCE = '1491e5eca2f749849136d0b41cc9a2ca7b255023'
APOLLO = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
WIDTHS = (320, 360, 390, 768, 1024, 1440, 1920)


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def custody(root: pathlib.Path, expected: dict[str, str]) -> list[dict]:
    results=[]
    root_real=root.resolve()
    for relative, sha in expected.items():
        file=root/relative
        try:
            resolved=file.resolve(strict=True)
            if not resolved.is_relative_to(root_real):
                raise ValueError('symlink leaves reviewed source root')
            actual=git_blob(resolved.read_bytes())
            state='PASS' if actual == sha else 'FAIL'
            results.append({'path':relative,'expected_git_blob':sha,'actual_git_blob':actual,'state':state})
        except (OSError, ValueError) as err:
            results.append({'path':relative,'expected_git_blob':sha,'actual_git_blob':None,'state':'BLOCKED','reason':str(err)})
    return results


def php_two_instances(bridge: pathlib.Path, research: pathlib.Path) -> str:
    if not shutil.which('php'):
        raise RuntimeError('PHP executable unavailable')
    script='''<?php
error_reporting(E_ALL);
function wp_get_environment_type(){return 'staging';}
function is_singular(){return true;}
function get_queried_object_id(){return 424;}
function add_shortcode($a,$b){}
function add_action($a,$b,$c=10){}
define('ABSPATH', '/staging-only/');
define('FV_R423_ENABLED', true);
define('FV_R423_STAGING_PAGE_ID', 424);
define('FV_R423_RESEARCH_DESK_ROOT', %s);
require %s;
echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><main>';
echo fv_r423_shortcode();echo fv_r423_shortcode();
echo '</main></body></html>';
''' % (json.dumps(str(research)), json.dumps(str(bridge)))
    with tempfile.TemporaryDirectory() as d:
        p=pathlib.Path(d)/'render.php';p.write_text(script)
        proc=subprocess.run(['php',str(p)],capture_output=True,text=True,timeout=15,check=False)
        if proc.returncode or proc.stderr:
            raise RuntimeError(f'PHP renderer failed exit={proc.returncode}: {proc.stderr[:400]}')
        return proc.stdout


class FragmentIds(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.anchors=[];self.external=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a':
            self.anchors.append(a.get('href',''))
        if tag in ('iframe','form','img','canvas','video'):
            self.external.append(tag)


def browser_acceptance(html: str, css: str, js: str, out: pathlib.Path) -> dict:
    from playwright.sync_api import sync_playwright
    report={'mode':'real-PHP-rendered-template-in-memory-Chromium','tests':[],'screenshots':[],'genuine_axe':'BLOCKED: reviewed axe-core bundle unavailable','navigated_LCP_CLS':'BLOCKED: browser navigation restricted; set_content cannot verify navigation metrics','field_CWV':'UNOBSERVED'}
    def check(name, ok, details=''):
        report['tests'].append({'name':name,'pass':bool(ok),'detail':details})
        if not ok: raise AssertionError(f'{name}: {details}')
    out.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path=os.environ.get('FV_CHROMIUM','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
        try:
            for width in WIDTHS:
                page=b.new_page(viewport={'width':width,'height':820},device_scale_factor=1)
                page.set_content(html,wait_until='domcontentloaded')
                page.add_style_tag(content=css)
                page.add_script_tag(content=js)
                roots=page.locator('[data-fv-r423-bridge]')
                check(f'{width} dual source desks', roots.count()==2)
                check(f'{width} twelve authentic records',page.locator('[data-fvx-record]').count()==12)
                check(f'{width} twelve custody notes',page.locator('.fv-r423__notes li').count()==12)
                check(f'{width} no horizontal overflow',page.evaluate('document.documentElement.scrollWidth <= innerWidth'),f'width={width}')
                check(f'{width} two free-article CTAs',page.locator('.fv-ex2-ledger__footer a[href="'+APOLLO+'"]').count()==2)
                if width==390:
                    inp=page.locator('[data-fvx-search]').first
                    check('search enabled',inp.is_visible())
                    inp.fill('ignition')
                    check('first ledger search isolated', page.locator('[data-fvx-ledger]').nth(1).locator('[data-fvx-record]:visible').count()==6)
                    inp.fill('')
                    check('first ledger restored',page.locator('[data-fvx-ledger]').first.locator('[data-fvx-record]:visible').count()==6)
                    page.locator('.fv-r423__notes summary').first.focus()
                    page.keyboard.press('Enter')
                    check('native keyboard disclosure',page.locator('.fv-r423__notes details').first.get_attribute('open') is not None)
                file=out/f'{width}.png';page.screenshot(path=str(file),full_page=True,animations='disabled');report['screenshots'].append(file.name)
                page.close()
            nojs=b.new_page(java_script_enabled=False,viewport={'width':320,'height':820})
            nojs.set_content(html);nojs.add_style_tag(content=css)
            check('no JS twelve records visible',nojs.locator('[data-fvx-record]:visible').count()==12)
            check('no JS native custody disclosures',nojs.locator('.fv-r423__notes summary').count()==12)
            nojs.screenshot(path=str(out/'320-nojs.png'),full_page=True);report['screenshots'].append('320-nojs.png');nojs.close()
            for name,args in [('reduced-motion',{'reduced_motion':'reduce'}),('forced-colors',{'forced_colors':'active'})]:
                page=b.new_page(viewport={'width':390,'height':820},**args);page.set_content(html);page.add_style_tag(content=css)
                check(name+' content accessible',page.locator('[data-fvx-record]').count()==12)
                page.screenshot(path=str(out/f'390-{name}.png'),full_page=True,animations='disabled')
                report['screenshots'].append(f'390-{name}.png');page.close()
        finally: b.close()
    return report


def run(repo: pathlib.Path, bridge_dir: pathlib.Path, output: pathlib.Path, run_browser: bool=True) -> int:
    output.mkdir(parents=True,exist_ok=True)
    research=repo/'experience2/research-desk'
    bridge=bridge_dir/'staging-research-desk-bridge.php'
    receipt={'status':'HOLD','source':'R424 actual PR158 / R423 integration','pr158_commit':'250d7f05a4de037e73826dcf0cfaef0ec4c29383','r423_commit':'93dda51158453fbc8e2fcc353ef535490eac0d73','files':custody(research,PR158),'bridge':custody(bridge_dir,{'staging-research-desk-bridge.php':R423_SOURCE}),'browser':None,'blockers':[]}
    try:
        if any(x['state']!='PASS' for x in receipt['files']+receipt['bridge']):
            raise RuntimeError('Reviewed PR158 / R423 source files missing or changed; no synthetic replacement permitted')
        html=php_two_instances(bridge,research)
        dom=FragmentIds();dom.feed(html)
        if len(dom.ids)!=len(set(dom.ids)) or len([x for x in dom.anchors if x==APOLLO])!=2 or dom.external:
            raise RuntimeError('Actual dual-instance markup violates unique ID, CTA or media/form contract')
        if 'Research Desk unavailable' in html:
            raise RuntimeError('Actual R423 failed open to fallback; staging adapter not integrated')
        (output/'actual-php.html').write_text(html,encoding='utf-8')
        if run_browser:
            css=(research/'assets/source-ledger.css').read_text()+'\n'+(bridge_dir/'assets/bridge.css').read_text()
            js=(research/'assets/source-ledger.js').read_text()
            receipt['browser']=browser_acceptance(html,css,js,output/'screenshots')
        receipt['status']='LOCAL_PASS_RELEASE_HOLD'
    except Exception as err:
        receipt['blockers'].append(str(err))
    receipt['release']='HARD_HOLD: no installed WP staging, genuine axe, navigated LCP/CLS, independent QD, exact-head CI or founder approval'
    (output/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return 0 if receipt['status']=='LOCAL_PASS_RELEASE_HOLD' else 2


if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--repo',type=pathlib.Path,required=True,help='Git checkout with exact PR158 files');a.add_argument('--bridge-dir',type=pathlib.Path,required=True,help='Local R423 checkout');a.add_argument('--output',type=pathlib.Path,required=True);a.add_argument('--skip-browser',action='store_true')
    args=a.parse_args();sys.exit(run(args.repo,args.bridge_dir,args.output,not args.skip_browser))
