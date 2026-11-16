"""R402 security regression: local Python and real Chromium, no external HTTP."""
import importlib.util
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from network_custody import read_only_permits, inspect_trace, audit_run, EXPECTED_CONTEXTS

# Load R400's actual reviewed API from a checkout. Test fixture-only fallback
# can be provided with FV_R400_TEST_PATH; report shadow mismatch explicitly.
import os
p = Path(os.getenv("FV_R400_TEST_PATH") or Path(__file__).resolve().parents[2] / "apollo-r400" / "qa" / "staging_browser_gate.py")
if not p.is_file():
    raise RuntimeError("Missing R400 browser runner; checkout required")
spec = importlib.util.spec_from_file_location("staging_browser_gate", p)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
ORIGIN = "https://staging.finalvestige.example"
LANDING = ORIGIN + "/apollo-1-evidence-atlas/"
CSS_ROOT = ORIGIN + "/wp-content/plugins/fv-site-layer/experience2"


class StrictNetworkCustody(unittest.TestCase):
    def test_approved_document_and_two_styles(self):
        for method in ("GET", "HEAD"):
            self.assertTrue(read_only_permits(LANDING, method, LANDING, base))
            for path in base.CSS:
                version = base.CSS_VERSIONS[path] if hasattr(base, "CSS_VERSIONS") else base.CSS[path][0]
                url = CSS_ROOT + path + "?ver=" + version
                self.assertTrue(read_only_permits(url, method, LANDING, base), url)

    def test_unreviewed_same_origin_gets_rejected(self):
        paths = ["/wp-json/", "/wp-admin/admin-ajax.php", "/", "/wp-content/plugins/x/analytics.js",
                 "/wp-content/uploads/tracker.gif", "/feed/", "/robots.txt",
                 "/wp-content/plugins/fv-site-layer/experience2/apollo-r384/assets/other.css",
                 "/x/experience2/apollo-r384/assets/gallery.css",
                 "/wp-content/plugins/a/experience2/fake/experience2/apollo-r384/assets/gallery.css"]
        for path in paths:
            self.assertFalse(read_only_permits(ORIGIN + path, "GET", LANDING, base), path)
        for method in ("POST", "PUT", "PATCH", "DELETE", "OPTIONS"):
            self.assertFalse(read_only_permits(LANDING, method, LANDING, base), method)

    def test_query_and_host_tricks_rejected(self):
        good = CSS_ROOT + "/apollo-r384/assets/gallery.css?ver=r384-reviewed-1"
        for bad in [good + "&track=1", good.replace(ORIGIN, "http://staging.finalvestige.example"),
                    good.replace("staging.finalvestige.example", "evil.finalvestige.example"),
                    good.replace("fv-site-layer", "../fv-site-layer"),
                    good.replace("?ver=", "?cache=1&ver="),
                    good.replace("/experience2/", "/x/experience2/")]:
            self.assertFalse(read_only_permits(bad, "GET", LANDING, base), bad)

    def test_denied_trace_always_blocks_release(self):
        clean = {"network": [{"url": LANDING, "method": "GET", "allowed": True}],
                 "screens": [{"context": x} for x in EXPECTED_CONTEXTS],
                 "http_css_sha256": "MATCHED", "csp": "PRESENT", "axe": "PASS_GENUINE_ASSET"}
        self.assertEqual(inspect_trace(clean, True), [])
        bad = dict(clean, network=clean["network"] + [{"url": ORIGIN + "/wp-json/", "method": "GET", "allowed": False}])
        self.assertIn("unreviewed_network_requests_denied:1", inspect_trace(bad, True))
        for key in ("axe", "csp", "http_css_sha256"):
            mutated = dict(clean, **{key: "NOT_TESTED"})
            self.assertTrue(inspect_trace(mutated, True))

    def test_wrapper_restores_parent_request_policy_after_denial(self):
        import tempfile
        parent_policy = base.permits if hasattr(base, "permits") else base.approved_request
        class StubOverlay:
            def run(self, args):
                request_fn = base.permits if hasattr(base, "permits") else base.approved_request
                self.reported_narrow_policy = not request_fn(ORIGIN + "/wp-json/", "GET", LANDING)
                return {"network": [{"url": ORIGIN + "/wp-json/", "method": "GET", "allowed": False}],
                        "screens": [{"context": x} for x in EXPECTED_CONTEXTS],
                        "http_css_sha256": "MATCHED", "csp": "PRESENT", "axe": "PASS_GENUINE_ASSET",
                        "blockers": [], "status": "PASS_STAGING_BROWSER_GATE_ONLY"}
        stub = StubOverlay()
        with tempfile.TemporaryDirectory() as path:
            result = audit_run(SimpleNamespace(url=LANDING, out=path), stub, base)
            self.assertTrue(stub.reported_narrow_policy)
            self.assertEqual(result["status"], "HARD_HOLD_UNREVIEWED_NETWORK_OR_STAGING_PROOF")
            self.assertTrue((Path(path) / "r402-report.json").is_file())
        restored = base.permits if hasattr(base, "permits") else base.approved_request
        self.assertIs(restored, parent_policy)

    def test_parent_policy_restored_when_runner_raises(self):
        parent = base.permits if hasattr(base, "permits") else base.approved_request
        class Broken:
            def run(self, args):
                raise RuntimeError("deliberate browser fault")
        with self.assertRaisesRegex(RuntimeError, "deliberate"):
            audit_run(SimpleNamespace(url=None, out="/unused"), Broken(), base)
        restored = base.permits if hasattr(base, "permits") else base.approved_request
        self.assertIs(parent, restored)

    def test_real_chromium_denied_resources_not_silently_accepted(self):
        html = """<!doctype html><html lang=en><head><title>Apollo local network probe</title>
            <link rel=stylesheet href='https://staging.finalvestige.example/wp-content/plugins/fv-site-layer/experience2/apollo-r384/assets/gallery.css?ver=r384-reviewed-1'>
            <script src='https://staging.finalvestige.example/wp-json/rogue-analytics.js'></script></head><body>
            <main><h1>Apollo Evidence</h1><img src='https://staging.finalvestige.example/wp-content/uploads/track.gif' alt=''></main></body></html>"""
        css = CSS_ROOT + "/apollo-r384/assets/gallery.css?ver=r384-reviewed-1"
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, executable_path="/usr/bin/chromium", args=["--no-sandbox"])
            try:
                for width in (320, 390, 768, 1440, 1920):
                    context = browser.new_context(viewport={"width": width, "height": 760}, service_workers="block")
                    events = []
                    def route_request(route):
                        request = route.request
                        allowed = read_only_permits(request.url, request.method, LANDING, base)
                        events.append({"url": request.url, "method": request.method, "allowed": allowed})
                        if not allowed:
                            route.abort("blockedbyclient")
                        elif request.url == LANDING:
                            route.fulfill(status=200, content_type="text/html", body=html)
                        elif request.url == css:
                            route.fulfill(status=200, content_type="text/css", body="body{font-family:sans-serif}")
                        else:
                            route.abort("blockedbyclient")
                    context.route("**/*", route_request)
                    page = context.new_page()
                    # set_content avoids actual staging navigation: all URL requests are synthetic/blocked.
                    page.set_content(html, wait_until="load")
                    self.assertEqual(page.title(), "Apollo local network probe")
                    denied = [e for e in events if not e["allowed"]]
                    self.assertEqual(len(denied), 2, (width, events))
                    report = {"network": events, "screens": [{"context": x} for x in EXPECTED_CONTEXTS],
                              "http_css_sha256": "MATCHED", "csp": "PRESENT", "axe": "PASS_GENUINE_ASSET"}
                    self.assertIn("unreviewed_network_requests_denied:2", inspect_trace(report, True))
                    context.close()
            finally:
                browser.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
