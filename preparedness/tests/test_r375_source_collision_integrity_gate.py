"""Adversarial and deterministic synthetic fixtures; NOT authentic native source QA."""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "tools" / "r375_source_collision_integrity_gate.py"
spec = importlib.util.spec_from_file_location("r375_gate", TOOL)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
BRANCHES = ["claude/prep-start-a", "claude/prep-food-b", "claude/prep-health-c",
            "claude/prep-hist-field-d", "claude/prep-hist-food-e", "claude/prep-hist-home-f",
            "claude/prep-shelter-g", "claude/prep-shelter-h", "claude/prep-shelter-i"]
FRAGMENTS = ["start", "food", "health", "hist-field", "hist-food", "hist-home", "shelter", "shelter", "shelter"]


def make_fixture():
    blobs = {b: f"{i + 1:040x}" for i, b in enumerate(BRANCHES)}
    objects = {"schema_version": 1, "repository": gate.REPO, "release_state": "DRAFT_HARD_HOLD",
               "branch_pins": [{"branch": b, "sha": f"{i + 30:040x}"} for i, b in enumerate(BRANCHES)],
               "article_count": 35, "conflict_count": 9,
               "objects": [{"path": f"preparedness/sources/fragments/{f}.json",
                            "selected_sha": None, "variants": [{"branch": b, "sha": blobs[b]}]}
                           for b, f in zip(BRANCHES, FRAGMENTS)]}
    groups = []
    for i in range(203):
        count = 3 if i < 31 else (2 if i < 46 else 1)
        variants = []
        for j in range(count):
            k = (i + j) % 9
            branch = BRANCHES[k]
            url = f"https://example.org/report-{i//2 if i < 34 else i+500}"
            variants.append({"id": f"id-{i}", "branch": branch,
                             "fragment": f"preparedness/sources/fragments/{FRAGMENTS[k]}.json",
                             "source_blob": blobs[branch], "url": url,
                             "publisher": "Official source", "kind": "regulator",
                             "verified_on": "2026-10-29", "human_link_check": False,
                             "supports": f"Exact original reading scope {i}" + (" alt" if i < 5 and j == 1 else ""),
                             "notes": "Original reading limitation"})
        groups.append({"id": f"id-{i}", "requires_human_review": count > 1, "variants": variants})
    docket = [{"url": f"https://example.org/report-{i}", "ids": [f"id-{2*i}", f"id-{2*i+1}"],
               "review_required": True} for i in range(17)]
    source = {"schema_version": 1, "repository": gate.REPO, "release_state": "DRAFT_HARD_HOLD",
              "original_fragment_count": 7, "record_occurrences": 280, "distinct_source_ids": 203,
              "source_id_variants": groups, "shared_url_docket": docket}
    return objects, source


