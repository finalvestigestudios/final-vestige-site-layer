"""Regression tests for the Start Here cluster: four articles, two tools, the editorial hub and the audit files.
Run:  python -I -m unittest discover -s preparedness/tests -v
"""
from __future__ import annotations
import json, re, shutil, subprocess, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402

ARTICLES = ["household-emergency-plan", "three-day-kit", "go-bags", "preparedness-real-households"]
TOOLS = ["reunification-plan", "kit-builder"]
AUDIT = ROOT / "audit" / "start-here"


class StartHereGovernance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = build.Library()

    def test_everything_stays_draft_and_pending(self):
        for slug in ARTICLES + TOOLS:
            m = self.lib.articles[slug]
            self.assertEqual(m["status"]["publish"], "draft", slug)
            self.assertEqual(m["safety_review"]["state"], "pending", slug)
            self.assertIsNone(m["safety_review"]["reviewer"], slug)

    def test_no_start_source_claims_a_human_link_check(self):
        frag = json.loads((ROOT / "sources" / "fragments" / "start.json").read_text(encoding="utf-8"))["sources"]
        for s in frag:
            self.assertIs(s["human_link_check"], False, f"{s['id']} cannot claim a human link check from an automated run")

    def test_removed_wording_stays_removed(self):
        banned = {
            "household-emergency-plan": [r"switch off the main power", r"main power for an evening"],
            "three-day-kit": [r"We follow the newer", r"use the shorter time", r"Do not stop, throw away or ration"],
            "preparedness-real-households": [r"Rental Assistance Demonstration \(RAD\) program must", r"properties converting through"],
        }
        for slug, pats in banned.items():
            body = (ROOT / "content" / "articles" / f"{slug}.body.html").read_text(encoding="utf-8")
            for p in pats:
                self.assertIsNone(re.search(p, body), f"{slug} must not contain {p!r}")

    def test_medicine_box_present_and_does_not_direct_readers(self):
        body = (ROOT / "content" / "articles" / "three-day-kit.body.html").read_text(encoding="utf-8")
        self.assertIn("ask your prescriber or pharmacist", body.lower())
        self.assertIn("cannot tell you what to do with any particular medicine", body)
        self.assertIn("start-fema-power-sheet", body)
        self.assertIn("start-fsis-emergency-food", body)

    def test_hud_template_is_not_used_as_legal_evidence(self):
        body = (ROOT / "content" / "articles" / "preparedness-real-households.body.html").read_text(encoding="utf-8")
        self.assertIn("make no claim about what any landlord", body)
        self.assertIn("12 of its 79 pages", body)

    def test_infant_and_pregnancy_cautions(self):
        body = (ROOT / "content" / "articles" / "go-bags.body.html").read_text(encoding="utf-8")
        self.assertIn("no unsupervised dosing", body.lower())
        self.assertIn("Emergency birth supplies: context, not instructions", body)
        self.assertIn("pediatrician", body)


class StartHereTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = build.Library()
        cls.built = {s: build.build_article(cls.lib, s)["inner"] for s in TOOLS}

    def test_node_unit_tests_pass(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node not installed")
        r = subprocess.run([node, str(ROOT / "tests" / "test_start_tools.js")], capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_tool_scripts_are_private(self):
        for slug, built in self.built.items():
            script = "\n".join(re.findall(r"<script>(.*?)</script>", built, flags=re.S))
            self.assertTrue(script, slug)
            for banned in ("localStorage", "sessionStorage", "indexedDB", "document.cookie", "fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "navigator.", "import(", "eval(", "new Function", "history.pushState", "history.replaceState", "location.hash", "location.search", "postMessage", "EventSource", "Worker("):
                self.assertNotIn(banned, script, f"{slug} script must not use {banned}")
            self.assertNotRegex(built, r"<form[^>]+(action|method)=")
            self.assertNotRegex(built, r"<(img|iframe|embed|object|link)\b[^>]*(src|href)=[\"']https?://")

    def test_plan_builder_never_prefills_personal_fields(self):
        ui = (ROOT / "tools" / "plan_builder_ui.js").read_text(encoding="utf-8")
        self.assertIn("autocomplete: 'off'", ui)
        self.assertNotIn("value: '", ui.replace("value: ''", ""))

    def test_plan_builder_has_no_js_fallback_and_labels(self):
        built = self.built["reunification-plan"]
        self.assertIn('<details id="pb-blank"', built)
        self.assertIn(" open>", built[built.index('<details id="pb-blank"'):][:80])
        self.assertIn("<noscript>", built)
        self.assertGreaterEqual(built.count("<caption>"), 7)
        self.assertEqual(built.count('role="region"'), built.count('class="pa-tablewrap"'))
        for needed in ('id="pb-status"', 'role="status"', 'aria-live="polite"', 'id="pb-errors" role="alert"'):
            self.assertIn(needed, built)

    def test_kit_builder_items_are_all_sourced_and_free_of_products(self):
        sys.path.insert(0, str(ROOT / "content" / "tools" / "src"))
        import kit_builder_items as D  # noqa: E402
        ids = [i[0] for i in D.ITEMS]
        self.assertEqual(len(ids), len(set(ids)))
        groups = {g[0] for g in D.GROUPS}
        for iid, gid, label, why, srcs in D.ITEMS:
            self.assertIn(gid, groups, iid)
            self.assertTrue(srcs, f"{iid} has no source")
            for s in srcs:
                self.assertTrue(self.lib.register[s].get("verified_on"), f"{iid} cites unverified {s}")
            self.assertNotRegex(label + why, r"(?i)\b(buy now|affiliate|brand|\$\d|coupon|amazon|click here)\b", iid)
        scen = {s[0] for s in D.SCENARIOS}
        self.assertTrue({g[3] for g in D.GROUPS if g[3]} <= scen)
        self.assertEqual({"adults", "children", "infants", "pets", "mobility", "power", "storage", "foot", "car", "budget"} - scen, set())

    def test_kit_builder_body_matches_generator(self):
        out = ROOT / "content" / "tools" / "kit-builder.body.html"
        before = out.read_text(encoding="utf-8")
        subprocess.run([sys.executable, "-I", str(ROOT / "content" / "tools" / "src" / "gen_kit_builder.py")], check=True, capture_output=True)
        self.assertEqual(out.read_text(encoding="utf-8"), before, "kit-builder.body.html is stale: rerun gen_kit_builder.py")

    def test_kit_builder_gives_no_medicine_instructions(self):
        built = re.sub(r"<[^>]+>", " ", self.built["kit-builder"])
        self.assertNotRegex(built, r"(?i)\b(you should|you must|always|never) (stop|discard|throw away|ration|skip|double|increase|decrease)\b")
        self.assertIn("Do not decide for yourself whether to use or discard a medicine", built)
        self.assertIn("Do not give any medicine to an infant without direction", built)


class StartHereHub(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = build.Library()
        cls.hub = build.build_hub(cls.lib, "start-here")

    def test_hub_structure(self):
        inner = self.hub["inner"]
        self.assertEqual(inner.count("<h1"), 1)
        self.assertIn("Preparedness Starts at Home", inner)
        self.assertIn("Practical plans. Real households. Evidence you can trust.", inner)
        self.assertIn("ACT NOW", inner)
        self.assertIn('aria-label="Breadcrumb"', inner)
        self.assertIn('id="pa-guides"', inner)
        steps = re.findall(r'<li class="ph-step"><h3><a href="([^"]+)">', inner)
        self.assertEqual([s.rstrip("/").split("/")[-1] for s in steps], ["household-emergency-plan", "three-day-kit", "go-bags", "preparedness-real-households"])
        for t in TOOLS:
            self.assertIn(self.lib.url_path(t), inner)

    def test_hub_lists_every_start_guide_once_in_the_card_list(self):
        cards = re.findall(r'<h3><a href="([^"]+)">', self.hub["inner"].split('id="h-all"')[1])
        self.assertEqual(sorted(c.rstrip("/").split("/")[-1] for c in cards), sorted(ARTICLES))

    def test_hub_makes_no_empty_destinations(self):
        for href in re.findall(r'href="(/preparedness/[^"]*)"', self.hub["inner"]):
            parts = [p for p in href.split("/") if p]
            if len(parts) == 1:
                continue
            if len(parts) == 2:
                self.assertTrue(any(m["section"] == parts[1] for m in self.lib.articles.values()), f"empty section link {href}")
            else:
                self.assertIn(parts[2], self.lib.articles, href)

    def test_hub_keeps_history_out(self):
        text = re.sub(r"<[^>]+>", " ", self.hub["inner"])
        self.assertNotRegex(text, r"(?i)salt beef|hardtack|pemmican|curing")
        self.assertIn("not safety guidance", text)

    def test_hub_says_it_is_a_draft(self):
        self.assertIn("Draft for review", self.hub["inner"])


class StartHereAudit(unittest.TestCase):
    def test_claim_matrix_is_consistent_with_the_register_and_articles(self):
        lib = build.Library()
        claims = json.loads((AUDIT / "claims.json").read_text(encoding="utf-8"))["claims"]
        ids = [c["id"] for c in claims]
        self.assertEqual(len(ids), len(set(ids)))
        for c in claims:
            if c["source"]:
                self.assertIn(c["source"], lib.register, c["id"])
                self.assertTrue(c["anchors"] or c.get("manual_evidence"), f"{c['id']} has neither anchors nor manual evidence")
            else:
                self.assertEqual(c["basis"], "editorial", c["id"])
            self.assertIn(c["review"], {"editorial", "human-safety", "human-legal"}, c["id"])
            self.assertIn(c["article"], ARTICLES, c["id"])

    def test_ledger_and_matrix_exist_and_have_no_failed_anchors(self):
        led = json.loads((AUDIT / "ledger.json").read_text(encoding="utf-8"))
        mat = json.loads((AUDIT / "claim-matrix.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(led["sources"]), 29)
        for s in led["sources"]:
            self.assertIs(s["human_link_check"], False, s["source_id"])
            self.assertTrue(s["automated"]["resolves"], f"{s['source_id']} did not resolve on the last run")
        failed = [m["id"] for m in mat if (m.get("automated_result") or {}).get("anchors_found") is False]
        self.assertEqual(failed, [], f"claims whose anchor phrases were not found on the last run: {failed}")
        manual = [m["id"] for m in mat if m.get("source") and (m.get("automated_result") or {}).get("anchors_found") is None]
        self.assertEqual(manual, ["C21b"], "only C21b is expected to need a human; update the audit notes if this changes")

    def test_every_source_cited_by_the_four_articles_is_in_the_ledger(self):
        lib = build.Library()
        led = {s["source_id"] for s in json.loads((AUDIT / "ledger.json").read_text(encoding="utf-8"))["sources"]}
        cited = set()
        for slug in ARTICLES:
            cited |= set(build.resolve_tokens(lib, lib.articles[slug])[1])
        self.assertEqual(sorted(cited - led), [], "cited sources missing from the ledger: rerun audit/start-here/verify_sources.py")


class StartHereBrowser(unittest.TestCase):
    def test_quick_browser_qa(self):
        try:
            import playwright  # noqa: F401
        except ImportError:
            self.skipTest("playwright not installed")
        if not (ROOT / "build" / "preview" / "hub-start-here.html").exists():
            self.skipTest("run tools/build.py first")
        r = subprocess.run([sys.executable, "-I", str(ROOT / "tests" / "browser_qa_start.py"), "--quick"], capture_output=True, text=True, timeout=300)
        if "channel" in r.stderr and "msedge" in r.stderr:
            self.skipTest("Microsoft Edge is not available to Playwright")
        self.assertEqual(r.returncode, 0, r.stdout[-1500:] + r.stderr[-800:])


if __name__ == "__main__":
    unittest.main()
