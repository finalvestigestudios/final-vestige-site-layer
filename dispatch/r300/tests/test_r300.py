"""Static fail-closed R300 review suite; run: python -I -m unittest discover -s dispatch/r300/tests -v"""
from pathlib import Path
import json
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
class ReviewGate(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.md=(ROOT/'issue02-franklin-review.md').read_text(encoding='utf-8')
  cls.txt=(ROOT/'issue02-franklin-review.txt').read_text(encoding='utf-8')
  cls.html=(ROOT/'issue02-franklin-review.html').read_text(encoding='utf-8')
  cls.ledger=json.loads((ROOT/'evidence.json').read_text(encoding='utf-8'))
 def test_hold_status(self):
  self.assertIn('UNSENT / NOT ADOPTED',self.md)
  self.assertTrue(self.ledger['no_send'])
  self.assertFalse(self.ledger['founder_final_send_approval'])
 def test_mix_and_commercial_hold(self):
  self.assertEqual(self.ledger['offer_allocations_unchanged']['commercial_held'],[3,5])
  self.assertEqual(self.ledger['offer_allocations_unchanged']['editorial'],[1,2,4,6])
  self.assertEqual(self.ledger['merchant_review']['issues_03_05'],'HOLD_MERCHANT')
 def test_source_links_in_all_formats(self):
  for link in self.ledger['source_links']+[self.ledger['primary_cta']]:
   for body in (self.md,self.txt,self.html):
    self.assertIn(link,body)
 def test_single_primary_cta(self):
  self.assertEqual(self.html.count('class="primary-cta"'),1)
  self.assertEqual(self.md.count('**Read the source-led investigation:**'),1)
 def test_no_mail_or_tracking_activation(self):
  for body in (self.md,self.txt,self.html):
   for bad in ('utm_source=','utm_campaign=','mailto:','https://zen12.com','https://hypnosislive.com','buy now','100% guaranteed'):
    self.assertNotIn(bad,body.lower())
 def test_legal_hard_stops_every_format(self):
  for body in (self.md,self.txt,self.html):
   self.assertIn('[[VALID_POSTAL_ADDRESS_REQUIRED]]',body)
   self.assertIn('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]',body)
 def test_historical_boundaries(self):
  for phrase in ('four other trees','Deslon','not','fluid'):
   self.assertIn(phrase.lower(),self.md.lower())
  self.assertIn('English translation published in 1785',self.md)
 def test_subject_and_preheader_parity(self):
  for body in (self.md,self.txt,self.html):
   self.assertIn(self.ledger['subject'],body)
   self.assertIn(self.ledger['proposed_preheader'],body)
  self.assertLessEqual(len(self.ledger['subject']),60)
 def test_email_safe_preview(self):
  self.assertIn('role="presentation"',self.html)
  self.assertIn('lang="en"',self.html)
  self.assertNotRegex(self.html.lower(),r'<script|<form|<iframe|onload=|onclick=')
 def test_not_false_consent(self):
  self.assertEqual(self.ledger['provider_snapshot']['email_eligible'],'UNKNOWN')
  self.assertEqual(self.ledger['provider_snapshot']['welcome_message'],'CONFIGURED_NOT_RECEIVED')
  self.assertNotEqual(self.ledger['provider_snapshot']['diagnostic_counts']['confirmed'],self.ledger['provider_snapshot']['separate_followers']['email'])
 def test_native_preheader_is_unverified(self):
  self.assertEqual(self.ledger['preheader_native_jetpack'],'UNVERIFIED')
 def test_revenue_unknown(self):
  self.assertEqual(self.ledger['settled_revenue'],'UNKNOWN')
  self.assertEqual(self.ledger['qualified_sessions'],'UNKNOWN')

if __name__=='__main__': unittest.main()
