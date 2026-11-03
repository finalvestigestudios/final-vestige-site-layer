"""Read-only fail-closed source and content freeze tests for all seven clusters."""
import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build
import validate
import evidence_freeze


class InputFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = build.Library()

    def changed_copy(self, modify):
        with tempfile.TemporaryDirectory(prefix="fv-pa-provenance-") as tmp:
            root = Path(tmp) / "preparedness"
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns("build", "__pycache__"))
            modify(root)
            return evidence_freeze.verify(build.Library(root=root))

    def test_original_full_input_baseline_is_stable(self):
        self.assertEqual(evidence_freeze.verify(self.lib), [])

    def test_exact_thirty_five_articles_plus_water_planner(self):
        lock = json.loads((ROOT / "sources" / "article-evidence-lock.json").read_text())
        self.assertEqual(len(lock["records"]), 41)
        self.assertEqual(lock["longform_article_count"], 35)
        self.assertEqual(lock["local_tool_count"], 6)

    def test_noncolliding_source_claim_change_is_detected(self):
        def change(root):
            f = root / "sources/register.json"
            d = json.loads(f.read_text(encoding="utf-8"))
            collisions = set(self.lib.crosswalk_groups)
            row = next(s for s in d["sources"] if s["url"] not in collisions)
            row["supports"] = (row.get("supports") or "") + " Unreviewed extra claim."
            f.write_text(json.dumps(d), encoding="utf-8")
        self.assertTrue(any("raw source bytes changed" in x for x in self.changed_copy(change)))

    def test_fragment_source_reading_notes_change_is_detected(self):
        def change(root):
            f = root / "sources/fragments/hist-home.json"
            d = json.loads(f.read_text(encoding="utf-8"))
            d["sources"][0]["notes"] = "Unreviewed new reading-depth claim"
            f.write_text(json.dumps(d), encoding="utf-8")
        self.assertTrue(any("raw source bytes changed" in x for x in self.changed_copy(change)))

    def test_new_fragment_needs_provenance_reaudit(self):
        def change(root):
            (root / "sources/fragments/extra.json").write_text('{"sources":[]}', encoding="utf-8")
        self.assertTrue(any("source file inventory" in x for x in self.changed_copy(change)))

    def test_body_edit_invalidates_locked_longform_copy(self):
        def change(root):
            f = root / "content/articles/making-water-safer.body.html"
            f.write_text(f.read_text(encoding="utf-8") + "\n<!-- altered after review -->", encoding="utf-8")
        self.assertTrue(any("article body bytes changed" in x for x in self.changed_copy(change)))

    def test_review_metadata_edit_invalidates_locked_approval(self):
        def change(root):
            f = root / "content/articles/making-water-safer.meta.json"
            d = json.loads(f.read_text(encoding="utf-8"))
            d["safety_review"]["state"] = "pending"
            f.write_text(json.dumps(d), encoding="utf-8")
        self.assertTrue(any("article metadata bytes changed" in x for x in self.changed_copy(change)))

    def test_unpaired_body_is_not_silently_accepted(self):
        def change(root):
            (root / "content/articles/untracked.body.html").write_text("none", encoding="utf-8")
        self.assertTrue(any("untracked or unpaired" in x for x in self.changed_copy(change)))

    def test_article_contributor_origin_change_rejected(self):
        lib = build.Library()
        lib.article_origins["go-bags"] = "hist-food"
        self.assertTrue(any("article origin changed" in x for x in evidence_freeze.verify(lib)))

    def test_existing_crosswalk_source_sha_cannot_be_redefined(self):
        lib = build.Library()
        lib.crosswalk["source_files"][0]["git_blob_sha"] = "0" * 40
        self.assertTrue(any("raw source bytes changed" in x for x in evidence_freeze.verify(lib)))

    def test_missing_article_lock_rejected(self):
        lock = json.loads((ROOT / "sources/article-evidence-lock.json").read_text())
        lock["records"].pop()
        self.assertTrue(any("article inventory changed" in x for x in evidence_freeze.verify(self.lib, lock)))

    def test_locked_article_path_traversal_rejected(self):
        lock = json.loads((ROOT / "sources/article-evidence-lock.json").read_text())
        lock["records"][0]["body"]["path"] = "../../outside.html"
        self.assertTrue(any("path changed or escaped" in x for x in evidence_freeze.verify(self.lib, lock)))

    def test_fingerprint_is_deterministic(self):
        meta = self.lib.articles["making-water-safer"]
        self.assertEqual(evidence_freeze.fingerprint(self.lib, meta),
                         evidence_freeze.fingerprint(self.lib, meta))

    def test_change_to_body_invalidates_prior_review_digest(self):
        lib = build.Library()
        meta = lib.articles["making-water-safer"]
        stamp = evidence_freeze.fingerprint(lib, meta)
        meta["_body"] += " New unreviewed copy."
        self.assertNotEqual(stamp, evidence_freeze.fingerprint(lib, meta))

    def test_change_to_cited_source_notes_invalidates_prior_review_digest(self):
        lib = build.Library()
        meta = lib.articles["pioneer-travel-rations"]
        stamp = evidence_freeze.fingerprint(lib, meta)
        source = lib.source_for(meta, next(iter(meta["source_use"])))
        source["notes"] = "changed without reading"
        self.assertNotEqual(stamp, evidence_freeze.fingerprint(lib, meta))

    def test_legacy_founder_safety_approval_cannot_publish_unbound_copy(self):
        lib = build.Library()
        meta = lib.articles["making-water-safer"]
        meta["status"]["publish"] = "published"
        meta["status"]["editorial"] = "reviewed"
        errors, _ = validate.validate(lib)
        self.assertTrue(any("human safety review is not bound" in e for e in errors), errors)

    def test_named_release_review_without_fingerprint_does_not_publish(self):
        lib = build.Library()
        meta = lib.articles["making-water-safer"]
        meta["status"]["publish"] = "published"
        meta["status"]["editorial"] = "reviewed"
        meta["release_review"] = {"state": "approved", "reviewer": "test-only",
                                  "date": "2026-10-30",
                                  "evidence_url": "https://example.org/review"}
        errors, _ = validate.validate(lib)
        self.assertTrue(any("release review is not bound" in e for e in errors), errors)

    def test_old_review_stamp_invalidated_after_a_text_edit(self):
        lib = build.Library()
        meta = lib.articles["making-water-safer"]
        meta["safety_review"]["review_fingerprint"] = evidence_freeze.fingerprint(lib, meta)
        meta["status"]["publish"] = "published"
        meta["_body"] += " Never human-reviewed addition."
        errors, _ = validate.validate(lib)
        self.assertTrue(any("human safety review is not bound" in e for e in errors), errors)

    def test_unchanged_blobs_never_imply_human_safety_qa(self):
        import audit_integration
        report = audit_integration.make_report(self.lib)
        self.assertTrue(report["integrity"]["original_bytes_match_crosswalk_and_article_ledger"])
        self.assertFalse(report["external_human_qa_proven"])
        self.assertEqual(report["publication"], "HOLD")


if __name__ == "__main__":
    unittest.main()
