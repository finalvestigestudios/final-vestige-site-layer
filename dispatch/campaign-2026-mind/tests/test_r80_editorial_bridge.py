"""R80 optional editorial archive/transport review; NEVER authorizes sending."""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PACK = ROOT / "r80-editorial-bridge"
SRC = PACK / "SOURCE-AND-RELEASE.json"


class EditorialBridgeR80(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads(SRC.read_text(encoding="utf-8"))
        cls.issues = {it["number"]: (PACK / it["file"]).read_text(encoding="utf-8")
                      for it in cls.ledger["issues"]}
        cls.html = (PACK / "REVIEWER.html").read_text(encoding="utf-8")
        cls.plain = (PACK / "REVIEWER.txt").read_text(encoding="utf-8")
        cls.audit = (PACK / "EXCERPT-AND-COPY-AUDIT.md").read_text(encoding="utf-8")

    def test_exact_editorial_edition_set(self):
        self.assertEqual(set(self.issues), {1, 2, 6})

    def test_master_allocation_not_changed(self):
        self.assertEqual(self.ledger["campaign_mix_original"]["editorial"], [1, 2, 4, 6])
        self.assertEqual(self.ledger["campaign_mix_original"]["commercial_reserved"], [3, 5])

    def test_all_commercial_and_send_gates_closed(self):
        self.assertFalse(self.ledger["replacements_approved"])
        self.assertFalse(self.ledger["newsletter_send_approved"])
        self.assertFalse(self.ledger["merchant_email_rights_verified"])
        self.assertFalse(self.ledger["commercial_guides_approved_and_live"])
        self.assertFalse(self.ledger["publisher_address_verified"])
        self.assertFalse(self.ledger["rendered_unsubscribe_verified"])
        self.assertFalse(self.ledger["received_email_verified"])
        self.assertFalse(any(self.ledger["release_gates_all_false"].values()))

    def test_all_explicit_hold(self):
        self.assertEqual(self.ledger["status"], "HOLD_UNSENT")
        for body in self.issues.values():
            self.assertIn("STATUS: HOLD_UNSENT", body)
            self.assertIn("Not approved to replace master PR #175", body)

    def test_all_three_original_sources_long_form(self):
        for body in self.issues.values():
            self.assertGreaterEqual(len(body.split()), 450)

    def test_subjects_match_source_manifest_and_reviewer(self):
        for n, body in self.issues.items():
            item = next(i for i in self.ledger["issues"] if i["number"] == n)
            self.assertIn("SUBJECT: " + item["subject"], body)
            self.assertIn(item["subject"], self.html)
            self.assertIn(item["subject"], self.plain)

    def test_preheaders_disclaimed_not_transport_claim(self):
        for body in self.issues.values():
            self.assertIn("NOT VERIFIED AS JETPACK FEATURE", body)
        self.assertFalse(self.ledger["custom_preheader_control_verified"])

    def test_custom_excerpts_readable_and_short(self):
        for body in self.issues.values():
            excerpt = re.search(r"^PROPOSED CUSTOM EXCERPT[^\n]*?: (.*)$", body, re.M)
            self.assertIsNotNone(excerpt)
            self.assertGreaterEqual(len(excerpt.group(1).split()), 35)
            self.assertLessEqual(len(excerpt.group(1).split()), 55)
            self.assertIn("NOT A RECEIVED EMAIL", body)

    def test_one_content_cta_each(self):
        for n, body in self.issues.items():
            hits = re.findall(r"^\*\*One next step\b[^\n]*", body, re.M)
            self.assertEqual(len(hits), 1, n)
            item = next(i for i in self.ledger["issues"] if i["number"] == n)
            self.assertIn(item["cta"], hits[0])

    def test_evidence_citations_present_in_full_body(self):
        for n, body in self.issues.items():
            item = next(i for i in self.ledger["issues"] if i["number"] == n)
            for source in item["evidence"]:
                self.assertIn(source, body, (n, source))
            self.assertIn("**Sources and further reading**", body)

    def test_no_earning_urls_in_editorial_text(self):
        for body in self.issues.values():
            for banned in ("href=\"https://zen12", "https://zen12.com/hnp",
                           "https://hypnosislive.com/mental-skills/total-focus",
                           "affiliates.inspire3.com", "utm_source=", "bit.ly/"):
                self.assertNotIn(banned, body)

    def test_legal_placeholders_remain_hard_stops(self):
        for body in self.issues.values():
            self.assertIn("[[VALID_POSTAL_ADDRESS_REQUIRED]]", body)
            self.assertIn("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]", body)

    def test_issue_01_does_not_generalize_population(self):
        body = self.issues[1]
        self.assertIn("only about half", body)
        self.assertIn("does not mean half of all people", body)
        self.assertIn("https://doi.org/10.3758/BF03208840", body)

    def test_issue_02_distinguishes_event_report_and_print(self):
        body = self.issues[2]
        for phrase in ("May 4, 1784", "May 8", "1784–1785",
                       "does **not** prove", "catalogue.bnf.fr"):
            self.assertIn(phrase, body)

    def test_issue_06_no_testimonial_or_medical_efficacy(self):
        body = self.issues[6]
        self.assertIn("including zero", body)
        self.assertIn("not a diagnosis", body)
        self.assertIn("subjective log cannot diagnose", body)

    def test_wordpress_snapshot_counters_not_added(self):
        snap = self.ledger["cms_snapshot"]
        self.assertEqual(snap["subscriber_diagnostics"], {"total": 2, "confirmed": 2, "unconfirmed": 2})
        self.assertEqual(snap["separate_followers"]["email"], 0)
        self.assertEqual(snap["separate_followers"]["wpcom"], 2)
        self.assertEqual(snap["actual_eligible_recipients"], "UNKNOWN")
        self.assertFalse(snap["automatic_new_post_email"])

    def test_email_review_board_is_accessible_static(self):
        html = self.html
        for token in ('<!doctype html>', 'lang="en"', 'name="viewport"', 'class="skip"',
                      'aria-label="Issue reviewer navigation"', 'role="presentation"',
                      'id="issue-01"', 'id="issue-02"', 'id="issue-06"'):
            self.assertIn(token, html)
        for banned in ("<script", "<iframe", "<form", "<img", "utm_", "track.gif"):
            self.assertNotIn(banned, html.lower())

    def test_review_html_has_no_active_merchant_anchors(self):
        self.assertNotRegex(self.html, r'href="https?://(?:www\.)?(?:zen12|hypnosislive|inspire3)\.')

    def test_plaintext_contains_full_editions_and_source_urls(self):
        for body in self.issues.values():
            self.assertIn(body.split("\n")[3], self.plain)
        self.assertIn("https://doi.org/10.3758/BF03208840", self.plain)
        self.assertIn("HOLD_UNSENT", self.plain)

    def test_excerpt_ambiguity_is_documented(self):
        for token in ("55-word", "350-character", "custom excerpt",
                      "NOT delivery results", "HOLD_UNSENT"):
            self.assertIn(token, self.audit)

    def test_merchant_issues_remain_independently_blocked(self):
        seller = self.ledger["official_sales_alignment_notes"]
        self.assertIn("MERCHANT ASSERTION", seller["zen12"]["editorial_position"])
        self.assertIn("NOT established", seller["total_focus"]["editorial_position"])
        self.assertFalse(self.ledger["merchant_email_rights_verified"])


if __name__ == "__main__":
    unittest.main()
