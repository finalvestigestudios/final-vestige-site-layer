"""R64 isolated synthetic/adversarial review-coverage tests; never publish."""
from __future__ import annotations

import copy
import csv
import importlib.util
import io
from pathlib import Path
import unittest
from unittest import mock


MODULE = Path(__file__).resolve().parents[1] / "tools" / "r64_article_source_dependency_review.py"
SPEC = importlib.util.spec_from_file_location("r64_synthetic_under_test", MODULE)
assert SPEC and SPEC.loader
r64 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r64)


def fixture():
    def reading(cluster, sid, digest):
        rec = {"id": sid, "url": "https://example.invalid/" + sid,
               "reading_note": "Unverified preserved reading depth " + sid}
        return {"record_sha256": digest,
                "unabridged_contributor_reading_NOT_HUMAN_CHECKED": rec,
                "same_exact_url_distinct_identity_NOT_ALIAS": False,
                "candidate_citation_occurrences_NOT_SUPPORT_PROOF": [],
                "article_source_use_notes_UNABRIDGED_NOT_SUPPORT_PROOF": []}

    source_rows = []
    for sid, cluster, hashchar in (("alpha", "food", "a"), ("beta", "health", "b")):
        source_rows.append({
            "cluster": cluster, "source_id": sid,
            "work_order_sha256": hashchar * 64,
            "change_kind": "UNCHANGED_NOT_REVERIFIED",
            "human_source_review": "NOT_REVIEWED",
            "qualified_claim_safety_review": "NOT_REVIEWED",
            "versions": {"frozen": reading(cluster, sid, hashchar * 64),
                         "observed": reading(cluster, sid, hashchar * 64)},
        })

    def article(n):
        def version():
            return {
                "body_sha256": "c" * 64, "metadata_sha256": "d" * 64,
                "status_as_recorded_NOT_REVIEWED": {"publish": "draft"},
                "safety_review_as_recorded_NOT_CLEARED": {"state": "pending"},
                "full_source_use_mapping_UNABRIDGED": {"alpha": "Full original note"},
                "citation_occurrences_in_original_order": [{
                    "source_id": "alpha", "offset_codepoints": 5,
                    "unabridged_local_context": "Context of cited claim",
                }],
            }
        return {"cluster": "food", "slug": f"synthetic-article-{n:02d}",
                "review_state": "NOT_REVIEWED",
                "versions": {"frozen": version(), "observed": version()}}

    lineage = {
        "fingerprint_sha256": "1" * 64,
        "existing_R14_exception_remains_open": True,
        "counts": {"old_citation_occurrences": 29,
                   "observed_citation_occurrences_UNVERIFIED": 29},
        "per_article_citation_and_context_lineage_NOT_REVIEWED":
            [article(n) for n in range(1, 30)],
    }
    docket = {"fingerprint_sha256": "2" * 64}
    sources = {"fingerprint_sha256": "3" * 64,
               "source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS": source_rows}
    return lineage, docket, sources


def first(result):
    return result["article_source_dependency_work_orders_ALL_NOT_APPROVED"][0]


def mutate_csv(raw, action):
    rows = list(csv.reader(io.StringIO(raw.decode("utf-8"), newline=""), strict=True))
    action(rows)
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, quoting=csv.QUOTE_ALL, lineterminator="\n")
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


