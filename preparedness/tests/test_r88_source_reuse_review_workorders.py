"""R88 synthetic/adversarial source/citation custody tests. All fixtures in memory.

No shared working-tree fixture writes, network calls, CMS publication or safety verdict.
"""
from __future__ import annotations
from copy import deepcopy
import hashlib
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location(
    "r88_tests",ROOT/"tools"/"r88_source_reuse_review_workorders.py")
r88=importlib.util.module_from_spec(spec)
spec.loader.exec_module(r88)
R=r88.REVIEW


def source(origin="water",sid="s",url="https://example.org/source",reading="a"*64):
    return {"source_origin":origin,"source_id":sid,
            "complete_source_reading_sha256":reading,
            "exact_URL_NOT_CANONICALIZED":url}


def doc(slug="one",kind="article",references=None,cues=None):
    if references is None:
        references=[("s",[source()])]
    text="Original complete unreviewed text with literal citation context."
    b={"block_id":"block-001","DOM_text_sha256":
       hashlib.sha256(text.encode("utf-8")).hexdigest(),
       "unabridged_DOM_text_NOT_REVIEWED":text,
       "human_claim_support_review":R,"qualified_safety_review":R}
    reviews=[]
    for n,(sid,variants) in enumerate(references,1):
        c={"raw_source_id":sid,"citation_ordinal":n,
           "source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT":variants}
        bridge={"R80_original_citation_UNABRIDGED_NOT_APPROVED":c,
                "R80_original_block_id":"block-001"}
        reviews.append({"R86_original_citation_bridge_UNABRIDGED_NOT_APPROVED":bridge,
                        "R80_original_complete_DOM_block_UNABRIDGED_NOT_APPROVED":
                            deepcopy(b),
                        "review_cues_NOT_VERDICTS":list(cues or []),
                        "rank_alignment_proves_claim_identity":False,
                        "human_claim_support":R,"qualified_safety_review":R,
                        "may_publish":False})
    original={"all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED":[b],
              "original_DOM_block_ids_in_reading_order":["block-001"],
              "citation_occurrences_NOT_UNIQUE_CLAIMS":len(references)}
    return {"kind":kind,"slug":slug,
            "R86_complete_document_UNABRIDGED_NOT_APPROVED":{
                "R80_complete_original_document_UNABRIDGED_NOT_APPROVED":original,
                "private_draft_url_NOT_PUBLISHED":"/preparedness/"+slug+"/"},
            "all_original_citation_and_claim_context_reviews_NOT_APPROVED":reviews,
            "human_claim_support":R,"qualified_safety_review":R,
            "independent_QD_review":R,"may_publish":False}


def sample(docs=None,unpaired=None):
    docs=[doc()] if docs is None else docs
    cites=sum(len(d["all_original_citation_and_claim_context_reviews_NOT_APPROVED"])
              for d in docs)
    edges=sum(len(row["R86_original_citation_bridge_UNABRIDGED_NOT_APPROVED"]
                  ["R80_original_citation_UNABRIDGED_NOT_APPROVED"]
                  ["source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT"])
              for d in docs for row in
              d["all_original_citation_and_claim_context_reviews_NOT_APPROVED"])
    return {"schema":r88.PARENT_SCHEMA,"issue":136,"release_state":r88.HOLD,
            "may_publish":False,"medical_safety_approved":False,
            "human_source_approvals":0,"human_claim_approvals":0,
            "qualified_safety_approvals":0,"independent_QD_approvals":0,
            "counts":{"documents":len(docs),"citations":cites,
                      "source_variant_edges":edges,"blocks":len(docs)},
            "all_41_rank_ambiguity_review_packets_NOT_APPROVED":docs,
            "unpaired_historical_review_records_UNABRIDGED":unpaired or []}


