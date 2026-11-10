"""R272 synthetic adversarial source crosswalk tests; never release QA."""
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("r272", ROOT / "tools/r272_crosswalk_snapshot_hold.py")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

URL = "https://example.org/jerky"
SLASH = URL + "/"
OTHER = "https://example.org/other?language=en"
HEX = "a" * 40
CENSUS = {"rows": 3, "exact_urls": 3, "alias_urls": 2, "shared_groups": 1,
          "duplicate_id_groups": 1, "alias_variants": 1, "article_origins": 2}


def fixture():
    a = {"id": "shared-id", "url": URL, "supports": "Evidence A", "human_link_check": False}
    b = {"id": "shared-id", "url": SLASH, "supports": "Evidence B", "human_link_check": False}
    c = {"id": "solo-id", "url": OTHER, "supports": "Evidence C", "human_link_check": False}
    sources = {"base": [a, c], "food": [b]}
    paths = {"base": "preparedness/sources/register.json",
             "food": "preparedness/sources/fragments/food.json"}
    group = {
        "url": URL, "canonical_url": URL,
        "review_status": "pending-human-source-and-reading-scope-review",
        "reviewer": None, "reviewed_on": None,
        "variants": [
            {"origin": o, "source_file": paths[o], "row_index": 0, "source": copy.deepcopy(sources[o][0])}
            for o in ("base", "food")
        ],
        "identities": [{"origin": o, "row_index": 0, "id": "shared-id"} for o in ("base", "food")]
    }
    candidate = {"status": "DRAFT_UNREVIEWED_HOLD"}
    candidate.update({key: False for key in guard.FLAGS})
    x = {
        "schema_version": 1,
        "status": "DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED",
        "warning": "UNREVIEWED source reading scope; no safety approval",
        "source_files": [
            {"origin": o, "path": paths[o], "git_blob_sha": HEX, "count": len(sources[o])}
            for o in ("base", "food")
        ],
        "source_head_commits": {"base": HEX, "food": HEX},
        "article_origins": {"example-a": "base", "example-b": "food"},
        "groups": [group], "candidate_reconciliation_20261104": candidate,
        "raw_source_rows": 3, "unique_source_urls": 3,
        "duplicate_url_groups": 1, "duplicate_id_groups": 1
    }
    return x, sources


def replace_in(which, path, value):
    def change(x, sources):
        node = x if which == "x" else sources
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
    return change


def remove_in(which, path):
    def change(x, sources):
        node = x if which == "x" else sources
        for key in path[:-1]:
            node = node[key]
        del node[path[-1]]
    return change


