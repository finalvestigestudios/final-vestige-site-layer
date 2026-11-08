"""Static, read-only verification of optional R61 excerpts. Never authorizes sending."""
import json
import pathlib
import re
import unittest
from html.parser import HTMLParser
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
PKG = ROOT / "r61-excerpt-consent"

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.hrefs = []
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        for name,value in attrs:
            if name in ("href","src") and value:
                self.hrefs.append((tag,name,value))

class R61EditorialDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((PKG/"excerpt_packet.json").read_text(encoding="utf-8"))
        cls.issues=cls.data["issues"]
        cls.board=(PKG/"review_board.html").read_text(encoding="utf-8")
        cls.txt=(PKG/"review_board.txt").read_text(encoding="utf-8")
        cls.memo=(PKG/"release_decision.md").read_text(encoding="utf-8")
        cls.copy=(PKG/"commercial_editorial_inserts.md").read_text(encoding="utf-8")

    def test_package_remains_an_optional_unsent_draft(self):
        self.assertEqual(self.data["status"],"ALL_HOLD_UNSENT")
        self.assertEqual(self.data["canonical_master_pr"],175)
        self.assertEqual(self.data["immediate_parent_pr"],574)
        self.assertIn("NOT APPROVED",self.data["purpose"])
        self.assertFalse(self.data["operational_notes"]["founder_final_send_approval"])
        self.assertFalse(self.data["operational_notes"]["email_test_authorized"])

    def test_ratio_and_order_preserved(self):
        self.assertEqual(len(self.issues),6)
        self.assertEqual([x["number"] for x in self.issues],[1,2,3,4,5,6])
        self.assertEqual([x["number"] for x in self.issues if x["kind"]=="commercial-review-pending"],[3,5])
        self.assertEqual(sum(x["kind"]=="editorial" for x in self.issues),4)

    def test_subjects_match_canonical_manifest(self):
        canonical=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
        self.assertEqual([x["subject"] for x in self.issues],[x["subject"] for x in canonical["issues"]])

    def test_preheaders_match_canonical_subject_without_claiming_actual_control(self):
        for entry in self.issues:
            with self.subTest(issue=entry["number"]):
                self.assertLessEqual(len(entry["preheader"]),120)
                self.assertGreaterEqual(len(entry["preheader"]),32)
        self.assertIn("may not be controllable",self.memo.lower())

    def test_excerpts_are_useful_and_not_empty(self):
        for entry in self.issues:
            with self.subTest(issue=entry["number"]):
                words=entry["excerpt"].split()
                self.assertGreaterEqual(len(words),46)
                self.assertLessEqual(len(words),90)
                self.assertFalse(entry["excerpt"].endswith("..."))

    def test_commercial_disclosures_are_unambiguously_in_first_55_words(self):
        for entry in self.issues:
            if entry["kind"]=="commercial-review-pending":
                with self.subTest(issue=entry["number"]):
                    front=" ".join(entry["excerpt"].split()[:55]).lower()
                    self.assertIn("commercial note",front)
                    self.assertIn("commission",front)
                    self.assertIn("not",front)
                    self.assertIsNone(entry["cta_url"])
                    self.assertEqual(entry["cta_state"],"BLOCKED_UNPUBLISHED_UNAUTHORIZED")

    def test_no_commercial_clickable_guide(self):
        for entry in self.issues:
            if entry["kind"]=="commercial-review-pending":
                self.assertNotRegex(entry["excerpt"],r"https?://")
                self.assertIsNone(entry["cta_url"])
        self.assertNotIn("href=\"https://zen12.com",self.board)
        self.assertNotIn("href=\"https://hypnosislive.com",self.board)
        self.assertNotIn("href=\"https://affiliates.inspire3.com",self.board)

    def test_no_merchant_price_or_benefit_promise_in_excerpt(self):
        joined=" ".join(x["excerpt"].lower() for x in self.issues)
        for claim in ("$2","$24.44","$87.99","guaranteed","proven to cure","only today","clinical proof","life changing"):
            with self.subTest(claim=claim): self.assertNotIn(claim,joined)

    def test_only_first_party_editorial_urls_in_packet(self):
        for entry in self.issues:
            url=entry["cta_url"]
            if url:
                with self.subTest(issue=entry["number"]):
                    self.assertEqual(urlparse(url).hostname,"finalvestige.com")
                    self.assertEqual(entry["kind"],"editorial")

    def test_no_unverified_commercial_flags(self):
        notes=self.data["operational_notes"]
        for flag in ("merchant_permission_verified","physical_postal_address_verified","unsubscribe_in_received_email_verified","recipient_eligibility_verified","actual_received_jetpack_email_verified","founder_final_send_approval"):
            with self.subTest(flag=flag): self.assertIs(notes[flag],False)
        self.assertIs(notes["auto_send_enabled"],False)

    def test_board_is_accessible_static_reviewer_only(self):
        parser=Links()
        parser.feed(self.board)
        self.assertIn("<html lang=\"en\">",self.board)
        self.assertIn('href="#review"',self.board)
        self.assertEqual(self.board.count("<article class=\"card\">"),6)
        self.assertNotIn("<script",self.board.lower())
        self.assertNotIn("<form",self.board.lower())
        for tag,name,url in parser.hrefs:
            with self.subTest(url=url):
                self.assertNotIn("mailto:",url)
                if url.startswith("http"):
                    self.assertEqual(urlparse(url).hostname,"finalvestige.com")
        self.assertNotIn("data:",self.board.lower())

    def test_board_uses_disabled_future_guide_instead_of_fake_link(self):
        self.assertEqual(self.board.count('class="disabled"'),2)
        self.assertIn("[[VALID_POSTAL_ADDRESS_REQUIRED]]",self.board)
        self.assertIn("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]",self.board)

    def test_board_and_plaintext_repeat_exact_excerpts(self):
        for entry in self.issues:
            with self.subTest(issue=entry["number"]):
                self.assertIn(entry["excerpt"],self.txt)
                self.assertIn(entry["subject"],self.board)
                self.assertIn(entry["subject"],self.txt)

    def test_no_pii_or_active_tracking(self):
        corpus="\n".join((self.board,self.txt,self.memo,self.copy))
        for phrase in ("utm_source=","fbclid=","gclid=","pixel.gif","sendgrid","mailchimp","convertkit"):
            with self.subTest(phrase=phrase):self.assertNotIn(phrase,corpus.lower())

    def test_evidence_and_companion_owner_acknowledged(self):
        self.assertIn("Issue #171",self.memo)
        self.assertIn("Issue #174",self.memo)
        self.assertIn("https://hypnosislive.com/mental-skills/total-focus",self.memo)
        self.assertIn("https://zen12.com/hnp",self.memo)
        self.assertIn("https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business",self.memo)
        self.assertIn("HOLD_UNSENT",self.board)

    def test_separate_product_disclosures_and_buyer_blocks(self):
        self.assertIn("[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]",self.copy)
        self.assertIn("[[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]]",self.copy)
        self.assertIn("may receive a commission",self.copy)
        self.assertIn("NOT LIVE",self.issues[2]["cta_label"])
        self.assertIn("NOT LIVE",self.issues[4]["cta_label"])

    def test_snapshot_is_privacy_safe_readonly(self):
        snap=json.loads((PKG/"wordpress-readonly-snapshot.json").read_text(encoding="utf-8"))
        self.assertFalse(snap["newsletter"]["email_new_posts_by_default"])
        self.assertEqual(snap["newsletter"]["email_content_format"],"excerpt")
        self.assertEqual(snap["newsletter"]["subscribers"]["total"],2)
        self.assertEqual(snap["newsletter"]["subscribers"]["unconfirmed"],2)
        self.assertFalse(snap["newsletter"]["unique_eligible_recipients_verified"])
        self.assertIn("Read only",snap["actions_performed"])

if __name__ == "__main__":
    unittest.main()
