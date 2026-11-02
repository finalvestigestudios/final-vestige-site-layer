"""R68 read-only local contract tests; real WordPress gate runs separately in CI."""
import hashlib, json, tempfile, unittest, zipfile
from pathlib import Path
from wordpress_r68 import blueprint, unpack_assembler, digest, PLUGINS, BASE, SLUG

def make_zip(path,extra=None):
    files={'assembler-wpcom/style.css':'/*\nTheme Name: Assembler\n*/',
           'assembler-wpcom/templates/index.html':'<!-- wp:group --><!-- /wp:group -->'}
    files.update(extra or {})
    with zipfile.ZipFile(path,'w') as a:
        for name,data in files.items():a.writestr(name,data)

class R68WordPressContracts(unittest.TestCase):
    def test_only_ephemeral_local_host(self):
        self.assertEqual(BASE,'http://127.0.0.1:9438/')
        self.assertEqual(SLUG,'fv-apollo-review-private')
        self.assertEqual(len(PLUGINS),3)
        data=blueprint()
        self.assertTrue(data['login'])
        self.assertEqual(data['steps'][0]['consts']['WP_ENVIRONMENT_TYPE'],'local')
        self.assertIn('post_status',data['steps'][-1]['code'])
        self.assertIn("'private'",data['steps'][-1]['code'])
        self.assertIn('NONLOCAL_WORDPRESS_REFUSED',data['steps'][-1]['code'])
        self.assertNotIn('https://finalvestige.com',json.dumps(data))
    def test_exactly_three_components(self):
        steps=blueprint()['steps']
        plugins=[s['pluginPath'] for s in steps if s['step']=='activatePlugin']
        self.assertEqual(len(plugins),3)
        self.assertEqual(plugins,[f'/wordpress/wp-content/plugins/{slug}/{filename}'
            for slug,filename in PLUGINS])
    def test_normalize_actual_assembler_folder(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);z=root/'t.zip';make_zip(z)
            self.assertEqual(unpack_assembler(z,root/'out'),2)
            self.assertTrue((root/'out/style.css').exists())
    def test_reject_traversal(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);z=root/'t.zip'
            make_zip(z,{'assembler-wpcom/../../outside.txt':'bad'})
            with self.assertRaisesRegex(ValueError,'UNSAFE_THEME_ARCHIVE'):
                unpack_assembler(z,root/'out')
    def test_reject_duplicate_case_fold(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);z=root/'t.zip'
            make_zip(z,{'assembler-wpcom/STYLE.CSS':'bad'})
            with self.assertRaisesRegex(ValueError,'DUPLICATE_THEME_FILE'):
                unpack_assembler(z,root/'out')
    def test_real_browser_uses_playwright_response_status_property(self):
        # Playwright Python Response.status is an int property, not a function.
        source=Path(__file__).with_name('wordpress_r68.py').read_text()
        self.assertIn('res.status==200', source)
        self.assertNotIn('res.status()', source)
    def test_nasa_image_prohibition_scoped_to_component(self):
        # Assembler theme may own decorative images. Only Apollo-owned
        # photographic usage is subject to its current media clearance HOLD.
        source=Path(__file__).with_name('wordpress_r68.py').read_text()
        self.assertIn("page.locator('.fv-ex2-apollo-suite img').count()==0",source)
        self.assertNotIn("page.locator('img').count()==0",source)
    def test_reject_unrecognized_theme(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);z=root/'t.zip'
            make_zip(z,{'assembler-wpcom/style.css':'/*\nTheme Name: Other\n*/'})
            with self.assertRaisesRegex(ValueError,'THEME_NOT_ASSEMBLER'):
                unpack_assembler(z,root/'out')

if __name__=='__main__': unittest.main()
