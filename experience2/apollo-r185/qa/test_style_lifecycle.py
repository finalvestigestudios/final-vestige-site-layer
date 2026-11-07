#!/usr/bin/env python3
"""Isolated PHP WordPress-hook simulation: NOT an installed WordPress or axe audit."""
import hashlib, json, shutil, subprocess, tempfile, unittest
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
PHP=ROOT/'dist/fv-ex2-apollo-r185.php'

BOOTSTRAP=r'''<?php
define('ABSPATH','/mock/');
class WP_Post {public $post_content; function __construct($text){$this->post_content=$text;}}
$GLOBALS['hooks']=array(); $GLOBALS['styles']=array(); $GLOBALS['shortcodes']=array();
$GLOBALS['headed']=false; $GLOBALS['admin']=false; $GLOBALS['singular']=true;
function add_action($name,$cb,$prio=10){$GLOBALS['hooks'][$name][]=$cb;}
function add_shortcode($name,$cb){$GLOBALS['shortcodes'][$name]=$cb;}
function do_action($name){foreach($GLOBALS['hooks'][$name]??array() as $cb) call_user_func($cb);}
function plugin_dir_path($file){return dirname($file).'/';}
function plugins_url($path,$file){return 'https://test-staging.invalid/'.$path;}
function is_admin(){return $GLOBALS['admin'];}
function is_singular(){return $GLOBALS['singular'];}
function get_queried_object(){return $GLOBALS['post']??null;}
function has_shortcode($content,$tag){return strpos($content,'['.$tag.']')!==false;}
function wp_enqueue_style($name,$src,$deps=array(),$ver=false){$GLOBALS['styles'][$name]=array('src'=>$src,'ver'=>$ver);}
function wp_style_is($name,$status){return isset($GLOBALS['styles'][$name]);}
function did_action($name){return $name==='wp_head' && $GLOBALS['headed']?1:0;}
require $argv[1];
$case=$argv[2];
$GLOBALS['post']=new WP_Post($case==='unrelated'?'A page with no component':'[fv_ex2_apollo_atlas]');
if($case==='admin')$GLOBALS['admin']=true;
if($case==='archive')$GLOBALS['singular']=false;
if($case==='early'){
  $before=fv_ex2_r185_render();
  $head=array_keys($GLOBALS['styles']);
  $GLOBALS['headed']=true;
  $after='';
}else{
  do_action('wp_enqueue_scripts');
  $head=array_keys($GLOBALS['styles']);
  $GLOBALS['headed']=true;
  $before='';
  $after=fv_ex2_r185_render();
}
$second=$case==='duplicate'?fv_ex2_r185_render():null;
echo json_encode(array('head'=>$head,'before'=>$before,'after'=>$after,'second'=>$second,'queued'=>array_keys($GLOBALS['styles'])));
'''

class Lifecycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=PHP
        cls.html=ROOT/'dist/templates/atlas-fragment.html'
        cls.css=ROOT/'dist/assets/atlas-scoped.css'
        cls.m=json.loads((ROOT/'dist/manifest.json').read_text())

    def invoke(self,case='normal',tamper=False):
        with tempfile.TemporaryDirectory() as d:
            temp=Path(d)
            (temp/'templates').mkdir();(temp/'assets').mkdir()
            for source,dst in [(self.p,temp/self.p.name),(self.html,temp/'templates/atlas-fragment.html'),(self.css,temp/'assets/atlas-scoped.css')]:shutil.copyfile(source,dst)
            if tamper:(temp/'assets/atlas-scoped.css').write_text('body{display:none}')
            bootstrap=temp/'mock.php';bootstrap.write_text(BOOTSTRAP)
            result=subprocess.run(['php',str(bootstrap),str(temp/self.p.name),case],text=True,capture_output=True,check=True)
            return json.loads(result.stdout)

    def test_source_pins(self):
        for key,src in [('r184_fragment_sha256',self.html),('r184_css_sha256',self.css),('r185_php_sha256',self.p)]:
            self.assertEqual(self.m[key],hashlib.sha256(src.read_bytes()).hexdigest())

    def test_syntax(self):
        result=subprocess.run(['php','-l',str(self.p)],text=True,capture_output=True,check=True)
        self.assertIn('No syntax errors',result.stdout)

    def test_head_contains_style_when_shortcode_present(self):
        got=self.invoke(); self.assertEqual(got['head'],['fv-apollo-r185'])
        self.assertIn('What the records support',got['after'])

    def test_no_style_on_unrelated_page(self):
        got=self.invoke('unrelated');self.assertEqual(got['head'],[])
        self.assertIn('Read the original investigation',got['after'])
        self.assertNotIn('What the records support',got['after'])

    def test_fails_open_on_bad_assets(self):
        got=self.invoke(tamper=True);self.assertEqual(got['head'],[])
        self.assertIn('Read the original investigation',got['after'])

    def test_guard_on_archive_context(self):
        got=self.invoke('archive');self.assertEqual(got['head'],[])
        self.assertIn('Read the original investigation',got['after'])

    def test_guard_on_admin_context(self):
        got=self.invoke('admin');self.assertEqual(got['head'],[])
        self.assertIn('Read the original investigation',got['after'])

    def test_early_render_can_register_style(self):
        got=self.invoke('early');self.assertEqual(got['head'],['fv-apollo-r185'])
        self.assertIn('What the records support',got['before'])

    def test_duplicate_shortcode_fails_open(self):
        got=self.invoke('duplicate');self.assertIn('What the records support',got['after'])
        self.assertNotIn('What the records support',got['second'])
        self.assertIn('Read the original investigation',got['second'])

    def test_evidence_and_single_action_preserved(self):
        soup=BeautifulSoup(self.html.read_text(),'html.parser')
        self.assertEqual(len(soup.select('.rail li')),4)
        self.assertEqual(len(soup.select('.plate')),4)
        self.assertEqual(len(soup.select('.source-card')),4)
        self.assertEqual(len(soup.select('details summary')),8)
        self.assertEqual([a['href'] for a in soup.select('a.cta')],['https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'])
        self.assertFalse(soup.select('script,iframe,img,form,[data-lat],[data-map-pin]'))
        self.assertIn('not conclusively',soup.get_text(' ',strip=True))

if __name__=='__main__':unittest.main()
