"""R100 optional Issue 05: exact seller SKU, reader value, inactive CTA and release gate.
Executable offline; NEVER attempts to read/send mail or mutate WordPress.
"""
import copy
import importlib.util
import json
import pathlib
import re
import unittest
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[1]
PKG = ROOT / "r100-total-focus-specific"
SPEC = importlib.util.spec_from_file_location("r100_offer_guard",PKG/"offer_guard.py")
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)

class R100ExactProductReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger,cls.md,cls.txt,cls.html,cls.manifest=guard.load()
        cls.all_text=[cls.md,cls.txt,cls.html]

    def test_01_committed_guard_accepts_static_draft(self):
        self.assertEqual(guard.validate(*guard.load()),[])

    def test_02_exact_master_is_still_unsent(self):
        self.assertEqual(self.manifest["status"],"DRAFT_UNSENT_NO_SCHEDULING")
        self.assertTrue(all(e["publish_state"]=="hold" for e in self.manifest["issues"]))

    def test_03_four_two_original_cadence(self):
        self.assertEqual(self.ledger["mix"],{"editorial":[1,2,4,6],"commercial_reserved":[3,5]})
        self.assertEqual([i["number"] for i in self.manifest["issues"] if i["kind"]!="editorial"],[3,5])

    def test_04_original_issue_five_unmodified(self):
        original=(ROOT/"issues"/"05-before-you-press-play.md").read_text(encoding="utf-8")
        self.assertIn("Before you press play on a hypnosis audio",original)
        self.assertIn("[[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]]",original)
        self.assertNotIn("The recording is 33 minutes",original)

    def test_05_exact_subject_consistent(self):
        s=self.ledger["proposed_subject"]
        self.assertTrue(24<=len(s)<=72)
        self.assertTrue(all(s in body for body in self.all_text))

    def test_06_preheader_not_promised_as_native_field(self):
        self.assertFalse(self.ledger["native_preheader_field_verified"])
        self.assertTrue(all("preheader" in b.lower() for b in self.all_text))

    def test_07_same_exact_recording(self):
        for b in self.all_text:
            self.assertIn("Total Focus",b)
            self.assertIn("33-minute",b)
            self.assertIn("47 MB",b)

    def test_08_seller_claims_not_independent_facts(self):
        self.assertIn("not independently verified",self.md.lower())
        self.assertIn("seller",self.md.lower())
        self.assertIn("product-specific",self.md.lower())

    def test_09_refund_caveats_and_no_guaranteed_outcomes(self):
        self.assertIn("14-day",self.md)
        self.assertIn("five",self.md)
        self.assertIn("twelve-month",self.md)
        self.assertNotIn("we guarantee a refund",self.md.lower())

    def test_10_no_fixed_purchase_price(self):
        self.assertTrue(all(not re.search(r"\$\s*\d+",x) for x in self.all_text))

    def test_11_five_useful_questions(self):
        self.assertIn("five checks",self.md.lower())
        for term in ["product","outcome","refund","privacy","work sessions"]:
            self.assertIn(term,self.md.lower())

    def test_12_nonclinical_baseline_exercise(self):
        for term in ["three ordinary work sessions","first interruption","setting"]:
            self.assertIn(term,self.md)

    def test_13_data_minimization_not_feigned(self):
        self.assertIn("aggregate-only",self.md)
        self.assertIn("buyer",self.md.lower())
        self.assertFalse(self.ledger["blocked_permissions"]["aggregate_only_purchaser_reporting_contract"])

    def test_14_affiliate_approval_not_inferred(self):
        self.assertFalse(self.ledger["blocked_permissions"]["named_final_vestige_affiliate_acceptance"])
        self.assertFalse(self.ledger["blocked_permissions"]["exact_sku_email_promotion_permission"])
        self.assertIsNone(self.ledger["approved_affiliate_merchant_url"])

    def test_15_source_urls_primary_and_product_specific(self):
        urls={s["url"] for s in self.ledger["sources"]}
        for suffix in ["hypnosislive.com/mental-skills/total-focus",
                       "hypnosislive.com/faq","inspire3.com/terms/","inspire3.com/privacy/"]:
            self.assertTrue(any(suffix in u for u in urls))

    def test_16_source_matrix_with_limitations(self):
        self.assertGreaterEqual(len(self.ledger["sources"]),6)
        self.assertTrue(all(len(x["limitations"])>35 for x in self.ledger["sources"]))

    def test_17_no_direct_merchant_offer(self):
        self.assertTrue(all("href=" not in b.lower() for b in [self.html]))
        self.assertIsNone(self.ledger["approved_live_buyer_guide_url"])

    def test_18_only_one_main_cta_intended(self):
        self.assertEqual(self.md.count("[[APPROVED_LIVE_TOTAL_FOCUS_GUIDE_URL_REQUIRED]]"),1)
        self.assertEqual(self.html.count("[[APPROVED_LIVE_TOTAL_FOCUS_GUIDE_URL_REQUIRED]]"),1)
        self.assertEqual(self.txt.count("[[APPROVED_LIVE_TOTAL_FOCUS_GUIDE_URL_REQUIRED]]"),1)

    def test_19_disclosure_beside_cta(self):
        for b in self.all_text:
            p=b.index("[[APPROVED_LIVE_TOTAL_FOCUS_GUIDE_URL_REQUIRED]]")
            near=b[p:p+700].lower()
            self.assertIn("commercial disclosure",near)
            self.assertIn("commission",near)

    def test_20_excerpt_leads_with_financial_relationship(self):
        e=self.ledger["email_excerpts"]["commercial_first_350_char_candidate"]
        self.assertTrue(e.startswith("Commercial note:"))
        self.assertIn("commission",e)
        self.assertIn("no earning link is active",e)

    def test_21_excerpt_no_dead_cta_or_tracking(self):
        e=self.ledger["email_excerpts"]["commercial_first_350_char_candidate"]
        self.assertNotIn("[[",e)
        self.assertNotIn("http",e)
        self.assertNotIn("utm_",e)

    def test_22_accessible_email_safe_review(self):
        self.assertIn('lang="en"',self.html)
        self.assertIn('name="viewport"',self.html)
        self.assertIn('role="presentation"',self.html)
        self.assertIn("<h1",self.html)
        self.assertIn("<h2",self.html)

    def test_23_no_remote_email_media_or_scripts(self):
        parsed=guard.EmailHTML()
        parsed.feed(self.html)
        self.assertEqual(parsed.links,[])
        self.assertEqual(parsed.media,[])
        self.assertEqual(parsed.forms,[])
        self.assertEqual(parsed.scripts,[])
        self.assertGreaterEqual(len(parsed.tables),2)

    def test_24_reviewer_not_a_real_jetpack_mime(self):
        self.assertIn("NOT A JETPACK RECEIVED EMAIL",self.html)
        self.assertIn("not a verified native Jetpack",self.html)

    def test_25_commercial_legal_footer_unresolved_all_variants(self):
        for b in self.all_text:
            self.assertIn(guard.POSTAL,b)
            self.assertIn(guard.UNSUB,b)

    def test_26_no_fake_analytics_or_recipient_eligibility(self):
        self.assertIsNone(self.ledger["verified_eligible_recipients"])
        self.assertEqual(self.ledger["sent_count_this_run"],0)

    def test_27_offer_terms_are_seller_statements_only(self):
        self.assertIn("seller-published",self.md)
        self.assertIn("not independently verified",self.md.lower())

    def test_28_fail_closed_if_false_permission_becomes_true(self):
        clone=copy.deepcopy(self.ledger)
        clone["blocked_permissions"]["exact_sku_email_promotion_permission"]=True
        self.assertTrue(guard.validate(clone,self.md,self.txt,self.html,self.manifest))

    def test_29_fail_closed_if_affiliate_link_inserted(self):
        clone=copy.deepcopy(self.ledger)
        clone["approved_affiliate_merchant_url"]="https://not-an-approved-link.example"
        self.assertTrue(guard.validate(clone,self.md,self.txt,self.html,self.manifest))

    def test_30_fail_closed_if_guide_claimed_live(self):
        clone=copy.deepcopy(self.ledger)
        clone["approved_live_buyer_guide_url"]="https://finalvestige.com/unauthorized"
        self.assertTrue(guard.validate(clone,self.md,self.txt,self.html,self.manifest))

    def test_31_fail_closed_if_recipient_count_guessed(self):
        clone=copy.deepcopy(self.ledger)
        clone["verified_eligible_recipients"]=4
        self.assertTrue(guard.validate(clone,self.md,self.txt,self.html,self.manifest))

    def test_32_fail_closed_if_site_auto_send_asserted(self):
        clone=copy.deepcopy(self.ledger)
        clone["new_post_default_send"]=True
        self.assertTrue(guard.validate(clone,self.md,self.txt,self.html,self.manifest))

    def test_33_fail_closed_if_excerpt_disclosure_missing(self):
        clone=copy.deepcopy(self.ledger)
        clone["email_excerpts"]["commercial_first_350_char_candidate"]="We recommend this powerful recording."
        self.assertTrue(guard.validate(clone,self.md,self.txt,self.html,self.manifest))

    def test_34_fail_closed_if_postal_address_faked(self):
        bad=self.html.replace(guard.POSTAL,"An address someone made up")
        self.assertTrue(guard.validate(self.ledger,self.md,self.txt,bad,self.manifest))

    def test_35_fail_closed_if_unsubscribe_removed(self):
        bad=self.txt.replace(guard.UNSUB,"Unsubscribe anytime")
        self.assertTrue(guard.validate(self.ledger,self.md,bad,self.html,self.manifest))

    def test_36_fail_closed_if_live_clickable_button_added(self):
        bad=self.html.replace("<h1",'<a href="https://hypnosislive.com/mental-skills/total-focus">BUY</a><h1',1)
        self.assertTrue(guard.validate(self.ledger,self.md,self.txt,bad,self.manifest))

    def test_37_fail_closed_if_price_claim_added(self):
        bad=self.md+"\nPrice: $24.44 guaranteed forever"
        self.assertTrue(guard.validate(self.ledger,bad,self.txt,self.html,self.manifest))

    def test_38_fail_closed_if_product_efficacy_exaggerated(self):
        bad=self.md+"\nResults guaranteed."
        self.assertTrue(guard.validate(self.ledger,bad,self.txt,self.html,self.manifest))

    def test_39_fail_closed_if_primary_source_missing(self):
        clone=copy.deepcopy(self.ledger)
        clone["sources"]=[s for s in clone["sources"] if s["key"]!="total_focus"]
        self.assertTrue(guard.validate(clone,self.md,self.txt,self.html,self.manifest))

    def test_40_fail_closed_if_four_two_mix_changed(self):
        clone=copy.deepcopy(self.ledger)
        clone["mix"]={"editorial":[1,2,3,4,6],"commercial_reserved":[5]}
        self.assertTrue(guard.validate(clone,self.md,self.txt,self.html,self.manifest))

if __name__ == "__main__":
    unittest.main()
