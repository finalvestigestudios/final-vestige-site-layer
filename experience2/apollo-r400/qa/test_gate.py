"""R400 adversarial read-only URL and source-contract tests; offline, deterministic."""
import unittest
from staging_browser_gate import safe_url,reviewed_css,permits,redact,CSS
ROOT="https://staging.finalvestige.example/apollo-1-evidence-atlas/"
class TestAdmission(unittest.TestCase):
    def test_canonical(self):
        self.assertTrue(safe_url(ROOT,True))
        self.assertTrue(permits(ROOT,"GET",ROOT))
        self.assertTrue(permits(ROOT,"HEAD",ROOT))
        self.assertFalse(permits(ROOT,"POST",ROOT))
        self.assertFalse(permits(ROOT,"DELETE",ROOT))
    def test_reject_landing(self):
        cases=[
          "http://staging.finalvestige.example/apollo-1-evidence-atlas/",
          "https://user:pass@staging.finalvestige.example/apollo-1-evidence-atlas/",
          "https://staging.finalvestige.example:443/apollo-1-evidence-atlas/",
          ROOT+"?utm_content=secret",ROOT+"#anchor",
          "https://staging.finalvestige.example/other/",
          "https://staging.finalvestige.example/x/../apollo-1-evidence-atlas/",
          "https://staging.finalvestige.example/x/%2e%2e/apollo-1-evidence-atlas/",
          "https://staging.finalvestige.example//apollo-1-evidence-atlas/",
          "https://localhost/apollo-1-evidence-atlas/",
          "https://xn--test.example/apollo-1-evidence-atlas/"
        ]
        for x in cases:
            with self.subTest(url=x):self.assertFalse(safe_url(x,True))
    def test_deny_cross_site_and_modifying_methods(self):
        for x in ["https://www.nasa.gov/history/","https://evil-staging.finalvestige.example/x",
                  "http://staging.finalvestige.example/x","https://finalvestige.example/x"]:
            self.assertFalse(permits(x,"GET",ROOT))
        for method in ["POST","PUT","PATCH","DELETE","CONNECT","OPTIONS"]:
            self.assertFalse(permits(ROOT,method,ROOT))
    def test_css_version_allowlist(self):
        for path,(ver,sha) in CSS.items():
            u="https://staging.finalvestige.example/wp-content/plugins/layer/experience2"+path+"?ver="+ver
            self.assertEqual(reviewed_css(u),path)
            self.assertTrue(permits(u,"GET",ROOT))
            self.assertEqual(len(sha),64)
            for bad in [u+"&x=1",u.replace("?ver="+ver,"?ver=wrong"),u.replace("https:","http:")]:
                self.assertIsNone(reviewed_css(bad))
                self.assertFalse(permits(bad,"GET",ROOT))
    def test_redacted_receipts(self):
        result=redact(ROOT+"?secret=abcdef#private")
        for word in ["secret","abcdef","private"]:self.assertNotIn(word,result)
if __name__=="__main__":unittest.main(verbosity=2)
