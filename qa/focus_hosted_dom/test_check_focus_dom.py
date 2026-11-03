"""Strict fail-closed regression tests. No HTTP or subscriber operations."""
import unittest
from check_focus_dom import CASES, grade, safe_request

def good():
    return [dict(width=w, js=js, status=200, host="finalvestige.com",
                 path="/focus/", blocks=1, links=5, target=True,
                 script="PASS", pageerrors=[], overflow=False)
            for w, js in CASES]

class GateTests(unittest.TestCase):
    def test_complete_pass(self): self.assertEqual(grade(good()), [])
    def test_missing_case(self): self.assertIn("incomplete_matrix", grade(good()[:2]))
    def test_duplicate_case(self):
        a=good(); a[1]=dict(a[0]); self.assertIn("incomplete_matrix", grade(a))
    def test_wrong_host(self):
        a=good(); a[0]["host"]="other.invalid"; self.assertTrue(grade(a))
    def test_non_200(self):
        a=good(); a[0]["status"]=404; self.assertTrue(grade(a))
    def test_missing_block(self):
        a=good(); a[0]["blocks"]=0; self.assertTrue(grade(a))
    def test_double_block(self):
        a=good(); a[0]["blocks"]=2; self.assertTrue(grade(a))
    def test_nojs_fragment_broken(self):
        a=good(); a[1]["target"]=False
        self.assertTrue(any("broken_cta_fragment" in s for s in grade(a)))
    def test_script_syntax(self):
        a=good(); a[0]["script"]="FAIL:SyntaxError"; self.assertTrue(grade(a))
    def test_browser_error(self):
        a=good(); a[0]["pageerrors"]=["SyntaxError"]; self.assertTrue(grade(a))
    def test_overflow(self):
        a=good(); a[0]["overflow"]=True; self.assertTrue(grade(a))
    def test_no_cta(self):
        a=good(); a[0]["links"]=0; self.assertTrue(grade(a))
    def test_request_deny_post(self):
        class R: method="POST"; url="https://finalvestige.com/focus/"
        self.assertFalse(safe_request(R()))
    def test_request_deny_fake_signup(self):
        class R: method="GET"; url="https://finalvestige.com/focus/?subscribe=success"
        self.assertFalse(safe_request(R()))
    def test_request_deny_email_query(self):
        class R: method="GET"; url="https://finalvestige.com/focus/?email=test"
        self.assertFalse(safe_request(R()))
    def test_request_allows_css_get(self):
        class R: method="GET"; url="https://finalvestige.com/wp-content/style.css"
        self.assertTrue(safe_request(R()))
if __name__=="__main__": unittest.main()
