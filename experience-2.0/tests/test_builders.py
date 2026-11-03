"""Builder, data-validation, bundle and static-analysis tests. No browser."""
from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
import unittest

import support  # noqa: F401  (sets sys.path)
import fvx_lib as lib
from render_desk import render_desk
from render_flagship import render_flagship


class UrlSafety(unittest.TestCase):
    def test_rejects_unsafe(self):
        for bad in ["http://www.nasa.gov/x", "javascript:alert(1)", "https://evil.example/preview", "https://nasa.gov.evil.test/report",
                    "https://u:p@www.nasa.gov/x", "https://www.nasa.gov", "https://www.nasa.gov/a b", "https://www.nasa.gov/\"onmouseover=1", "", None]:
            with self.assertRaises(lib.BadRecord, msg=bad):
                lib.safe_https(bad)

    def test_accepts_approved(self):
        self.assertTrue(lib.safe_https("https://www.nasa.gov/missions/apollo/"))
        self.assertTrue(lib.safe_https("https://images-assets.nasa.gov/image/S67-15717/S67-15717~large.jpg", lib.IMAGE_HOSTS))
        with self.assertRaises(lib.BadRecord):  # an image host is not a link host
            lib.safe_https("https://images-assets.nasa.gov/image/x.jpg")


class DataValidation(unittest.TestCase):
    def _mutate(self, fn):
        bad = copy.deepcopy(lib.load_apollo1())
        fn(bad)
        lib.load_apollo1(bad)

    def test_real_data_is_valid(self):
        data = lib.load_apollo1()
        self.assertEqual(len(data["records"]), 6)

    def test_every_record_has_limit_and_explicit_event_flag(self):
        for rec in lib.load_apollo1()["records"]:
            self.assertTrue(rec["caution"].strip())
            self.assertIsInstance(rec["image"]["depicts_event"], bool)

    def test_rejections(self):
        cases = {
            "missing limitation": lambda d: d["records"][0].pop("caution"),
            "unknown evidence kind": lambda d: d["records"][0].__setitem__("kind", "UNREVIEWED"),
            "http image": lambda d: d["records"][1]["image"].__setitem__("src", "http://images-assets.nasa.gov/a.jpg"),
            "foreign image host": lambda d: d["records"][1]["image"].__setitem__("src", "https://cdn.example.com/a.jpg"),
            "implicit depicts_event": lambda d: d["records"][0]["image"].__setitem__("depicts_event", "no"),
            "bad crosswalk status": lambda d: d["records"][0]["crosswalk"][0].__setitem__("status", "trust-me"),
            "duplicate id": lambda d: d["records"][1].__setitem__("id", d["records"][0]["id"]),
            "missing alt": lambda d: d["records"][2]["image"].__setitem__("alt", " "),
            "marker outside range": lambda d: d["chronology"]["markers"][-1].__setitem__("t", 99),
        }
        for name, fn in cases.items():
            with self.subTest(name), self.assertRaises(lib.BadRecord):
                self._mutate(fn)

    def test_prototype_image_mismatch_is_not_reintroduced(self):
        """KSC-20170124-PH_KLS01_0164 is a spacecraft mockup; the prototype wrongly captioned it as the original hatch."""
        blob = json.dumps(lib.load_apollo1())
        self.assertNotIn("KLS01_0164", blob.replace("Replaces KSC-20170124-PH_KLS01_0164", ""))
        hatch = lib.load_apollo1()["records"][3]["image"]
        self.assertEqual(hatch["nasa_id"], "KSC-20170124-PH_KLS01_0129")
        self.assertIn("2017", hatch["caption"])


