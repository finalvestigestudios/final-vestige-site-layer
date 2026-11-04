"""EX2 / source-native observer to free Focus regression contract.

No CMS/network writes, merchant simulation, fake lead totals or release bypass.
Runs on exact seven-chapter checkout. Does NOT establish WordPress or revenue.
"""
from __future__ import annotations
import re
import sys
import unittest
from pathlib import Path

HOME = Path(__file__).resolve().parents[1]
QA = HOME / "qa" / "release-candidate"
sys.path.insert(0, str(QA))
from write_source_flagship_playground_candidate import read_sources, compose, NAV_TARGETS

FOCUS = "https://finalvestige.com/focus/"
HISTORY = "https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"
BEGIN = '<div class="fv-hf__observer-exit" data-fv-observer-exit>'
MARKER = 'data-fv-destination="focus"'
CTA = "Explore the free 52-page Focus Fieldbook"
BRIDGE_CLASS = ".fv-hf__observer-exit-actions"


def assert_bridge(index: str, css: str) -> None:
    if index.count(BEGIN) != 1:
        raise ValueError("Native observer exit absent or duplicated")
    # Only inspect inside the authentic observer chapter, never a QA fixture.
    part = index[index.index(BEGIN):index.index("</section>", index.index(BEGIN))]
    anchors = re.findall(r"<a\\b[^>]*>", part)
    focus = [a for a in anchors if MARKER in a]
    if len(focus) != 1 or f'href="{FOCUS}"' not in focus[0]:
        raise ValueError("Native Focus CTA must be unique, untagged, and canonical")
    if f'href="{HISTORY}"' not in part:
        raise ValueError("Historical source exit lost")
    if CTA not in part or "no purchase required" not in part or "health assessment" not in part:
        raise ValueError("No clear free offer and evidence limits")
    if any(x in part.lower() for x in (
        "utm_", "onclick=", "onmouseover=", "affiliate", "inspire3",
        "buy now", "limited time", "guaranteed", "<script", "<form"
    )):
        raise ValueError("Commercial / attribution / tracking policy violation")
    if BRIDGE_CLASS not in css or "min-height:48px" not in css or "@media(forced-colors:active)" not in css:
        raise ValueError("Responsive/touch/forced-colors styling missing")
    if "prefers-reduced-motion:reduce" not in css or "@media(max-width:900px)" not in css:
        raise ValueError("Reduced motion or mobile fallback missing")
    if index.count('class="fv-hf__chapter-nav"') != 1:
        raise ValueError("Seven chapter navigation changed")
    if any(index.count('href="#' + target + '"') == 0 for target in NAV_TARGETS):
        raise ValueError("Chapter targets changed")


class NativeObserverFocusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index, cls.css, cls.js = read_sources(HOME)
        cls.observer = cls.css["observer-lab.css"]

    def test_real_unmodified_chapter_custody_and_native_bridge(self):
        assert_bridge(self.index, self.observer)
        self.assertEqual(len(self.js), 4)
        self.assertEqual(len(self.css), 6)
        self.assertIn('data-fv-observer', self.index)
        self.assertIn('id="fv-hf-observer-answer"', self.index)
        self.assertIn("Rensink, O’Regan", self.index)
        self.assertIn("Simons &amp; Levin", self.index)

    def test_native_saved_gutenberg_candidate_carries_source_change(self):
        saved, receipt = compose(self.index, self.css, self.js)
        self.assertIn(BEGIN, saved)
        self.assertEqual(saved.count(MARKER), 1)
        self.assertIn(CTA, saved)
        self.assertIn("DRAFT #150 conversion review", saved)
        self.assertIn("72 PUBLISHED MARGINS · TEST FIXTURE", saved)
        self.assertEqual(saved.count("jetpack/subscriptions"), 1)
        self.assertEqual(saved.count('class="fv-hf__chapter-nav"'), 1)
        self.assertEqual(saved.count('<script data-fv-source='), 4)
        self.assertEqual(receipt["release"], "HOLD")

    def test_fail_closed_twelve_adversarial_native_mutations(self):
        target = 'data-fv-destination="focus" href="' + FOCUS + '"'
        attacks = [
            (self.index.replace(BEGIN, '<div class="fv-hf__observer-exit">'), self.observer),
            (self.index.replace(BEGIN, BEGIN + BEGIN), self.observer),
            (self.index.replace(target, target.replace(FOCUS, "https://evil.invalid/")), self.observer),
            (self.index.replace(MARKER, ''), self.observer),
            (self.index.replace(CTA, "A resource"), self.observer),
            (self.index.replace("no purchase required", "subscribe now"), self.observer),
            (self.index.replace("health assessment", "health result"), self.observer),
            (self.index.replace(f'href="{HISTORY}"', 'href="https://evil.invalid/"'), self.observer),
            (self.index.replace(MARKER, MARKER + ' onclick="track()"'), self.observer),
            (self.index.replace(MARKER, MARKER + ' utm_content="fake_asset"'), self.observer),
            (self.index, self.observer.replace("min-height:48px", "min-height:19px")),
            (self.index, self.observer.replace("@media(forced-colors:active)", "@media(max-colors:active)"))
        ]
        for i, (markup, style) in enumerate(attacks):
            with self.subTest(mutation=i):
                with self.assertRaises(ValueError):
                    assert_bridge(markup, style)

    def test_no_duplicate_campaign_or_merchant_payloads(self):
        chapter = self.index[self.index(BEGIN):self.index("</section>", self.index(BEGIN))]
        self.assertNotRegex(chapter, r"(https?://payhip|utm_[a-z]+=|data-fv-asset-id=)")
        self.assertEqual(chapter.count(FOCUS), 1)
        self.assertEqual(chapter.count(HISTORY), 1)


if __name__ == "__main__":
    unittest.main()
