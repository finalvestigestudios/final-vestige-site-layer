"""R108 adversarial in-memory regression tests; never modify live source tree."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import r108_source_citation_change_impact_crosswalk as g
import r107_exact_branch_progression_adjudication as r107

BODY = "preparedness/content/articles/rain-barrels-and-cisterns.body.html"
META = "preparedness/content/articles/rain-barrels-and-cisterns.meta.json"
FRAG = "preparedness/sources/fragments/hist-home.json"
DOC = "preparedness/docs/CLUSTER-hist-home.md"
TEST = "preparedness/tests/test_preparedness.py"
OLD_COMMIT = "1" * 40
ORIGIN = "hist-home"


def b(value):
    return value.encode("utf-8")


def body(text='''<section class="pa-act"><h2>Before</h2>
<p>Original careful explanation {{cite:source-a}} and scope. {{cite:source-b}}</p>
<span class="pa-tag--unc">Not validated</span></section>'''):
    return b(text)


def meta(*, slug="rain-barrels-and-cisterns", status="draft",
         safety="pending", use=None, checked="2026-10-30", note=None):
    return b(json.dumps({
        "slug": slug, "status": {"publish": status, "editorial": "drafted"},
        "safety_review": {"state": safety, "reviewer": None,
                          "scope": note or "Requires qualified human review"},
        "source_use": use if use is not None else
        {"source-a": "scope of source A", "source-b": "historical scope of B"},
        "last_checked": checked,
    }, sort_keys=True))


def fragment(*, source_id="source-a", url="https://example.org/source-a",
             supports="Interpretation subject to human review", checked=False,
             verified="2026-10-30", notes="Read introduction only"):
    return b(json.dumps({"sources": [{
        "id": source_id, "url": url, "publisher": "Synthetic review fixture",
        "supports": supports, "notes": notes, "human_link_check": checked,
        "verified_on": verified,
    }]}, sort_keys=True))


def make(old=None, new=None, path=BODY, origin=ORIGIN):
    if old is None:
        old = body()
    if new is None:
        new = body("<h2>Revised</h2><p>A different claim {{cite:source-b}}.</p>")
    tips = []
    for name, sha in sorted(r107.EXPECTED_HEADS.items()):
        tips.append({"origin": name, "frozen_commit_sha": OLD_COMMIT,
                     "observed_commit_sha": sha, "is_direct_descendant": True,
                     "human_lineage_approval": "NOT_REVIEWED"})
    row = {
        "origin": origin, "path": path, "classification": r107.kind(path),
        "frozen_blob_sha": r107.r60.blob_sha(old),
        "current_blob_sha": r107.r60.blob_sha(new),
        "original_72_path_scope": True, "human_provenance_review": "NOT_REVIEWED",
        "human_source_and_claim_review": "NOT_REVIEWED", "may_publish": False,
    }
    q = {
        "schema": r107.SCHEMA, "release_state": "HOLD", "may_publish": False,
        "source_or_claim_accuracy_verified": False,
        "qualified_emergency_or_medical_safety_review": False,
        "independent_QD_PASS": False,
        "frozen_R14_historical_exception_open": True,
        "mandatory_R15_seven_cluster_parity": "FAIL_CLOSED_ON_MOVED_REFS",
        "changed_path_count": 1,
        "seven_contributor_commit_ancestry": tips,
        "contributor_reviewer_queue_NOT_APPROVED": [row],
    }
    seal(q)
    def fetch(commit, asked_path):
        if asked_path != path:
            raise AssertionError("cross-path read")
        return old if commit == OLD_COMMIT else new
    return q, fetch


def seal(q):
    q["sha256_NOT_A_SIGNATURE"] = r107.digest({
        k: v for k, v in q.items() if k != "sha256_NOT_A_SIGNATURE"})


class R108SourceImpactCrosswalk(unittest.TestCase):
    def result(self, old=None, new=None, path=BODY):
        return g.crosswalk(*make(old, new, path))

    def test_body_changed_citation_counts(self):
        x = self.result()["rows_NOT_APPROVED"][0]["change_indicators_NOT_FACT_VERDICTS"]
        self.assertEqual(x["citations_removed"], {"source-a": 1})
        self.assertEqual(x["citation_total_before"], 2)
        self.assertEqual(x["citation_total_after"], 1)

    def test_body_words_depth_warning(self):
        x = self.result()["rows_NOT_APPROVED"][0]["change_indicators_NOT_FACT_VERDICTS"]
        self.assertTrue(x["depth_reduction_needs_review"])

    def test_body_safety_marker_warning(self):
        x = self.result()["rows_NOT_APPROVED"][0]["change_indicators_NOT_FACT_VERDICTS"]
        self.assertTrue(x["safety_marker_reduction_needs_review"])

    def test_body_repeated_citation_occurrences(self):
        old = body("<p>{{cite:source-a}}{{cite:source-a}} {{cite:source-b}}</p>")
        new = body("<p>{{cite:source-a}} {{cite:source-b}}{{cite:source-b}}</p>")
        x = self.result(old, new)["rows_NOT_APPROVED"][0]["change_indicators_NOT_FACT_VERDICTS"]
        self.assertEqual(x["citations_added"], {"source-b": 1})
        self.assertEqual(x["citations_removed"], {"source-a": 1})

    def test_body_no_change_in_citation_ids_does_not_signal_approval(self):
        old = body("<p>Original text {{cite:source-a}}</p>")
        new = body("<p>Entirely different claim {{cite:source-a}}</p>")
        x = self.result(old, new)
        self.assertFalse(x["factual_claim_support_approved"])
        self.assertEqual(x["rows_NOT_APPROVED"][0]["human_source_or_claim_review"],
                         "NOT_REVIEWED")

    def test_malformed_citation_rejected(self):
        with self.assertRaises(g.Hold):
            self.result(body(), body("<p>{{cite:Bad ID}}</p>"))

    def test_truncated_citation_rejected(self):
        with self.assertRaises(g.Hold):
            self.result(body(), body("<p>{{cite:source-a</p>"))

    def test_empty_citation_rejected(self):
        with self.assertRaises(g.Hold):
            self.result(body(), body("<p>{{cite:}}</p>"))

    def test_unknown_unicode_body_rejected(self):
        with self.assertRaises(UnicodeDecodeError):
            self.result(body(), b"\xff" + body())

    def test_meta_source_use_interpretation_changed(self):
        x = self.result(meta(), meta(use={"source-a": "different use",
                                         "source-b": "historical scope of B"}),
                        META)["rows_NOT_APPROVED"][0]["change_indicators_NOT_FACT_VERDICTS"]
        self.assertEqual(x["source_use_reinterpreted"], ["source-a"])

    def test_meta_source_use_add_remove(self):
        x = self.result(meta(), meta(use={"source-b": "historical scope of B",
                                         "source-c": "unverified"}),
                        META)["rows_NOT_APPROVED"][0]["change_indicators_NOT_FACT_VERDICTS"]
        self.assertEqual(x["source_use_added"], ["source-c"])
        self.assertEqual(x["source_use_removed"], ["source-a"])

    def test_meta_slug_change_flag(self):
        x = self.result(meta(), meta(slug="proposed-new-route"), META)
        self.assertTrue(x["rows_NOT_APPROVED"][0]["change_indicators_NOT_FACT_VERDICTS"]["slug_changed"])
        self.assertFalse(x["may_publish"])

    def test_meta_publication_status_escalation_detected(self):
        x = self.result(meta(), meta(status="published"), META)
        self.assertTrue(x["rows_NOT_APPROVED"][0]["change_indicators_NOT_FACT_VERDICTS"]
                        ["proposed_release_status_is_not_draft"])
        self.assertFalse(x["may_publish"])

    def test_meta_safety_state_escalation_not_approval(self):
        x = self.result(meta(), meta(safety="approved"), META)
        self.assertTrue(x["rows_NOT_APPROVED"][0]["change_indicators_NOT_FACT_VERDICTS"]
                        ["changed_safety_record_requires_human_review"])
        self.assertFalse(x["qualified_emergency_safety_approved"])

    def test_meta_safety_scope_change_detected(self):
        x = self.result(meta(), meta(note="Proposed unverified new scope"), META)
        self.assertIn("scope", x["rows_NOT_APPROVED"][0]
                      ["change_indicators_NOT_FACT_VERDICTS"]["safety_review_fields_changed"])

    def test_meta_review_date_changed(self):
        x = self.result(meta(), meta(checked="2026-11-03"), META)
        self.assertTrue(x["rows_NOT_APPROVED"][0]
                        ["change_indicators_NOT_FACT_VERDICTS"]["last_checked_changed"])

    def test_meta_bad_source_use_type_rejected(self):
        x = json.loads(meta()); x["source_use"] = ["source-a"]
        with self.assertRaises(g.Hold):
            self.result(meta(), b(json.dumps(x)), META)

    def test_meta_missing_safety_record_rejected(self):
        x = json.loads(meta()); del x["safety_review"]
        with self.assertRaises(g.Hold):
            self.result(meta(), b(json.dumps(x)), META)

    def test_meta_non_string_source_use_rejected(self):
        x = json.loads(meta()); x["source_use"]["source-b"] = True
        with self.assertRaises(g.Hold):
            self.result(meta(), b(json.dumps(x)), META)

    def test_multi_file_source_id_impact_join(self):
        old_body = body("<p>History {{cite:source-a}}</p>")
        new_body = body("<p>Revised history {{cite:source-c}}</p>")
        old_meta, new_meta = meta(), meta(use={
            "source-b": "historical scope of B",
            "source-c": "a new reading scope pending review"})
        old_frag, new_frag = fragment(), fragment(supports="changed reading claim")
        q, _ = make(old_body, new_body, BODY)
        rows = q["contributor_reviewer_queue_NOT_APPROVED"]
        payloads = {
            BODY: (old_body, new_body), META: (old_meta, new_meta),
            FRAG: (old_frag, new_frag),
        }
        for p in (META, FRAG):
            old, new = payloads[p]
            r = copy.deepcopy(rows[0])
            r.update({"path": p, "classification": r107.kind(p),
                      "frozen_blob_sha": r107.r60.blob_sha(old),
                      "current_blob_sha": r107.r60.blob_sha(new)})
            rows.append(r)
        q["changed_path_count"] = 3
        seal(q)
        def fetch(commit, path):
            old, new = payloads[path]
            return old if commit == OLD_COMMIT else new
        x = g.crosswalk(q, fetch)
        intersection = x["cross_file_source_id_intersections_NOT_APPROVED"]
        self.assertEqual(intersection["source-a"], ["body", "fragment", "meta"])
        self.assertEqual(intersection["source-c"], ["body", "meta"])
        self.assertFalse(x["factual_claim_support_approved"])
        self.assertEqual(len(x["source_id_change_impact_index_NOT_APPROVED"]["source-a"]), 3)

    def test_single_file_impact_index_is_not_false_shared_source(self):
        x = self.result()
        self.assertIn("source-a", x["source_id_change_impact_index_NOT_APPROVED"])
        self.assertEqual(x["cross_file_source_id_intersections_NOT_APPROVED"], {})

    def test_impact_index_contains_no_source_support_or_original_prose(self):
        x = self.result()
        index_text = json.dumps(x["source_id_change_impact_index_NOT_APPROVED"])
        self.assertNotIn("Original careful explanation", index_text)
        self.assertIn("human_review", index_text)

    def test_fragment_source_support_changed(self):
        x = self.result(fragment(), fragment(supports="New meaning"), FRAG)
        fields = x["rows_NOT_APPROVED"][0]["change_indicators_NOT_FACT_VERDICTS"]
        self.assertEqual(fields["reading_support_changed"], ["source-a"])
        self.assertFalse(x["factual_claim_support_approved"])

    def test_fragment_url_changed(self):
        x = self.result(fragment(), fragment(url="https://example.org/second"), FRAG)
        self.assertEqual(x["rows_NOT_APPROVED"][0]
                         ["change_indicators_NOT_FACT_VERDICTS"]["literal_urls_changed"],
                         ["source-a"])

    def test_fragment_same_url_different_scope(self):
        x = self.result(fragment(), fragment(notes="Read different page"), FRAG)
        fields = x["rows_NOT_APPROVED"][0]["change_indicators_NOT_FACT_VERDICTS"]
        self.assertEqual(fields["reading_support_changed"], ["source-a"])
        self.assertEqual(fields["literal_urls_changed"], [])
        self.assertTrue(fields["unchanged_literal_url_does_not_imply_same_source_scope"])

    def test_fragment_human_link_check_changed_not_approval(self):
        x = self.result(fragment(), fragment(checked=True), FRAG)
        self.assertEqual(x["rows_NOT_APPROVED"][0]
                         ["change_indicators_NOT_FACT_VERDICTS"]["human_link_check_value_changed"],
                         ["source-a"])
        self.assertFalse(x["factual_claim_support_approved"])

    def test_fragment_verified_date_changed_not_approval(self):
        x = self.result(fragment(), fragment(verified="2026-11-03"), FRAG)
        self.assertEqual(x["rows_NOT_APPROVED"][0]
                         ["change_indicators_NOT_FACT_VERDICTS"]["verified_date_changed"],
                         ["source-a"])

    def test_fragment_removed_source_id(self):
        x = self.result(fragment(), fragment(source_id="source-b"), FRAG)
        fields = x["rows_NOT_APPROVED"][0]["change_indicators_NOT_FACT_VERDICTS"]
        self.assertEqual(fields["source_ids_removed"], ["source-a"])
        self.assertEqual(fields["source_ids_added"], ["source-b"])

    def test_fragment_duplicate_id_rejected(self):
        x = json.loads(fragment()); x["sources"].append(x["sources"][0])
        with self.assertRaises(g.Hold):
            self.result(fragment(), b(json.dumps(x)), FRAG)

    def test_fragment_invalid_source_id_rejected(self):
        with self.assertRaises(g.Hold):
            self.result(fragment(), fragment(source_id="OR injected"), FRAG)

    def test_fragment_nonobject_rejected(self):
        with self.assertRaises(g.Hold):
            self.result(fragment(), b('{"sources":[null]}'), FRAG)

    def test_fragment_missing_url_rejected(self):
        x = json.loads(fragment()); del x["sources"][0]["url"]
        with self.assertRaises(g.Hold):
            self.result(fragment(), b(json.dumps(x)), FRAG)

    def test_fragment_oversize_source_count_rejected(self):
        with self.assertRaises(g.Hold):
            g.summarize_fragment(b(json.dumps({"sources": [{}] * 2001})))

    def test_doc_unstructured_review_required(self):
        x = self.result(b("frozen doc"), b("revised doc"), DOC)
        self.assertTrue(x["rows_NOT_APPROVED"][0]
                        ["change_indicators_NOT_FACT_VERDICTS"]["human_diff_review_required"])

    def test_test_path_outside_original_scope_never_approval(self):
        x = self.result(b("old test"), b("new test"), TEST)
        self.assertFalse(x["may_publish"])
        self.assertFalse(x["independent_QD_PASS"])

    def test_duplicate_path_rejected_even_with_seal_recomputed(self):
        q, fetch = make()
        q["contributor_reviewer_queue_NOT_APPROVED"].append(copy.deepcopy(
            q["contributor_reviewer_queue_NOT_APPROVED"][0]))
        q["changed_path_count"] = 2; seal(q)
        with self.assertRaises(g.Hold):
            g.crosswalk(q, fetch)

    def test_missing_observed_object_rejected(self):
        q, fetch = make()
        with self.assertRaises(g.Hold):
            g.crosswalk(q, lambda commit, path: b("forged"))

    def test_forger_recomputes_r107_hash_not_original_blob(self):
        q, fetch = make()
        q["contributor_reviewer_queue_NOT_APPROVED"][0]["current_blob_sha"] = "e" * 40
        seal(q)
        with self.assertRaises(g.Hold):
            g.crosswalk(q, fetch)

    def test_oversize_git_object_rejected(self):
        q, fetch = make()
        with self.assertRaises(g.Hold):
            g.crosswalk(q, lambda sha, path: b"a" * (g.MAX_BYTES+1))

    def test_body_content_not_placed_in_dossier(self):
        x = self.result()
        serialized = json.dumps(x)
        self.assertNotIn("Original careful explanation", serialized)

    def test_dossier_is_deterministic(self):
        self.assertEqual(self.result(), self.result())

    def test_result_digest_replay(self):
        x = self.result()
        self.assertEqual(x["sha256_NOT_A_SIGNATURE"], r107.digest({
            k: v for k, v in x.items() if k != "sha256_NOT_A_SIGNATURE"}))

    def test_input_not_mutated(self):
        q, fetch = make(); before = copy.deepcopy(q)
        g.crosswalk(q, fetch)
        self.assertEqual(q, before)

    def test_git_path_checks(self):
        with self.assertRaises(g.Hold):
            g.git_object(Path("."), "f"*40, "preparedness/../config")

    def test_git_object_requires_sha(self):
        with self.assertRaises(g.Hold):
            g.git_object(Path("."), "HEAD; echo bad", BODY)


# Each case is an independent adversarial test of a distinct field/path
# manipulation; recomputing an unsigned checksum must NOT confer trust.
GATE_MUTATIONS = [
    ("schema", "other-schema"), ("release_state", "PASS"),
    ("may_publish", True), ("source_or_claim_accuracy_verified", True),
    ("qualified_emergency_or_medical_safety_review", True),
    ("independent_QD_PASS", True), ("frozen_R14_historical_exception_open", False),
    ("mandatory_R15_seven_cluster_parity", "PASS"), ("changed_path_count", 0),
]
ROW_MUTATIONS = [
    ("path", "preparedness/../private"),
    ("path", "preparedness/content/articles/other.body.html"),
    ("classification", "meta"),
    ("human_provenance_review", "APPROVED"),
    ("human_source_and_claim_review", "APPROVED"),
    ("may_publish", True),
    ("origin", "invented"),
    ("frozen_blob_sha", "not-sha"),
    ("current_blob_sha", "not-sha"),
    ("frozen_blob_sha", None),
]
HEAD_MUTATIONS = [
    ("observed_commit_sha", "a"*40),
    ("is_direct_descendant", False),
    ("human_lineage_approval", "APPROVED"),
    ("origin", "invented"),
    ("frozen_commit_sha", None),
]


def rejection_test(which, field, value):
    def test(self):
        q, fetch = make()
        target = (q if which == "gate" else
                  q["contributor_reviewer_queue_NOT_APPROVED"][0]
                  if which == "row" else
                  q["seven_contributor_commit_ancestry"][0])
        target[field] = value
        seal(q)
        with self.assertRaises((g.Hold, ValueError, TypeError)):
            g.crosswalk(q, fetch)
    return test


for kind, mutations in (("gate", GATE_MUTATIONS),
                        ("row", ROW_MUTATIONS),
                        ("head", HEAD_MUTATIONS)):
    for n, (field, value) in enumerate(mutations):
        setattr(R108SourceImpactCrosswalk,
                "test_reject_" + kind + "_" + str(n).zfill(2) + "_" + field,
                rejection_test(kind, field, value))


if __name__ == "__main__":
    unittest.main()
