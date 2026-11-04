"""R120 synthetic tamper tests; no real repository, network, or source modifications."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).with_name("r120_citation_context_gate.py")
if not MODULE.exists():
    MODULE = Path(__file__).resolve().parents[1] / "tools" / "r120_citation_context_gate.py"
spec = importlib.util.spec_from_file_location("r120_gate", MODULE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

A, B, C = "a" * 40, "b" * 40, "c" * 40
SLUGS = ["article-" + str(i) for i in range(35)]
CHANGED = SLUGS[:13]

def fixture():
    original = {s + ext: A for s in SLUGS for ext in (".body.html", ".meta.json")}
    changed = copy.deepcopy(original)
    for s in CHANGED:
        changed[s + ".body.html"] = B
    heads = [{"role": "baseline", "sha": A, "article_files": original},
             {"role": "candidate", "sha": B, "article_files": changed}]
    heads += [{"role": "contributor", "sha": str(i + 1) * 40, "cluster": "cluster-" + str(i)} for i in range(7)]
    snapshot = {"schema": gate.SOURCE_SCHEMA, "issue": 136, "business_issue": 820,
                "governance": {"release_state": "HOLD", "may_publish": False,
                               "may_merge": False, "independent_QD_PASS": False,
                               "medical_safety_verified": False, "merchant_offer_verified": False},
                "snapshots": heads}
    rows = []
    for s in CHANGED:
        rows.append({"slug": s, "before_git_blob": A, "after_git_blob": B,
                     "before_word_count": 100, "after_word_count": 107,
                     "before_citation_count": 2, "after_citation_count": 3,
                     "citation_sequence_changed": True,
                     "occurrence_changes": [{"source_id": "regulator-x", "before": 2, "after": 3}],
                     "same_source_id_changed_context_count": 1,
                     "context_examples": [{"citation": "regulator-x#1", "before": "prior wording", "after": "current wording"}],
                     "approval": "UNREVIEWED"})
    parts = [{"schema": gate.PART_SCHEMA, "issue": 136,
              "base_sha": A, "candidate_sha": B, "rows": rows[:7]},
             {"schema": gate.PART_SCHEMA, "issue": 136,
              "base_sha": A, "candidate_sha": B, "rows": rows[7:]}]
    return snapshot, parts

class R120Integrity(unittest.TestCase):
    def test_valid_reconciles(self):
        a, b = fixture()
        result = gate.check(a, b)
        self.assertEqual(result["article_count"], 35)
        self.assertEqual(result["changed_body_count"], 13)
        self.assertEqual(result["total_added_citation_tokens"], 13)
        self.assertEqual(result["unmodified_body_count"], 22)
        self.assertEqual(result["state"], "HOLD")
        self.assertFalse(result["may_publish"])
        self.assertEqual(result["QD_status"], "NOT_APPROVED")

    def test_determinism(self):
        a, b = fixture()
        x = gate.check(a, b)
        b[0]["rows"].reverse()
        self.assertEqual(x, gate.check(a, b))

    def test_duplicate_json_key_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "duplicate.json"
            p.write_text('{"a":1,"a":2}', encoding="utf-8")
            with self.assertRaisesRegex(gate.Hold, "DUPLICATE_JSON_KEY"):
                gate.strict_json(p)

    def test_invalid_global_release_upgrade(self):
        a, b = fixture()
        a["governance"]["may_publish"] = True
        with self.assertRaisesRegex(gate.Hold, "GOVERNANCE_UPGRADE"):
            gate.check(a, b)

    def test_invalid_row_approval(self):
        a, b = fixture()
        b[0]["rows"][0]["approval"] = "QD_PASS"
        with self.assertRaisesRegex(gate.Hold, "ILLEGAL_APPROVAL"):
            gate.check(a, b)

    def test_duplicate_changed_row(self):
        a, b = fixture()
        b[1]["rows"].append(copy.deepcopy(b[0]["rows"][0]))
        with self.assertRaisesRegex(gate.Hold, "DUPLICATE_ARTICLE_EVIDENCE"):
            gate.check(a, b)

    def test_count_conservation(self):
        a, b = fixture()
        b[0]["rows"][0]["after_citation_count"] += 1
        with self.assertRaisesRegex(gate.Hold, "CITATION_CONSERVATION_MISMATCH"):
            gate.check(a, b)

    def test_noop_source_delta(self):
        a, b = fixture()
        b[0]["rows"][0]["occurrence_changes"][0]["after"] = 2
        with self.assertRaisesRegex(gate.Hold, "NOOP_SOURCE_DELTA"):
            gate.check(a, b)

    def test_malformed_context(self):
        a, b = fixture()
        b[0]["rows"][0]["context_examples"][0]["after"] = "prior wording"
        with self.assertRaisesRegex(gate.Hold, "INVALID_CONTEXT_DIFFERENCE"):
            gate.check(a, b)

    def test_source_sequence_impossible(self):
        a, b = fixture()
        b[0]["rows"][0]["citation_sequence_changed"] = False
        with self.assertRaisesRegex(gate.Hold, "CITATION_SEQUENCE_CONTRADICTION"):
            gate.check(a, b)

    def test_wrong_candidate_ref(self):
        a, b = fixture()
        b[1]["candidate_sha"] = C
        with self.assertRaisesRegex(gate.Hold, "STALE_PART_HEAD"):
            gate.check(a, b)

    def test_wrong_baseline_blob(self):
        a, b = fixture()
        b[0]["rows"][0]["before_git_blob"] = C
        with self.assertRaisesRegex(gate.Hold, "BODY_BLOB_IDENTITY_MISMATCH"):
            gate.check(a, b)

    def test_wrong_candidate_blob(self):
        a, b = fixture()
        b[0]["rows"][0]["after_git_blob"] = C
        with self.assertRaisesRegex(gate.Hold, "BODY_BLOB_IDENTITY_MISMATCH"):
            gate.check(a, b)

    def test_signed_word_counts_forbidden(self):
        a, b = fixture()
        b[0]["rows"][0]["after_word_count"] = -1
        with self.assertRaisesRegex(gate.Hold, "INVALID_COUNT"):
            gate.check(a, b)

    def test_bool_is_not_int(self):
        a, b = fixture()
        b[0]["rows"][0]["before_citation_count"] = True
        with self.assertRaisesRegex(gate.Hold, "INVALID_COUNT"):
            gate.check(a, b)

    def test_context_count_smaller_than_examples(self):
        a, b = fixture()
        b[0]["rows"][0]["same_source_id_changed_context_count"] = 0
        with self.assertRaisesRegex(gate.Hold, "UNSOUND_CONTEXT_EXAMPLES"):
            gate.check(a, b)

    def test_extra_article_in_baseline(self):
        a, b = fixture()
        a["snapshots"][0]["article_files"]["added.body.html"] = A
        with self.assertRaisesRegex(gate.Hold, "ARTICLE_ROSTER_CHANGED"):
            gate.check(a, b)

    def test_remove_metadata_from_both(self):
        a, b = fixture()
        for h in a["snapshots"][:2]:
            h["article_files"].pop(SLUGS[0] + ".meta.json")
        with self.assertRaisesRegex(gate.Hold, "NOT_35_PAIRED_ARTICLES"):
            gate.check(a, b)

    def test_manifest_requires_two_parts(self):
        a, b = fixture()
        with self.assertRaisesRegex(gate.Hold, "TWO_PARTS_REQUIRED"):
            gate.check(a, b[:1])

    def test_unverified_part_schema(self):
        a, b = fixture()
        b[0]["schema"] = "APPROVED"
        with self.assertRaisesRegex(gate.Hold, "INVALID_PART_SCHEMA"):
            gate.check(a, b)

    def test_opaque_test_citation_after_edit(self):
        a, b = fixture()
        b[0]["rows"][0]["occurrence_changes"][0]["source_id"] = "bad:source"
        with self.assertRaisesRegex(gate.Hold, "INVALID_SOURCE_ID"):
            gate.check(a, b)

    def test_dangerous_fake_context_key(self):
        a, b = fixture()
        b[0]["rows"][0]["context_examples"][0]["citation"] = "bad#0"
        with self.assertRaisesRegex(gate.Hold, "BAD_CITATION_OCCURRENCE_KEY"):
            gate.check(a, b)

def make_missing_test(slug):
    def test(self):
        a, b = fixture()
        for part in b:
            part["rows"] = [x for x in part["rows"] if x["slug"] != slug]
        with self.assertRaisesRegex(gate.Hold, "MISSING_OR_EXTRA_CHANGED_BODIES"):
            gate.check(a, b)
    return test

def make_extra_test(slug):
    def test(self):
        a, b = fixture()
        wrong = copy.deepcopy(b[0]["rows"][0])
        wrong["slug"] = slug
        b[0]["rows"].append(wrong)
        with self.assertRaisesRegex(gate.Hold, "UNTRACKED_OR_UNCHANGED_BODY"):
            gate.check(a, b)
    return test

for index, slug in enumerate(CHANGED):
    setattr(R120Integrity, f"test_missing_changed_body_{index:02d}", make_missing_test(slug))
for index, slug in enumerate(SLUGS[13:]):
    setattr(R120Integrity, f"test_untracked_unchanged_body_{index:02d}", make_extra_test(slug))



class R120ActualFrozenCorpus(unittest.TestCase):
    def test_35_original_routes_against_two_exact_object_manifests(self):
        root = Path(__file__).resolve().parents[1]
        snapshot = root / "docs" / "R117_NINE_SNAPSHOT_GIT_OBJECT_CUSTODY_HOLD.json"
        a = root / "docs" / "r120" / "CITATION_CONTEXT_CHANGED_BODIES_PART_A_HOLD.json"
        b = root / "docs" / "r120" / "CITATION_CONTEXT_CHANGED_BODIES_PART_B_HOLD.json"
        if not snapshot.exists() or not a.exists() or not b.exists():
            self.skipTest("full repository / frozen manifest files not mounted")
        report = gate.check(gate.strict_json(snapshot),
                            [gate.strict_json(a), gate.strict_json(b)])
        self.assertEqual(report["article_count"], 35)
        self.assertEqual(report["changed_body_count"], 13)
        self.assertEqual(report["unmodified_body_count"], 22)
        self.assertEqual(report["total_added_citation_tokens"], 48)
        self.assertEqual(report["source_occurrence_delta_articles"], 10)
        self.assertEqual(report["source_context_drift_articles"], 8)
        self.assertEqual(report["state"], "HOLD")
        self.assertFalse(report["may_publish"])

if __name__ == "__main__":
    unittest.main()
