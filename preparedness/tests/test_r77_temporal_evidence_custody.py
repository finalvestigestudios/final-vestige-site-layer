"""R77 isolated synthetic/adversarial source-temporal review tests; never writes corpus."""
from __future__ import annotations

from copy import deepcopy
import csv
import importlib.util
import io
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


gate = load(ROOT / "tools" / "r77_temporal_evidence_custody.py",
            "r77_under_test")
prior = load(ROOT / "tests" / "test_r76_source_impact_crosswalk.py",
             "r76_synthetic_for_r77")


def parent():
    return prior.make()


def expected(p):
    c = p["counts"]
    return tuple(c[k] for k in (
        "articles", "tools", "complete_origin_scoped_source_readings",
        "citation_occurrences", "unabridged_DOM_blocks",
        "citation_source_variant_edges_NOT_CLAIM_COUNT",
        "shared_URL_groups_preserved", "reused_source_ID_groups_preserved"))


N = expected(parent())


def make(p=None, *, as_of=gate.SNAPSHOT):
    x = parent() if p is None else p
    return gate.construct(x, expected=N, as_of=as_of)


def reseal(p):
    p["fingerprint_sha256"] = gate.digest({
        k: v for k, v in p.items() if k != "fingerprint_sha256"})
    return p


def reading(p):
    return p["all_244_unabridged_source_readings_NOT_REVIEWED"][0]


def impact(p):
    return p["all_origin_scoped_source_impact_packets_NOT_REVIEWED"][0]


def citation(p):
    return p["every_attached_citation_crosswalk_NOT_SOURCE_SUPPORT_PROOF"][0]


def alter_impact(p, key, value):
    row = impact(p)
    row[key] = value
    row["packet_sha256"] = gate.digest({
        k: v for k, v in row.items() if k != "packet_sha256"})


def alter_citation(p, key, value):
    row = citation(p)
    row[key] = value
    row["packet_sha256"] = gate.digest({
        k: v for k, v in row.items() if k != "packet_sha256"})


def dates(**kwargs):
    return {k: gate.metadata_date(kwargs.get(k)) for k in gate.FIELDS}


