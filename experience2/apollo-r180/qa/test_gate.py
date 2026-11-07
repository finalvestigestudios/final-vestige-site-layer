"""R180 guard regression checks; no outbound network."""
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from gate import preflight
class GuardTests(unittest.TestCase):
 def args(self, **kw):
  d={'fixture':None,'url':None,'approved_host':None,'axe_js':None}
  d.update(kw);return SimpleNamespace(**d)
 def test_fixture_is_labeled_only(self):
  self.assertEqual(preflight(self.args(fixture=Path('fixture.html'))),'FIXTURE_ONLY')
 def test_refuse_missing_or_ambiguous_mode(self):
  with self.assertRaises(ValueError):preflight(self.args())
  with self.assertRaises(ValueError):preflight(self.args(fixture=Path('x'),url='https://staging.test/'))
 def test_refuse_production(self):
  with self.assertRaises(ValueError):preflight(self.args(url='https://finalvestige.com/apollo/',approved_host='finalvestige.com'))
 def test_refuse_host_or_scheme_without_network(self):
  for url in ('http://staging.test/','https://other.test/','file:///tmp/staging.html'):
   with self.assertRaises(ValueError):preflight(self.args(url=url,approved_host='staging.test'))
 def test_refuse_real_staging_without_axe(self):
  with self.assertRaises(ValueError):preflight(self.args(url='https://staging.test/apollo',approved_host='staging.test'))
 def test_declares_candidate_with_local_axe(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'axe.js';p.write_text('synthetic only; do not use for acceptance')
   self.assertEqual(preflight(self.args(url='https://staging.test/apollo',approved_host='staging.test',axe_js=p)),'STAGING_UNAPPROVED')
if __name__=='__main__':unittest.main()
