"""R430 fail-closed source custody + actual executed PHP assertions. Does not claim WP staging."""
from pathlib import Path
import hashlib
import shutil
import subprocess
import tempfile
import json

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parent
EXPECTED = {
    'staging-attribution-bridge.php': 'c604bccf9873688ec1d9b64187d1a9a7fdcf89ac',
    'assets/bridge.css': '15942f8ef27d82695c8d2af8bdc8a807396da33e',
}
assertions=[]
def ok(name, condition):
    if not condition:
        raise AssertionError(name)
    assertions.append(name)

def blob(raw): return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\x00'+raw).hexdigest()
for rel, sha in EXPECTED.items():
    p=ROOT/'apollo-r429'/rel
    ok(f'parent exact Git blob {rel}',p.is_file() and not p.is_symlink() and blob(p.read_bytes())==sha)

# Exercise independent PHP processes so require_once cannot hide mutated dependencies.
def run_php(directory, code):
    p=directory/'apollo-r430'/'staging-educator-case-lab.php'
    snippet=f'define("ABSPATH",__DIR__);require {json.dumps(str(p))};'+code
    return subprocess.run(['php','-r',snippet],capture_output=True,text=True,check=True).stdout

with tempfile.TemporaryDirectory() as tmp:
    t=Path(tmp)
    shutil.copytree(HERE,t/'apollo-r430',ignore=shutil.ignore_patterns('QA','__pycache__'))
    shutil.copytree(ROOT/'apollo-r429',t/'apollo-r429')
    ok('verified trusted parent',run_php(t,'echo fv_r430_verified_sources()?"yes":"no";')=='yes')
    ok('staging fails closed by default',run_php(t,'echo fv_r430_allowed()?"yes":"no";')=='no')
    output=run_php(t,'echo fv_r430_render(1,[]),fv_r430_render(2,[]);')
    ok('two source-backed instances',output.count('data-fv-r430')==2)
    ok('six R429 source stages',output.count('class="fv-r429__plate"')==6)
    ok('six original reasoning questions',output.count('class="fv-r430__question"')==6)
    ok('two free investigation CTAs',output.count('class="fv-r429__cta"')==2)
    ok('native instructor notes',output.count('<details class="fv-r430__reason">')==6)
    ok('NASA primary and retrospective source preserved', 'Apollo 204 Review Board' in output and '2018-02-14' in output)
    ok('no images, scripts, or forms', all(x not in output for x in ['<img','<script','<form']))
    ok('no purchase/link insertion',not any(x in output.lower() for x in ['payhip','checkout','affiliate']))
    ok('no remote collection',not any(x in output for x in ['method="post"','type="submit"']))
    ok('question IDs scoped to instances', 'fv-r430-1-q1' in output and 'fv-r430-2-q1' in output)
    ok('CTA untagged by default',output.count('href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"')==2)
    ok('single documented fallback', 'fv-r430-fallback' in run_php(t,'echo fv_r430_render(41,[]);'))
    # Explicit permission only after a genuine WordPress staging env + single page ID.
    cases = [
       ('staging',123,True,123,True),('production',123,True,123,False),
       ('staging',124,True,123,False),('staging',123,False,123,False),
    ]
    for env,page,singular,expected,should_pass in cases:
        code=(f'define("FV_R430_ENABLED",true);define("FV_R430_STAGING_PAGE_ID",{expected});'
              f'function wp_get_environment_type(){{return "{env}";}}'
              f'function is_singular(){{return {str(singular).lower()};}}'
              f'function get_queried_object_id(){{return {page};}}'
              'echo fv_r430_allowed()?"yes":"no";')
        ok(f'env gate {env}/{page}/{singular}',(run_php(t,code)=='yes')==should_pass)
    bad_code='echo fv_r430_render(1,[]);'
    css=t/'apollo-r429'/'assets'/'bridge.css'
    css.write_text(css.read_text()+'/* modified */')
    ok('tampered parent CSS produces safe article fallback', 'fv-r430-fallback' in run_php(t,bad_code))
    css.unlink();css.symlink_to(ROOT/'apollo-r429'/'assets'/'bridge.css')
    ok('symlinked parent CSS rejected', 'fv-r430-fallback' in run_php(t,bad_code))
    css.unlink();shutil.copyfile(ROOT/'apollo-r429'/'assets'/'bridge.css',css)
    original_php=t/'apollo-r429'/'staging-attribution-bridge.php'
    original_php.write_text(original_php.read_text()+'/* modified */')
    ok('tampered parent PHP produces safe article fallback', 'fv-r430-fallback' in run_php(t,bad_code))

result={'assertions':len(assertions),'passed':assertions,'parent_blobs':EXPECTED,'runtime':'Local PHP; no WordPress staging install','result':'PASS'}
(HERE/'QA').mkdir(exist_ok=True)
(HERE/'QA'/'contract_results.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
print(f'PASS {len(assertions)}/{len(assertions)} contract assertions')
