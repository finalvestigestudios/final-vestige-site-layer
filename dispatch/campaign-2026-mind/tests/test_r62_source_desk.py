"""R62: verify original source desk is explicit, conservative and unsendable.

These source-level guards are NOT substitutes for a delivered Jetpack message or legal review.
"""
import json
import pathlib
import re
import unittest
from html.parser import HTMLParser
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
PKG = ROOT / "r62-source-desk"

class MiniHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.tags = []
        self.lang = None

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        d = dict(attrs)
        if tag == "html":
            self.lang = d.get("lang")
        if tag == "a":
            self.links.append(d.get("href", ""))


class SourceDeskGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((PKG / "verified_status.json").read_text(encoding="utf-8"))
        cls.crosswalk = (PKG / "source_crosswalk.md").read_text(encoding="utf-8")
        cls.passages = (PKG / "editorial_passages.md").read_text(encoding="utf-8")
        cls.email_html = (PKG / "issue04-offline-email.html").read_text(encoding="utf-8")
        cls.email_text = (PKG / "issue04-offline-email.txt").read_text(encoding="utf-8")
        cls.parser = MiniHTMLParser()
        cls.parser.feed(cls.email_html)

    def test_six_entries(self):
        self.assertEqual([i["number"] for i in self.report["issues"]], [1, 2, 3, 4, 5, 6])

    def test_preserves_editorial_commercial_mix(self):
        types = [i["type"] for i in self.report["issues"]]
        self.assertEqual(types.count("editorial"), 4)
        self.assertEqual(types.count("commercial-review-pending"), 2)

    def test_named_commercial_position_unchanged(self):
        self.assertEqual([i["number"] for i in self.report["issues"] if i["type"].startswith("commercial")], [3, 5])

    def test_all_six_release_states_hold(self):
        self.assertTrue(all(i["release"].startswith("HOLD_UNSENT") for i in self.report["issues"]))

    def test_two_offers_blocked(self):
        for i in (self.report["issues"][2], self.report["issues"][4]):
            self.assertIsNone(i["cta"])
            self.assertIsNone(i["wordpress_id"])
            self.assertEqual(i["cta_status"], "BLOCKED_GUIDE_NOT_LIVE_OR_AUTHORIZED")
            self.assertIn("HOLD_MERCHANT", i["release"])

    def test_editorial_first_party_destinations(self):
        for i in self.report["issues"]:
            if i["type"] != "editorial":
                continue
            self.assertEqual(urlparse(i["cta"]).hostname, "finalvestige.com")
            self.assertIsInstance(i["wordpress_id"], int)
            self.assertEqual(i["cta_status"], "PUBLISHED_FIRST_PARTY")

    def test_snapshot_auto_send_is_off(self):
        self.assertFalse(self.report["live_readonly"]["new_post_auto_email"])
        self.assertEqual(self.report["live_readonly"]["email_format"], "excerpt")

    def test_welcome_delivery_is_not_claimed(self):
        self.assertTrue(self.report["live_readonly"]["welcome_fieldbook_configured"])
        self.assertFalse(self.report["live_readonly"]["welcome_received_verified"])

    def test_subscriber_totals_are_nonadditive(self):
        s = self.report["live_readonly"]
        self.assertEqual((s["subscriber_total_reported"], s["subscriber_confirmed_reported"], s["subscriber_unconfirmed_reported"]), (2, 2, 2))
        self.assertFalse(s["subscriber_buckets_additive"])
        self.assertFalse(s["unique_eligible_recipients_verified"])

    def test_no_permission_attested(self):
        self.assertTrue(all(v is False for v in self.report["hard_gates"].values()))

    def test_no_unverified_performance_measurements(self):
        self.assertIn("No audience number", self.report["no_claims"])
        self.assertFalse(self.report["live_readonly"]["lifetime_sends_verified"])

    def test_source_notes_cover_four_editorial_issues(self):
        for heading in ("01 —", "02 —", "04 —", "06 —"):
            self.assertIn(heading, self.crosswalk)

    def test_vendor_approval_separately_blocked(self):
        self.assertIn("EMAIL", self.crosswalk)
        self.assertIn("Zen12", self.crosswalk)
        self.assertIn("Total Focus", self.crosswalk)

    def test_nasa_timings_are_explained(self):
        for item in ("17.1 seconds", "10.3 seconds", "6.8-second"):
            self.assertIn(item, self.crosswalk)
        self.assertIn("17.1-second", self.passages)

    def test_puysegur_original_date_caveat(self):
        self.assertIn("not yet independently verified", self.crosswalk)
        self.assertIn("May 4", self.passages)

    def test_stone_wider_time_window(self):
        for item in ("90%", "11%", "20%"):
            self.assertIn(item, self.crosswalk)

    def test_passages_are_optional(self):
        self.assertIn("not canonical", self.passages.lower())
        self.assertIn("NOT authorized substitutions", self.passages)

    def test_html_declares_language_and_title(self):
        self.assertEqual(self.parser.lang, "en")
        self.assertIn("<h1", self.email_html.lower())
        self.assertIn("<title>", self.email_html)

    def test_html_is_email_safe_and_inert(self):
        banned = {"script", "form", "iframe", "object", "embed", "video", "audio", "img"}
        self.assertFalse(banned.intersection(self.parser.tags))
        self.assertNotIn("tracking-pixel", self.email_html.lower())
        self.assertNotIn("utm_", self.email_html.lower())

    def test_email_table_avoids_fixed_640_pixel_width(self):
        self.assertNotIn('width="640"', self.email_html)
        self.assertIn('max-width:640px;width:100%', self.email_html)

    def test_html_has_only_one_first_party_link(self):
        links = [urlparse(x) for x in self.parser.links]
        self.assertEqual(sum(x.hostname == "finalvestige.com" for x in links), 1)
        self.assertEqual(len(self.parser.links), 3)

    def test_html_has_no_merchant_destinations(self):
        self.assertFalse(any(("zen12" in x.lower() or "hypnosislive" in x.lower() or "inspire3" in x.lower()) for x in self.parser.links))

    def test_two_previews_contain_primary_facts(self):
        for content in (self.email_html, self.email_text):
            for fact in ("17.1", "10.3", "6.8", "23:31:04.7", "23:31:21.8"):
                self.assertIn(fact, content)

    def test_previews_have_explicit_unresolved_postal_and_unsubscribe(self):
        for content in (self.email_html, self.email_text):
            self.assertIn("[[VALID_POSTAL_ADDRESS_REQUIRED]]", content)
            self.assertIn("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]", content)

    def test_preview_never_masquerades_as_received_email(self):
        self.assertIn("REVIEW ONLY", self.email_html)
        self.assertIn("not a real jetpack rendering", self.email_html.lower())
        self.assertIn("DO NOT SEND", self.email_text)

    def test_original_canonical_titles_unchanged(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual([i["subject"] for i in manifest["issues"]], [i["subject"] for i in self.report["issues"]])
        self.assertEqual(manifest["status"], "DRAFT_UNSENT_NO_SCHEDULING")

    def test_no_active_affiliate_url_in_canonical(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(all(i["merchant_affiliate_url"] is None for i in manifest["issues"]))

    def test_reference_only_previous_prs(self):
        self.assertEqual(self.report["canonical_master_pr"], 175)
        self.assertEqual(self.report["parent_dispatch_pr"], 581)
        self.assertEqual(self.report["prior_quality_pr"], 201)

if __name__ == "__main__":
    unittest.main()
