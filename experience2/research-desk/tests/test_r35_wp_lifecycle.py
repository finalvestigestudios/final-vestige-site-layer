"""Runnable tests against unchanged PR #158 source plus R35 patch.

Tests are lifecycle probes, not a complete WordPress install.
"""
import json
import hashlib
import pathlib
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "final-vestige-ex2-research-desk.php"
PROBE = pathlib.Path(__file__).with_name("r35_wp_lifecycle_probe.php")


def run_case(case):
    p = subprocess.run(["php", str(PROBE), str(PLUGIN), case], capture_output=True, text=True, check=True)
    return json.loads(p.stdout)


class R35LifecycleTest(unittest.TestCase):
    def test_singular_direct_loads_before_render(self):
        got = run_case("direct")
        self.assertTrue(got["direct_literal_shortcode"])
        self.assertTrue(got["early_css_and_js"])

    def test_singular_nested_reusable_block_without_literal_loads_before_render(self):
        got = run_case("reusable")
        self.assertFalse(got["direct_literal_shortcode"])
        self.assertTrue(got["early_css_and_js"])

    def test_singular_dynamic_block_without_literal_loads_before_render(self):
        got = run_case("dynamic")
        self.assertFalse(got["direct_literal_shortcode"])
        self.assertTrue(got["early_css_and_js"])

    def test_archive_keeps_unstyled_content_instead_of_suppressing(self):
        got = run_case("archive")
        self.assertFalse(got["singular"])
        self.assertFalse(got["styles"])
        self.assertFalse(got["scripts"])
        self.assertTrue(got["has_static_ledger"] or got["fallback_url"])

    def test_asset_urls_are_first_party_and_versioned(self):
        got = run_case("direct")
        for handle, value in [*got["styles"].items(), *got["scripts"].items()]:
            self.assertEqual(handle, "fv-ex2-research-desk")
            self.assertTrue(value["url"].startswith("https://staging.example.test/wp-content/plugins/research-desk/assets/"))
            self.assertEqual(value["version"], "0.0.3-research")
        self.assertTrue(got["scripts"]["fv-ex2-research-desk"]["footer"])

    def test_static_output_remains_independent_of_literal_shortcode(self):
        direct, dynamic = run_case("direct"), run_case("dynamic")
        self.assertEqual(direct["rendered_sha256"], dynamic["rendered_sha256"])
        self.assertGreater(direct["content_length"], 0)

    def test_php_lint(self):
        for f in (PLUGIN, PROBE):
            p = subprocess.run(["php", "-l", str(f)], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_r37_reviewed_assets_match_exact_git_blobs(self):
        # Detect accidental drift in the NASA evidence and progressive-enhancement source.
        pinned = {
            "assets/source-ledger.css": "e1e448f1ab14061d5ddd94fb51b652799f859791",
            "assets/source-ledger.js": "98e5cde97eb487df1a2854400833fd8ed1f06c69",
            "templates/ledger.html": "8b14587187b375e93cfbd4436b99bfb6cd3d2f32",
        }
        missing = [rel for rel in pinned if not (ROOT / rel).is_file()]
        if missing:
            self.skipTest("R37 reviewed assets not mounted in the local partial checkout: " + ', '.join(missing))
        for rel, expected in pinned.items():
            b = (ROOT / rel).read_bytes()
            actual = hashlib.sha1(f"blob {len(b)}\0".encode() + b).hexdigest()
            self.assertEqual(actual, expected, "Reviewed R37 source unexpectedly changed: " + rel)

    def test_six_nasa_records_when_original_template_available(self):
        source = ROOT / "templates/ledger.html"
        if not source.is_file():
            self.skipTest("Original PR #158 ledger.html missing locally")
        text = source.read_text()
        self.assertEqual(text.count('data-fvx-record '), 6)
        self.assertIn('https://www.nasa.gov/', text)
        self.assertIn('S67-19766', text)

    def test_no_external_http_requests(self):
        src = PLUGIN.read_text()
        for bad in ("curl_exec(", "wp_remote_get(", "wp_remote_post(", "file_get_contents('https:"):
            self.assertNotIn(bad, src)


if __name__ == '__main__':
    unittest.main()
