import unittest
from focus_route_contract import examine

PAGE='''<div class="fv-focus"><h2 id="subscribe-blog"></h2>
<div class="wp-block-jetpack-subscriptions"><p><a href="https://finalvestige.com/?post_type=page&amp;p=1579" style="background-color: #113AF5; color: #FFFFFF">Send me the fieldbook</a></p></div>
<a href="#subscribe-blog">Free fieldbook</a></div>'''

class FocusPageContract(unittest.TestCase):
    def test_current_published_editor_html_fragment_requires_runtime_confirmation(self):
        r=examine(PAGE)
        self.assertEqual(r['status'],'HOLD_FOR_RUNTIME_CONFIRMATION')
        self.assertEqual(r['counts']['self_loop_fallbacks'],1)
        self.assertEqual(r['counts']['inline_blue_fallbacks'],1)
        self.assertIn('NO_NATIVE_SUBSCRIBE_FORM_IN_EXPORTED_MARKUP',r['flags'])
    def test_script_text_is_not_a_real_email_field(self):
        r=examine(PAGE+'<script>var fake=`<form><input type="email"><button type="submit">`;</script>')
        self.assertEqual(r['counts']['forms'],0)
        self.assertEqual(r['counts']['email_inputs'],0)
    def test_real_form_cannot_be_mistaken_for_confirmed_subscriber(self):
        html='''<h2 id="subscribe-blog"></h2><div class="wp-block-jetpack-subscriptions">
        <form><label>Email<input type="email" required></label><button type="submit">Subscribe</button></form></div>'''
        r=examine(html)
        self.assertEqual(r['status'],'STATIC_MARKUP_PRESENT_RUNTIME_UNVERIFIED')
        self.assertIn('confirmed subscriber',r['cannot_infer'])
        self.assertEqual(r['counts']['forms'],1)
    def test_missing_target_is_release_hold(self):
        self.assertIn('FOCUS_JUMP_TARGET_MISSING',examine(PAGE.replace('id="subscribe-blog"',''))['flags'])
    def test_fake_submit_button_without_form_does_not_pass(self):
        self.assertIn('NO_NATIVE_SUBSCRIBE_FORM_IN_EXPORTED_MARKUP',examine(PAGE+'<button type="submit">Go</button>')['flags'])
    def test_hash_reference_does_not_count_as_form(self):
        self.assertIn('NO_NATIVE_SUBSCRIBE_FORM_IN_EXPORTED_MARKUP',examine('<div class="wp-block-jetpack-subscriptions"><a href="#subscribe-blog">Join</a></div><div id="subscribe-blog"></div>')['flags'])

if __name__=='__main__':unittest.main()
