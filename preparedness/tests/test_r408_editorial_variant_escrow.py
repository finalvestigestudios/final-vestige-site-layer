"""R408 fail-closed *synthetic* regression suite, not E399/E400 safety approval."""
from __future__ import annotations
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
import os

TOOL = Path(__file__).resolve().parents[1] / "tools" / "r408_editorial_variant_escrow.py"
spec = importlib.util.spec_from_file_location("r408_exact", TOOL)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
N = "https://nchfp.uga.edu/how/dry/recipes/jerky/"
C = "https://www.cdc.gov/trichinellosis/prevention/index.html"
F = "https://www.foodsafety.gov/recalls-and-outbreaks"

def html(text, extra=""):
    return f'<h2 id="source">Sources</h2><p>{text}</p><a href="{N}">NCHFP</a>{extra}'.encode()

class Custody(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.a, self.b = (Path(self.t.name)/n for n in ("e399.html","e400.html"))
        self.a.write_bytes(html("Evidence and background"))
        self.b.write_bytes(html("Shorter reader-facing background"))
    def audit(self, a=None, b=None):
        if a is not None: self.a.write_bytes(a)
        if b is not None: self.b.write_bytes(b)
        pins = tuple(hashlib.sha256(p.read_bytes()).hexdigest() for p in (self.a,self.b))
        return g.audit(self.a,self.b,pins=pins)
    def test_valid_fixture_always_hard_hold(self):
        r=self.audit()
        self.assertTrue(r["integrity_ok"])
        self.assertFalse(r["eligible"])
        self.assertFalse(r["publication_approved"])
        self.assertEqual(r["decision"],"DRAFT_HARD_HOLD")
        self.assertEqual(r["qualified_food_safety"],"NOT_GRANTED")
        self.assertEqual(r["qualified_privacy"],"NOT_GRANTED")
    def test_real_reported_pins_do_not_match_synthetic(self):
        self.assertFalse(g.audit(self.a,self.b)["integrity_ok"])
    def test_sha_mismatch(self):
        self.assertIn("SHA256 mismatch", str(g.audit(self.a,self.b)["errors"]))
    def test_same_bytes_different_names(self):
        self.assertFalse(self.audit(b=html("Evidence and background"))["integrity_ok"])
    def test_missing_artifact(self):
        self.b.unlink()
        self.assertFalse(g.audit(self.a,self.b)["integrity_ok"])
    def test_no_source_in_e400(self):
        self.assertFalse(self.audit(b=b"<h2>Uncited</h2>")["integrity_ok"])
    def test_source_removed(self):
        original=html("old",f'<a href="{C}">CDC</a>')
        result=self.audit(a=original,b=html("new"))
        self.assertEqual(result["comparison"]["removed_source_urls"],[C])
        self.assertFalse(result["integrity_ok"])
    def test_new_source_requires_adjudication(self):
        result=self.audit(b=html("new",f'<a href="{F}">FoodSafety</a>'))
        self.assertTrue(result["review_warnings"])
        self.assertFalse(result["publication_approved"])
    def test_citation_repetition_visible(self):
        result=self.audit(b=html("new",f'<a href="{N}">Again</a>'))
        self.assertEqual(result["comparison"]["duplicate_source_urls_E400"],[N])
    def test_reduced_reading_depth_never_means_safe(self):
        result=self.audit(a=html("long "*100),b=html("short"))
        self.assertTrue(any("reading depth" in x for x in result["review_warnings"]))
        self.assertFalse(result["publication_approved"])
    def test_headings_delta_requires_review(self):
        result=self.audit(b=html("Changed").replace(b"Sources",b"Different"))
        self.assertTrue(any("headings changed" in x for x in result["review_warnings"]))
    def test_non_utf8_rejected(self):
        self.assertFalse(self.audit(b=html("read")+b"\\xff")["integrity_ok"])
    def test_symlink_rejected(self):
        target=Path(self.t.name)/"target"
        self.b.rename(target)
        self.b.symlink_to(target)
        self.assertFalse(g.audit(self.a,self.b)["integrity_ok"])
    def test_hardlink_rejected(self):
        os.link(self.b,Path(self.t.name)/"alias")
        self.assertFalse(g.audit(self.a,self.b)["integrity_ok"])
    def test_directory_rejected(self):
        self.b.unlink();self.b.mkdir()
        self.assertFalse(g.audit(self.a,self.b)["integrity_ok"])
    def test_oversize_rejected(self):
        self.b.write_bytes(b"x"*(g.LIMIT+1))
        self.assertFalse(g.audit(self.a,self.b)["integrity_ok"])
    def test_bad_pins_never_crash_or_pass(self):
        for pins in (None,(),("0"*64,),("x","y"),("A"*64,"a"*64),[1,2]):
            with self.subTest(pins=pins):
                self.assertFalse(g.audit(self.a,self.b,pins=pins)["integrity_ok"])
    def test_original_hashes_are_expected(self):
        self.assertEqual(len(g.E399_SHA),64)
        self.assertEqual(len(g.E400_SHA),64)
        self.assertNotEqual(g.E399_SHA,g.E400_SHA)

_BAD_URLS = [
    "http://nchfp.uga.edu/a", "//nchfp.uga.edu/a", "https://evil.com/a",
    "https://nchfp.uga.edu.evil.com/a", "https://nchfp.uga.edu:8080/a",
    "https://user:pass@nchfp.uga.edu/a", "https://www.cdc.gov/a#wrong",
    "https://www.cdc.gov/a?utm_campaign=test", "https://www.cdc.gov/a?fbclid=a",
    "https://www.cdc.gov/a?token=secret", "https://www.cdc.gov/a?email=user",
    "https://www.cdc.gov/a?affiliate=1", "https://www.cdc.gov/a?gclid=a",
    "javascript:alert(1)", "mailto:a@b.com", "https://www.cdc.gov/a b",
    "https://www.cdc.gov:9000/a", "https://attacker.gov/fake",
]
_BAD_HTML = [
    "<script>alert(1)</script>", "<iframe></iframe>", "<form></form>",
    "<input>", "<button></button>", "<svg></svg>", "<canvas></canvas>",
    "<video></video>", "<audio></audio>", "<object></object>",
    "<embed>", "<meta>", "<link href=\"/x\">", "<template></template>",
    "<p onclick=\"bad()\">X</p>", "<img src=\"https://evil.com/pixel\">",
    "<p onerror=\"bad()\">X</p>", "<p style=\"background:url(//evil.com/x)\">X</p>",
    "<p style=\"@import url(x)\">X</p>",
    "<h2 id=\"source\">Duplicated id</h2>", "<p id=\"x\" id=\"y\">dup</p>",
]
def _bad_url_test(value):
    def test(self):
        self.assertIsNotNone(g.check_url(value))
        self.assertFalse(self.audit(b=html("a",f'<a href="{value}">Bad</a>'))["integrity_ok"])
    return test
def _bad_html_test(value):
    def test(self):
        self.assertFalse(self.audit(b=html("a",value))["integrity_ok"])
    return test
for i, value in enumerate(_BAD_URLS):
    setattr(Custody, f"test_invalid_url_{i:02d}", _bad_url_test(value))
for i, value in enumerate(_BAD_HTML):
    setattr(Custody, f"test_unsafe_markup_{i:02d}", _bad_html_test(value))

if __name__ == "__main__": unittest.main()
