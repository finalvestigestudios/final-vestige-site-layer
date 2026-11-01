"""R42: adversarial, offline source-first checks for OPTIONAL Apollo 1 email candidate.

This suite does not make network calls, WordPress changes or send any email.
Passing tests are never release authorization.
"""
from __future__ import annotations

import json
import pathlib
import re
import unittest
from html.parser import HTMLParser
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIR = ROOT / "r42-apollo-precision"
ARTICLE = "https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"
NASA = "https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/"
NASA_SUMMARY = "https://www.nasa.gov/missions/apollo/apollo-1/apollo-204-review-board-summary/"
POSTAL = "[[VALID_POSTAL_ADDRESS_REQUIRED]]"
UNSUB = "[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"
SUBJECT = "The spark NASA could not name"
PREHEADER = "Apollo 1's investigators couldn't identify one proven ignition wire. They identified six dangerous conditions."


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.tags = []
        self.media = []
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        vals = dict(attrs)
        if tag == "a":
            self.hrefs.append(vals.get("href"))
        if tag in ("script", "iframe", "img", "form", "video", "audio"):
            self.media.append(tag)


def parsed_html(value: str) -> Links:
    v = Links()
    v.feed(value)
    return v


def candidate_gate(markdown: str, plain: str, html: str, blocks: str, ledger: dict) -> bool:
    """Fails closed on loss of postal placeholders, proof or trusted CTA."""
    if any(POSTAL not in s or UNSUB not in s for s in (markdown, plain, html, blocks)):
        return False
    if any("UNSENT" not in s for s in (markdown, plain, html, blocks)):
        return False
    if any(SUBJECT not in s or PREHEADER not in s for s in (markdown, plain, html)):
        return False
    if ledger.get("status") != "UNSENT_OPTIONAL_REVIEW":
        return False
    if ledger.get("edition") != 4 or ledger.get("canonical_issue_04_unchanged") is not True:
        return False
    if ledger.get("founder_approved_replacement") is not False:
        return False
    if ledger.get("mix") != {"editorial": 4, "commercial_reserved": 2}:
        return False
    if ledger.get("primary_cta") != ARTICLE or ledger.get("affiliate_urls") != []:
        return False
    keys = (
        "email_promotion_permissions_verified", "postal_address_verified",
        "unsubscribe_delivered_verified", "subscriber_eligibility_verified",
        "founder_final_send_approval"
    )
    if any(ledger.get(k) is not False for k in keys):
        return False
    for s in (markdown, plain, html, blocks):
        if not all(n in s for n in ("23:31:04.7", "23:31:19", "16.7", "29 psia")):
            return False
        if not all(n in s.lower() for n in ("six conditions", "not the full duration of the fire")):
            return False
        if any(u in s.lower() for u in ("zen12.com", "hypnosislive.com", "inspire3.com", "affiliates.inspire3.com")):
            return False
    lh = parsed_html(html)
    lb = parsed_html(blocks)
    if lh.media or lb.media:
        return False
    if sorted(lh.hrefs) != sorted([ARTICLE, NASA, NASA_SUMMARY]):
        return False
    if sorted(lb.hrefs) != sorted([ARTICLE, NASA, NASA_SUMMARY]):
        return False
    if markdown.count("](") != 3:
        return False
    if any(plain.count(u) != 1 for u in (ARTICLE, NASA, NASA_SUMMARY)):
        return False
    return True


