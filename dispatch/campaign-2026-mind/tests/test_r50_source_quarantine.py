"""R50 review-only commercial source-citation quarantine: canonical originals untouched."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unittest
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "r50-commercial-source-quarantine"
REGISTRY = json.loads((PACK / "source_registry.json").read_text(encoding="utf-8"))
SOURCE = (ROOT / "issues" / "03-the-twelve-minute-question.md").read_text(encoding="utf-8")
MARKDOWN = (PACK / "issue03-proposed.md").read_text(encoding="utf-8")
PLAINTEXT = (PACK / "issue03-proposed.txt").read_text(encoding="utf-8")
HTML = (PACK / "issue03-proposed.html").read_text(encoding="utf-8")
MERCHANTS = ("zen12.com", "hypnosislive.com", "inspire3.com")

class Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() in ("a", "area"):
            self.urls += [v for k, v in attrs if k.lower() == "href" and v]

def git_blob_sha(s):
    b = s.encode("utf-8")
    return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()

def links_markdown(s):
    return re.findall(r"\[[^\]]+\]\((https?://[^)]+)\)", s)

def is_merchant(url):
    host = (urlsplit(url).hostname or "").lower()
    return any(host == d or host.endswith("." + d) for d in MERCHANTS)

class R50SourceQuarantine(unittest.TestCase):
    def test_original_canonical_blob_unchanged(self):
        self.assertEqual(git_blob_sha(SOURCE), REGISTRY["canonical_issue03_blob"])

    def test_two_and_only_two_local_source_transformations(self):
        replacements = REGISTRY["only_source_changes"]
        self.assertEqual(len(replacements), 2)
        expected = SOURCE
        for item in replacements:
            self.assertEqual(expected.count(item["before"]), 1)
            expected = expected.replace(item["before"], item["after"])
        self.assertEqual(MARKDOWN, expected)

    def test_original_routes_still_present_in_canonical_only(self):
        self.assertEqual(sum(is_merchant(u) for u in links_markdown(SOURCE)), 2)
        self.assertEqual(sum(is_merchant(u) for u in links_markdown(MARKDOWN)), 0)

    def test_no_merchant_url_in_proposed_reader_formats(self):
        for label, s in [("markdown", MARKDOWN), ("plaintext", PLAINTEXT), ("html", HTML)]:
            with self.subTest(label=label):
                self.assertNotRegex(s.lower(), r"https?://(?:[a-z0-9-]+\.)*(?:zen12|hypnosislive|inspire3)\.com")

    def test_rendered_html_no_merchants_in_actual_anchors(self):
        reader = Anchors()
        reader.feed(HTML)
        reader.close()
        self.assertGreaterEqual(len(reader.urls), 1)
        self.assertFalse(any(is_merchant(url) for url in reader.urls))
        self.assertFalse(any("APPROVED_ZEN12" in url for url in reader.urls))

    def test_zero_active_affiliate_paths_or_instrumentation(self):
        for payload in (MARKDOWN, PLAINTEXT, HTML):
            for bad in ("utm_source=", "fbclid=", "gclid=", "affiliate_id=", "ref_id=", "<script", "<form"):
                self.assertNotIn(bad, payload.lower())

    def test_exact_subject_preheader_from_canonical(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        issue = manifest["issues"][2]
        self.assertIn(issue["subject"], MARKDOWN)
        self.assertIn(issue["preheader"], MARKDOWN)
        self.assertIn(issue["subject"], HTML)
        self.assertEqual(issue["publish_state"], "hold")
        self.assertIsNone(issue["merchant_affiliate_url"])

    def test_original_4_to_2_all_holds(self):
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["mix"], {"editorial": 4, "commercial_review_pending": 2})
        self.assertEqual(len(manifest["issues"]), 6)
        self.assertTrue(all(x["publish_state"] == "hold" for x in manifest["issues"]))

    def test_legal_placeholders_remain_explicit(self):
        for payload in (MARKDOWN, PLAINTEXT, HTML):
            for token in ("[[VALID_POSTAL_ADDRESS_REQUIRED]]",
                          "[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]",
                          "[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]"):
                self.assertIn(token, payload)

    def test_html_preview_keeps_terminal_footer_not_just_a_separator(self):
        # Prevent the first hosted-run regression: a renderer saw a separator
        # and incorrectly discarded the rest of the legal footer paragraph.
        self.assertIn("Pre-send compliance block", HTML)
        self.assertIn("Sender: Final Vestige Studios", HTML)
        self.assertIn("These placeholders intentionally prevent sending.", HTML)
        self.assertIn("[[VALID_POSTAL_ADDRESS_REQUIRED]]", HTML)
        self.assertIn("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]", HTML)

    def test_commission_disclosure_before_inactive_guide_cta(self):
        for payload in (MARKDOWN, PLAINTEXT, HTML):
            self.assertIn("Commercial disclosure", payload)
            self.assertLess(payload.index("Commercial disclosure"),
                            payload.index("APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED"))

    def test_official_citations_preserved_in_internal_registry(self):
        urls = REGISTRY["official_source_urls_internal_only"]
        self.assertIn("https://zen12.com/hnp", urls)
        self.assertIn("https://zen12.com/about", urls)
        self.assertIn("https://hypnosislive.com/mental-skills/total-focus", urls)

    def test_proposed_custom_excerpts_disclose_early(self):
        for number in ("03", "05"):
            s = REGISTRY["proposed_jetpack_custom_excerpts"][number]
            self.assertNotRegex(s, r"https?://")
            self.assertIn("commission", s.lower())
            self.assertTrue("not live" in s.lower())
            self.assertLess(s.lower().index("commission"), 55 * 12)
            self.assertLessEqual(len(s.split()), 75)

    def test_proposed_excerpts_explicitly_uninstalled(self):
        self.assertEqual(REGISTRY["status"], "UNSENT_REVIEW_ONLY")
        self.assertFalse(REGISTRY["preview_assertions"]["received_mime_verified"])
        self.assertFalse(REGISTRY["preview_assertions"]["founder_final_approval"])
        self.assertFalse(REGISTRY["preview_assertions"]["commercial_guides_live"])
        self.assertFalse(REGISTRY["preview_assertions"]["merchant_email_permission_verified"])

    def test_html_is_static_non_actionable_review_with_language(self):
        self.assertIn('lang="en"', HTML)
        self.assertIn("INTERNAL UNSENT REVIEW", HTML)
        self.assertIn("NOT A WORDPRESS OR RECEIVED JETPACK EMAIL", HTML)
        self.assertIn('role="presentation"', HTML)
        self.assertNotIn("javascript:", HTML.lower())

    def test_plaintext_preserves_claim_skepticism(self):
        for clause in ("twelve minutes", "zen12", "not active", "NIH", "Commercial disclosure"):
            self.assertIn(clause.lower(), PLAINTEXT.lower())

    def test_canonical_issue_five_also_remains_unmodified(self):
        src = (ROOT / "issues" / "05-before-you-press-play.md").read_text(encoding="utf-8")
        self.assertEqual(sum(is_merchant(u) for u in links_markdown(src)), 0)
        self.assertIn("APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED", src)

    def test_no_release_authority_in_registry(self):
        self.assertIn("ALL_ISSUES_HOLD_UNSENT", REGISTRY["holds"])
        self.assertIn("ISSUES_03_AND_05_HOLD_MERCHANT", REGISTRY["holds"])
        for flag in REGISTRY["preview_assertions"].values():
            if isinstance(flag, bool):
                self.assertFalse(flag)

if __name__ == "__main__":
    unittest.main()
