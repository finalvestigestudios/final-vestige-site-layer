"""Static, no-network QA for the R86 accessible reviewer assets (not native email)."""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1] / "r86-mime-parity"
HTML = (ROOT / "review_board.html").read_text(encoding="utf-8")
PLAIN = (ROOT / "review_board.txt").read_text(encoding="utf-8")


class Collect(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.links = []
        self.disabled = []
        self.ids = []
        self.lang = None
        self.text = []

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        self.tags.append((tag, attr))
        if tag == "html":
            self.lang = attr.get("lang")
        if "id" in attr:
            self.ids.append(attr["id"])
        if tag == "a":
            self.links.append(attr.get("href", ""))
        if "aria-disabled" in attr:
            self.disabled.append(attr.get("aria-disabled"))
    def handle_data(self, data):
        self.text.append(data)


class R86BoardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = Collect()
        cls.doc.feed(HTML)

    def test_six_separate_edition_cards(self):
        self.assertEqual(sum(t == "article" for t, a in self.doc.tags), 6)

    def test_six_honest_subjects_in_both_renditions(self):
        subjects = [
            "The person changed. The conversation went on.",
            "Before hypnosis had a name",
            "The twelve-minute question: practice before purchase",
            "Apollo 1: one spark was never the whole story",
            "A focus recording isn't proof of better focus",
            "Your focus log should include the boring days",
        ]
        for subject in subjects:
            with self.subTest(subject=subject):
                self.assertIn(subject, HTML)
                self.assertIn(subject, PLAIN)

    def test_accessible_language_skip_and_headings(self):
        self.assertEqual(self.doc.lang, "en")
        self.assertIn("#editions", self.doc.links)
        self.assertEqual(len([x for x in self.doc.tags if x[0] == "h1"]), 1)
        self.assertEqual(len([x for x in self.doc.tags if x[0] == "h2"]), 6)
        self.assertEqual(len(self.doc.ids), len(set(self.doc.ids)))

    def test_presentation_tables_and_responsive_viewport(self):
        self.assertIn('name="viewport"', HTML)
        self.assertEqual(sum(t == "table" and a.get("role") == "presentation" for t, a in self.doc.tags), 6)
        self.assertIn("@media(max-width:480px)", HTML)

    def test_every_card_is_explicitly_held(self):
        for id_ in range(1, 7):
            # The exact HTML card segment has the edition's number and HOLD wording.
            segment = HTML.split('<article class="card"')[id_].split("</article>")[0]
            self.assertIn("HOLD_UNSENT", segment)
        self.assertIn("HOLD_MERCHANT", HTML)

    def test_two_commercial_disabled_controls(self):
        self.assertEqual(self.doc.disabled, ["true", "true"])
        self.assertEqual(HTML.count('class="disclose"'), 2)
        self.assertIn("Possible future commission", HTML)
        self.assertIn("may earn a commission", HTML)

    def test_commercial_guides_have_no_active_hrefs(self):
        self.assertNotIn("zen12.com", " ".join(self.doc.links).lower())
        self.assertNotIn("hypnosislive.com", " ".join(self.doc.links).lower())
        self.assertFalse(any("/mind/zen12" in x or "/mind/hypnosis" in x for x in self.doc.links))
        self.assertFalse(any("affiliate" in x.lower() or "ref=" in x.lower() for x in self.doc.links))

    def test_only_first_party_editorial_cta_links(self):
        target_ctas = [
            "https://finalvestige.com/2026/11/02/change-blindness/",
            "https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/",
            "https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/",
            "https://finalvestige.com/focus/",
        ]
        for cta in target_ctas:
            self.assertIn(cta, self.doc.links)
            self.assertIn(cta, PLAIN)
        self.assertEqual(len([x for x in self.doc.links if x in target_ctas]), 4)

    def test_plaintext_mirror_has_exact_six_sections(self):
        self.assertEqual(len(re.findall(r"^## 0[1-6] —", PLAIN, re.M)), 6)
        self.assertEqual(PLAIN.count("**One proposed CTA — INACTIVE:**"), 2)
        self.assertIn("**NO SIGNOFF / NO SEND.**", PLAIN)

    def test_static_not_a_real_inbox_or_send_claim(self):
        for s in ("NOT native WordPress", "NOT received Jetpack email", "NOT approved"):
            # Either board or plaintext explanation must make the distinction.
            self.assertIn(s, HTML + PLAIN)
        self.assertIn("genuine received email", HTML + PLAIN)
        self.assertIn("HOLD_UNSENT", HTML)
        self.assertIn("HOLD_UNSENT", PLAIN)

    def test_disclosure_precedes_disabled_commercial_cta(self):
        for id_ in (3, 5):
            segment = HTML.split('<article class="card"')[id_].split("</article>")[0]
            self.assertLess(segment.index('class="disclose"'), segment.index('aria-disabled="true"'))

    def test_no_exfiltration_or_web_scripts(self):
        self.assertNotIn("<script", HTML.lower())
        self.assertNotIn("<form", HTML.lower())
        self.assertNotIn("mailto:", HTML.lower())
        self.assertNotIn("utm_", HTML.lower())
        self.assertNotIn("pixel", HTML.lower())
        self.assertNotIn("open tracking", HTML.lower())

    def test_no_fictional_live_mail_address_or_unsubscribe(self):
        self.assertIn("NOT included in preview cards", HTML)
        self.assertIn("functional unsubscribe", PLAIN)
        self.assertNotIn("EXAMPLE PUBLISHER MAIL STOP", HTML + PLAIN)
        self.assertNotIn("subscriptions/example-fixture", HTML + PLAIN)


if __name__ == "__main__":
    unittest.main()