class Invariants(unittest.TestCase):
    def setUp(self):
        self.parent=sample()
        self.report=r88.index(self.parent)

    def test_original_report_retained_verbatim(self):
        self.assertEqual(
            self.report["complete_R87_original_evidence_UNABRIDGED_NOT_APPROVED"],
            self.parent)

    def test_original_literal_url_preserved(self):
        self.assertEqual(self.report[
            "all_distinct_source_variant_review_workorders_NOT_APPROVED"][0][
            "exact_URL_NOT_CANONICALIZED_NOT_VERIFIED"],
            "https://example.org/source")

    def test_citation_count(self):
        self.assertEqual(self.report["counts"]["citations"],1)

    def test_source_variant_edge_count(self):
        self.assertEqual(self.report["counts"]["source_variant_edges"],1)

    def test_full_dom_block_count(self):
        self.assertEqual(self.report["counts"]["complete_DOM_blocks"],1)

    def test_human_review_is_unapproved(self):
        row=self.report["all_literal_citation_occurrence_workorders_NOT_APPROVED"][0]
        self.assertEqual(row["human_claim_support"],R)
        self.assertIs(row["may_publish"],False)

    def test_no_qualified_safety_approval(self):
        self.assertIs(self.report["medical_safety_approved"],False)
        self.assertEqual(self.report["qualified_safety_approvals"],0)

    def test_no_QD_PASS(self):
        self.assertEqual(self.report["independent_QD_approvals"],0)

    def test_one_original_source_variant(self):
        self.assertEqual(self.report["counts"]["distinct_source_variants"],1)

    def test_identical_input_deterministic_output(self):
        self.assertEqual(r88.digest(self.report),
                         r88.digest(r88.index(deepcopy(self.parent))))

    def test_same_literal_url_distinct_variants_retained(self):
        p=sample([doc(references=[
            ("s",[source(),source(origin="food",reading="b"*64)])])])
        out=r88.index(p)
        self.assertEqual(out["counts"]["literal_URL_variant_collision_groups"],1)
        group=out["exact_literal_URL_reuse_groups_NOT_EQUIVALENCE"][0]
        self.assertEqual(len(group["distinct_variant_keys_NOT_MERGED"]),2)
        self.assertIs(group["same_URL_proves_source_identity"],False)

    def test_same_source_reused_does_not_prove_claim_support(self):
        p=sample([doc(references=[("s",[source()]),("s",[source()])])])
        out=r88.index(p)
        self.assertEqual(out["counts"]["source_variants_reused_by_multiple_citations"],1)
        self.assertEqual(len(out["all_distinct_source_variant_review_workorders_NOT_APPROVED"][0][
            "separate_citation_occurrences"]),2)

    def test_url_case_not_normalized(self):
        p=sample([doc(references=[("s",[source(url="https://EXAMPLE.org/source"),
                                            source(origin="food",reading="b"*64)])])])
        out=r88.index(p)
        self.assertEqual(out["counts"]["literal_URL_variant_collision_groups"],0)

    def test_two_original_documents_preserved(self):
        out=r88.index(sample([doc(slug="one"),doc(slug="two")]))
        self.assertEqual(out["counts"]["documents"],2)
        self.assertEqual(out["counts"]["citations"],2)

    def test_tool_preserved_separately(self):
        out=r88.index(sample([doc(kind="tool")]))
        self.assertEqual(out["counts"]["tool"],1)
        self.assertEqual(out["counts"]["article"],0)

    def test_uncited_tool_retained(self):
        out=r88.index(sample([doc(kind="tool",references=[])]))
        self.assertEqual(out["counts"]["documents"],1)
        self.assertEqual(out["counts"]["citations"],0)

    def test_unpaired_historical_records_not_discarded(self):
        prior=[{"unabridged":"historical-only"}]
        out=r88.index(sample(unpaired=prior))
        self.assertEqual(out["original_unpaired_historical_reviews_UNABRIDGED"],prior)

    def test_priority_not_claim_support(self):
        self.assertEqual(r88.priority([]),"P4_ROUTINE_HUMAN_REVIEW")
        self.assertNotIn("SAFE",r88.priority(["RANK_SHIFT"]))

    def test_rank_shift_high_work_order_priority(self):
        p=sample([doc(cues=["SAME_SOURCE_ID_HISTORICAL_ADDITION_REMOVAL_RANK_SHIFT_RISK"])])
        self.assertEqual(r88.index(p)["counts"]["P1_provenance_or_context"],1)

    def test_changed_source_metadata_review_priority(self):
        self.assertEqual(r88.priority(["R80_TO_R85_DISTINCT_SOURCE_VARIANTS_DIFFER"]),
                         "P2_SOURCE_IDENTITY_REVIEW")

    def test_repeat_rank_review_priority(self):
        self.assertEqual(r88.priority(["SAME_SOURCE_ID_REPEATED_RANK_IS_NOT_CLAIM_IDENTITY"]),
                         "P3_CITATION_ALIGNMENT_REVIEW")

    def test_formula_injection_quarantine(self):
        for x in ("=2+2","+cmd()","-HYPERLINK(1)"," @SUM(1)"):
            self.assertTrue(r88.excel_safe(x).startswith("'"))

    def test_unicode_literal_source_identity(self):
        s=source(origin="source\u00e9",url="https://example.org/\u00e9")
        out=r88.index(sample([doc(references=[("s",[s])])]))
        row=out["all_distinct_source_variant_review_workorders_NOT_APPROVED"][0]
        self.assertEqual(row["literal_source_origin"],"source\u00e9")

    def test_separate_origins_with_identical_reading_kept(self):
        p=sample([doc(references=[("s",[source(origin="x"),source(origin="y")])])])
        self.assertEqual(r88.index(p)["counts"]["distinct_source_variants"],2)


