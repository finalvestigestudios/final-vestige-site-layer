import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from sanitize_theme_parity import prepare, safe_css, safe_markup

BASE = Path(__file__).parent


def sample():
    return {
        'site': 'https://finalvestige.com',
        'theme': {'stylesheet': 'assembler', 'version': '0.0.126'},
        'templates': {
            'page': {'id':'assembler//page','content': '''<!-- wp:template-part {"slug":"header","theme":"assembler"} /-->
<!-- wp:group --><main class="wp-block-group"><!-- wp:post-content /--></main><!-- /wp:group -->
<!-- wp:html --><style>.fv{color:#f4efe6}</style><!-- /wp:html -->
<!-- wp:template-part {"slug":"footer","theme":"assembler"} /-->'''},
            'header': {'id':'assembler//header','content': '''<!-- wp:group --><header><a href="/">FINAL VESTIGE</a></header><!-- /wp:group -->
<!-- wp:html --><script>window.PRODUCTION_TRACKER = "PRIVATE_PROJECT_ID"</script><!-- /wp:html -->'''},
            'footer': {'id':'assembler//footer','content': '''<!-- wp:group --><footer><a href="/focus/">Focus</a><a href="/affiliate-disclosure/">Disclosure</a></footer><!-- /wp:group -->
<!-- wp:html --><script src="https://www.googletagmanager.com/gtm.js?id=GTM-PRIVATE"></script><!-- /wp:html -->
<!-- wp:html --><script>posthog.init('phc_PRIVATE_PROJECT_KEY')</script><!-- /wp:html -->'''},
            'overlay': {'id':'assembler//fv-archive-index-overlay','content': '''<!-- wp:group --><nav aria-label="Archive"><a href="/archive/">Archive</a></nav><!-- /wp:group -->
<!-- wp:html --><style>.fv-overlay{width:100%}</style><!-- /wp:html -->'''}
        },
        'global_styles': {'settings':{'layout':{'contentSize':'760px','wideSize':'1440px'}},'styles':{'css':'.fv{background:#090a0a;color:#f4efe6}'}}
    }

