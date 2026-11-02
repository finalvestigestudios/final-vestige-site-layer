"""R72 adversarial review-custody tests; synthetic source/DOM evidence only.

No external requests, CMS writes, article edits or safety-status approvals.
Mutations re-sign the outer report to test internal consistency, not only seals.
"""
from __future__ import annotations

from copy import deepcopy
import csv
import importlib.util
import io
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parents[1]
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    out=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(out)
    return out

gate=module(HERE/"tools"/"r72_source_scope_collision_impact.py","r72_under_test")
fixture=module(HERE/"tests"/"test_r71_rc_dom_block_source_review.py",
               "r71_synthetic_fixture_for_r72")
N=fixture.N


def baseline():
    return fixture.produce()


def reseal(report, deep=False):
    if deep:
        for task in report["all_DOM_block_claim_and_exact_source_review_tasks_NOT_APPROVED"]:
            task["task_sha256"]=gate.fingerprint({
                k:v for k,v in task.items() if k!="task_sha256"})
    report.pop("fingerprint_sha256",None)
    report["fingerprint_sha256"]=gate.fingerprint(report)
    return report


def src(d,n=0):
    return d["all_244_unabridged_source_reading_review_records_NOT_APPROVED"][n]


def blk(d,n=0):
    return d["all_DOM_block_claim_and_exact_source_review_tasks_NOT_APPROVED"][n]


def edge(d,n=1,which=0):
    return blk(d,n)["local_citations_NOT_CLAIM_SUPPORT_PROOF"][which]


def variant(d,n=1,v=0):
    return edge(d,n)["origin_scoped_source_variants_NOT_ALIASED"][v]


def reverse(d,n=0):
    return d["source_to_cited_block_reverse_custody_NOT_APPROVED"][n]


def add_unattached(d):
    d["citations_with_no_DOM_block_NOT_APPROVED"].append({
        "kind":"article","slug":"first","citation_ordinal":1,
        "source_id":"alpha","review_state":"NOT_REVIEWED"})