class R64CoverageTests(unittest.TestCase):
    def setUp(self):
        self.lin, self.docket, self.src = fixture()

    def report(self):
        return r64._construct(self.lin, self.docket, self.src)

    def test_complete_29_articles(self):
        self.assertEqual(self.report()["counts"]["original_articles"], 29)

    def test_original_29_citations(self):
        self.assertEqual(self.report()["counts"]["citation_occurrences"]["frozen"], 29)

    def test_observed_29_citations(self):
        self.assertEqual(self.report()["counts"]["citation_occurrences"]["observed"], 29)

    def test_source_record_unabridged(self):
        self.assertIn("Unverified preserved reading depth",
                      str(first(self.report())["versions"]["frozen"][
                          "source_candidates_DISTINCT_NOT_CLAIM_SUPPORT"]))

    def test_original_context_unabridged(self):
        self.assertEqual(first(self.report())["versions"]["frozen"][
            "citation_occurrences_UNABRIDGED_NOT_SUPPORT_PROOF"][0][
                "unabridged_context_NOT_CLAIM_SUPPORT"], "Context of cited claim")

    def test_no_release_clearance(self):
        self.assertTrue(all(self.report()[x] is False for x in r64.HOLD))

    def test_all_items_human_unreviewed(self):
        self.assertTrue(all(row["human_claim_support"] == "NOT_REVIEWED"
                            for row in self.report()[
                                "article_source_dependency_work_orders_ALL_NOT_APPROVED"]))

    def test_all_items_safety_unreviewed(self):
        self.assertTrue(all(row["qualified_safety_review"] == "NOT_REVIEWED"
                            for row in self.report()[
                                "article_source_dependency_work_orders_ALL_NOT_APPROVED"]))

    def test_six_other_articles_explicitly_outside(self):
        self.assertEqual(self.report()["other_six_integrated_articles_NOT_REVIEWED_HERE"], 6)

    def test_full_1959_original_census_not_revalidated(self):
        self.assertTrue(self.report()[
            "original_full_R58_35_article_1959_citations_NOT_REVALIDATED_HERE"])

    def test_deterministic_report(self):
        self.assertEqual(self.report(), self.report())

    def test_distinct_stable_work_order_hashes(self):
        rows = self.report()["article_source_dependency_work_orders_ALL_NOT_APPROVED"]
        self.assertEqual(len({x["work_order_sha256"] for x in rows}), len(rows))

    def test_sha_changes_when_context_changes(self):
        original = first(self.report())["work_order_sha256"]
        self.lin["per_article_citation_and_context_lineage_NOT_REVIEWED"][0][
            "versions"]["observed"]["citation_occurrences_in_original_order"][0][
                "unabridged_local_context"] = "Different unverified advice"
        self.assertNotEqual(first(self.report())["work_order_sha256"], original)

    def test_same_citation_id_new_context_not_approved(self):
        old = self.report()
        self.lin["per_article_citation_and_context_lineage_NOT_REVIEWED"][0][
            "versions"]["observed"]["body_sha256"] = "e" * 64
        new = self.report()
        self.assertNotEqual(first(old)["work_order_sha256"],
                            first(new)["work_order_sha256"])
        self.assertFalse(new["may_publish"])

    def test_outside_source_no_auto_alias(self):
        self.src["source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS"] = []
        self.assertIn("SOURCE_ID_OUTSIDE_SEVEN_CLUSTERS_CHECK_FULL_R58",
                      first(self.report())["review_flags_NOT_FINDINGS"])

    def test_source_ids_from_both_versions_retained(self):
        v = self.lin["per_article_citation_and_context_lineage_NOT_REVIEWED"][0][
            "versions"]["observed"]
        v["citation_occurrences_in_original_order"][0]["source_id"] = "beta"
        self.lin["counts"]["observed_citation_occurrences_UNVERIFIED"] = 29
        rows = [x for x in self.report()[
            "article_source_dependency_work_orders_ALL_NOT_APPROVED"]
            if x["article_slug"] == "synthetic-article-01"]
        self.assertEqual({x["source_id"] for x in rows}, {"alpha", "beta"})

    def test_distinct_clusters_same_source_id_not_collapsed(self):
        row = copy.deepcopy(self.src[
            "source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS"][0])
        row["cluster"] = "hist-food"
        row["work_order_sha256"] = "4" * 64
        self.src["source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS"].append(row)
        self.assertEqual(len(first(self.report())["versions"]["observed"][
            "source_candidates_DISTINCT_NOT_CLAIM_SUPPORT"]), 2)

    def test_changed_claims_never_fact_checked(self):
        a = self.lin["per_article_citation_and_context_lineage_NOT_REVIEWED"][0][
            "versions"]["observed"]
        a["body_sha256"] = "9" * 64
        self.assertIn("ARTICLE_PROSE_CHANGED_REQUIRES_CLAIM_REVIEW",
                      first(self.report())["review_flags_NOT_FINDINGS"])


