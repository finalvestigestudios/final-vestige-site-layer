"""R437 deterministic isolated synthetic review tests; NOT authentic export or QD PASS."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

TOOLS=Path(__file__).resolve().parents[1]/'tools'
SRC=TOOLS/'r437_fallback_print_disclosure_custody_gate.py'
spec=importlib.util.spec_from_file_location('r437',SRC)
r437=importlib.util.module_from_spec(spec)
spec.loader.exec_module(r437)
base_spec=importlib.util.spec_from_file_location('r436',TOOLS/'r436_outside_main_semantic_custody_gate.py')
r436=importlib.util.module_from_spec(base_spec)
base_spec.loader.exec_module(r436)

def html(extra='',main='<p>Official sources and review dates matter.</p>',head=''):
    return ('<!DOCTYPE html><html><head><title>Preparedness</title>'+head+
            '</head><body><main>'+main+extra+'</main><footer>Follow local orders.</footer></body></html>').encode()

class Contract(unittest.TestCase):
    def test_clean_pair(self):self.assertEqual(r437.pair_review(html(),html())['errors'],[])
    def test_clean_fallback(self):self.assertEqual(r437.inspect(html('<noscript><p>Offline overview</p></noscript>'))['errors'],[])
    def test_nojs_copy_diff(self):
        a=html('<noscript><p>Read the guide carefully</p></noscript>')
        b=html('<noscript><p>Read slowly</p></noscript>')
        self.assertIn('NOJS_FALLBACK_COPY_OR_LINK_DRIFT',r437.pair_review(a,b)['errors'])
        self.assertEqual(r436.pair_review(a,b)['errors'],[],'demonstrates old gap')
    def test_unchanged_noscript_no_drift(self):
        a=html('<noscript><p>Read the guide carefully</p></noscript>')
        self.assertEqual(r437.pair_review(a,a)['errors'],[])
    def test_print_rule_drift(self):
        a=html(head='<style>@media print { body {color: black;} }</style>')
        b=html(head='<style>@media print { body {color: navy;} }</style>')
        self.assertIn('PRINT_STYLESHEET_RULE_DRIFT',r437.pair_review(a,b)['errors'])
    def test_unrelated_style_not_print_rule(self):
        a=html(head='<style>p{font-size:1rem}</style>')
        b=html(head='<style>p{font-size:1.2rem}</style>')
        self.assertNotIn('PRINT_STYLESHEET_RULE_DRIFT',r437.pair_review(a,b)['errors'])
    def test_print_hide_review(self):
        x=r437.inspect(html(head='<style>@media print { .warning {display:none} }</style>'))
        self.assertIn('PRINT_STYLE_POTENTIAL_WARNING_CONCEALMENT',x['errors'])
    def test_print_external_hold(self):
        x=r437.inspect(html(head='<link rel="stylesheet" media="print" href="/print.css">'))
        self.assertIn('EXTERNAL_PRINT_STYLESHEET_NOT_BYTE_AUTHENTICATED',x['errors'])
    def test_print_external_destination_drift(self):
        a=html(head='<link rel="stylesheet" media="print" href="/print-a.css">')
        b=html(head='<link rel="stylesheet" media="print" href="/print-b.css">')
        self.assertIn('EXTERNAL_PRINT_STYLESHEET_DESTINATION_DRIFT',r437.pair_review(a,b)['errors'])
    def test_disclosure_visibility_diff(self):
        a=html('<details><summary>Warnings</summary><p>Hazard explanation</p></details>')
        b=html('<details open><summary>Warnings</summary><p>Hazard explanation</p></details>')
        self.assertIn('DISCLOSURE_DEFAULT_VISIBILITY_DRIFT',r437.pair_review(a,b)['errors'])
        self.assertEqual(r436.pair_review(a,b)['errors'],[],'demonstrates old gap')
    def test_safety_collapsed_review(self):
        a=html('<details><summary>Notice</summary><p>Follow evacuation orders.</p></details>')
        self.assertIn('COLLAPSED_SAFETY_DISCLOSURE_REVIEW',r437.inspect(a)['errors'])
    def test_safety_open_not_collapsed(self):
        a=html('<details open><summary>Notice</summary><p>Follow evacuation orders.</p></details>')
        self.assertNotIn('COLLAPSED_SAFETY_DISCLOSURE_REVIEW',r437.inspect(a)['errors'])
    def test_details_no_summary(self):
        self.assertIn('DETAILS_SUMMARY_MISSING',r437.inspect(html('<details><p>Historical content</p></details>'))['errors'])
    def test_dialog_visibility_diff(self):
        a=html('<dialog><p>Reference</p></dialog>');b=html('<dialog open><p>Reference</p></dialog>')
        self.assertIn('DISCLOSURE_DEFAULT_VISIBILITY_DRIFT',r437.pair_review(a,b)['errors'])
    def test_bidi_in_text(self):
        self.assertIn('INVISIBLE_OR_BIDI_TEXT_REVIEW',r437.inspect(html('<p>Read \u202elocal orders</p>'))['errors'])
    def test_bidi_in_attribute(self):
        self.assertIn('INVISIBLE_OR_BIDI_ATTRIBUTE_REVIEW',r437.inspect(html('<p aria-label="Unsafe\u200d order">Notice</p>'))['errors'])
    def test_valid_input_type(self):self.assertEqual(r437.inspect(html('<input type="checkbox" aria-label="Check">'))['errors'],[])
    def test_invalid_utf8(self):
        with self.assertRaises(UnicodeError):r437.inspect(b'<html>\xff</html>')
    def test_invalid_null(self):
        with self.assertRaises(ValueError):r437.inspect(b'<html>\0</html>')
    def test_max_size(self):
        with self.assertRaises(ValueError):r437.inspect(b'x'*(r437.MAX_BYTES+1))
    def test_non_bytes(self):
        with self.assertRaises(ValueError):r437.inspect('html text')
    def test_empty(self):
        with self.assertRaises(ValueError):r437.inspect(b'')
    def test_manifest_missing(self):
        with patch.object(r437,'load_parent',side_effect=ValueError):
            self.assertIn('PARENT_R436_AUDIT_UNAVAILABLE',r437.audit({}, {}, {})['errors'])
    def test_missing_pair(self):
        with patch.object(r437,'load_parent') as f:
            f.return_value.audit.return_value={'errors':[]}
            out=r437.audit({'articles':[{'slug':'a'}]},{},{},test_only=True)
        self.assertIn('MISSING_EXPORT_PAIR:a',out['errors'])
    def test_duplicate_slug(self):
        with patch.object(r437,'load_parent') as f:
            f.return_value.audit.return_value={'errors':[]}
            out=r437.audit({'articles':[{'slug':'a'},{'slug':'a'}]},{'a':(html(),html())},{},test_only=True)
        self.assertIn('DUPLICATE_OR_INVALID_ARTICLE_IDENTITY',out['errors'])
    def test_surplus_pair(self):
        with patch.object(r437,'load_parent') as f:
            f.return_value.audit.return_value={'errors':[]}
            out=r437.audit({'articles':[{'slug':'a'}]},{'a':(html(),html()),'b':(html(),html())},{},test_only=True)
        self.assertIn('EXTRA_OR_MISSING_EXPORT_IDENTITY',out['errors'])
    def test_hard_hold_forever(self):
        out=r437.hold([],{'errors':[]},[{'slug':'test'}]*35)
        self.assertFalse(out['eligible']);self.assertFalse(out['publication_approved'])
        self.assertFalse(out['qualified_safety_approved']);self.assertFalse(out['paid_offer_approved'])
        self.assertIsNone(out['merchant_confirmed_orders']);self.assertIsNone(out['net_revenue_per_1000_qualified_human_sessions'])
    def test_cli_missing_evidence_exit_2(self):
        p=subprocess.run([sys.executable,'-I',str(SRC),'/missing/manifest','/missing/lock','/missing/exports'],capture_output=True,text=True,timeout=6)
        self.assertEqual(p.returncode,2);self.assertIn('DRAFT_HARD_HOLD',p.stdout)
    def test_no_network_cms_dependencies(self):
        code=SRC.read_text()
        for word in ('requests.', 'urllib.request', 'httpx.', 'subprocess.run(', 'wordpress_xmlrpc','wp_remote_post','selenium.'):
            with self.subTest(word=word):self.assertNotIn(word,code)
    def test_repeated_parse_determinism(self):
        x=html('<details open><summary>Instructions</summary><p>Read the guide</p></details>')
        self.assertEqual(r437.inspect(x),r437.inspect(x))

# Explicit independent named tests rather than inflating assertions or shared subtests.
NOJS_ADVISORIES={
 'evacuation':'Follow local evacuation notices.',
 'medical':'Speak to a medical professional.',
 'generator':'Generator exhaust contains carbon monoxide.',
 'water':'Boil water only if the authority says that works.',
 'food':'Food safety during outages has limits.',
 'child':'Child reunion instructions require privacy review.',
 'contact':'Keep emergency contact numbers private.',
 'checkout':'Do not require checkout for emergency instructions.',
 'subscription':'Subscribe only with affirmative consent.',
 'first_aid':'First aid does not replace emergency services.',
 '911':'Call 911 for immediate emergency help.',
 'purification':'Purification does not eliminate every contaminant.',
}
PRINT_STYLES={
 'display_none':'@media print{.warning{display:none}}',
 'visibility_hidden':'@media print{#source{visibility:hidden}}',
 'opacity_zero':'@media print{.alert{opacity:0}}',
 'content_empty':'@media print{.alert::after{content:""}}',
 'content_none':'@media print{.alert::after{content:none}}',
}
DISAPPEAR={
 'warning':'Safety warning',
 'evacuation':'Review evacuation orders',
 'medicine':'Medication storage',
 'carbon_monoxide':'Carbon monoxide hazard',
 'generator':'Generator location matters',
 'children':'Child safety contacts',
 'first_aid':'First aid',
 'food':'Food safety',
 'boil':'Boil water notice',
}
INVISIBLE={
 'zwsp':'\u200b','zwnj':'\u200c','zwj':'\u200d','lrm':'\u200e','rlm':'\u200f',
 'lre':'\u202a','rle':'\u202b','pdf':'\u202c','lro':'\u202d','rlo':'\u202e',
 'lri':'\u2066','rli':'\u2067','fsi':'\u2068','pdi':'\u2069',
}

def make_nojs(value):
    def check(self):
        raw=html('<noscript><p>'+value+'</p></noscript>')
        self.assertIn('NOJS_ACTIONABLE_GUIDANCE_QUALIFIED_REVIEW',r437.inspect(raw)['errors'])
    return check
for label,value in NOJS_ADVISORIES.items():setattr(Contract,'test_nojs_advisory_'+label,make_nojs(value))

def make_print(css):
    def check(self):
        self.assertIn('PRINT_STYLE_POTENTIAL_WARNING_CONCEALMENT',r437.inspect(html(head='<style>'+css+'</style>'))['errors'])
    return check
for label,css in PRINT_STYLES.items():setattr(Contract,'test_print_hiding_'+label,make_print(css))

def make_disclosure(txt):
    def check(self):
        raw=html('<details><summary>Details</summary><p>'+txt+'</p></details>')
        self.assertIn('COLLAPSED_SAFETY_DISCLOSURE_REVIEW',r437.inspect(raw)['errors'])
    return check
for label,txt in DISAPPEAR.items():setattr(Contract,'test_disclosure_'+label,make_disclosure(txt))

def make_unicode(char):
    def check(self):
        raw=html('<p>Local'+char+'orders</p>')
        self.assertIn('INVISIBLE_OR_BIDI_TEXT_REVIEW',r437.inspect(raw)['errors'])
    return check
for label,char in INVISIBLE.items():setattr(Contract,'test_unicode_'+label,make_unicode(char))

if __name__=='__main__':unittest.main()