class TestR375(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = make_fixture()
        cls.original_digest = gate.check_crosswalk(*cls.base)["source_records_digest"]

    def fixture(self):
        return copy.deepcopy(self.base)

    def test_01_synthetic_inventory_custody_holds_release(self):
        result = gate.check_crosswalk(*self.fixture())
        self.assertEqual(result["status"], "SOURCE_REVIEW_HARD_HOLD", result["issues"])
        self.assertEqual(result["counts"], gate.PINNED)
        self.assertFalse(result["publication_approved"])
        self.assertFalse(result["qualified_safety_approved"])

    def test_02_semantic_divergence_docket(self):
        r = gate.check_crosswalk(*self.fixture())
        self.assertEqual([g["id"] for g in r["divergent_source_review_queue"]], [f"id-{i}" for i in range(5)])
        self.assertEqual(len(r["shared_url_review_queue"]), 17)
        self.assertEqual(r["human_link_checked"], 0)

    def test_03_order_independent_source_custody(self):
        o, s = self.fixture()
        a = gate.check_crosswalk(o, s)
        s["source_id_variants"].reverse()
        for g in s["source_id_variants"]:
            g["variants"].reverse()
        b = gate.check_crosswalk(o, s)
        self.assertEqual(a["source_records_digest"], b["source_records_digest"])
        self.assertEqual(a["divergent_source_review_queue"], b["divergent_source_review_queue"])

    def test_04_digest_sensitivity_to_scope(self):
        o, s = self.fixture()
        original = gate.check_crosswalk(o, s)["source_records_digest"]
        s["source_id_variants"][61]["variants"][0]["supports"] += " changed"
        self.assertNotEqual(original, gate.check_crosswalk(o, s)["source_records_digest"])

    def test_05_malformed_manifest_types_fail_closed(self):
        for a, b in (([], {}), ({}, []), (None, None)):
            self.assertEqual(gate.check_crosswalk(a, b)["status"], "INVALID_HARD_HOLD")

    def test_06_missing_native_files_exit_two(self):
        with tempfile.TemporaryDirectory() as td:
            x = subprocess.run([sys.executable, str(TOOL), str(Path(td)/"missing1.json"),
                                str(Path(td)/"missing2.json")], capture_output=True, text=True)
            self.assertEqual(x.returncode, 2)
            self.assertEqual(json.loads(x.stdout)["status"], "INVALID_HARD_HOLD")

    def test_07_correct_synthetic_cli_never_exits_success(self):
        with tempfile.TemporaryDirectory() as td:
            a, b = self.fixture()
            p, q = Path(td)/"a.json", Path(td)/"b.json"
            p.write_text(json.dumps(a)); q.write_text(json.dumps(b))
            x = subprocess.run([sys.executable, str(TOOL), str(p), str(q)], capture_output=True, text=True)
            self.assertEqual(x.returncode, 2)
            self.assertEqual(json.loads(x.stdout)["status"], "INVALID_HARD_HOLD")  # synthetic fixture cannot impersonate pinned authentic Git blobs


# Each generated named test is separately counted by unittest, and each checks
# a different adversarial mutation of the source and object inventories.
def mutations():
    v = []
    for key in ("repository", "release_state", "schema_version"):
        for root in (0, 1):
            def edit(x, y, k=key, n=root):
                item = (x, y)[n]
                item[k] = "WRONG" if k != "schema_version" else 5
            v.append((f"identity_{root}_{key}", edit))
    for k in ("approval", "approved", "publish", "published", "qd_pass", "release_ready", "live"):
        def edit(x, y, key=k): y[key] = True
        v.append((f"forged_approval_{k}", edit))
    for idx in (0, 1, 2, 3, 4, 10, 60, 202):
        def edit(x, y, i=idx):
            y["source_id_variants"][i]["variants"][0]["source_blob"] = "a" * 40
        v.append((f"wrong_source_blob_{idx}", edit))
    for value in ("http://host.invalid/x", "javascript:alert(1)", "https:///missing-host",
                  "https://user:pass@host.invalid/x", "https://host.invalid/x#secret", "file:///etc/passwd"):
        def edit(x, y, url=value): y["source_id_variants"][50]["variants"][0]["url"] = url
        v.append((f"unsafe_url_{len(v)}", edit))
    for value in ("", " ", None):
        def edit(x, y, s=value): y["source_id_variants"][50]["variants"][0]["supports"] = s
        v.append((f"lost_reading_scope_{len(v)}", edit))
    for value in (True, None, "false", 1):
        def edit(x, y, s=value): y["source_id_variants"][70]["variants"][0]["human_link_check"] = s
        v.append((f"unverified_link_flag_{len(v)}", edit))
    for name, edit in [
        ("no_object_branch", lambda x,y: x["branch_pins"].pop()),
        ("selected_source_version", lambda x,y: x["objects"][0].update(selected_sha="a"*40)),
        ("wrong_article_count", lambda x,y: x.update(article_count=34)),
        ("wrong_conflict_count", lambda x,y: x.update(conflict_count=8)),
        ("no_original_fragments", lambda x,y: y.update(original_fragment_count=6)),
        ("source_total_tampering", lambda x,y: y.update(record_occurrences=279)),
        ("distinct_id_tampering", lambda x,y: y.update(distinct_source_ids=202)),
        ("missing_source_group", lambda x,y: y["source_id_variants"].pop()),
        ("extra_source_group", lambda x,y: y["source_id_variants"].append(copy.deepcopy(y["source_id_variants"][30]))),
        ("source_id_cross_assignment", lambda x,y: y["source_id_variants"][0]["variants"][0].update(id="another-id")),
        ("missing_variant", lambda x,y: y["source_id_variants"][1]["variants"].pop()),
        ("duplicated_variant", lambda x,y: y["source_id_variants"][1]["variants"].append(copy.deepcopy(y["source_id_variants"][1]["variants"][0]))),
        ("source_branch_unknown", lambda x,y: y["source_id_variants"][1]["variants"][0].update(branch="claude/rogue")),
        ("fragment_outside_scope", lambda x,y: y["source_id_variants"][1]["variants"][0].update(fragment="../../oops.json")),
        ("shared_url_docket_deleted", lambda x,y: y["shared_url_docket"].pop()),
        ("shared_url_docket_renamed", lambda x,y: y["shared_url_docket"][0].update(url="https://wrong.example")),
        ("shared_url_review_unset", lambda x,y: y["shared_url_docket"][0].update(review_required=False)),
        ("duplicate_object_entry", lambda x,y: x["objects"].append(copy.deepcopy(x["objects"][0]))),
        ("object_sha_tampered", lambda x,y: x["objects"][0]["variants"][0].update(sha="f"*40)),
        ("original_source_notes_changed", lambda x,y: y["source_id_variants"][2]["variants"][0].update(notes="Different source reading evidence")),
        ("original_source_publisher_changed", lambda x,y: y["source_id_variants"][2]["variants"][0].update(publisher="Not the same publisher")),
    ]: v.append((name, edit))
    return v


def make_test(name, mutate):
    def test(self):
        a, b = self.fixture()
        mutate(a, b)
        result = gate.check_crosswalk(a, b, expected_digest=self.original_digest)
        self.assertEqual(result["status"], "INVALID_HARD_HOLD", (name, result["issues"]))
        self.assertFalse(result["publication_approved"])
        self.assertFalse(result["qualified_safety_approved"])
    test.__name__ = "test_guard_" + name
    return test


for _name, _edit in mutations():
    setattr(TestR375, "test_guard_" + _name, make_test(_name, _edit))


if __name__ == "__main__":
    unittest.main()
