"""R71 private DOM-block / citation / unabridged source custody adversarial tests.

Synthetic data only. Do not read or write production preparedness source files,
create reviewers, hit URLs, trigger WordPress, or grant editorial/safety approval.
"""
from __future__ import annotations

from copy import deepcopy
import csv
import importlib.util
import io
from pathlib import Path
import unittest

FILE=Path(__file__).resolve().parents[1]/"tools"/"r71_rc_dom_block_source_review.py"
spec=importlib.util.spec_from_file_location("r71_under_test", FILE)
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
N=(1,1,3,3)


def seal(item):
    item.pop("fingerprint_sha256",None)
    item["fingerprint_sha256"]=gate.digest(item)
    return item


def reseal(dom,urls):
    for doc in dom["all_document_DOM_text_and_citation_review_orders_NOT_APPROVED"]:
        doc["task_sha256"]=gate.digest({
            k:v for k,v in doc.items() if k!="task_sha256"})
    seal(dom)
    urls["R69_DOM_citation_context_fingerprint_sha256"]=dom["fingerprint_sha256"]
    seal(urls)
    return dom,urls


def fake_source(origin,sid,title,url):
    reading={"id":sid,"title":title,"url":url,"publisher":"Synthetic",
             "human_link_check":False,
             "supports":"Full synthetic evidence notes preserved without omission."}
    return {
        "source_origin":origin,"source_id":sid,
        "candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED":reading,
        "original_reading_UNABRIDGED_NOT_HUMAN_VERIFIED":None,
        "original_record_sha256":None,
        "source_record_sha256":gate.digest(reading),
        "exact_URL_NO_CANONICAL_ALIAS":url,
        "URL_structural_blockers_NOT_HTTP_VERDICT":[],
        "URL_manual_review_signals_NOT_VERDICT":[],
        "human_link_review":"NOT_REVIEWED",
        "human_claim_support_review":"NOT_REVIEWED",
        "qualified_safety_review":"NOT_REVIEWED",
    }


def block(bid,tag,text,offsets,at):
    topics=gate.signals(text)
    flags=(["TOPIC_SIGNAL_WITH_NO_CITATION_IN_THIS_DOM_BLOCK_REVIEW_CONTEXT"]
           if topics and not offsets else
           ["TOPIC_SIGNAL_WITH_CITATION_NOT_CLAIM_SUPPORT_PROOF"]
           if topics else [])
    return {
        "block_id":bid,"html_tag":tag,"html_element_id_OR_NULL":None,
        "start_offset_codepoints":at,
        "DOM_TEXT_UNABRIDGED_NOT_BROWSER_VERIFIED":text,
        "DOM_text_sha256":gate.raw_sha(text),
        "citation_offsets_in_DOM_text":offsets,
        "review_topic_signals_NOT_SAFETY_CLASSIFICATION":topics,
        "review_flags_NOT_SAFETY_VERDICTS":flags,
        "human_claim_support_review":"NOT_REVIEWED",
    }


def doc(kind,slug,blocks,citations):
    row={
        "kind":kind,"slug":slug,
        "proposed_url_PRIVATE_DRAFT_ONLY":"/preparedness/"+kind+"/"+slug+"/",
        "R68_task_sha256":"a"*64,
        "R68_HTML_sha256":"b"*64,
        "full_DOM_text_blocks_UNABRIDGED_NOT_SOURCE_APPROVED":blocks,
        "citation_visibility_audit_NOT_BROWSER_PROOF":citations,
        "human_source_review":"NOT_REVIEWED",
        "qualified_safety_review":"NOT_REVIEWED",
        "independent_QD_review":"NOT_REVIEWED",
    }
    row["task_sha256"]=gate.digest(row)
    return row


def r69_citation(ordinal,sid,offset,bid,variants,preferred):
    return {
        "ordinal":ordinal,"source_id":sid,
        "unicode_codepoint_offset":offset,
        "literal_token":"{{cite:"+sid+"}}",
        "nearest_HTML_text_block_id_OR_NULL":bid,
        "DOM_CLASSIFICATION_NOT_BROWSER_PROOF":
            "DOM_TEXT_POTENTIALLY_VISIBLE_NOT_BROWSER_VERIFIED",
        "candidate_source_identity_OR_NULL":preferred,
        "all_source_identity_variants_NOT_ALIASED":variants,
        "human_claim_support_review":"NOT_REVIEWED",
    }


