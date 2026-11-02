"""Real-browser checks for the three Shelter, Power and Family Communication tools.

Runs the built preview pages in headless Chromium (Playwright; Microsoft Edge or Chrome if installed, otherwise Playwright's
own Chromium). Skips, and says so, when Playwright or a browser is unavailable. These pages are standalone previews: the
checks do not prove behavior inside a WordPress theme, which needs its own test.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREVIEW = ROOT / "build" / "preview"
QA_DIR = os.environ.get("PA_QA_DIR")  # optional: write screenshots and PDFs here
SLUGS = ["home-fire-escape-worksheet", "power-outage-planner", "family-reunification-card"]
ARTICLES = ["outage-heat-cold-generators", "home-fire-escape-plan", "shelter-or-evacuate", "family-communication-plan"]
WIDTHS = [320, 360, 390, 428, 768, 1024, 1440, 1920]
TODAY_FALLBACK = "2026-11-01"

try:
    from playwright.sync_api import sync_playwright
except Exception:  # pragma: no cover
    sync_playwright = None


def _launch(p):
    for kwargs in ({"channel": "msedge"}, {"channel": "chrome"}, {}):
        try:
            return p.chromium.launch(headless=True, **kwargs), kwargs.get("channel", "playwright-chromium")
        except Exception:
            continue
    return None, None


class BrowserToolTests(unittest.TestCase):
    pw = None
    browser = None
    channel = None

    @classmethod
    def setUpClass(cls):
        if sync_playwright is None:
            raise unittest.SkipTest("playwright is not installed")
        r = subprocess.run([sys.executable, "-I", str(ROOT / "tools" / "build.py")], capture_output=True, text=True, timeout=120)
        if r.returncode:
            raise RuntimeError("build failed: " + r.stderr)
        cls.pw = sync_playwright().start()
        cls.browser, cls.channel = _launch(cls.pw)
        if cls.browser is None:
            cls.pw.stop()
            raise unittest.SkipTest("no Chromium-based browser available")

    @classmethod
    def tearDownClass(cls):
        if cls.browser:
            cls.browser.close()
        if cls.pw:
            cls.pw.stop()

    # ---------------------------------------------------------------- helpers
    def url(self, slug):
        return (PREVIEW / f"{slug}.html").as_uri()

    def page(self, slug, width=1024, height=900, js=True, reduced=False, **ctx):
        context = self.browser.new_context(viewport={"width": width, "height": height}, java_script_enabled=js,
                                           reduced_motion="reduce" if reduced else "no-preference", accept_downloads=True, **ctx)
        pg = context.new_page()
        pg.requests = []
        pg.errors = []
        pg.on("request", lambda r: pg.requests.append(r.url))
        pg.on("pageerror", lambda e: pg.errors.append(str(e)))
        pg.on("console", lambda m: pg.errors.append(m.text) if m.type == "error" else None)
        pg.goto(self.url(slug))
        pg.wait_for_load_state("load")
        return pg

    def close(self, pg):
        pg.context.close()

    # ---------------------------------------------------------------- tests
    def test_no_network_requests_and_no_errors(self):
        for slug in SLUGS:
            pg = self.page(slug)
            try:
                bad = [u for u in pg.requests if not u.startswith(("file:", "data:", "blob:"))]
                self.assertEqual(bad, [], f"{slug} made network requests")
                self.assertEqual(pg.errors, [], f"{slug} had console or page errors")
            finally:
                self.close(pg)

    def test_no_horizontal_overflow_at_every_width(self):
        for slug in SLUGS:
            for w in WIDTHS:
                pg = self.page(slug, width=w)
                try:
                    over = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
                    self.assertLessEqual(over, 1, f"{slug} overflows horizontally by {over}px at {w}px")
                    if QA_DIR and w in (320, 768, 1440):
                        os.makedirs(QA_DIR, exist_ok=True)
                        pg.screenshot(path=os.path.join(QA_DIR, f"{slug}-{w}.png"), full_page=True)
                finally:
                    self.close(pg)

    def test_every_control_has_an_accessible_name_and_target_size(self):
        js = """() => {
          const out = [];
          document.querySelectorAll('.pa-sheet input, .pa-sheet select, .pa-sheet textarea, .pa-sheet button, .pa-printbar button').forEach(el => {
            const r = el.getBoundingClientRect(); if (!r.width || !r.height) return;
            const named = (el.labels && el.labels.length) || el.getAttribute('aria-label') || el.getAttribute('aria-labelledby') || (el.tagName === 'BUTTON' && el.textContent.trim());
            const box = el.type === 'checkbox';
            const target = box ? Math.max(r.height, el.closest('label') ? el.closest('label').getBoundingClientRect().height : 0) : r.height;
            out.push({id: el.id, named: !!named, h: target, w: r.width, tag: el.tagName, type: el.type});
          });
          return out;
        }"""
        for slug in SLUGS:
            pg = self.page(slug, width=390)
            try:
                items = pg.evaluate(js)
                self.assertGreater(len(items), 10, slug)
                for i in items:
                    self.assertTrue(i["named"], f"{slug}: {i['tag']}#{i['id']} has no accessible name")
                    self.assertGreaterEqual(i["h"], 44 - 1, f"{slug}: {i['tag']}#{i['id']} target height {i['h']}px is under 44px")
            finally:
                self.close(pg)

    def test_keyboard_reaches_controls_with_visible_focus(self):
        for slug in SLUGS:
            pg = self.page(slug)
            try:
                seen = set()
                for _ in range(40):
                    pg.keyboard.press("Tab")
                    info = pg.evaluate("""() => { const e = document.activeElement; if (!e || e === document.body) return null;
                      const cs = getComputedStyle(e); return {id: e.id, tag: e.tagName, ow: parseFloat(cs.outlineWidth) || 0, os: cs.outlineStyle, inForm: !!e.closest('.pa-sheet, .pa-printbar')}; }""")
                    if info and info["inForm"]:
                        seen.add(info["id"] or info["tag"])
                        self.assertGreaterEqual(info["ow"], 2, f"{slug}: focus ring missing on {info['id']}")
                self.assertGreater(len(seen), 8, f"{slug}: keyboard reached too few form controls")
            finally:
                self.close(pg)

    def test_html_in_inputs_is_inert(self):
        payload = "<img src=x onerror=window.__pwned=1><script>window.__pwned=2</script>"
        pg = self.page("home-fire-escape-worksheet")
        try:
            pg.fill("#fw-rooms-0-room", payload)
            pg.fill("#fw-meeting-primary", payload)
            pg.fill("#fw-fireDept", payload)
            pg.wait_for_timeout(100)
            self.assertIsNone(pg.evaluate("window.__pwned"))
            self.assertEqual(pg.evaluate("document.querySelectorAll('#fw-check img, #fw-check script').length"), 0)
            self.assertIn("fewer than two ways out", pg.inner_text("#fw-check"))
            self.assertIn("<img", pg.inner_text("#fw-check"))   # shown as text, not parsed
        finally:
            self.close(pg)
        pg = self.page("power-outage-planner")
        try:
            pg.check("#op-q-medDevice")
            pg.fill("#op-c-utility", payload)
            with pg.expect_download() as d:
                pg.click("#op-download")
            text = Path(d.value.path()).read_text(encoding="utf-8")
            self.assertIn("<img", text)                       # exported as plain text
            self.assertIsNone(pg.evaluate("window.__pwned"))
            self.assertEqual(pg.evaluate("document.querySelectorAll('#op-out img, #op-out script').length"), 0)
        finally:
            self.close(pg)
        pg = self.page("family-reunification-card")
        try:
            pg.fill("#rc-hhName", payload)
            pg.fill("#rc-meet1", payload)
            pg.wait_for_timeout(100)
            self.assertIsNone(pg.evaluate("window.__pwned"))
            self.assertEqual(pg.evaluate("document.querySelectorAll('#rc-preview img, #rc-preview script, #rc-sheet img').length"), 0)
        finally:
            self.close(pg)

    def test_nothing_is_stored_by_the_page(self):
        for slug, sel, val in [("home-fire-escape-worksheet", "#fw-fireDept", "555-0100"), ("power-outage-planner", "#op-c-utility", "555-0100"), ("family-reunification-card", "#rc-hhPhone", "555-0100")]:
            pg = self.page(slug)
            try:
                pg.fill(sel, val)
                pg.wait_for_timeout(100)
                stored = pg.evaluate("({ls: localStorage.length, ss: sessionStorage.length, ck: document.cookie})")
                self.assertEqual(stored["ls"], 0, slug)
                self.assertEqual(stored["ss"], 0, slug)
                self.assertEqual(stored["ck"], "", slug)
            finally:
                self.close(pg)

    def test_reduced_motion_removes_transitions(self):
        for slug in SLUGS:
            pg = self.page(slug, reduced=True)
            try:
                d = pg.evaluate("[...document.querySelectorAll('.pa-btn, .pa a')].map(e => getComputedStyle(e).transitionDuration)")
                self.assertTrue(all(x in ("0s", "") for x in d), f"{slug}: transitions remain under reduced motion: {set(d)}")
            finally:
                self.close(pg)

    def test_fire_worksheet_behaviour(self):
        pg = self.page("home-fire-escape-worksheet")
        try:
            self.assertIn("No rooms listed", pg.inner_text("#fw-check"))
            pg.fill("#fw-rooms-0-room", "Bedroom")
            pg.fill("#fw-rooms-0-out1", "Door")
            self.assertIn("fewer than two ways out", pg.inner_text("#fw-check"))
            pg.fill("#fw-rooms-0-out2", "Window")
            self.assertNotIn("Bedroom", pg.inner_text("#fw-check"))
            pg.fill("#fw-alarms-mfgDate", "2016-03-15")
            self.assertIn("2026-03-15", pg.inner_text("#fw-replace"))
            self.assertIn("10 years old or more", pg.inner_text("#fw-check")) if TODAY_FALLBACK >= "2026-03-15" else None
            pg.fill("#fw-practice-0-date", "2026-06-01")
            self.assertIn("2026-12-01", pg.inner_text("#fw-next"))
            before = pg.locator('[data-list="rooms"]').count()
            pg.click("#fw-add-room")
            self.assertEqual(pg.locator('[data-list="rooms"]').count(), before + 1)
            pg.fill("#fw-rooms-8-room", "Attic")
            self.assertIn('"Attic"', pg.inner_text("#fw-check"))
            with pg.expect_download() as d:
                pg.click("#fw-download")
            text = Path(d.value.path()).read_text(encoding="utf-8")
            self.assertIn("Bedroom: 1) Door 2) Window", text)
            self.assertIn("Attic", text)
            pg.click("#fw-reset")
            self.assertEqual(pg.locator('[data-list="rooms"]').count(), before)
            self.assertEqual(pg.input_value("#fw-rooms-0-room"), "")
        finally:
            self.close(pg)

    def test_outage_planner_adapts(self):
        pg = self.page("power-outage-planner")
        try:
            base = pg.locator("#op-out input[type=checkbox]").count()
            self.assertGreater(base, 15)
            self.assertEqual(pg.locator("#op-i-M4").count(), 0)
            pg.check("#op-q-medDevice")
            self.assertEqual(pg.locator("#op-i-M4").count(), 1)
            self.assertIn("Source: FEMA", pg.inner_text("#op-i-M4 >> xpath=ancestor::li"))
            pg.check("#op-q-generator")
            self.assertEqual(pg.locator("#op-i-G3").count(), 1)
            pg.check("#op-i-L1")
            pg.uncheck("#op-q-generator")
            pg.check("#op-q-generator")
            self.assertEqual(pg.locator("#op-i-G1").count(), 1)
            text = pg.inner_text("#op-out")
            self.assertNotRegex(text, r"(?i)\b(watts?|kilowatts?|btu|gallons?)\b")
            self.assertNotRegex(pg.inner_text("#op-g-meds + ul"), r"(?i)throw (it )?(away|out)|discard")
            with pg.expect_download() as d:
                pg.click("#op-download")
            body = Path(d.value.path()).read_text(encoding="utf-8")
            self.assertIn("[x] Keep a flashlight", body)
            self.assertIn("Not medical advice", body)
            pg.click("#op-reset")
            self.assertEqual(pg.locator("#op-i-M4").count(), 0)
        finally:
            self.close(pg)

    def test_card_behaviour_and_minimal_version(self):
        pg = self.page("family-reunification-card")
        try:
            pg.fill("#rc-outName", "Aunt Rosa")
            pg.fill("#rc-outPhone", "555-0199")
            pg.fill("#rc-meet1", "Mailbox out front")
            pg.fill("#rc-school", "Lincoln Elementary")
            pg.fill("#rc-careName", "Mr. Lee")
            self.assertIn("Lincoln Elementary", pg.inner_text("#rc-preview"))
            pg.check("#rc-minimal")
            pv = pg.inner_text("#rc-preview")
            self.assertNotIn("Lincoln", pv)
            self.assertNotIn("Mr. Lee", pv)
            self.assertIn("Aunt Rosa", pv)
            pg.select_option("#rc-copies", "3")
            self.assertEqual(pg.locator("#rc-sheet .pa-foldcard").count(), 3)
            pg.fill("#rc-meet1", "123 Maple Street")
            self.assertIn("street address", pg.inner_text("#rc-warn"))
            self.assertEqual(pg.get_attribute("#rc-hhName", "maxlength"), "24")
        finally:
            self.close(pg)

    def test_print_layout_of_the_card_is_legible_and_fits(self):
        pg = self.page("family-reunification-card")
        try:
            long = "W" * 80
            for k, n in [("hhName", 24), ("hhPhone", 24), ("outName", 24), ("outPhone", 24), ("meet1", 32), ("meet2", 32), ("school", 32), ("schoolPlan", 44), ("pickup", 44), ("careName", 24), ("carePhone", 24), ("access", 44)]:
                pg.fill(f"#rc-{k}", ("5" * n) if k.endswith("Phone") else long[:n])
            pg.fill("#rc-reviewed", "2026-11-01")
            pg.select_option("#rc-copies", "4")
            pg.emulate_media(media="print")
            r = pg.evaluate("""() => [...document.querySelectorAll('#rc-sheet .pa-foldcard')].map(c => {
              const b = c.getBoundingClientRect();
              const faces = [...c.querySelectorAll('.pa-face')].map(f => ({over: f.scrollHeight - f.clientHeight, fs: parseFloat(getComputedStyle(f).fontSize)}));
              return {w: b.width, h: b.height, faces};
            })""")
            self.assertEqual(len(r), 4)
            for c in r:
                self.assertAlmostEqual(c["w"], 672, delta=3)          # 7 in at 96 dpi
                self.assertAlmostEqual(c["h"], 204, delta=3)          # 2.125 in
                for f in c["faces"]:
                    self.assertLessEqual(f["over"], 1, "worst-case text overflows a card face")
                    self.assertGreaterEqual(f["fs"], 9.9, "card text is under 7.5 pt")
            hidden = pg.evaluate("[...document.querySelectorAll('.pa-noprint, .pa-card-mainhide')].every(e => getComputedStyle(e).display === 'none')")
            self.assertTrue(hidden)
            if QA_DIR:
                os.makedirs(QA_DIR, exist_ok=True)
                pg.pdf(path=os.path.join(QA_DIR, "reunification-card-print.pdf"), format="Letter", print_background=True)
        finally:
            self.close(pg)

    def test_print_layout_of_worksheet_and_planner(self):
        for slug in ("home-fire-escape-worksheet", "power-outage-planner"):
            pg = self.page(slug)
            try:
                pg.emulate_media(media="print")
                self.assertTrue(pg.evaluate("[...document.querySelectorAll('.pa-noprint')].every(e => getComputedStyle(e).display === 'none')"), slug)
                over = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
                self.assertLessEqual(over, 1, slug)
                if QA_DIR:
                    os.makedirs(QA_DIR, exist_ok=True)
                    pg.pdf(path=os.path.join(QA_DIR, f"{slug}-print.pdf"), format="Letter", print_background=True)
            finally:
                self.close(pg)

    def test_print_output_is_only_the_printable_sheet(self):
        """The printed page is the card, the worksheet or the checklist, not the whole article."""
        limits = {"family-reunification-card": 1, "home-fire-escape-worksheet": 5, "power-outage-planner": 4}
        for slug, max_pages in limits.items():
            pg = self.page(slug)
            try:
                if slug == "family-reunification-card":
                    pg.select_option("#rc-copies", "4")
                    pg.fill("#rc-outName", "Aunt Rosa")
                pdf = pg.pdf(format="Letter", print_background=True)
                pages = len(re.findall(rb"/Type\s*/Page(?![s])", pdf))
                self.assertLessEqual(pages, max_pages, f"{slug} prints {pages} pages; expected at most {max_pages}")
                pg.emulate_media(media="print")
                hidden = pg.evaluate("[...document.querySelectorAll('.pa-head, .pa-toc, .pa-crumbs')].every(e => getComputedStyle(e).display === 'none')")
                self.assertTrue(hidden, slug)
            finally:
                self.close(pg)

    def test_pages_work_without_javascript(self):
        pg = self.page("home-fire-escape-worksheet", js=False)
        try:
            self.assertGreaterEqual(pg.locator("#fw input, #fw textarea").count(), 40)
            self.assertTrue(pg.is_visible("#fw-rooms-0-room"))
            self.assertTrue(pg.is_visible("svg.pa-gridsvg"))
            self.assertFalse(pg.is_visible("#fw-print"))      # JS-only buttons stay hidden rather than broken
        finally:
            self.close(pg)
        pg = self.page("power-outage-planner", js=False)
        try:
            n = pg.locator("#op-static input[type=checkbox]").count()
            self.assertGreaterEqual(n, 50)                     # the complete checklist is present
            self.assertTrue(pg.is_visible("#op-static"))
            self.assertIn("If: someone depends on electrically powered medical equipment", pg.inner_text("#op-static"))
        finally:
            self.close(pg)
        pg = self.page("family-reunification-card", js=False)
        try:
            self.assertTrue(pg.is_visible(".pa-foldcard"))
            self.assertFalse(pg.is_visible("#rc"))
            pg.emulate_media(media="print")
            r = pg.evaluate("[...document.querySelectorAll('.pa-foldcard .pa-face')].map(f => f.scrollHeight - f.clientHeight)")
            self.assertTrue(r and all(x <= 1 for x in r), "blank fallback card overflows")
        finally:
            self.close(pg)

    def test_axe_core_has_no_violations(self):
        """Runs only when PA_AXE_JS points at an independently verified axe.min.js (see docs/SHELTER-QA.md); otherwise skipped."""
        axe = os.environ.get("PA_AXE_JS")
        if not axe or not os.path.exists(axe):
            self.skipTest("axe-core not provided (set PA_AXE_JS to a verified axe.min.js)")
        src = Path(axe).read_text(encoding="utf-8")
        for slug in SLUGS:
            for w in (390, 1440):
                pg = self.page(slug, width=w)
                try:
                    pg.evaluate(src)
                    res = pg.evaluate("axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice']}}).then(r => r.violations.map(v => ({id: v.id, impact: v.impact, n: v.nodes.length, sample: v.nodes[0].target.join(' ')})))")
                    if QA_DIR:
                        os.makedirs(QA_DIR, exist_ok=True)
                        Path(QA_DIR, f"axe-{slug}-{w}.json").write_text(__import__("json").dumps(res, indent=2), encoding="utf-8")
                    self.assertEqual(res, [], f"{slug} at {w}px: axe violations")
                finally:
                    self.close(pg)

    def test_articles_and_diagrams_render_cleanly(self):
        """The four articles (with their diagrams) at every width, plus axe-core when provided."""
        axe = os.environ.get("PA_AXE_JS")
        src = Path(axe).read_text(encoding="utf-8") if axe and os.path.exists(axe) else None
        for slug in ARTICLES:
            for w in WIDTHS:
                pg = self.page(slug, width=w)
                try:
                    self.assertLessEqual(pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth"), 1, f"{slug} overflows at {w}px")
                    self.assertEqual(pg.errors, [], slug)
                    if src and w in (390, 1440):
                        res = pg.evaluate(src + "; axe.run(document, {runOnly: {type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice']}}).then(r => r.violations.map(v => ({id: v.id, n: v.nodes.length, sample: v.nodes[0].target.join(' ')})))")
                        self.assertEqual(res, [], f"{slug} at {w}px: axe violations")
                    if QA_DIR and slug in ("shelter-or-evacuate", "home-fire-escape-plan") and w in (320, 1440):
                        os.makedirs(QA_DIR, exist_ok=True)
                        pg.screenshot(path=os.path.join(QA_DIR, f"{slug}-{w}.png"), full_page=True)
                finally:
                    self.close(pg)

    def test_zoom_reflow_at_400_percent(self):
        for slug in SLUGS:
            pg = self.page(slug, width=320, height=256)   # 1280 x 1024 CSS px at 400% zoom is a 320 x 256 viewport
            try:
                over = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
                self.assertLessEqual(over, 1, f"{slug} does not reflow at 400% zoom")
            finally:
                self.close(pg)


if __name__ == "__main__":
    unittest.main()