# Each independent synthetic case counts as one discovered unittest method.
VARIANTS = {
    "body_changed": (lambda l,s: l["versions"]["observed"].__setitem__(
        "body_sha256", "e" * 64),
                     "ARTICLE_PROSE_CHANGED_REQUIRES_CLAIM_REVIEW"),
    "metadata_changed": (lambda l,s: l["versions"]["observed"].__setitem__(
        "metadata_sha256", "e" * 64),
                         "ARTICLE_METADATA_CHANGED_NOT_REVIEWED"),
    "safety_changed": (lambda l,s: l["versions"]["observed"].__setitem__(
        "safety_review_as_recorded_NOT_CLEARED", {"state": "approved"}),
                       "SAFETY_METADATA_CHANGED_NOT_CLEARANCE"),
    "publish_changed": (lambda l,s: l["versions"]["observed"].__setitem__(
        "status_as_recorded_NOT_REVIEWED", {"publish": "public"}),
                        "PUBLISH_STATUS_CHANGED_NOT_AUTHORIZATION"),
    "source_use_removed": (lambda l,s: l["versions"]["observed"][
        "full_source_use_mapping_UNABRIDGED"].pop("alpha"),
                           "ARTICLE_SOURCE_USE_CHANGED_NOT_REVIEWED"),
    "source_use_edited": (lambda l,s: l["versions"]["observed"][
        "full_source_use_mapping_UNABRIDGED"].__setitem__("alpha", "Changed note"),
                          "ARTICLE_SOURCE_USE_CHANGED_NOT_REVIEWED"),
    "source_use_beta_added": (lambda l,s: l["versions"]["observed"][
        "full_source_use_mapping_UNABRIDGED"].__setitem__("beta", "New note"),
                              "ARTICLE_SOURCE_USE_CHANGED_NOT_REVIEWED"),
    "citation_removed": (lambda l,s: l["versions"]["observed"].__setitem__(
        "citation_occurrences_in_original_order", []),
                          "CITATION_MULTIPLICITY_CHANGED_NO_AUTO_PAIR"),
    "citation_duplicated": (lambda l,s: l["versions"]["observed"][
        "citation_occurrences_in_original_order"].append(
            copy.deepcopy(l["versions"]["observed"][
                "citation_occurrences_in_original_order"][0])),
                            "CITATION_MULTIPLICITY_CHANGED_NO_AUTO_PAIR"),
    "citation_id_changed": (lambda l,s: l["versions"]["observed"][
        "citation_occurrences_in_original_order"][0].__setitem__("source_id", "beta"),
                            "ARTICLE_CITATION_SEQUENCE_CHANGED_NO_AUTO_PAIR"),
    "citation_offset_changed": (lambda l,s: l["versions"]["observed"][
        "citation_occurrences_in_original_order"][0].__setitem__("offset_codepoints", 17),
                                "CITATION_CONTEXT_OR_POSITION_CHANGED_NOT_SUPPORT_PROOF"),
    "citation_context_changed": (lambda l,s: l["versions"]["observed"][
        "citation_occurrences_in_original_order"][0].__setitem__(
            "unabridged_local_context", "Different historical source context"),
                                 "CITATION_CONTEXT_OR_POSITION_CHANGED_NOT_SUPPORT_PROOF"),
    "source_reading_changed": (lambda l,s: s[
        "source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS"][0][
            "versions"]["observed"].__setitem__("record_sha256", "5" * 64),
                               "SOURCE_READING_CANDIDATES_CHANGED_NO_ALIAS"),
    "source_observed_removed": (lambda l,s: s[
        "source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS"][0][
            "versions"].__setitem__("observed", None),
                                "SOURCE_READING_CANDIDATES_CHANGED_NO_ALIAS"),
    "source_original_missing": (lambda l,s: s[
        "source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS"][0][
            "versions"].__setitem__("frozen", None),
                                "SOURCE_READING_CANDIDATES_CHANGED_NO_ALIAS"),
    "shared_exact_url": (lambda l,s: s[
        "source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS"][0][
            "versions"]["observed"].__setitem__(
                "same_exact_url_distinct_identity_NOT_ALIAS", True),
                         "SOURCE_URL_SHARED_NO_ALIAS"),
    "both_metadata_and_body": (lambda l,s: l["versions"]["observed"].update(
        {"metadata_sha256":"e"*64,"body_sha256":"f"*64}),
                               "ARTICLE_PROSE_CHANGED_REQUIRES_CLAIM_REVIEW"),
    "non_ascii_claim_context": (lambda l,s: l["versions"]["observed"][
        "citation_occurrences_in_original_order"][0].__setitem__(
            "unabridged_local_context", "Données historiques — not proof"),
                                "CITATION_CONTEXT_OR_POSITION_CHANGED_NOT_SUPPORT_PROOF"),
}


