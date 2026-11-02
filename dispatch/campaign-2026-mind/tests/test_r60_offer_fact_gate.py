"""Independent merchant-fact anti-release tests for R60."""
import copy,json,pathlib,sys,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]/"r60-offer-fact-check"
sys.path.insert(0,str(ROOT))
from offer_fact_gate import check,decision
D=json.loads((ROOT/"evidence.json").read_text(encoding="utf-8"))
class TestR60OfferFactGate(unittest.TestCase):
 def test_baseline(self): self.assertEqual(check(D),[])
 def test_declaration_never_authorizes(self): self.assertFalse(decision(D)["send_authorized"])
 def test_counts_not_added(self): self.assertEqual(D["wordpress"]["subscriber_counts"]["total"],2)
 def test_no_received_message(self): self.assertFalse(D["wordpress"]["real_email_preview_verified"])
 def test_no_received_welcome(self): self.assertFalse(D["wordpress"]["welcome_received_verified"])
 def test_no_postal_claim(self): self.assertFalse(D["wordpress"]["mailing_address_verified"])
 def test_no_optout_claim(self): self.assertFalse(D["wordpress"]["unsubscribe_in_received_email_verified"])
 def test_no_approved_guide(self): self.assertTrue(all(x["live_approved_guide"] is None for x in D["offers"].values()))
 def test_no_commission_urls(self): self.assertTrue(all(x["earning_url"] is None for x in D["offers"].values()))
 def test_zen12_privacy_risk(self): self.assertIn("Cell/mobile",D["offers"]["zen12"]["personal_data_field"])
 def test_total_focus_price_conflict(self): self.assertIn("$22.95",D["offers"]["total_focus"]["observed_dynamic_checkout"])
 def test_no_seller_claims_as_proof(self): self.assertIn("NOT_PRODUCT_SPECIFIC_INDEPENDENT_EVIDENCE",D["source_classification"]["seller_page"])
 def test_status_mutation(self):
  x=copy.deepcopy(D);x["campaign"]["status"]="READY";self.assertIn("campaign hold removed",check(x))
 def test_mixture_mutation(self):
  x=copy.deepcopy(D);x["campaign"]["mix"]["commercial"]=[3];self.assertIn("original 4:2 mix altered",check(x))
 def test_affiliate_link_mutation(self):
  x=copy.deepcopy(D);x["offers"]["zen12"]["earning_url"]="https://example.com/affiliate";self.assertTrue(any("activated earning_url" in e for e in check(x)))
 def test_fabricated_approval(self):
  x=copy.deepcopy(D);x["offers"]["total_focus"]["partner_approved"]=True;self.assertTrue(any("unverified partner_approved" in e for e in check(x)))
 def test_email_permission_mutation(self):
  x=copy.deepcopy(D);x["offers"]["zen12"]["email_promotion_approved"]=True;self.assertTrue(any("email_promotion_approved" in e for e in check(x)))
 def test_postal_mutation(self):
  x=copy.deepcopy(D);x["wordpress"]["mailing_address_verified"]=True;self.assertTrue(any("mailing_address_verified" in e for e in check(x)))
 def test_preview_mutation(self):
  x=copy.deepcopy(D);x["wordpress"]["real_email_preview_verified"]=True;self.assertTrue(any("real_email_preview_verified" in e for e in check(x)))
 def test_sender_mutation(self):
  x=copy.deepcopy(D);x["wordpress"]["auto_new_posts"]=True;self.assertTrue(any("new-post sending" in e for e in check(x)))
 def test_safety_mutation(self):
  x=copy.deepcopy(D);x["constraints"]["no_mail"]=False;self.assertTrue(any("safety constraint disabled" in e for e in check(x)))
 def test_missing_offer(self):
  x=copy.deepcopy(D);del x["offers"]["zen12"];self.assertIn("named offers changed",check(x))
 def test_no_wrong_product_refund(self):self.assertNotEqual(D["offers"]["zen12"]["advertised_refund"],D["offers"]["total_focus"]["advertised_refund"])
 def test_zero_cost_policy(self):self.assertTrue(D["constraints"]["no_tracking"] and D["constraints"]["no_list_import"])
 def test_founder_permission_forgery(self):
  x=copy.deepcopy(D);x["campaign"]["founder_final_send_permission"]=True;self.assertIn("founder permission fabricated",check(x))
if __name__=="__main__":unittest.main()
