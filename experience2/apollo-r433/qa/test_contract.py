"""Executable negative evidence and release gates; no remote network or live writes."""
from pathlib import Path
import subprocess,hashlib,re
HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parent
PINNED={'apollo-r432/staging-custody-gate.php':'749e708b018b3dddfdc5dab3897665ad2bde55ec','apollo-r432/assets/custody-gate.css':'9c586627f8c7e7096b9d6be8ac646bb990478400'}
count=0
def check(yes,what):
 global count
 assert yes,what
 count+=1

def php(code):
 r=subprocess.run(['php','-r',code],cwd=str(ROOT),capture_output=True,text=True)
 check(r.returncode==0,'PHP failed: '+r.stderr)
 return r.stdout

def main():
 check(subprocess.run(['php','-l',str(HERE/'staging-claim-bridge.php')],capture_output=True).returncode==0,'PHP lint')
 for path,sha in PINNED.items():
  b=(ROOT/path).read_bytes(); check(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==sha,'pin '+path)
 code=f"define('ABSPATH','/'); require '{HERE/'staging-claim-bridge.php'}';"
 check(php(code+' echo fv_r433_parent_verified()?"OK":"BAD";')=='OK','parent custody')
 check(php(code+' echo fv_r433_allowed()?"BAD":"DENIED";')=='DENIED','deny activation by default')
 check(php(code+' echo fv_r433_shortcode();').count('Read the free Apollo 1 investigation')==1,'default fallback')
 allowed="function wp_get_environment_type(){return 'staging';}function is_singular(){return true;}function get_queried_object_id(){return 99;}"
 active="define('FV_R433_ENABLED',true);define('FV_R433_STAGING_PAGE_ID',99);"
 check(php(allowed+active+code+' echo fv_r433_allowed()?"ALLOWED":"DENIED";')=='ALLOWED','exact staging gate')
 check(php(allowed+active.replace('99','100')+code+' echo fv_r433_allowed()?"BAD":"DENIED";')=='DENIED','wrong staging page')
 check(php("function wp_get_environment_type(){return 'production';}"+active+code+' echo fv_r433_allowed()?"BAD":"DENIED";')=='DENIED','production denied')
 html=subprocess.run(['php',str(HERE/'qa/fixture.php')],capture_output=True,text=True,check=True).stdout
 check(html.count('data-fv-r433')==2,'two actual R433 instances')
 check(html.count('class="fv-r429__cta"')==2,'one article CTA per instance')
 check(html.count('class="fv-r433__claim"')==6,'three evidence statuses per instance')
 check(html.count('class="fv-r430__question"')==6,'original educator questions')
 check(html.count('data-fv-r431-actions hidden')==2,'original note tools')
 check('utm_content=apollo_documentary_001' in html and html.count('utm_content=apollo_documentary_001')==1,'campaign only on first CTA')
 check(not re.search(r'href="https?://[^\"]*(payhip|checkout|affiliate)',html,re.I),'no unapproved checkout links')
 check('NASA does not endorse' in html and 'no single ignition source' in html.lower(),'honest historical limitations')
 check('source review is unavailable' in subprocess.run(['php',str(HERE/'qa/fixture.php')],env={'FV_R433_FALLBACK':'1'},capture_output=True,text=True,check=True).stdout.lower(),'plain fallback works')
 print(f'PASS {count} R433 PHP/source/gate assertions')
if __name__=='__main__':main()
