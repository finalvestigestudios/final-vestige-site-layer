"""Static release smoke checks for the public Preparedness hub snapshot.

Does not imply safety clearance of held Preparedness manuals.
"""
from html.parser import HTMLParser
from pathlib import Path
import unittest

SOURCE = Path(__file__).with_name("gateway-wordpress-1868.block.html")

class ArchiveParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.h1 = 0
        self.cards = []
        self.links = []
        self.script_types = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.append(a["id"])
        if tag == "h1":
            self.h1 += 1
        if tag == "li" and "pa-card--rich" in a.get("class", "").split():
            self.cards.append((a.get("data-track"), a.get("data-section"), a.get("data-text")))
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "script":
            self.script_types.append(a.get("type", ""))

class PublicGatewayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SOURCE.read_text(encoding="utf-8")
        cls.parser = ArchiveParser()
        cls.parser.feed(cls.text)

    def test_canonical_h1_and_unique_ids(self):
        self.assertEqual(self.parser.h1, 1)
        self.assertEqual(len(self.parser.ids), len(set(self.parser.ids)))
        self.assertIn("Old knowledge. Modern safeguards.", self.text)

    def test_balanced_source_linked_collection(self):
        self.assertEqual(len(self.parser.cards), 24)
        self.assertEqual(sum(t == "lost-ways" for t, _, _ in self.parser.cards), 18)
        self.assertEqual(sum(t == "modern" for t, _, _ in self.parser.cards), 6)
        self.assertTrue(all(section and searchable for _, section, searchable in self.parser.cards))
        for endpoint in ("nchfp.uga.edu", "www.nps.gov", "www.energy.gov", "www.cdc.gov", "www.cdph.ca.gov"):
            self.assertTrue(any(endpoint in link for link in self.parser.links), endpoint)

    def test_no_unreviewed_guides_or_unsafe_script(self):
        self.assertNotIn("/preparedness/water/making-water-safer/", self.text)
        self.assertNotIn("salt-beef-salt-pork-age-of-sail/", self.text)
        self.assertNotIn("&#038;&#038;", self.text)
        self.assertIn("groups.forEach", self.text)
        self.assertIn(".pa-curated[hidden]", self.text)
        self.assertTrue(self.text.startswith("<!-- wp:html -->"))
        self.assertTrue(self.text.rstrip().endswith("<!-- /wp:html -->"))

if __name__ == "__main__":
    unittest.main()
