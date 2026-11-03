"""R89 private full-claim-source-dossier tests. Synthetic fixtures live in memory.

No repository file writes, temporary source fragments, network, CMS or publication.
"""
from __future__ import annotations
from copy import deepcopy
import csv
import hashlib
import importlib.util
import io
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]


def load(stem):
    path=ROOT/"tools"/(stem+".py")
    spec=importlib.util.spec_from_file_location("r89_test_"+stem,path)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


r88=load("r88_source_reuse_review_workorders")
r89=load("r89_full_claim_block_source_dossiers")
R=r89.REVIEW


def source(origin="water",sid="s",url="https://example.org/source",reading="a"*64):
    return {"source_origin":origin,"source_id":sid,
            "complete_source_reading_sha256":reading,
            "exact_URL_NOT_CANONICALIZED":url}


def doc(slug="one",kind="article",references=None,text=None,cues=None):
    if references is None:
        references=[("s",[source()])]
    if text is None:
        text="Never use unverified synthetic advice. {{cite:s}} Only test in memory."
    b={"block_id":"block-001",
       "DOM_text_sha256":hashlib.sha256(text.encode("utf-8")).hexdigest(),
       "unabridged_DOM_text_NOT_REVIEWED":text,
       "human_claim_support_review":R,"qualified_safety_review":R}
    reviews=[]
    for n,(sid,variants) in enumerate(references,1):
        c={"raw_source_id":sid,"citation_ordinal":n,
           "source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT":deepcopy(variants)}
        bridge={"R80_original_citation_UNABRIDGED_NOT_APPROVED":c,
                "R80_original_block_id":"block-001",
                "R85_original_four_stage_impact_UNABRIDGED_NOT_APPROVED":None}
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


def sealed(docs=None,unpaired=None):
    report=r88.index(sample(docs,unpaired))
    report["sha256_seal"]=r88.digest(report)
    return report


def ancestor_doc(p):
    return p["complete_R87_original_evidence_UNABRIDGED_NOT_APPROVED"][
        "all_41_rank_ambiguity_review_packets_NOT_APPROVED"][0]


def first_review(p):
    return ancestor_doc(p)["all_original_citation_and_claim_context_reviews_NOT_APPROVED"][0]


def original_block(p):
    return ancestor_doc(p)["R86_complete_document_UNABRIDGED_NOT_APPROVED"][
        "R80_complete_original_document_UNABRIDGED_NOT_APPROVED"][
        "all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"][0]


def first_cite(p):
    return first_review(p)["R86_original_citation_bridge_UNABRIDGED_NOT_APPROVED"][
        "R80_original_citation_UNABRIDGED_NOT_APPROVED"]


def historical(before,after):
    return {"R83_complete_unabridged_current_to_RC_review":{
        "before_FULL_ANCHOR":
            None if before is None else {"complete_container_text_UNABRIDGED":before},
        "after_FULL_ANCHOR":
            None if after is None else {"complete_container_text_UNABRIDGED":after}}}


