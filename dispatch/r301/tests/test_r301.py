"""Offline fail-closed checks for R301; does not authorize email sending."""
import json
from pathlib import Path
import unittest
R=Path(__file__).resolve().parents[1]
class TestIssue01(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=(R/'issue01-alternative.md').read_text();cls.t=(R/'issue01-alternative.txt').read_text();cls.h=(R/'issue01-alternative.html').read_text();cls.e=json.loads((R/'evidence-and-release.json').read_text())
 def test_status(self):
  self.assertEqual(self.e['status'],'HOLD_UNSENT');self.assertFalse(self.e['founder_adoption'])
 def test_mix(self):
  self.assertEqual(self.e['mix']['commercial_held'],[3,5]);self.assertEqual(self.e['mix']['editorial'],[1,2,4,6])
 def test_subject(self):
  for b in [self.m,self.t,self.h]:self.assertIn(self.e['subject'],b);self.assertIn(self.e['proposed_preheader'],b)
 def test_cta(self):
  self.assertEqual(self.h.count('class="primary-cta"'),1);self.assertEqual(self.e['primary_cta_count'],1)
 def test_study_sources(self):
  for url in self.e['original_studies']:
   for b in [self.m,self.t,self.h]:self.assertIn(url,b)
 def test_no_merchant_tracking(self):
  for b in [self.m,self.t,self.h]:
   for s in ['utm_source','https://zen12.com','https://hypnosislive.com']:self.assertNotIn(s,b)
 def test_no_active_scripts(self):
  for x in ['<script','<iframe','<form','onclick=','<canvas']:self.assertNotIn(x,self.h.lower())
 def test_legal_holds(self):
  for b in [self.m,self.t,self.h]:
   self.assertIn('[[VALID_POSTAL_ADDRESS_REQUIRED]]',b);self.assertIn('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]',b)
 def test_no_fake_revenue(self):
  self.assertEqual(self.e['provider']['email_eligible'],'UNKNOWN');self.assertIsNone(self.e['revenue']['paid_orders'])
 def test_no_approval(self):
  self.assertFalse(any(self.e['hard_holds'].values()));self.assertFalse(self.e['jetpack_native_preheader_verified'])
if __name__=='__main__':unittest.main()
