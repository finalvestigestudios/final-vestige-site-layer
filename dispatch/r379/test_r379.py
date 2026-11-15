"""Deterministic source-only QA for R379; never contacts a subscriber."""
import unittest, json
from pathlib import Path
D=Path(__file__).resolve().parent
class ReleaseTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.s=json.loads((D/'HOLD_MATRIX.json').read_text())
  cls.md=(D/'ISSUE04_CORRECTION_CANDIDATE.md').read_text()
  cls.html=(D/'ISSUE04_CORRECTION_CANDIDATE.html').read_text()
  cls.txt=(D/'ISSUE04_CORRECTION_CANDIDATE.txt').read_text()
 def test_4_to_2(self):
  self.assertEqual([x['type'] for x in self.s['issues']].count('editorial'),4)
  self.assertEqual([x['type'] for x in self.s['issues']].count('commercial'),2)
 def test_all_hold(self):
  self.assertTrue(all(x['status'].startswith('HOLD_') for x in self.s['issues']))
  self.assertFalse(self.s['delivery']['founder_send_approval'])
 def test_merchant_disallowed(self):
  for x in self.s['issues']:
   if x['type']=='commercial':
    self.assertFalse(x['email_partner_rights_verified'])
    self.assertFalse(x['approved_guide_live'])
    self.assertFalse(x['issued_earning_link_verified'])
 def test_no_recipient_invention(self):
  self.assertIsNone(self.s['delivery']['email_eligible_unique_recipients'])
  self.assertEqual(self.s['delivery']['confirmed_reported'],3)
 def test_unverified_delivery(self):
  for key in ('received_fieldbook_welcome_verified','native_jetpack_preview_verified','valid_fv_postal_address_verified','actual_unsubscribe_verified'):
   self.assertFalse(self.s['delivery'][key])
 def test_no_fake_sales(self):
  self.assertIsNone(self.s['paid_orders'])
  self.assertIsNone(self.s['net_revenue'])
  self.assertIsNone(self.s['qualified_human_sessions'])
  self.assertIsNone(self.s['net_revenue_per_1000_qualified_sessions'])
 def test_corrected_source_trace(self):
  self.assertIn('nasa.gov/history/Apollo204/seamans3.html',self.md)
  self.assertIn('nasa.gov/history/Apollo204/seamans2.html',self.md)
  self.assertIn('NOT ADOPTED',self.md)
 def test_one_main_cta(self):
  self.assertEqual(self.html.count('href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"'),1)
 def test_review_only_markup(self):
  self.assertIn('lang="en"',self.html)
  self.assertIn('role="presentation"',self.html)
  self.assertIn('COMPLIANCE STOP',self.html)
  for disallowed in ('<form','<script','<iframe','<img'):
   self.assertNotIn(disallowed,self.html.lower())
 def test_plaintext(self):
  self.assertIn('SUBJECT:',self.txt)
  self.assertIn('STOP:',self.txt)
if __name__=='__main__':
 unittest.main()