class Dossiers(unittest.TestCase):
    def setUp(self):
        self.p=sealed()
        self.output=r89.index(self.p)
        self.row=self.output["all_literal_citation_claim_contexts_UNABRIDGED_NOT_APPROVED"][0]

    def test_deterministic_reconstruction(self):
        self.assertEqual(self.output,r89.index(deepcopy(self.p)))

    def test_source_variant_full_context(self):
        group=self.output["all_source_variant_reverse_impact_dossiers_NOT_APPROVED"][0]
        self.assertEqual(group["all_unabridged_cited_claim_blocks_IN_ORIGINAL_ORDER_NOT_REVIEWED"][0],self.row)

    def test_one_original_document(self):
        self.assertEqual(self.output["counts"]["documents"],1)

    def test_original_document_kind(self):
        self.assertEqual(self.output["counts"]["article"],1)

    def test_original_tool_zero(self):
        self.assertEqual(self.output["counts"]["tool"],0)

    def test_full_DOM_conserved(self):
        self.assertEqual(self.output["counts"]["complete_DOM_blocks"],1)

    def test_literal_citation_conserved(self):
        self.assertEqual(self.output["counts"]["citation_occurrences"],1)

    def test_source_edges_conserved(self):
        self.assertEqual(self.output["counts"]["source_variant_edges"],1)

    def test_original_DOM_text_not_cut(self):
        self.assertEqual(self.row["unabridged_original_DOM_text_NOT_REVIEWED"],
                         original_block(self.p)["unabridged_DOM_text_NOT_REVIEWED"])

    def test_original_DOM_text_hash(self):
        self.assertEqual(hashlib.sha256(
            self.row["unabridged_original_DOM_text_NOT_REVIEWED"].encode()).hexdigest(),
            self.row["original_DOM_text_sha256"])

    def test_original_parent_unabridged(self):
        self.assertEqual(self.output[
            "complete_R88_original_evidence_UNABRIDGED_NOT_APPROVED"],self.p)

    def test_private_only(self):
        self.assertIs(self.row["may_publish"],False)
        self.assertIs(self.output["may_publish"],False)

    def test_no_medical_safety_approval(self):
        self.assertIs(self.output["medical_safety_approved"],False)

    def test_no_source_approval(self):
        self.assertEqual(self.output["human_source_approvals"],0)

    def test_no_qualified_safety_approval(self):
        self.assertEqual(self.output["qualified_safety_approvals"],0)

    def test_no_independent_QD_approval(self):
        self.assertEqual(self.output["independent_QD_approvals"],0)

    def test_no_claim_support_inference(self):
        self.assertEqual(self.row["human_claim_support"],R)

    def test_source_URL_retained_literal(self):
        self.assertEqual(self.output["all_source_variant_reverse_impact_dossiers_NOT_APPROVED"][0][
            "exact_URL_NOT_CANONICALIZED_NOT_VERIFIED"],"https://example.org/source")

    def test_source_reading_sha_retained(self):
        self.assertEqual(self.output["all_source_variant_reverse_impact_dossiers_NOT_APPROVED"][0][
            "complete_source_reading_sha256"],"a"*64)

    def test_raw_source_origin_retained(self):
        self.assertEqual(self.output["all_source_variant_reverse_impact_dossiers_NOT_APPROVED"][0][
            "literal_source_origin"],"water")

    def test_citation_ordinal_retained(self):
        self.assertEqual(self.row["citation_ordinal"],1)

    def test_original_citation_token_present(self):
        self.assertNotIn("LITERAL_CITATION_TOKEN_NOT_IN_ORIGINAL_DOM_TEXT_REVIEW_CONTEXT",
                         self.row["review_cues_NOT_VERDICTS"])

    def test_original_citation_token_absence_triggers_review(self):
        out=r89.index(sealed([doc(text="A synthetic text without a citation.")]))
        self.assertIn("LITERAL_CITATION_TOKEN_NOT_IN_ORIGINAL_DOM_TEXT_REVIEW_CONTEXT",
                      out["all_literal_citation_claim_contexts_UNABRIDGED_NOT_APPROVED"][0][
                          "review_cues_NOT_VERDICTS"])

    def test_literal_qualifier_terms(self):
        self.assertIn("never",r89.qualifiers("Never make a recommendation."))

    def test_unicode_qualifier_casefold(self):
        self.assertEqual(r89.qualifiers("NEVER, Never."),["never"])

    def test_quantity_lexical_review(self):
        out=r89.index(sealed([doc(text="Use 5 liters? No; purely a test. {{cite:s}}")]))
        self.assertIn("NUMBER_OR_UNIT_IN_CITED_BLOCK_LEXICAL_REVIEW_ONLY",
                      out["all_literal_citation_claim_contexts_UNABRIDGED_NOT_APPROVED"][0][
                          "review_cues_NOT_VERDICTS"])

    def test_no_quantity_flag_on_plain_text(self):
        self.assertNotIn("NUMBER_OR_UNIT_IN_CITED_BLOCK_LEXICAL_REVIEW_ONLY",
                         self.row["review_cues_NOT_VERDICTS"])

    def test_duplicate_citations_same_source_separately_retained(self):
        out=r89.index(sealed([doc(references=[("s",[source()]),("s",[source()])])]))
        self.assertEqual(out["counts"]["citation_occurrences"],2)
        self.assertEqual(len(out["all_source_variant_reverse_impact_dossiers_NOT_APPROVED"][0][
            "all_unabridged_cited_claim_blocks_IN_ORIGINAL_ORDER_NOT_REVIEWED"]),2)
        self.assertEqual(out["counts"]["multi_citation_DOM_blocks"],1)

    def test_two_distinct_origin_source_variants(self):
        out=r89.index(sealed([doc(references=[("s",[
            source(origin="alpha"),source(origin="beta",reading="b"*64)])])]))
        self.assertEqual(out["counts"]["distinct_source_variants"],2)
        self.assertEqual(out["counts"]["source_variant_edges"],2)

    def test_same_URL_different_variants_not_merged(self):
        out=r89.index(sealed([doc(references=[("s",[
            source(),source(origin="different",reading="b"*64)])])]))
        self.assertEqual(out["counts"]["literal_URL_variant_collision_groups"],1)
        self.assertEqual(len(out["all_source_variant_reverse_impact_dossiers_NOT_APPROVED"]),2)

    def test_cross_document_same_source_retains_separate_claims(self):
        out=r89.index(sealed([doc(slug="a"),doc(slug="b")]))
        self.assertEqual(out["counts"]["documents"],2)
        self.assertEqual(out["counts"]["distinct_source_variants"],1)
        self.assertEqual(len(out["all_source_variant_reverse_impact_dossiers_NOT_APPROVED"][0][
            "all_unabridged_cited_claim_blocks_IN_ORIGINAL_ORDER_NOT_REVIEWED"]),2)

    def test_uncited_tool_retains_DOM(self):
        out=r89.index(sealed([doc(slug="printable",kind="tool",references=[])]))
        self.assertEqual(out["counts"]["tool"],1)
        self.assertEqual(out["counts"]["citation_occurrences"],0)
        self.assertEqual(out["counts"]["complete_DOM_blocks"],1)

    def test_unpaired_historical_evidence_preserved(self):
        unpaired=[{"historical":"a complete record"}]
        out=r89.index(sealed(unpaired=unpaired))
        self.assertEqual(out["unpaired_historical_reviews_UNABRIDGED"],unpaired)

    def test_changes_in_qualifier_are_review_only(self):
        d=doc()
        d["all_original_citation_and_claim_context_reviews_NOT_APPROVED"][0][
            "R86_original_citation_bridge_UNABRIDGED_NOT_APPROVED"][
            "R85_original_four_stage_impact_UNABRIDGED_NOT_APPROVED"]=historical(
                "Never attempt this without an expert.", "Try this with an expert.")
        out=r89.index(sealed([d]))
        row=out["all_literal_citation_claim_contexts_UNABRIDGED_NOT_APPROVED"][0]
        self.assertIn("never",row["lexical_qualifiers_lost_NOT_SAFETY_VERDICT"])
        self.assertIn("HISTORICAL_QUALIFIER_LEXICAL_DELTA_REQUIRES_HUMAN_SCOPE_REVIEW",
                      row["review_cues_NOT_VERDICTS"])
        self.assertEqual(row["human_claim_support"],R)

    def test_gained_qualifier_not_approval(self):
        d=doc()
        d["all_original_citation_and_claim_context_reviews_NOT_APPROVED"][0][
            "R86_original_citation_bridge_UNABRIDGED_NOT_APPROVED"][
            "R85_original_four_stage_impact_UNABRIDGED_NOT_APPROVED"]=historical(
                "Try this.", "Never try this.")
        row=r89.index(sealed([d]))[
            "all_literal_citation_claim_contexts_UNABRIDGED_NOT_APPROVED"][0]
        self.assertIn("never",row["lexical_qualifiers_gained_NOT_SAFETY_VERDICT"])
        self.assertEqual(row["qualified_safety_review"],R)

    def test_historical_missing_side_not_invented(self):
        d=doc()
        d["all_original_citation_and_claim_context_reviews_NOT_APPROVED"][0][
            "R86_original_citation_bridge_UNABRIDGED_NOT_APPROVED"][
            "R85_original_four_stage_impact_UNABRIDGED_NOT_APPROVED"]=historical(
                None,"Never do this.")
        row=r89.index(sealed([d]))[
            "all_literal_citation_claim_contexts_UNABRIDGED_NOT_APPROVED"][0]
        self.assertIsNone(row["historical_before_claim_container_UNABRIDGED_OR_NONE"])
        self.assertEqual(row["lexical_qualifiers_gained_NOT_SAFETY_VERDICT"],[])

    def test_private_route_case_collision(self):
        p=sealed([doc(slug="a"),doc(slug="b")])
        p["all_41_document_workorder_headers_NOT_APPROVED"][1][
            "private_route_NOT_PUBLISHED"]="/preparedness/A/"
        original=p["complete_R87_original_evidence_UNABRIDGED_NOT_APPROVED"][
            "all_41_rank_ambiguity_review_packets_NOT_APPROVED"][1][
            "R86_complete_document_UNABRIDGED_NOT_APPROVED"]
        original["private_draft_url_NOT_PUBLISHED"]="/preparedness/A/"
        p["sha256_seal"]=r89.digest({k:v for k,v in p.items() if k!="sha256_seal"})
        with self.assertRaises(r89.Gate):
            r89.index(p)

    def test_route_unicode_collision_key(self):
        self.assertEqual(r89.route_collision_key("/preparedness/%61/"),
                         r89.route_collision_key("/preparedness/A/"))

    def test_route_traversal_denied(self):
        with self.assertRaises(r89.Gate):
            r89.route_collision_key("/preparedness/a/../b/")

    def test_route_query_denied(self):
        with self.assertRaises(r89.Gate):
            r89.route_collision_key("/preparedness/a/?draft=1")

    def test_route_anchor_denied(self):
        with self.assertRaises(r89.Gate):
            r89.route_collision_key("/preparedness/a/#section")

    def test_route_not_public(self):
        with self.assertRaises(r89.Gate):
            r89.route_collision_key("https://finalvestige.com/preparedness/a/")

    def test_no_rewrite_of_literal_source_url(self):
        out=r89.index(sealed([doc(references=[("s",[
            source(url="https://EXAMPLE.org/%61")])])]))
        self.assertEqual(out["all_source_variant_reverse_impact_dossiers_NOT_APPROVED"][0][
            "exact_URL_NOT_CANONICALIZED_NOT_VERIFIED"],"https://EXAMPLE.org/%61")

    def test_sealed_parent_required(self):
        p=deepcopy(self.p)
        p["sha256_seal"]="0"*64
        with self.assertRaises(r89.Gate):
            r89.index(p)

    def test_invalid_approval_bool_as_int_rejected(self):
        p=deepcopy(self.p)
        p["human_source_approvals"]=False
        p["sha256_seal"]=r89.digest({k:v for k,v in p.items() if k!="sha256_seal"})
        with self.assertRaises(r89.Gate):
            r89.index(p)


