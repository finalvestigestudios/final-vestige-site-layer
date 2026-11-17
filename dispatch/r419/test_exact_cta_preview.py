"""Fail-closed, non-sending checks for original-source-faithful R419 previews."""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "dispatch" / "campaign-2026-mind" / "issues"
OUT = Path(__file__).resolve().parent

class Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.scripts = 0
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.hrefs.extend(v for k, v in attrs if k == "href")
        if tag == "script":
            self.scripts += 1

class SixPreviewChecks(unittest.TestCase):
    def test_every_issue_has_exact_original_first_party_cta(self):
        names = [
            "01-the-mind-is-not-a-camera",
            "02-before-hypnosis-had-a-name",
            "03-the-twelve-minute-question",
            "04-the-hatch-and-the-spark",
            "05-before-you-press-play",
            "06-the-evidence-log",
        ]
        for num, name in enumerate(names, 1):
            with self.subTest(issue=num):
                src = (SOURCE / (name + ".md")).read_text(encoding="utf-8")
                html = (OUT / f"canonical_issue_{num:02d}.html").read_text(encoding="utf-8")
                txt = (OUT / f"canonical_issue_{num:02d}.txt").read_text(encoding="utf-8")
                original_urls = re.findall(r"\[[^\]]+\]\((https://[^\s)]+)\)", src)
                self.assertGreater(len(original_urls), 0, "vacuously green with all CTAs missing")
                self.assertTrue(all(u.startswith("https://finalvestige.com/") for u in original_urls))
                parser = Anchors()
                parser.feed(html)
                self.assertEqual(parser.hrefs, original_urls)
                self.assertEqual(parser.scripts, 0)
                self.assertIn("[[VALID_POSTAL_ADDRESS_REQUIRED]]", html)
                self.assertIn("[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]", html)
                self.assertIn("OFFLINE", txt.upper())
                self.assertNotIn("href=\"https://zen12.com", html)
                self.assertNotIn("href=\"https://hypnosislive.com", html)
                if num in (3, 5):
                    self.assertIn("INACTIVE: APPROVED_", html)
                    self.assertIn("Commercial disclosure", html)
if __name__ == "__main__":
    unittest.main()
