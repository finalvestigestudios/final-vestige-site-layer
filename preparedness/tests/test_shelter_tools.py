"""Static, privacy and security checks for the Shelter, Power and Family Communication tools.
The real-browser checks are in test_shelter_tools_browser.py; the logic assertions are in test_shelter_tools.js."""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402

SLUGS = ["home-fire-escape-worksheet", "power-outage-planner", "reunification-plan"]
JS_MODULES = ["shelter_common.js", "fire_worksheet.js", "outage_items.js", "reunion_card.js"]
BANNED_API = ("localStorage", "sessionStorage", "indexedDB", "document.cookie", "fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket",
              "navigator.", "import(", "eval(", "new Function", "document.write", "innerHTML", "outerHTML", "insertAdjacentHTML", "postMessage", "window.open", "location.href", "location.assign")


class ShelterToolStaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = build.Library()
        cls.built = {s: build.build_article(cls.lib, s)["inner"] for s in SLUGS}

    def test_logic_unit_tests_pass_in_node(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node not installed")
        r = subprocess.run([node, str(ROOT / "tests" / "test_shelter_tools.js")], capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_generated_pages_are_current(self):
        if not shutil.which("node"):
            self.skipTest("node not installed")
        r = subprocess.run([sys.executable, "-I", str(ROOT / "tools" / "gen_shelter_tools.py"), "--check"], capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr + "\nRun: python -I preparedness/tools/gen_shelter_tools.py")

    def test_modules_use_no_storage_network_or_html_injection_apis(self):
        for name in JS_MODULES:
            src = (ROOT / "tools" / name).read_text(encoding="utf-8")
            code = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
            for banned in BANNED_API:
                self.assertNotIn(banned, code, f"{name} must not use {banned}")

    def test_built_page_scripts_use_no_storage_network_or_html_injection_apis(self):
        for slug, page in self.built.items():
            script = "\n".join(re.findall(r"<script>(.*?)</script>", page, flags=re.S))
            self.assertTrue(script, slug)
            code = re.sub(r"/\*.*?\*/", "", script, flags=re.S)
            for banned in BANNED_API:
                self.assertNotIn(banned, code, f"{slug}: page script must not use {banned}")
            self.assertNotRegex(page, r"<form[^>]+(action|method)=")
            self.assertIn('onsubmit="return false"', page)
            self.assertNotRegex(page, r"<(iframe|embed|object|link rel=\"stylesheet\"|img)\b")
            self.assertNotRegex(page, r"(?i)\b(analytics|gtag|pixel|affiliate|utm_)\b")
            body, _ = build.resolve_tokens(self.lib, self.lib.articles[slug])
            self.assertNotRegex(body, r"\bon(click|load|error|focus|input|change|key[a-z]+|mouse[a-z]+)=")   # the tool body has no inline handlers except onsubmit

    def test_no_duplicate_ids_in_any_page(self):
        for slug, page in self.built.items():
            ids = re.findall(r'\bid="([^"]+)"', page)
            dupes = [k for k, v in Counter(ids).items() if v > 1]
            self.assertEqual(dupes, [], f"{slug}: duplicate ids {dupes}")

    def test_every_field_has_a_label_and_a_length_limit(self):
        for slug, page in self.built.items():
            for m in re.finditer(r'<(input|textarea|select)\b([^>]*)>', page):
                attrs = m.group(2)
                fid = re.search(r'\bid="([^"]+)"', attrs)
                if not fid or 'type="hidden"' in attrs:
                    continue
                fid = fid.group(1)
                self.assertRegex(page, rf'<label[^>]*\bfor="{re.escape(fid)}"', f"{slug}: {fid} has no label")
                if m.group(1) in ("input", "textarea") and 'type="checkbox"' not in attrs and 'type="date"' not in attrs:
                    self.assertRegex(attrs, r'maxlength="\d+"', f"{slug}: {fid} has no maxlength")

    def test_pages_have_no_javascript_fallbacks(self):
        self.assertIn("<noscript>", self.built["home-fire-escape-worksheet"])
        self.assertEqual(self.built["home-fire-escape-worksheet"].count('data-list="rooms"'), 8)
        self.assertIn('id="op-static"', self.built["power-outage-planner"])
        self.assertGreaterEqual(self.built["power-outage-planner"].count('id="ops-'), 60)
        self.assertIn('<div class="pa-foldcard">', self.built["reunification-plan"])
        for slug in SLUGS:                                       # scripted-only buttons are hidden until the script runs them
            for m in re.finditer(r'<button\b[^>]*id="(fw|op|rc)-(print|download|reset|add-[a-z]+)"[^>]*>', self.built[slug]):
                self.assertIn(" hidden", m.group(0), m.group(0))

    def test_tools_are_registered_gated_and_still_drafts(self):
        tools = {t["slug"]: t for t in self.lib.taxonomy["tools"]}
        for slug in SLUGS:
            self.assertIn(slug, tools)
            self.assertTrue(tools[slug].get("gate"), slug)
            meta = self.lib.articles[slug]
            self.assertEqual(meta["status"]["publish"], "draft")
            self.assertEqual(meta["safety_review"]["state"], "pending")
            self.assertEqual(meta["section"], "field-tools")

    def test_sources_are_cited_and_unverified_ones_are_not(self):
        for slug in SLUGS:
            body, order = build.resolve_tokens(self.lib, self.lib.articles[slug])
            self.assertGreaterEqual(len(order), 5, slug)
            for sid in order:
                self.assertTrue(self.lib.register[sid].get("verified_on"), f"{slug} cites unverified {sid}")
                self.assertFalse(self.lib.register[sid].get("human_link_check"), f"{sid}: automated checks must not be labelled human-verified")

    def test_planner_page_gives_no_sizing_or_medical_instructions(self):
        page = re.sub(r"<script>.*?</script>", " ", self.built["power-outage-planner"], flags=re.S)
        text = re.sub(r"<[^>]+>", " ", page)
        self.assertNotRegex(text, r"(?i)\b\d+\s*(watts?|kw|kilowatts?|amps?|btu)\b")
        self.assertNotRegex(text, r"(?i)\b(throw (it )?away|discard) (your )?(medic|insulin|prescription)")
        self.assertIn("Do not stop, skip or throw out a medicine you depend on without asking your pharmacist or prescriber", text)

    def test_card_page_warns_about_lost_cards_and_offers_minimal_version(self):
        text = re.sub(r"<[^>]+>", " ", self.built["reunification-plan"])
        self.assertIn("A printed card can be lost", text)
        self.assertIn("Minimal version", text)
        self.assertNotRegex(text, r"(?i)\b(full name|social security number)\b.*\b(enter|type|required)\b")


if __name__ == "__main__":
    unittest.main()
