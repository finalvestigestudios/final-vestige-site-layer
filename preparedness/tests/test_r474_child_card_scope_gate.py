"""R474 isolated adversarial custody tests. All assertions are structural, NOT safety review."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "tools/r474_child_card_scope_gate.py"
spec = importlib.util.spec_from_file_location("r474_child_card", SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
MANIFEST = json.loads((Path(__file__).resolve().parents[1] /
                      "reviews/r474_child_card_scope_manifest.json").read_text())


def setup():
    a = {"n": 15, "slug": gate.ARTICLE, "status":{"publish":"draft"},
         "safety_review":{"state":"pending","reviewer":None,"date":None},
         "source_use":{k:"older documented scope" for k in gate.REQUIRED_OLD_IDS}}
    t = copy.deepcopy(a);t["n"]=104;t["slug"]=gate.TOOL
    article = ("<strong>Keep it on paper, too.</strong> This is our caution, not an agency's. "
               "{{link:family-reunification-card|fold-over wallet card}} "
               "{{cite:shelter-cdc-reunification}} {{cite:shelter-ready-plan-form}}")
    tool = ("A printed card can be lost. Do not put a child's full name, "
            "a medical diagnosis or a password on it. "
            "First names or nicknames and phone numbers are usually enough. "
            "minimal version. School, childcare and care (left off the minimal version). "
            "{{cite:shelter-cdc-reunification}}")
    return [article, a, tool, t, copy.deepcopy(MANIFEST)]


class ReviewCustodyTests(unittest.TestCase):
    def test_original_synthetic_holds(self):
        d = gate.validate_originals(*setup())
        self.assertEqual(d["state"], "CHILD_CARD_CONTEXT_AND_CITATION_REVIEW_HARD_HOLD")
        self.assertFalse(d["may_publish"])
        self.assertFalse(d["qualified_qd_pass"])
        self.assertEqual(d["review_sources_unregistered"], 3)
        self.assertEqual(d["unadjudicated_decisions"], 8)

    def test_strict_duplicate_json(self):
        with self.assertRaises(gate.Hold):
            gate.strict_json(b'{"x":1,"x":2}')

    def test_strict_non_object(self):
        with self.assertRaises(gate.Hold):gate.strict_json(b'[]')

    def test_valid_sha_git_blob(self):
        self.assertEqual(gate.blob_sha(b"hello"), "b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0")

    def test_pinned_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(gate.Hold):gate.checked_file(Path(tmp),"notthere", "abcd")

    def test_pinned_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp);(path/"regular").write_text("hello");(path/"link").symlink_to(path/"regular")
            with self.assertRaises(gate.Hold):gate.checked_file(path,"link",gate.blob_sha(b"hello"))

    def test_pinned_wrong_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/"evidence").write_text("fraud")
            with self.assertRaises(gate.Hold):gate.checked_file(p,"evidence",gate.blob_sha(b"original"))

    def test_pinned_correct_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);(p/"evidence").write_text("original")
            self.assertEqual(gate.checked_file(p,"evidence",gate.blob_sha(b"original")),b"original")

    def test_native_missing_original_holds(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(gate.Hold):gate.native(Path(tmp))

    def test_cli_always_returns_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(gate.main(["--root",tmp]),2)