def r70_citation(kind,slug,ordinal,sid,offset,variants,urls,preferred):
    return {
        "kind":kind,"slug":slug,"draft_url":"/preparedness/"+kind+"/"+slug+"/",
        "citation_ordinal":ordinal,"source_id":sid,
        "unicode_codepoint_offset":offset,
        "DOM_visibility_NOT_BROWSER_VERIFIED":
            "DOM_TEXT_POTENTIALLY_VISIBLE_NOT_BROWSER_VERIFIED",
        "all_candidate_origin_scoped_identities_NOT_ALIASED":variants,
        "all_candidate_exact_urls_NOT_DEDUPLICATED":urls,
        "preferred_candidate_identity_NOT_APPROVED":preferred,
        "URL_structural_blockers_NOT_SOURCE_VERDICT":[],
        "human_claim_support_review":"NOT_REVIEWED",
        "qualified_safety_review":"NOT_REVIEWED",
    }


def fixture():
    shared="https://www.example.org/alpha"
    sources=[
        fake_source("start","alpha","Primary synthetic alpha",shared),
        fake_source("food","alpha","Separate synthetic alpha",shared),
        fake_source("start","beta","Synthetic beta","https://www.example.org/beta"),
    ]
    a=[["food","alpha"],["start","alpha"]]
    b=[["start","beta"]]
    domdocs=[
        doc("article","first",[
            block("block-1","h2","Medication backup",[],10),
            block("block-2","p","Ask a pharmacist {{cite:alpha}}",[100],100),
            block("block-3","p","Check water safety {{cite:alpha}}",[200],200),
        ],[
            r69_citation(1,"alpha",100,"block-2",a,["start","alpha"]),
            r69_citation(2,"alpha",200,"block-3",a,["start","alpha"]),
        ]),
        doc("tool","planner",[
            block("block-1","p","Check water {{cite:beta}}",[50],10),
        ],[
            r69_citation(1,"beta",50,"block-1",b,["start","beta"]),
        ]),
    ]
    dom=seal({
        "schema":gate.R69_SCHEMA,"issue":136,"release_state":"HOLD",
        "machine_only":True,
        "counts":{"candidate_articles":1,"candidate_tools":1,
                  "candidate_source_records_kept_in_R68":3,
                  "candidate_citation_occurrences_accounted_for":3,
                  "review_topic_blocks_without_same_block_citation":1,
                  "human_claim_or_safety_checks_performed_BY_R69":0},
        "all_document_DOM_text_and_citation_review_orders_NOT_APPROVED":domdocs,
        **{k:False for k in gate.HOLD}
    })
    cites=[
        r70_citation("article","first",1,"alpha",100,a,[shared,shared],["start","alpha"]),
        r70_citation("article","first",2,"alpha",200,a,[shared,shared],["start","alpha"]),
        r70_citation("tool","planner",1,"beta",50,b,["https://www.example.org/beta"],
                     ["start","beta"]),
    ]
    urls=seal({
        "schema":gate.R70_SCHEMA,"issue":136,"release_state":"HOLD",
        "machine_only":True,"R69_DOM_citation_context_fingerprint_sha256":
            dom["fingerprint_sha256"],
        "counts":{"candidate_articles":1,"candidate_tools":1,
                  "source_records_conserved":3,"citation_occurrences_conserved":3,
                  "human_url_or_claim_checks_performed_BY_R70":0},
        "all_244_source_URL_and_reading_work_orders_NOT_APPROVED":sources,
        "all_2173_citation_URL_identity_work_orders_NOT_APPROVED":cites,
        **{k:False for k in gate.HOLD}
    })
    return dom,urls


def produce(data=None):
    return gate.construct(*(data or fixture()),expected=N)


def mutate(fault):
    items=deepcopy(fixture())
    fault(*items)
    return reseal(*items)


