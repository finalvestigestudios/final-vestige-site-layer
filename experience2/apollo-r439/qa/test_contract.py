"""Executed real PHP fixture, exact pinned Git ancestry, opt-in staging and fail-open mutation tests."""
import hashlib,json,subprocess,shutil,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];BASE=HERE.parent
checks=0;failed=[]
def ok(x,name):
 global checks
 checks+=1
 if not x:failed.append(name)
def php(source):return subprocess.run(['php'],input=source,capture_output=True,text=True)
def code(text,plugin=HERE/'staging-evidence-receipt.php'):
 return "<?php define('ABSPATH','/qa/');require "+repr(str(plugin))+";"+text
p=subprocess.run(['php','-l',str(HERE/'staging-evidence-receipt.php')],capture_output=True,text=True)
ok(p.returncode==0,'PHP syntax passes')
for fn,sha in [('staging-source-atlas.php','4d3d8e72e71db109cf22083ec57c3b27ae7ff184'),('assets/source-atlas.css','2154e3feb3811ef7abd53f229264cdb83428ae41'),('assets/source-atlas.js','bd327465626fe3e591ae055273ced676bd03190e'),('source_catalog.json','60903bdcf67a1f6b22f92508d4dcc181c5f95c5a')]:
 b=(BASE/'apollo-r438'/fn).read_bytes();ok(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==sha,'exact R438 Git blob '+fn)
p=php(code("echo json_encode(['verified'=>fv_r439_verify(),'parent'=>fv_r439_parent(),'html'=>fv_r439_render(1,['utm_source'=>'youtube','utm_medium'=>'organic_social','utm_campaign'=>'history_pilot_2026_11','utm_content'=>'qa_not_live'])]);"))
ok(p.returncode==0,'PHP render returns success')
d=json.loads(p.stdout) if p.returncode==0 else {};s=d.get('html','')
ok(d.get('verified') is True,'R439 own and parent pinned assets verified')
ok(d.get('parent') is True,'full ancestor custody passes')
ok('data-r439-root' in s and 'data-r439-receipt' in s,'render includes passport')
ok(s.count('data-r439-receipt')==1,'single evidence passport per instance')
ok(s.count('data-r438-card=')==5,'source atlas five curated records unchanged')
ok(s.count('class="fv-r429__cta"')==1,'one original article CTA retained')
ok(s.count('https://www.nasa.gov/')>=6,'NASA evidence records unchanged')
ok('utm_content=qa_not_live' in s,'approved campaign parameter continuity retained')
ok('maps.google' not in s and 'latitude' not in s and 'longitude' not in s,'no speculative geographic mapping')
ok('href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/' in s,'original investigation destination preserved')
ok('data-r439-manual-label hidden' in s,'no-JS manual fallback label hidden until needed')
ok('data-r439-controls></div>' in s,'no-JS: no dead export buttons')
for v in ['woocommerce','payhip.com','fetch(','<iframe','ga(']:ok(v not in (HERE/'assets/source-receipt.js').read_text().lower(),'no sale/remote collection '+v)
attack=php(code("echo fv_r439_render(2,['utm_source'=>'<script>alert(1)</script>','utm_campaign'=>'https://malicious.invalid']);"))
ok(attack.returncode==0 and '<script>alert(1)</script>' not in attack.stdout and 'malicious.invalid' not in attack.stdout,'inherited URL allowlist rejects untrusted campaign')
def stage(status='staging',page=4):
 return php(code("function wp_get_environment_type(){return '"+status+"';}function is_singular(){return true;}function get_queried_object_id(){return "+str(page)+";}define('FV_R439_ENABLED',true);define('FV_R439_STAGING_PAGE_ID',4);echo fv_r439_shortcode();"))
ok('Evidence receipt unavailable' in stage('production').stdout,'production environment denied')
ok('Evidence receipt unavailable' in stage('staging',3).stdout,'non-allowlisted staging page denied')
ok('data-r439-receipt' in stage().stdout,'explicit approved staging page returns evidence')
# Run actual code in a cloned immutable ancestor tree and corrupt one asset at a time.
with tempfile.TemporaryDirectory() as tmp:
 clone=Path(tmp)/'experience2';shutil.copytree(BASE,clone,ignore=shutil.ignore_patterns('QA','__pycache__'))
 for relative in ['apollo-r439/assets/source-receipt.css','apollo-r439/assets/source-receipt.js','apollo-r438/staging-source-atlas.php','apollo-r438/source_catalog.json']:
  path=clone/relative;orig=path.read_bytes();path.write_bytes(orig+b'\nMUTATED')
  r=php(code('echo fv_r439_render(1);',clone/'apollo-r439/staging-evidence-receipt.php'))
  ok(r.returncode==0 and 'Evidence receipt unavailable' in r.stdout and 'data-r439-root' not in r.stdout,'corruption blocks component '+relative)
  path.write_bytes(orig)
 # symlink rejection without changing checkout
 relative='apollo-r439/assets/source-receipt.css';path=clone/relative
 path.unlink();path.symlink_to(BASE/'apollo-r439/assets/source-receipt.css')
 r=php(code('echo fv_r439_render(1);',clone/'apollo-r439/staging-evidence-receipt.php'))
 ok('Evidence receipt unavailable' in r.stdout,'symlinked asset rejected')
report={'kind':'EXECUTED_REAL_PHP_LOCAL_CONTRACT_NOT_WORDPRESS_STAGING','checks':checks,'failed':failed,'status':'PASS' if not failed else 'FAIL'}
(HERE/'QA').mkdir(exist_ok=True);(HERE/'QA/contracts.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps(report));raise SystemExit(bool(failed))
