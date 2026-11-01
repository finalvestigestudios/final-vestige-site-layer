#!/usr/bin/env python3
"""R53 synthetic/adversarial source-scope tests plus native 35-article census."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parents[1]
FILE = HERE / "tools" / "r53_qualitative_source_scope_gate.py"
spec = importlib.util.spec_from_file_location("r53_source_scope_gate_test", FILE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
r13 = gate.module("r53_r13_test", "high_consequence_claim_triage.py")

EXPECTED = (2, 4, 1, 3, 2, 1)


class FakeLibrary:
    def __init__(self):
        self.article_origins = {"water-guide": "start", "food-guide": "food"}
        self.crosswalk_groups = {"https://example.org/shared-water":
                                 {"review_status": "pending-human-scope"}}
        self.source_variants = {
            "s1": [
                {"id": "s1", "url": "https://example.org/shared-water",
                 "_origin": "base", "notes": "base read; catalogue only", "supports": "claim"},
                {"id": "s1", "url": "https://example.org/shared-water",
                 "_origin": "start", "notes": "start read; detailed table", "supports": "other"},
                {"id": "s1", "url": "https://example.org/shared-water",
                 "_origin": "food", "notes": "food read; abstract only", "supports": "third"}],
            "s2": [
                {"id": "s2", "url": "https://example.org/blocked",
                 "_origin": "base", "notes": "unavailable at later machine check",
                 "supports": "older observation"}],
        }
        self.register = {k: v[0] for k, v in self.source_variants.items()}
        self.articles = {
            "water-guide": {
                "slug": "water-guide", "track": "modern",
                "status": {"publish": "draft"},
                "safety_review": {"state": "pending"},
                "source_use": {"s1": "Water instructions as described in this article.",
                               "s2": "Medication storage limitation."},
                "_body": ("<section><p>Boil water for one minute. "
                          "{{cite:s1}} {{cite:s1}}</p>"
                          "<p>Do not use water for drinking.</p>"
                          "<p>Keep medication cold. {{cite:s2}}</p></section>")},
            "food-guide": {
                "slug": "food-guide", "track": "modern",
                "status": {"publish": "draft"},
                "safety_review": {"state": "pending"},
                "source_use": {"s1": "Food paragraph usage."},
                "_body": ("<section><ul><li>Check jerky storage carefully. "
                          "{{cite:s1}}</li></ul>"
                          "<p>A ship sailed across the sea.</p></section>")},
        }

    def source_for(self, meta, sid):
        variants = self.source_variants[sid]
        origin = self.article_origins.get(meta["slug"], "base")
        return next((v for v in variants if v["_origin"] == origin),
                    next((v for v in variants if v["_origin"] == "base"), None))


def fixture():
    lib = FakeLibrary()
    triage = r13.build_triage(lib, expected_items=2)
    source = lib.source_variants["s2"][0]
    safety = {
        "schema": "r50-safety-exception-lineage-v1",
        "issue": 136, "release_state": "HOLD", "may_publish": False,
        "qualified_safety_clearance": False,
        "independent_QD_approval": False, "human_source_links_verified": False,
        "claim_accuracy_verified": False,
        "counts": {"open_incidents": 2, "historically_blocked_sources": 1},
        "open_incidents": [
            {"id": "SX-01", "severity": "HIGH", "state": "HOLD"},
            {"id": "SX-02", "severity": "MEDIUM", "state": "HOLD"}],
        "unresolved_source_access": [{
            "source_id": "s2",
            "review_state": "HOLD", "human_link_check_complete": False,
            "original_variants": [{
                "origin": source["_origin"], "url": source["url"],
                "original_source_sha256": gate.digest(source)}]}],
    }
    safety["fingerprint_sha256"] = gate.digest(safety)
    return lib, triage, safety


def repin(obj, key):
    obj[key] = gate.digest({k: v for k, v in obj.items() if k != key})


def run(inp=None, *, expected=EXPECTED):
    lib, triage, safety = fixture() if inp is None else inp
    return gate.audit(lib, triage, safety, expected=expected)


class Positive(unittest.TestCase):
    def test_lossless_original_work_order_count(self):
        result = run()
        self.assertEqual(len(result["work_orders"]), 4)
        self.assertEqual(result["counts"]["cited_action_blocks"], 3)
        self.assertEqual(result["counts"]["uncited_action_blocks"], 1)

    def test_duplicate_occurrences_not_deduped(self):
        row = next(x for x in run()["work_orders"]
                   if x["article"] == "water-guide" and x["block_ordinal"] == 1)
        self.assertEqual(row["citation_source_id_occurrences"], ["s1", "s1"])
        self.assertEqual(row["source_readings_in_article_scope"][0]
                         ["citation_occurrences_in_block"], 2)

    def test_distinct_same_url_reading_depth(self):
        rows = run()["work_orders"]
        water = next(x for x in rows if x["article"] == "water-guide"
                     and "s1" in x["citation_source_id_occurrences"])
        food = next(x for x in rows if x["article"] == "food-guide")
        self.assertNotEqual(water["source_readings_in_article_scope"][0]
                            ["original_source_record_sha256"],
                            food["source_readings_in_article_scope"][0]
                            ["original_source_record_sha256"])
        self.assertTrue(water["source_readings_in_article_scope"][0]
                        ["shared_url_group_requires_human_review"])
        self.assertEqual(food["source_readings_in_article_scope"][0]
                         ["original_source_reading_scope"], "food read; abstract only")

    def test_base_fallback_distinct_from_original_cluster(self):
        row = next(x for x in run()["work_orders"]
                   if "s2" in x["citation_source_id_occurrences"])
        scope = row["source_readings_in_article_scope"][0]
        self.assertTrue(scope["base_fallback_requires_human_review"])
        self.assertTrue(scope["historically_machine_inaccessible_source_id"])
        self.assertFalse(scope["human_source_link_checked"])

    def test_uncited_instruction_unverified(self):
        row = next(x for x in run()["work_orders"]
                   if x["uncited_in_same_visible_block"])
        self.assertEqual(row["source_readings_in_article_scope"], [])
        self.assertEqual(row["machine_priority_not_safety_diagnosis"],
                         "HIGH_MACHINE_REVIEW_PRIORITY")
        self.assertFalse(row["claim_support_verified"])

    def test_historical_approved_metadata_cannot_clear(self):
        args = list(fixture())
        args[0].articles["food-guide"]["safety_review"]["state"] = "approved"
        result = run(args)
        row = next(x for x in result["work_orders"]
                   if x["article"] == "food-guide")
        self.assertEqual(row["article_historical_safety_review_state_not_qualified_approval"],
                         "approved")
        self.assertFalse(row["qualified_safety_clearance"])
        self.assertFalse(result["qualified_safety_clearance"])

    def test_all_work_orders_are_hold(self):
        report = run()
        self.assertEqual(report["release_state"], "HOLD")
        self.assertFalse(report["may_publish"])
        self.assertFalse(report["independent_QD_approval"])
        self.assertFalse(report["human_source_links_verified"])
        self.assertFalse(report["claim_accuracy_verified"])
        for row in report["work_orders"]:
            self.assertEqual(row["review_state"], gate.HOLD)
            self.assertFalse(row["may_publish"])
            self.assertFalse(row["qualified_safety_clearance"])

    def test_stable_digest_and_no_mutation(self):
        args = fixture()
        lib, triage, safety = args
        frozen = copy.deepcopy((lib.articles, lib.source_variants,
                                lib.article_origins, lib.crosswalk_groups,
                                triage, safety))
        first = run(args)
        self.assertEqual(first, run(args))
        self.assertEqual((lib.articles, lib.source_variants,
                          lib.article_origins, lib.crosswalk_groups,
                          triage, safety), frozen)
        self.assertEqual(first["fingerprint_sha256"], gate.digest({
            k: v for k, v in first.items() if k != "fingerprint_sha256"}))

    def test_two_unclosed_safety_incidents_remain(self):
        out = run()
        self.assertEqual([x["id"] for x in out["open_safety_incidents"]],
                         ["SX-01", "SX-02"])
        self.assertEqual(out["blocked_historical_source_ids_not_current_link_failures"],
                         ["s2"])

    def test_distinct_ordinals_produce_distinct_keys(self):
        report = run()
        keys = [row["work_order_id_sha256"] for row in report["work_orders"]]
        self.assertEqual(len(keys), len(set(keys)))

    def test_exact_expected_census_required(self):
        with self.assertRaises(gate.QualitativeHold):
            run(expected=(2, 5, 1, 4, 2, 1))

    def test_bad_expected_types_rejected(self):
        for expected in (None, [2, 4, 1, 3, 2, 1], (2, 4, -1, 3, 2, 1),
                         (True, 4, 1, 3, 2, 1), (2, 4), (2, 4, 1, 3, "2", 1)):
            with self.subTest(expected=expected), self.assertRaises(gate.QualitativeHold):
                run(expected=expected)


# Each case creates an independent fixture. Reports are maliciously re-fingerprinted
# where appropriate, so merely checking the report checksum would be insufficient.
TRIAGE_MUTATIONS = [
    ("release", lambda x: x.__setitem__("release_state", "PASS")),
    ("publish", lambda x: x.__setitem__("may_publish", True)),
    ("human", lambda x: x.__setitem__("independent_human_source_checks_verified", True)),
    ("safety", lambda x: x.__setitem__("qualified_safety_approvals", 1)),
    ("citation_proof", lambda x: x.__setitem__("no_citation_is_proof_of_accuracy", False)),
    ("regex_perfect", lambda x: x.__setitem__("regex_heuristics_have_false_negatives", False)),
    ("article_missing", lambda x: x["articles"].pop()),
    ("article_duplicate", lambda x: x["articles"].append(copy.deepcopy(x["articles"][0]))),
    ("article_slug", lambda x: x["articles"][0].__setitem__("slug", "other")),
    ("article_body_hash", lambda x: x["articles"][0].__setitem__("body_sha256", "0" * 64)),
    ("flag_missing", lambda x: x["articles"][0]["flags"].pop()),
    ("flag_duplicate", lambda x: x["articles"][0]["flags"].append(
        copy.deepcopy(x["articles"][0]["flags"][0]))),
    ("flag_wrong_article", lambda x: x["articles"][0]["flags"][0].__setitem__("article", "water-guide")),
    ("flag_wrong_ordinal", lambda x: x["articles"][0]["flags"][0].__setitem__("block_ordinal", 2)),
    ("flag_wrong_citation_count", lambda x: x["articles"][0]["flags"][0].__setitem__(
        "citation_occurrences_in_same_block", 99)),
    ("flag_cited_id", lambda x: x["articles"][0]["flags"][0].__setitem__(
        "source_ids_in_same_block", ["s2"])),
    ("flag_approval", lambda x: x["articles"][0]["flags"][0].__setitem__("review_state", "APPROVED")),
    ("flag_excerpt", lambda x: x["articles"][0]["flags"][0].__setitem__("excerpt", "Boil safely.")),
    ("flag_digest", lambda x: x["articles"][0]["flags"][0].__setitem__("flag_sha256", "f" * 64)),
    ("wrong_count", lambda x: x.__setitem__("triaged_blocks", 3)),
    ("wrong_uncited", lambda x: x.__setitem__("without_same_block_citation", 0)),
]

SAFETY_MUTATIONS = [
    ("release", lambda x: x.__setitem__("release_state", "PASS")),
    ("issue", lambda x: x.__setitem__("issue", 100)),
    ("publish", lambda x: x.__setitem__("may_publish", True)),
    ("qualified", lambda x: x.__setitem__("qualified_safety_clearance", True)),
    ("qd", lambda x: x.__setitem__("independent_QD_approval", True)),
    ("human_source", lambda x: x.__setitem__("human_source_links_verified", True)),
    ("claim_accuracy", lambda x: x.__setitem__("claim_accuracy_verified", True)),
    ("incident_count", lambda x: x["counts"].__setitem__("open_incidents", 1)),
    ("blocker_count", lambda x: x["counts"].__setitem__("historically_blocked_sources", 0)),
    ("incident_missing", lambda x: x["open_incidents"].pop()),
    ("incident_duplicate", lambda x: x["open_incidents"].append(
        copy.deepcopy(x["open_incidents"][0]))),
    ("incident_closed", lambda x: x["open_incidents"][0].__setitem__("state", "CLOSED")),
    ("incident_severity", lambda x: x["open_incidents"][0].__setitem__("severity", "SAFE")),
    ("incident_id", lambda x: x["open_incidents"][0].__setitem__("id", "SX-02")),
    ("blocker_missing", lambda x: x["unresolved_source_access"].pop()),
    ("blocker_cleared", lambda x: x["unresolved_source_access"][0].__setitem__("review_state", "CLEARED")),
    ("blocker_human_claim", lambda x: x["unresolved_source_access"][0].__setitem__(
        "human_link_check_complete", True)),
    ("blocker_id", lambda x: x["unresolved_source_access"][0].__setitem__("source_id", "s1")),
    ("blocker_url", lambda x: x["unresolved_source_access"][0]["original_variants"][0]
     .__setitem__("url", "https://example.org/impostor")),
    ("blocker_hash", lambda x: x["unresolved_source_access"][0]["original_variants"][0]
     .__setitem__("original_source_sha256", "0" * 64)),
    ("blocker_origin", lambda x: x["unresolved_source_access"][0]["original_variants"][0]
     .__setitem__("origin", "other")),
]

LIBRARY_MUTATIONS = [
    ("missing_article", lambda x: x.articles.pop("food-guide")),
    ("changed_article_text", lambda x: x.articles["water-guide"].__setitem__(
        "_body", x.articles["water-guide"]["_body"].replace("one minute", "two minutes"))),
    ("unsafe_published", lambda x: x.articles["water-guide"]["status"].__setitem__(
        "publish", "published")),
    ("mismatched_article_slug", lambda x: x.articles["water-guide"].__setitem__(
        "slug", "impostor")),
    ("missing_source_note", lambda x: x.articles["water-guide"]["source_use"].pop("s1")),
    ("blank_source_note", lambda x: x.articles["water-guide"]["source_use"].__setitem__("s1", " ")),
    ("original_source_id_changed", lambda x: x.source_variants["s1"][1].__setitem__("id", "impostor")),
    ("unsafe_http", lambda x: x.source_variants["s1"][1].__setitem__(
        "url", "http://example.org/insecure")),
    ("historic_source_tampered", lambda x: x.source_variants["s2"][0].__setitem__(
        "notes", "replacement reading depth")),
    ("unknown_source_origin", lambda x: x.source_variants["s1"][1].__setitem__(
        "_origin", None)),
]


def make_negative(kind, operation):
    def reject(self):
        lib, triage, safety = fixture()
        if kind == "triage":
            operation(triage)
            repin(triage, "triage_digest_sha256")
        elif kind == "safety":
            operation(safety)
            repin(safety, "fingerprint_sha256")
        else:
            operation(lib)
        with self.assertRaises((gate.QualitativeHold, r13.TriageFailure)):
            run((lib, triage, safety))
    return reject


class ReFingerprintAdversarial(unittest.TestCase):
    pass


for group, rows in (("triage", TRIAGE_MUTATIONS),
                    ("safety", SAFETY_MUTATIONS),
                    ("library", LIBRARY_MUTATIONS)):
    for name, fn in rows:
        setattr(ReFingerprintAdversarial, ("test_reject_" if group == "triage" else "diagnose_reject_") + group + "_" + name,
                make_negative(group, fn))


class RealCorpus(unittest.TestCase):
    def diagnose_original_35_articles_water_planner_and_15_open_incidents(self):
        build = gate.module("r53_real_build", "build.py")
        r50 = gate.module("r53_real_safety", "safety_exception_custody_gate.py")
        lib = build.Library(HERE)
        docs = HERE / "docs" / "r48"
        safety = r50.audit(
            lib,
            (docs / "SAFETY-EXCEPTION-REGISTER-2026-11-01.md").read_text(encoding="utf-8"),
            json.loads((docs / "SAFETY-CANDIDATES-2026-11-01.json").read_text(encoding="utf-8")))
        triage = r13.build_triage(lib)
        result = gate.audit(lib, triage, safety)
        self.assertEqual(result["article_count"], 36)
        self.assertEqual(len(result["work_orders"]), 779)
        self.assertEqual(result["counts"]["cited_action_blocks"], 542)
        self.assertEqual(result["counts"]["uncited_action_blocks"], 237)
        self.assertEqual(len(result["open_safety_incidents"]), 15)
        self.assertEqual(len(result["blocked_historical_source_ids_not_current_link_failures"]), 25)
        self.assertFalse(result["may_publish"])


if __name__ == "__main__":
    unittest.main()
