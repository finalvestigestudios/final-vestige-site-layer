"""Real PHP source checks, inherited custody and executable mutation/fail-open tests."""
import hashlib,json,re,subprocess,tempfile,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];BASE=HERE.parent
checks=0;fail=[]
def ok(v,label):
 global checks
 checks+=1
 if not v:fail.append(label)
def php(script):return subprocess.run(['php'],input=script,text=True,capture_output=True)
def render_code(extra=''):
 return "<?php define('ABSPATH','/local/');require "+repr(str(HERE/'staging-source-atlas.php'))+";"+extra
lint=subprocess.run(['php','-l',str(HERE/'staging-source-atlas.php')],capture_output=True,text=True)
ok(lint.returncode==0,'PHP lint')
parent=(BASE/'apollo-r437/staging-chronology-audit.php').read_bytes();expected=lambda x:hashlib.sha1(b'blob '+str(len(x)).encode()+b'\x00'+x).hexdigest()
ok(expected(parent)=='b911e256942805649cdc298b81ae1ceda420c429','R437 parent immutable content')
script=render_code("echo json_encode(['verify'=>fv_r438_verify(),'parent'=>fv_r438_parent(),'count'=>count(fv_r438_catalog()),'html'=>fv_r438_render(1,['utm_source'=>'youtube','utm_medium'=>'organic_social','utm_campaign'=>'history_pilot_2026_11','utm_content'=>'qa_not_published'])]);")
r=php(script);ok(r.returncode==0,'r438 render PHP returns successfully '+r.stderr[:120]);d=json.loads(r.stdout) if r.returncode==0 else {'verify':False,'html':''}
html=d['html'];ok(d.get('verify') is True,'verified all immutable sources');ok(d.get('parent') is True,'full R437 chain verifiable');ok(d.get('count')==5,'five curated records')
for thing in ['data-r438-atlas-root','data-r438-card','data-r438-supports','data-r438-limit','No NASA','class="fv-r429__cta"']:
 ok(thing in html,'render contains '+thing)
ok(html.count('data-r438-card=')==5,'5 atlas source records')
ok(html.count('class="fv-r429__cta"')==1,'exactly one inherited investigation CTA')
ok('href="https://www.nasa.gov/gallery/apollo-1/"' in html,'photo link canonical')
ok('utm_source=youtube' in html and 'utm_content=qa_not_published' in html,'validated campaign passed through')
ok('latitude' not in html and 'longitude' not in html and 'google.com/maps' not in html,'no speculative geopins')
catalog=json.loads((HERE/'source_catalog.json').read_text());ids=[x['id'] for x in catalog['records']]
ok(len(ids)==len(set(ids)),'source IDs unique')
ok(all(x['source_url'].startswith('https://www.nasa.gov/') for x in catalog['records']),'original nasa host only')
ok(all(x['supports'] and x['limit'] and x['rights'] for x in catalog['records']),'all sources have evidence bounds + rights')
# Malformed/special URL query does not get printed into a button or source link
attack=php(render_code("echo fv_r438_render(2,['utm_source'=>'<script>unsafe</script>','utm_campaign'=>'http://evil.example']);"))
ok(attack.returncode==0 and '<script>unsafe</script>' not in attack.stdout and 'evil.example' not in attack.stdout,'rejects malicious campaign forwarding')
# Explicit staging opt-in; never renders on production; no WP writes
staging=php(render_code("function wp_get_environment_type(){return 'production';}function is_singular(){return true;}function get_queried_object_id(){return 30;}define('FV_R438_ENABLED',true);define('FV_R438_STAGING_PAGE_ID',30);echo fv_r438_shortcode();"))
ok(staging.returncode==0 and 'Source comparison unavailable' in staging.stdout,'production remains gated')
staging=php(render_code("function wp_get_environment_type(){return 'staging';}function is_singular(){return true;}function get_queried_object_id(){return 31;}define('FV_R438_ENABLED',true);define('FV_R438_STAGING_PAGE_ID',30);echo fv_r438_shortcode();"))
ok('Source comparison unavailable' in staging.stdout,'mismatched staging page gated')
staging=php(render_code("function wp_get_environment_type(){return 'staging';}function is_singular(){return true;}function get_queried_object_id(){return 30;}define('FV_R438_ENABLED',true);define('FV_R438_STAGING_PAGE_ID',30);echo fv_r438_shortcode();"))
ok('data-r438-atlas-root' in staging.stdout,'exact authorized staging page renders')
# Exercise actual files by copying tree and mutate catalogue, CSS, JS, parent.
with tempfile.TemporaryDirectory() as temp:
 dest=Path(temp)/'experience2';shutil.copytree(BASE,dest)
 top=dest/'apollo-r438/staging-source-atlas.php'
 for p in ['source_catalog.json','assets/source-atlas.css','assets/source-atlas.js','../apollo-r437/staging-chronology-audit.php']:
  file=dest/'apollo-r438'/p;old=file.read_bytes();file.write_bytes(old+b'\n// modification')
  q=php("<?php define('ABSPATH','/local/');require "+repr(str(top))+";echo fv_r438_render(1);")
  ok(q.returncode==0 and 'Source comparison unavailable' in q.stdout and 'data-r438-atlas-root' not in q.stdout,'mutation rejected '+p)
  file.write_bytes(old)
# Verify local CSS and JS cannot be provided through symlink
for p in ['source_catalog.json','assets/source-atlas.css','assets/source-atlas.js']:
 ok(not (HERE/p).is_symlink(),p+' not a symlink')
report={'kind':'EXECUTED_PHP_CONTRACT_AND_MUTATION_NOT_WP_STAGING','checks':checks,'failed':fail,'status':'PASS' if not fail else 'FAIL'}
(HERE/'QA').mkdir(exist_ok=True)
(HERE/'QA/contracts.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(json.dumps(report))
if fail:raise SystemExit(1)