class R72ScopeReviewTests(unittest.TestCase):
    def report(self,data=None):
        return gate.construct(data if data is not None else baseline(),expected=N)

    def test_baseline(self):
        r=self.report()
        self.assertEqual(r["release_state"],"HOLD")
        self.assertEqual((r["counts"]["articles"],r["counts"]["tools"]), (1,1))
        self.assertEqual(r["counts"]["complete_distinct_origin_scoped_source_readings"],3)
        self.assertEqual(r["counts"]["citation_occurrences"],3)
        self.assertEqual(r["counts"]["unabridged_DOM_block_tasks"],4)
        self.assertEqual(r["counts"]["direct_DOM_citation_occurrences"],3)
        self.assertEqual(r["counts"]["shared_exact_URL_collision_groups"],1)
        self.assertEqual(r["counts"]["reused_source_ID_collision_groups"],1)

    def test_all_complete_readings_conserved(self):
        r=self.report()
        original=baseline()["all_244_unabridged_source_reading_review_records_NOT_APPROVED"]
        self.assertEqual(r["all_complete_source_readings_NOT_APPROVED"],original)
        self.assertEqual(len(r["all_unabridged_DOM_block_citation_tasks_NOT_APPROVED"]),4)

    def test_exact_url_collision_preserves_different_reading_hashes(self):
        group=self.report()["shared_exact_URL_collision_review_orders_NOT_APPROVED"][0]
        rows=group["source_readings_NOT_MERGED"]
        self.assertEqual({(x["origin"],x["id"]) for x in rows},
                         {("start","alpha"),("food","alpha")})
        self.assertEqual(len({x["full_candidate_reading_sha256"] for x in rows}),2)
        self.assertTrue(all(x["human_scope_and_claim_review"]=="NOT_REVIEWED" for x in rows))

    def test_duplicate_id_does_not_alias_evidence(self):
        group=self.report()["reused_source_ID_collision_review_orders_NOT_APPROVED"][0]
        self.assertEqual(group["value"],"alpha")
        self.assertEqual(len(group["source_readings_NOT_MERGED"]),2)
        self.assertEqual(group["human_scope_resolution"],"NOT_REVIEWED")

    def test_collision_reverse_impact(self):
        group=self.report()["shared_exact_URL_collision_review_orders_NOT_APPROVED"][0]
        self.assertEqual([len(x["downstream_block_citation_edges_NOT_SUPPORT"])
                          for x in group["source_readings_NOT_MERGED"]],[2,2])

    def test_same_block_citation_not_source_support(self):
        r=self.report()
        self.assertEqual(r["counts"]["same_block_topic_with_citation_still_unverified"],3)
        self.assertEqual(r["counts"]["human_claim_support_reviews"],0)
        self.assertEqual(r["counts"]["human_qualified_safety_reviews"],0)

    def test_uncited_topic_block_not_marked_unsafe(self):
        b=self.report()["all_unabridged_DOM_block_citation_tasks_NOT_APPROVED"][0]
        self.assertEqual(b["triage_bucket_NOT_SAFETY_VERDICT"],
                         "TOPIC_NO_SAME_BLOCK_CITATION_REVIEW")
        self.assertEqual(b["qualified_safety_review"],"NOT_REVIEWED")

    def test_all_citations_appear_only_once(self):
        r=self.report()
        self.assertEqual(r["counts"]["citation_occurrences"],3)
        self.assertEqual(r["counts"]["unattached_citation_review_tasks"],0)

    def test_preserves_all_article_tool_draft_urls(self):
        r=self.report()
        self.assertEqual({d["draft_url_NOT_PUBLIC"]
            for d in r["all_document_impact_orders_NOT_APPROVED"]},{
            "/preparedness/article/first/","/preparedness/tool/planner/"})

    def test_seals_and_determinism(self):
        a=self.report();b=self.report()
        self.assertEqual(a,b)
        gate.sealed(a,gate.SCHEMA)
        self.assertEqual(a["fingerprint_sha256"],
                         gate.fingerprint({k:v for k,v in a.items()
                                           if k!="fingerprint_sha256"}))

    def test_immutability_of_input(self):
        data=baseline();before=deepcopy(data)
        self.report(data)
        self.assertEqual(data,before)

    def test_output_does_not_alias_mutable_input(self):
        data=baseline();r=self.report(data)
        src(data)["candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"]["title"]="mutated"
        self.assertNotEqual(src(data)["candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"],
                            r["all_complete_source_readings_NOT_APPROVED"][0][
                              "candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"])

    def test_csv_same_url_two_readings_not_merged(self):
        rows=list(csv.DictReader(io.StringIO(gate.csv_collisions(self.report()))))
        self.assertEqual(len(rows),2)
        self.assertEqual(rows[0]["human_scope_review_NOT_REVIEWED"],"NOT_REVIEWED")

    def test_csv_formula_lead_neutralized(self):
        d=self.report()
        d["shared_exact_URL_collision_review_orders_NOT_APPROVED"][0]["value"]="=2+2"
        reseal(d)
        rows=list(csv.DictReader(io.StringIO(gate.csv_collisions(d))))
        self.assertEqual(rows[1]["exact_value_NOT_NORMALIZED"],"'=2+2")

    def test_csv_invisible_lead_neutralized(self):
        d=self.report()
        d["reused_source_ID_collision_review_orders_NOT_APPROVED"][0]["value"]=" \ufeff@calc"
        reseal(d)
        rows=list(csv.DictReader(io.StringIO(gate.csv_collisions(d))))
        self.assertTrue(rows[0]["exact_value_NOT_NORMALIZED"].startswith("'"))

    def test_reject_nonpositive_census(self):
        with self.assertRaises(gate.Hold):
            gate.construct(baseline(),expected=(1,1,3,0))

    def test_reject_census_boolean(self):
        with self.assertRaises(gate.Hold):
            gate.construct(baseline(),expected=(True,1,3,3))


