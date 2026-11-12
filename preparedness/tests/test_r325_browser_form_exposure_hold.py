"""Synthetic-only adversarial tests; never a qualified source/privacy/QD PASS."""
import hashlib
import html
import json
import os
from pathlib import Path
import unittest
from preparedness.tools import r325_browser_form_exposure_hold as g
from preparedness.tools import r324_tool_privacy_egress_hold as r324
from preparedness.tools import r319_three_way_custody_hold as custody

class Gate(unittest.TestCase):
    def test_contract(self):
        self.assertFalse(any(g.RELEASE.values()))
        self.assertEqual(g.SCHEMA,'fv-preparedness-r325-browser-form-exposure-draft-hard-hold-v1')
    def test_blob_identity(self):
        self.assertEqual(g.audit(lambda p:b'bad')['state'],'INVALID_HARD_HOLD')
    def test_pin_set_modified(self):
        self.assertEqual(g.audit(lambda p:b'bad',{'fake':'abc'})['errors'],['PIN_SET_MISMATCH'])
    def test_no_form_not_approved(self):
        r=g.inspect_html(b'<p>Offline notes</p>')
        self.assertEqual(r['forms'],0);self.assertFalse(r['browser_privacy_approved'])
    def test_bytes_only(self):
        with self.assertRaises(TypeError):g.inspect_html('<form/>')
    def test_utf8_only(self):
        with self.assertRaises(UnicodeDecodeError):g.inspect_html(b'\xff')
    def test_nul_rejected(self):
        with self.assertRaises(ValueError):g.inspect_html(b'abc\x00')
    def test_nested_form_conservative(self):
        r=g.inspect_html(b'<form><form><input name=x></form></form>')
        self.assertTrue(any('GET_QUERY_FORM_HOLD' in f['flags'] for f in r['form_entries']))
    def test_duplicate_form_ids(self):
        r=g.inspect_html(b'<form id=x></form><form id=x></form>')
        self.assertIn('DUPLICATE_FORM_ID_HOLD',r['errors'])
    def test_submit_implicit(self):
        r=g.inspect_html(b'<form><input name=k></form>')
        self.assertIn('ENTER_IMPLICIT_SUBMIT_REVIEW',r['form_entries'][0]['flags'])
    def test_button_implicit_submit(self):
        r=g.inspect_html(b'<form><input name=k><button>Go</button></form>')
        self.assertIn('EXPLICIT_SUBMIT_CONTROL_REVIEW',r['form_entries'][0]['flags'])
    def test_button_override(self):
        r=g.inspect_html(b'<form method=post><input name=k><button formaction="https://example.org" formmethod=get>Go</button></form>')
        self.assertIn('BUTTON_OVERRIDE_DESTINATION_REVIEW',r['form_entries'][0]['flags'])
    def test_external_form_field(self):
        r=g.inspect_html(b'<form id=foo></form><input form=foo name=email type=email>')
        self.assertIn('POTENTIAL_PRIVATE_QUERY_STRING',r['form_entries'][0]['flags'])
    def test_csp_handler_not_safety(self):
        r=g.inspect_html(b'<form onsubmit="return false"><input name=email type=email></form>')
        self.assertIn('INLINE_JS_NOT_NOJS_PROTECTION',r['form_entries'][0]['flags'])
        self.assertIn('POTENTIAL_PRIVATE_QUERY_STRING',r['form_entries'][0]['flags'])
    def test_dialog_not_privacy_pass(self):
        r=g.inspect_html(b'<form method=dialog><input name=email type=email></form>')
        self.assertIn('DIALOG_CONTEXT_NOT_PROVEN_HOLD',r['form_entries'][0]['flags'])
    def test_base_tag(self):
        self.assertIn('BASE_URI_REVIEW',g.inspect_html(b'<base href="https://example.org">')['errors'])
    def test_external_script(self):
        self.assertIn('EXTERNAL_SCRIPT_REVIEW',g.inspect_html(b'<script src="a.js"></script>')['errors'])
    def test_no_real_human_input_values(self):
        # Behavior output summarizes counts/flags; no field names or values emitted.
        s=g.inspect_html(b'<form><input type=email name="child_private_email"></form>')
        self.assertNotIn('child_private_email',json.dumps(s))

class Browser(unittest.TestCase):
    @unittest.skipUnless(os.path.exists('/usr/bin/chromium'),'chromium missing')
    def test_js_off_get_csp_exposure(self):
        raw=b'<html><body><form onsubmit="return false"><input name=contact type=text><button>Submit</button></form></body></html>'
        r=g.browser_probe(raw)
        self.assertEqual(r['state'],'BROWSER_DOM_SEMANTICS_OBSERVED_STILL_HARD_HOLD',r)
        self.assertEqual(r['observations'][0]['forms'][0]['method'],'GET')
        self.assertFalse(r['browser_privacy_approved'])
    @unittest.skipUnless(os.path.exists('/usr/bin/chromium'),'chromium missing')
    def test_button_type_button_no_observed_exposure(self):
        raw=b'<html><body><form><input name=contact type=text><button type=button>Print only</button></form></body></html>'
        r=g.browser_probe(raw)
        # Enter can implicitly submit a one-text-field form even when button is type=button.
        self.assertEqual(r['state'],'BROWSER_DOM_SEMANTICS_OBSERVED_STILL_HARD_HOLD',r)
        self.assertFalse(r['browser_privacy_approved'])
    @unittest.skipUnless(os.path.exists('/usr/bin/chromium'),'chromium missing')
    def test_dialog_no_approval(self):
        raw=b'<html><body><dialog open><form method=dialog><input name=contact type=text><button>OK</button></form></dialog></body></html>'
        r=g.browser_probe(raw)
        self.assertEqual(r['state'],'BROWSER_DOM_SEMANTICS_OBSERVED_STILL_HARD_HOLD',r)
        self.assertFalse(r['browser_privacy_approved'])

# Generate standalone discoverable independent test cases rather than counting subtests.
methods=['','get','GET','gEt','post','POST','dialog','DIALOG','delete','head','options','patch']
kinds=['text','email','tel','number','date','password','search','hidden','checkbox','radio','submit','image','url','textarea','select']
for mi,method in enumerate(methods):
    for ki,kind in enumerate(kinds):
        if (mi*len(kinds)+ki)%3:continue
        def check(self,method=method,kind=kind):
            meth=f' method="{method}"' if method else ''
            field=f'<{kind} name=x></{kind}>' if kind in ('textarea','select') else f'<input name=x type={kind}>'
            raw=(f'<form{meth} onsubmit="return false">{field}<button type="button">A</button></form>').encode()
            report=g.inspect_html(raw)
            self.assertEqual(report['forms'],1)
            self.assertEqual(report['form_entries'][0]['method'],method.upper() if method else 'GET')
            flags=report['form_entries'][0]['flags']
            self.assertIn('INLINE_JS_NOT_NOJS_PROTECTION',flags)
            if (method or 'GET').upper()=='GET':self.assertIn('GET_QUERY_FORM_HOLD',flags)
            if (method or 'GET').upper()=='POST':self.assertIn('POST_NETWORK_FORM_HOLD',flags)
            if (method or 'GET').upper() not in g.FORM_METHODS:self.assertIn('UNSUPPORTED_FORM_METHOD_HOLD',flags)
            self.assertFalse(report['browser_privacy_approved'])
        setattr(Gate,f'test_matrix_{mi:02d}_{ki:02d}',check)

if __name__=='__main__':unittest.main()
