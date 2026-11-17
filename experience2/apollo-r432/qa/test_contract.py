"""Exact real PHP custody-gate tests. Mutations occur ONLY in isolated temp copies."""
import base64, hashlib, json, shutil, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parents[1]
PINS={
 'apollo-r429/staging-attribution-bridge.php':'c604bccf9873688ec1d9b64187d1a9a7fdcf89ac',
 'apollo-r429/assets/bridge.css':'15942f8ef27d82695c8d2af8bdc8a807396da33e',
 'apollo-r430/staging-educator-case-lab.php':'11a30d871bb0c5840aa3ee8932e12a6068b50cd3',
 'apollo-r430/assets/educator-case-lab.css':'be6880577faed2453f5633a3718fce8dedf9ac3b',
 'apollo-r431/staging-evidence-notebook.php':'32d827d3ae5aa432c350d9db867e4131c8dfb935',
 'apollo-r431/assets/evidence-notebook.css':'7dae0a5f73a434b40dc9b728657308c07d3b7c0e',
 'apollo-r431/assets/evidence-notebook.js':'87dfe1b7d5bba87bbe3eb461f919eee16a7815c2',
}
def gitblob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\x00'+b).hexdigest()
def php(script,cwd):
 p=subprocess.run(['php','-r',script],cwd=cwd,capture_output=True,text=True,timeout=15)
 if p.returncode:raise AssertionError(p.stderr)
 return p.stdout
CHECKS=0
def ok(test,msg):
 global CHECKS
 assert test,msg
 CHECKS+=1

def main():
 for rel,sha in PINS.items():ok(gitblob((ROOT/rel).read_bytes())==sha,'pin '+rel)
 fixture=subprocess.run(['php',str(HERE/'qa/fixture.php')],capture_output=True,text=True,check=True)
 body=fixture.stdout.split('</style></head><body>',1)[-1].split('<script>',1)[0]
 ok(body.count('data-fv-r432')==2,'two real instances')
 ok(body.count('class="fv-r429__plate"')==6,'six real source plates')
 ok(body.count('class="fv-r430__question"')==6,'six real worksheet questions')
 ok(body.count('class="fv-r429__cta"')==2,'single CTA per instance')
 ok(body.count('data-fv-r431-actions')==2,'parent progressive controls present')
 ok('apollo_documentary_001' in body,'approved Grok asset preserved')
 ok('https://www.nasa.gov/nasa-brand-center/images-and-media/' in body,'actual media policy cited')
 ok('data-fv-r432' in body and 'NASA does not endorse' in body,'visible source custody')
 ok('payhip.com' not in body and 'href="https://checkout' not in body, 'no unverified checkout CTA')
 ok('data-fv-r432' in php("define('ABSPATH',1);require 'apollo-r432/staging-custody-gate.php';echo fv_r432_render(1,[]);",ROOT),'clean render')
 badq={'utm_source':'youtube','utm_medium':'organic_social','utm_campaign':'history_pilot_2026_11','utm_content':'<img src=x onerror=alert(1)>'}
 src=base64.b64encode(json.dumps(badq).encode()).decode()
 qphp="define('ABSPATH',1);require 'apollo-r432/staging-custody-gate.php';echo fv_r432_render(1,json_decode(base64_decode('"+src+"'),true));"
 # The inherited target accepts only validated, literal lowercase asset IDs.
 ok('onerror' not in php(qphp,ROOT),'invalid campaign rejected')
 # Verify all 7 objects fail closed, including JS/CSS that the previous wrapper did not pin.
 with tempfile.TemporaryDirectory() as temp:
  clone=Path(temp)/'experience2';clone.mkdir()
  for version in ['apollo-r429','apollo-r430','apollo-r431','apollo-r432']:
   shutil.copytree(ROOT/version,clone/version,ignore=shutil.ignore_patterns('QA','__pycache__'))
  test="define('ABSPATH',1);require 'apollo-r432/staging-custody-gate.php';echo fv_r432_verified()?'OK':'HOLD';"
  ok(php(test,clone)=='OK','isolated clean clone accepted')
  for rel in PINS:
   f=clone/rel; original=f.read_bytes();f.write_bytes(original+b'\n// tamper\n')
   ok(php(test,clone)=='HOLD','tamper rejected '+rel)
   f.write_bytes(original)
  for rel in PINS:
   f=clone/rel;missing=f.with_name(f.name+'.away');f.rename(missing)
   ok(php(test,clone)=='HOLD','missing rejected '+rel)
   missing.rename(f)
  css=clone/'apollo-r431/assets/evidence-notebook.css'
  original=css.read_bytes();css.unlink();css.symlink_to(clone/'apollo-r430/assets/educator-case-lab.css')
  ok(php(test,clone)=='HOLD','symlink refused');css.unlink();css.write_bytes(original)
  # Confirm WordPress gate cannot be bypassed by an otherwise pristine source tree.
  ok('Read the free Apollo 1 investigation' in php("define('ABSPATH',1);require 'apollo-r432/staging-custody-gate.php';echo fv_r432_shortcode();",clone),'disabled shortcode free-article fallback')
 report={'status':'PASS_LOCAL_CONTRACT','checks':CHECKS,'pins':PINS,'actual_fixture':'PHP-rendered source from exact R429/R430/R431 dependencies','staging':'NOT TESTED','revenue':'NOT MEASURED'}
 (HERE/'QA').mkdir(exist_ok=True)
 (HERE/'QA/contract.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
 print('PASS',CHECKS,'local custody/attribution/adversarial checks')
if __name__=='__main__':main()
