"""Source-only contract tests, no public requests or subscriber actions."""
import unittest
from candidate import OLD_CHECK, NEW_CHECK, OLD_OBSERVER, NEW_OBSERVER, patch_document, candidate_grade

CODE = ("(function(){var g=document.getElementById('fvf-gift');"
        "var q=new URLSearchParams(location.search).get('subscribe');"
        "if(q){g.hidden=false;}" + OLD_CHECK + OLD_OBSERVER + "})();")
HTML = '<html><script>other()</script><script>' + CODE + '</script></html>'

def ok():
    return [dict(width=w, http=200, host="finalvestige.com", path="/focus/",
                 blocks=1, links=5, target=True, syntax="PASS", overflow=False,
                 initially_hidden=True, visible_after_mock_class=True,
                 patch_replacements=2, source_sha256="abc", candidate_sha256="def",
                 browser_syntax_errors=[]) for w in (390, 1440)]

class Contract(unittest.TestCase):
    def test_exact_two_replacements(self):
        page, info = patch_document(HTML)
        self.assertEqual(info["replacements"], 2)
        self.assertIn(NEW_CHECK, page)
        self.assertIn(NEW_OBSERVER, page)
        self.assertNotIn(OLD_CHECK, page)
        self.assertNotIn(OLD_OBSERVER, page)
        self.assertIn("<script>other()</script>", page)
    def test_refuse_missing_html(self):
        with self.assertRaises(ValueError): patch_document("<html/>")
    def test_refuse_missing_target(self):
        with self.assertRaises(ValueError): patch_document("<html><script>other()</script></html>")
    def test_refuse_duplicate_target(self):
        with self.assertRaises(ValueError):
            patch_document("<html><script>"+CODE+"</script><script>"+CODE+"</script></html>")
    def test_refuse_one_changed_expression(self):
        with self.assertRaises(ValueError):
            patch_document(HTML.replace(OLD_CHECK, NEW_CHECK))
    def test_refuse_old_script_fixed_in_production(self):
        with self.assertRaises(ValueError):
            patch_document(HTML.replace(OLD_OBSERVER, NEW_OBSERVER))
    def test_refuse_encoded_entity_leftover(self):
        with self.assertRaises(ValueError):
            patch_document(HTML.replace("})();", "if(x&#038;y){show();}})();"))
    def test_complete_matrix_passes(self):
        self.assertEqual(candidate_grade(ok()), [])
    def test_no_missing_viewport(self):
        self.assertIn("candidate_matrix_incomplete", candidate_grade(ok()[:1]))
    def test_missing_form_fails(self):
        rows=ok(); rows[0]["blocks"]=0; self.assertTrue(candidate_grade(rows))
    def test_duplicate_form_fails(self):
        rows=ok(); rows[0]["blocks"]=2; self.assertTrue(candidate_grade(rows))
    def test_damaged_anchor_fails(self):
        rows=ok(); rows[0]["target"]=False; self.assertTrue(candidate_grade(rows))
    def test_non_200_fails(self):
        rows=ok(); rows[0]["http"]=404; self.assertTrue(candidate_grade(rows))
    def test_wrong_host_fails(self):
        rows=ok(); rows[0]["host"]="other.test"; self.assertTrue(candidate_grade(rows))
    def test_candidate_syntax_fails(self):
        rows=ok(); rows[0]["syntax"]="FAIL:SyntaxError"; self.assertTrue(candidate_grade(rows))
    def test_browser_error_fails(self):
        rows=ok(); rows[0]["browser_syntax_errors"]=["SyntaxError"]; self.assertTrue(candidate_grade(rows))
    def test_gift_hidden_after_class_fails(self):
        rows=ok(); rows[0]["visible_after_mock_class"]=False; self.assertTrue(candidate_grade(rows))
    def test_premature_gift_visible_fails(self):
        rows=ok(); rows[0]["initially_hidden"]=False; self.assertTrue(candidate_grade(rows))
    def test_missing_provenance_fails(self):
        rows=ok(); rows[0]["source_sha256"]=""; self.assertTrue(candidate_grade(rows))
    def test_horizontal_overflow_fails(self):
        rows=ok(); rows[0]["overflow"]=True; self.assertTrue(candidate_grade(rows))

if __name__ == "__main__":
    unittest.main()
