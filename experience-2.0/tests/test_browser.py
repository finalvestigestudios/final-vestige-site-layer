"""Real-browser tests (Chromium family). A missing browser is a hard error, never a skip.

Media hosts are answered with correctly proportioned local JPEGs so these tests are deterministic offline;
tools/verify_media.py checks the real NASA URLs separately."""
from __future__ import annotations

import json
import re
import unittest

from playwright.sync_api import sync_playwright

import support
from browser import launch, serve
from render_desk import render_desk

BASE = None
_server = None
_pw = None
_browser = None


def setUpModule():
    global BASE, _server, _pw, _browser
    support.build()
    _server = serve(support.DIST)
    BASE = _server.__enter__()
    _pw = sync_playwright().start()
    _browser = launch(_pw)


def tearDownModule():
    _browser.close()
    _pw.stop()
    _server.__exit__(None, None, None)


class Probe:
    """A page plus the console/network problems it produced."""

    def __init__(self, path: str, width=1440, height=900, js=True, reduced=None, touch=False, init_script=None, stubs=True):
        kwargs = {"viewport": {"width": width, "height": height}, "java_script_enabled": js}
        if reduced:
            kwargs["reduced_motion"] = reduced
        if touch:
            kwargs.update(has_touch=True, is_mobile=True)
        self.ctx = _browser.new_context(**kwargs)
        if stubs:
            support.install_media_stubs(self.ctx)
        self.page = self.ctx.new_page()
        self.problems: list[str] = []
        self.page.on("pageerror", lambda e: self.problems.append(f"pageerror: {e}"))
        self.page.on("console", lambda m: self.problems.append(f"console.{m.type}: {m.text}") if m.type in ("error", "warning") and "favicon" not in m.text else None)
        self.page.on("requestfailed", lambda r: self.problems.append(f"requestfailed: {r.url}") if "favicon" not in r.url else None)
        self.page.on("response", lambda r: self.problems.append(f"http {r.status}: {r.url}") if r.status >= 400 and "favicon" not in r.url else None)
        if init_script:
            self.page.add_init_script(init_script)
        self.page.goto(f"{BASE}/{path}", wait_until="load")

    def scroll_through(self):
        h = self.page.evaluate("document.documentElement.scrollHeight")
        for y in range(0, h, 700):
            self.page.evaluate(f"window.scrollTo(0,{y})")
            self.page.wait_for_timeout(40)
        self.page.evaluate("window.scrollTo(0,0)")
        self.page.wait_for_timeout(150)

    def close(self):
        self.ctx.close()


class Base(unittest.TestCase):
    def probe(self, *a, **k) -> Probe:
        p = Probe(*a, **k)
        self.addCleanup(p.close)
        return p


class Responsive(Base):
    def test_all_pages_all_widths(self):
        widths = support.VIEWPORTS + [(320, 640)]
        for name, path in support.PAGES.items():
            for w, h in widths:
                with self.subTest(page=name, width=w):
                    p = self.probe(path, w, h)
                    p.scroll_through()
                    stats = p.page.evaluate("""() => ({
                        overflow: document.documentElement.scrollWidth - innerWidth,
                        h1: document.querySelectorAll('h1').length,
                        ready: [...document.querySelectorAll('[data-fvx]')].map(e => e.getAttribute('data-fvx-ready')),
                        broken: [...document.images].filter(i => !(i.complete && i.naturalWidth > 0)).map(i => i.currentSrc || i.src),
                        lang: document.documentElement.lang})""")
                    self.assertLessEqual(stats["overflow"], 0, f"horizontal overflow {stats}")
                    self.assertEqual(stats["h1"], 1)
                    self.assertTrue(all(r == "true" for r in stats["ready"]), stats)
                    self.assertEqual(stats["broken"], [])
                    self.assertEqual(stats["lang"], "en")
                    self.assertEqual(p.problems, [])


