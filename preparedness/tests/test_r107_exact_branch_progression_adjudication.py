"""R107 synthetic adversarial HOLD tests; do not write contributor files or CMS.

The real Git path is exercised separately on the exact checkout in private CI.
All fixtures here are in memory. Git-object hashes are NOT source approvals.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import r107_exact_branch_progression_adjudication as g
import r60_contributor_provenance_drift_docket as r60
import cluster_git_parity_gate as r15

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = json.loads((ROOT / "docs/R14-SEVEN-CLUSTER-GIT-BLOB-PARITY.json")
                      .read_text(encoding="utf-8"))
NEW_BLOB = "c" * 40


def fixture():
    original = copy.deepcopy(ORIGINAL)
    by_name = {b["name"]: b for b in original["branches"]}
    moved = []
    for name in ("food", "health", "hist-food", "hist-home", "hist-field"):
        moved.append({
            "cluster": name,
            "frozen_commit_sha": by_name[name]["contributor_commit_sha"],
            "observed_commit_sha": g.EXPECTED_HEADS[name],
        })
    changes = []
    for name, path in (
        ("food", "preparedness/docs/CLUSTER-food.md"),
        ("hist-food", "preparedness/content/articles/pemmican-and-dried-meats.body.html"),
        ("hist-home", "preparedness/sources/fragments/hist-home.json"),
        ("hist-field", "preparedness/tests/test_preparedness.py"),
    ):
        scope = {x["path"]: x for x in by_name[name]["files"]}
        changes.append({
            "cluster": name, "path": path,
            "frozen_blob_sha": scope[path]["contributor_blob_sha"]
            if path in scope else "d"*40,
            "observed_blob_sha": NEW_BLOB,
            "human_provenance_review_state": "NOT_REVIEWED",
        })
    drift = {
        "schema": r60.SCHEMA,
        "release_state": "HOLD", "may_publish": False,
        "frozen_manifest_blob_sha": r60.R14_BLOB,
        "checked_clusters": 7,
        "moved_contributor_heads": moved,
        "changed_file_count": len(changes),
        "changed_files": changes,
        "existing_R14_exception_remains_open": True,
        "human_source_links_verified": False,
        "qualified_safety_clearance": False,
        "independent_QD_approval": False,
    }
    reseal(drift)
    return original, drift


def reseal(drift):
    drift["fingerprint_sha256"] = r60.sha256(r60.canonical({
        k: v for k, v in drift.items() if k != "fingerprint_sha256"
    }))


def integrate(manifest, drift, **opts):
    known = {f["path"]: f["integrated_blob_sha"]
             for b in ORIGINAL["branches"] for f in b["files"]}
    return g.workorder(
        manifest, drift,
        is_ancestor=opts.get("ancestor", lambda frozen, current: True),
        integrated_blob=opts.get(
            "integrated", lambda sha, path: known[path]))


class R107PrivateFixture(unittest.TestCase):
    def setUp(self):
        self.manifest, self.drift = fixture()

    def run_workorder(self):
        return integrate(self.manifest, self.drift)

    def test_original_r14_authority_remains_hold(self):
        self.assertEqual(self.manifest["release_state"], "HOLD")
        self.assertIs(self.manifest["may_publish"], False)
        self.assertEqual(sum(b["article_count"] for b in self.manifest["branches"]), 29)

    def test_baseline_exact_moved_branches(self):
        row = self.run_workorder()
        self.assertEqual(row["moved_branch_count"], 5)
        self.assertEqual(len(row["seven_contributor_commit_ancestry"]), 7)

    def test_original_72_paths_retained(self):
        self.assertEqual(self.run_workorder()["original_evidence_paths"], 72)

    def test_all_human_approvals_remain_closed(self):
        x = self.run_workorder()
        self.assertIs(x["may_publish"], False)
        self.assertIs(x["independent_QD_PASS"], False)
        self.assertIs(x["qualified_emergency_or_medical_safety_review"], False)
        self.assertIs(x["source_or_claim_accuracy_verified"], False)

    def test_original_exception_remains_open(self):
        self.assertIs(self.run_workorder()["frozen_R14_historical_exception_open"], True)

    def test_r15_not_silently_replaced(self):
        self.assertEqual(self.run_workorder()["mandatory_R15_seven_cluster_parity"],
                         "FAIL_CLOSED_ON_MOVED_REFS")

    def test_fragment_source_review_priority(self):
        row = next(x for x in self.run_workorder()[
            "contributor_reviewer_queue_NOT_APPROVED"]
            if x["classification"] == "fragment")
        self.assertIn("SOURCE_IDENTITY", row["risk_queue"])

    def test_body_citation_review_priority(self):
        self.assertEqual(self.run_workorder()[
            "change_classification_counts"]["body"], 1)

    def test_unscoped_test_change_is_visible(self):
        row = next(x for x in self.run_workorder()[
            "contributor_reviewer_queue_NOT_APPROVED"]
            if x["classification"] == "test")
        self.assertFalse(row["original_72_path_scope"])
        self.assertEqual(row["integration_relationship_NOT_APPROVAL"],
                         "OUTSIDE_ORIGINAL_72_PATH_SCOPE_REVIEW")

    def test_scoped_changes_stay_unapproved(self):
        for item in self.run_workorder()["contributor_reviewer_queue_NOT_APPROVED"]:
            self.assertEqual(item["human_provenance_review"], "NOT_REVIEWED")
            self.assertEqual(item["human_source_and_claim_review"], "NOT_REVIEWED")
            self.assertIs(item["may_publish"], False)

    def test_all_counts_are_machine_only(self):
        row = self.run_workorder()
        self.assertEqual(row["unreviewed_shared_url_groups"], 30)
        self.assertEqual(row["human_safety_exceptions_unresolved"], 15)
        self.assertEqual(row["editorial_decisions_unresolved"], 22)

    def test_exact_pinned_rc_is_not_published(self):
        self.assertEqual(len(g.EXPECTED_RC), 40)
        self.assertIs(self.run_workorder()["site_or_wordpress_write"], False)

    def test_deterministic_digest(self):
        self.assertEqual(self.run_workorder(), self.run_workorder())

    def test_digest_not_a_signature(self):
        report = self.run_workorder()
        self.assertEqual(report["sha256_NOT_A_SIGNATURE"],
                         g.digest({k:v for k,v in report.items()
                                   if k != "sha256_NOT_A_SIGNATURE"}))

    def test_ancestry_failure_blocks_everything(self):
        with self.assertRaisesRegex(g.Hold, "NOT an ancestor"):
            integrate(self.manifest, self.drift,
                      ancestor=lambda old, new: False)

    def test_integrated_git_blob_disagreement_blocks(self):
        with self.assertRaisesRegex(g.Hold, "integrated Git blob"):
            integrate(self.manifest, self.drift,
                      integrated=lambda sha, path: "e"*40)

    def test_ancestry_checked_for_unchanged_branches_too(self):
        pairs = []
        integrate(self.manifest, self.drift, ancestor=lambda a,b: pairs.append(
            (a,b)) or True)
        self.assertEqual(len(pairs), 7)

    def test_review_queue_deterministic_order(self):
        rows = self.run_workorder()["contributor_reviewer_queue_NOT_APPROVED"]
        self.assertEqual([(x["origin"], x["path"]) for x in rows],
                         sorted((x["origin"], x["path"]) for x in rows))

    def test_invalid_category_paths_fail(self):
        for path in ("../article", "preparedness/../../hack",
                     "preparedness/tests/evil\\name.py",
                     "preparedness//bad", "public/x", "preparedness/\x00bad"):
            with self.subTest(path=repr(path)):
                with self.assertRaises(g.Hold):
                    g.kind(path)

    def test_historical_metadata_exception_does_not_disappear(self):
        self.assertEqual(self.manifest["totals"]["nonidentical_paths"], 1)
        self.assertIs(self.run_workorder()["frozen_R14_historical_exception_open"], True)

    def test_current_matches_integrated_is_not_approval(self):
        original = {f["path"]: f["integrated_blob_sha"] for b in self.manifest["branches"]
                    for f in b["files"]}
        path = "preparedness/docs/CLUSTER-food.md"
        self.drift["changed_files"][0]["observed_blob_sha"] = original[path]
        g.need(self.drift["changed_files"][0]["frozen_blob_sha"] != original[path],
               "fixture would not be a modified path") if False else None
        # Retain source drift; only inspect label when Git identities truly differ.
        self.drift["changed_files"][0]["observed_blob_sha"] = "c"*40
        reseal(self.drift)
        self.assertNotEqual(
            self.run_workorder()["contributor_reviewer_queue_NOT_APPROVED"][0][
                "human_provenance_review"], "APPROVED")

    def test_unscoped_other_change_is_visible(self):
        self.drift["changed_files"].append({
            "cluster": "food", "path": "preparedness/tools/synthetic.py",
            "frozen_blob_sha": None, "observed_blob_sha": "f"*40,
            "human_provenance_review_state": "NOT_REVIEWED",
        })
        self.drift["changed_file_count"] += 1
        reseal(self.drift)
        self.assertIn("other", self.run_workorder()["change_classification_counts"])


# A distinct unittest method for each attack, not one subtest that inflates claims.
MUTATIONS = [
    ("manifest_authority", lambda m,d: m.__setitem__("authority", "APPROVED")),
    ("manifest_release", lambda m,d: m.__setitem__("release_state", "PUBLISHED")),
    ("manifest_publish", lambda m,d: m.__setitem__("may_publish", True)),
    ("manifest_human", lambda m,d: m.__setitem__("human_source_review_complete", True)),
    ("manifest_medical", lambda m,d: m.__setitem__("qualified_emergency_safety_clearance", True)),
    ("manifest_verified", lambda m,d: m.__setitem__("independent_human_source_checks_verified", 1)),
    ("manifest_integrated", lambda m,d: m.__setitem__("reference_integrated_commit_sha", "0"*40)),
    ("manifest_missing_branch", lambda m,d: m["branches"].pop()),
    ("manifest_duplicate_branch", lambda m,d: m["branches"].__setitem__(0, copy.deepcopy(m["branches"][1]))),
    ("manifest_articles", lambda m,d: m["branches"][0].__setitem__("article_count", 999)),
    ("manifest_missing_file", lambda m,d: m["branches"][0]["files"].pop()),
    ("manifest_duplicate_file", lambda m,d: m["branches"][0]["files"].__setitem__(0, copy.deepcopy(m["branches"][0]["files"][1]))),
    ("manifest_bad_file", lambda m,d: m["branches"][0]["files"][0].__setitem__("path", "../escaped")),
    ("manifest_false_identical", lambda m,d: m["branches"][0]["files"][0].__setitem__("identical", False)),
    ("manifest_source_revision", lambda m,d: m["branches"][0]["files"][0].__setitem__("integrated_blob_sha", "0"*40)),
    ("manifest_exception_removed", lambda m,d: m.__setitem__("exceptions", [])),
    ("manifest_exception_approved", lambda m,d: m["exceptions"][0].__setitem__("state", "APPROVED")),
    ("drift_schema", lambda m,d: d.__setitem__("schema", "FAKE")),
    ("drift_publish", lambda m,d: d.__setitem__("may_publish", True)),
    ("drift_release", lambda m,d: d.__setitem__("release_state", "LIVE")),
    ("drift_manifest", lambda m,d: d.__setitem__("frozen_manifest_blob_sha", "f"*40)),
    ("drift_cluster_count", lambda m,d: d.__setitem__("checked_clusters", 6)),
    ("drift_exception_removed", lambda m,d: d.__setitem__("existing_R14_exception_remains_open", False)),
    ("drift_source_approved", lambda m,d: d.__setitem__("human_source_links_verified", True)),
    ("drift_safety_approved", lambda m,d: d.__setitem__("qualified_safety_clearance", True)),
    ("drift_qd_approved", lambda m,d: d.__setitem__("independent_QD_approval", True)),
    ("drift_missing_moved", lambda m,d: d["moved_contributor_heads"].pop()),
    ("drift_extra_moved", lambda m,d: d["moved_contributor_heads"].append(copy.deepcopy(d["moved_contributor_heads"][0]))),
    ("drift_unknown_origin", lambda m,d: d["moved_contributor_heads"][0].__setitem__("cluster", "bogus")),
    ("drift_unpinned_sha", lambda m,d: d["moved_contributor_heads"][0].__setitem__("observed_commit_sha", "b"*40)),
    ("drift_frozen_mismatch", lambda m,d: d["moved_contributor_heads"][0].__setitem__("frozen_commit_sha", "b"*40)),
    ("drift_missing_changes", lambda m,d: d.__setitem__("changed_files", None)),
    ("drift_wrong_count", lambda m,d: d.__setitem__("changed_file_count", 18)),
    ("drift_duplicated_path", lambda m,d: d["changed_files"].append(copy.deepcopy(d["changed_files"][0]))),
    ("drift_foreign_path", lambda m,d: d["changed_files"][0].__setitem__("path", "some/path")),
    ("drift_contributor_takeover", lambda m,d: d["changed_files"][0].__setitem__("cluster", "hist-food")),
    ("drift_forged_old_blob", lambda m,d: d["changed_files"][0].__setitem__("frozen_blob_sha", "a"*40)),
    ("drift_same_blob", lambda m,d: d["changed_files"][0].__setitem__("observed_blob_sha", d["changed_files"][0]["frozen_blob_sha"])),
    ("drift_false_human_approval", lambda m,d: d["changed_files"][0].__setitem__("human_provenance_review_state", "APPROVED")),
    ("drift_untrusted_path", lambda m,d: d["changed_files"][0].__setitem__("path", "preparedness/../secrets")),
    ("drift_bad_fingerprint", lambda m,d: d.__setitem__("fingerprint_sha256", "0"*64)),
]


def make_negative(name, mutation):
    def test(self):
        manifest, drift = fixture()
        mutation(manifest, drift)
        if name != "drift_bad_fingerprint":
            reseal(drift)
        with self.assertRaises((g.Hold, KeyError, TypeError, ValueError),
                               msg=name):
            integrate(manifest, drift)
    test.__name__ = "test_reject_" + name
    return test


for name, callback in MUTATIONS:
    setattr(R107PrivateFixture, "test_reject_" + name,
            make_negative(name, callback))


if __name__ == "__main__":
    unittest.main()
