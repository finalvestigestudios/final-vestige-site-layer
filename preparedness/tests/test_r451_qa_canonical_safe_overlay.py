"""R451 synthetic-only offline QA tests. Never represent a qualified release or a native build."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SRC = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("r451_gate", SRC / "tools" / "r451_qa_canonical_safe_overlay.py")
assert spec and spec.loader
r451 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r451)
spec2 = importlib.util.spec_from_file_location("r450_test_helpers", SRC / "tests" / "test_r450_qa_overlap_rehearsal.py")
assert spec2 and spec2.loader
helpers = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(helpers)


def fixtures():
    return helpers.variants()


def patched_fixtures():
    v = fixtures()
    # The repair branch's replacement fixtures are safe and structurally distinct.
    repair = v["repair2205"].decode()
    for name in r451.REPLACEMENTS:
        original = helpers.FIXTURE.format(name=name)
        replacement = original.replace("self.assertTrue(True)", "self.assertEqual(1 + 1, 2)")
        repair = repair.replace(original, replacement)
    v["repair2205"] = repair.encode()
    return v


class Baseline(unittest.TestCase):
    def setUp(self):
        self.v = patched_fixtures()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.checkout = self.root / "canonical"
        self.checkout.mkdir()
        self.target = self.root / "external" / "candidate.py.txt"

    def test_01_structural_candidate_40_tests(self):
        code, receipt = r451.compose(self.v, require_pins=False)
        self.assertEqual(receipt["original_test_count"], 38)
        self.assertEqual(receipt["candidate_test_count"], 40)
        self.assertEqual(len(r451.r450.parse_methods(code)[1]), 40)

    def test_02_exact_three_fixture_replacements(self):
        _, receipt = r451.compose(self.v, require_pins=False)
        self.assertEqual(set(receipt["fixture_method_replacements"]), set(r451.REPLACEMENTS))

    def test_03_two_independent_qa_guards_added(self):
        _, receipt = r451.compose(self.v, require_pins=False)
        self.assertEqual(set(receipt["independent_gate_additions"]), {r451.r450.SAFETY_METHOD, r451.r450.RUNTIME_METHOD})

    def test_04_original_bytes_never_modified(self):
        old = dict(self.v)
        r451.compose(self.v, require_pins=False)
        self.assertEqual(self.v, old)

    def test_05_composite_has_verified_safety_witness(self):
        code, _ = r451.compose(self.v, require_pins=False)
        _, tests, _ = r451._inventory(code)
        self.assertEqual(r451.r450.verify_safety_method(tests[r451.r450.SAFETY_METHOD]), [])

    def test_06_composite_has_runtime_guard_witness(self):
        code, _ = r451.compose(self.v, require_pins=False)
        _, tests, _ = r451._inventory(code)
        self.assertEqual(r451.r450.verify_runtime_method(tests[r451.r450.RUNTIME_METHOD]), [])

    def test_07_no_qd_pass_and_no_publication(self):
        _, r = r451.compose(self.v, require_pins=False)
        for key in ("publishable", "merged", "qd_pass", "native_suite_pass", "paid_offer_verified", "attributed_revenue_verified"):
            self.assertIs(r[key], False)
        self.assertEqual(r["release_state"], r451.HOLD)

    def test_08_other_article_files_still_pending(self):
        _, r = r451.compose(self.v, require_pins=False)
        self.assertEqual(len(r["qa157_other_4_files_unmerged"]), 4)

    def test_09_preserves_non_fixture_assertions(self):
        code, _ = r451.compose(self.v, require_pins=False)
        _, base, _ = r451._inventory(self.v["target_r449"])
        _, combined, _ = r451._inventory(code)
        for name in set(base) - set(r451.REPLACEMENTS):
            self.assertEqual(r451.ast.dump(base[name], include_attributes=False), r451.ast.dump(combined[name], include_attributes=False), name)

    def test_10_export_review_artifact_outside_checkout(self):
        r = r451.export_review_only(self.v, self.target, self.checkout, require_pins=False)
        self.assertTrue(self.target.exists())
        self.assertTrue(self.target.read_text().startswith("# REVIEW CANDIDATE ONLY"))
        self.assertTrue(r["review_candidate_written"])
        self.assertFalse(r["publishable"])

    def test_11_existing_artifact_never_overwritten(self):
        self.target.parent.mkdir()
        self.target.write_text("preserve")
        with self.assertRaisesRegex(r451.OverlayError, "already exists"):
            r451.export_review_only(self.v, self.target, self.checkout, require_pins=False)
        self.assertEqual(self.target.read_text(), "preserve")

    def test_12_refuses_output_inside_checkout(self):
        with self.assertRaisesRegex(r451.OverlayError, "canonical checkout"):
            r451.export_review_only(self.v, self.checkout / "danger.py.txt", self.checkout, require_pins=False)

    def test_13_refuses_output_as_checkout(self):
        with self.assertRaisesRegex(r451.OverlayError, "canonical checkout"):
            r451.export_review_only(self.v, self.checkout, self.checkout, require_pins=False)

    def test_14_refuses_executable_py_artifact(self):
        with self.assertRaisesRegex(r451.OverlayError, "non-executable"):
            r451.export_review_only(self.v, self.root / "outside.py", self.checkout, require_pins=False)

    def test_15_default_requires_exact_github_pins(self):
        with self.assertRaisesRegex(r451.r450.GateError, "unaligned authenticated"):
            r451.compose(self.v)

    def test_16_hard_hold_original_source_conflicts(self):
        _, r = r451.compose(self.v, require_pins=False)
        self.assertIn("5_source_disputes", r["pending_qualified_review"])
        self.assertIn("9_forks", r["pending_qualified_review"])

    def test_17_no_new_invented_canonical_source_file(self):
        r451.export_review_only(self.v, self.target, self.checkout, require_pins=False)
        self.assertEqual(list(self.checkout.iterdir()), [])

    def test_18_source_pin_records_mark_synthetic_mismatch(self):
        _, r = r451.compose(self.v, require_pins=False)
        self.assertTrue(all(not item["matched"] for item in r["source_git_blobs"].values()))

    def test_19_sha_is_for_candidate_only(self):
        code, r = r451.compose(self.v, require_pins=False)
        self.assertEqual(r["composite_sha256"], r451.hashlib.sha256(code).hexdigest())

    def test_20_stable_deterministic_output(self):
        first = r451.compose(self.v, require_pins=False)
        second = r451.compose(self.v, require_pins=False)
        self.assertEqual(first, second)


# Additional mutation tests cover every independent source record and class method.
MUTATIONS = [
    ("bad_qa_source", "qa157", lambda x: x.replace(b"approved human safety review", b"verified safe today"), "witness"),
    ("no_safety_slug", "qa157", lambda x: x.replace(b"household-emergency-plan", b"deleted-plan"), "slug"),
    ("no_safety_finally", "qa157", lambda x: x.replace(b"finally:", b"except Exception:"), "finally"),
    ("no_runtime", "repair2205", lambda x: x.replace(b"def test_fixture_tests_never_write_or_unlink_in_canonical_checkout", b"def test_other_noguard"), "runtime"),
    ("remove_write_patch", "repair2205", lambda x: x.replace(b"Path.write_text", b"Path.touch"), "runtime"),
    ("remove_unlink_patch", "repair2205", lambda x: x.replace(b"Path.unlink", b"Path.touch"), "runtime"),
    ("remove_fixture_test", "repair2205", lambda x: x.replace(b"def test_register_fragments_cannot_duplicate_ids", b"def former_register_fragments"), "fixture"),
    ("remove_base_fixture", "target_r449", lambda x: x.replace(b"def test_register_fragments_cannot_duplicate_ids", b"def former_register_fragments"), "fixture"),
    ("bad_qa_encoding", "qa157", lambda x: b"\xff" + x, "invalid Python"),
    ("bad_repair_syntax", "repair2205", lambda x: x + b"\ndef incomplete(\n", "invalid Python"),
    ("drop_qa_tests", "qa157", lambda x: b"class LibraryTests:\n def test_one(self): pass\n", "truncated"),
    ("drop_base_tests", "target_r449", lambda x: b"class LibraryTests:\n def test_one(self): pass\n", "truncated"),
    ("unknown_extra_variant", None, None, "exactly"),
]


def make_mutation_test(label, key, change, expected):
    def test(self):
        v = patched_fixtures()
        if key is None:
            v["untrusted"] = b"garbage"
        else:
            v[key] = change(v[key])
        with self.assertRaisesRegex((r451.OverlayError, r451.r450.GateError), expected):
            r451.compose(v, require_pins=False)
    test.__name__ = "test_mutation_" + label
    return test

for label, key, change, expected in MUTATIONS:
    setattr(Baseline, "test_mutation_" + label, make_mutation_test(label, key, change, expected))

# All 35 article decisions must stay outside synthetic QA proof.
for idx in range(35):
    def test_article_hold(self, _idx=idx):
        _, report = r451.compose(fixtures(), require_pins=False)
        self.assertFalse(report["publishable"], f"Article {_idx + 1} incorrectly releasable")
        self.assertEqual(report["release_state"], r451.HOLD)
    setattr(Baseline, f"test_article_{idx+1:02d}_never_claim_safe", test_article_hold)

if __name__ == "__main__":
    unittest.main()
