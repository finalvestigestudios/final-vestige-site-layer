"""Independent static checks for R67 optional commercial letter packet."""
import unittest,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
D=ROOT/"r67-offer-proof-letters"
class R67Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.manifest=json.loads((D/"manifest.json").read_text(encoding="utf8"))
  cls.texts={n:(D/f"issue-{n}.md").read_text(encoding="utf8") for n in ("03","05")}
 def test_eight_hard_hold_constraints(self):
  x=self.manifest
  self.assertEqual(x["status"],"DRAFT_ONLY_HOLD_UNSENT")
  self.assertFalse(x["canonical_changed"]);self.assertFalse(x["founder_approved_substitution"])
  self.assertTrue(all(v is False for v in x["gates"].values()))
  self.assertTrue(x["no_wordpress_writes"] and x["no_email_sent"] and x["no_contacts"])
 def test_mix_and_commercial_urls(self):
  m=self.manifest
  self.assertEqual(m["mix"],{"editorial":[1,2,4,6],"commercial_reserved":[3,5]})
  self.assertTrue(all(a["affiliate_url"] is None for a in m["letters"]))
 def test_early_disclosure_both(self):
  for n,t in self.texts.items():
   first=" ".join(t.split("\n---\n",1)[1].split()[:55]).lower()
   self.assertIn("commercial transparency",first,n)
   self.assertIn("commission",first,n)
 def test_disclosure_beside_disabled_guide(self):
  for n,t in self.texts.items():
   p=t.index("[[APPROVED_")
   self.assertIn("Commercial disclosure",t[p:p+450],n)
 def test_claims_and_refs(self):
  self.assertIn("https://zen12.com/hnp",self.texts["03"])
  self.assertIn("https://hypnosislive.com/mental-skills/total-focus",self.texts["05"])
  for t in self.texts.values():
   self.assertIn("www.nccih.nih.gov",t)
   self.assertIn("[[VALID_POSTAL_ADDRESS_REQUIRED]]",t)
   self.assertIn("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]",t)
 def test_preview_safe(self):
  for n in ("03","05"):
   html=(D/f"preview-{n}.html").read_text(encoding="utf8").lower()
   plain=(D/f"preview-{n}.txt").read_text(encoding="utf8")
   self.assertIn('<html lang="en">',html)
   self.assertIn('role="presentation"',html)
   self.assertNotRegex(html,r"<(?:script|form|iframe|img|button)\b")
   self.assertNotIn('href=',html)
   self.assertIn("hold_unsent",html)
   self.assertIn("[[APPROVED_",plain)
 def test_no_unsupported_promises(self):
  banned=("guaranteed income","clinically proven zen12","guarantees better concentration","buy now before midnight","cures anxiety")
  for t in self.texts.values():
   for b in banned:self.assertNotIn(b,t.lower())
 def test_no_real_metrics(self):
  self.assertFalse(self.manifest["live_attribution"])
  self.assertTrue(all(v is None for v in self.manifest["actual_metrics"].values()))
if __name__=="__main__":unittest.main()