class Baseline(unittest.TestCase):
    def test_parent_is_sealed(self):
        gate._r76().sealed(parent())

    def test_r77_report_sealed(self):
        gate.sealed(make())

    def test_stable_deterministic_report(self):
        self.assertEqual(make(), make())

    def test_original_r76_fingerprint_preserved(self):
        p = parent()
        self.assertEqual(make(p)["original_R76_fingerprint_sha256"],
                         p["fingerprint_sha256"])

    def test_unabridged_r76_custody(self):
        p = parent()
        self.assertEqual(make(p)["complete_R76_evidence_UNABRIDGED_NOT_APPROVED"], p)

    def test_no_parent_mutation(self):
        p = parent()
        before = deepcopy(p)
        make(p)
        self.assertEqual(p, before)

    def test_source_identity_conserved(self):
        p = parent()
        rows = make(p)["all_origin_scoped_temporal_review_packets_NOT_APPROVED"]
        src = p["all_origin_scoped_source_impact_packets_NOT_REVIEWED"]
        self.assertEqual([(s["source_origin"], s["source_id"]) for s in rows],
                         [(s["source_origin"], s["source_id"]) for s in src])

    def test_source_date_metadata_verbatim(self):
        p = parent()
        report = make(p)
        by_key = {(s["source_origin"], s["source_id"]): s for s in
                  p["all_244_unabridged_source_readings_NOT_REVIEWED"]}
        for row in report["all_origin_scoped_temporal_review_packets_NOT_APPROVED"]:
            origin = by_key[(row["source_origin"], row["source_id"])]
            original = origin["candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"]
            for k in gate.FIELDS:
                self.assertEqual(row["candidate_metadata_VERBATIM"][k]["raw"],
                                 original.get(k))

    def test_candidate_source_sha_never_changed(self):
        p = parent()
        rows = make(p)["all_origin_scoped_temporal_review_packets_NOT_APPROVED"]
        src = p["all_244_unabridged_source_readings_NOT_REVIEWED"]
        self.assertEqual([s["complete_candidate_reading_sha256"] for s in rows],
                         [s["candidate_reading_sha256"] for s in src])

    def test_historical_reading_has_independent_sha(self):
        p = parent()
        rows = make(p)["all_origin_scoped_temporal_review_packets_NOT_APPROVED"]
        src = p["all_244_unabridged_source_readings_NOT_REVIEWED"]
        self.assertEqual([s["original_reading_sha256"] for s in rows],
                         [s["original_reading_sha256"] for s in src])

    def test_all_citation_edges_conserved(self):
        p = parent()
        rows = make(p)["all_origin_scoped_temporal_review_packets_NOT_APPROVED"]
        self.assertEqual(sum(len(s[
            "all_downstream_citation_variant_edges_NOT_CLAIM_PROOF"]) for s in rows),
            p["counts"]["citation_source_variant_edges_NOT_CLAIM_COUNT"])

    def test_citation_occurrences_not_variant_edges(self):
        c = make()["counts"]
        self.assertEqual(c["citation_occurrences_preserved"],
                         parent()["counts"]["citation_occurrences"])
        self.assertGreaterEqual(c["citation_source_variant_edges_preserved"],
                                c["citation_occurrences_preserved"] -
                                len(parent()["citations_without_DOM_block_UNRESOLVED"]))

    def test_all_dom_blocks_preserved(self):
        self.assertEqual(make()["counts"]["unabridged_DOM_blocks_preserved"],
                         N[4])

    def test_document_counts_preserved(self):
        c = make()["counts"]
        self.assertEqual((c["articles"], c["tools"]), N[:2])

    def test_url_collisions_not_merged(self):
        self.assertEqual(make()["counts"]["shared_URL_groups_preserved"], N[6])

    def test_id_collisions_not_merged(self):
        self.assertEqual(make()["counts"]["reused_ID_groups_preserved"], N[7])

    def test_temporal_disagreement_not_called_error(self):
        for p in make()["shared_URL_temporal_contrast_packets_NOT_EQUIVALENCE"]:
            self.assertEqual(p["human_source_scope_review"], "NOT_REVIEWED")
            self.assertEqual(p["qualified_safety_review"], "NOT_REVIEWED")

    def test_human_checks_never_implied(self):
        for row in make()["all_origin_scoped_temporal_review_packets_NOT_APPROVED"]:
            self.assertFalse(row["human_link_check"])
            self.assertEqual(row["human_claim_support_review"], "NOT_REVIEWED")
            self.assertEqual(row["qualified_safety_review"], "NOT_REVIEWED")

    def test_all_hold_keys_false(self):
        r = make()
        self.assertEqual(r["release_state"], "HOLD")
        self.assertIs(r["publication_clearance"], False)
        for key in gate.HOLD_KEYS:
            self.assertIs(r[key], False)

    def test_no_human_approvals(self):
        c = make()["counts"]
        self.assertEqual((c["human_link_checks"], c["human_claim_support_reviews"],
                          c["qualified_safety_reviews"], c["independent_QD_approvals"]),
                         (0, 0, 0, 0))

    def test_exact_pinned_snapshot(self):
        self.assertEqual(make()["pinned_snapshot_date_NOT_LIVE_FRESHNESS_CHECK"],
                         "2026-11-02")

    def test_report_packet_sha_seals(self):
        r = make()
        for p in r["all_origin_scoped_temporal_review_packets_NOT_APPROVED"]:
            self.assertEqual(p["packet_sha256"], gate.digest({
                k: v for k, v in p.items() if k != "packet_sha256"}))

    def test_collision_packet_sha_seals(self):
        for p in make()["shared_URL_temporal_contrast_packets_NOT_EQUIVALENCE"]:
            self.assertEqual(p["packet_sha256"], gate.digest({
                k: v for k, v in p.items() if k != "packet_sha256"}))

    def test_review_work_order_exact_conservation(self):
        r = make()
        self.assertCountEqual([x["packet_sha256"] for x in
            r["temporal_reviewer_work_order_NOT_A_SAFETY_RISK_SCORE"]],
            [x["packet_sha256"] for x in
            r["all_origin_scoped_temporal_review_packets_NOT_APPROVED"]])

    def test_work_order_deterministic_sort(self):
        r = make()
        rows = r["temporal_reviewer_work_order_NOT_A_SAFETY_RISK_SCORE"]
        self.assertEqual(rows, sorted(rows, key=lambda p: (
            -len(p["literal_temporal_review_cues_NOT_FRESHNESS_OR_SAFETY_VERDICT"]),
            -p["consequential_lexical_citation_edges_NOT_RISK_SCORE"],
            -len(p["distinct_documents_NOT_VALIDATED_CLAIMS"]),
            p["source_origin"], p["source_id"])))

    def test_csv_one_row_per_identity(self):
        r = make()
        rows = list(csv.DictReader(io.StringIO(gate.csv_review_work_order(r))))
        self.assertEqual(len(rows), N[2])
        self.assertTrue(all(x["human_claim_support_review"] == "NOT_REVIEWED"
                            for x in rows))

    def test_csv_is_deterministic(self):
        r = make()
        self.assertEqual(gate.csv_review_work_order(r),
                         gate.csv_review_work_order(r))

    def test_csv_formula_injection_escaped(self):
        r = make()
        r["temporal_reviewer_work_order_NOT_A_SAFETY_RISK_SCORE"][0][
            "source_origin"] = " =cmd|'/C calc'"
        reseal(r)
        rows = list(csv.DictReader(io.StringIO(gate.csv_review_work_order(r))))
        self.assertTrue(any(x["source_origin"].startswith("' =cmd") for x in rows))

    def test_csv_unicode_and_field_integrity(self):
        r = make()
        txt = gate.csv_review_work_order(r)
        rows = list(csv.DictReader(io.StringIO(txt)))
        self.assertTrue(all(len(row) == 13 for row in rows))

    def test_missing_metadata_is_not_approval(self):
        self.assertIn("NO_DOCUMENTED_MACHINE_FETCH_DATE",
                      gate.temporal_signals(dates(), "2026-11-02"))

    def test_bad_snapshot_rejected(self):
        with self.assertRaises(gate.Hold):
            make(as_of="2026-11-31")

    def test_snapshot_must_be_explicit_iso(self):
        with self.assertRaises(gate.Hold):
            make(as_of="today")

    def test_expected_census_pinned(self):
        with self.assertRaises(gate.Hold):
            gate.construct(parent(), expected=N[:-1])

    def test_sealed_report_rejects_false_qd(self):
        r = make()
        r["independent_QD_approval"] = True
        reseal(r)
        with self.assertRaises(gate.Hold):
            gate.sealed(r)

    def test_sealed_report_rejects_mutated_unsealed_packet(self):
        r = make()
        r["counts"]["source_readings_preserved"] = -1
        with self.assertRaises(gate.Hold):
            gate.sealed(r)