class Rejects(unittest.TestCase):
    def setUp(self):
        self.p=sample()

    def reject(self,mutate):
        p=deepcopy(self.p)
        mutate(p)
        with self.assertRaises((r88.Gate,KeyError,TypeError,ValueError)):
            r88.index(p)

    def test_forged_publish(self):
        self.reject(lambda p:p.__setitem__("may_publish",True))

    def test_forged_medical_safety(self):
        self.reject(lambda p:p.__setitem__("medical_safety_approved",True))

    def test_forged_source_approval(self):
        self.reject(lambda p:p.__setitem__("human_source_approvals",1))

    def test_false_QD_review_boolean(self):
        self.reject(lambda p:p.__setitem__("independent_QD_approvals",False))

    def test_wrong_issue_number(self):
        self.reject(lambda p:p.__setitem__("issue",135))

    def test_changed_parent_schema(self):
        self.reject(lambda p:p.__setitem__("schema","wrong"))

    def test_missing_source_variant_edge(self):
        self.reject(lambda p:p["counts"].__setitem__("source_variant_edges",0))

    def test_missing_citation_occurrence(self):
        self.reject(lambda p:p["counts"].__setitem__("citations",0))

    def test_missing_full_DOM_block(self):
        self.reject(lambda p:p["counts"].__setitem__("blocks",0))

    def test_missing_all_citation_rows(self):
        self.reject(lambda p:p["all_41_rank_ambiguity_review_packets_NOT_APPROVED"][0]
                    ["all_original_citation_and_claim_context_reviews_NOT_APPROVED"].clear())

    def test_forged_human_claim_support(self):
        self.reject(lambda p:p["all_41_rank_ambiguity_review_packets_NOT_APPROVED"][0]
                    ["all_original_citation_and_claim_context_reviews_NOT_APPROVED"][0]
                    .__setitem__("human_claim_support","PASS"))

    def test_forged_rank_proves_same_claim(self):
        self.reject(lambda p:p["all_41_rank_ambiguity_review_packets_NOT_APPROVED"][0]
                    ["all_original_citation_and_claim_context_reviews_NOT_APPROVED"][0]
                    .__setitem__("rank_alignment_proves_claim_identity",True))

    def test_mutated_original_block_text(self):
        self.reject(lambda p:p["all_41_rank_ambiguity_review_packets_NOT_APPROVED"][0]
                    ["R86_complete_document_UNABRIDGED_NOT_APPROVED"]
                    ["R80_complete_original_document_UNABRIDGED_NOT_APPROVED"]
                    ["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"][0]
                    .__setitem__("unabridged_DOM_text_NOT_REVIEWED","tampered"))

    def test_wrong_source_ID_link(self):
        self.reject(lambda p:p["all_41_rank_ambiguity_review_packets_NOT_APPROVED"][0]
                    ["all_original_citation_and_claim_context_reviews_NOT_APPROVED"][0]
                    ["R86_original_citation_bridge_UNABRIDGED_NOT_APPROVED"]
                    ["R80_original_citation_UNABRIDGED_NOT_APPROVED"]
                    .__setitem__("raw_source_id","replaced"))

    def test_source_variant_collapsed_to_duplicate(self):
        self.reject(lambda p:p["all_41_rank_ambiguity_review_packets_NOT_APPROVED"][0]
                    ["all_original_citation_and_claim_context_reviews_NOT_APPROVED"][0]
                    ["R86_original_citation_bridge_UNABRIDGED_NOT_APPROVED"]
                    ["R80_original_citation_UNABRIDGED_NOT_APPROVED"]
                    ["source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT"].append(source()))

    def test_corrupted_citation_review_cue(self):
        self.reject(lambda p:p["all_41_rank_ambiguity_review_packets_NOT_APPROVED"][0]
                    ["all_original_citation_and_claim_context_reviews_NOT_APPROVED"][0]
                    ["review_cues_NOT_VERDICTS"].append(123))

    def test_duplicate_document_identity(self):
        with self.assertRaises(r88.Gate):
            r88.index(sample([doc(),doc()]))

    def test_duplicate_citation_ordinal(self):
        d=doc(references=[("s",[source()]),("s",[source()])])
        d["all_original_citation_and_claim_context_reviews_NOT_APPROVED"][1][
            "R86_original_citation_bridge_UNABRIDGED_NOT_APPROVED"][
            "R80_original_citation_UNABRIDGED_NOT_APPROVED"]["citation_ordinal"]=1
        with self.assertRaises(r88.Gate):
            r88.index(sample([d]))


# 24 distinct synthetic literal-URL/origin/reading permutations, each tests
# full original custody without URL aliasing or claiming an emergency verdict.
for i in range(24):
    def factory(n):
        def check(self):
            url="https://example.org/source/"+str(n)+"?case="+str(n)
            s=source(origin="origin-"+str(n),url=url,reading=format(n,"064x"))
            out=r88.index(sample([doc(references=[("s",[s])])]))
            x=out["all_distinct_source_variant_review_workorders_NOT_APPROVED"][0]
            self.assertEqual(x["literal_source_origin"],"origin-"+str(n))
            self.assertEqual(x["exact_URL_NOT_CANONICALIZED_NOT_VERIFIED"],url)
            self.assertFalse(x["claim_support_approved"])
            self.assertFalse(x["qualified_safety_approved"])
        return check
    setattr(Invariants,"test_literal_source_variant_%02d"%i,factory(i))

if __name__=="__main__":
    unittest.main()