class Rendering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = lib.load_apollo1()

    def test_instance_ids_are_unique_per_instance(self):
        a, b = render_desk(self.data, "apollo1"), render_desk(self.data, "apollo1-2")
        ids = re.findall(r'\sid="([^"]+)"', a + b)
        self.assertEqual(len(ids), len(set(ids)))

    def test_instance_must_be_a_slug(self):
        for bad in ["Apollo1", "a b", 'x"><script>', "../x", ""]:
            with self.assertRaises(lib.BadRecord):
                render_desk(self.data, bad)

    def test_html_is_escaped(self):
        data = copy.deepcopy(self.data)
        data["records"][0]["title"] = '<img src=x onerror=alert(1)>"'
        html = render_desk(data, "apollo1") + render_flagship(data, desk_url="d.html", atlas_url="a.html")
        self.assertNotIn("<img src=x", html)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", html)

    def test_flagship_structure(self):
        html = render_flagship(self.data, desk_url="../research-desk/index.html", atlas_url="../atlas/index.html")
        self.assertEqual(html.count('data-fvx-chapter '), 6)
        self.assertEqual(html.count("<h1"), 1)
        self.assertEqual(html.count("<template data-fvx-source="), 6)
        # no static element may advertise an interactive role
        for role in ("role=\"button\"", "role=\"tab\"", "role=\"slider\"", "tabindex=\"0\""):
            self.assertNotIn(role, html)
        # enhancement controls start hidden so no-JS users never see dead buttons
        self.assertEqual(len(re.findall(r'data-fvx-open-source="[^"]+" hidden', html)), 6)
        self.assertIn("data-fvx-chrono-tool hidden", html)

    def test_every_image_has_dimensions_and_alt(self):
        html = render_flagship(self.data, desk_url="d.html", atlas_url="a.html")
        for tag in re.findall(r"<img [^>]+>", html):
            self.assertRegex(tag, r'width="\d+"')
            self.assertRegex(tag, r'height="\d+"')
            self.assertIn("alt=", tag)

    def test_desk_honest_labels_for_exhibit_photos(self):
        html = render_desk(self.data, "apollo1")
        self.assertIn("Museum exhibit, 2017, not taken during the events described", html)


class Bundle(unittest.TestCase):
    def test_build_is_deterministic_and_plugin_payload_current(self):
        support.build()
        first = (lib.EX2 / "wp-plugin" / "final-vestige-experience-2" / "assets" / "manifest.json").read_text(encoding="utf-8")
        support._built = False
        support.build()
        self.assertEqual(first, (lib.EX2 / "wp-plugin" / "final-vestige-experience-2" / "assets" / "manifest.json").read_text(encoding="utf-8"))
        proc = subprocess.run([sys.executable, str(support.TOOLS / "build_all.py"), "--check"], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_size_budget(self):
        m = lib.bundle_manifest(lib.bundle_css(), lib.bundle_js())
        self.assertLess(m["css"]["gzip_bytes"] + m["js"]["gzip_bytes"], 20 * 1024, "Experience 2.0 CSS+JS must stay under 20 KB gzipped")

    def test_css_is_namespaced(self):
        allowed = re.compile(r"^(:where\(\.fv-ex2\)|\.fv-ex2|html\.fv-ex2-scroll-lock)")
        offenders = []
        for path in sorted(lib.CSS_SRC.glob("*.css")):
            text = re.sub(r"/\*.*?\*/", "", path.read_text(encoding="utf-8"), flags=re.S)
            # flatten @media/@supports wrappers so inner rules are checked too
            for block in re.finditer(r"([^{}@]+)\{", text):
                selector_list = block.group(1).strip()
                if not selector_list or re.fullmatch(r"(from|to|\d+%)(\s*,\s*(from|to|\d+%))*", selector_list) or selector_list.startswith("keyframes "):
                    continue
                if ":" in selector_list and selector_list.endswith(")") and "(" in selector_list and "." not in selector_list:
                    continue  # media-feature fragment
                for sel in (s.strip() for s in selector_list.split(",")):
                    if sel and not allowed.match(sel):
                        offenders.append(f"{path.name}: {sel}")
        self.assertEqual(offenders, [])

    def test_keyframes_and_properties_are_prefixed(self):
        css = "".join(p.read_text(encoding="utf-8") for p in lib.CSS_SRC.glob("*.css"))
        self.assertEqual([n for n in re.findall(r"@keyframes\s+([\w-]+)", css) if not n.startswith("fvx-")], [])
        self.assertEqual([n for n in re.findall(r"(?<![\w-])(--[\w-]+)\s*:", css) if not n.startswith("--fvx-")], [])

    def test_js_has_no_dangerous_apis(self):
        js = lib.bundle_js()
        for banned in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(", "new Function", "fetch(", "XMLHttpRequest",
                       "localStorage", "sessionStorage", "document.cookie", "sendBeacon", "WebSocket", "import("):
            self.assertNotIn(banned, js, banned)

    def test_contrast(self):
        tokens = lib.read_tokens()
        for fg, bg, minimum in lib.CONTRAST_PAIRS:
            self.assertGreaterEqual(lib.contrast(tokens[fg], tokens[bg]), minimum, f"{fg} on {bg}")

    def test_no_scroll_blocking_css(self):
        css = lib.bundle_css()
        self.assertIsNone(re.search(r"touch-action:\s*none", css))
        # the only rule allowed to lock page scroll is the open-dialog class, which script removes on close
        self.assertEqual(re.findall(r"([^{}]+)\{overflow:\s*hidden;?\}", css), ["html.fv-ex2-scroll-lock"])


if __name__ == "__main__":
    unittest.main()