class MetadataParsing(unittest.TestCase):
    """Metadata precision is conserved, not interpolated into invented dates."""


_DATE_CASES = [
    ("null", None, "MISSING", None),
    ("year_1800", "1800", "YEAR", None),
    ("year_2026", "2026", "YEAR", None),
    ("year_0000", "0000", "INVALID_CALENDAR_YEAR", None),
    ("month_2026_10", "2026-10", "MONTH", None),
    ("month_2026_13", "2026-13", "INVALID_CALENDAR_MONTH", None),
    ("month_2024_02", "2024-02", "MONTH", None),
    ("day_2026_10_29", "2026-10-29", "DAY", "2026-10-29"),
    ("leap_2024_02_29", "2024-02-29", "DAY", "2024-02-29"),
    ("nonleap_2025_02_29", "2025-02-29", "INVALID_CALENDAR_DATE", None),
    ("bad_day_2026_04_31", "2026-04-31", "INVALID_CALENDAR_DATE", None),
    ("bad_month_2026_00_02", "2026-00-02", "INVALID_CALENDAR_DATE", None),
    ("year_old_0900", "0900", "YEAR", None),
    ("n_d", "n.d.", "NON_ISO_TEXT_REVIEW_ONLY", None),
    ("space_around", " 2026-01-01 ", "NON_ISO_TEXT_REVIEW_ONLY", None),
    ("human_text_date", "October 29, 2026", "NON_ISO_TEXT_REVIEW_ONLY", None),
    ("partial_year_month_text", "2026/10", "NON_ISO_TEXT_REVIEW_ONLY", None),
    ("natural_month", "2026 October", "NON_ISO_TEXT_REVIEW_ONLY", None),
    ("blank", "", "NON_ISO_TEXT_REVIEW_ONLY", None),
    ("relative", "yesterday", "NON_ISO_TEXT_REVIEW_ONLY", None),
    ("unicode", "２０２６", "NON_ISO_TEXT_REVIEW_ONLY", None),
]


def register_date(name, raw, precision, calendar_date):
    def scenario(self):
        p = gate.metadata_date(raw)
        self.assertEqual((p["raw"], p["precision"], p["calendar_date"]),
                         (raw, precision, calendar_date))
    scenario.__name__ = "test_parse_" + name
    setattr(MetadataParsing, scenario.__name__, scenario)


for _name, _raw, _precision, _calendar in _DATE_CASES:
    register_date(_name, _raw, _precision, _calendar)


_BAD_TYPES = [("true", True), ("false", False), ("int", 2026),
              ("float", 2026.1), ("list", []), ("dict", {}),
              ("bytes", b"2026-10-29")]


