"""R151 fail-closed three-way admission tests; no remote checkout required."""
import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve()
TOOL = HERE.parents[1] / "tools" / "r151_branch_admission.py"
SPEC = importlib.util.spec_from_file_location("r151_branch_admission", TOOL)
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)
MANIFEST_PATH = HERE.parents[1] / "docs" / "r151" / "contributor-three-way.json"
MANIFEST = json.loads(MANIFEST_PATH.read_text(encoding="utf8"))


def make_row(index):
    src = MANIFEST["articles"][index]
    # Synthetic but source-ID-realistic article variants, including a pure CRLF case.
    a = b"<h2>Historical evidence</h2>\n<p>Documented source{{cite:hist-food-nchfp-jerky}}</p>\n"
    b = a.replace(b"hist-food-nchfp-jerky", b"nchfp-jerky")
    status = src["resolution"]
    if status != "PINNED_SUBSTITUTION_PENDING":
        b = a + b"<p>New, sourced primary history{{cite:new-primary-source}}</p>\n"
        if status == "UPSTREAM_EOL_ONLY":
            b = b.replace(b"\n", b"\r\n")
    c = a if status == "PINNED_SUBSTITUTION_PENDING" else (b.replace(b"\r\n", b"\n") if status == "UPSTREAM_EOL_ONLY" else b)
    variants = {"pinned": a, "upstream": b, "candidate": c}
    data = {"slug": src["slug"], "resolution": status}
    for kind, raw in variants.items():
        data[kind] = {"commit": {"pinned": "a" * 40, "upstream": "b" * 40,
                                   "candidate": "c" * 40}[kind],
                      "blob": GATE.git_blob(raw), "words": GATE.word_count(raw),
                      "citations": len(GATE.source_tokens(raw))}
    return data, variants


class ManifestContract(unittest.TestCase):
    def test_valid_manifest(self):
        self.assertTrue(GATE.check_manifest(MANIFEST))

    def test_hard_hold(self):
        self.assertEqual(MANIFEST["decision"], "DRAFT_HARD_HOLD")
        self.assertFalse(MANIFEST["qualified_safety_review"])
        self.assertFalse(MANIFEST["qd_pass"])

    def test_duplicate_identity(self):
        m = copy.deepcopy(MANIFEST); m["articles"][1]["slug"] = m["articles"][0]["slug"]
        with self.assertRaises(ValueError): GATE.check_manifest(m)

    def test_publish_state_forgery(self):
        m = copy.deepcopy(MANIFEST); m["decision"] = "LIVE"
        with self.assertRaises(ValueError): GATE.check_manifest(m)

    def test_qd_forgery(self):
        m = copy.deepcopy(MANIFEST); m["qd_pass"] = True
        with self.assertRaises(ValueError): GATE.check_manifest(m)

    def test_medical_forgery(self):
        m = copy.deepcopy(MANIFEST); m["qualified_safety_review"] = True
        with self.assertRaises(ValueError): GATE.check_manifest(m)

    def test_reject_broken_candidate_sha(self):
        m = copy.deepcopy(MANIFEST); m["candidate_commit"] = "yesterday"
        with self.assertRaises(ValueError): GATE.check_manifest(m)

    def test_missing_metadata_custody(self):
        m = copy.deepcopy(MANIFEST); del m["metadata_blobs"]
        with self.assertRaises(ValueError): GATE.check_manifest(m)

    def test_metadata_blob_forgery(self):
        m = copy.deepcopy(MANIFEST); m["metadata_blobs"]["water-math"] = "NotAnObject"
        with self.assertRaises(ValueError): GATE.check_manifest(m)

    def test_metadata_article_missing(self):
        m = copy.deepcopy(MANIFEST); m["metadata_blobs"].pop("water-math")
        with self.assertRaises(ValueError): GATE.check_manifest(m)

    def test_crosswalk_branch_removed(self):
        m = copy.deepcopy(MANIFEST); del m["source_head_commits"]["hist-food"]
        with self.assertRaises(ValueError): GATE.check_manifest(m)

    def test_crosswalk_branch_added(self):
        m = copy.deepcopy(MANIFEST); m["source_head_commits"]["unreviewed"] = "a" * 40
        with self.assertRaises(ValueError): GATE.check_manifest(m)

    def test_missing_article(self):
        m = copy.deepcopy(MANIFEST); m["articles"].pop()
        with self.assertRaises(ValueError): GATE.check_manifest(m)

    def test_bucket_forgery(self):
        m = copy.deepcopy(MANIFEST); m["articles"][0]["resolution"] = "UPSTREAM_EXACT"
        with self.assertRaises(ValueError): GATE.check_manifest(m)

    def test_frozen_pin_switch(self):
        m = copy.deepcopy(MANIFEST); m["articles"][0]["pinned"]["commit"] = "a" * 40
        with self.assertRaises(ValueError): GATE.check_manifest(m)

    def test_low_reading_depth(self):
        m = copy.deepcopy(MANIFEST); m["articles"][0]["pinned"]["words"] = 200
        with self.assertRaises(ValueError): GATE.check_manifest(m)

    def test_zero_citations(self):
        m = copy.deepcopy(MANIFEST); m["articles"][0]["candidate"]["citations"] = 0
        with self.assertRaises(ValueError): GATE.check_manifest(m)

    def test_parent_crosswalk_ref_immutability(self):
        m = copy.deepcopy(MANIFEST); m["articles"][2]["candidate"]["commit"] = "a" * 40
        with self.assertRaises(ValueError): GATE.check_manifest(m)

    def test_slug_path_traversal(self):
        row, v = make_row(2); row["slug"] = "../../evil"
        with self.assertRaises(ValueError): GATE.check_row(row, lambda ref, path: v[{"a"*40:"pinned", "b"*40:"upstream", "c"*40:"candidate"}[ref]])

    def test_cite_parser_invalid(self):
        with self.assertRaises(ValueError): GATE.source_tokens(b"{{cite:invalid id}}")

    def test_cite_parser_incomplete(self):
        with self.assertRaises(ValueError): GATE.source_tokens(b"{{cite:missing")

    def test_source_normalization_only_line_endings(self):
        self.assertEqual(GATE.normalize_eol(b"a\r\nb"), b"a\nb")
        self.assertNotEqual(GATE.normalize_eol(b"a  b"), b"a b")

    def test_git_blob_real_object(self):
        self.assertEqual(GATE.git_blob(b"hello\n"), "ce013625030ba8dba906f756967f9e9ca394464a")

    def test_invalid_git_ref(self):
        with self.assertRaises(ValueError): GATE.read_git(".", "main", "preparedness/content/articles/a.body.html")

    def test_unsafe_git_path(self):
        with self.assertRaises(ValueError): GATE.read_git(".", "a"*40, "preparedness/../../secrets")


