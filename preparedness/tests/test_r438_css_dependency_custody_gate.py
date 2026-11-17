"""R438 synthetic, fail-closed CSS custody tests. No actual browser/QD approval."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

TOOLS=Path(__file__).resolve().parents[1]/'tools'
SRC=TOOLS/'r438_css_dependency_custody_gate.py'

def load(n):
    spec=importlib.util.spec_from_file_location(n,TOOLS/(n+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
r438=load('r438_css_dependency_custody_gate')
r437=load('r437_fallback_print_disclosure_custody_gate')

def html(extra='',head='',attrs=''):
    return ('<!doctype html><html><head><title>Archive</title>'+head+'</head><body><main><p '+attrs+
            '>Use official sources.</p>'+extra+'</main><footer>Follow local orders.</footer></body></html>').encode()

class Contract(unittest.TestCase):
    def test_clean_pair(self):self.assertEqual(r438.pair_review(html(),html())['errors'],[])
    def test_clean_embedded_css(self):self.assertEqual(r438.inspect(html(head='<style>p{color:black}</style>'))['errors'],[])
    def test_embed_drift(self):
        a=html(head='<style>p{color:black}</style>');b=html(head='<style>p{color:red}</style>')
        self.assertIn('INLINE_STYLESHEET_PARITY_DRIFT',r438.pair_review(a,b)['errors'])
    def test_external_screen_css_gap(self):
        x=html(head='<link rel="stylesheet" media="screen" href="/hide-warning.css">')
        self.assertEqual(r437.pair_review(x,x)['errors'],[],'older print-only gate misses screen stylesheet')
        self.assertIn('wordpress:EXTERNAL_CSS_BYTES_UNVERIFIED',r438.pair_review(x,x)['errors'])
    def test_inline_import_old_gap(self):
        x=html(head='<style>@import "/malicious-print.css" screen;</style>')
        self.assertEqual(r437.pair_review(x,x)['errors'],[],'earlier print-only gate misses import')
        self.assertIn('wordpress:CSS_IMPORT_DEPENDENCY_UNAUTHENTICATED',r438.pair_review(x,x)['errors'])
    def test_link_drift(self):
        a=html(head='<link rel="stylesheet" media="screen" href="/safe.css">')
        b=html(head='<link rel="stylesheet" media="screen" href="/other.css">')
        self.assertIn('CSS_DEPENDENCY_OR_INTEGRITY_PARITY_DRIFT',r438.pair_review(a,b)['errors'])
    def test_integrity_drift(self):
        a=html(head='<link rel="stylesheet" href="/a.css" integrity="sha384-good">')
        b=html(head='<link rel="stylesheet" href="/a.css" integrity="sha384-bad">')
        self.assertIn('CSS_DEPENDENCY_OR_INTEGRITY_PARITY_DRIFT',r438.pair_review(a,b)['errors'])
    def test_preload_style(self):
        x=r438.inspect(html(head='<link rel="preload" as="style" href="/print.css">'))
        self.assertIn('EXTERNAL_CSS_BYTES_UNVERIFIED',x['errors'])
    def test_base_href(self):
        x=r438.inspect(html(head='<base href="https://evil.invalid/">'))
        self.assertIn('HTML_BASE_CHANGES_LINK_RESOLUTION_REQUIRES_REVIEW',x['errors'])
    def test_base_drift(self):
        a=html(head='<base href="/preparedness/">');b=html(head='<base href="/">')
        self.assertIn('HTML_BASE_PARITY_DRIFT',r438.pair_review(a,b)['errors'])
    def test_base_multiple(self):
        x=r438.inspect(html(head='<base href="/"><base target="_blank">'))
        self.assertIn('MULTIPLE_HTML_BASE_ELEMENTS',x['errors'])
    def test_css_generated_copy(self):
        x=r438.inspect(html(head='<style>.alert::after{content:"safe"}</style>'))
        self.assertIn('CSS_GENERATED_COPY_REQUIRES_REVIEW',x['errors'])
    def test_inline_hiding(self):
        x=r438.inspect(html(attrs='style="display:none"'))
        self.assertIn('INLINE_STYLE_MAY_HIDE_OR_REPLACE_SAFETY_COPY',x['errors'])
    def test_inline_style_drift(self):
        a=html(attrs='style="color:black"');b=html(attrs='style="color:red"')
        self.assertIn('ELEMENT_STYLE_PARITY_DRIFT',r438.pair_review(a,b)['errors'])
    def test_visibility_attribute_drift(self):
        a=html(extra='<p aria-expanded="false">Details</p>')
        b=html(extra='<p aria-expanded="true">Details</p>')
        self.assertIn('VISIBILITY_CONTROL_PARITY_DRIFT',r438.pair_review(a,b)['errors'])
    def test_style_media_drift(self):
        a=html(head='<style media="screen">p{color:blue}</style>')
        b=html(head='<style media="all">p{color:blue}</style>')
        self.assertIn('STYLE_ELEMENT_ATTRIBUTES_PARITY_DRIFT',r438.pair_review(a,b)['errors'])
    def test_duplicate_attr(self):
        x=r438.inspect(html(head='<link rel="stylesheet" href="/a" href="/b">'))
        self.assertIn('CSS_RELEVANT_DUPLICATE_HTML_ATTRIBUTE',x['errors'])
    def test_empty_href(self):
        x=r438.inspect(html(head='<link rel="stylesheet">'))
        self.assertIn('CSS_LINK_WITHOUT_HREF',x['errors'])
    def test_unsafe_css_link_scheme(self):
        x=r438.inspect(html(head='<link rel="stylesheet" href="javascript:alert(1)">'))
        self.assertIn('CSS_LINK_UNSAFE_SCHEME_OR_ESCAPE',x['errors'])
    def test_malformed_utf8(self):
        with self.assertRaises(UnicodeError):r438.inspect(b'<html>\xff</html>')
    def test_reject_nul(self):
        with self.assertRaises(ValueError):r438.inspect(b'<html>\0</html>')
    def test_reject_str(self):
        with self.assertRaises(ValueError):r438.inspect('<html>abc</html>')
    def test_reject_short(self):
        with self.assertRaises(ValueError):r438.inspect(b'hello')
    def test_reject_large(self):
        with self.assertRaises(ValueError):r438.inspect(b'X'*(r438.MAX_BYTES+1))
    def test_css_large(self):
        with self.assertRaises(ValueError):r438.analyze_css('a'*(r438.CSS_LIMIT+1))
    def test_source_determinism(self):
        x=html(head='<style>.x{ color:black; }</style>')
        self.assertEqual(r438.inspect(x),r438.inspect(x))
    def test_two_export_order_preserved(self):
        a=html(head='<style>p{color:red}</style><style>h2{color:blue}</style>')
        b=html(head='<style>h2{color:blue}</style><style>p{color:red}</style>')
        self.assertIn('INLINE_STYLESHEET_PARITY_DRIFT',r438.pair_review(a,b)['errors'])
    def test_unbalanced_css_comment(self):
        self.assertIn('CSS_UNBALANCED_COMMENT_REQUIRES_REVIEW',r438.analyze_css('p{/*broken')['errors'])
    def test_bidi(self):
        self.assertIn('CSS_BIDI_OR_ZERO_WIDTH_CHARACTERS',r438.analyze_css('p{content:"\u202eevacuate"}')['errors'])
    def test_escaped_import(self):
        self.assertIn('CSS_ESCAPED_TOKEN_REQUIRES_BROWSER_REVIEW',r438.analyze_css('@\\69mport "mystery.css"')['errors'])
    def test_missing_parent_fails_closed(self):
        with patch.object(r438,'load_parent',side_effect=ValueError('blocked')):
            self.assertIn('PARENT_R437_AUDIT_UNAVAILABLE',r438.audit({}, {}, {})['errors'])
    def test_missing_manifest_fails_closed(self):
        with patch.object(r438,'load_parent') as p:
            p.return_value.audit.return_value={'errors':[]}
            self.assertIn('AUTHENTIC_MANIFEST_OR_EXPORTS_MISSING',r438.audit(None,{},{} )['errors'])
    def test_duplicate_slug(self):
        with patch.object(r438,'load_parent') as p:
            p.return_value.audit.return_value={'errors':[]}
            out=r438.audit({'articles':[{'slug':'abc'},{'slug':'abc'}]},{'abc':(html(),html())},{},test_only=True)
        self.assertIn('DUPLICATE_OR_INVALID_ARTICLE_IDENTITY',out['errors'])
    def test_surplus_exports(self):
        with patch.object(r438,'load_parent') as p:
            p.return_value.audit.return_value={'errors':[]}
            out=r438.audit({'articles':[{'slug':'abc'}]},{'abc':(html(),html()),'extra':(html(),html())},{},test_only=True)
        self.assertIn('EXTRA_OR_MISSING_EXPORT_IDENTITY',out['errors'])
    def test_missing_export_pair(self):
        with patch.object(r438,'load_parent') as p:
            p.return_value.audit.return_value={'errors':[]}
            out=r438.audit({'articles':[{'slug':'abc'}]},{},{},test_only=True)
        self.assertIn('MISSING_EXPORT_PAIR:abc',out['errors'])
    def test_exact_35_review_only(self):
        out=r438.hold([],{},{'slug':'fake'} if False else [])
        for key in ('eligible','publication_approved','paid_offer_approved','qualified_safety_approved'):
            self.assertFalse(out[key])
        self.assertIsNone(out['merchant_confirmed_orders'])
        self.assertIsNone(out['net_revenue_per_1000_qualified_human_sessions'])
    def test_cli_missing_proof_exit2(self):
        p=subprocess.run([sys.executable,'-I',str(SRC),'/missing/manifest','/missing/lock','/missing/exports'],capture_output=True,text=True,timeout=6)
        self.assertEqual(p.returncode,2);self.assertIn('DRAFT_HARD_HOLD',p.stdout)
    def test_no_network_write_helpers(self):
        source=SRC.read_text()
        for forbidden in ('urllib.request','requests.get(', 'requests.post(', 'wordpress_xmlrpc','selenium.', 'subprocess.run(', 'httpx.', 'open("w"'):
            self.assertNotIn(forbidden,source)

IMPORTS={
 'quoted':'@import "theme.css";',
 'single_quoted':"@import 'theme.css' print;",
 'url_quoted':'@import url("theme.css") screen;',
 'url_unquoted':'@import url(critical.css);',
 'nested':'@layer reset {@import url(extra.css);}',
 'layered':'@import url(a.css) layer(utilities);',
 'case':'@IMPORT url(a.css);',
 'spaces':'@ import "a.css";',
 'supports':'@import url(a.css) supports(display: grid);',
 'remote':'@import url(https://cdn.example.com/theme.css);',
}
HIDERS={
 'display_none':'.warning{display:none}',
 'visibility_hidden':'#alert{visibility:hidden}',
 'visibility_collapse':'.warning{visibility:collapse}',
 'opacity_zero':'.warning{opacity:0}',
 'font_size_zero':'.warning{font-size:0}',
 'clip_path':'.warning{clip-path:inset(100%)}',
 'clip_rect':'.warning{clip:rect(0,0,0,0)}',
 'under_media':'@media screen {.warning{display:none}}',
 'under_supports':'@supports (display:flex){.warning{visibility:hidden}}',
 'force_important':'.warning{display:none!important}',
}
LINKS={
 'print':'<link rel="stylesheet" media="print" href="/print.css">',
 'all':'<link rel="stylesheet" media="all" href="/print.css">',
 'screen':'<link rel="stylesheet" media="screen" href="/print.css">',
 'no_media':'<link rel="stylesheet" href="/print.css">',
 'alternate':'<link rel="alternate stylesheet" href="/print.css">',
 'uppercase':'<link rel="STYLEsheet" href="/print.css">',
 'preload':'<link rel="preload" as="style" href="/print.css">',
 'modulepreload':'<link rel="modulepreload" href="/print.css">',
}

def generate_css_case(source,code):
    def check(self):
        self.assertIn(code,r438.inspect(html(head='<style>'+source+'</style>'))['errors'])
    return check
for name,css in IMPORTS.items():setattr(Contract,'test_import_'+name,generate_css_case(css,'CSS_IMPORT_DEPENDENCY_UNAUTHENTICATED'))
for name,css in HIDERS.items():setattr(Contract,'test_hide_'+name,generate_css_case(css,'CSS_POSSIBLE_SAFETY_COPY_CONCEALMENT'))
for name,tag in LINKS.items():
    def f(self,tag=tag):
        self.assertIn('EXTERNAL_CSS_BYTES_UNVERIFIED',r438.inspect(html(head=tag))['errors'])
    setattr(Contract,'test_link_'+name,f)

if __name__=='__main__':unittest.main()