def register_bad_type(name, raw):
    def scenario(self):
        with self.assertRaises(gate.Hold):
            gate.metadata_date(raw)
    scenario.__name__ = "test_reject_date_" + name
    setattr(MetadataParsing, scenario.__name__, scenario)


for _name, _raw in _BAD_TYPES:
    register_bad_type(_name, _raw)


class ChronologySignals(unittest.TestCase):
    """Cue detection does not decide clinical safety or factual support."""


_CHRONOLOGY_CASES = [
    ("no_fetch_date", {}, "NO_DOCUMENTED_MACHINE_FETCH_DATE"),
    ("no_update_review", {}, "NO_VISIBLE_UPDATE_OR_REVIEW_DATE"),
    ("updated_before_published",
     {"published": "2024-09-16", "updated": "2024-07-18"},
     "UPDATED_DATE_BEFORE_PUBLISHED_DATE_METADATA_REVIEW"),
    ("reviewed_before_published",
     {"published": "2024-09-16", "reviewed": "2024-07-18"},
     "REVIEWED_DATE_BEFORE_PUBLISHED_DATE_METADATA_REVIEW"),
    ("updated_after_fetch",
     {"updated": "2026-11-02", "verified_on": "2026-10-29"},
     "DOCUMENT_UPDATED_AFTER_RECORDED_MACHINE_FETCH"),
    ("reviewed_after_fetch",
     {"reviewed": "2026-11-02", "verified_on": "2026-10-29"},
     "DOCUMENT_REVIEWED_AFTER_RECORDED_MACHINE_FETCH"),
    ("future_published", {"published": "2027-01-01"},
     "PUBLISHED_DATE_AFTER_PINNED_SNAPSHOT"),
    ("future_updated", {"updated": "2027-01-01"},
     "UPDATED_DATE_AFTER_PINNED_SNAPSHOT"),
    ("future_reviewed", {"reviewed": "2027-01-01"},
     "REVIEWED_DATE_AFTER_PINNED_SNAPSHOT"),
    ("future_verified", {"verified_on": "2027-01-01"},
     "VERIFIED_ON_DATE_AFTER_PINNED_SNAPSHOT"),
    ("invalid_published", {"published": "2026-99-99"},
     "UNPARSEABLE_PUBLISHED_DATE_REVIEW"),
    ("invalid_updated", {"updated": "2026-02-30"},
     "UNPARSEABLE_UPDATED_DATE_REVIEW"),
    ("invalid_reviewed", {"reviewed": "2026-13"},
     "UNPARSEABLE_REVIEWED_DATE_REVIEW"),
    ("text_verified", {"verified_on": "last week"},
     "UNPARSEABLE_VERIFIED_ON_DATE_REVIEW"),
]


def register_chronology(name, row, flag):
    def scenario(self):
        self.assertIn(flag, gate.temporal_signals(dates(**row), "2026-11-02"))
    scenario.__name__ = "test_flags_" + name
    setattr(ChronologySignals, scenario.__name__, scenario)


for _name, _row, _flag in _CHRONOLOGY_CASES:
    register_chronology(_name, _row, _flag)


class Adversarial(unittest.TestCase):
    """Mutation attempts are re-fingerprinted to avoid seal-only false positives."""


