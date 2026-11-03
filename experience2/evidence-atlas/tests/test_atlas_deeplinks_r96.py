#!/usr/bin/env python3
"""Apollo R96: archive-source deep links remain semantic and focusable."""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "experience2/evidence-atlas/tools"
spec = importlib.util.spec_from_file_location("r94_deeplinks", TOOLS / "build_curated_atlas_r94.py")
r94 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r94)


class Fragments(HTMLParser):
    def __init__(self):
        super().__init__()
        self.articles = []
        self.jumps = []
        self.filter_hidden = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "article" and "card" in a.get("class", "").split():
            self.articles.append(a)
        if tag == "a" and a.get("href", "").startswith("#atlas-"):
            self.jumps.append(a["href"])
        if tag == "section" and a.get("id") == "filters":
            self.filter_hidden = "hidden" in a


class R96DeepLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work = tempfile.TemporaryDirectory()
        base = Path(cls.work.name)
        subprocess.run([sys.executable, str(TOOLS/"build_reciprocal_routes_r92.py"),
                        str(base/"r92")], check=True, stdout=subprocess.DEVNULL)
        subprocess.run([sys.executable, str(TOOLS/"build_source_passports_r93.py"),
                        "--src", str(base/"r92"), "--out", str(base/"r93")],
                       check=True, stdout=subprocess.DEVNULL)
        cls.out = base/"r94"
        cls.receipt = r94.build(base/"r93", cls.out)
        cls.html = (cls.out/"R94_CURATED_ATLAS.html").read_text()
        cls.js = (cls.out/"curated_atlas_r94.js").read_text()

    @classmethod
    def tearDownClass(cls):
        cls.work.cleanup()

    def test_all_six_native_targets_are_programmatically_focusable(self):
        p = Fragments()
        p.feed(self.html)
        self.assertEqual([a["id"] for a in p.articles],
                         ["atlas-%02d" % i for i in range(1, 7)])
        self.assertEqual([a.get("tabindex") for a in p.articles], ["-1"]*6)
        self.assertEqual(p.jumps, ["#atlas-%02d" % i for i in range(1, 7)])
        self.assertTrue(p.filter_hidden, "Filter enhancement must remain hidden without JS")

    def test_fragment_guard_is_explicit_and_identity_scoped(self):
        self.assertIn('^#atlas-0[1-6]$', self.js)
        self.assertIn('cards.includes(node)', self.js)
        self.assertIn('window.addEventListener("hashchange"', self.js)
        self.assertIn('requestAnimationFrame(', self.js)
        self.assertIn('node.focus({preventScroll: true})', self.js)
        self.assertIn('node.scrollIntoView({block: "start"})', self.js)

    def test_reveal_resets_both_filters_without_changing_source(self):
        self.assertIn('if (node.hidden)', self.js)
        self.assertIn('mode = "all";', self.js)
        self.assertIn('search.value = "";', self.js)
        self.assertIn('reveal(targetFor(location.hash)', self.js)
        self.assertIn('link.getAttribute("href")', self.js)

    def test_no_remote_dependencies_or_storage_added(self):
        for prohibited in ('fetch(', 'XMLHttpRequest', 'localStorage', 'sessionStorage',
                           'sendBeacon(', '<img ', '<iframe ', '<canvas '):
            self.assertNotIn(prohibited, self.js + self.html)
        self.assertEqual(self.receipt["release"], "STAGING_HOLD")
        self.assertEqual(self.receipt["photo_rights_cleared"], 0)
        self.assertEqual(self.receipt["geo_pins"], 0)
        self.assertEqual(self.receipt["inferred_edges"], 0)
        self.assertEqual(len(self.receipt["files"]), 24)

    def test_generated_js_parses_in_node(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js unavailable; Chromium CI still required")
        subprocess.run([node, "--check", str(self.out/"curated_atlas_r94.js")],
                       check=True, capture_output=True)


if __name__ == "__main__":
    unittest.main()