class R71ConservationTests(unittest.TestCase):
    def test_baseline_census(self):
        report=produce()
        self.assertEqual(report["counts"]["candidate_citations_conserved"],3)
        self.assertEqual(report["counts"]["unabridged_source_readings_conserved"],3)
        self.assertEqual(report["counts"]["DOM_text_blocks_review_tasks"],4)
        self.assertEqual(report["counts"]["citation_occurrences_attached_to_DOM_blocks"],3)

    def test_without_same_block_citation_is_not_declared_unsafe(self):
        report=produce()
        row=report["all_DOM_block_claim_and_exact_source_review_tasks_NOT_APPROVED"][0]
        self.assertEqual(row["triage_bucket_NOT_SAFETY_VERDICT"],
                         "TOPIC_NO_SAME_BLOCK_CITATION_REVIEW")
        self.assertEqual(row["local_citations_NOT_CLAIM_SUPPORT_PROOF"],[])
        self.assertTrue(row["adjacent_citations_NAVIGATION_HINTS_NOT_SUPPORT"])
        self.assertEqual(row["qualified_safety_review"],"NOT_REVIEWED")

    def test_same_block_citation_is_not_automatic_support(self):
        row=produce()["all_DOM_block_claim_and_exact_source_review_tasks_NOT_APPROVED"][1]
        self.assertEqual(row["triage_bucket_NOT_SAFETY_VERDICT"],
                         "TOPIC_HAS_CITATION_SUPPORT_STILL_UNVERIFIED")
        self.assertEqual(row["human_claim_support_review"],"NOT_REVIEWED")

    def test_duplicate_exact_url_keeps_two_readings(self):
        report=produce()
        edges=report["all_DOM_block_claim_and_exact_source_review_tasks_NOT_APPROVED"][1][
            "local_citations_NOT_CLAIM_SUPPORT_PROOF"][0][
            "origin_scoped_source_variants_NOT_ALIASED"]
        self.assertEqual([x["source_origin"] for x in edges],["food","start"])
        self.assertEqual(edges[0]["exact_URL_NOT_ALIAS"],edges[1]["exact_URL_NOT_ALIAS"])
        self.assertNotEqual(edges[0]["complete_source_reading_sha256"],
                            edges[1]["complete_source_reading_sha256"])

    def test_uncited_source_remains_conserved(self):
        dom,urls=fixture()
        citation=urls["all_2173_citation_URL_identity_work_orders_NOT_APPROVED"][2]
        self.assertEqual(citation["source_id"],"beta")
        report=produce((dom,urls))
        self.assertEqual(len(report[
            "all_244_unabridged_source_reading_review_records_NOT_APPROVED"]),3)

    def test_reverse_custody_keeps_each_source_id_variant(self):
        r=produce()
        reverse=r["source_to_cited_block_reverse_custody_NOT_APPROVED"]
        self.assertEqual(len(reverse),3)
        self.assertEqual(sorted((x["source_origin"],x["source_id"])
                                for x in reverse),
                         [("food","alpha"),("start","alpha"),("start","beta")])

    def test_report_fingerprint(self):
        r=produce()
        gate.sealed(r,gate.SCHEMA)
        self.assertEqual(r["fingerprint_sha256"],
                         gate.digest({k:v for k,v in r.items()
                                      if k!="fingerprint_sha256"}))

    def test_no_authority_flags(self):
        r=produce()
        self.assertEqual(r["release_state"],"HOLD")
        self.assertTrue(r["machine_only"])
        self.assertTrue(all(r[x] is False for x in gate.HOLD))
        self.assertEqual(r["counts"]["human_source_claim_or_safety_reviews_by_R71"],0)

    def test_deterministic(self):
        self.assertEqual(produce(),produce())

    def test_csv_preserves_unabridged_block_text(self):
        r=produce()
        rows=list(csv.DictReader(io.StringIO(gate.csv_tasks(r))))
        self.assertEqual(len(rows),4)
        self.assertEqual(rows[0]["unabridged_DOM_text_NOT_VERIFIED"],
                         "Medication backup")
        self.assertTrue(all(row["human_claim_support_NOT_REVIEWED"]=="NOT_REVIEWED"
                            for row in rows))

    def test_csv_formula_neutralization(self):
        dom,urls=fixture()
        b=dom["all_document_DOM_text_and_citation_review_orders_NOT_APPROVED"][0][
            "full_DOM_text_blocks_UNABRIDGED_NOT_SOURCE_APPROVED"][0]
        b["DOM_TEXT_UNABRIDGED_NOT_BROWSER_VERIFIED"]="=1+1"
        b["DOM_text_sha256"]=gate.raw_sha("=1+1")
        b["review_topic_signals_NOT_SAFETY_CLASSIFICATION"]=[]
        b["review_flags_NOT_SAFETY_VERDICTS"]=[]
        dom["counts"]["review_topic_blocks_without_same_block_citation"]=0
        reseal(dom,urls)
        rows=list(csv.DictReader(io.StringIO(gate.csv_tasks(produce((dom,urls))))))
        self.assertEqual(rows[0]["unabridged_DOM_text_NOT_VERIFIED"],"'=1+1")

    def test_csv_formula_neutralization_in_nonascii(self):
        dom,urls=fixture()
        b=dom["all_document_DOM_text_and_citation_review_orders_NOT_APPROVED"][0][
            "full_DOM_text_blocks_UNABRIDGED_NOT_SOURCE_APPROVED"][0]
        b["DOM_TEXT_UNABRIDGED_NOT_BROWSER_VERIFIED"]="\ufeff @risk"
        b["DOM_text_sha256"]=gate.raw_sha("\ufeff @risk")
        b["review_topic_signals_NOT_SAFETY_CLASSIFICATION"]=[]
        b["review_flags_NOT_SAFETY_VERDICTS"]=[]
        dom["counts"]["review_topic_blocks_without_same_block_citation"]=0
        reseal(dom,urls)
        rows=list(csv.DictReader(io.StringIO(gate.csv_tasks(produce((dom,urls))))))
        self.assertTrue(rows[0]["unabridged_DOM_text_NOT_VERIFIED"].startswith("'"))

    def test_missing_dom_nearest_block_is_quarantined(self):
        dom,urls=fixture()
        d=dom["all_document_DOM_text_and_citation_review_orders_NOT_APPROVED"][0]
        d["citation_visibility_audit_NOT_BROWSER_PROOF"][0][
            "nearest_HTML_text_block_id_OR_NULL"]=None
        d["citation_visibility_audit_NOT_BROWSER_PROOF"][0][
            "DOM_CLASSIFICATION_NOT_BROWSER_PROOF"]="NON_DOM_TEXT_ATTRIBUTE_COMMENT_OR_TOKEN_SPLIT"
        urls["all_2173_citation_URL_identity_work_orders_NOT_APPROVED"][0][
            "DOM_visibility_NOT_BROWSER_VERIFIED"]="NON_DOM_TEXT_ATTRIBUTE_COMMENT_OR_TOKEN_SPLIT"
        b=d["full_DOM_text_blocks_UNABRIDGED_NOT_SOURCE_APPROVED"][1]
        b["DOM_TEXT_UNABRIDGED_NOT_BROWSER_VERIFIED"]="Ask a pharmacist"
        b["DOM_text_sha256"]=gate.raw_sha("Ask a pharmacist")
        b["citation_offsets_in_DOM_text"]=[]
        b["review_flags_NOT_SAFETY_VERDICTS"]=[
            "TOPIC_SIGNAL_WITH_NO_CITATION_IN_THIS_DOM_BLOCK_REVIEW_CONTEXT"]
        dom["counts"]["review_topic_blocks_without_same_block_citation"]=2
        reseal(dom,urls)
        r=produce((dom,urls))
        self.assertEqual(r["counts"]["citations_without_DOM_block_unresolved"],1)
        self.assertEqual(len(r["citations_with_no_DOM_block_NOT_APPROVED"]),1)

    def test_synthetic_nearby_citation_does_not_affect_local_review_state(self):
        r=produce()
        first=r["all_DOM_block_claim_and_exact_source_review_tasks_NOT_APPROVED"][0]
        self.assertEqual(first["human_claim_support_review"],"NOT_REVIEWED")
        hint=first["adjacent_citations_NAVIGATION_HINTS_NOT_SUPPORT"][0]
        self.assertTrue(hint["NOT_EVIDENCE_OF_SUPPORT"])

    def test_immutability_of_inputs(self):
        orig=fixture()
        before=deepcopy(orig)
        produce(orig)
        self.assertEqual(orig,before)

    def test_bad_census_contract(self):
        with self.assertRaises(gate.ReviewHold):
            gate.construct(*fixture(),expected=(1,1,3,-1))

    def test_missing_seal(self):
        dom,urls=fixture()
        del dom["fingerprint_sha256"]
        with self.assertRaises(gate.ReviewHold):
            produce((dom,urls))

    def test_spoofed_approval_at_report_top(self):
        dom,urls=fixture()
        dom["may_publish"]=True
        reseal(dom,urls)
        with self.assertRaises(gate.ReviewHold):
            produce((dom,urls))

    def test_spoofed_report_human_count(self):
        def bad(dom,urls):
            urls["counts"]["human_url_or_claim_checks_performed_BY_R70"]=1
        with self.assertRaises(gate.ReviewHold):
            produce(mutate(bad))