class ParityTests(unittest.TestCase):
    def test_production_trackers_are_entirely_excluded(self):
        output, report=prepare(sample())
        payload=json.dumps(output)
        self.assertNotIn('posthog',payload)
        self.assertNotIn('googletagmanager',payload)
        self.assertNotIn('PRIVATE_PROJECT',payload)
        self.assertNotIn('<script',payload)
        self.assertEqual(report['omitted_custom_html_blocks']['footer'],2)
        self.assertEqual(report['omitted_custom_html_blocks']['header'],1)
        self.assertFalse(report['staging_has_production_analytics'])

    def test_mixed_style_and_tracking_preserves_only_safe_css(self):
        raw='<!-- wp:html --><style id="fv-cursor-r2">.nav{color:#fff}</style><script>posthog.init("secret")</script><!-- /wp:html -->'
        output,omitted=safe_markup('<!-- wp:group --><header>ARCHIVE</header><!-- /wp:group -->'+raw)
        self.assertEqual(omitted,1)
        self.assertIn('<style>.nav{color:#fff}</style>',output)
        self.assertNotIn('<script',output)
        self.assertNotIn('secret',output)

    def test_public_content_and_global_styles_survive(self):
        output,_=prepare(sample())
        self.assertIn('FINAL VESTIGE',output['template_content']['header'])
        self.assertIn('/focus/',output['template_content']['footer'])
        self.assertIn('/affiliate-disclosure/',output['template_content']['footer'])
        self.assertIn('fv-overlay{width:100%}',output['template_content']['overlay'])
        self.assertIn('wp:post-content',output['template_content']['page'])
        self.assertEqual(output['global_styles']['settings']['layout']['wideSize'],'1440px')
        self.assertEqual(output['release'],'HOLD')

    def test_outside_html_block_script_is_rejected(self):
        src=sample()
        src['templates']['header']['content']+='<script>alert(1)</script>'
        with self.assertRaises(ValueError):prepare(src)

    def test_unmatched_block_must_not_pass_through(self):
        src=sample();src['templates']['footer']['content']+='<!-- wp:html --><script>bad</script>'
        with self.assertRaises(ValueError):prepare(src)

    def test_inline_event_handlers_are_rejected(self):
        src=sample();src['templates']['header']['content']+='<a onclick="leak()" href="#">X</a>'
        with self.assertRaises(ValueError):prepare(src)

    def test_reject_remote_styles_and_markup_in_css(self):
        for css in ('@import "https://evil.tld/x.css";',
                    'div{background:url(//evil.tld/img)}',
                    '<style>x</style>',
                    '.x{color:red}</style>',
                    '.x{color:red}</style><script>bad()</script>'):
            with self.subTest(css=css),self.assertRaises(ValueError):safe_css(css)

    def test_reject_wrong_source_theme_version_and_extra_fields(self):
        for mutate in (
            lambda x: x['theme'].update(version='0.0.125'),
            lambda x: x.update(site='https://attacker.tld'),
            lambda x: x.update(subscribers=['someone@example.com']),
            lambda x: x['templates']['page'].update(id='assembler//single'),
            lambda x: x['global_styles']['settings'].update(layout={'contentSize':'100vw','wideSize':'900px'}),
        ):
            src=sample();mutate(src)
            with self.assertRaises(ValueError):prepare(src)

    def test_reject_shortcodes_and_private_emails(self):
        for fragment in ('<!-- wp:shortcode -->[tracking]<!-- /wp:shortcode -->',
                         'Contact PRIVATE@example.org',
                         '<img src="javascript:alert(1)">'):
            with self.subTest(fragment=fragment),self.assertRaises(ValueError):safe_markup(sample()['templates']['header']['content']+fragment)

    def test_source_receipt_is_deterministic_and_has_no_secret(self):
        a,ar=prepare(sample());b,br=prepare(sample())
        self.assertEqual(a,b);self.assertEqual(ar,br)
        self.assertNotIn('PRIVATE_PROJECT',json.dumps(ar))
        self.assertTrue(all(len(v)==64 for v in ar['source_template_sha256'].values()))
        self.assertFalse(ar['import_performed'])
        self.assertFalse(ar['wordpress_parity_verified'])

    def test_cli_only_writes_new_output_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'raw.snapshot.json';source.write_text(json.dumps(sample()))
            output=Path(tmp)/'out'
            runner=BASE/'sanitize_theme_parity.py'
            cmd=['python',str(runner),'--snapshot',str(source),'--out',str(output)]
            r=subprocess.run(cmd,capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertTrue((output/'site-parity.safe.json').exists())
            self.assertFalse((output/'site-parity.safe.json').read_text().find('PRIVATE_PROJECT')!=-1)
            second=subprocess.run(cmd,capture_output=True,text=True)
            self.assertNotEqual(second.returncode,0)

    def test_php_guard_uses_loopback_environment_theme_and_marker(self):
        php=(BASE/'apply_local_parity.php').read_text()
        for value in ('wp_get_environment_type()', "'localhost'", "'127.0.0.1'", "'assembler'", "'0.0.126'", "'HOLD'", "'_fv_ex2_local_parity'", 'wp_template_part', 'wp_global_styles'):
            self.assertIn(value,php)
        result=subprocess.run(['php','-l',str(BASE/'apply_local_parity.php')],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_browser_executes_no_production_tracker_from_sanitized_markup(self):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            self.skipTest('Playwright not installed; no browser PASS claim')
        output,_=prepare(sample())
        # This is a synthetic visual fixture, not actual WordPress block rendering.
        html='<!doctype html><html><body>'+output['template_content']['header']+output['template_content']['footer']+'</body></html>'
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
            page=browser.new_page(); requests=[]
            page.on('request',lambda request:requests.append(request.url))
            page.route('**/*',lambda route:route.abort())
            page.set_content(html)
            self.assertIsNone(page.evaluate('window.PRODUCTION_TRACKER'))
            self.assertEqual(requests,[])
            self.assertTrue(page.locator('a[href="/focus/"]').count())
            browser.close()

if __name__=='__main__':unittest.main()