_MUTATIONS = [
    ("wrong_schema", lambda p: p.__setitem__("schema", "other")),
    ("not_hold", lambda p: p.__setitem__("release_state", "PASS")),
    ("not_machine_only", lambda p: p.__setitem__("machine_only", False)),
    ("approved", lambda p: p.__setitem__("may_publish", True)),
    ("fake_qd", lambda p: p.__setitem__("independent_QD_approval", True)),
    ("fake_safety", lambda p: p.__setitem__("qualified_safety_clearance", True)),
    ("fake_links_checked", lambda p: p.__setitem__("human_source_links_verified", True)),
    ("wrong_article_count", lambda p: p["counts"].__setitem__("articles", 99)),
    ("wrong_tool_count", lambda p: p["counts"].__setitem__("tools", 99)),
    ("wrong_source_count", lambda p: p["counts"].__setitem__("complete_origin_scoped_source_readings", 1)),
    ("wrong_citation_count", lambda p: p["counts"].__setitem__("citation_occurrences", 1)),
    ("wrong_dom_count", lambda p: p["counts"].__setitem__("unabridged_DOM_blocks", 1)),
    ("wrong_variant_count", lambda p: p["counts"].__setitem__("citation_source_variant_edges_NOT_CLAIM_COUNT", 1)),
    ("wrong_collision_count", lambda p: p["counts"].__setitem__("shared_URL_groups_preserved", 99)),
    ("wrong_id_count", lambda p: p["counts"].__setitem__("reused_source_ID_groups_preserved", 99)),
    ("fake_human_claim", lambda p: p["counts"].__setitem__("human_claim_support_reviews", 1)),
    ("fake_human_safety", lambda p: p["counts"].__setitem__("qualified_safety_reviews", 1)),
    ("fake_human_qd", lambda p: p["counts"].__setitem__("independent_QD_approvals", 1)),
    ("drop_source_record", lambda p: p["all_244_unabridged_source_readings_NOT_REVIEWED"].pop()),
    ("drop_source_packet", lambda p: p["all_origin_scoped_source_impact_packets_NOT_REVIEWED"].pop()),
    ("drop_citation", lambda p: p["every_attached_citation_crosswalk_NOT_SOURCE_SUPPORT_PROOF"].pop()),
    ("drop_block", lambda p: p["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"].pop()),
    ("drop_doc", lambda p: p["all_document_block_orders_NOT_REVIEWED"].pop()),
    ("source_origin_modified", lambda p: reading(p).__setitem__("source_origin", "bogus-origin")),
    ("source_id_modified", lambda p: reading(p).__setitem__("source_id", "bogus-id")),
    ("source_url_modified", lambda p: reading(p).__setitem__("exact_URL_NO_ALIAS", "https://bogus.invalid")),
    ("source_reading_hash_modified", lambda p: reading(p).__setitem__("candidate_reading_sha256", "0" * 64)),
    ("historical_reading_hash_modified", lambda p: reading(p).__setitem__("original_reading_sha256", "0" * 64)),
    ("source_human_review_modified", lambda p: reading(p).__setitem__("human_source_and_claim_review", "APPROVED")),
    ("source_safety_modified", lambda p: reading(p).__setitem__("qualified_safety_review", "APPROVED")),
    ("source_date_changed", lambda p: reading(p)["candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"].__setitem__("updated", "2027-02-01")),
    ("source_human_link_modified", lambda p: reading(p)["candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"].__setitem__("human_link_check", True)),
    ("source_date_type_bool", lambda p: reading(p)["candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"].__setitem__("verified_on", True)),
    ("impact_url_substituted", lambda p: alter_impact(p, "exact_URL_NOT_CANONICALIZED", "https://bogus.invalid")),
    ("impact_sha_substituted", lambda p: alter_impact(p, "complete_source_reading_sha256", "0" * 64)),
    ("impact_false_review", lambda p: alter_impact(p, "human_source_and_claim_review", "PASS")),
    ("impact_false_safety", lambda p: alter_impact(p, "qualified_safety_review", "PASS")),
    ("impact_edges_erased", lambda p: alter_impact(p, "citation_variant_edges_NOT_UNIQUE_CLAIMS", [])),
    ("impact_count_tamper", lambda p: alter_impact(p, "all_citation_variant_edges_NOT_VERDICT", 99)),
    ("citation_ordinal_mutated", lambda p: alter_citation(p, "citation_ordinal", 100)),
    ("citation_id_mutated", lambda p: alter_citation(p, "raw_source_id", "bogus-id")),
    ("citation_block_mutated", lambda p: alter_citation(p, "block_id", "bogus-block")),
    ("citation_false_review", lambda p: alter_citation(p, "human_claim_support_review", "PASS")),
    ("citation_variants_removed", lambda p: alter_citation(p, "source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT", [])),
    ("citation_variant_url_changed", lambda p: alter_citation(p, "source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT", [{
        **citation(p)["source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT"][0],
        "exact_URL_NOT_CANONICALIZED": "https://bogus.invalid"}])),
    ("citation_variant_sha_changed", lambda p: alter_citation(p, "source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT", [{
        **citation(p)["source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT"][0],
        "complete_source_reading_sha256": "0" * 64}])),
    ("duplicate_source_record", lambda p: p["all_244_unabridged_source_readings_NOT_REVIEWED"].append(
        deepcopy(reading(p)))),
    ("duplicate_citation_occurrence", lambda p: p["every_attached_citation_crosswalk_NOT_SOURCE_SUPPORT_PROOF"].append(
        deepcopy(citation(p)))),
]


def register_mutation(name, mutate):
    def scenario(self):
        p = parent()
        mutate(p)
        reseal(p)
        with self.assertRaises((gate.Hold, ValueError, TypeError,
                                KeyError, AttributeError)):
            make(p)
    scenario.__name__ = "test_reject_" + name
    setattr(Adversarial, scenario.__name__, scenario)


for _name, _mutation in _MUTATIONS:
    register_mutation(_name, _mutation)


if __name__ == "__main__":
    unittest.main()
