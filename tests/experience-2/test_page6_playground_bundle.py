"""Isolated blueprint bundle-builder tests; mocks are NOT WordPress acceptance."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
import zipfile

REPO=Path(__file__).resolve().parents[2]
SOURCE=REPO/'experience2/home-flagship'
TOOL=REPO/'tools/experience-2/build_page6_playground_bundle.py'
sp=importlib.util.spec_from_file_location('fv_build_page6_blueprint',TOOL)
bp=importlib.util.module_from_spec(sp); sp.loader.exec_module(bp)


def fake_raw():
    records=''.join(f'<span class="fv-margin-strip__item">SYNTHETIC TEST {x}</span>' for x in range(72))
    sections=''.join('<div id="'+id+'">Synthetic chapter</div>' for id in (
        'fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry',
        'fv-hf-method-title','fv-hf-observer','fv-hf-mind-title'))
    return ('<!-- wp:html -->\n<!-- FV-SYNTHETIC-FIXTURE: NOT HISTORICAL CONTENT -->\n'+records+'<!-- /wp:html -->'
            '<!-- wp:html -->\n<div data-fv-home-flagship>'+sections+'</div>\n<!-- /wp:html -->'
            '<!-- wp:html -->\n<section class="fv-focus-cta"><a class="fv-focus-cta__button" href="/focus/">Fieldbook</a></section>\n<!-- /wp:html -->'
            '<!-- wp:group -->\n<div class="wp-block-group">'
            '<!-- wp:jetpack/subscriptions /-->\n</div>\n<!-- /wp:group -->'
            '<!-- wp:html -->\n<p>Other public content</p>\n<!-- /wp:html -->')


class IntegrationBlueprint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()
        cls.fake=fake_raw()

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)
        self.page=self.path/'page.html'
        self.page.write_text(self.fake,encoding='utf-8')
        self.sha=hashlib.sha256(self.page.read_bytes()).hexdigest()

    def make(self, filename='review.zip', **kwargs):
        return bp.build(REPO,SOURCE,self.page,self.path/filename,self.head,
                        kwargs.get('sha',self.sha),kwargs.get('synthetic',True))

    def test_blueprint_self_contained_wordpress_parser_and_private_review(self):
        result=self.make()
        with zipfile.ZipFile(result['bundle']) as z:
            self.assertEqual(sorted(z.namelist()),['DO_NOT_DEPLOY.txt','MANIFEST.json','blueprint.json','blueprint.local-cli.json','page6-review.blocks.html'])
            doc=json.loads(z.read('blueprint.json')); local_doc=json.loads(z.read('blueprint.local-cli.json')); receipt=json.loads(z.read('MANIFEST.json'))
            self.assertEqual([s['step'] for s in doc['steps']],['defineWpConfigConsts','writeFile','runPHP'])
            self.assertTrue(doc['login'])
            self.assertTrue(doc['steps'][0]['consts']['FV_EX2_LOCAL_ONLY'])
            self.assertEqual(type(local_doc['steps'][1]['data']),str)
            self.assertEqual(local_doc['steps'][1]['data'],z.read('page6-review.blocks.html').decode())
            self.assertIn('/tmp/',doc['steps'][1]['path'])
            self.assertNotIn('wp-content/',doc['steps'][1]['path'])
            php=doc['steps'][2]['code']
            for term in ('wp_get_environment_type()',"!== 'local'",'parse_blocks($raw)','wp_insert_post','wp_slash($raw)',"'post_status' => 'private'",'get_post($id)','wp_delete_post($id, true)'):
                self.assertIn(term,php)
            self.assertNotIn('update_option(',php)
            self.assertNotIn('wp_mail(',php)
            self.assertEqual(receipt['release'],'HOLD')
            self.assertEqual(receipt['wordpress_runtime_execution'],'NOT_TESTED')
            self.assertFalse(receipt['real_page6'])
            data=z.read('page6-review.blocks.html').decode()
            self.assertEqual(data.count('class="fv-margin-strip__item'),72)
            self.assertEqual(data.count('wp:jetpack/subscriptions'),1)
            self.assertEqual(data.count('<!-- wp:html -->'),4)
            self.assertEqual(len(re.findall(r'<div\b[^>]*\bdata-fv-home-flagship\b',data)),1)
            self.assertEqual(data.count('id="fv-hf-evidence"'),1)
            self.assertIn('FV-SYNTHETIC-FIXTURE',data)

    def test_php_checks_actual_native_focus_action_not_candidate_link(self):
        self.make()
        with zipfile.ZipFile(self.path/'review.zip') as z:
            doc = json.loads(z.read('blueprint.json'))
            php = doc['steps'][2]['code']
        self.assertIn('fv-focus-cta__button', php)
        self.assertIn("$focus_href === '/focus/'", php)
        self.assertIn('NON-FLAGSHIP Gutenberg HTML', php)
        self.assertNotIn("strpos($raw, 'https://finalvestige.com/focus/')", php)

    def test_php_rejects_redirect_even_when_source_digest_matches(self):
        self.make()
        with zipfile.ZipFile(self.path/'review.zip') as z:
            raw = z.read('page6-review.blocks.html').decode()
        self.assertIn('href="/focus/"', raw)
        attacked = raw.replace('href="/focus/"', 'href="https://example.invalid/focus/"', 1)
        contents = self.path/'changed.blocks.html'
        contents.write_text(attacked, encoding='utf-8')
        generated = bp.guarded_php(bp.digest(attacked.encode()), True, 5, 4)
        generated = generated.replace("require_once '/wordpress/wp-load.php';", '')
        generated = generated.replace('/tmp/fv-ex2-page6-review.blocks.html', str(contents))
        mock = """<?php
        define('FV_EX2_LOCAL_ONLY', true);
        function wp_get_environment_type(){return 'local';}
        function parse_blocks($source){
            $items=[];
            for($i=0;$i<4;$i++){$items[]=['blockName'=>'core/html','innerBlocks'=>[]];}
            $items[]=['blockName'=>'core/group','innerBlocks'=>[['blockName'=>'jetpack/subscriptions','innerBlocks'=>[]]]];
            return $items;
        }
        function get_page_by_path($path){return null;}
        function wp_insert_post($post,$error){throw new Exception('Must never reach insert');}
        ?>"""
        file = self.path/'redirect.php'
        file.write_text(mock+'\n'+generated, encoding='utf-8')
        self.assertEqual(subprocess.run(['php','-l',str(file)], capture_output=True).returncode, 0)
        run = subprocess.run(['php',str(file)], capture_output=True, text=True)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('native Jetpack/Focus custody failed', run.stderr)

    def test_deterministic_zip_bytes(self):
        a=self.make('a.zip');b=self.make('b.zip')
        self.assertEqual(a['bundle_sha256'],b['bundle_sha256'])

    def test_php_syntax_and_mock_wordpress_success(self):
        self.make()
        with zipfile.ZipFile(self.path/'review.zip') as z:
            doc=json.loads(z.read('blueprint.json'))
            content=z.read('page6-review.blocks.html')
        # The CLI mock is *not* real WordPress. It verifies generated PHP executes
        # with the intended API calls and byte-preserving post_content handling.
        rendered_path=self.path/'source.blocks.html';rendered_path.write_bytes(content)
        php=doc['steps'][2]['code'].replace("require_once '/wordpress/wp-load.php';",'')
        php=php.replace('/tmp/fv-ex2-page6-review.blocks.html',str(rendered_path))
        fixture='''<?php
        define('FV_EX2_LOCAL_ONLY',true);
        function wp_get_environment_type(){return getenv('FV_ENV') ?: 'local';}
        function parse_blocks($s){$b=[];foreach(range(1,substr_count($s,'<!-- wp:html -->')) as $i){$b[]=['blockName'=>'core/html','innerBlocks'=>[]];}
          $b[]=['blockName'=>'core/group','innerBlocks'=>[['blockName'=>'jetpack/subscriptions','innerBlocks'=>[]]]];return $b;}
        function get_page_by_path($x){return null;}
        function wp_slash($x){return $x;}
        function wp_insert_post($v,$e){$GLOBALS['saved']=$v;return 33;}
        function is_wp_error($e){return false;}
        function get_post($i){return (object)['post_content'=>$GLOBALS['saved']['post_content']];}
        function update_post_meta($id,$key,$value){return true;}
        function wp_delete_post($id,$force){throw new Exception('Unexpected delete');}
        ?>'''
        file=self.path/'mock.php';file.write_text(fixture+'\n'+php,encoding='utf-8')
        lint=subprocess.run(['php','-l',str(file)],capture_output=True,text=True)
        self.assertEqual(lint.returncode,0,lint.stderr)
        run=subprocess.run(['php',str(file)],capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stderr)
        denied=subprocess.run(['php',str(file)],env={'FV_ENV':'production'},capture_output=True,text=True)
        self.assertNotEqual(denied.returncode,0)
        self.assertIn('Not a verified isolated',denied.stderr)

    def test_rejects_wrong_page_sha(self):
        with self.assertRaisesRegex(ValueError,'source digest mismatch'):self.make(sha='0'*64)

    def test_rejects_changed_git_head(self):
        with self.assertRaisesRegex(ValueError,'HEAD mismatch'):
            bp.build(REPO,SOURCE,self.page,self.path/'review.zip','0'*40,self.sha,True)

    def test_rejects_original_jetpack_loss(self):
        self.page.write_text(self.fake.replace('wp:jetpack/subscriptions','wp:paragraph'))
        with self.assertRaisesRegex(ValueError,'Jetpack'):self.make(sha=hashlib.sha256(self.page.read_bytes()).hexdigest())

    def test_rejects_71_records(self):
        self.page.write_text(self.fake.replace('class="fv-margin-strip__item"','class="gone"',1))
        with self.assertRaisesRegex(ValueError,'72 Margins'):self.make(sha=hashlib.sha256(self.page.read_bytes()).hexdigest())

    def test_requires_synthetic_marker_on_synthetic_mode(self):
        self.page.write_text(self.fake.replace('FV-SYNTHETIC-FIXTURE','NOT-A-MARKER'))
        with self.assertRaisesRegex(ValueError,'unmistakably labeled'):self.make(sha=hashlib.sha256(self.page.read_bytes()).hexdigest())

    def test_rejects_synthetic_content_claimed_as_real(self):
        with self.assertRaisesRegex(ValueError,'Refusing synthetic'):
            self.make(synthetic=False)

    def test_refuses_existing_output(self):
        self.make()
        with self.assertRaisesRegex(ValueError,'Output must be a new'):self.make()

    def test_refuses_output_inside_repo(self):
        with self.assertRaisesRegex(ValueError,'Output must be a new'):
            bp.build(REPO,SOURCE,self.page,REPO/'bad.zip',self.head,self.sha,True)

    def test_rejects_symlinked_page(self):
        symlink=self.path/'link';symlink.symlink_to(self.page)
        with self.assertRaisesRegex(ValueError,'symlinked page'):
            bp.build(REPO,SOURCE,symlink,self.path/'review.zip',self.head,self.sha,True)


if __name__=='__main__':unittest.main(verbosity=2)
