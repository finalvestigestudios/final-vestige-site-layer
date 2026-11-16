"""R407 isolated adversarial fixtures. These DO NOT review actual E399 artifacts."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

path = Path(__file__).resolve().parents[1] / "tools" / "r407_printable_citation_privacy_gate.py"
spec = importlib.util.spec_from_file_location("r407", path)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
A = "https://www.fda.gov/food/buy-store-serve-safe-food/food-recalls-what-you-need-know"
B = "https://www.cdc.gov/foodborne-outbreaks/what-to-do/index.html"
ARTICLE = ('<html><body><main><p>Review <a href="' + A + '">FDA</a></p>'
           '<p>Recall absence is not a safety guarantee.</p></main></body></html>').encode()
BASE = ('<html><head><style>@media print {p {margin:0}}</style></head>'
        '<body><main><h1>Commercial Package Record</h1><p>Keep label details.</p>'
        '<p><a href="' + A + '">FDA recall information</a></p></main></body></html>').encode()
def run(printable=BASE, article=ARTICLE, allowed=None):
    return r.audit(article, printable, {A,B} if allowed is None else allowed,
        article_pin=hashlib.sha256(article).hexdigest() if isinstance(article,bytes) else "0"*64,
        print_pin=hashlib.sha256(printable).hexdigest() if isinstance(printable,bytes) else "0"*64)

class TestR407(unittest.TestCase):
    def test_pass_still_release_hold(self):
        x=run();self.assertEqual(x["integrity"],"PASS");self.assertFalse(x["eligible"])
        self.assertFalse(x["publication_approved"]);self.assertEqual(x["release"],r.HOLD)
    def test_sources(self): self.assertEqual(run()["printed_source_urls"],[A])
    def test_print_words(self): self.assertGreater(run()["print_word_count"],5)
    def test_cannot_claim_food_approval(self): self.assertEqual(run()["qualified_food_safety"],"NOT_GRANTED")
    def test_cannot_claim_privacy_approval(self): self.assertEqual(run()["qualified_child_privacy"],"NOT_GRANTED")
    def test_bad_article_pin(self):
        x=r.audit(ARTICLE,BASE,{A},article_pin="0"*64,print_pin=r.sha(BASE))
        self.assertIn("article_original_hash_mismatch",x["failures"])
    def test_bad_print_pin(self):
        x=r.audit(ARTICLE,BASE,{A},article_pin=r.sha(ARTICLE),print_pin="0"*64)
        self.assertIn("print_original_hash_mismatch",x["failures"])
    def test_missing_print(self):self.assertIn("missing_or_oversized_print",run(printable=b"")["failures"])
    def test_missing_article(self):self.assertIn("missing_or_oversized_article",run(article=b"")["failures"])
    def test_wrong_source_inventory(self):self.assertIn("untrusted_article_source_inventory",run(allowed=[A])["failures"])
    def test_unknown_print_link(self):
        altered=BASE.replace(A.encode(),b"https://www.cdc.gov/new")
        self.assertIn("printed_link_without_visible_article_citation",run(printable=altered)["failures"])
    def test_local_anchor(self):
        altered=BASE.replace(b"<main>",b'<main><p id="anchor">Text</p><p><a href="#anchor">Read above</a></p>')
        self.assertEqual(run(printable=altered)["integrity"],"PASS")
    def test_missing_local_anchor(self):
        altered=BASE.replace(b"<main>",b'<main><p><a href="#absent">Read above</a></p>')
        self.assertIn("print:broken_local_link",run(printable=altered)["failures"])
    def test_unclosed_markup(self):
        x=run(printable=b"<html><p>Unclosed")
        self.assertIn("print:unclosed_markup",x["failures"])
    def test_duplicate_attribute(self):
        x=run(printable=BASE.replace(b"<main>",b'<main><p id="a" id="b">Hello</p>'))
        self.assertIn("print:duplicate_attribute",x["failures"])
    def test_duplicate_id(self):
        x=run(printable=BASE.replace(b"<main>",b'<main><p id="a">A</p><p id="a">B</p>'))
        self.assertIn("print:duplicate_id",x["failures"])
    def test_invalid_utf8(self):self.assertIn("unparseable_print",run(printable=b"\xff")["failures"])
    def test_regular_bounded_file(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"file";f.write_bytes(BASE)
            self.assertEqual(r.read_original(f),BASE)
    def test_missing_bounded_file(self):self.assertIsNone(r.read_original(Path("/not/a/real/path")))
    def test_cli_always_hold(self):self.assertEqual(r.main([]),2)

# One independent case per forbidden component, event handler, link scheme and CSS network construct.
BAD_TAGS=["script","iframe","form","input","button","select","textarea","object","embed",
          "video","audio","canvas","svg","math","link","base","noscript","template",
          "details","summary","dialog","picture","source","img","frame","frameset","applet"]
BAD_ATTR=["onclick","onload","onerror","onmouseover","onchange","onfocus","oninput",
          "onkeydown","src","srcset","formaction","action","poster","background",
          "data","hrefdoc","http-equiv","xlink:href"]
BAD_URL=["javascript:alert(1)","data:text/html,x","mailto:someone@example.org",
         "tel:911","http://www.fda.gov/x","https://www.cdc.gov/x?utm_content=y",
         "https://www.fda.gov/x?fbclid=z","https://www.fda.gov:8443/x",
         "https://user@www.fda.gov/x","https://store.example.org/pay"]
BAD_CSS=["@import url(https://example.org/x)","@font-face{font-family:z}",
         "background:url(https://example.org/x)","width:expression(alert(1))",
         "background:image-set(url(https://example.org/x))",
         "binding:url(x)","background:u\\72l(https://evil.test/x)",
         "@/**/import url(https://evil.test/x)"]

def scenario(payload,match):
    def test(self):
        x=run(printable=BASE.replace(b"<main>",b"<main>"+payload.encode()))
        self.assertTrue(any(match in f for f in x["failures"]),x["failures"])
    return test
for i,name in enumerate(BAD_TAGS):
    setattr(TestR407,f"test_forbidden_tag_{i:02d}_{name}",scenario(f"<{name}>unsafe</{name}>","unsafe_element"))
for i,name in enumerate(BAD_ATTR):
    setattr(TestR407,f"test_forbidden_attr_{i:02d}",scenario(f'<p {name}="bad">Unsafe</p>',"active_or_remote_attribute"))
for i,url in enumerate(BAD_URL):
    setattr(TestR407,f"test_forbidden_link_{i:02d}",scenario(f'<p><a href="{url}">bad</a></p>',"unsafe_tracking_or_commercial_link"))
for i,css in enumerate(BAD_CSS):
    setattr(TestR407,f"test_forbidden_css_{i:02d}",scenario(f"<style>{css}</style>","remote_or_executable_css"))