def make_review_test(index, variation):
    def one(self):
        row, originals = make_row(index)
        data = dict(originals)
        refs = {row[k]["commit"]: k for k in ("pinned", "upstream", "candidate")}
        if variation == "accept":
            result = GATE.check_row(row, lambda sha, _: data[refs[sha]])
            self.assertEqual(result["resolution"], row["resolution"])
            self.assertEqual(result["review"], "PENDING")
            return
        if variation == "candidate_word_mutation":
            data["candidate"] += b" <strong>unexpected text</strong>"
        elif variation == "pinned_edit":
            data["pinned"] = data["pinned"].replace(b"Documented", b"Suppressed")
        elif variation == "upstream_edit":
            data["upstream"] = data["upstream"].replace(b"source", b"source-adulterated")
        elif variation == "citation_deleted":
            data["candidate"] = data["candidate"].replace(b"{{cite:", b"{{omitted:")
        elif variation == "citation_substituted":
            data["candidate"] = data["candidate"].replace(b"{{cite:", b"{{cite:forged-")
        elif variation == "identity_forgery":
            row["candidate"]["blob"] = "0" * 40
        elif variation == "approval_without_evidence":
            row["resolution"] = "PUBLISHED_SAFE"
        else:
            raise RuntimeError(variation)
        with self.assertRaises(ValueError): GATE.check_row(row, lambda sha, _: data[refs[sha]])
    return one


class PerArticleAdversarial(unittest.TestCase):
    pass


for n in range(7):
    for var in ("accept", "candidate_word_mutation", "pinned_edit", "upstream_edit",
                "citation_deleted", "citation_substituted", "identity_forgery", "approval_without_evidence"):
        setattr(PerArticleAdversarial, f"test_article_{n}_{var}", make_review_test(n, var))


if __name__ == "__main__":
    unittest.main()
