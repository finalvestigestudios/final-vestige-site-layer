"""R437 executable source identity, staging gate, fallback and source/date contract tests."""
import hashlib, html.parser, json, re, shutil, subprocess, tempfile
from pathlib import Path
here=Path(__file__).resolve().parents[1]
root=here.parent
checks=0
failures=[]
def check(condition,label):
 global checks
 checks+=1
 if not condition: failures.append(label)
def php_script(code):
 p=subprocess.run(['php','-r',code],capture_output=True,text=True,cwd=here)
 return p.returncode,p.stdout,p.stderr
for path in [here/'staging-chronology-audit.php',here/'qa/fixture.php']:
 p=subprocess.run(['php','-l',str(path)],capture_output=True,text=True)
 check(p.returncode==0,'PHP syntax '+path.name)
ret,out,err=php_script("define('ABSPATH','/qa/');require 'staging-chronology-audit.php';echo fv_r437_verify() ? 'PASS':'FAIL';")
check(ret==0 and out=='PASS','all four exact source identities')
ret,out,err=php_script("define('ABSPATH','/qa/');require 'staging-chronology-audit.php';echo fv_r437_allowed() ? 'BAD':'SAFE';")
check(ret==0 and out=='SAFE','not self activating')
ret,out,err=php_script("define('ABSPATH','/qa/');define('FV_R437_ENABLED',true);define('FV_R437_STAGING_PAGE_ID',49);function wp_get_environment_type(){return 'production';}function is_singular(){return true;}function get_queried_object_id(){return 49;}require 'staging-chronology-audit.php';echo fv_r437_allowed() ? 'BAD':'SAFE';")
check(ret==0 and out=='SAFE','production blocked despite correct page')
ret,out,err=php_script("define('ABSPATH','/qa/');define('FV_R437_ENABLED',true);define('FV_R437_STAGING_PAGE_ID',49);function wp_get_environment_type(){return 'staging';}function is_singular(){return true;}function get_queried_object_id(){return 50;}require 'staging-chronology-audit.php';echo fv_r437_allowed() ? 'BAD':'SAFE';")
check(ret==0 and out=='SAFE','wrong page blocked')
ret,out,err=php_script("define('ABSPATH','/qa/');define('FV_R437_ENABLED',true);define('FV_R437_STAGING_PAGE_ID',49);function wp_get_environment_type(){return 'staging';}function is_singular(){return true;}function get_queried_object_id(){return 49;}require 'staging-chronology-audit.php';echo fv_r437_allowed() ? 'PASS':'FAIL';")
check(ret==0 and out=='PASS','explicit staging page only')
ret,out,err=php_script("define('ABSPATH','/qa/');require 'staging-chronology-audit.php';echo fv_r437_render(0);echo fv_r437_render(31);")
check(ret==0 and out.count('Read the free Apollo 1 investigation')==2,'invalid instance fallback')
ret,out,err=php_script("define('ABSPATH','/qa/');require 'staging-chronology-audit.php';echo fv_r437_render(1,['utm_source'=>'youtube','utm_medium'=>'organic_social','utm_campaign'=>'history_pilot_2026_11','utm_content'=>'fixture_not_a_published_asset']);")
check(ret==0 and 'data-fv-r437' in out,'full parent rendering and chain')
check(out.count('class="fv-r429__cta"')==1,'one existing free CTA')
check(out.count('data-period=')==4,'four source records')
for phrase in ['January 27, 1967','2017','February 14, 2018','not claimed release day','no NASA media']:
 check(phrase in out,'source/date truth '+phrase)
check('utm_content=fixture_not_a_published_asset' in out,'allowlisted campaign passes original CTA')
for word in ['NASA approved','100% guaranteed','buy now','limited time']:
 check(word not in out,'unapproved claim absent: '+word)
ret,bad,_=php_script("define('ABSPATH','/qa/');require 'staging-chronology-audit.php';echo fv_r437_render(1,['utm_source'=>'youtube','utm_medium'=>'organic_social','utm_campaign'=>'history_pilot_2026_11','utm_content'=>'<script>alert(1)</script>']);")
check('utm_content=' not in bad and '<script>alert(1)</script>' not in bad,'invalid campaign never forwards')
check(out.count('<details')>=4,'native disclosures before enhancement')
check(out.count('<a href="https://www.nasa.gov')>=4,'source URLs directly inspectable')
check('S67-19766 / crew portrait' not in out,'unverified catalog ID suppressed')
check('Crew photograph / catalogue ID not confirmed' in out,'uncertainty shown')
for path,expected in [('assets/chronology-audit.css','5da69288a2bd50995fcd2187cc662624e27b49aac68c7019b9aac7eab1369e70'),('assets/chronology-audit.js','515350dc54788ab010e4f09ddee3fe56dc4b61a56ba94a8f13c443caa9ae89fc')]:
 check(hashlib.sha256((here/path).read_bytes()).hexdigest()==expected,'asset SHA256 '+path)
# Actively mutate bytes and verify the guard rejects corruption; restore exactly, even on exceptions.
for relative in ['assets/chronology-audit.css','assets/chronology-audit.js','../apollo-r436/staging-source-proof.php']:
 target=(here/relative).resolve();original=target.read_bytes()
 try:
  target.write_bytes(original+b'\n/* UNREVIEWED TEST MUTATION */\n')
  ret,o,e=php_script("define('ABSPATH','/qa/');require 'staging-chronology-audit.php';echo fv_r437_verify() ? 'UNSAFE':'SAFE';")
  check(ret==0 and o=='SAFE','changed file is rejected: '+relative)
 finally:target.write_bytes(original)
# Print should reveal limitations even for closed disclosures.
css=(here/'assets/chronology-audit.css').read_text()
check('@media print' in css and '.fv-r437__print{display:block!important}' in css,'print keeps evidence limitations')
js=(here/'assets/chronology-audit.js').read_text()
for forbidden in ['localStorage','sessionStorage','navigator.sendBeacon','fetch(','XMLHttpRequest','document.cookie']:
 check(forbidden not in js,'no telemetry/storage: '+forbidden)
check('document.createElement' in js and 'querySelectorAll' in js,'progressive filtering control')
report={'kind':'EXECUTED_LOCAL_CONTRACT_NOT_STAGING','checks':checks,'failures':failures,'status':'PASS' if not failures else 'FAIL'}
(here/'QA').mkdir(exist_ok=True)
(here/'QA/contract.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps(report))
if failures:raise SystemExit(1)
