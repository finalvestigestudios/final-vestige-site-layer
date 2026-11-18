"""Synthetic, fully local threat-model tests; not evidence that source advice is safe."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1] / "tools" / "r460_original_branch_provenance_gate.py"
spec = importlib.util.spec_from_file_location("r460_gate", HERE)
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "preparedness"
        self.rows = []
        self.sources = []
        self.branches = {key: {"ref": "claude/prep-" + key, "sha": "%040x" % (i+10)}
                         for i, key in enumerate(sorted(R.BRANCH_IDS))}
        self.metadata = {}
        for kind, count, start in (("articles", 35, 1), ("tools", 6, 101)):
            for i in range(count):
                slug = f"{kind}-{i+1}"
                src = {"slug": slug, "n": start + i, "section": "start-here" if kind == "articles" else "field-tools",
                       "status": {"publish": "draft", "editorial": "drafted"},
                       "safety_review": {"state": "pending", "reviewer": None}}
                for ext, raw in (("body.html", f"<p>Original source #{i}</p>\n".encode()),
                                 ("meta.json", (json.dumps(src, sort_keys=True) + "\n").encode())):
                    path = f"preparedness/content/{kind}/{slug}.{ext}"
                    self.write(path, raw)
                    self.rows.append(self.row(path, raw))
                self.metadata[slug] = src
        path = "preparedness/content/hubs/start-here.body.html"
        raw = b"<p>Private draft hub; no publication authorization</p>\n"
        self.write(path, raw)
        self.rows.append(self.row(path, raw))
        for name in ("register", "fragments/start", "fragments/food", "fragments/health",
                     "fragments/shelter", "fragments/hist-field", "fragments/hist-food", "fragments/hist-home"):
            path = f"preparedness/sources/{name}.json"
            raw = (json.dumps({"sources": [name], "gate": "PENDING"}) + "\n").encode()
            self.write(path, raw)
            self.sources.append({"path": path, "integrated_blob": R.blob_sha(raw), "contributors": {}})
        self.rows.sort(key=lambda row: row["path"])
        self.sources.sort(key=lambda row: row["path"])
        self.manifest = {
            "schema_version": 1, "release_state": R.STATE, "qualified_qd_pass": False,
            "wordpress_publication_performed": False, "source_claim_support_verified": False,
            "paid_conversion_verified": False, "issue": 136, "conversion_issue": 820,
            "integrated_head": R.INTEGRATED_COMMIT, "article_count": 35, "tool_count": 6,
            "branches": self.branches, "artifacts": self.rows, "source_fragments": self.sources,
        }
        self.freeze()

    def row(self, path, raw):
        return {"path": path, "integrated_blob": R.blob_sha(raw),
                "contributors": {}, "matches_integrated": [], "distinct_contributor_blobs": 0,
                "requires_human_disposition": True}

    def write(self, rel, raw):
        path = self.root.joinpath(*Path(rel).parts[1:])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    def freeze(self):
        self.raw = (json.dumps(self.manifest, sort_keys=True) + "\n").encode()
        R.MANIFEST_BLOB = R.blob_sha(self.raw)

    def audit(self):
        return R.verify_checkout(self.root, self.raw)

    def test_baseline_structural_hold_remains(self):
        out = self.audit()
        self.assertEqual(out["local_source_custody"], "STRUCTURAL_PASS_ONLY")
        self.assertFalse(out["qualified_qd_pass"])
        self.assertEqual(out["medical_emergency_food_privacy_review"], "NOT_APPROVED")
        self.assertEqual(out["current_branch_sha_evidence"], "NOT_RECHECKED_IN_CLI")
        self.assertEqual(out["file_blob_checks"], 91)

    def test_exact_branch_refs_checked_not_approved(self):
        obs = {k: v["sha"] for k, v in self.branches.items()}
        out = R.verify_checkout(self.root, self.raw, obs)
        self.assertEqual(out["current_branch_sha_evidence"], "RECHECKED_EXACT_REF_SHA")
        self.assertFalse(out["qualified_qd_pass"])

    def test_changed_branch_head_blocks(self):
        observed = {k: v["sha"] for k, v in self.branches.items()}
        observed["start"] = "a" * 40
        with self.assertRaises(R.ProvenanceHold):
            R.verify_checkout(self.root, self.raw, observed)

    def test_missing_branch_ref_blocks(self):
        with self.assertRaises(R.ProvenanceHold):
            R.verify_checkout(self.root, self.raw, {"start": "a"*40})

    def test_duplicate_json_properties_block(self):
        with self.assertRaises(R.ProvenanceHold):
            R.load_json(b'{"publish":"draft","publish":"published"}')

    def test_frozen_manifest_tamper_blocks_even_if_semantically_same(self):
        with self.assertRaises(R.ProvenanceHold):
            R.verify_checkout(self.root, self.raw + b" ")

    def test_missing_article_body_blocks(self):
        p = self.root / "content/articles/articles-1.body.html"
        p.unlink()
        with self.assertRaises(R.ProvenanceHold):
            self.audit()

    def test_extra_article_blocks(self):
        self.write("preparedness/content/articles/unauthorized.body.html", b"hello")
        with self.assertRaises(R.ProvenanceHold):
            self.audit()

    def test_symlink_body_blocks(self):
        p = self.root / "content/articles/articles-1.body.html"
        p.unlink()
        p.symlink_to(self.root / "content/articles/articles-2.body.html")
        with self.assertRaises(R.ProvenanceHold):
            self.audit()

    def test_duplicate_meta_numeric_identity_blocks(self):
        path = "preparedness/content/articles/articles-2.meta.json"
        meta = copy.deepcopy(self.metadata["articles-2"])
        meta["n"] = 1
        self.write(path, (json.dumps(meta) + "\n").encode())
        self.adjust_blob(path)
        with self.assertRaises(R.ProvenanceHold):
            self.audit()

    def test_release_status_published_blocks(self):
        path = "preparedness/content/articles/articles-3.meta.json"
        meta = copy.deepcopy(self.metadata["articles-3"])
        meta["status"]["publish"] = "published"
        self.write(path, (json.dumps(meta) + "\n").encode())
        self.adjust_blob(path)
        with self.assertRaises(R.ProvenanceHold):
            self.audit()

    def test_false_medical_approval_blocks(self):
        path = "preparedness/content/articles/articles-3.meta.json"
        meta = copy.deepcopy(self.metadata["articles-3"])
        meta["safety_review"]["state"] = "approved"
        self.write(path, (json.dumps(meta) + "\n").encode())
        self.adjust_blob(path)
        with self.assertRaises(R.ProvenanceHold):
            self.audit()

    def adjust_blob(self, rel):
        """Even coordinated original+manifest mutation needs review; not an allowed release."""
        b = self.root.joinpath(*Path(rel).parts[1:]).read_bytes()
        for row in self.manifest["artifacts"]:
            if row["path"] == rel:
                row["integrated_blob"] = R.blob_sha(b)
        self.freeze()

    def test_duplicate_route_state_blocks(self):
        meta = copy.deepcopy(self.metadata["articles-5"])
        meta["slug"] = "articles-4"
        path = "preparedness/content/articles/articles-5.meta.json"
        self.write(path, (json.dumps(meta) + "\n").encode())
        self.adjust_blob(path)
        with self.assertRaises(R.ProvenanceHold):
            self.audit()

    def test_extra_fragment_blocks(self):
        self.write("preparedness/sources/fragments/evil.json", b"{}")
        with self.assertRaises(R.ProvenanceHold):
            self.audit()

    def test_original_register_modification_blocks(self):
        self.write("preparedness/sources/register.json", b"{}")
        with self.assertRaises(R.ProvenanceHold):
            self.audit()

    def test_source_variant_not_silently_labeled_exact_match(self):
        obj = copy.deepcopy(self.manifest)
        obj["artifacts"][0]["contributors"] = {"start": "a" * 40, "food": "b" * 40}
        obj["artifacts"][0]["distinct_contributor_blobs"] = 1
        with self.assertRaises(R.ProvenanceHold):
            R.validate_graph(obj)

    def test_source_selection_requires_disposition(self):
        obj = copy.deepcopy(self.manifest)
        obj["artifacts"][0]["requires_human_disposition"] = False
        with self.assertRaises(R.ProvenanceHold):
            R.validate_graph(obj)

    def test_unlisted_branch_cannot_be_added(self):
        obj = copy.deepcopy(self.manifest)
        obj["artifacts"][0]["contributors"] = {"new-agent": "a" * 40}
        with self.assertRaises(R.ProvenanceHold):
            R.validate_graph(obj)

    def test_unsafe_pseudo_pass_flag_blocks(self):
        for flag in ("qualified_qd_pass", "wordpress_publication_performed", "paid_conversion_verified"):
            with self.subTest(flag=flag):
                obj = copy.deepcopy(self.manifest)
                obj[flag] = True
                with self.assertRaises(R.ProvenanceHold):
                    R.validate_graph(obj)


# One independently named test per original authored article body to expose omission
# and corruption across the entire slate, not a single bulk subtest result.
def make_article_tamper_test(i):
    def tamper(self):
        name = f"articles-{i}"
        path = f"preparedness/content/articles/{name}.body.html"
        self.write(path, b"<p>Deceptively shorter copy, while metadata and citations might remain intact.</p>\n")
        with self.assertRaises(R.ProvenanceHold):
            self.audit()
    return tamper

for i in range(1, 36):
    setattr(Fixture, f"test_mutation_article_{i:02}", make_article_tamper_test(i))

if __name__ == "__main__":
    unittest.main()