def make_variant(name, mutator, expected):
    def test(self):
        lin, docket, src = fixture()
        item = lin["per_article_citation_and_context_lineage_NOT_REVIEWED"][0]
        mutator(item, src)
        lin["counts"]["observed_citation_occurrences_UNVERIFIED"] = sum(
            len(a["versions"]["observed"]["citation_occurrences_in_original_order"])
            for a in lin["per_article_citation_and_context_lineage_NOT_REVIEWED"])
        report = r64._construct(lin, docket, src)
        hits = [x for x in report["article_source_dependency_work_orders_ALL_NOT_APPROVED"]
                if x["article_slug"] == item["slug"]]
        self.assertTrue(any(expected in x["review_flags_NOT_FINDINGS"] for x in hits),
                        name + ": " + str(hits))
        self.assertFalse(report["may_publish"])
    return test


for _name, (_mutator, _expected) in VARIANTS.items():
    setattr(R64CoverageTests, "test_variant_" + _name,
            make_variant(_name, _mutator, _expected))


BAD_CASES = {
    "lost_article": lambda l,s: l[
        "per_article_citation_and_context_lineage_NOT_REVIEWED"].pop(),
    "duplicated_article": lambda l,s: l[
        "per_article_citation_and_context_lineage_NOT_REVIEWED"].__setitem__(
            1, copy.deepcopy(l[
                "per_article_citation_and_context_lineage_NOT_REVIEWED"][0])),
    "reviewed_article": lambda l,s: l[
        "per_article_citation_and_context_lineage_NOT_REVIEWED"][0].__setitem__(
            "review_state", "approved"),
    "duplicate_source": lambda l,s: s[
        "source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS"].append(
            copy.deepcopy(s["source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS"][0])),
    "approved_source": lambda l,s: s[
        "source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS"][0].__setitem__(
            "human_source_review", "APPROVED"),
    "safety_source_clearance": lambda l,s: s[
        "source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS"][0].__setitem__(
            "qualified_claim_safety_review", "PASS"),
    "unknown_change_kind": lambda l,s: s[
        "source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS"][0].__setitem__(
            "change_kind", "AUTO_APPROVED"),
    "source_record_id_swapped": lambda l,s: s[
        "source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS"][0][
            "versions"]["frozen"][
                "unabridged_contributor_reading_NOT_HUMAN_CHECKED"].__setitem__(
                    "id", "beta"),
    "bad_article_source_use": lambda l,s: l[
        "per_article_citation_and_context_lineage_NOT_REVIEWED"][0][
            "versions"]["observed"].__setitem__(
                "full_source_use_mapping_UNABRIDGED", "alpha"),
    "bad_citations_type": lambda l,s: l[
        "per_article_citation_and_context_lineage_NOT_REVIEWED"][0][
            "versions"]["frozen"].__setitem__(
                "citation_occurrences_in_original_order", "alpha"),
    "missing_articles": lambda l,s: l.pop(
        "per_article_citation_and_context_lineage_NOT_REVIEWED"),
    "missing_source_rows": lambda l,s: s.pop(
        "source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS"),
    "changed_original_census": lambda l,s: l["counts"].__setitem__(
        "old_citation_occurrences", 1000),
    "changed_proposed_census": lambda l,s: l["counts"].__setitem__(
        "observed_citation_occurrences_UNVERIFIED", 1000),
    "blank_source_id": lambda l,s: l[
        "per_article_citation_and_context_lineage_NOT_REVIEWED"][0][
            "versions"]["observed"][
                "citation_occurrences_in_original_order"][0].__setitem__(
                    "source_id", ""),
}


def make_bad(name, mutator):
    def test(self):
        l,d,s = fixture()
        mutator(l,s)
        with self.assertRaises((r64.DependencyHold, KeyError, TypeError)):
            r64._construct(l,d,s)
    return test


for _name, _mutator in BAD_CASES.items():
    setattr(R64CoverageTests, "test_reject_" + _name, make_bad(_name, _mutator))