class Flagship(Base):
    PATH = support.PAGES["flagship"]

    def test_structure_and_heading_outline(self):
        p = self.probe(self.PATH)
        outline = p.page.evaluate("[...document.querySelectorAll('h1,h2')].map(h => h.tagName + ':' + h.textContent.trim())")
        self.assertEqual(outline[0], "H1:The Hatch Opened Inward")
        self.assertEqual(sum(1 for o in outline if o.startswith("H2:")), 7)  # six chapters + conclusion
        self.assertEqual(p.page.locator("[data-fvx-chapter]").count(), 6)
        self.assertEqual(p.page.locator("main").count(), 1)

    def test_source_drawer_focus_keyboard_and_deeplink(self):
        p = self.probe(self.PATH)
        page = p.page
        opener = page.locator('[data-fvx-open-source="record-04"]')
        opener.scroll_into_view_if_needed()
        opener.focus()
        page.keyboard.press("Enter")
        dialog = page.locator("dialog[data-fvx-drawer]")
        self.assertTrue(dialog.evaluate("d => d.open"))
        label = dialog.get_attribute("aria-labelledby")
        self.assertEqual(page.locator(f"#{label}").inner_text(), "The hatch opened inward.")
        self.assertEqual(page.evaluate("document.activeElement.hasAttribute('data-fvx-drawer-close')"), True)
        self.assertTrue(page.evaluate("location.hash") == "#source-record-04")
        self.assertTrue(page.evaluate("document.documentElement.classList.contains('fv-ex2-scroll-lock')"))
        for _ in range(30):  # focus may reach browser chrome (body) but must never land on the inert page behind the modal
            page.keyboard.press("Tab")
            self.assertTrue(page.evaluate("""() => { const a = document.activeElement; return a === document.body || document.querySelector('dialog[data-fvx-drawer]').contains(a); }"""))
        self.assertIn("2017", dialog.inner_text())
        self.assertIn("Museum exhibit", dialog.inner_text())
        page.locator("[data-fvx-drawer-next]").click()
        self.assertEqual(page.locator(f"#{dialog.get_attribute('aria-labelledby')}").inner_text(), "The spark was never conclusively identified.")
        page.keyboard.press("Escape")
        self.assertFalse(dialog.evaluate("d => d.open"))
        page.wait_for_function("document.activeElement && document.activeElement.getAttribute('data-fvx-open-source') === 'record-05'", timeout=3000)
        self.assertEqual(page.evaluate("document.activeElement.getAttribute('data-fvx-open-source')"), "record-05")
        self.assertFalse(page.evaluate("document.documentElement.classList.contains('fv-ex2-scroll-lock')"))
        self.assertEqual(page.evaluate("location.hash"), "#record-05")
        self.assertEqual(p.problems, [])

    def test_drawer_deeplink_opens_on_load(self):
        p = self.probe(self.PATH + "#source-record-02")
        self.assertTrue(p.page.locator("dialog[data-fvx-drawer]").evaluate("d => d.open"))
        label = p.page.locator("dialog[data-fvx-drawer]").get_attribute("aria-labelledby")
        self.assertEqual(p.page.locator(f"#{label}").inner_text(), "An atmosphere built for a different risk.")

    def test_drawer_unknown_deeplink_is_ignored(self):
        p = self.probe(self.PATH + "#source-record-99")
        self.assertFalse(p.page.locator("dialog[data-fvx-drawer]").evaluate("d => d.open"))
        self.assertEqual(p.problems, [])

    def test_drawer_on_touch_phone_and_backdrop_close(self):
        p = self.probe(self.PATH, 390, 844, touch=True)
        o = p.page.locator('[data-fvx-open-source="record-01"]')
        o.scroll_into_view_if_needed()
        o.tap()
        d = p.page.locator("dialog[data-fvx-drawer]")
        self.assertTrue(d.evaluate("x => x.open"))
        self.assertLessEqual(p.page.evaluate("document.documentElement.scrollWidth - innerWidth"), 0)
        p.page.locator("[data-fvx-drawer-close]").first.tap()
        self.assertFalse(d.evaluate("x => x.open"))

    def test_chronology_slider_never_interpolates(self):
        p = self.probe(self.PATH)
        page = p.page
        tool = page.locator("[data-fvx-chrono-tool]")
        tool.scroll_into_view_if_needed()
        self.assertTrue(tool.is_visible())
        rng = page.locator('[data-fvx-chronology] input[type="range"]')
        self.assertTrue(page.locator('label[for="apollo1-final-seconds-range"]').count() == 1)

        def set_value(v):
            rng.evaluate("(e, v) => { e.value = v; e.dispatchEvent(new Event('input', {bubbles: true})); }", v)
            return page.locator("[data-fvx-chrono-readout]").inner_text()

        self.assertIn("Marker 1", set_value("0"))
        self.assertIn("Marker 2", set_value("6"))
        mid = set_value("8.2")
        self.assertIn("Last recorded marker: 2", mid)
        self.assertIn("Nothing is recorded between markers", mid)
        self.assertIn("Next marker", mid)
        self.assertEqual(page.locator('[data-fvx-marker][data-passed="true"]').count(), 2)
        self.assertIn("Marker 4", set_value("14.7"))
        self.assertEqual(page.locator('[data-fvx-dot][data-passed="true"]').count(), 4)
        rng.focus()
        page.keyboard.press("Home")
        self.assertEqual(rng.input_value(), "0")
        page.keyboard.press("End")
        self.assertEqual(rng.input_value(), "15")

    def test_chapter_bar_marks_exactly_one_current_chapter(self):
        p = self.probe(self.PATH)
        p.page.evaluate("document.getElementById('record-04').scrollIntoView()")
        p.page.wait_for_timeout(500)
        current = p.page.evaluate("[...document.querySelectorAll('[data-fvx-chapterbar] [aria-current], .fv-ex2-chapterbar [aria-current]')].map(a => a.getAttribute('href'))")
        self.assertEqual(current, ["#record-04"])

    def test_sticky_plate_only_with_room(self):
        tall = self.probe(self.PATH, 1440, 900)
        self.assertEqual(tall.page.evaluate("getComputedStyle(document.querySelector('#record-03 .fv-ex2-chapter__plate')).position"), "sticky")
        tall.page.evaluate("document.getElementById('record-03').scrollIntoView()")
        tall.page.evaluate("window.scrollBy(0, 300)")
        tall.page.wait_for_timeout(200)
        top = tall.page.evaluate("document.querySelector('#record-03 .fv-ex2-chapter__plate').getBoundingClientRect().top")
        self.assertTrue(0 < top < 200, f"plate should be pinned near the top, got {top}")
        short = self.probe(self.PATH, 1440, 500)
        self.assertEqual(short.page.evaluate("getComputedStyle(document.querySelector('#record-03 .fv-ex2-chapter__plate')).position"), "static")
        phone = self.probe(self.PATH, 390, 844)
        self.assertEqual(phone.page.evaluate("getComputedStyle(document.querySelector('#record-03 .fv-ex2-chapter__plate')).position"), "static")

    def test_no_javascript_is_a_complete_document(self):
        for w, h in [(390, 844), (1440, 900)]:
            with self.subTest(width=w):
                p = self.probe(self.PATH, w, h, js=False)
                stats = p.page.evaluate("""() => ({
                    figures: [...document.querySelectorAll('.fv-ex2-plate figure')].filter(f => f.getBoundingClientRect().width > 0).length,
                    openers: [...document.querySelectorAll('[data-fvx-open-source]')].filter(b => b.getBoundingClientRect().width > 0).length,
                    chronoTool: document.querySelector('[data-fvx-chrono-tool]').getBoundingClientRect().width,
                    markers: [...document.querySelectorAll('[data-fvx-marker]')].filter(m => m.getBoundingClientRect().width > 0).length,
                    nasaLinks: document.querySelectorAll('a[href^="https://www.nasa.gov/"]').length,
                    overflow: document.documentElement.scrollWidth - innerWidth,
                    templatesRendered: [...document.querySelectorAll('template')].filter(t => t.getBoundingClientRect().width > 0).length})""")
                self.assertEqual(stats["figures"], 6)
                self.assertEqual(stats["openers"], 0, "dead buttons must not appear without JS")
                self.assertEqual(stats["chronoTool"], 0)
                self.assertEqual(stats["markers"], 4)
                self.assertGreaterEqual(stats["nasaLinks"], 6)
                self.assertLessEqual(stats["overflow"], 0)
                self.assertEqual(stats["templatesRendered"], 0)

    def test_missing_intersection_observer_fails_open(self):
        p = self.probe(self.PATH, init_script="delete window.IntersectionObserver;")
        stats = p.page.evaluate("""() => ({figures: [...document.querySelectorAll('.fv-ex2-plate figure')].filter(f => f.getBoundingClientRect().width > 0).length,
            current: document.querySelectorAll('.fv-ex2-chapterbar [aria-current]').length, ready: document.querySelector('[data-fvx]').getAttribute('data-fvx-ready')})""")
        self.assertEqual(stats["figures"], 6)
        self.assertEqual(stats["current"], 0)
        # the other modules must still work
        p.page.locator('[data-fvx-open-source="record-03"]').scroll_into_view_if_needed()
        p.page.locator('[data-fvx-open-source="record-03"]').click()
        self.assertTrue(p.page.locator("dialog[data-fvx-drawer]").evaluate("d => d.open"))

    def test_throwing_observer_does_not_break_other_modules(self):
        p = self.probe(self.PATH, init_script="window.IntersectionObserver = class { constructor() { throw new Error('simulated'); } };")
        self.assertEqual(p.page.evaluate("document.querySelector('[data-fvx]').getAttribute('data-fvx-ready')"), "partial")
        self.assertEqual(p.page.evaluate("[...document.querySelectorAll('.fv-ex2-plate figure')].filter(f => f.getBoundingClientRect().width > 0).length"), 6)
        p.page.locator('[data-fvx-open-source="record-01"]').click()
        self.assertTrue(p.page.locator("dialog[data-fvx-drawer]").evaluate("d => d.open"))
        self.assertTrue(any("simulated" in m for m in p.problems), "the failure should be reported once to the console")

    def test_reduced_motion_removes_animation(self):
        p = self.probe(self.PATH, reduced="reduce")
        names = p.page.evaluate("""() => [document.querySelector('.fv-ex2-hero__title'), document.querySelector('#record-02 .fv-ex2-chapter__title'),
            document.querySelector('#record-02 .fv-ex2-plate__frame img')].map(e => getComputedStyle(e).animationName)""")
        self.assertEqual(names, ["none", "none", "none"])
        self.assertNotEqual(p.page.evaluate("document.querySelector('[data-fvx]').getAttribute('data-fvx-motion')"), "on")

    def test_motion_enabled_when_allowed_never_hides_text(self):
        p = self.probe(self.PATH, reduced="no-preference")
        p.page.evaluate("document.getElementById('record-05').scrollIntoView()")
        p.page.wait_for_timeout(300)
        opacity = p.page.evaluate("Math.min(...[...document.querySelectorAll('.fv-ex2-chapter__text > *')].map(e => parseFloat(getComputedStyle(e).opacity)))")
        self.assertEqual(opacity, 1, "scroll-linked reveal must move text, never fade it")
        self.assertEqual(p.page.evaluate("document.querySelector('[data-fvx]').getAttribute('data-fvx-motion')"), "on")

    def test_plate_space_is_reserved_before_the_image_loads(self):
        """Regression for CLS 0.226 on cold loads: the image box collapsed until its file arrived, so the label and controls below
        jumped. With every image request aborted, each plate frame must still hold its full aspect-ratio box."""
        for w, h, touch in [(1440, 900, False), (390, 844, True)]:
            with self.subTest(width=w):
                p = Probe(self.PATH, w, h, touch=touch, stubs=False)
                self.addCleanup(p.close)
                p.ctx.route("https://images-assets.nasa.gov/**", lambda route: route.abort())
                p.ctx.route("https://finalvestige.com/wp-content/**", lambda route: route.abort())
                p.page.reload(wait_until="load")
                frames = p.page.evaluate("""() => [...document.querySelectorAll('.fv-ex2-plate__frame')].map(f => {
                    const r = f.getBoundingClientRect(), cs = getComputedStyle(f);
                    return {w: r.width, h: r.height, ratio: parseFloat(cs.getPropertyValue('--fvx-h')) / parseFloat(cs.getPropertyValue('--fvx-w'))}; })""")
                self.assertEqual(len(frames), 6)
                for f in frames:
                    self.assertGreater(f["w"], 100)
                    self.assertAlmostEqual(f["h"] / f["w"], f["ratio"], delta=0.02, msg=f"frame collapsed before load: {f}")
    def test_scrolling_is_never_blocked(self):
        d = self.probe(self.PATH, 1440, 900)
        d.page.mouse.move(700, 500)
        d.page.mouse.wheel(0, 1500)
        d.page.wait_for_timeout(300)
        self.assertGreater(d.page.evaluate("scrollY"), 500)
        m = self.probe(self.PATH, 390, 844, touch=True)
        m.page.evaluate("window.scrollTo(0, 2500)")
        self.assertGreater(m.page.evaluate("scrollY"), 1000)
        self.assertNotEqual(m.page.evaluate("getComputedStyle(document.documentElement).overflow"), "hidden")
        self.assertNotEqual(m.page.evaluate("getComputedStyle(document.body).touchAction"), "none")

    def test_touch_targets_are_at_least_44px(self):
        p = self.probe(self.PATH, 390, 844, touch=True)
        small = p.page.evaluate("""() => [...document.querySelectorAll('button:not([hidden]), .fv-ex2-chapterbar a, .fv-ex2-button, input')]
            .filter(e => e.getBoundingClientRect().width > 0)
            .map(e => [e.textContent.trim().slice(0, 24) || e.getAttribute('type'), Math.round(e.getBoundingClientRect().width), Math.round(e.getBoundingClientRect().height)])
            .filter(([, w, h]) => w < 44 || h < 44)""")
        self.assertEqual(small, [])

    def test_all_external_links_are_safe(self):
        p = self.probe(self.PATH)
        bad = p.page.evaluate("""() => [...document.querySelectorAll('a[target="_blank"]')].filter(a => !/noopener/.test(a.rel) || !/noreferrer/.test(a.rel)).map(a => a.href)""")
        self.assertEqual(bad, [])
        insecure = p.page.evaluate("[...document.querySelectorAll('a[href], img[src], link[href], script[src]')].map(e => e.href || e.src).filter(u => u.startsWith('http://') && !u.startsWith('http://127.0.0.1'))")
        self.assertEqual(insecure, [])

    def test_prototype_regression_chapter_figure_matches_chapter(self):
        """The removed sticky-viewer design could show exhibit 01 beside later chapters. Each plate is now inside its own chapter."""
        p = self.probe(self.PATH)
        pairs = p.page.evaluate("""() => [...document.querySelectorAll('[data-fvx-chapter]')].map(c => [c.id, c.querySelectorAll('.fv-ex2-plate figure').length,
            c.querySelector('.fv-ex2-plate__id').textContent])""")
        ids = [x[2].split("·")[0].strip() for x in pairs]
        self.assertEqual([x[1] for x in pairs], [1] * 6)
        self.assertEqual(len(set(ids)), 6, ids)
        data = support.lib.load_apollo1()
        self.assertEqual(ids, [f"NASA {r['image']['nasa_id']}" for r in data["records"]])