class ApolloProof(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.md = (DIR / "ISSUE_04_REVIEW_CANDIDATE.md").read_text(encoding="utf-8")
        cls.plain = (DIR / "ISSUE_04_REVIEW_CANDIDATE.txt").read_text(encoding="utf-8")
        cls.html = (DIR / "ISSUE_04_REVIEW_CANDIDATE.html").read_text(encoding="utf-8")
        cls.blocks = (DIR / "ISSUE_04_REVIEW_CANDIDATE.blocks.html").read_text(encoding="utf-8")
        cls.ledger = json.loads((DIR / "CLAIM_REGISTER.json").read_text(encoding="utf-8"))
        cls.readme = (DIR / "README.md").read_text(encoding="utf-8")

    def test_optional_release_gate_passes_as_hold(self):
        self.assertTrue(candidate_gate(self.md, self.plain, self.html, self.blocks, self.ledger))

    def test_original_campaign_manifest_is_untouched(self):
        m = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(m["status"], "DRAFT_UNSENT_NO_SCHEDULING")
        self.assertEqual([x["kind"] for x in m["issues"]].count("editorial"), 4)
        self.assertEqual([x["kind"] for x in m["issues"]].count("commercial-review-pending"), 2)
        self.assertEqual(m["issues"][3]["subject"], "Seventeen seconds. A much longer explanation.")
        self.assertEqual(m["issues"][3]["editorial_cta"], ARTICLE)

    def test_canonical_fourth_issue_not_rewritten(self):
        canonical = (ROOT / "issues" / "04-the-hatch-and-the-spark.md").read_text(encoding="utf-8")
        self.assertIn("Seventeen seconds. A much longer explanation.", canonical)
        self.assertIn("UNSENT DRAFT", canonical)
        self.assertNotIn(SUBJECT, canonical)

    def test_story_is_substantive(self):
        main = self.md.split("---", 1)[1].split("**ONE READER ACTION", 1)[0]
        self.assertGreaterEqual(len(main.split()), 600)
        self.assertLess(len(main.split()), 1100)

    def test_subject_lengths_and_accuracy(self):
        self.assertLessEqual(len(SUBJECT), 65)
        self.assertLessEqual(len(PREHEADER), 115)
        self.assertNotIn("proven cure", SUBJECT.lower())
        self.assertIn("could not name", SUBJECT)

    def test_native_preheader_not_implicitly_claimed(self):
        self.assertIn("Jetpack custom preheader unverified", self.md)
        self.assertIn("not verified in Jetpack", self.plain)
        self.assertIn("custom preheader support not established", self.readme)

    def test_preheader_is_display_hidden_in_html(self):
        self.assertIn('aria-hidden="true"', self.html)
        self.assertIn("max-height:0", self.html)

    def test_html_is_email_safe_without_external_assets(self):
        p = parsed_html(self.html)
        self.assertFalse(p.media)
        self.assertEqual(self.html.count('role="presentation"'), 2)
        self.assertIn('<html lang="en">', self.html)
        self.assertIn('name="viewport"', self.html)
        self.assertNotIn("onload=", self.html.lower())
        self.assertNotIn("<style", self.html.lower())

    def test_html_links_are_only_one_cta_and_two_sources(self):
        self.assertEqual(parsed_html(self.html).hrefs, [ARTICLE, NASA, NASA_SUMMARY])

    def test_gutenberg_links_are_only_one_cta_and_two_sources(self):
        self.assertEqual(parsed_html(self.blocks).hrefs, [ARTICLE, NASA, NASA_SUMMARY])

    def test_html_uses_accessible_link_contrast_not_image_cta(self):
        self.assertIn("color:#fff", self.html)
        self.assertIn("Read The Hatch Opened Inward", self.html)
        self.assertNotIn("<img", self.html.lower())

    def test_all_formats_have_exact_research_time_markers(self):
        for s in (self.md, self.plain, self.html, self.blocks):
            with self.subTest(format=s[:25]):
                for token in ("23:31:04.7", "23:31:19", "16.7", "29 psia"):
                    self.assertIn(token, s)

    def test_unknown_first_ignition_and_sequence_not_conflated(self):
        for s in (self.md, self.plain, self.html, self.blocks):
            self.assertIn("not the full duration of the fire", s)
            self.assertIn("could not conclusively identify a single ignition source", s)

    def test_death_not_reduced_to_fourteen_seconds(self):
        self.assertNotIn("died in fourteen seconds", self.md.lower())
        self.assertNotIn("fire lasted fourteen seconds", self.md.lower())
        self.assertIn("approximately fifteen seconds", self.md)

    def test_historical_six_condition_list(self):
        for x in ("sealed oxygen-pressurized cabin", "combustible materials", "electrical wiring",
                  "coolant plumbing", "means of escape", "rescue or medical assistance"):
            self.assertIn(x, self.md)

    def test_authoritative_source_register_is_specific(self):
        claims = self.ledger["claims"]
        self.assertGreaterEqual(len(claims), 8)
        self.assertTrue(all("claim" in c and "type" in c and "qualification" in c and "source" in c for c in claims))
        self.assertTrue(any(c["type"] == "Board finding" for c in claims))
        self.assertIn("NASA", self.readme)

    def test_citations_are_noncommercial_and_precise(self):
        for s in (self.md, self.plain, self.html, self.blocks):
            self.assertIn(NASA, s)
            self.assertIn(NASA_SUMMARY, s)
            self.assertIn(ARTICLE, s)
            self.assertNotIn("zen12.com", s.lower())
            self.assertNotIn("hypnosislive.com", s.lower())

    def test_markdown_one_action(self):
        self.assertEqual(self.md.count("**ONE READER ACTION"), 1)
        self.assertEqual(self.md.count("]("), 3)

    def test_plaintext_single_action_and_urls(self):
        self.assertEqual(self.plain.count("ONE READER ACTION"), 1)
        self.assertTrue(all(self.plain.count(u) == 1 for u in (ARTICLE, NASA, NASA_SUMMARY)))

    def test_rendered_footer_is_not_falsely_verified(self):
        self.assertFalse(self.ledger["postal_address_verified"])
        self.assertFalse(self.ledger["unsubscribe_delivered_verified"])
        self.assertFalse(self.ledger["founder_final_send_approval"])

    def test_refuse_missing_postal(self):
        self.assertFalse(candidate_gate(self.md.replace(POSTAL, "123 Fake Street"), self.plain, self.html, self.blocks, self.ledger))

    def test_refuse_missing_unsubscribe(self):
        self.assertFalse(candidate_gate(self.md, self.plain.replace(UNSUB, "UNSUB SENT"), self.html, self.blocks, self.ledger))

    def test_refuse_accidental_live_release(self):
        mutated = dict(self.ledger, status="SEND_APPROVED")
        self.assertFalse(candidate_gate(self.md, self.plain, self.html, self.blocks, mutated))

    def test_refuse_fake_founder_approval(self):
        mutated = dict(self.ledger, founder_final_send_approval=True)
        self.assertFalse(candidate_gate(self.md, self.plain, self.html, self.blocks, mutated))

    def test_refuse_fake_list_consent(self):
        mutated = dict(self.ledger, subscriber_eligibility_verified=True)
        self.assertFalse(candidate_gate(self.md, self.plain, self.html, self.blocks, mutated))

    def test_refuse_merchant_link_inserted(self):
        bad = self.html.replace('href="' + ARTICLE + '"', 'href="https://zen12.com/hnp"')
        self.assertFalse(candidate_gate(self.md, self.plain, bad, self.blocks, self.ledger))

    def test_refuse_hidden_second_cta(self):
        bad = self.html.replace("</body>", '<a href="https://other.example/">Buy</a></body>')
        self.assertFalse(candidate_gate(self.md, self.plain, bad, self.blocks, self.ledger))

    def test_refuse_tracking_script(self):
        bad = self.html.replace("</body>", "<script>alert(1)</script></body>")
        self.assertFalse(candidate_gate(self.md, self.plain, bad, self.blocks, self.ledger))

    def test_refuse_loss_of_ignition_qualification(self):
        bad = self.plain.replace("not the full duration of the fire", "the entire fire duration")
        self.assertFalse(candidate_gate(self.md, bad, self.html, self.blocks, self.ledger))

    def test_refuse_unapproved_merchant_earning_link(self):
        mutated = dict(self.ledger, affiliate_urls=["https://merchant.example/?ref=example"])
        self.assertFalse(candidate_gate(self.md, self.plain, self.html, self.blocks, mutated))

    def test_refuse_noncanonical_mix(self):
        mutated = dict(self.ledger, mix={"editorial": 5, "commercial_reserved": 1})
        self.assertFalse(candidate_gate(self.md, self.plain, self.html, self.blocks, mutated))

    def test_no_recipient_data_in_review_assets(self):
        for s in (self.md, self.plain, self.html, self.blocks, self.readme):
            self.assertIsNone(re.search(r"[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+\\.[A-Za-z]{2,}", s))
            self.assertNotIn("newsletter subscriber email:", s.lower())


if __name__ == "__main__":
    unittest.main()
