"""Chromium DOM fixture regression tests; no network, signup, or real user data."""
import unittest
import os
import shutil
from playwright.sync_api import sync_playwright
from no_submit_signup_probe import inspect, safe_url

PAGES = {
 '/form/': '<main><div class="wp-block-jetpack-subscriptions"><form><label>Email<input type="email"></label><button type="submit">Subscribe</button></form></div></main>',
 '/modal/': '<main><div class="wp-block-jetpack-subscriptions"><button type="button" onclick="document.getElementById(\'email\').hidden=false">Subscribe</button><div id="email" hidden><label>Email<input type="email"></label></div></div></main>',
 '/loop/': '<main><div class="wp-block-jetpack-subscriptions"><a href="/loop/" onclick="event.preventDefault()">Subscribe</a></div></main>',
 '/link/': '<main><div class="wp-block-jetpack-subscriptions"><a href="/form/" onclick="event.preventDefault();document.querySelector(\'main\').innerHTML=\'<label>Email<input type=email></label>\'">Subscribe</a></div></main>',
 '/danger/': '<main><div class="wp-block-jetpack-subscriptions"><form onsubmit="window.submitted=true;event.preventDefault()"><button type="submit">Subscribe</button></form></div></main>',
 '/unlabelled/': '<main><input type="email" placeholder="Your email address"></main>',
}

class SignupBrowserProof(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.pw=sync_playwright().start()
  cls.browser=cls.pw.chromium.launch(headless=True,executable_path=os.environ.get('CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('chromium-browser'))
 @classmethod
 def tearDownClass(cls): cls.browser.close();cls.pw.stop()
 def setUp(self):
  self.context=self.browser.new_context(service_workers='block',accept_downloads=False)
  self.page=self.context.new_page()
 def tearDown(self): self.context.close()
 def check(self,path,expected):
  self.page.set_content(PAGES[path]);row=inspect(self.page,'https://fixture.invalid'+path,60,preloaded=True)
  self.assertEqual(row['decision'],expected,row)
  self.assertFalse(row['entered_email'])
  self.assertFalse(row['submitted'])
  self.assertFalse(row['clicked_submit'])
  return row
 def test_standard_form_is_detected(self): self.check('/form/','FORM_PRESENT_LABELLED')
 def test_button_modal_is_detected(self): self.check('/modal/','FORM_ACCESSIBLE_AFTER_SAFE_CLICK')
 def test_self_link_loop_is_flagged(self): self.check('/loop/','SUSPECT_SELF_LINK_LOOP_NO_FORM')
 def test_safe_click_reveals_form(self): self.check('/link/','FORM_ACCESSIBLE_AFTER_SAFE_CLICK')
 def test_submit_button_without_field_never_clicked(self):
  self.check('/danger/','NO_SAFE_CONTROL_OR_FORM')
  self.assertFalse(self.page.evaluate('!!window.submitted'))
 def test_unlabelled_field_not_approved(self): self.check('/unlabelled/','FORM_PRESENT_NEEDS_LABEL_REVIEW')
 def test_redacts_query_fragment_and_token(self):
  self.assertEqual(safe_url('https://finalvestige.com/focus/?token=secret#x'),'https://finalvestige.com/focus/')
 def test_redacts_basic_auth(self):
  self.assertNotIn('secret',safe_url('https://secret:password@finalvestige.com/dispatch/?x=secret'))

if __name__=='__main__':unittest.main()
