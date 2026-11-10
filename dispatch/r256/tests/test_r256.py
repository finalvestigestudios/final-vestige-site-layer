"""R256 isolated offline source/regression tests: no requests, no sends."""
import json, pathlib, unittest
P=pathlib.Path(__file__).resolve().parents[1]
class R256Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.md=(P/'issue02_OPTIONAL_UNSENT.md').read_text();cls.htm=(P/'issue02_OPTIONAL_UNSENT.html').read_text();cls.txt=(P/'issue02_OPTIONAL_UNSENT.txt').read_text();cls.g=json.loads((P/'RELEASE_GATES.json').read_text())
 def test_hold(self):
  self.assertEqual(self.g['status'],'ALL_HOLD_UNSENT')
  for k,v in self.g.items():
   if k.endswith('_verified') or k.endswith('_approval') or k.endswith('_adopted') or k.endswith('_reconciled'):self.assertIs(v,False,k)
 def test_six_issue_mix_preserved(self):self.assertEqual((self.g['editorial_count'],self.g['commercial_held']),(4,[3,5]))
 def test_primary_cta_once(self):self.assertEqual(self.htm.count('Read the Franklin commission investigation</a>'),1)
 def test_source_citations(self):
  for domain in ('gutenberg.org','commons.wikimedia.org','circee.org'):
   for s in (self.md,self.htm,self.txt):self.assertIn(domain,s)
 def test_no_merchant_or_scripting(self):
  for word in ('zen12.com','hypnosislive.com','<script','<img','<form','utm_','affiliates.inspire3.com'):
   for s in (self.md,self.htm,self.txt):self.assertNotIn(word,s.lower())
 def test_email_safe(self):
  for x in ('<html lang="en">','<table role="presentation"','display:none!important','max-width:640px'):self.assertIn(x,self.htm)
 def test_optional_not_authorized(self):
  for s in (self.md,self.htm,self.txt):self.assertIn('UNSENT',s)
  self.assertIn('NOT ADOPTED',self.md)
 def test_distinct_case_scope(self):
  for word in ('Franklin','Deslon','Puységur'):self.assertIn(word,self.md)
if __name__=='__main__':unittest.main()
