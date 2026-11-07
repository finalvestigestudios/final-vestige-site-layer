"""R192 fail-closed regression: duplicated HTML attributes and comment-obfuscated CSS.
SYNTHETIC FIXTURES ONLY; never browser privacy, merchant, or QD clearance.
"""
from __future__ import annotations
from pathlib import Path
import importlib.util
import tempfile
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/'tools/r191_static_resource_offer_gate.py'
spec=importlib.util.spec_from_file_location('r191_patched',SCRIPT)
g=importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
CSS_BAD=["@/**/import url(https://evil.test/x)","@im/**/port url(https://evil.test/x)","@imp/**/ort url(https://evil.test/x)","@import/**/url(https://evil.test/x)","@/*ordinary*/import \"https://evil.test/x\"","@/**/font-face{src:url(#abc)}","@fo/**/nt-face{src:url(#abc)}","@/**/namespace svg \"https://evil.test\"",".x{background:u/**/rl(https://evil.test/x)}",".x{background:ur/**/l(https://evil.test/x)}",".x{background:url/**/(https://evil.test/x)}",".x{background:u/**/r/**/l/**/(https://evil.test/x)}",".x{background:url(/*x*/https://evil.test/x)}",".x{background:url(https://evil.test/x/*x*/)}",".x{background:url(/*x*/data:image/png;base64,a)}",".x{background:url(/*x*/../secret.png)}",".x{background:url(/**/)}",".x{background:image/**/-set(url(#x) 1x)}",".x{filter:ex/**/pression(alert(1))}",".x{behavior/**/:url(#local)}",".x{-moz/**/-binding:url(#local)}",".x{background:cross/**/-fade(url(#x),url(#y),.5)}",".x{background:el/**/ement(#foo)}",".x{background:url(https://evil.test/x)",".x{background:/**/url(https://evil.test/x)",".x{background:/*unterminated",".x{background:*/none}",".x{background:/*multi\nline*/url(https://evil.test/x)}","@im/*many\nline*/port \"other.css\"",".x{background:u/**/rl(http://evil.test/x)}",".x{background:u/**/rl(//evil.test/x)}"]
CSS_OK=[".x{color:black}","/* comment */.x{color:inherit}",".x{color:red/*x*/}",".x{fill:url(#fw-pat)}","/*before*/.x{fill:url(#fw-pat)}/*after*/",".x{fill:url/**/(#fw-pat)}","/*safe*/.x{background:url(#local)}",".x::after{content:\"/* not comment */\"}",".x::after{content:\"*/\"}",".x::after{content:'/*'}",".x{--x:\"/* inside a literal */\"}",".x{display:grid}/* some\ntext */"]
DUPLICATES=["<div style=\"background:url(https://evil.test/a)\" style=\"\">hi</div>","<div style=\"\" style=\"background:url(https://evil.test/a)\">hi</div>","<svg><rect fill=\"url(https://evil.test/a)\" fill=\"red\"/></svg>","<svg><rect fill=\"red\" fill=\"url(https://evil.test/a)\"/></svg>","<svg><rect stroke=\"url(https://evil.test/a)\" stroke=\"none\"/></svg>","<svg><rect mask=\"url(https://evil.test/a)\" mask=\"none\"/></svg>","<svg><rect filter=\"url(https://evil.test/a)\" filter=\"none\"/></svg>","<svg><rect clip-path=\"url(https://evil.test/a)\" clip-path=\"none\"/></svg>","<p class=\"a\" class=\"b\">Hi</p>","<p id=\"a\" id=\"b\">Hi</p>","<p role=\"text\" role=\"presentation\">Hi</p>","<input type=\"text\" type=\"hidden\">","<button onclick=\"window.print()\" onclick=\"alert(1)\">Print</button>","<img src=\"https://evil.test/a\" src=\"\">","<img src=\"\" src=\"https://evil.test/a\">","<script type=\"application/ld+json\" type=\"text/plain\">{\"@type\":\"Product\"}</script>","<link rel=\"canonical\" rel=\"alternate\">","<form action=\"\" action=\"https://evil.test\">x</form>","<svg><use href=\"#local\" href=\"https://evil.test/x\"/></svg>","<div STYLE=\"bad\" style=\"\"></div>"]
HTML_OK=["<svg><rect fill=\"url(#fw-pat)\"/></svg>","<div style=\"background:url(#local)\">A</div>","<div style=\"color:red\">A</div>","<div aria-label=\"hello\" id=\"x\">A</div>","<style>.x{fill:url(#local)}</style>","<style>/* local comment */.x{fill:url(#local)}</style>","<script type=\"application/ld+json\">{\"@type\":\"Article\"}</script>","<svg><use href=\"#local\"/></svg>"]

class CSSCases(unittest.TestCase):pass
class HTMLCases(unittest.TestCase):pass
for i,value in enumerate(CSS_BAD):
    def f(self,value=value):self.assertTrue(g.css_errors(value),value)
    setattr(CSSCases,f'test_reject_comment_bypass_{i:02}',f)
for i,value in enumerate(CSS_OK):
    def f(self,value=value):self.assertEqual(g.css_errors(value),[],value)
    setattr(CSSCases,f'test_preserve_local_css_{i:02}',f)
for i,value in enumerate(DUPLICATES):
    def f(self,value=value):self.assertTrue(g.scan(value),value)
    setattr(HTMLCases,f'test_reject_duplicate_attribute_{i:02}',f)
for i,value in enumerate(HTML_OK):
    def f(self,value=value):self.assertEqual(g.scan(value),[],value)
    setattr(HTMLCases,f'test_preserve_local_html_{i:02}',f)

class CorpusGate(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.p=Path(t.name)/'preparedness'
        (self.p/'content/tools').mkdir(parents=True)
        (self.p/'build/wp').mkdir(parents=True)
        for slug in g.TOOLS:
            (self.p/'content/tools'/f'{slug}.body.html').write_text('<h2>Unpublished tool</h2><style>.x{fill:url(#local)}</style>')
            (self.p/'build/wp'/f'{slug}.html').write_text('<!-- wp:html -->\n<h2>Unpublished draft</h2>\n<!-- /wp:html -->')

    def test_synthetic_success_still_hard_hold(self):
        x=g.check(self.p)
        self.assertEqual((x['state'],x['authored_checked'],x['wp_exports_checked']),(g.HOLD,6,6))
        self.assertFalse(x['publication_authorized'])
        self.assertFalse(x['merchant_offer_verified'])
        self.assertFalse(x['independent_qd_pass'])
        self.assertFalse(x['privacy_browser_qa_complete'])

    def test_source_only_invalid(self):self.assertEqual(g.check(self.p,exports=False)['state'],g.INVALID)

for i,slug in enumerate(g.TOOLS):
    def source_case(self,slug=slug):
        p=self.p/'content/tools'/f'{slug}.body.html'
        p.write_text('<div style="background:url(https://evil.test/x)" style="">x</div>')
        self.assertEqual(g.check(self.p)['state'],g.INVALID)
    setattr(CorpusGate,f'test_source_duplicate_{i:02}',source_case)
    def export_case(self,slug=slug):
        p=self.p/'build/wp'/f'{slug}.html'
        p.write_text('<!-- wp:html -->\n<style>@im/**/port "https://evil.test/x";</style>\n<!-- /wp:html -->')
        self.assertEqual(g.check(self.p)['state'],g.INVALID)
    setattr(CorpusGate,f'test_export_css_comment_{i:02}',export_case)

if __name__=='__main__':unittest.main()