class SyntheticMutationRejection(unittest.TestCase):
    """Independent mutations reseal R88; deeper crosswalk still must reject."""
    def setUp(self):
        self.p=sealed()

    def reject(self,mutator):
        p=deepcopy(self.p)
        mutator(p)
        p["sha256_seal"]=r89.digest({k:v for k,v in p.items() if k!="sha256_seal"})
        with self.assertRaises((r89.Gate,KeyError,TypeError,ValueError)):
            r89.index(p)


def add_mutation_test(name, mutation):
    def test(self):
        self.reject(mutation)
    setattr(SyntheticMutationRejection,"test_reject_"+name,test)


MUTATIONS={
    "top_publish":lambda p:p.__setitem__("may_publish",True),
    "top_medical":lambda p:p.__setitem__("medical_safety_approved",True),
    "top_issue":lambda p:p.__setitem__("issue",135),
    "top_schema":lambda p:p.__setitem__("schema","changed"),
    "top_state":lambda p:p.__setitem__("release_state","PASS"),
    "top_source_approval":lambda p:p.__setitem__("human_source_approvals",1),
    "top_claim_approval":lambda p:p.__setitem__("human_claim_approvals",1),
    "top_safety_approval":lambda p:p.__setitem__("qualified_safety_approvals",1),
    "top_QD_approval":lambda p:p.__setitem__("independent_QD_approvals",1),
    "missing_headers":lambda p:p["all_41_document_workorder_headers_NOT_APPROVED"].clear(),
    "missing_citations":lambda p:p["all_literal_citation_occurrence_workorders_NOT_APPROVED"].clear(),
    "missing_variants":lambda p:p["all_distinct_source_variant_review_workorders_NOT_APPROVED"].clear(),
    "missing_orig_docs":lambda p:p["complete_R87_original_evidence_UNABRIDGED_NOT_APPROVED"][
        "all_41_rank_ambiguity_review_packets_NOT_APPROVED"].clear(),
    "header_false_claim":lambda p:p["all_41_document_workorder_headers_NOT_APPROVED"][0].__setitem__(
        "human_claim_review","PASS"),
    "header_published":lambda p:p["all_41_document_workorder_headers_NOT_APPROVED"][0].__setitem__(
        "may_publish",True),
    "header_block_count":lambda p:p["all_41_document_workorder_headers_NOT_APPROVED"][0].__setitem__(
        "unabridged_original_DOM_blocks",3),
    "header_wrong_route":lambda p:p["all_41_document_workorder_headers_NOT_APPROVED"][0].__setitem__(
        "private_route_NOT_PUBLISHED","/preparedness/other/"),
    "header_wrong_citation_count":lambda p:p["all_41_document_workorder_headers_NOT_APPROVED"][0].__setitem__(
        "citation_occurrences",10),
    "citation_ordinal_changed":lambda p:p["all_literal_citation_occurrence_workorders_NOT_APPROVED"][0].__setitem__(
        "citation_ordinal",9),
    "citation_source_changed":lambda p:p["all_literal_citation_occurrence_workorders_NOT_APPROVED"][0].__setitem__(
        "literal_source_ID","fake"),
    "citation_block_changed":lambda p:p["all_literal_citation_occurrence_workorders_NOT_APPROVED"][0].__setitem__(
        "original_DOM_block_ID","wrong"),
    "citation_DOM_hash_changed":lambda p:p["all_literal_citation_occurrence_workorders_NOT_APPROVED"][0].__setitem__(
        "original_DOM_text_sha256","a"*64),
    "citation_source_keys_removed":lambda p:p["all_literal_citation_occurrence_workorders_NOT_APPROVED"][0][
        "distinct_source_variant_keys_NOT_ALIASES"].clear(),
    "citation_false_support":lambda p:p["all_literal_citation_occurrence_workorders_NOT_APPROVED"][0].__setitem__(
        "human_claim_support","PASS"),
    "citation_false_safety":lambda p:p["all_literal_citation_occurrence_workorders_NOT_APPROVED"][0].__setitem__(
        "qualified_safety_review","PASS"),
    "citation_false_publish":lambda p:p["all_literal_citation_occurrence_workorders_NOT_APPROVED"][0].__setitem__(
        "may_publish",True),
    "source_fake_sha":lambda p:p["all_distinct_source_variant_review_workorders_NOT_APPROVED"][0].__setitem__(
        "variant_key_sha256","a"*64),
    "source_url_changed":lambda p:p["all_distinct_source_variant_review_workorders_NOT_APPROVED"][0].__setitem__(
        "exact_URL_NOT_CANONICALIZED_NOT_VERIFIED","https://fake.example"),
    "source_reading_changed":lambda p:p["all_distinct_source_variant_review_workorders_NOT_APPROVED"][0].__setitem__(
        "complete_source_reading_sha256","b"*64),
    "source_origin_changed":lambda p:p["all_distinct_source_variant_review_workorders_NOT_APPROVED"][0].__setitem__(
        "literal_source_origin","invented"),
    "source_forged_support":lambda p:p["all_distinct_source_variant_review_workorders_NOT_APPROVED"][0].__setitem__(
        "claim_support_approved",True),
    "source_forged_safety":lambda p:p["all_distinct_source_variant_review_workorders_NOT_APPROVED"][0].__setitem__(
        "qualified_safety_approved",True),
    "source_forged_review":lambda p:p["all_distinct_source_variant_review_workorders_NOT_APPROVED"][0].__setitem__(
        "human_source_review","APPROVED"),
    "source_occurrence_loss":lambda p:p["all_distinct_source_variant_review_workorders_NOT_APPROVED"][0][
        "separate_citation_occurrences"].clear(),
    "original_text_changed":lambda p:original_block(p).__setitem__(
        "unabridged_DOM_text_NOT_REVIEWED","tampered original"),
    "original_hash_changed":lambda p:original_block(p).__setitem__(
        "DOM_text_sha256","0"*64),
    "original_review_forged":lambda p:original_block(p).__setitem__(
        "human_claim_support_review","PASS"),
    "original_safety_forged":lambda p:original_block(p).__setitem__(
        "qualified_safety_review","PASS"),
    "original_cite_ID_changed":lambda p:first_cite(p).__setitem__(
        "raw_source_id","fake"),
    "original_cite_ordinal_changed":lambda p:first_cite(p).__setitem__(
        "citation_ordinal",99),
    "original_citation_removed":lambda p:ancestor_doc(p)[
        "all_original_citation_and_claim_context_reviews_NOT_APPROVED"].clear(),
    "original_citation_forged":lambda p:first_review(p).__setitem__(
        "human_claim_support","PASS"),
    "original_safety_forged":lambda p:first_review(p).__setitem__(
        "qualified_safety_review","PASS"),
    "original_rank_forged":lambda p:first_review(p).__setitem__(
        "rank_alignment_proves_claim_identity",True),
    "original_block_ID_changed":lambda p:original_block(p).__setitem__(
        "block_id","changed"),
    "original_reading_order_changed":lambda p:ancestor_doc(p)[
        "R86_complete_document_UNABRIDGED_NOT_APPROVED"][
        "R80_complete_original_document_UNABRIDGED_NOT_APPROVED"][
        "original_DOM_block_ids_in_reading_order"].clear(),
}
for _name,_mutation in MUTATIONS.items():
    add_mutation_test(_name,_mutation)


if __name__=="__main__":
    unittest.main()