# Each mutation is independently applied to a fully valid synthetic R71 ledger.
# Outer and per-block digests are intentionally recomputed so structural checks
# catch drift even when an attacker can manufacture consistent-looking hashes.
FAULTS={
    "top_missing_seal":(lambda d:d.pop("fingerprint_sha256"),False),
    "top_wrong_schema":(lambda d:d.update(schema="public-r72"),False),
    "top_issue_changed":(lambda d:d.update(issue=0),False),
    "top_release_pass":(lambda d:d.update(release_state="PASS"),False),
    "top_machine_fraud":(lambda d:d.update(machine_only=False),False),
    "top_publish_spoof":(lambda d:d.update(may_publish=True),False),
    "top_qd_spoof":(lambda d:d.update(independent_QD_approval=True),False),
    "top_safety_spoof":(lambda d:d.update(qualified_safety_clearance=True),False),
    "top_human_link_spoof":(lambda d:d.update(human_source_links_verified=True),False),
    "count_article_loss":(lambda d:d["counts"].update(candidate_articles=2),False),
    "count_tool_loss":(lambda d:d["counts"].update(candidate_tools=0),False),
    "count_source_loss":(lambda d:d["counts"].update(
        unabridged_source_readings_conserved=4),False),
    "count_cite_loss":(lambda d:d["counts"].update(candidate_citations_conserved=2),False),
    "count_fraud_human_reviews":(lambda d:d["counts"].update(
        human_source_claim_or_safety_reviews_by_R71=1),False),
    "source_deleted":(lambda d:d["all_244_unabridged_source_reading_review_records_NOT_APPROVED"].pop(),False),
    "source_duplicate":(lambda d:d["all_244_unabridged_source_reading_review_records_NOT_APPROVED"].__setitem__(2,deepcopy(src(d,0))),False),
    "source_order_changed":(lambda d:d["all_244_unabridged_source_reading_review_records_NOT_APPROVED"].reverse(),False),
    "source_origin_empty":(lambda d:src(d).update(source_origin=""),False),
    "source_ID_empty":(lambda d:src(d).update(source_id=""),False),
    "source_ID_rewritten":(lambda d:src(d).update(source_id="beta"),False),
    "source_URL_switched":(lambda d:src(d).update(exact_URL_NO_ALIAS="https://example.org/else"),False),
    "source_reading_title_drift":(lambda d:src(d)["candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"].update(title="changed"),False),
    "source_reading_url_retarget":(lambda d:src(d)["candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"].update(url="https://example.org/else"),False),
    "source_reading_id_retarget":(lambda d:src(d)["candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"].update(id="else"),False),
    "source_reading_false_link_check":(lambda d:src(d)["candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"].update(human_link_check=True),False),
    "source_sha_modified":(lambda d:src(d).update(candidate_reading_sha256="f"*64),False),
    "source_claim_approved":(lambda d:src(d).update(human_source_and_claim_review="APPROVED"),False),
    "source_safety_approved":(lambda d:src(d).update(qualified_safety_review="SAFE"),False),
    "source_original_sha_invalid":(lambda d:src(d).update(original_reading_sha256="not-sha"),False),
    "source_original_reading_altered":(lambda d:src(d).update(
        original_reading_UNABRIDGED_NOT_HUMAN_VERIFIED={"id":"alpha"},
        original_reading_sha256="0"*64),False),
    "block_removed":(lambda d:d["all_DOM_block_claim_and_exact_source_review_tasks_NOT_APPROVED"].pop(),True),
    "block_duplicate":(lambda d:d["all_DOM_block_claim_and_exact_source_review_tasks_NOT_APPROVED"].append(deepcopy(blk(d))),True),
    "block_wrong_text_sha":(lambda d:blk(d).update(DOM_text_sha256="0"*64),True),
    "block_empty_text":(lambda d:blk(d).update(DOM_text_UNABRIDGED_NOT_BROWSER_OR_SAFETY_VERIFIED=""),True),
    "block_wrong_R69_parent":(lambda d:blk(d).update(R69_document_task_sha256="not-sha"),True),
    "block_doc_kind":(lambda d:blk(d).update(kind="gallery"),True),
    "block_doc_slug":(lambda d:blk(d).update(slug=""),True),
    "block_doc_url_external":(lambda d:blk(d).update(private_draft_url="https://site"),True),
    "block_doc_url_traversal":(lambda d:blk(d).update(private_draft_url="/preparedness/../published/"),True),
    "block_doc_url_double_slash":(lambda d:blk(d).update(private_draft_url="/preparedness//broken/"),True),
    "block_doc_url_collision":(lambda d:blk(d,3).update(
        private_draft_url="/preparedness/article/first/"),True),
    "block_id_empty":(lambda d:blk(d).update(block_id=""),True),
    "block_id_duplicate":(lambda d:blk(d,1).update(block_id="block-1"),True),
    "block_start_negative":(lambda d:blk(d).update(start_offset_codepoints=-1),True),
    "block_start_bool":(lambda d:blk(d).update(start_offset_codepoints=True),True),
    "block_qd_approved":(lambda d:blk(d).update(independent_QD_review="PASS"),True),
    "block_claim_approved":(lambda d:blk(d).update(human_claim_support_review="APPROVED"),True),
    "block_safety_approved":(lambda d:blk(d).update(qualified_safety_review="SAFE"),True),
    "block_topic_duplicate":(lambda d:blk(d).update(topic_signals_TRIAGE_NOT_SAFETY_VERDICT=[
        "MEDICINE_HEALTH","MEDICINE_HEALTH"]),True),
    "block_topic_unsorted":(lambda d:blk(d,2).update(topic_signals_TRIAGE_NOT_SAFETY_VERDICT=[
        "WATER_SANITATION","FOOD_STORAGE"]),True),
    "block_wrong_triage":(lambda d:blk(d).update(triage_bucket_NOT_SAFETY_VERDICT=
        "TOPIC_HAS_CITATION_SUPPORT_STILL_UNVERIFIED"),True),
    "block_neighbor_support_forged":(lambda d:blk(d)[
        "adjacent_citations_NAVIGATION_HINTS_NOT_SUPPORT"][0].update(
        NOT_EVIDENCE_OF_SUPPORT=False),True),
    "block_neighbor_bad_ordinal":(lambda d:blk(d)[
        "adjacent_citations_NAVIGATION_HINTS_NOT_SUPPORT"][0].update(
        citation_ordinals_NAVIGATION_ONLY=["1"]),True),
    "edge_missing":(lambda d:blk(d,1).update(local_citations_NOT_CLAIM_SUPPORT_PROOF=[]),True),
    "edge_duplicate":(lambda d:blk(d,1)[
        "local_citations_NOT_CLAIM_SUPPORT_PROOF"].append(deepcopy(edge(d))),True),
    "edge_ordinal_zero":(lambda d:edge(d).update(ordinal=0),True),
    "edge_ordinal_string":(lambda d:edge(d).update(ordinal="1"),True),
    "edge_duplicate_crossblock_ordinal":(lambda d:edge(d,2).update(ordinal=1),True),
    "edge_offset_negative":(lambda d:edge(d).update(unicode_codepoint_offset=-1),True),
    "edge_offset_bool":(lambda d:edge(d).update(unicode_codepoint_offset=True),True),
    "edge_visibility_spoof":(lambda d:edge(d).update(DOM_visibility_NOT_BROWSER_PROOF="BROWSER_VISIBLE_APPROVED"),True),
    "edge_source_id_changed":(lambda d:edge(d).update(source_id="beta"),True),
    "edge_claim_approved":(lambda d:edge(d).update(human_claim_support_review="APPROVED"),True),
    "edge_variant_removed":(lambda d:edge(d).update(origin_scoped_source_variants_NOT_ALIASED=[]),True),
    "edge_variant_duplicate":(lambda d:edge(d)[
        "origin_scoped_source_variants_NOT_ALIASED"].append(deepcopy(variant(d))),True),
    "edge_variant_reorder":(lambda d:edge(d)[
        "origin_scoped_source_variants_NOT_ALIASED"].reverse(),True),
    "edge_variant_source_removed":(lambda d:variant(d).update(source_origin="nonexistent"),True),
    "edge_variant_source_sha_changed":(lambda d:variant(d).update(complete_source_reading_sha256="0"*64),True),
    "edge_variant_url_changed":(lambda d:variant(d).update(exact_URL_NOT_ALIAS="https://fake.test/"),True),
    "edge_variant_approved":(lambda d:variant(d).update(human_source_and_claim_review="APPROVED"),True),
    "edge_preferred_missing":(lambda d:edge(d).update(preferred_identity_NOT_APPROVED=["other","alpha"]),True),
    "reverse_row_removed":(lambda d:d["source_to_cited_block_reverse_custody_NOT_APPROVED"].pop(),False),
    "reverse_row_duplicate":(lambda d:d["source_to_cited_block_reverse_custody_NOT_APPROVED"].append(deepcopy(reverse(d))),False),
    "reverse_source_id_changed":(lambda d:reverse(d).update(source_id="missing"),False),
    "reverse_sha_changed":(lambda d:reverse(d).update(source_record_sha256="0"*64),False),
    "reverse_claim_approved":(lambda d:reverse(d).update(human_source_claim_review="APPROVED"),False),
    "reverse_edge_removed":(lambda d:reverse(d)[
        "citation_block_occurrences_NOT_SOURCE_SUPPORT_PROOF"].pop(),False),
    "reverse_edge_added":(lambda d:reverse(d)[
        "citation_block_occurrences_NOT_SOURCE_SUPPORT_PROOF"].append(["article","first","fake",1]),False),
    "unattached_duplicate":(add_unattached,False),
    "count_blocks_wrong":(lambda d:d["counts"].update(DOM_text_blocks_review_tasks=5),False),
    "count_direct_wrong":(lambda d:d["counts"].update(citation_occurrences_attached_to_DOM_blocks=1),False),
    "count_missing_topic_wrong":(lambda d:d["counts"].update(keyword_topic_blocks_without_same_block_citation=2),False),
    "count_with_topic_wrong":(lambda d:d["counts"].update(keyword_topic_blocks_with_local_citation_UNVERIFIED=1),False),
    "count_reverse_wrong":(lambda d:d["counts"].update(source_variants_with_cited_DOM_blocks=2),False),
    "count_unattached_wrong":(lambda d:d["counts"].update(citations_without_DOM_block_unresolved=1),False),
}


def _test_mutation(name,defn):
    mutate,deep=defn
    def test(self):
        bad=deepcopy(baseline())
        mutate(bad)
        if name!="top_missing_seal":
            reseal(bad,deep=deep)
        with self.assertRaises(gate.Hold,msg=name):
            self.report(bad)
    test.__name__="test_fail_closed_"+name
    return test


for _name,_defn in FAULTS.items():
    setattr(R72ScopeReviewTests,"test_fail_closed_"+_name,_test_mutation(_name,_defn))


if __name__=="__main__":
    unittest.main()
