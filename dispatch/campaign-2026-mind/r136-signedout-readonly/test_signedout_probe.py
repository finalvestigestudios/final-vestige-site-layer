"""Native Python and offline Chromium regression. Never goes to a public URL."""
import unittest
from signedout_probe import permitted_get, classify, run_fixture, FIXTURES, PAGES

class PolicyTests(unittest.TestCase):
    def test_known_target(self): self.assertEqual(set(PAGES),{'dispatch','focus'})
    def test_known_host(self): self.assertTrue(permitted_get('https://finalvestige.com/focus/','GET'))
    def test_known_wp_cdn(self): self.assertTrue(permitted_get('https://s0.wp.com/wp-includes/script.js','GET'))
    def test_blocks_post(self): self.assertFalse(permitted_get('https://finalvestige.com/focus/','POST'))
    def test_blocks_delete(self): self.assertFalse(permitted_get('https://finalvestige.com/focus/','DELETE'))
    def test_blocks_get_to_unknown_domain(self): self.assertFalse(permitted_get('https://not-finalvestige.com/x','GET'))
    def test_blocks_lookalike(self): self.assertFalse(permitted_get('https://finalvestige.com.evil.example/x','GET'))
    def test_blocks_cleartext_http(self): self.assertFalse(permitted_get('http://finalvestige.com/dispatch/','GET'))
    def test_blocks_ftp(self): self.assertFalse(permitted_get('ftp://finalvestige.com/focus/','GET'))
    def test_blocks_empty(self): self.assertFalse(permitted_get('','GET'))
    def test_blocks_javascript(self): self.assertFalse(permitted_get('javascript:alert(1)','GET'))
    def test_blocks_non_method(self): self.assertFalse(permitted_get('https://finalvestige.com/focus/','PATCH'))

class BrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.byname={r['page']:r for r in run_fixture()['cases']}
    def test_six_fixtures_run(self): self.assertEqual(set(self.byname),set(FIXTURES))
    def test_visible_label(self): self.assertEqual(self.byname['visible_labeled']['status'],'VISIBLE_LABELED_FORM_NOT_SIGNUP_PROOF')
    def test_same_page_warns(self): self.assertEqual(self.byname['same_page_only']['status'],'SAME_PAGE_ANCHOR_ONLY_PENDING_NATIVE_VALIDATION')
    def test_safe_modal(self): self.assertEqual(self.byname['safe_modal']['status'],'VISIBLE_FORM_AFTER_SAFE_MODAL_ACTION_NOT_SIGNUP_PROOF')
    def test_modal_never_subscribes(self): self.assertIsNone(self.byname['safe_modal']['confirmed_signup'])
    def test_safe_noop_not_form(self): self.assertEqual(self.byname['no_op_button']['status'],'NO_VISIBLE_SIGNUP_FORM_VERIFIED')
    def test_no_block(self): self.assertEqual(self.byname['no_block']['status'],'NO_SUBSCRIBE_BLOCK_DETECTED')
    def test_hidden_is_not_visible(self): self.assertEqual(self.byname['hidden_email']['initial']['visible_email_inputs'],0)
    def test_hidden_no_verified_lead(self): self.assertIsNone(self.byname['hidden_email']['confirmed_signup'])
    def test_fixture_does_not_verify_email(self):
        for r in self.byname.values(): self.assertIsNone(r['email_delivered'])
    def test_no_submission_on_any_fixture(self):
        for r in self.byname.values(): self.assertEqual(r['initial']['form_submit_attempts'],0)
    def test_no_personal_data_fields(self):
        for r in self.byname.values():
            raw=str(r).lower()
            for token in ('email_address','subscriber_email','input_value','email@'): self.assertNotIn(token,raw)
    def test_classify_missing_not_success(self):
        self.assertEqual(classify({'block_count':1,'visible_email_inputs':0,'same_page_anchors':0}),'NO_VISIBLE_SIGNUP_FORM_VERIFIED')

if __name__=='__main__': unittest.main(verbosity=2)
