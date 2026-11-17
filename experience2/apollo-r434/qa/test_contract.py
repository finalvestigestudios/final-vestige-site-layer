"""R434 exact-source custody, fail-open and conversion-link tests; no CMS/network writes."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from urllib.parse import parse_qs, urlparse
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / 'apollo-r434'
PINNED = {
    'apollo-r433/staging-claim-bridge.php': 'e48e577d0d14964ba77a86f5fc66db6f2c37a830',
    'apollo-r433/assets/claim-bridge.css': '548c3b479e5003a925babbdebbb43712443675a9',
}
checks = 0

def ok(condition, label):
    global checks
    assert condition, label
    checks += 1

def run_php(code: str, cwd: Path = ROOT):
    proc = subprocess.run(['php','-r',code], cwd=cwd, text=True, capture_output=True)
    ok(proc.returncode == 0, f'PHP process failed: {proc.stderr}')
    return proc.stdout

def blob(path):
    data = path.read_bytes()
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\x00' + data).hexdigest()

def main():
    ok(subprocess.run(['php','-l',str(HERE/'staging-research-route.php')],capture_output=True).returncode==0, 'PHP syntax')
    for name, expected in PINNED.items():
        ok(blob(ROOT/name) == expected, 'source pinned '+name)
    phpfile = HERE/'staging-research-route.php'
    program = 'define("ABSPATH","/test/");require '+json.dumps(str(phpfile))+';'
    ok(run_php(program+'echo fv_r434_verify()?"ok":"bad";') == 'ok','real parents match')
    ok(run_php(program+'echo fv_r434_allowed()?"ok":"no";') == 'no','default staging disabled')
    ok('free Apollo 1 investigation' in run_php(program+'echo fv_r434_shortcode();'), 'production/no-config fallback')
    ok(run_php(program+'echo fv_r434_parent()?"ok":"bad";') == 'ok','upstream seven-object chain is authentic')
    ok(run_php(program+'echo fv_r434_render(31,[]);').find('temporarily unavailable')>=0,'out-of-bound instance fallback')
    ok(run_php(program+'echo fv_r434_render(0,[]);').find('temporarily unavailable')>=0,'zero instance fallback')
    ok(run_php('define("ABSPATH","/test/");function fv_r433_render(){};require '+json.dumps(str(phpfile))+';echo fv_r434_render(1,[]);').find('temporarily unavailable')>=0,'reject preloaded untrusted function')
    allowed='define("ABSPATH","/test/");define("FV_R434_ENABLED",true);define("FV_R434_STAGING_PAGE_ID",123);function wp_get_environment_type(){return "staging";}function is_singular(){return true;}function get_queried_object_id(){return 123;}'
    ok('<section class="fv-r434"' in run_php(allowed+';require '+json.dumps(str(phpfile))+';echo fv_r434_shortcode();'),'explicit staged shortcode renders')
    denied=allowed.replace('return 123;', 'return 124;')
    ok('temporarily unavailable' in run_php(denied+';require '+json.dumps(str(phpfile))+';echo fv_r434_shortcode();'),'wrong WP page fallback')
    raw=subprocess.run(['php',str(HERE/'qa/fixture.php')],text=True,capture_output=True,check=True).stdout
    soup=BeautifulSoup(raw,'html.parser')
    routes=soup.select('[data-fv-r434]')
    ok(len(routes)==2,'two actual PHP-rendered instances')
    for n, route in enumerate(routes,1):
        cta=route.select('.fv-r429__cta')
        ok(len(cta)==1,f'one and only one article CTA per instance {n}')
        ok(cta[0].find_parent('details') is None, f'CTA visible before expanded notes {n}')
        ok(route.select('details.fv-r434__deep'), f'complete historical archive still present {n}')
        ok(len(route.select('.fv-r434__row'))==3, f'visible grounded chronological overview {n}')
        ok(len(route.select('.fv-r433__claim'))==3, f'actual inherited claims {n}')
        ok(len(route.select('.fv-r429__plate'))==3, f'actual inherited R429 plates {n}')
        ok(len(route.select('.fv-r430__question'))==3, f'actual inherited educator questions {n}')
        ok(len(route.select('[data-fv-r431-actions]'))==1, f'actual inherited notebook {n}')
        ok(not route.select('a[href*="payhip"],a[href*="checkout"],form'), f'no unapproved merchant or lead form {n}')
        ok(cta[0]['href'].startswith('https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'),f'canonical article href {n}')
        ok(all(a['href'].startswith('https://www.nasa.gov/') for a in route.select('.fv-r434__row a')),f'NASA sources only {n}')
    ids=[a['id'] for a in soup.select('[id]')]
    ok(len(ids)==len(set(ids)), 'distinct IDs between all nested components')
    q=parse_qs(urlparse(routes[0].select_one('.fv-r429__cta')['href']).query)
    ok(q=={'utm_source':['youtube'],'utm_medium':['organic_social'],'utm_campaign':['history_pilot_2026_11'],'utm_content':['fixture_not_a_published_asset']},'valid allowlisted test UTMs survive')
    ok(not urlparse(routes[1].select_one('.fv-r429__cta')['href']).query,'plain visitor has no invented attribution')
    bad='["utm_source"=>"javascript:alert(1)","utm_medium"=>"organic_social","utm_campaign"=>"history_pilot_2026_11","utm_content"=>"foo-bar"]'
    bad_out=run_php(program+'echo fv_r434_render(1,'+bad+');')
    ok('class="fv-r434"' in bad_out,'invalid attribution still shows the free experience')
    invalid_soup=BeautifulSoup(bad_out,'html.parser')
    ok('?' not in invalid_soup.select_one('.fv-r429__cta')['href'],'invalid attribution fails to plain canonical URL')
    # Test both mutation and symlink attack in an independent copy, never in checked-in source.
    with tempfile.TemporaryDirectory(prefix='fv-r434-check-') as d:
        work=Path(d)/'experience2'
        for name in ['apollo-r429','apollo-r430','apollo-r431','apollo-r432','apollo-r433','apollo-r434']:
            shutil.copytree(ROOT/name,work/name,ignore=shutil.ignore_patterns('QA'))
        target=work/'apollo-r433/staging-claim-bridge.php'
        target.write_bytes(target.read_bytes()+b'\n/* deliberate mutation */\n')
        prog='define("ABSPATH","/test/");require '+json.dumps(str(work/'apollo-r434/staging-research-route.php'))+';echo fv_r434_render(1,[]);'
        ok('temporarily unavailable' in run_php(prog,cwd=work),'R433 PHP mutation refuses render')
        target.write_bytes((ROOT/'apollo-r433/staging-claim-bridge.php').read_bytes())
        linked=work/'apollo-r433/assets/claim-bridge.css'
        linked.unlink()
        linked.symlink_to(ROOT/'apollo-r433/assets/claim-bridge.css')
        ok('temporarily unavailable' in run_php(prog,cwd=work),'symlinked CSS refuses render')
    report={'status':'PASS_LOCAL_CONTRACT_ONLY','checks':checks,'sources':PINNED,'browser_staging':'NOT_TESTED','merchant_sales':'NOT_VERIFIED'}
    dest=HERE/'QA/contract-report.json'
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(f'PASS {checks} R434 source, conversion and negative contract assertions (LOCAL ONLY)')

if __name__=='__main__':main()
