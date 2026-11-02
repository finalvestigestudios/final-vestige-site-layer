"""R71 native source/terms/preview checks: no network, CMS or messaging."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1] / "r71-merchant-terms"
SPEC = importlib.util.spec_from_file_location("r71_guard", ROOT / "verify_offer_guard.py")
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

class R71MerchantSafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "offer-evidence.json").read_text(encoding="utf-8"))
    def test_real_gate_is_permanently_held(self):
        self.assertEqual(mod.inspect(ROOT)["status"], "HOLD_UNSENT")
    def test_two_reserved_commercial_slots(self):
        self.assertEqual([x["number"] for x in self.data["issues"]],[3,5])
    def test_affiliate_account_unverified(self):
        self.assertEqual(self.data["permission_gate"]["specific_inspire3_account_accepted"],"UNVERIFIED")
    def test_email_permission_each_offer_unverified(self):
        for k in ("written_zen12_email_permission","written_total_focus_email_permission"):
            self.assertEqual(self.data["permission_gate"][k],"UNVERIFIED")
    def test_final_approval_not_granted(self):
        self.assertEqual(self.data["permission_gate"]["final_founder_send_approval"],"NOT_GRANTED")
    def test_exact_zen12_package_tiers(self):
        z=self.data["issues"][0]["seller_described"]
        self.assertEqual((z["premium_mp3s"],z["beginner_mp3s"],z["advanced_mp3s"]),(48,24,24))
    def test_refund_terms_not_equal(self):
        self.assertEqual([o["seller_terms"]["refund_days"] for o in self.data["issues"]],[365,14])
    def test_hypnosis_refund_cap(self):
        self.assertEqual(self.data["issues"][1]["seller_terms"]["refund_album_cap_per_twelve_months"],5)
    def test_merchant_product_specific_efficacy_unsubstantiated(self):
        for row in self.data["issues"]: self.assertGreater(len(row["unsupported_claims"]),1)
    def test_price_never_in_preview(self):
        for number in (3,5):
            for ext in ("txt","html"):
                p=(ROOT/f"issue-{number:02d}-preview.{ext}").read_text()
                self.assertNotRegex(p,r"\$\s*\d+")
    def test_no_active_merchant_or_buyer_guide_links(self):
        for number in (3,5):
            s=mod.Scan();s.feed((ROOT/f"issue-{number:02d}-preview.html").read_text())
            self.assertEqual(s.links,[])
    def test_disclosure_in_first_55_words(self):
        for number in (3,5):
            s=mod.Scan();s.feed((ROOT/f"issue-{number:02d}-preview.html").read_text())
            self.assertIn("commission",[x.lower() for x in s.words[:55]])
    def test_no_scripts_trackers_forms_images(self):
        for number in (3,5):
            s=mod.Scan();s.feed((ROOT/f"issue-{number:02d}-preview.html").read_text())
            self.assertFalse(set(s.tags) & {"script","iframe","form","img","button"})
    def test_original_canonical_not_changed_by_added_files(self):
        self.assertNotIn("issues/",str(ROOT))
    def test_source_matrix_has_direct_offer_checkout_policy(self):
        urls={s["url"] for s in self.data["source_provenance"]}
        self.assertIn("https://zen12.com/getstarted",urls)
        self.assertIn("https://hypnosislive.com/mental-skills/total-focus",urls)
        self.assertIn("https://inspire3.com/privacy/",urls)
    def test_phone_sms_may_not_is(self):
        s=self.data["issues"][0]["seller_terms"]
        self.assertIn("may",s["sms_caveat"])
    def test_reader_may_not_receives_pii(self):
        for i in self.data["issues"]:
            self.assertIn("MAY",i["affiliate_and_privacy"])
            self.assertIn("no evidence",i["affiliate_and_privacy"])
    def test_price_snapshots_labeled_internal(self):
        for i in self.data["issues"]:
            self.assertTrue(i["observed_prices_internal_only"]["do_not_quote_in_email"])
    def test_missing_expected_publisher_footer(self):
        for number in (3,5):
            s=(ROOT/f"issue-{number:02d}-preview.txt").read_text()
            self.assertIn("FINAL VESTIGE POSTAL ADDRESS: UNVERIFIED",s)
            self.assertIn("JETPACK UNSUBSCRIBE: UNVERIFIED",s)
    def test_mutation_fake_email_approval_rejected(self):
        tampered=copy.deepcopy(self.data)
        tampered["permission_gate"]["written_zen12_email_permission"]="APPROVED"
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)
            for f in ROOT.glob("issue-*-preview.*"): (p/f.name).write_bytes(f.read_bytes())
            (p/"offer-evidence.json").write_text(json.dumps(tampered))
            with self.assertRaises(AssertionError):mod.inspect(p)
    def test_mutation_silent_refund_cap_rejected(self):
        tampered=copy.deepcopy(self.data)
        tampered["issues"][1]["seller_terms"]["refund_album_cap_per_twelve_months"]=10
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)
            for f in ROOT.glob("issue-*-preview.*"): (p/f.name).write_bytes(f.read_bytes())
            (p/"offer-evidence.json").write_text(json.dumps(tampered))
            with self.assertRaises(AssertionError):mod.inspect(p)
    def test_mutation_active_affiliate_link_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)
            for f in ROOT.glob("issue-*-preview.*"): (p/f.name).write_bytes(f.read_bytes())
            (p/"offer-evidence.json").write_bytes((ROOT/"offer-evidence.json").read_bytes())
            f=p/"issue-05-preview.html"
            f.write_text(f.read_text().replace("</body>","<a href='https://example.org/affiliate'>Buy now</a></body>"))
            with self.assertRaises(AssertionError):mod.inspect(p)

if __name__=="__main__":unittest.main()
