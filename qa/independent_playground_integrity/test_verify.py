"""Synthetic-only negative controls: no WordPress instance, network or user data."""
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from verify import verify, Hold

HEAD = "a" * 40


def zip_data(files):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w", zipfile.ZIP_DEFLATED) as z:
        for n, d in files.items():
            z.writestr(n, d)
    return b.getvalue()


class StageIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.stage = self.root / "stage"
        self.stage.mkdir()
        self.zip = self.root / "assembler.zip"
        self.theme_files = {"style.css": b"/* Theme Name: Assembler */", "templates/index.html": b"<!-- wp:post-content /-->"}
        self.zip.write_bytes(zip_data({"assembler/" + n: data for n, data in self.theme_files.items()}))
        self.sha = hashlib.sha256(self.zip.read_bytes()).hexdigest()
        self.mount = self.stage / "mounts" / "assembler"
        for name, data in self.theme_files.items():
            p = self.mount / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        self.receipt = {"exact_git_head": HEAD, "assembler_zip_sha256": self.sha,
                        "release": "HOLD", "wordpress_instance": "NOT_STARTED"}
        self.args = ["npx", "@wp-playground/cli@1.2.3", "server", "--port=9400"]
        self.blueprint = {"login": True, "steps": [{"step": "defineWpConfigConsts", "consts": {"WP_ENVIRONMENT_TYPE": "local"}},
                                                    {"step": "activateTheme", "themeFolderName": "assembler"}]}
        self.save()

    def save(self):
        for name, data in [("STAGING_PREP_RECEIPT.json", self.receipt),
                           ("playground-cli-arguments.json", self.args),
                           ("playground-blueprint.json", self.blueprint)]:
            (self.stage / name).write_text(json.dumps(data))

    def check(self):
        self.save()
        return verify(self.stage, self.zip, self.sha, HEAD)

    def test_valid_offline_fixture_admitted_but_release_hold(self):
        self.assertEqual(self.check()["release"], "HOLD")

    def test_trusted_digest_required(self):
        with self.assertRaisesRegex(Hold, "REQUIRED"):
            verify(self.stage, self.zip, "", HEAD)

    def test_substituted_zip_rejected(self):
        self.zip.write_bytes(zip_data({"assembler/style.css": b"fake"}))
        with self.assertRaisesRegex(Hold, "trusted digest"):
            self.check()

    def test_mounted_theme_modified_rejected(self):
        (self.mount / "style.css").write_text("tamper")
        with self.assertRaisesRegex(Hold, "Mounted theme bytes"):
            self.check()

    def test_extra_theme_file_rejected(self):
        (self.mount / "functions.php").write_text("<?php // arbitrary")
        with self.assertRaisesRegex(Hold, "file set"):
            self.check()

    def test_latest_cli_rejected(self):
        self.args[1] = "@wp-playground/cli@latest"
        with self.assertRaisesRegex(Hold, "pinned"):
            self.check()

    def test_version_range_rejected(self):
        self.args[1] = "@wp-playground/cli@^1.2.3"
        with self.assertRaisesRegex(Hold, "pinned"):
            self.check()

    def test_head_mismatch_rejected(self):
        self.receipt["exact_git_head"] = "b" * 40
        with self.assertRaisesRegex(Hold, "provenance"):
            self.check()

    def test_nonhold_release_rejected(self):
        self.receipt["release"] = "GO"
        with self.assertRaisesRegex(Hold, "HOLD"):
            self.check()

    def test_not_started_required(self):
        self.receipt["wordpress_instance"] = "RUNNING"
        with self.assertRaisesRegex(Hold, "unstarted"):
            self.check()

    def test_remote_blueprint_rejected(self):
        self.blueprint["steps"][0]["consts"]["WP_ENVIRONMENT_TYPE"] = "production"
        with self.assertRaisesRegex(Hold, "Local-only"):
            self.check()

    def test_import_rejected(self):
        self.blueprint["steps"].append({"step": "importWxr"})
        with self.assertRaisesRegex(Hold, "data import"):
            self.check()

    def test_production_domain_rejected(self):
        self.blueprint["landingPage"] = "https://finalvestige.com/"
        with self.assertRaisesRegex(Hold, "Production domain"):
            self.check()


if __name__ == "__main__":
    unittest.main()