CHANGES = {
    "schema": replace_in("x", ["schema_version"], 2),
    "status": replace_in("x", ["status"], "APPROVED"),
    "warning": replace_in("x", ["warning"], "approved"),
    "missing_origin": remove_in("sources", ["food"]),
    "invalid_origin_name": replace_in("x", ["source_files", 0, "origin"], "other"),
    "duplicate_origin": replace_in("x", ["source_files", 1, "origin"], "base"),
    "origin_count": replace_in("x", ["source_files", 0, "count"], 1),
    "origin_count_large": replace_in("x", ["source_files", 1, "count"], 7),
    "origin_sha": replace_in("x", ["source_files", 0, "git_blob_sha"], "fake"),
    "source_id": replace_in("sources", ["base", 0, "id"], "renamed"),
    "source_id_blank": replace_in("sources", ["base", 0, "id"], ""),
    "source_id_numeric": replace_in("sources", ["base", 0, "id"], 5),
    "url_scheme": replace_in("sources", ["food", 0, "url"], "http://example.org/jerky"),
    "url_authority": replace_in("sources", ["food", 0, "url"], "https://user@example.org/jerky"),
    "url_spacing": replace_in("sources", ["food", 0, "url"], " https://example.org/jerky"),
    "url_other": replace_in("sources", ["food", 0, "url"], "https://example.org/unrelated"),
    "new_shared_group": replace_in("sources", ["base", 1, "url"], URL),
    "variant_content": replace_in("x", ["groups", 0, "variants", 0, "source", "supports"], "Not A"),
    "variant_id": replace_in("x", ["groups", 0, "variants", 0, "source", "id"], "wrong"),
    "variant_index": replace_in("x", ["groups", 0, "variants", 0, "row_index"], 1),
    "variant_origin": replace_in("x", ["groups", 0, "variants", 0, "origin"], "food"),
    "variant_path": replace_in("x", ["groups", 0, "variants", 0, "source_file"], "other"),
    "variant_url": replace_in("x", ["groups", 0, "variants", 0, "source", "url"], OTHER),
    "variant_missing": remove_in("x", ["groups", 0, "variants", 1]),
    "group_url": replace_in("x", ["groups", 0, "url"], OTHER),
    "group_slash": replace_in("x", ["groups", 0, "url"], SLASH),
    "group_canonical": replace_in("x", ["groups", 0, "canonical_url"], OTHER),
    "group_status": replace_in("x", ["groups", 0, "review_status"], "approved"),
    "group_reviewer": replace_in("x", ["groups", 0, "reviewer"], "Reviewer"),
    "group_review_date": replace_in("x", ["groups", 0, "reviewed_on"], "2026-11-10"),
    "identity_origin": replace_in("x", ["groups", 0, "identities", 0, "origin"], "food"),
    "identity_id": replace_in("x", ["groups", 0, "identities", 0, "id"], "wrong"),
    "identity_index": replace_in("x", ["groups", 0, "identities", 1, "row_index"], 1),
    "identity_missing": remove_in("x", ["groups", 0, "identities", 1]),
    "head_missing": remove_in("x", ["source_head_commits", "food"]),
    "head_fake": replace_in("x", ["source_head_commits", "food"], "invalid"),
    "article_origin": replace_in("x", ["article_origins", "example-a"], "other"),
    "article_removed": remove_in("x", ["article_origins", "example-a"]),
    "candidate_status": replace_in("x", ["candidate_reconciliation_20261104", "status"], "LIVE"),
    "candidate_missing_flag": remove_in("x", ["candidate_reconciliation_20261104", "may_publish"]),
    "candidate_qd": replace_in("x", ["candidate_reconciliation_20261104", "independent_QD_PASS"], True),
    "candidate_safety": replace_in("x", ["candidate_reconciliation_20261104", "safety_approved"], True),
    "candidate_medical": replace_in("x", ["candidate_reconciliation_20261104", "medical_safety_verified"], True),
    "candidate_publish": replace_in("x", ["candidate_reconciliation_20261104", "may_publish"], True),
    "candidate_merge": replace_in("x", ["candidate_reconciliation_20261104", "may_merge"], True),
    "candidate_merchant": replace_in("x", ["candidate_reconciliation_20261104", "merchant_offer_verified"], True),
    "top_approval": replace_in("x", ["publication_authorized"], True),
    "wrong_rows": replace_in("x", ["raw_source_rows"], 7),
    "wrong_exact_urls": replace_in("x", ["unique_source_urls"], 2),
    "wrong_shared": replace_in("x", ["duplicate_url_groups"], 7),
    "wrong_duplicate_id": replace_in("x", ["duplicate_id_groups"], 2),
    "crosswalk_groups_empty": replace_in("x", ["groups"], []),
    "no_candidate": replace_in("x", ["candidate_reconciliation_20261104"], {}),
}


class CrosswalkTests(unittest.TestCase):
    def test_baseline_is_hold_not_pass(self):
        x, sources = fixture()
        result = guard.inspect(x, sources, census=CENSUS)
        self.assertEqual(result["state"], guard.HOLD)
        self.assertFalse(result["independent_qd_pass"])
        self.assertEqual(result["counts"], CENSUS)

    def test_conservative_slash_equivalence(self):
        self.assertEqual(guard.alias(URL), guard.alias(SLASH))
        self.assertNotEqual(guard.alias(URL), guard.alias(URL + "/subpage"))

    def test_query_preserved(self):
        self.assertNotEqual(guard.alias(URL + "?q=one"), guard.alias(URL + "?q=two"))

    def test_fragment_preserved(self):
        self.assertNotEqual(guard.alias(URL + "#a"), guard.alias(URL + "#b"))

    def test_json_duplicate_keys_fail(self):
        with self.assertRaises(ValueError):
            guard.decode(b'{"a":1,"a":2}')

    def test_json_nonfinite_fail(self):
        with self.assertRaises(ValueError):
            guard.decode(b'{"a":NaN}')

    def test_blob_git_identity(self):
        self.assertEqual(guard.blob(b"hello"), "b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0")

    def test_bad_crosswalk_blob_invalid_hard_hold(self):
        result = guard.audit(Path("."), lambda root, rel: b'{"not":"crosswalk"}')
        self.assertEqual(result["state"], guard.INVALID)
        self.assertFalse(result["publication_authorized"])


for name, change in CHANGES.items():
    def adversarial(self, mutation=change):
        x, sources = fixture()
        mutation(x, sources)
        with self.assertRaises((ValueError, KeyError, TypeError, AttributeError)):
            guard.inspect(x, sources, census=CENSUS)
    setattr(CrosswalkTests, "test_adversarial_" + name, adversarial)


if __name__ == "__main__":
    unittest.main()