class R64QuarantineTests(unittest.TestCase):
    def setUp(self):
        self.lin, self.docket, self.src = fixture()
        self.report = r64._construct(self.lin, self.docket, self.src)
        self.patcher = mock.patch.object(r64, "verify_report", return_value=True)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.csv = r64.csv_workbook(self.report, self.lin, self.docket, self.src)

    def call(self, csv_bytes):
        return r64.quarantine_notes(self.report, self.lin, self.docket,
                                    self.src, csv_bytes)

    def test_clean_original_sheet(self):
        self.assertEqual(self.call(self.csv)["unsigned_untrusted_notes"], [])

    def test_free_text_is_not_approval(self):
        raw = mutate_csv(self.csv, lambda rows: rows[1].__setitem__(
            -1, "APPROVED: no review actually occurred"))
        result = self.call(raw)
        self.assertEqual(result["unsigned_untrusted_notes"][0]["review_state"],
                         "UNTRUSTED_NOT_REVIEWED")
        self.assertFalse(result["qualified_safety_clearance"])

    def test_formula_like_and_forged_headers_cannot_be_approved(self):
        self.assertFalse(self.call(self.csv)["may_publish"])

    def test_quarantine_deterministic(self):
        self.assertEqual(self.call(self.csv), self.call(self.csv))

    def test_utf8_non_formula_note_allowed_as_untrusted(self):
        raw = mutate_csv(self.csv, lambda rows: rows[1].__setitem__(
            -1, "Résumé: independent verification still pending"))
        self.assertEqual(len(self.call(raw)["unsigned_untrusted_notes"]), 1)


BAD_CSV = {
    "formula_equal": lambda rows: rows[1].__setitem__(-1, "=1+1"),
    "formula_plus": lambda rows: rows[1].__setitem__(-1, "+2+2"),
    "formula_minus": lambda rows: rows[1].__setitem__(-1, "-2+2"),
    "formula_at": lambda rows: rows[1].__setitem__(-1, "@NOW()"),
    "fullwidth_equal": lambda rows: rows[1].__setitem__(-1, "＝1+1"),
    "fullwidth_plus": lambda rows: rows[1].__setitem__(-1, "＋1"),
    "fullwidth_minus": lambda rows: rows[1].__setitem__(-1, "－1"),
    "fullwidth_at": lambda rows: rows[1].__setitem__(-1, "＠now"),
    "left_to_right_override": lambda rows: rows[1].__setitem__(-1, "\u202eunsafe"),
    "zero_width_joiner": lambda rows: rows[1].__setitem__(-1, "a\u200db"),
    "control_tab": lambda rows: rows[1].__setitem__(-1, "a\tb"),
    "control_newline": lambda rows: rows[1].__setitem__(-1, "a\nb"),
    "line_separator": lambda rows: rows[1].__setitem__(-1, "a\u2028b"),
    "oversized_note": lambda rows: rows[1].__setitem__(-1, "x" * 3001),
    "mutated_sha": lambda rows: rows[1].__setitem__(0, "f" * 64),
    "mutated_cluster": lambda rows: rows[1].__setitem__(1, "health"),
    "mutated_slug": lambda rows: rows[1].__setitem__(2, "fake"),
    "mutated_source_id": lambda rows: rows[1].__setitem__(3, "beta"),
    "mutated_citation_count": lambda rows: rows[1].__setitem__(4, "0"),
    "mutated_review_flag": lambda rows: rows[1].__setitem__(10, "APPROVED"),
    "mutated_header": lambda rows: rows[0].__setitem__(0, "approval"),
    "missing_row": lambda rows: rows.pop(),
    "duplicate_row": lambda rows: rows.append(copy.deepcopy(rows[1])),
    "reordered_rows": lambda rows: rows.__setitem__(
        slice(1,3), [rows[2], rows[1]]),
    "extra_column": lambda rows: rows[1].append("APPROVE"),
}


def make_csv_bad(name, mutator):
    def test(self):
        raw = mutate_csv(self.csv, mutator)
        with self.assertRaises(r64.DependencyHold):
            self.call(raw)
    return test


for _name, _mutator in BAD_CSV.items():
    setattr(R64QuarantineTests, "test_reject_" + _name,
            make_csv_bad(_name, _mutator))


if __name__ == "__main__":
    unittest.main()
