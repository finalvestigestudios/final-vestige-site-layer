"""Synthetic and provider-excerpt regression tests; no HTTP, WordPress writes or email."""
import unittest
from provider_surface_guard import inspect

def wrap(x):return '<section><div class="wp-block-jetpack-subscriptions">'+x+'</div></section>'

DISPATCH=wrap('<p><a href="https://finalvestige.com/?post_type=page&#038;p=523">Subscribe</a></p>')
FOCUS=wrap('<p><a href="https://finalvestige.com/?post_type=page&#038;p=1579">Send me the fieldbook</a></p>')
FORM=wrap('<form><label for="e">Email</label><input id="e" type="email"><button type="submit">Subscribe</button></form>')

class WordPressReadOnlyContract(unittest.TestCase):
 def test_dispatch_real_provider_excerpt(self):
  r=inspect(DISPATCH,523);self.assertEqual(r['status'],'SAME_PAGE_LINK_ONLY_REQUIRES_BROWSER_VERIFICATION');self.assertEqual(r['blocks'],1)
 def test_focus_real_provider_excerpt(self):self.assertEqual(inspect(FOCUS,1579)['status'],'SAME_PAGE_LINK_ONLY_REQUIRES_BROWSER_VERIFICATION')
 def test_wrong_page_id_is_not_proof(self):self.assertIn('UNKNOWN',inspect(DISPATCH,1579)['status'])
 def test_not_forms_in_css(self):
  r=inspect('<style>input[type=email]{color:red} form{display:block}</style>'+DISPATCH,523);self.assertEqual(r['details'][0]['email_inputs'],0)
 def test_markup_outside_block_does_not_count(self):self.assertEqual(inspect('<form><input type="email"><button>Yes</button></form>'+DISPATCH,523)['details'][0]['forms'],0)
 def test_real_form_is_not_confirmed_signup(self):
  r=inspect(FORM,523);self.assertIn('HTML_FORM_PRESENT',r['status']);self.assertIsNone(r['confirmed_signup'])
 def test_all_signups_unverified_even_with_form(self):
  r=inspect(FORM,523);self.assertIsNone(r['deliverable_recipient_count']);self.assertFalse(r['test_send_authorized'])
 def test_input_without_form_is_unknown(self):self.assertIn('UNKNOWN',inspect(wrap('<input type="email">'),523)['status'])
 def test_form_missing_submit_is_unknown(self):self.assertIn('UNKNOWN',inspect(wrap('<form><input type="email"></form>'),523)['status'])
 def test_disabled_form_never_passes(self):self.assertIn('DISABLED_INPUT',inspect(wrap('<form><input type="email" disabled><button>Go</button></form>'),523)['status'])
 def test_empty_string(self):self.assertEqual(inspect('',523)['status'],'NO_EVIDENCE')
 def test_missing_block(self):self.assertEqual(inspect('<input type="email">',523)['status'],'NO_SUBSCRIBE_BLOCK_IN_CAPTURE')
 def test_unknown_origin_is_not_fv_self_link(self):self.assertIn('UNKNOWN',inspect(wrap('<a href="https://evil.test/?post_type=page&amp;p=523">Subscribe</a>'),523)['status'])
 def test_non_page_query_is_not_same_page(self):self.assertIn('UNKNOWN',inspect(wrap('<a href="https://finalvestige.com/?p=523">Subscribe</a>'),523)['status'])
 def test_encoded_ampersand_is_decoded(self):self.assertEqual(inspect(DISPATCH,523)['details'][0]['self_links'][0],'https://finalvestige.com/?post_type=page&p=523')
 def test_two_blocks_are_reported_separately(self):self.assertEqual(inspect(DISPATCH+FORM,523)['blocks'],2)
 def test_scripted_future_hydration_is_not_assumed(self):
  self.assertIn('SAME_PAGE_LINK_ONLY',inspect(DISPATCH+'<script>hydrate()</script>',523)['status'])
 def test_untrusted_css_label_no_effect(self):self.assertEqual(inspect(wrap('<span style="content:\'input type=email\'">No form</span>'),523)['details'][0]['email_inputs'],0)
 def test_no_false_commercial_permission(self):
  r=inspect(FOCUS,1579);self.assertFalse(r['test_send_authorized'])

if __name__=='__main__':unittest.main()