class Desk(Base):
    PATH = support.PAGES["desk"]

    def test_search_counts_empty_state_and_reset(self):
        p = self.probe(self.PATH)
        page = p.page
        search = page.locator("[data-fvx-search]")
        status = page.locator("[data-fvx-status]")
        self.assertEqual(status.inner_text(), "6 of 6 evidence records")
        search.fill("hatch")
        shown = page.locator("[data-fvx-item]:not([hidden])").count()
        self.assertTrue(0 < shown < 6)
        self.assertEqual(status.inner_text(), f"{shown} of 6 evidence records")
        search.fill("zzzzqqq")
        self.assertEqual(page.locator("[data-fvx-item]:not([hidden])").count(), 0)
        self.assertTrue(page.locator("[data-fvx-empty]").is_visible())
        search.fill("")
        self.assertEqual(status.inner_text(), "6 of 6 evidence records")
        self.assertFalse(page.locator("[data-fvx-empty]").is_visible())

    def test_native_details_and_limitations_without_js(self):
        p = self.probe(self.PATH, js=False)
        self.assertEqual(p.page.locator("[data-fvx-item]:visible").count(), 6)
        self.assertEqual(p.page.locator("[data-fvx-tools]:visible").count(), 0)
        self.assertEqual(p.page.locator(".fv-ex2-callout:visible").count(), 6)
        p.page.locator(".fv-ex2-record details summary").first.click()
        self.assertTrue(p.page.locator(".fv-ex2-record details").first.evaluate("d => d.open"))

    def test_two_instances_filter_independently(self):
        data = support.lib.load_apollo1()
        html = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>t</title>'
                '<link rel="stylesheet" href="../assets/fv-ex2.css"></head><body>' + render_desk(data, "apollo1") + render_desk(data, "apollo1-2")
                + '<script src="../assets/fv-ex2.js" defer></script></body></html>')
        tmp = support.DIST / "_tests"
        tmp.mkdir(exist_ok=True)
        (tmp / "two-desks.html").write_text(html, encoding="utf-8")
        p = self.probe("_tests/two-desks.html")
        ids = p.page.evaluate("[...document.querySelectorAll('[id]')].map(e => e.id)")
        self.assertEqual(len(ids), len(set(ids)), "duplicate ids with two desks on one page")
        first, second = p.page.locator('[data-fvx="desk"]').nth(0), p.page.locator('[data-fvx="desk"]').nth(1)
        first.locator("[data-fvx-search]").fill("hatch")
        self.assertLess(first.locator("[data-fvx-item]:not([hidden])").count(), 6)
        self.assertEqual(second.locator("[data-fvx-item]:not([hidden])").count(), 6)
        self.assertEqual(second.locator("[data-fvx-status]").inner_text(), "6 of 6 evidence records")


