"""R146 adversarial tests. All fixtures are synthetic; no source or safety approval."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

TOOL = Path(__file__).resolve().parents[1] / "tools" / "r146_head_custody.py"
SPEC = importlib.util.spec_from_file_location("r146_head_custody", TOOL)
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)

FAKE_SHA = lambda n: f"{n + 1:040x}"


def synthetic_lock():
    items = []
    for i in range(35):
        stem = f"preparedness/content/articles/fictional-{i:02d}"
        items.extend(({"path": stem + ".body.html", "blob_sha": FAKE_SHA(i)},
                      {"path": stem + ".meta.json", "blob_sha": FAKE_SHA(35 + i)}))
    for i in range(10):
        items.append({"path": f"preparedness/sources/fragments/synthetic-{i}.json",
                      "blob_sha": FAKE_SHA(70 + i)})
    return {"files": items, "source_release_candidate":
            "ddb3528ba6494dada1fa1c3a142ce746e3a67706",
            "expected_citation_occurrences": 2000, "may_publish": False,
            "qd_pass": False, "medical_safety_verified": False,
            "merchant_offer_verified": False}


def tree_bytes(locked, additions=m.ADDITIONS):
    entries = []
    for path, sha in sorted(locked.items()):
        entries.append(f"100644 blob {sha}\t{path}".encode() + b"\0")
    for i, path in enumerate(sorted(additions)):
        entries.append(f"100644 blob {FAKE_SHA(100+i)}\t{path}".encode() + b"\0")
    return b"".join(entries)


def diff_bytes(additions=m.ADDITIONS):
    return b"".join(b"A\0" + path.encode() + b"\0" for path in sorted(additions))


class TestLockValidation(unittest.TestCase):
    def test_exact_80_originals_pass(self):
        lock = m.parse_lock(json.dumps(synthetic_lock()).encode())
        self.assertEqual(len(lock), 80)

    def test_missing_release_candidate_pin_rejected(self):
        d = synthetic_lock()
        d["source_release_candidate"] = "0" * 40
        with self.assertRaises(m.Hold):
            m.parse_lock(json.dumps(d).encode())

    def test_wrong_citation_baseline_rejected(self):
        d = synthetic_lock()
        d["expected_citation_occurrences"] = 1999
        with self.assertRaises(m.Hold):
            m.parse_lock(json.dumps(d).encode())

    def test_duplicate_article_pair_rejected(self):
        d = synthetic_lock()
        d["files"][1]["path"] = d["files"][0]["path"]
        with self.assertRaises(m.Hold):
            m.parse_lock(json.dumps(d).encode())

    def test_traversal_in_lock_rejected(self):
        d = synthetic_lock()
        d["files"][1]["path"] = "preparedness/../outside"
        with self.assertRaises(m.Hold):
            m.parse_lock(json.dumps(d).encode())

    def test_bad_sha_in_lock_rejected(self):
        d = synthetic_lock()
        d["files"][1]["blob_sha"] = "abc"
        with self.assertRaises(m.Hold):
            m.parse_lock(json.dumps(d).encode())

    def test_extra_metadata_no_body_rejected(self):
        d = synthetic_lock()
        d["files"][0]["path"] = "preparedness/content/articles/orphan.meta.json"
        with self.assertRaises(m.Hold):
            m.parse_lock(json.dumps(d).encode())

    def test_invalid_json_fails_closed(self):
        with self.assertRaises(m.Hold):
            m.parse_lock(b"{incomplete")

    def test_invalid_unicode_fails_closed(self):
        with self.assertRaises(m.Hold):
            m.parse_lock(b"\xff")

    def test_approval_flags_cannot_be_forged(self):
        for field in ("may_publish", "qd_pass", "medical_safety_verified",
                      "merchant_offer_verified"):
            with self.subTest(field=field):
                d = synthetic_lock()
                d[field] = True
                with self.assertRaises(m.Hold):
                    m.parse_lock(json.dumps(d).encode())


class TestTreeAndChanges(unittest.TestCase):
    def setUp(self):
        self.locked = m.parse_lock(json.dumps(synthetic_lock()).encode())
        self.tree = tree_bytes(self.locked)

    def test_valid_current_tree(self):
        report = m.check_current_tree(self.tree, self.locked)
        self.assertEqual(report["original_git_blobs_unchanged_at_current_head"], 80)
        self.assertEqual(report["review_additions_present"], 3)

    def test_valid_additions(self):
        self.assertEqual(m.check_review_diff(diff_bytes()), 3)

    def test_old_source_can_not_be_replaced_even_when_additions_only(self):
        target = next(iter(self.locked))
        self.assertEqual(m.check_review_diff(diff_bytes()), 3)
        mutated = self.tree.replace(self.locked[target].encode(),
                                    FAKE_SHA(310).encode(), 1)
        with self.assertRaisesRegex(m.Hold, "CHANGED"):
            m.check_current_tree(mutated, self.locked)

    def test_unknown_new_review_file_is_rejected(self):
        with self.assertRaises(m.Hold):
            m.check_review_diff(diff_bytes() + b"A\0preparedness/docs/rogue.md\0")

    def test_existing_article_modification_rejected(self):
        with self.assertRaisesRegex(m.Hold, "non-additive"):
            m.check_review_diff(diff_bytes() +
                                b"M\0preparedness/content/articles/a.body.html\0")

    def test_existing_sources_deletion_rejected(self):
        with self.assertRaisesRegex(m.Hold, "non-additive"):
            m.check_review_diff(diff_bytes() +
                                b"D\0preparedness/sources/fragments/start.json\0")

    def test_rename_rejected(self):
        with self.assertRaisesRegex(m.Hold, "unexpected Git diff|non-additive"):
            m.check_review_diff(diff_bytes() +
                                b"R100\0preparedness/x\0preparedness/y\0")

    def test_unrelated_site_change_rejected(self):
        with self.assertRaisesRegex(m.Hold, "change-set mismatch"):
            m.check_review_diff(diff_bytes() + b"A\0public/homepage.html\0")

    def test_duplicate_change_rejected(self):
        path = sorted(m.ADDITIONS)[0].encode()
        with self.assertRaisesRegex(m.Hold, "duplicate"):
            m.check_review_diff(diff_bytes() + b"A\0" + path + b"\0")

    def test_missing_review_test_rejected(self):
        paths = set(m.ADDITIONS)
        paths.remove("preparedness/tests/test_r146_head_custody.py")
        with self.assertRaisesRegex(m.Hold, "missing="):
            m.check_review_diff(diff_bytes(paths))

    def test_truncated_diff_rejected(self):
        with self.assertRaises(m.Hold):
            m.check_review_diff(diff_bytes()[:-1])

    def test_truncated_tree_rejected(self):
        with self.assertRaises(m.Hold):
            m.check_current_tree(self.tree[:-1], self.locked)

    def test_symlink_rejected(self):
        modified = self.tree.replace(b"100644 blob ", b"120000 blob ", 1)
        with self.assertRaisesRegex(m.Hold, "symlink"):
            m.check_current_tree(modified, self.locked)

    def test_gitlink_rejected(self):
        modified = self.tree.replace(b"100644 blob ", b"160000 commit ", 1)
        with self.assertRaisesRegex(m.Hold, "symlink"):
            m.check_current_tree(modified, self.locked)

    def test_executable_original_evidence_rejected(self):
        modified = self.tree.replace(b"100644 blob ", b"100755 blob ", 1)
        with self.assertRaisesRegex(m.Hold, "mode CHANGED"):
            m.check_current_tree(modified, self.locked)

    def test_executable_review_script_rejected(self):
        p = "preparedness/tools/r146_head_custody.py"
        original = f"100644 blob {FAKE_SHA(102)}\t{p}\0".encode()
        changed = original.replace(b"100644", b"100755")
        with self.assertRaises(m.Hold):
            m.check_current_tree(self.tree.replace(original, changed), self.locked)

    def test_no_automatic_publication_approval(self):
        self.assertEqual(m.STATUS, "DRAFT_HOLD")

    def test_parse_diff_malformed_utf8(self):
        with self.assertRaises(UnicodeError):
            m.parse_name_status(b"A\0\xff\0")

    def test_tree_duplicate_rejected(self):
        a = self.tree.split(b"\0")[0] + b"\0"
        with self.assertRaises(m.Hold):
            m.parse_tree(self.tree + a)


# Generate discrete, independently reported mutations for EVERY original blob.
for index in range(80):
    def corrupt(self, position=index):
        locked = m.parse_lock(json.dumps(synthetic_lock()).encode())
        path = list(locked)[position]
        old = locked[path]
        tree = tree_bytes(locked)
        old_record = f"100644 blob {old}\t{path}\0".encode()
        new_record = f"100644 blob {FAKE_SHA(200+position)}\t{path}\0".encode()
        self.assertIn(old_record, tree)
        with self.assertRaisesRegex(m.Hold, "CHANGED"):
            m.check_current_tree(tree.replace(old_record, new_record), locked)
    setattr(TestTreeAndChanges, f"test_mutate_original_{index:02d}_must_hold", corrupt)


# Missing articles are distinguished from citation-count-only checks.
for index in range(35):
    def missing(self, position=index):
        locked = m.parse_lock(json.dumps(synthetic_lock()).encode())
        path = f"preparedness/content/articles/fictional-{position:02d}.body.html"
        tree = tree_bytes(locked)
        old_record = f"100644 blob {locked[path]}\t{path}\0".encode()
        with self.assertRaisesRegex(m.Hold, "missing"):
            m.check_current_tree(tree.replace(old_record, b""), locked)
    setattr(TestTreeAndChanges, f"test_missing_article_{index:02d}_must_hold", missing)


class TestRealLocalGit(unittest.TestCase):
    """Real git commands on temporary, synthetic 80-blob repositories."""
    def run_git(self, *args):
        p = subprocess.run(["git", "-C", str(self.repo), *args],
                           check=True, capture_output=True, text=True)
        return p.stdout.strip()

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="fv-r146-local-fixture-")
        cls.repo = Path(cls.temp.name)
        subprocess.run(["git", "init", "-q", str(cls.repo)],
                       check=True, capture_output=True)
        files = synthetic_lock()
        for item in files["files"]:
            f = cls.repo / item["path"]
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(f"synthetic evidence: {item['path']}\n")
            item["blob_sha"] = subprocess.run(
                ["git", "hash-object", str(f)],
                capture_output=True, check=True, text=True).stdout.strip()
        lockpath = cls.repo / m.LOCK_FILE
        lockpath.parent.mkdir(parents=True, exist_ok=True)
        lockpath.write_text(json.dumps(files, indent=2))
        subprocess.run(["git", "-C", str(cls.repo), "add", "."],
                       check=True, capture_output=True)
        subprocess.run(["git", "-C", str(cls.repo), "-c", "user.name=FV Test",
                        "-c", "user.email=test@example.invalid", "commit",
                        "-qm", "synthetic fixed original"], check=True)
        cls.base = subprocess.run(
            ["git", "-C", str(cls.repo), "rev-parse", "HEAD"],
            capture_output=True, check=True, text=True).stdout.strip()
        cls.lock_blob = subprocess.run(
            ["git", "-C", str(cls.repo), "rev-parse", f"{cls.base}:{m.LOCK_FILE}"],
            capture_output=True, check=True, text=True).stdout.strip()
        for relative in sorted(m.ADDITIONS):
            f = cls.repo / relative
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("synthetic review file\n")
        subprocess.run(["git", "-C", str(cls.repo), "add", "."],
                       check=True, capture_output=True)
        subprocess.run(["git", "-C", str(cls.repo), "-c", "user.name=FV Test",
                        "-c", "user.email=test@example.invalid", "commit",
                        "-qm", "synthetic review additions"], check=True)
        cls.head = subprocess.run(
            ["git", "-C", str(cls.repo), "rev-parse", "HEAD"],
            capture_output=True, check=True, text=True).stdout.strip()

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.run_git("reset", "--hard", self.head)
        self.run_git("clean", "-fdq")

    def inspect(self, expected=None):
        return m.inspect_checkout(
            self.repo, expected or self.head, base=self.base,
            expected_lock_sha=self.lock_blob)

    def test_real_git_authentic_additions_pass(self):
        report = self.inspect()
        self.assertEqual(report["original_git_blobs_unchanged_at_current_head"], 80)
        self.assertFalse(report["publication_allowed"])

    def test_real_git_dirty_original_held(self):
        target = self.repo / "preparedness/content/articles/fictional-00.body.html"
        target.write_text("dirty but not committed")
        with self.assertRaisesRegex(m.Hold, "uncommitted"):
            self.inspect()

    def test_real_git_untracked_staging_file_held(self):
        p = self.repo / "preparedness" / "rogue.txt"
        p.write_text("unexpected")
        with self.assertRaisesRegex(m.Hold, "uncommitted"):
            self.inspect()

    def test_real_git_head_mismatch_held(self):
        with self.assertRaisesRegex(m.Hold, "HEAD moved"):
            self.inspect(self.base)

    def test_real_git_committed_original_mutation_held(self):
        target = self.repo / "preparedness/content/articles/fictional-01.body.html"
        target.write_text("changed content, citations could silently be lost")
        self.run_git("add", ".")
        self.run_git("-c", "user.name=FV Test", "-c",
                     "user.email=test@example.invalid", "commit", "-qm", "mutate")
        changed_head = self.run_git("rev-parse", "HEAD")
        with self.assertRaisesRegex(m.Hold, "non-additive"):
            self.inspect(changed_head)

    def test_real_git_extra_new_file_held(self):
        p = self.repo / "preparedness/docs/r146/unapproved.txt"
        p.write_text("extra")
        self.run_git("add", ".")
        self.run_git("-c", "user.name=FV Test", "-c",
                     "user.email=test@example.invalid", "commit", "-qm", "extra")
        changed_head = self.run_git("rev-parse", "HEAD")
        with self.assertRaisesRegex(m.Hold, "change-set mismatch"):
            self.inspect(changed_head)


if __name__ == "__main__":
    unittest.main()
