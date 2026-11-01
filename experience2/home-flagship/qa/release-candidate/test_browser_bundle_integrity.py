"""Fail-closed release-manifest and CSP regression checks; no production access."""
import hashlib
import importlib.util
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
if "playwright.sync_api" not in sys.modules:
    fake = types.ModuleType("playwright.sync_api")
    fake.sync_playwright = lambda: None
    sys.modules.setdefault("playwright", types.ModuleType("playwright"))
    sys.modules["playwright.sync_api"] = fake
spec = importlib.util.spec_from_file_location("fv_offline_browser", HERE / "verify_release_surface_browser.py")
browser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(browser)

class BundleIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = '<!doctype html><html><head></head><body>' + ''.join(
            '<link rel="stylesheet" href="./%s">' % n for n in browser.STYLES
        ) + ''.join('<script src="./%s" defer></script>' % n for n in browser.SCRIPTS) + '</body></html>'
        self.files = {"index.release-review.html": self.source.encode(),
                      "wordpress-page-fragment.review-only.html": b"<div>review</div>"}
        for name in browser.STYLES: self.files[name] = b".test { display: block; }"
        for name in browser.SCRIPTS: self.files[name] = b"window.fvTest = true;"
        self.commit()

    def commit(self):
        for name, data in self.files.items():
            (self.root / name).write_bytes(data)
        self.manifest = {"sourceGitBlob": "synthetic", "sourceSha256": "synthetic",
                         "assetGitBlobs": {},
                         "files": {n: {"bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}
                                   for n,b in self.files.items()}}
        (self.root / "SOURCE_MANIFEST.json").write_text(json.dumps(self.manifest))

    def test_exact_complete_bundle_passes(self):
        output, record = browser.create_page(self.root)
        self.assertIn('http-equiv="Content-Security-Policy"', output)
        self.assertEqual(output.count('data-fv-exact-asset='), 10)

    def test_missing_source_manifest_entry_is_rejected(self):
        del self.manifest["files"]["flagship.js"]
        (self.root / "SOURCE_MANIFEST.json").write_text(json.dumps(self.manifest))
        with self.assertRaises(AssertionError): browser.create_page(self.root)

    def test_unexpected_manifest_entry_is_rejected(self):
        self.manifest["files"]["../outside"] = {"bytes": 0, "sha256": "0"*64}
        (self.root / "SOURCE_MANIFEST.json").write_text(json.dumps(self.manifest))
        with self.assertRaises(AssertionError): browser.create_page(self.root)

    def test_tampered_asset_is_rejected(self):
        (self.root / "flagship.js").write_text("tampered")
        with self.assertRaises(AssertionError): browser.create_page(self.root)

    def test_symlinked_asset_is_rejected(self):
        link = self.root / "flagship.js"
        data = self.root / "outside.txt"
        data.write_bytes(self.files["flagship.js"])
        link.unlink()
        try: link.symlink_to(data)
        except (OSError, NotImplementedError): self.skipTest("symlinks unavailable")
        with self.assertRaises(AssertionError): browser.create_page(self.root)

    def test_missing_head_boundary_is_rejected(self):
        self.files["index.release-review.html"] = self.source.replace("</head>", "").encode()
        self.commit()
        with self.assertRaises(AssertionError): browser.create_page(self.root)

    def test_duplicate_head_boundary_is_rejected(self):
        self.files["index.release-review.html"] = self.source.replace("</head>", "</head></head>").encode()
        self.commit()
        with self.assertRaises(AssertionError): browser.create_page(self.root)

    def test_preexisting_csp_rejected(self):
        self.files["index.release-review.html"] = self.source.replace("</head>", '<meta http-equiv="Content-Security-Policy" content="default-src *"></head>').encode()
        self.commit()
        with self.assertRaises(AssertionError): browser.create_page(self.root)

    def test_invalid_digest_metadata_rejected(self):
        self.manifest["files"]["flagship.css"]["sha256"] = "abc"
        (self.root / "SOURCE_MANIFEST.json").write_text(json.dumps(self.manifest))
        with self.assertRaises(AssertionError): browser.create_page(self.root)

if __name__ == "__main__": unittest.main()