class Atlas(Base):
    PATH = support.PAGES["atlas"]

    def _dataset(self):
        return json.loads((support.EX2 / "atlas" / "data" / "atlas.json").read_text(encoding="utf-8"))

    def test_filter_search_and_pressed_state(self):
        ds = self._dataset()
        expect = sum(1 for i in ds["investigations"] if "catastrophe" in i["themes"])
        p = self.probe(self.PATH)
        page = p.page
        chip = page.get_by_role("button", name="Catastrophe")
        chip.click()
        self.assertEqual(chip.get_attribute("aria-pressed"), "true")
        self.assertEqual(page.get_by_role("button", name="All").get_attribute("aria-pressed"), "false")
        self.assertEqual(page.locator("[data-fvx-item]:not([hidden])").count(), expect)
        self.assertEqual(page.locator("[data-fvx-status]").inner_text(), f"{expect} of 6 investigations")
        page.locator("[data-fvx-search]").fill("petra")
        self.assertEqual(page.locator("[data-fvx-item]:not([hidden])").count(), 0, "petra is not tagged Catastrophe")
        self.assertTrue(page.locator("[data-fvx-empty]").is_visible())
        page.get_by_role("button", name="All").click()
        self.assertEqual(page.locator("[data-fvx-item]:not([hidden])").count(), 1)

    def test_no_map_and_no_pin_without_verified_geography(self):
        p = self.probe(self.PATH)
        self.assertEqual(p.page.locator("canvas, svg, .leaflet-container, [class*='pin'], [class*='marker'], [data-lat], [data-lon]").count(), 0)
        self.assertEqual(p.page.locator("[data-location-status='unverified_reference']").count(), 6)
        self.assertIn("0 of 6 places qualify", p.page.locator("main").inner_text())

    def test_no_javascript_lists_every_investigation_with_real_links(self):
        p = self.probe(self.PATH, js=False)
        self.assertEqual(p.page.locator(".fv-ex2-atlascard:visible").count(), 6)
        hrefs = p.page.evaluate("[...document.querySelectorAll('.fv-ex2-atlascard__title a')].map(a => a.href)")
        self.assertTrue(all(h.startswith("https://finalvestige.com/20") for h in hrefs), hrefs)
        self.assertEqual(p.page.locator("[data-fvx-tools]:visible").count(), 0)


