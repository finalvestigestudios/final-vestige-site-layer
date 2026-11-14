"""R347 source-only fail-closed editorial and merchant guards. No network, mail or accounts."""
import json, pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parent
class R347(unittest.TestCase):
 def setUp(self):
  self.md=(ROOT/"OPTIONAL_ISSUE05_CHEVREUL.md").read_text()
  self.txt=(ROOT/"OPTIONAL_ISSUE05_CHEVREUL.txt").read_text()
  self.html=(ROOT/"OPTIONAL_ISSUE05_CHEVREUL.html").read_text()
  self.mat=json.loads((ROOT/"RELEASE_GATES.json").read_text())
 def test_one_source_candidate(self):
  self.assertIn("NOT ADOPTED",self.md)
  self.assertIn("HOLD_MERCHANT",self.md)
  self.assertEqual(self.md.count("**Proposed single CTA — NOT ACTIVE:**"),1)
 def test_merchant_never_activated(self):
  self.assertIn("[[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]]",self.md)
  self.assertFalse(any(g["passed"] for g in self.mat["release_gates"]))
  self.assertTrue(all(v is None for v in self.mat["affiliate_urls"]))
 def test_disclosure_adjacent(self):
  p=self.md.index("[[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]]")
  self.assertIn("Commercial disclosure",self.md[p:p+400])
 def test_history_not_product_proof(self):
  for s in ["Chevreul","ideomotor effect","does not show","branded recording"]:
   self.assertIn(s,self.md)
 def test_full_sources(self):
  for s in ["books.google.com/books?id=kzsAAAAAQAAJ","doi.org/10.1080/00029157.2011.10401754","nccih.nih.gov/health/hypnosis","hypnosislive.com/mental-skills/total-focus","hypnosislive.com/faq"]:
   self.assertIn(s,self.md)
 def test_sender_footer_gate(self):
  for token in ["[[VALID_POSTAL_ADDRESS_REQUIRED]]","[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"]:
   self.assertIn(token,self.md);self.assertIn(token,self.html);self.assertIn(token,self.txt)
 def test_email_safe_html(self):
  for token in ['<html lang="en">','role="presentation"','<title>','viewport','overflow-wrap:anywhere']:
   self.assertIn(token,self.html)
  for bad in ["<script","<iframe","<form","mailto:"]:
   self.assertNotIn(bad,self.html.lower())
 def test_no_active_offer_anchor(self):
  self.assertNotIn('href="[[APPROVED_',self.html)
  self.assertEqual(self.html.count("UNSENT DRAFT"),1)
 def test_prices_and_unapproved_guarantees_absent(self):
  for s in ["$17.95","$22.95","100% razor-sharp concentration","reprogram your brain","guaranteed"]:
   self.assertNotIn(s,self.md)
if __name__=="__main__":unittest.main()
