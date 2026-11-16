"""Local Chromium red-team: R400 structural-only PASS versus R401 custody FAIL.
No external web requests, redirects, or site writes. A fixture is not staging.
"""
import unittest
from playwright.sync_api import sync_playwright
import custody_overlay as overlay

FIXTURE=overlay.EXPERIENCE2/'apollo-r393'/'QA'/'local-php-fixture.html'
MUTATIONS={
 'changed_claim': "document.querySelector('.fv-r384__card p strong').parentElement.append(' NOT TRUE')",
 'changed_heading': "document.querySelector('[data-fv-r384-record] h4').textContent='Contrary to the report'",
 'changed_boundary': "document.querySelector('.fv-r384__limit').textContent='This proves an exact ignition point'",
 'altered_source_role': "document.querySelector('.fv-r384__drawer p').textContent='Source role: promotional advertising'",
 'substituted_card_nasa': "document.querySelector('[data-fv-r384-nasa]').setAttribute('href','https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/')",
 'hidden_rights': "document.querySelector('.fv-r384__rights').style.display='none'",
 'hidden_cta_opacity': "document.querySelector('[data-fv-free-cta]').style.opacity='0'",
 'incorrect_phase': "document.querySelector('.fv-r384__phase:last-of-type')?.append(document.querySelector('[data-fv-r384-record]'))",
 'relabel_publication': "document.querySelector('.fv-r384__source-group h4').textContent='NASA provided the original ignition spark'",
 'obscure_source': "document.querySelector('[data-fv-r384-nasa]').style.pointerEvents='none'",
}

class SourceCustodyRegression(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  overlay.dependencies(staging=False)
  cls.base,cls.visual=overlay.modules()
  cls.inspector=staticmethod(overlay.strengthened_inspector(cls.base,cls.visual))
  cls.browser_mgr=sync_playwright(); cls.pw=cls.browser_mgr.start()
  cls.browser=cls.pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  cls.context=cls.browser.new_context(service_workers='block');cls.context.route('**/*',lambda r:r.abort('blockedbyclient'))
  cls.page=cls.context.new_page()
  cls.html=FIXTURE.read_text(encoding='utf-8')
 @classmethod
 def tearDownClass(cls):
  cls.context.close();cls.browser.close();cls.pw.stop()
 def fresh(self):
  self.page.set_content(self.html,wait_until='domcontentloaded')
 def test_baseline_passes_both(self):
  self.fresh()
  self.assertEqual((getattr(self.base, 'inspect', None) or self.base.inspect_gallery)(self.page)['cards'],6)
  self.assertEqual(self.inspector(self.page)['exact_source_custody'],'PASS')
 def test_r400_misses_mutations_r401_detects(self):
  for name,script in MUTATIONS.items():
   with self.subTest(mutation=name):
    self.fresh();self.page.evaluate(script)
    self.assertEqual((getattr(self.base, 'inspect', None) or self.base.inspect_gallery)(self.page)['cards'],6,'R400 was expected to miss '+name)
    with self.assertRaises(AssertionError):self.inspector(self.page)
 def test_r401_nojs_readability(self):
  c=self.browser.new_context(java_script_enabled=False,service_workers='block')
  try:
   p=c.new_page();p.set_content(self.html)
   self.assertEqual(self.inspector(p)['exact_source_custody'],'PASS')
  finally:c.close()
 def test_staging_requires_exact_parent_git_blob(self):
  statuses=overlay.dependencies(staging=False)
  if all(row['match'] for row in statuses.values()):
   self.assertTrue(all(row['match'] for row in overlay.dependencies(staging=True).values()))
  else:
   with self.assertRaisesRegex(RuntimeError,'HOLD'):overlay.dependencies(staging=True)
 def test_parent_blob_custody(self):
  d=overlay.dependencies(staging=False)
  for path,v in d.items():
   if path not in ('apollo-r392/qa/semantic_custody.py','apollo-r400/qa/staging_browser_gate.py'):self.assertTrue(v['match'],path)

if __name__=='__main__':unittest.main(verbosity=2)