class Accessibility(Base):
    TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"]

    @classmethod
    def setUpClass(cls):
        from fetch_axe import ensure_axe
        cls.axe = ensure_axe()  # a failed download raises: the accessibility suite cannot be skipped
        cls.results: dict = {}

    @classmethod
    def tearDownClass(cls):
        (support.DIST / "a11y-results.json").write_text(json.dumps(cls.results, indent=2, sort_keys=True), encoding="utf-8")

    def run_axe(self, p: Probe, label: str):
        p.page.add_script_tag(path=str(self.axe))
        res = p.page.evaluate("axe.run(document, {runOnly: {type: 'tag', values: %s}})" % json.dumps(self.TAGS))
        self.results[label] = {
            "violations": [{"id": v["id"], "impact": v["impact"], "nodes": [n["target"] for n in v["nodes"]][:5]} for v in res["violations"]],
            "passes": len(res["passes"]), "incomplete": [{"id": i["id"], "nodes": len(i["nodes"])} for i in res["incomplete"]],
            "axe": res["testEngine"]["version"],
        }
        self.assertEqual(self.results[label]["violations"], [], label)

    def test_axe_all_pages_desktop_and_mobile(self):
        for name, path in support.PAGES.items():
            for w, h, touch in [(1440, 900, False), (390, 844, True)]:
                with self.subTest(page=name, width=w):
                    p = self.probe(path, w, h, touch=touch, reduced="reduce")
                    p.scroll_through()
                    self.run_axe(p, f"{name}@{w}")

    def test_axe_with_drawer_open(self):
        p = self.probe(support.PAGES["flagship"], 1440, 900, reduced="reduce")
        p.page.locator('[data-fvx-open-source="record-04"]').click()
        self.run_axe(p, "flagship-drawer@1440")

    def test_axe_with_motion_enabled(self):
        p = self.probe(support.PAGES["flagship"], 1440, 900, reduced="no-preference")
        p.scroll_through()
        self.run_axe(p, "flagship-motion@1440")

    def test_accessible_names_and_landmarks(self):
        p = self.probe(support.PAGES["flagship"])
        info = p.page.evaluate("""() => ({
            nav: [...document.querySelectorAll('nav')].map(n => n.getAttribute('aria-label')),
            main: document.querySelectorAll('main').length,
            skip: document.querySelector('.fv-ex2-skip').getAttribute('href'),
            sections: [...document.querySelectorAll('section[aria-labelledby]')].every(s => document.getElementById(s.getAttribute('aria-labelledby'))),
            decorativeHero: document.querySelector('.fv-ex2-hero__media img').getAttribute('alt')})""")
        self.assertEqual(info["nav"], ["Experience navigation", "Records"])
        self.assertEqual(info["main"], 1)
        self.assertEqual(info["skip"], "#fvx-main")
        self.assertTrue(info["sections"])
        self.assertEqual(info["decorativeHero"], "")

    def test_skip_link_is_first_tab_stop_and_works(self):
        p = self.probe(support.PAGES["flagship"])
        p.page.keyboard.press("Tab")
        self.assertEqual(p.page.evaluate("document.activeElement.className"), "fv-ex2-skip")
        p.page.keyboard.press("Enter")
        self.assertEqual(p.page.evaluate("location.hash"), "#fvx-main")

    def test_focus_is_always_visible_on_controls(self):
        p = self.probe(support.PAGES["desk"])
        p.page.locator("[data-fvx-search]").focus()
        outline = p.page.evaluate("getComputedStyle(document.activeElement).outlineStyle + ' ' + getComputedStyle(document.activeElement).outlineWidth")
        self.assertEqual(outline, "solid 3px")


if __name__ == "__main__":
    unittest.main()
