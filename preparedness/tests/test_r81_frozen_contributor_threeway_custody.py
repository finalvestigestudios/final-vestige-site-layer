"""R81 PRIVATE HOLD — full synthetic Git graph and adversarial release-custody tests."""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

FILE = Path(__file__).resolve().parents[1] / "tools" / "r81_frozen_contributor_threeway_custody.py"
SPEC = importlib.util.spec_from_file_location("r81_under_test", FILE)
r81 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r81)
COUNTS = {"start": 4, "shelter": 4, "food": 4, "health": 3,
          "hist-food": 6, "hist-home": 5, "hist-field": 3}


def shell(repo, *args):
    p = subprocess.run(["git", "-C", str(repo), *args], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout.decode("utf-8").strip()


class SyntheticGitFixture(unittest.TestCase):
    """Construct a real 72-path, 29-article Git graph entirely in a temp dir."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="fv-r81-private-fixture-")
        cls.repo = Path(cls.tmp.name) / "site"
        cls.repo.mkdir()
        shell(cls.repo, "init", "-q")
        shell(cls.repo, "config", "user.email", "r81-fixture@example.invalid")
        shell(cls.repo, "config", "user.name", "R81 Synthetic Fixture")
        cls.paths = {}
        for origin, n in COUNTS.items():
            files = []
            for i in range(n):
                slug = "synthetic-" + origin + "-" + str(i)
                files.extend((
                    "preparedness/content/articles/" + slug + ".body.html",
                    "preparedness/content/articles/" + slug + ".meta.json"))
            files.extend(("preparedness/docs/CLUSTER-" + origin + ".md",
                          "preparedness/sources/fragments/" + origin + ".json"))
            cls.paths[origin] = files
            for path in files:
                dest = cls.repo / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                if path.endswith(".body.html"):
                    raw = "<p>Not medical advice. {{cite:common}}</p>\n"
                elif path.endswith(".meta.json"):
                    raw = '{"status":"drafted-pending-safety-review","human_approval":false}\n'
                elif path.endswith(".json"):
                    raw = json.dumps({"sources": [{
                        "id": "common", "url": "https://example.invalid/shared-review-only",
                        "publisher": "Synthetic Fixture", "human_link_check": False,
                        "supports": "NOT REVIEWED. Complete unabridged synthetic record",
                        "notes": "Not an independently verified source."
                    }]}, sort_keys=True)
                else:
                    raw = "# Synthetic cluster; not a publishable article.\n"
                dest.write_text(raw, encoding="utf-8")
        shell(cls.repo, "add", "preparedness")
        shell(cls.repo, "commit", "-qm", "Frozen synthetic 7 contributors")
        cls.frozen = shell(cls.repo, "rev-parse", "HEAD")
        cls.manifest = {
            "schema_version": 1, "authority":
                "GIT_BLOB_PARITY_ONLY_NOT_FACT_OR_SAFETY_APPROVAL",
            "issue": 136, "release_state": "HOLD", "may_publish": False,
            "reference_integrated_commit_sha": cls.frozen,
            "human_source_review_complete": False,
            "independent_human_source_checks_verified": 0,
            "qualified_emergency_safety_clearance": False,
            "branches": [], "exceptions": [],
            "totals": {"contributor_branches": 7, "cluster_authored_articles": 29,
                       "scoped_blob_paths": 72, "exact_matches": 72,
                       "nonidentical_paths": 0},
        }
        for origin, paths in cls.paths.items():
            records = []
            for path in paths:
                sha = shell(cls.repo, "rev-parse", cls.frozen + ":" + path)
                records.append({
                    "path": path, "contributor_blob_sha": sha,
                    "integrated_blob_sha": sha, "identical": True})
            cls.manifest["branches"].append({
                "name": origin, "contributor_commit_sha": cls.frozen,
                "article_count": COUNTS[origin], "scoped_paths": len(paths),
                "exact_matches": len(paths), "nonidentical_paths": 0,
                "files": records})
        # Contributor food advances beyond historical frozen research.
        shell(cls.repo, "checkout", "-qb", "synthetic-advanced")
        cls.advanced_path = cls.paths["food"][0]
        (cls.repo / cls.advanced_path).write_text(
            "<p>Advanced unpublished source claim {{cite:common}}</p>\n",
            encoding="utf-8")
        shell(cls.repo, "add", cls.advanced_path)
        shell(cls.repo, "commit", "-qm", "Unreviewed contributor advance")
        cls.advanced = shell(cls.repo, "rev-parse", "HEAD")
        # Independent RC diverges on food and also alters a start article.
        shell(cls.repo, "checkout", "--detach", "-q", cls.frozen)
        cls.start_path = cls.paths["start"][0]
        (cls.repo / cls.start_path).write_text(
            "<p>RC editorial wording {{cite:common}}{{cite:common}}</p>\n",
            encoding="utf-8")
        (cls.repo / cls.advanced_path).write_text(
            "<p>RC THIRD UNREVIEWED VERSION {{cite:common}}</p>\n",
            encoding="utf-8")
        shell(cls.repo, "add", "preparedness")
        shell(cls.repo, "commit", "-qm", "Separate synthetic RC")
        cls.rc = shell(cls.repo, "rev-parse", "HEAD")
        cls.heads = {name: cls.frozen for name in COUNTS}
        cls.heads["food"] = cls.advanced
        cls.report = r81.three_way(cls.repo, cls.manifest, cls.heads, cls.rc)
        r81.verify(cls.report)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_001_seven_scoped_contributors(self):
        self.assertEqual(len(self.report["branch_reviews"]), 7)

    def test_002_exact_29_authored_article_scope(self):
        self.assertEqual(self.report["counts"]["cluster_authored_articles"], 29)

    def test_003_exact_72_scoped_blob_paths(self):
        self.assertEqual(len(self.report["all_72_three_way_scoped_Git_blob_reviews"]), 72)

    def test_004_sources_distinct_by_origin(self):
        self.assertEqual(len(self.report["all_RC_fragment_source_readings_UNABRIDGED_NOT_APPROVED"]), 7)

    def test_005_same_url_not_one_source(self):
        self.assertEqual(len(self.report["shared_exact_URL_groups_NOT_ALIASED"]), 1)
        self.assertEqual(len(self.report["shared_exact_URL_groups_NOT_ALIASED"][0][
            "distinct_origin_readings"]), 7)

    def test_006_same_id_not_one_source(self):
        self.assertEqual(len(self.report["reused_ID_groups_NOT_ALIASED"]), 1)
        self.assertEqual(len(self.report["reused_ID_groups_NOT_ALIASED"][0][
            "distinct_origin_readings"]), 7)

    def test_007_advanced_contributor_detected(self):
        self.assertEqual(self.report["counts"]["current_advanced_branches"], 1)

    def test_008_advanced_branch_has_frozen_ancestor(self):
        food = next(b for b in self.report["branch_reviews"] if b["origin"] == "food")
        self.assertTrue(food["frozen_is_ancestor_of_current"])

    def test_009_three_distinct_versions_not_silently_merged(self):
        item = next(x for x in self.report["all_72_three_way_scoped_Git_blob_reviews"]
                    if x["path"] == self.advanced_path)
        self.assertEqual(item["comparison"], "THREE_DISTINCT_BLOBS_REVIEW")
        self.assertEqual(len({item["frozen_blob"], item["current_blob"], item["rc_blob"]}), 3)

    def test_010_rc_differs_from_unchanged_contributor(self):
        item = next(x for x in self.report["all_72_three_way_scoped_Git_blob_reviews"]
                    if x["path"] == self.start_path)
        self.assertEqual(item["comparison"], "RC_DIFFERS_FROM_UNCHANGED_CONTRIBUTOR")

    def test_011_all_origins_scoped(self):
        self.assertEqual({r["origin"] for r in self.report[
            "all_72_three_way_scoped_Git_blob_reviews"]}, set(COUNTS))

    def test_012_all_sha256_file_evidence_present(self):
        for row in self.report["all_72_three_way_scoped_Git_blob_reviews"]:
            self.assertTrue(all(len(v) == 64 for v in
                                row["sha256_entire_file_bytes"].values()))

    def test_013_whole_byte_counts_not_summarized(self):
        for row in self.report["all_72_three_way_scoped_Git_blob_reviews"]:
            self.assertTrue(all(v > 0 for v in row["byte_lengths"].values()))

    def test_014_contributor_reading_per_origin_not_shortened(self):
        for row in self.report["all_72_three_way_scoped_Git_blob_reviews"]:
            for variant in ("frozen", "R14_integrated", "current", "rc"):
                self.assertIn(variant, row["sha256_entire_file_bytes"])

    def test_015_rc_citation_count_tracks_literal_tokens(self):
        item = next(x for x in self.report["all_72_three_way_scoped_Git_blob_reviews"]
                    if x["path"] == self.start_path)
        self.assertEqual(item["citation_token_counts_NOT_CLAIM_PROOF"]["rc"], 2)

    def test_016_full_unreviewed_source_metadata_survives(self):
        for rec in self.report["all_RC_fragment_source_readings_UNABRIDGED_NOT_APPROVED"]:
            self.assertEqual(rec["complete_reading_NOT_HUMAN_VERIFIED"]["notes"],
                             "Not an independently verified source.")

    def test_017_no_source_link_approval(self):
        self.assertEqual(self.report["human_source_approvals"], 0)

    def test_018_no_claim_approval(self):
        self.assertEqual(self.report["human_claim_approvals"], 0)

    def test_019_no_medical_or_emergency_clearance(self):
        self.assertEqual(self.report["qualified_safety_approvals"], 0)

    def test_020_no_independent_QD_approval(self):
        self.assertEqual(self.report["independent_QD_approvals"], 0)

    def test_021_no_publication_state(self):
        self.assertIs(self.report["may_publish"], False)

    def test_022_deterministic_seal(self):
        self.assertEqual(self.report, r81.three_way(
            self.repo, self.manifest, self.heads, self.rc))

    def test_023_csv_never_masquerades_as_approval(self):
        s = r81.reviewer_csv(self.report)
        self.assertIn("NOT_REVIEWED", s)
        self.assertIn("HOLD", s)
        self.assertEqual(len(s.splitlines()), 73)

    def test_024_readonly_audit_does_not_change_checkout(self):
        self.assertFalse(shell(self.repo, "status", "--porcelain"))

    def test_025_manifest_stays_HOLD(self):
        r81.guard_manifest(self.manifest)

    def test_026_blob_path_hash_matches_real_git(self):
        row = self.report["all_72_three_way_scoped_Git_blob_reviews"][0]
        self.assertEqual(row["frozen_blob"], shell(
            self.repo, "rev-parse", self.frozen + ":" + row["path"]))

    def test_027_bad_current_pin_fails(self):
        heads = dict(self.heads)
        heads["food"] = "0" * 40
        with self.assertRaises(r81.Hold):
            r81.three_way(self.repo, self.manifest, heads, self.rc)

    def test_028_missing_origin_fails(self):
        heads = dict(self.heads)
        del heads["food"]
        with self.assertRaises(r81.Hold):
            r81.three_way(self.repo, self.manifest, heads, self.rc)

    def test_029_readonly_pin_rejects_wrong_refs(self):
        with self.assertRaises(r81.Hold):
            r81.three_way(self.repo, self.manifest, self.heads, self.rc,
                          verify_remote=True)

    def test_030_original_blob_evidence_mutation_fails(self):
        m = deepcopy(self.manifest)
        m["branches"][0]["files"][0]["contributor_blob_sha"] = "0" * 40
        with self.assertRaises(r81.Hold):
            r81.three_way(self.repo, m, self.heads, self.rc)

    def test_031_original_file_removed_fails(self):
        m = deepcopy(self.manifest)
        m["branches"][0]["files"].pop()
        with self.assertRaises(r81.Hold):
            r81.three_way(self.repo, m, self.heads, self.rc)

    def test_032_original_exception_approved_fails(self):
        m = deepcopy(self.manifest)
        m["exceptions"] = [{"branch":"start", "path":self.start_path,
                            "state":"APPROVED"}]
        m["totals"]["nonidentical_paths"] = 1
        m["totals"]["exact_matches"] = 71
        with self.assertRaises(r81.Hold):
            r81.guard_manifest(m)

    def test_033_all_paths_restricted_to_preparedness(self):
        for row in self.report["all_72_three_way_scoped_Git_blob_reviews"]:
            self.assertEqual(r81.safe_path(row["path"]), row["path"])

    def test_034_review_rows_are_distinct(self):
        rows = self.report["all_72_three_way_scoped_Git_blob_reviews"]
        self.assertEqual(len({(r["origin"], r["path"]) for r in rows}), 72)

    def test_035_no_unreviewed_source_marked_safe(self):
        for r in self.report["all_RC_fragment_source_readings_UNABRIDGED_NOT_APPROVED"]:
            self.assertEqual(r["qualified_safety_review"], "NOT_REVIEWED")

    def test_036_current_git_advancement_not_human_clearance(self):
        for b in self.report["branch_reviews"]:
            self.assertEqual(b["review_state"], "NOT_REVIEWED")

    def test_037_source_uses_literal_exact_url(self):
        for r in self.report["all_RC_fragment_source_readings_UNABRIDGED_NOT_APPROVED"]:
            self.assertEqual(r["exact_URL_UNVERIFIED"],
                             "https://example.invalid/shared-review-only")

    def test_038_no_git_mutation(self):
        self.assertEqual(shell(self.repo, "rev-parse", "HEAD"), self.rc)

    def test_039_missing_reseal_caught(self):
        p = deepcopy(self.report)
        p["counts"]["frozen_scoped_paths"] = 71
        with self.assertRaises(r81.Hold):
            r81.verify(p)

    def test_040_release_hold_remains_after_fake_reseal(self):
        p = deepcopy(self.report)
        p["may_publish"] = True
        p.pop("sha256_seal")
        p["sha256_seal"] = r81.sha256(json.dumps(
            p, sort_keys=True, ensure_ascii=False, allow_nan=False,
            separators=(",", ":")).encode())
        with self.assertRaises(r81.Hold):
            r81.verify(p)


class R81InputAdversarial(unittest.TestCase):
    def test_source_record_must_have_explicit_unreviewed_human_link_flag(self):
        with self.assertRaises(r81.Hold):
            r81.source_records(json.dumps({"sources": [{"id": "x",
                "url": "https://example.invalid/"}]}).encode(), "start")

    def test_source_record_requires_literal_url(self):
        with self.assertRaises(r81.Hold):
            r81.source_records(json.dumps({"sources": [{"id":"x", "url":"",
                "human_link_check":False}]}).encode(), "start")

    def test_source_record_does_not_equate_sources_by_url(self):
        records = [{"id":"x","url":"https://example.invalid/","human_link_check":False},
                   {"id":"y","url":"https://example.invalid/","human_link_check":False}]
        out = r81.source_records(json.dumps({"sources":records}).encode(), "start")
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0]["exact_URL_UNVERIFIED"],out[1]["exact_URL_UNVERIFIED"])

    def test_duplicate_ids_in_same_origin_fail(self):
        x = {"id":"x","url":"https://example.invalid/","human_link_check":False}
        with self.assertRaises(r81.Hold):
            r81.source_records(json.dumps({"sources":[x,x]}).encode(),"food")

    def test_source_records_preserve_unusual_fields(self):
        x = {"id":"x","url":"https://example.invalid/",
             "human_link_check":False,"full_quoted_context":"<>&\"'\\u202e"}
        parsed = r81.source_records(json.dumps({"sources":[x]}).encode(),"start")
        self.assertEqual(parsed[0]["complete_reading_NOT_HUMAN_VERIFIED"],x)

    def test_spreadsheet_formula_disarmed(self):
        for text in ("=2+3", "+SUM(A1:A2)", "-1+2", "@HYPERLINK(A1)", "\t=4", "\r=1"):
            self.assertTrue(r81.safe_csv(text).startswith("'"))

    def test_safe_csv_does_not_corrupt_regular_url(self):
        self.assertEqual(r81.safe_csv("https://example.invalid/x"),
                         "https://example.invalid/x")

    def test_r81_schema_explicitly_hard_hold(self):
        self.assertIn("hold",r81.SCHEMA)

    def test_real_manifest_has_original_frozen_exception(self):
        m = json.loads((FILE.parents[2] / r81.MANIFEST).read_text(encoding="utf-8"))
        r81.guard_manifest(m)
        self.assertEqual(len(m["exceptions"]), 1)

    def test_seven_current_contributor_pins_are_unique(self):
        self.assertEqual(len({v[1] for v in r81.PINNED.values()}),7)

    def test_rc_is_separate_from_all_contributor_pins(self):
        self.assertNotIn(r81.RC_SHA,{v[1] for v in r81.PINNED.values()})


INVALID_PATHS = [
    "/tmp/foo", "../preparedness/foo", "preparedness/../foo",
    "preparedness//x", "preparedness/./x", "preparedness/x/",
    "preparedness\\x", "preparedness/.git/config",
    "other/content", "", "preparedness/", "preparedness/\x00evil",
    "preparedness/a/../../etc", "preparedness/x/../y",
    "preparedness//", "preparedness/.git",
]

for n, bad_path in enumerate(INVALID_PATHS):
    def path_test(self, candidate=bad_path):
        with self.assertRaises(r81.Hold):
            r81.safe_path(candidate)
    setattr(R81InputAdversarial, "test_bad_path_%02d" % n, path_test)


BAD_SOURCE_PAYLOADS = [
    b"", b"\xff", b"null", b"[]", b"{}", b'{"sources":null}',
    b'{"sources":{}}', b'{"sources":[null]}',
    b'{"sources":[{}]}', b'{"sources":[{"id":"x","url":"https://e","human_link_check":true}]}',
    b'{"sources":[{"id":"x","url":"https://e","human_link_check":"false"}]}',
    b'{"sources":[{"id":13,"url":"https://e","human_link_check":false}]}',
]

for n, payload in enumerate(BAD_SOURCE_PAYLOADS):
    def source_test(self, raw=payload):
        with self.assertRaises(r81.Hold):
            r81.source_records(raw, "food")
    setattr(R81InputAdversarial, "test_bad_source_payload_%02d" % n, source_test)


CLASSIFICATIONS = [
    ("a","a","a","FROZEN_CURRENT_AND_RC_IDENTICAL"),
    ("a","b","b","RC_MATCHES_ADVANCED_CONTRIBUTOR"),
    ("a","b","a","RC_RETAINS_FROZEN_NOT_ADVANCED"),
    ("a","b","c","THREE_DISTINCT_BLOBS_REVIEW"),
    ("a","a","b","RC_DIFFERS_FROM_UNCHANGED_CONTRIBUTOR"),
]
for n,(a,b,c,expected) in enumerate(CLASSIFICATIONS):
    def classification_test(self, a=a, b=b, c=c, expected=expected):
        data={"a":"a"*40,"b":"b"*40,"c":"c"*40}
        self.assertEqual(r81.classify(data[a],data[b],data[c]),expected)
    setattr(R81InputAdversarial,"test_three_way_state_%02d"%n,classification_test)


if __name__ == "__main__":
    unittest.main()
