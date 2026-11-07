"""Offline regression, real Chromium DOM mutation and spoofing controls.
No live requests, subscriber actions, analytics, or commerce effects.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import unittest
from playwright.sync_api import sync_playwright
from propose_focus_gift_guard import stage, EXPECTED_SOURCE_SHA256

HERE=Path(__file__).resolve().parent
OLD=json.loads((HERE/'focus_gift_source_20261107.json').read_text())['script']
NEW=(HERE/'focus_gift_guard.js').read_text()

class FocusGuardSource(unittest.TestCase):
 def test_old_pinned_hash(self):
  self.assertEqual(hashlib.sha256(OLD.encode()).hexdigest(),EXPECTED_SOURCE_SHA256)
 def test_staging_replaces_exactly_once(self):
  raw=f'<p>Preserve this page</p><script id="fvf-gift-v2">{OLD}</script><p>Keep the Focus anchors</p>'
  cand=stage(raw,NEW,OLD)
  self.assertIn('<script id="fvf-gift-v3">',cand)
  self.assertEqual(cand.count('Focus anchors'),1)
  self.assertNotIn('id="fvf-gift-v2"',cand)
 def test_drift_refused(self):
  with self.assertRaisesRegex(ValueError,'does not match'):
   stage('<script id="fvf-gift-v2">tampered</script>',NEW,OLD)
 def test_duplicate_refused(self):
  raw=f'<script id="fvf-gift-v2">{OLD}</script>'*2
  with self.assertRaisesRegex(ValueError,'exactly one'):
   stage(raw,NEW,OLD)
 def test_html_tag_injection_refused(self):
  with self.assertRaisesRegex(ValueError,'script tag termination'):
   stage(f'<script id="fvf-gift-v2">{OLD}</script>',NEW+'</script>',OLD)
 def test_not_report_as_confirmed_signup(self):
  self.assertIn('NEVER a confirmed subscriber metric',NEW)
  self.assertNotIn('location.search',NEW)

class FocusGuardBrowser(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.pw=sync_playwright().start()
  cls.browser=cls.pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 @classmethod
 def tearDownClass(cls):
  cls.browser.close();cls.pw.stop()
 def build(self, js=True,klass='',gift=True):
  ctx=self.browser.new_context(viewport={'width':390,'height':844},java_script_enabled=js)
  p=ctx.new_page()
  gift_html='<div id="fvf-gift" hidden role="status">Your fieldbook is ready to download.</div>' if gift else ''
  h=f'''<!doctype html><html><head><style>body{{background:#0d1112;color:#e9ddc8}} #fvf-gift{{padding:22px;border:1px solid #b8955e}} [hidden]{{display:none!important}}</style></head><body><h1>Focus Fieldbook</h1><div class="wp-block-jetpack-subscriptions__container {klass}"><p>Jetpack fixture only</p></div>{gift_html}<script>{NEW}</script></body></html>'''
  p.set_content(h)
  return ctx,p
 def test_plain_no_url_spoof(self):
  ctx,p=self.build()
  self.assertTrue(p.locator('#fvf-gift').evaluate('(n)=>n.hidden'))
  # Browser URL query is deliberately unavailable, and patch has no URL read.
  self.assertNotIn('window.location',NEW)
  ctx.close()
 def test_subscriber_class_render(self):
  ctx,p=self.build(klass='is-subscriber')
  self.assertFalse(p.locator('#fvf-gift').evaluate('(n)=>n.hidden'))
  ctx.close()
 def test_revoke_class_hides_again(self):
  ctx,p=self.build(klass='is-subscriber')
  p.locator('.wp-block-jetpack-subscriptions__container').evaluate('(n)=>n.classList.remove("is-subscriber")')
  p.wait_for_function('document.getElementById("fvf-gift").hidden')
  self.assertTrue(p.locator('#fvf-gift').evaluate('(n)=>n.hidden'))
  ctx.close()
 def test_add_class_reveals(self):
  ctx,p=self.build()
  p.locator('.wp-block-jetpack-subscriptions__container').evaluate('(n)=>n.classList.add("is-subscriber")')
  p.wait_for_function('!document.getElementById("fvf-gift").hidden')
  self.assertFalse(p.locator('#fvf-gift').evaluate('(n)=>n.hidden'))
  ctx.close()
 def test_similar_untrusted_class_does_not_reveal(self):
  ctx,p=self.build(klass='is-subscriber-fake')
  self.assertTrue(p.locator('#fvf-gift').evaluate('(n)=>n.hidden'))
  ctx.close()
 def test_no_js_hidden(self):
  ctx,p=self.build(js=False,klass='is-subscriber')
  self.assertTrue(p.locator('#fvf-gift').evaluate('(n)=>n.hidden'))
  ctx.close()
 def test_missing_container_safe(self):
  ctx,p=self.build(gift=False)
  self.assertEqual(p.locator('#fvf-gift').count(),0)
  ctx.close()

if __name__=='__main__':unittest.main(verbosity=2)
