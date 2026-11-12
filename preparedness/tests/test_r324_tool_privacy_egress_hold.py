"""R324: source-custody and conservative privacy/egress review flags (not QD)."""
import unittest
from preparedness.tools import r324_tool_privacy_egress_hold as gate
from preparedness.tools import r319_three_way_custody_hold as custody

class Core(unittest.TestCase):
    def test_six_immutable_identifiers(self):
        self.assertEqual(len(gate.PINS),6)
        self.assertEqual(len(set(gate.PINS.values())),6)
        self.assertNotEqual(gate.PINS['reunification-plan'],gate.PINS['family-reunification-card'])
    def test_incomplete_source_hard_holds(self):
        result=gate.audit(lambda _:(_ for _ in ()).throw(OSError('missing')))
        self.assertEqual(result['state'],'INVALID_HARD_HOLD');self.assertEqual(result['tools_audited'],0)
    def test_nonbytes_hard_holds(self):
        self.assertEqual(gate.audit(lambda p:'not bytes')['state'],'INVALID_HARD_HOLD')
    def test_fake_pins_hard_hold(self):
        example=b'<form><input type="tel"></form>'
        fake={k:custody.blob(example) for k in gate.PINS}
        result=gate.audit(lambda _:example,fake)
        self.assertEqual(result['state'],'INVALID_HARD_HOLD')
    def test_missing_tool_hard_hold(self):
        self.assertIn('SIX_TOOL_IDENTITY_SET_CHANGED',gate.audit(lambda _:b'',{})['errors'])
    def test_non_utf8_rejected(self):
        with self.assertRaises(UnicodeError):gate.inspect_body(b'\xff')
    def test_nul_rejected(self):
        with self.assertRaises(ValueError):gate.inspect_body(b'a\x00b')
    def test_no_runtime_or_commercial_approval(self):
        self.assertTrue(all(v is False for v in gate.RELEASE.values()))
    def test_determinism(self):
        x=b'<form><input type="email"><script>fetch("/hello")</script></form>'
        self.assertEqual(gate.inspect_body(x),gate.inspect_body(x))
    def test_private_fields_are_not_proof_of_egress(self):
        a=gate.inspect_body(b'<form onsubmit="return false"><input type="tel"><button type="button"></button></form>')
        self.assertIn('HOUSEHOLD_FIELD_PRIVACY_REVIEW',a['review_flags'])
        self.assertNotIn('SCRIPT_SINK_FETCH_REVIEW',a['review_flags'])
    def test_script_words_in_prose_not_code(self):
        self.assertNotIn('SCRIPT_SINK_FETCH_REVIEW',gate.inspect_body(b'<p>fetch("/a")</p>')['review_flags'])

class Generated(unittest.TestCase):pass

def make_uri(uri,expected):
    def test(self):self.assertEqual(gate.classify_url(uri),expected)
    return test
for i,(uri,want) in enumerate([
    ('','empty'),(' ','empty'),('/preparedness/','relative'),('../guide','relative'),('#part','relative'),
    ('https://ready.gov/','network'),('http://example.org','network'),('//example.org','network'),
    ('javascript:alert(1)','active_or_local'),('data:text/plain,a','active_or_local'),
    ('vbscript:echo','active_or_local'),('file:///tmp/a','active_or_local'),
    ('blob:https://x/y','active_or_local'),('mailto:me@example.org','nonweb_scheme'),
    ('tel:911','nonweb_scheme'),('https://x/a b','invalid'),('/a\n','relative'),('\x00','invalid'),
]):setattr(Generated,f'test_uri_{i:02d}',make_uri(uri,want))

def make_script(code,sink):
    def test(self):
        out=gate.inspect_body(('<script>'+code+'</script>').encode())
        self.assertIn('SCRIPT_SINK_'+sink+'_REVIEW',out['review_flags'])
    return test
for i,(script,sink) in enumerate([
    ('fetch("/x")','FETCH'),('fetch ("/x")','FETCH'),('new XMLHttpRequest()','XHR'),
    ('navigator.sendBeacon("/x",x)','BEACON'),('new WebSocket("wss://s")','SOCKET'),
    ('new EventSource("/events")','EVENTSOURCE'),('localStorage.setItem("x",y)','STORAGE'),
    ('sessionStorage.clear()','STORAGE'),('indexedDB.open("x")','STORAGE'),
    ('document.cookie="x"','STORAGE'),('navigator.serviceWorker.register("a.js")','SERVICEWORKER'),
]):setattr(Generated,f'test_script_{i:02d}',make_script(script,sink))

def make_html(html,flag,expected=True):
    def test(self):
        found=flag in gate.inspect_body(html.encode())['review_flags']
        self.assertEqual(found,expected)
    return test
for i,(html,flag,expect) in enumerate([
    ('<form><input type="text"></form>','GET_FORM_DEFAULT_OR_EXPLICIT_REVIEW',True),
    ('<form method="POST"></form>','GET_FORM_DEFAULT_OR_EXPLICIT_REVIEW',False),
    ('<form action="/collect"></form>','FORM_ACTION_REQUIRES_PRIVACY_REVIEW',True),
    ('<form></form>','FORM_SUBMIT_HANDLER_ABSENT_REVIEW',True),
    ('<form><button>Go</button></form>','SUBMIT_BUTTON_REVIEW',True),
    ('<button type="button">Print</button>','SUBMIT_BUTTON_REVIEW',False),
    ('<input type="tel">','HOUSEHOLD_FIELD_PRIVACY_REVIEW',True),
    ('<input type="checkbox">','HOUSEHOLD_FIELD_PRIVACY_REVIEW',False),
    ('<textarea></textarea>','HOUSEHOLD_FIELD_PRIVACY_REVIEW',True),
    ('<input type="text">','NO_NOSCRIPT_WITNESS_REVIEW',True),
    ('<input type="text"><noscript>Print paper</noscript>','NO_NOSCRIPT_WITNESS_REVIEW',False),
    ('<script src="https://elsewhere.test/a.js"></script>','SCRIPT_SRC_REQUIRES_REVIEW',True),
    ('<iframe src="/doc"></iframe>','EMBED_OR_BASE_REQUIRES_REVIEW',True),
    ('<object data="https://elsewhere.test"></object>','EXTERNAL_OR_ACTIVE_ASSET_REVIEW',True),
    ('<img src="https://elsewhere.test/pixel">','EXTERNAL_OR_ACTIVE_ASSET_REVIEW',True),
    ('<link href="//elsewhere.test/app.css">','EXTERNAL_OR_ACTIVE_ASSET_REVIEW',True),
    ('<a href="https://unverified-seller.test">Buy</a>','OUTBOUND_OR_ACTIVE_LINK_REVIEW',True),
    ('<a href="/preparedness/">Guide</a>','OUTBOUND_OR_ACTIVE_LINK_REVIEW',False),
    ('<a href="javascript:alert(1)">Bad</a>','OUTBOUND_OR_ACTIVE_LINK_REVIEW',True),
]):setattr(Generated,f'test_html_{i:02d}',make_html(html,flag,expect))
if __name__=='__main__':unittest.main()
