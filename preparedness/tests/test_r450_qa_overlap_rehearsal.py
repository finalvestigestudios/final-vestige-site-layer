"""R450 synthetic adversarial tests: NO native-article or qualified safety PASS."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "r450_qa_overlap_rehearsal.py"
spec = importlib.util.spec_from_file_location("r450", SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

HEADER = ("import unittest\nfrom pathlib import Path\n"
          "class validate:\n    @staticmethod\n    def validate(x): return [], None\n"
          "class LibraryTests(unittest.TestCase):\n")
SAFETY = '''    def test_start_articles_require_human_safety_review_before_publishing(self):
        for slug in ("household-emergency-plan", "three-day-kit", "go-bags", "preparedness-real-households"):
            meta = {"status": {"publish": "draft"}}
            original = meta["status"]
            try:
                meta["status"] = {"publish": "published"}
                errors, _ = validate.validate(meta)
                self.assertTrue(any("CANNOT be published without an approved human safety review" in e for e in errors), slug)
            finally:
                meta["status"] = original
'''
RUNTIME = '''    def test_fixture_tests_never_write_or_unlink_in_canonical_checkout(self):
        from unittest.mock import patch
        canonical_root = Path('/canonical')
        original_write = Path.write_text
        original_unlink = Path.unlink
        def guarded_write(path, *args, **kwargs):
            if path == canonical_root:
                self.fail("canonical write")
        def guarded_unlink(path, *args, **kwargs):
            if path == canonical_root:
                self.fail("canonical unlink")
        with patch.object(Path, "write_text", guarded_write), patch.object(Path, "unlink", guarded_unlink):
            self.test_fragment_may_upgrade_a_placeholder_but_not_a_verified_source()
            self.test_register_fragments_cannot_duplicate_ids()
'''
FIXTURE = '''    def {name}(self):
        import shutil, tempfile
        with tempfile.TemporaryDirectory() as td:
            sandbox = Path(td) / 'preparedness'
            shutil.copytree('/source', sandbox)
            fragment = sandbox / 'sources' / 'fragments' / 'fixture.json'
            fragment.write_text('{{}}')
            self.assertTrue(True)
'''

def synthetic(kind):
    parts = [HEADER]
    for n in range(34):
        parts.append(f"    def test_generic_{n:02d}(self):\n        self.assertTrue(True)\n")
    for n in gate.FIXTURE_METHODS:
        parts.append(FIXTURE.format(name=n))
    if kind in ("qa", "both"):
        parts.append(SAFETY)
    if kind in ("repair", "both"):
        parts.append(RUNTIME)
    parts.append("\n\nclass ExtraTests(unittest.TestCase):\n    def test_second_class(self):\n        self.assertTrue(True)\n")
    return "\n".join(parts).encode()

def evidence():
    return {"qa157": synthetic("qa"), "fixture169": synthetic("base"),
            "repair2205": synthetic("repair"), "target_r449": synthetic("base")}

class TestReceipt(unittest.TestCase):
    def test_git_hash(self):
        self.assertEqual(gate.git_blob(b"hello"), "b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0")
    def test_pins_are_not_assumed(self):
        d = gate.assess(evidence(), require_pins=False)
        self.assertTrue(all(not v["matched"] for v in d["source_pins"].values()))
    def test_authentic_pins_required(self):
        with self.assertRaisesRegex(gate.GateError, "unaligned authenticated"):
            gate.assess(evidence())
    def test_release_is_always_held(self):
        d = gate.assess(evidence(), require_pins=False)
        self.assertEqual(d["release_state"], gate.HOLD)
        self.assertFalse(d["publishable"])
        self.assertFalse(d["qd_approved"])
        self.assertFalse(d["merge_approved"])
    def test_missing_sources_fail(self):
        d = evidence()
        del d["qa157"]
        with self.assertRaisesRegex(gate.GateError, "exactly"):
            gate.assess(d, require_pins=False)
    def test_nonbyte_sources_fail(self):
        d = evidence()
        d["qa157"] = "fake"
        with self.assertRaisesRegex(gate.GateError, "bytes"):
            gate.assess(d, require_pins=False)
    def test_duplicate_method_fails(self):
        d = evidence()
        d["target_r449"] = d["target_r449"].replace(
            b"class ExtraTests", b"    def test_generic_00(self):\n        pass\n\nclass ExtraTests")
        with self.assertRaisesRegex(gate.GateError, "duplicate"):
            gate.assess(d, require_pins=False)
    def test_valid_rehearsal_keeps_checkout_unmodified(self):
        d = evidence()
        original = d["target_r449"]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            root.mkdir()
            dst = Path(td) / "outside" / "candidate.py"
            report = gate.rehearse(d, dst, root, require_pins=False)
            self.assertEqual(report["candidate_tests"], 40)
            self.assertFalse(report["candidate_is_release_approved"])
            self.assertEqual(d["target_r449"], original)
            compile(dst.read_text(), str(dst), "exec")
    def test_no_output_inside_checkout(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            root.mkdir()
            with self.assertRaisesRegex(gate.GateError, "outside"):
                gate.rehearse(evidence(), root / "candidate.py", root, require_pins=False)
    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            root.mkdir()
            dest = Path(td) / "candidate.py"
            dest.write_text("preserve me")
            with self.assertRaisesRegex(gate.GateError, "already exists"):
                gate.rehearse(evidence(), dest, root, require_pins=False)
            self.assertEqual(dest.read_text(), "preserve me")
    def test_review_of_other_qa_files_explicit(self):
        d = gate.assess(evidence(), require_pins=False)
        self.assertEqual(len(d["qa157_non_test_files_require_separate_editorial_adjudication"]), 4)
        self.assertIn(gate.SAFETY_METHOD, d["qa157_unrepresented_tests"])
        self.assertIn(gate.RUNTIME_METHOD, d["repair2205_unrepresented_tests"])

MUTATIONS = []
for slug in gate.SAFETY_SLUGS:
    MUTATIONS.append((f"missing_slug_{slug}", "qa157", slug, "removed-"+slug, "missing protected slug"))
MUTATIONS += [
    ("safety_rejection", "qa157", "CANNOT be published without an approved human safety review", "safe", "rejection witness"),
    ("safety_validator", "qa157", "validate.validate(meta)", "len([])", "never invokes validator"),
    ("safety_assert", "qa157", "self.assertTrue(any(", "self.assertFalse(any(", "never asserts rejection"),
    ("safety_finally", "qa157", "            finally:\n", "            except Exception:\n", "finally restoration"),
    ("safety_publish", "qa157", '"published"', '"draft"', "does not simulate publishing"),
    ("runtime_write", "repair2205", "original_write = Path.write_text", "original_write = Path.read_text", "Path.write_text"),
    ("runtime_unlink", "repair2205", "original_unlink = Path.unlink", "original_unlink = Path.is_file", "Path.unlink"),
    ("runtime_root", "repair2205", "canonical_root", "something_else", "canonical_root"),
    ("runtime_fail", "repair2205", "self.fail(", "self.assertTrue(", "does not fail"),
    ("runtime_patch", "repair2205", "patch.object(", "object(", "does not patch"),
    ("runtime_first_fixture", "repair2205", "self.test_fragment_may_upgrade_a_placeholder_but_not_a_verified_source()", "self.assertTrue(True)", "test_fragment"),
    ("runtime_second_fixture", "repair2205", "self.test_register_fragments_cannot_duplicate_ids()", "self.assertTrue(True)", "test_register"),
    ("fixture_no_temp", "target_r449", "tempfile.TemporaryDirectory()", "tempfile.mkdtemp()", "TemporaryDirectory"),
    ("fixture_no_copy", "target_r449", "shutil.copytree(", "shutil.copy(", "isolated copy"),
]
for method in gate.FIXTURE_METHODS:
    MUTATIONS.append(("lost_fixture_"+method, "target_r449", "def "+method+"(", "def test_removed_"+method+"(", "baseline missing fixture"))
for n in range(34):
    MUTATIONS.append((f"newly_renamed_original_{n:02d}", "target_r449",
                      f"def test_generic_{n:02d}(", f"def test_synthetic_other_{n:02d}(", "not represented in fixture parent"))

class TestMutationCases(unittest.TestCase):
    pass

def make_case(key, before, after, reason):
    def exercise(self):
        d = evidence()
        self.assertIn(before.encode(), d[key])
        d[key] = d[key].replace(before.encode(), after.encode())
        report = gate.assess(d, require_pins=False)
        self.assertFalse(report["rehearsal_possible"])
        self.assertIn(reason, " ".join(report["structural_errors"]))
    return exercise

for label, key, old, new, reason in MUTATIONS:
    setattr(TestMutationCases, "test_"+label.replace("-", "_"),
            make_case(key, old, new, reason))

if __name__ == "__main__":
    unittest.main()