def _doc(dom,i=0):
    return dom["all_document_DOM_text_and_citation_review_orders_NOT_APPROVED"][i]


def _block(dom,i=0,j=0):
    return _doc(dom,i)["full_DOM_text_blocks_UNABRIDGED_NOT_SOURCE_APPROVED"][j]


def _citation(dom,i=0,j=0):
    return _doc(dom,i)["citation_visibility_audit_NOT_BROWSER_PROOF"][j]


def _url_cite(urls,j=0):
    return urls["all_2173_citation_URL_identity_work_orders_NOT_APPROVED"][j]


def _src(urls,j=0):
    return urls["all_244_source_URL_and_reading_work_orders_NOT_APPROVED"][j]


# Each independent mutation is a separate actual unittest. These bypass only
# the synthetic outer SHA checksum, exercising deeper source/citation semantics.
FAULTS={
    "source_modified_unabridged_support":
        lambda d,u:_src(u)["candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"].update(
            supports="changed evidence without new source fingerprint"),
    "source_changed_title":
        lambda d,u:_src(u)["candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"].update(
            title="silently rewritten"),
    "source_changed_exact_url":
        lambda d,u:_src(u)["candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"].update(
            url="https://www.example.com/changed"),
    "source_changed_fingerprint":
        lambda d,u:_src(u).update(source_record_sha256="0"*64),
    "source_changed_origin":
        lambda d,u:_src(u).update(source_origin=""),
    "source_duplicate_origin_id":
        lambda d,u:_src(u,1).update(source_origin="start"),
    "source_fake_link_approval":
        lambda d,u:_src(u).update(human_link_review="APPROVED"),
    "source_fake_claim_approval":
        lambda d,u:_src(u).update(human_claim_support_review="VERIFIED"),
    "source_fake_qualified_review":
        lambda d,u:_src(u).update(qualified_safety_review="SAFE"),
    "source_hidden_human_link_flag":
        lambda d,u:_src(u)["candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"].update(
            human_link_check=True),
    "source_missing_reading":
        lambda d,u:_src(u).pop("candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"),
    "source_non_dict_reading":
        lambda d,u:_src(u).update(candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED=""),
    "source_exact_url_alias":
        lambda d,u:_src(u).update(exact_URL_NO_CANONICAL_ALIAS="https://www.example.com/alias"),
    "citation_duplicate_ordinal":
        lambda d,u:_url_cite(u,1).update(citation_ordinal=1),
    "citation_changed_source_id":
        lambda d,u:_url_cite(u,1).update(source_id="beta"),
    "citation_changed_draft_url":
        lambda d,u:_url_cite(u,1).update(draft_url="/preparedness/other/"),
    "citation_changed_offset":
        lambda d,u:_url_cite(u,1).update(unicode_codepoint_offset=201),
    "citation_changed_visibility":
        lambda d,u:_url_cite(u,1).update(DOM_visibility_NOT_BROWSER_VERIFIED="HIDDEN"),
    "citation_fake_human_claim":
        lambda d,u:_url_cite(u,1).update(human_claim_support_review="APPROVED"),
    "citation_fake_qualified":
        lambda d,u:_url_cite(u,1).update(qualified_safety_review="APPROVED"),
    "citation_variants_removed":
        lambda d,u:_url_cite(u,1).update(
            all_candidate_origin_scoped_identities_NOT_ALIASED=[]),
    "citation_variants_aliased":
        lambda d,u:_url_cite(u,1).update(
            all_candidate_origin_scoped_identities_NOT_ALIASED=[["start","alpha"]]),
    "citation_variants_duplicate":
        lambda d,u:_url_cite(u,1).update(
            all_candidate_origin_scoped_identities_NOT_ALIASED=[
                ["food","alpha"],["food","alpha"]]),
    "citation_variants_reversed":
        lambda d,u:_url_cite(u,1).update(
            all_candidate_origin_scoped_identities_NOT_ALIASED=[
                ["start","alpha"],["food","alpha"]]),
    "citation_variant_malformed":
        lambda d,u:_url_cite(u,1).update(
            all_candidate_origin_scoped_identities_NOT_ALIASED=[["start"]]),
    "citation_variant_missing_source":
        lambda d,u:_url_cite(u,1).update(
            all_candidate_origin_scoped_identities_NOT_ALIASED=[
                ["food","alpha"],["unknown","alpha"]]),
    "citation_variant_url_rewrite":
        lambda d,u:_url_cite(u,1).update(
            all_candidate_exact_urls_NOT_DEDUPLICATED=[
                "https://www.example.com/wrong","https://www.example.org/alpha"]),
    "citation_variant_url_drop":
        lambda d,u:_url_cite(u,1).update(all_candidate_exact_urls_NOT_DEDUPLICATED=[]),
    "citation_wrong_preferred":
        lambda d,u:_url_cite(u,1).update(
            preferred_candidate_identity_NOT_APPROVED=["food","alpha"]),
    "citation_wrong_doc":
        lambda d,u:_url_cite(u,1).update(slug="other"),
    "citation_fake_doc_kind":
        lambda d,u:_url_cite(u,1).update(kind="chapter"),
    "citation_zero_offset":
        lambda d,u:_url_cite(u,1).update(unicode_codepoint_offset=-1),
    "citation_zero_ordinal":
        lambda d,u:_url_cite(u,1).update(citation_ordinal=0),
    "citation_nonint_offset":
        lambda d,u:_url_cite(u,1).update(unicode_codepoint_offset="200"),
    "doc_forged_qd":
        lambda d,u:_doc(d).update(independent_QD_review="PASS"),
    "doc_forged_qualified_review":
        lambda d,u:_doc(d).update(qualified_safety_review="SAFE"),
    "doc_forged_human_source":
        lambda d,u:_doc(d).update(human_source_review="APPROVED"),
    "doc_duplicate_slug":
        lambda d,u:_doc(d,1).update(slug="first",kind="article"),
    "doc_duplicate_url":
        lambda d,u:_doc(d,1).update(
            proposed_url_PRIVATE_DRAFT_ONLY="/preparedness/article/first/"),
    "doc_public_url":
        lambda d,u:_doc(d,1).update(proposed_url_PRIVATE_DRAFT_ONLY="/published/"),
    "doc_empty_slug":
        lambda d,u:_doc(d,1).update(slug=""),
    "doc_missing_blocks":
        lambda d,u:_doc(d,1).pop("full_DOM_text_blocks_UNABRIDGED_NOT_SOURCE_APPROVED"),
    "doc_missing_cites":
        lambda d,u:_doc(d,1).pop("citation_visibility_audit_NOT_BROWSER_PROOF"),
    "doc_fake_kind":
        lambda d,u:_doc(d,1).update(kind="page"),
    "block_unreviewed_spoof":
        lambda d,u:_block(d).update(human_claim_support_review="APPROVED"),
    "block_mutated_text":
        lambda d,u:_block(d).update(DOM_TEXT_UNABRIDGED_NOT_BROWSER_VERIFIED="Water now"),
    "block_mutated_sha":
        lambda d,u:_block(d).update(DOM_text_sha256="f"*64),
    "block_removed_visible_token_with_matching_sha":
        lambda d,u:_block(d,0,1).update(
            DOM_TEXT_UNABRIDGED_NOT_BROWSER_VERIFIED="Ask a pharmacist",
            DOM_text_sha256=gate.raw_sha("Ask a pharmacist")),
    "block_added_phantom_token_with_matching_sha":
        lambda d,u:_block(d).update(
            DOM_TEXT_UNABRIDGED_NOT_BROWSER_VERIFIED="Medication backup {{cite:beta}}",
            DOM_text_sha256=gate.raw_sha("Medication backup {{cite:beta}}")),
    "block_duplicate_id":
        lambda d,u:_block(d,0,1).update(block_id="block-1"),
    "block_missing_id":
        lambda d,u:_block(d).update(block_id=""),
    "block_empty_text":
        lambda d,u:_block(d).update(DOM_TEXT_UNABRIDGED_NOT_BROWSER_VERIFIED=""),
    "block_wrong_topic":
        lambda d,u:_block(d).update(review_topic_signals_NOT_SAFETY_CLASSIFICATION=[]),
    "block_wrong_flag":
        lambda d,u:_block(d).update(review_flags_NOT_SAFETY_VERDICTS=[]),
    "block_wrong_offset":
        lambda d,u:_block(d,0,1).update(citation_offsets_in_DOM_text=[101]),
    "block_duplicate_offsets":
        lambda d,u:_block(d,0,1).update(citation_offsets_in_DOM_text=[100,100]),
    "block_unsorted_offsets":
        lambda d,u:_block(d,0,1).update(citation_offsets_in_DOM_text=[200,100]),
    "block_negative_start":
        lambda d,u:_block(d).update(start_offset_codepoints=-1),
    "block_missing_local_cite":
        lambda d,u:_block(d,0,1).update(citation_offsets_in_DOM_text=[]),
    "r69_citation_changed_source":
        lambda d,u:_citation(d).update(source_id="beta"),
    "r69_citation_changed_ordinal":
        lambda d,u:_citation(d).update(ordinal=3),
    "r69_citation_changed_offset":
        lambda d,u:_citation(d).update(unicode_codepoint_offset=101),
    "r69_citation_unknown_block":
        lambda d,u:_citation(d).update(nearest_HTML_text_block_id_OR_NULL="absent"),
    "r69_citation_visible_but_unanchored":
        lambda d,u:_citation(d).update(nearest_HTML_text_block_id_OR_NULL=None),
    "r69_citation_fake_review":
        lambda d,u:_citation(d).update(human_claim_support_review="SAFE"),
    "r69_citation_variant_collapse":
        lambda d,u:_citation(d).update(all_source_identity_variants_NOT_ALIASED=[
            ["start","alpha"]]),
    "r69_citation_changed_preferred":
        lambda d,u:_citation(d).update(candidate_source_identity_OR_NULL=["food","alpha"]),
    "r69_citation_changed_visibility":
        lambda d,u:_citation(d).update(DOM_CLASSIFICATION_NOT_BROWSER_PROOF="SUPPRESSED"),
    "count_wrong_topic_blocks":
        lambda d,u:d["counts"].update(
            review_topic_blocks_without_same_block_citation=0),
    "count_wrong_total_citations":
        lambda d,u:d["counts"].update(candidate_citation_occurrences_accounted_for=2),
    "count_wrong_sources":
        lambda d,u:u["counts"].update(source_records_conserved=2),
    "count_wrong_tools":
        lambda d,u:u["counts"].update(candidate_tools=2),
}


def _make_fault_test(name,fn):
    def test(self):
        with self.assertRaises(gate.ReviewHold, msg=name):
            produce(mutate(fn))
    test.__name__="test_reject_"+name
    return test


for _name,_fn in FAULTS.items():
    setattr(R71ConservationTests,"test_reject_"+_name,_make_fault_test(_name,_fn))


if __name__=="__main__":
    unittest.main()
