"""Executable real PHP tests: stage gate, offer proof HOLD, custody, no commerce and fail-open."""
import hashlib,json,subprocess,shutil,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; QA=ROOT/'QA';QA.mkdir(exist_ok=True)
checks=0;fail=[]
def ok(test,what):
 global checks
 checks+=1
 if not test:fail.append(what)
def php(txt,plugin=ROOT/'staging-educator-intent.php'):
 return subprocess.run(['php'],input="<?php define('ABSPATH','/r440-test/');require "+repr(str(plugin))+";"+txt,text=True,capture_output=True)
ok(subprocess.run(['php','-l',str(ROOT/'staging-educator-intent.php')],capture_output=True).returncode==0,'php syntax')
for p,d in [('assets/educator-intent.css','b0b5c504e0ee57ed3f7b1525973842f8c2df1f9afdad0493f5a8fec4399971a1'),('assets/educator-intent.js','13a186fb80b552f8cc9b96ffcfda38c0ccd111f43c3e147349a7847db2120888'),('product_evidence.json','936cdae7af73e60139dd5fc7c58477be6aa4f7b662c4da5fb59c7f47b498b564')]:
 ok(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,'pinned sha256 '+p)
r=php("echo json_encode(['source'=>fv_r440_verify(),'offer_hold'=>fv_r440_offer_hold(),'html'=>fv_r440_render(1)]);")
ok(r.returncode==0,'render executes')
d=json.loads(r.stdout) if r.returncode==0 else {};s=d.get('html','')
ok(d.get('source') is True,'source verification')
ok(d.get('offer_hold') is True,'truthful no-sell manifest')
ok('data-r440-root' in s,'actual component rendered')
ok('href="https://www.nasa.gov/' in s,'direct NASA sources')
ok('data-r440-export></div>' in s,'no-JS no inert export button')
ok(s.count('<summary>')==1,'native disclosure')
ok(s.count('https://finalvestige.com/')==0,'no duplicate CTA, existing R439 CTA untouched')
ok(all(x not in s.lower() for x in ['payhip.com','buy now','add to cart','<form','<iframe','newsletter','utm_campaign=']),'no paid/inappropriate CTA, form, or UTM injection')
ok('proposal, not an available product' in s,'product truth disclosure')
ok('NASA does not endorse' not in s or 'rights' in s.lower(),'not false endorsement')
manifest=json.loads((ROOT/'product_evidence.json').read_text())
ok(manifest['verification_status']=='HOLD_NOT_SELLABLE','official offer on HOLD')
ok(all(manifest[k] is False for k in ['merchant_seller_identity_verified','specific_paid_sku_verified','payment_checkout_verified','deliverable_fulfillment_verified','original_content_rights_verified','nasamedia_rights_reviewed_for_product','founder_approved_paid_launch','published_grok_asset_id_verified']),'no unverified positive claims')
ok(manifest['paid_checkout_url'] is None and manifest['verified_orders'] is None and manifest['realized_net_revenue'] is None,'unknown sales stay null')
for env,page in [('production',8),('staging',7),('staging',8)]:
 q=php("function wp_get_environment_type(){return '"+env+"';}function is_singular(){return true;}function get_queried_object_id(){return "+str(page)+";}define('FV_R440_ENABLED',true);define('FV_R440_STAGING_PAGE_ID',8);echo fv_r440_shortcode();")
 ok(('data-r440-root' in q.stdout)==(env=='staging' and page==8),'stage exact gate '+env+str(page))
q=php('echo fv_r440_shortcode();');ok('Classroom preview unavailable' in q.stdout,'default disabled without flags')
q=php('echo fv_r440_render(0),fv_r440_render(31);');ok(q.stdout.count('Classroom preview unavailable')==2,'bounds')
with tempfile.TemporaryDirectory() as tmp:
 clone=Path(tmp)/'apollo-r440';shutil.copytree(ROOT,clone,ignore=shutil.ignore_patterns('QA','__pycache__'))
 for rel in ['product_evidence.json','assets/educator-intent.css','assets/educator-intent.js']:
  p=clone/rel;original=p.read_bytes();p.write_bytes(original+b'\nATTACK')
  q=php('echo fv_r440_render(1);',clone/'staging-educator-intent.php')
  ok(q.returncode==0 and 'Classroom preview unavailable' in q.stdout and 'data-r440-root' not in q.stdout,'mutated '+rel+' fail open')
  p.write_bytes(original)
 p=clone/'assets/educator-intent.js';p.unlink();p.symlink_to(ROOT/'assets/educator-intent.js')
 q=php('echo fv_r440_render(1);',clone/'staging-educator-intent.php')
 ok('Classroom preview unavailable' in q.stdout,'symlink rejected')
report={'kind':'REAL_PHP_SOURCE_TEST_NOT_WORDPRESS_STAGING','checks':checks,'failed':fail,'status':'PASS' if not fail else 'FAIL'}
(QA/'contracts.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
print(json.dumps(report));raise SystemExit(bool(fail))
