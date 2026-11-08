#!/usr/bin/env python3
"""Positive and adversarial real-PHP tests of exact import preflight and both MU guards."""
import io,json,subprocess,tempfile,unittest,zipfile
from pathlib import Path
from playground_web_admission import build,digest,PARENT_SHA
SOURCE=Path(__file__).with_name('parent_PR1509_review.zip')
BOOT='''<?php
$h=$argv[3];$env=$argv[4];$marker=$argv[5];
define('ABSPATH','/LOCAL-TEST/');
if($env==='production')define('WP_ENVIRONMENT_TYPE','production');
function home_url($x='/'){return $GLOBALS['h'];}
function wp_parse_url($u,$part=-1){return parse_url($u,$part);}
function get_option($a,$b=''){return $GLOBALS['marker']==='on'?'FV_EX2_LOCAL_PLAYGROUND_2026_11_05_V1':'';}
function add_action($h,$cb){$GLOBALS['actions'][$h][]=$cb;}
function add_shortcode($h,$cb){$GLOBALS['shortcodes'][$h]=$cb;}
function is_page($slug){return $slug==='fv-ex2-review';}
$GLOBALS['h']=$h;$GLOBALS['marker']=$marker;$GLOBALS['actions']=[];$GLOBALS['shortcodes']=[];
require $argv[1];require $argv[2];
echo json_encode(['shortcodes'=>array_keys($GLOBALS['shortcodes']),'hooks'=>array_keys($GLOBALS['actions'])]);
'''
class Admission(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.source=SOURCE.read_bytes();c.built=build(c.source)
  with zipfile.ZipFile(io.BytesIO(c.source)) as z:c.old={p:z.read(p) for p in z.namelist()}
  with zipfile.ZipFile(io.BytesIO(c.built)) as z:c.new={p:z.read(p) for p in z.namelist()}
 def preflight(self,d,host,env='local'):
  bp=json.loads(d['blueprint.json']);code=bp['steps'][0]['code'].replace("require_once '/wordpress/wp-load.php';",'').replace('<?php','')
  with tempfile.TemporaryDirectory() as tmp:
   f=Path(tmp)/'pre.php';f.write_text('<?php\nfunction home_url($x="/"){return $GLOBALS["h"];} function wp_parse_url($u){return parse_url($u);}\n$GLOBALS["h"]=$argv[1];if($argv[2]==="production")define("WP_ENVIRONMENT_TYPE","production");\n'+code+'\necho "PASS";')
   r=subprocess.run(['php',str(f),host,env],capture_output=True,text=True,timeout=12)
   return r.returncode,r.stdout
 def plugins(self,d,host,env='local',marker='on'):
  with tempfile.TemporaryDirectory() as tmp:
   paths=[]
   for i,p in enumerate(sorted(k for k in d if k.startswith('mu-plugins/'))):
    f=Path(tmp)/f'{i}.php';f.write_bytes(d[p]);paths.append(str(f))
   f=Path(tmp)/'boot.php';f.write_text(BOOT)
   r=subprocess.run(['php',str(f),*paths,host,env,marker],capture_output=True,text=True,timeout=12)
   self.assertEqual(r.returncode,0,r.stderr)
   return json.loads(r.stdout)
 def test_old_package_blocks_real_web_playground(self):
  h='https://wpsandbox.wordpress.net/scope:private/'
  self.assertNotEqual(self.preflight(self.old,h)[0],0)
  self.assertEqual(self.plugins(self.old,h)['shortcodes'],[])
 def test_fixed_package_admits_official_web_wordpress_host(self):
  h='https://wpsandbox.wordpress.net/scope:private/'
  self.assertEqual(self.preflight(self.new,h),(0,'PASS'))
  self.assertEqual(self.plugins(self.new,h)['shortcodes'],['fv_ex2_playground'])
  self.assertEqual(sorted(self.plugins(self.new,h)['hooks']),['wp_enqueue_scripts','wp_footer'])
 def test_prod_and_forged_hosts_denied(self):
  for h in ['https://finalvestige.com/','https://vestigefinal-tezws.wpcomstaging.com/',
            'https://playground.wordpress.net/','https://wpsandbox.wordpress.net.attacker.tld/',
            'https://fakewpsandbox.wordpress.net/']:
   with self.subTest(h=h):
    self.assertNotEqual(self.preflight(self.new,h)[0],0)
    self.assertEqual(self.plugins(self.new,h)['shortcodes'],[])
 def test_production_env_even_on_permitted_host_denied(self):
  for h in ['https://wpsandbox.wordpress.net/','http://localhost:8888/']:
   self.assertNotEqual(self.preflight(self.new,h,'production')[0],0)
   self.assertEqual(self.plugins(self.new,h,'production')['shortcodes'],[])
 def test_missing_marker_denied(self):
  self.assertEqual(self.plugins(self.new,'https://wpsandbox.wordpress.net/','local','off')['shortcodes'],[])
 def test_loopback_retained(self):
  for h in ['http://localhost:8888/','http://127.0.0.1:9000/','http://dev.localhost:8888/']:
   self.assertEqual(self.preflight(self.new,h),(0,'PASS'))
   self.assertEqual(self.plugins(self.new,h)['shortcodes'],['fv_ex2_playground'])
 def test_no_blueprint_step_reordered_or_theme_changed(self):
  a=json.loads(self.old['blueprint.json']);b=json.loads(self.new['blueprint.json'])
  self.assertEqual(a['steps'][1:],b['steps'][1:]);self.assertEqual(b['steps'][1]['themeData']['ref'],'75faa8a1e0367a37c2638250a3c9ed0a0f8c0b7f')
 def test_php_syntax_and_72_margins_5_focus(self):
  body=self.new['mu-plugins/fv-ex2-playground-review.php'];self.assertEqual(body.count(b'class="fv-margin-strip__item"'),72);self.assertEqual(body.count(b'https://finalvestige.com/focus/'),5)
  for p in self.new:
   if p.endswith('.php'):
    with tempfile.TemporaryDirectory() as tmp:
     f=Path(tmp)/'source.php';f.write_bytes(self.new[p]);r=subprocess.run(['php','-l',str(f)],capture_output=True,text=True)
     self.assertEqual(r.returncode,0,r.stdout+r.stderr)
 def test_sha_pin_and_deterministic_bundle(self):
  self.assertEqual(digest(self.source),PARENT_SHA)
  self.assertEqual(self.built,build(self.source))
  with self.assertRaisesRegex(ValueError,'SHA mismatch'):build(self.source+b'tamper')
 def test_readme_not_modified(self):self.assertEqual(self.old['REVIEW.txt'],self.new['REVIEW.txt'])
if __name__=='__main__':unittest.main(verbosity=2)
