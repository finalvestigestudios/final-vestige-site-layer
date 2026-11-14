"""R350 native Python test suite. No real subscribers or transactions."""
import copy, json, unittest
from pathlib import Path
from gate import audit
BASE=json.loads((Path(__file__).parent/"SIX_ISSUE_RELEASE_LEDGER.json").read_text())
class GateTests(unittest.TestCase):
    def test_holds(self): self.assertEqual(audit(BASE)["status"],"HOLD_UNSENT")
    def test_never_sends(self): self.assertFalse(audit(BASE)["send_authorized"])
    def test_overlap(self): self.assertIn("counts_overlap_no_addition",audit(BASE)["blockers"])
    def test_eligible(self): self.assertIn("eligible_recipients_unknown",audit(BASE)["blockers"])
    def test_address(self): self.assertIn("publisher_postal_unknown",audit(BASE)["blockers"])
    def test_unsubscribe(self): self.assertIn("working_unsubscribe_unknown",audit(BASE)["blockers"])
    def test_inbox(self): self.assertIn("native_received_email_unknown",audit(BASE)["blockers"])
    def test_approval(self): self.assertIn("no_final_founder_approval",audit(BASE)["blockers"])
    def test_sales(self): self.assertIn("settled_sales_unknown",audit(BASE)["blockers"])
    def test_sessions(self): self.assertIn("qualified_sessions_unknown",audit(BASE)["blockers"])
    def test_duplicate_cta(self): self.assertEqual(len(audit(BASE)["repeated_editorial_urls"]),1)
    def test_six_issue_integrity(self):
        d=copy.deepcopy(BASE);d["issues"].pop();self.assertIn("six_issue_integrity",audit(d)["blockers"])
    def test_mix_integrity(self):
        d=copy.deepcopy(BASE);d["issues"][1]["kind"]="commercial";self.assertIn("four_two_mix",audit(d)["blockers"])
    def test_no_activation(self):
        d=copy.deepcopy(BASE);d["issues"][2]["cta"]="https://example.org/offer";self.assertIn("commercial_guide_activated",audit(d)["blockers"])
    def test_no_fake_approval(self):
        d=copy.deepcopy(BASE);d["commercial_offers"]["zen12"]["email_permission"]=True;self.assertIn("merchant_attestation_unproved",audit(d)["blockers"])
    def test_no_manuscript_release(self):
        d=copy.deepcopy(BASE);d["issues"][0]["status"]="APPROVED";self.assertIn("release_status",audit(d)["blockers"])
    def test_no_fake_revenue(self): self.assertIsNone(audit(BASE)["net_revenue_per_1000"])
if __name__=="__main__":unittest.main()
