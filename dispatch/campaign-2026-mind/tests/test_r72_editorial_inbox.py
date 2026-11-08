"""R72: synthetic, privacy-safe tests of proposed custom excerpt release contract."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "r72-editorial-inbox"
S = importlib.util.spec_from_file_location("r72_contract", ROOT / "check_release_contract.py")
contract = importlib.util.module_from_spec(S)
S.loader.exec_module(contract)

class R72Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "candidates.json").read_text(encoding="utf-8"))

    def mutate(self, fn):
        doc=copy.deepcopy(self.data)
        fn(doc)
        self.assertTrue(contract.evaluate(doc))

    def test_01_contract_reviewable_but_not_sending(self):
        self.assertEqual(contract.evaluate(self.data), [])

    def test_02_all_six_and_mixture(self):
        self.assertEqual(len(self.data["editions"]),6)
        self.assertEqual([x["number"] for x in self.data["editions"] if x["kind"]=="commercial-review-pending"], [3,5])

    def test_03_status_mutation_fails(self):
        self.mutate(lambda d:d.update(release_state="APPROVED"))

    def test_04_sender_approval_mutation_fails(self):
        self.mutate(lambda d:d.update(future_email_approved=True))

    def test_05_schedule_mutation_fails(self):
        self.mutate(lambda d:d.update(future_email_scheduled=True))

    def test_06_premature_preheader_claim_fails(self):
        self.mutate(lambda d:d["channel"].update(preheader_editable_control="YES"))

    def test_07_privacy_consent_overclaim_fails(self):
        self.mutate(lambda d:d["commercial_permissions"].update(private_buyer_data_processing_plan_approved=True))

    def test_08_merchant_email_permission_overclaim_fails(self):
        self.mutate(lambda d:d["commercial_permissions"].update(zen12_email="APPROVED"))

    def test_09_commercial_cta_must_be_disabled(self):
        self.mutate(lambda d:d["editions"][2].update(planned_cta="https://zen12.com/"))

    def test_10_disclosure_in_first_55_required(self):
        self.mutate(lambda d:d["editions"][4].update(intro="First we explore a focus recording. " * 20+"Final Vestige may receive a commission."))

    def test_11_eligible_subscriber_inference_fails(self):
        self.mutate(lambda d:d["channel"]["reported_counts"].update(send_eligible=2))

    def test_12_no_tracking_urls(self):
        self.mutate(lambda d:d["editions"][0].update(intro=self.data["editions"][0]["intro"]+" https://example.com/?utm_campaign=test"))

    def test_13_cannot_delete_a_commercial_slot(self):
        self.mutate(lambda d:d["editions"].pop(4))

    def test_14_no_unsupported_merchant_promise(self):
        self.mutate(lambda d:d["editions"][2].update(intro=self.data["editions"][2]["intro"]+" Buy now for 100% guaranteed results"))

    def test_15_no_fake_source(self):
        self.mutate(lambda d:d["editions"][1].update(source_urls=["javascript:alert(1)"]))

    def test_16_no_automatic_wp_installation(self):
        self.mutate(lambda d:d["editions"][5].update(production_excerpt_installed=True))

    def test_17_offline_html_no_forms_or_sends(self):
        html=(ROOT/"review.html").read_text(encoding="utf-8")
        self.assertIn('lang="en"',html)
        self.assertIn('name="viewport"',html)
        self.assertIn('HOLD_UNSENT',html)
        for bad in ("<script", "<form", "mailto:", "data:image", "tracking-pixel"):
            self.assertNotIn(bad,html.lower())

    def test_18_html_and_plaintext_show_every_subject(self):
        html=(ROOT/"review.html").read_text(encoding="utf-8")
        txt=(ROOT/"review.txt").read_text(encoding="utf-8")
        for e in self.data["editions"]:
            self.assertIn(e["subject"],html)
            self.assertIn(e["subject"],txt)
            self.assertIn(e["intro"],txt)

    def test_19_no_pii_or_affiliate_links(self):
        contents = (ROOT/"review.html").read_text(encoding="utf-8")+(ROOT/"review.txt").read_text(encoding="utf-8")
        self.assertNotIn("brhodes",contents)
        self.assertNotIn("aff_id=",contents)
        self.assertNotIn("refid=",contents)

    def test_20_original_canonical_untouched(self):
        original=list((ROOT.parent/"issues").glob("*.md"))
        self.assertEqual(len(original),6)
        manifest=json.loads((ROOT.parent/"manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"],"DRAFT_UNSENT_NO_SCHEDULING")

if __name__ == "__main__":
    unittest.main()
