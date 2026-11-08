"""Pure and browser-backed regression checks for the non-submitting guest QA harness."""
import tempfile
import unittest
from pathlib import Path
from guest_browser_probe import classify, execute

class ClassificationTests(unittest.TestCase):
    def setUp(self):
        self.good={"forms":[{"visible":True,"email_visible":True,"email_enabled":True,"submit_visible":True,"submit_enabled":True}],"emails":[{"visible":True,"enabled":True}],"same_page_subscribe_links":0}
    def test_good_visible(self):self.assertEqual(classify(self.good),"VISIBLE_SUBSCRIPTION_FORM_NOT_SUBMITTED")
    def test_no_fake_confirmation(self):self.assertNotIn("CONFIRMED",classify(self.good))
    def test_missing_email(self):self.assertEqual(classify({"forms":[],"emails":[],"same_page_subscribe_links":1}),"SELF_LINK_WITHOUT_VISIBLE_EMAIL_INPUT")
    def test_no_link_no_email(self):self.assertEqual(classify({"forms":[],"emails":[],"same_page_subscribe_links":0}),"INDETERMINATE_NEEDS_MANUAL_BROWSER_REVIEW")
    def test_hidden_form(self):
        a={**self.good,"forms":[{**self.good["forms"][0],"visible":False}]};self.assertEqual(classify(a),"INDETERMINATE_NEEDS_MANUAL_BROWSER_REVIEW")
    def test_disabled_email(self):
        a={**self.good,"forms":[{**self.good["forms"][0],"email_enabled":False}]};self.assertEqual(classify(a),"INDETERMINATE_NEEDS_MANUAL_BROWSER_REVIEW")
    def test_disabled_submit(self):
        a={**self.good,"forms":[{**self.good["forms"][0],"submit_enabled":False}]};self.assertEqual(classify(a),"INDETERMINATE_NEEDS_MANUAL_BROWSER_REVIEW")
    def test_empty(self):self.assertEqual(classify({}),"INDETERMINATE_NEEDS_MANUAL_BROWSER_REVIEW")

class BrowserFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.out=Path(cls.temp.name)
        cls.report=execute("fixture",cls.out,"/usr/bin/chromium")
        cls.rows={(r['page'],r['viewport']):r for r in cls.report['results']}
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def test_sixteen_viewport_results(self):self.assertEqual(len(self.rows),16)
    def test_good_fixture_all_sizes(self):
        for w in (320,390,768,1440):self.assertEqual(self.rows['valid_form',f'{w}x{740 if w==320 else 844 if w==390 else 900}']['classification'],"VISIBLE_SUBSCRIPTION_FORM_NOT_SUBMITTED")
    def test_self_link_fixture_all_sizes(self):
        for w in (320,390,768,1440):self.assertEqual(self.rows['self_link',f'{w}x{740 if w==320 else 844 if w==390 else 900}']['classification'],"SELF_LINK_WITHOUT_VISIBLE_EMAIL_INPUT")
    def test_hidden_fixture_all_sizes(self):
        for w in (320,390,768,1440):self.assertEqual(self.rows['hidden_form',f'{w}x{740 if w==320 else 844 if w==390 else 900}']['classification'],"SELF_LINK_WITHOUT_VISIBLE_EMAIL_INPUT")
    def test_disabled_fixture(self):
        for w in (320,390,768,1440):self.assertEqual(self.rows['disabled_form',f'{w}x{740 if w==320 else 844 if w==390 else 900}']['classification'],"INDETERMINATE_NEEDS_MANUAL_BROWSER_REVIEW")
    def test_no_email_values_in_report(self):
        import json
        text=json.dumps(self.report)
        self.assertNotIn('someone@example.com',text)
        self.assertNotIn('cookies',text)
        self.assertNotIn('utm_',text)
    def test_no_submit_from_any_fixture(self):
        self.assertFalse(self.report['did_submit'])
        for r in self.rows.values(): self.assertFalse(r['submitted'])
    def test_screenshots_generated(self):
        for r in self.rows.values():self.assertTrue((self.out/r['screenshot']).exists())
    def test_no_revenue_claims(self):self.assertEqual(self.report['actual_subscriber_confirmation'],"UNVERIFIED")

if __name__=='__main__':unittest.main()
