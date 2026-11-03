"""WordPress staging plugin tests using the real PHP binary against WordPress stubs (see tests/php/run.php).

These prove the plugin's own logic. They do not prove behaviour inside WordPress.com Atomic or the Assembler theme."""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import support

PHP = None


def php() -> str:
    global PHP
    if PHP is None:
        PHP = support.find_php()
    return PHP


def run(plugin_dir: Path, scenario: str) -> dict:
    proc = subprocess.run([php(), str(support.EX2 / "tests" / "php" / "run.php"), str(plugin_dir), scenario], capture_output=True, text=True)
    if proc.returncode:
        raise AssertionError(f"php exited {proc.returncode}: {proc.stderr or proc.stdout}")
    return json.loads(proc.stdout)


class Plugin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        support.build()

    def test_every_php_file_lints(self):
        files = list(support.PLUGIN.rglob("*.php"))
        self.assertGreaterEqual(len(files), 4)
        for f in files:
            proc = subprocess.run([php(), "-l", str(f)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_no_php_files_outside_known_set_and_no_forbidden_calls(self):
        forbidden = ("eval(", "base64_decode", "shell_exec", "system(", "exec(", "passthru", "file_put_contents", "unserialize", "curl_", "wp_remote_", "$_GET", "$_POST", "$_REQUEST", "update_option", "add_option", "register_rest_route")
        for f in support.PLUGIN.rglob("*.php"):
            text = f.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text, f"{f.name} uses {token}")

    def test_two_instances_have_unique_ids_and_enqueue_assets(self):
        out = run(support.PLUGIN, "render")
        self.assertEqual(sorted(out["shortcodes"]), ["fv_ex2_atlas", "fv_ex2_research_desk"])
        self.assertTrue(out["first_has_title"])
        self.assertTrue(out["second_has_title"])
        self.assertEqual(out["duplicate_ids"], [])
        self.assertFalse(out["placeholder_left"])
        self.assertTrue(out["atlas_ok"])
        self.assertIn("fv-ex2", out["enqueued"]["style"])

    def test_assets_load_only_where_used(self):
        hit = run(support.PLUGIN, "assets-hit")
        self.assertEqual(hit["enqueued"]["style"], ["fv-ex2"])
        self.assertEqual(hit["registered"]["fv-ex2"]["args"], {"in_footer": True, "strategy": "defer"})
        miss = run(support.PLUGIN, "assets-miss")
        self.assertEqual(miss["enqueued"], {"style": [], "script": []})

    def test_asset_version_tracks_content_hash(self):
        manifest = json.loads((support.PLUGIN / "assets" / "manifest.json").read_text(encoding="utf-8"))
        ver = run(support.PLUGIN, "assets-hit")["registered"]["fv-ex2"]["ver"]
        self.assertEqual(ver, manifest["css"]["sha256"][:10] + "-" + manifest["js"]["sha256"][:10])

    def test_shortcode_attributes_are_ignored(self):
        out = run(support.PLUGIN, "injection")
        self.assertFalse(out["contains_script"])
        self.assertFalse(out["contains_payload"])
        self.assertTrue(out["has_desk_markup"])

    def _copy_plugin(self) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix="fvx-plugin-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        dest = tmp / "final-vestige-experience-2"
        shutil.copytree(support.PLUGIN, dest)
        return dest

    def test_missing_template_falls_back_to_article_link(self):
        dest = self._copy_plugin()
        (dest / "templates" / "research-desk.html").unlink()
        out = run(dest, "fallback-probe")
        self.assertTrue(out["is_fallback"] and out["has_article_link"] and out["no_desk_markup"])
        self.assertEqual(out["enqueued"], {"style": [], "script": []}, "a fallback must not load component assets")

    def test_tampered_template_is_refused(self):
        dest = self._copy_plugin()
        path = dest / "templates" / "research-desk.html"
        path.write_text(path.read_text(encoding="utf-8").replace("The proof", "The unreviewed proof"), encoding="utf-8")
        out = run(dest, "fallback-probe")
        self.assertTrue(out["is_fallback"] and out["no_desk_markup"])

    def test_missing_manifest_fails_closed(self):
        dest = self._copy_plugin()
        (dest / "assets" / "manifest.json").unlink()
        self.assertTrue(run(dest, "fallback-probe")["is_fallback"])

    def test_empty_template_falls_back(self):
        dest = self._copy_plugin()
        (dest / "templates" / "research-desk.html").write_text("", encoding="utf-8")
        self.assertTrue(run(dest, "fallback-probe")["is_fallback"])

    def test_plugin_templates_embed_cleanly_in_a_post(self):
        for name in ("research-desk", "atlas"):
            html = (support.PLUGIN / "templates" / f"{name}.html").read_text(encoding="utf-8")
            self.assertNotIn("<h1", html, "a post already owns the h1")
            self.assertNotIn('href="../', html, "relative standalone links do not resolve inside WordPress")
            self.assertNotIn("<main", html, "the theme owns the main landmark")
            self.assertIn("{{fvx-instance}}", html)


if __name__ == "__main__":
    unittest.main()
