"""R66 source-identity ledger: independent synthetic and adversarial tests."""
from __future__ import annotations
import copy
import csv
import importlib.util
import io
from pathlib import Path
import unittest

path=Path(__file__).resolve().parents[1]/"tools"/"r66_cited_source_identity_ledger.py"
spec=importlib.util.spec_from_file_location("r66_ledger_under_test",path)
r66=importlib.util.module_from_spec(spec)
spec.loader.exec_module(r66)
EXPECTED=(2,1,4,3,1)


def sign(p):
    p["fingerprint_sha256"]=r66.digest({k:v for k,v in p.items()
                                         if k!="fingerprint_sha256"})
    return p


def cited(slug,offset,sid,origin,url,notes):
    return {
        "source_id":sid,"source_origin":origin,
        "original_codepoint_offset":offset,
        "R58_work_order_sha256":r66.digest([slug,offset,sid,origin]),
        "unabridged_original_visible_context_NOT_SUPPORT_PROOF":
            "Original full context: "+slug+":"+sid,
        "unabridged_original_source_reading_NOT_HUMAN_CHECKED":{
            "id":sid,"_origin":origin,"url":url,
            "notes":notes,"supports":"Only unreviewed contributor assertion"},
        "unabridged_original_relationship_NOT_HUMAN_CHECKED":{
            "slug":slug,"source_id":sid,"source_origin":origin,
            "full_source_use_note_UNABRIDGED":"Kept without fact-check"},
    }


def doc(slug,citations,flags,contributor=None):
    return {
        "article_slug":slug,
        "integrated_article_html_sha256":r66.digest([slug,"original html"]),
        "all_original_integrated_citation_and_reading_evidence_UNABRIDGED":citations,
        "frozen_and_proposed_contributor_custody_OR_NULL":contributor,
        "review_flags_NOT_SAFETY_VERDICTS":sorted(flags),
        "human_source_review":"NOT_REVIEWED",
        "qualified_safety_review":"NOT_REVIEWED",
    }


def fixture():
    shared="https://example.invalid/one-exact-url"
    separate="https://example.invalid/different-url"
    return sign({
        "schema":"r65-private-35-article-citation-conservation-v1",
        "release_state":"HOLD","machine_only":True,
        "counts":{"integrated_articles":2,"original_water_planning_tools":1,
                  "integrated_citation_occurrences":4,
                  "original_article_citation_occurrences":3,
                  "original_water_tool_citation_occurrences":1},
        "all_35_original_article_review_work_orders_NOT_APPROVED":[
            doc("alpha-article",[
                cited("alpha-article",3,"source-alpha","food",shared,
                      "Whole alpha source note"),
                cited("alpha-article",19,"source-beta","base",separate,
                      "Whole beta source note")],
                ["CONTRIBUTOR_BODY_CHANGED_UNREVIEWED"],{"cluster":"food"}),
            doc("gamma-article",[
                cited("gamma-article",7,"source-gamma","history",shared,
                      "Different whole gamma note")],
                ["INTEGRATED_ONLY_SIX_ARTICLES_OUTSIDE_SEVEN_R14_CLUSTERS"])],
        "original_water_planning_tool_review_work_order_NOT_APPROVED":
            doc("water-planner",[
                cited("water-planner",11,"source-beta","base",separate,
                      "Whole beta source note")],
                ["INTEGRATED_ORIGINAL_WATER_TOOL_OUTSIDE_SEVEN_R14_CLUSTERS"]),
        **{x:False for x in r66.HOLD},
    })


class R66Tests(unittest.TestCase):
    def setUp(self): self.p=fixture()
    def report(self,p=None): return r66.construct(p if p is not None else self.p,
                                                  expected=EXPECTED)
    def test_3_docs(self): self.assertEqual(len(self.report()[
        "all_35_original_articles_plus_water_tool_NOT_APPROVED"]),3)
    def test_4_citations(self): self.assertEqual(self.report()["counts"][
        "all_original_citation_occurrences"],4)
    def test_articles_vs_tool(self):
        c=self.report()["counts"]
        self.assertEqual((c["article_citation_occurrences"],
                          c["water_tool_citation_occurrences"]),(3,1))
    def test_3_distinct_source_readings(self): self.assertEqual(self.report()["counts"][
        "distinct_original_CITED_source_origin_and_id_pairs"],3)
    def test_shared_exact_url_groups(self): self.assertEqual(self.report()["counts"][
        "shared_exact_url_groups_WITHOUT_ALIAS"],1)
    def test_shared_url_retain_distinct_identities(self): self.assertEqual(self.report()["counts"][
        "source_identities_in_shared_url_groups"],2)
    def test_original_notes_retained(self): self.assertIn("Different whole gamma note",
        str(self.report()["all_cited_original_source_identitites_NOT_APPROVED"]))
    def test_source_beta_used_by_article_and_tool(self):
        sources=self.report()["all_cited_original_source_identitites_NOT_APPROVED"]
        refs=next(s["all_original_citation_occurrences_AND_RELATIONSHIPS_UNABRIDGED"]
                  for s in sources if s["source_id"]=="source-beta")
        self.assertEqual(len(refs),2)
        self.assertEqual({x["original_document_slug"] for x in refs},
                         {"alpha-article","water-planner"})
    def test_original_contexts_preserved(self):
        self.assertIn("Original full context",str(self.report()))
    def test_original_relations_preserved(self):
        self.assertIn("full_source_use_note_UNABRIDGED",str(self.report()))
    def test_r65_fingerprint_bound(self): self.assertEqual(self.report()[
        "parent_R65_full_35_plus_tool_evidence_sha256"],self.p["fingerprint_sha256"])
    def test_no_auto_approval(self):
        r=self.report()
        self.assertEqual(r["release_state"],"HOLD")
        self.assertTrue(all(r[k] is False for k in r66.HOLD))
    def test_all_source_tasks_pending(self):
        self.assertTrue(all(x["human_claim_support_state"]=="NOT_REVIEWED"
         for x in self.report()["all_cited_original_source_identitites_NOT_APPROVED"]))
    def test_deterministic(self): self.assertEqual(self.report(),self.report())
    def test_original_article_order_does_not_change_output(self):
        p=copy.deepcopy(self.p)
        p["all_35_original_article_review_work_orders_NOT_APPROVED"].reverse()
        before,after=self.report(),self.report(sign(p))
        self.assertEqual(before["counts"],after["counts"])
        self.assertEqual([x["source_id"] for x in before[
            "all_cited_original_source_identitites_NOT_APPROVED"]],
            [x["source_id"] for x in after[
            "all_cited_original_source_identitites_NOT_APPROVED"]])
        self.assertNotEqual(before["fingerprint_sha256"],after["fingerprint_sha256"])
    def test_original_citation_order_does_not_change_output(self):
        p=copy.deepcopy(self.p)
        p["all_35_original_article_review_work_orders_NOT_APPROVED"][0][
            "all_original_integrated_citation_and_reading_evidence_UNABRIDGED"].reverse()
        before,after=self.report(),self.report(sign(p))
        self.assertEqual(before["counts"],after["counts"])
        self.assertEqual(len(before["all_cited_original_source_identitites_NOT_APPROVED"]),
                         len(after["all_cited_original_source_identitites_NOT_APPROVED"]))
        self.assertNotEqual(before["fingerprint_sha256"],after["fingerprint_sha256"])
    def test_no_alias_when_url_case_differs(self):
        p=copy.deepcopy(self.p)
        p["all_35_original_article_review_work_orders_NOT_APPROVED"][1][
            "all_original_integrated_citation_and_reading_evidence_UNABRIDGED"][0][
            "unabridged_original_source_reading_NOT_HUMAN_CHECKED"]["url"] = (
            "https://example.invalid/ONE-exact-url")
        self.assertEqual(self.report(sign(p))["counts"][
            "shared_exact_url_groups_WITHOUT_ALIAS"],0)
    def test_changed_contributor_body_flagged(self):
        self.assertIn("CITED_IN_CHANGED_CONTRIBUTOR_ARTICLE_NOT_APPROVED",
                      str(self.report()))
    def test_integrated_only_article_flagged(self):
        self.assertIn("CITED_IN_INTEGRATED_ONLY_ARTICLE_OUTSIDE_SEVEN_CLUSTERS",
                      str(self.report()))
    def test_water_tool_source_flagged(self):
        self.assertIn("ORIGINAL_WATER_TOOL_SOURCE_NOT_HUMAN_REVIEWED",
                      str(self.report()))
    def test_unverified_url_not_dropped(self):
        p=copy.deepcopy(self.p)
        row=p["all_35_original_article_review_work_orders_NOT_APPROVED"][1][
            "all_original_integrated_citation_and_reading_evidence_UNABRIDGED"][0]
        row["unabridged_original_source_reading_NOT_HUMAN_CHECKED"]["url"]=None
        self.assertIn("MISSING_OR_INVALID_HTTP_URL_HUMAN_RETRIEVAL_REQUIRED",
                      str(self.report(sign(p))))
    def test_non_http_url_flagged(self):
        p=copy.deepcopy(self.p)
        row=p["all_35_original_article_review_work_orders_NOT_APPROVED"][1][
            "all_original_integrated_citation_and_reading_evidence_UNABRIDGED"][0]
        row["unabridged_original_source_reading_NOT_HUMAN_CHECKED"]["url"]=(
            "file:///private/item")
        self.assertIn("MISSING_OR_INVALID_HTTP_URL_HUMAN_RETRIEVAL_REQUIRED",
                      str(self.report(sign(p))))
    def test_same_identity_changed_reading_fails_closed(self):
        p=copy.deepcopy(self.p)
        row=p["original_water_planning_tool_review_work_order_NOT_APPROVED"][
            "all_original_integrated_citation_and_reading_evidence_UNABRIDGED"][0]
        row["unabridged_original_source_reading_NOT_HUMAN_CHECKED"]["notes"]="changed!"
        with self.assertRaises(r66.SourceIdentityHold): self.report(sign(p))
    def test_unresigned_context_mutation_rejected(self):
        p=copy.deepcopy(self.p)
        p["all_35_original_article_review_work_orders_NOT_APPROVED"][0][
            "all_original_integrated_citation_and_reading_evidence_UNABRIDGED"][0][
            "unabridged_original_visible_context_NOT_SUPPORT_PROOF"]="tampered"
        with self.assertRaises(r66.SourceIdentityHold): self.report(p)
    def test_context_mutation_updates_hash_even_if_resigned(self):
        p=copy.deepcopy(self.p)
        p["all_35_original_article_review_work_orders_NOT_APPROVED"][0][
            "all_original_integrated_citation_and_reading_evidence_UNABRIDGED"][0][
            "unabridged_original_visible_context_NOT_SUPPORT_PROOF"]="new context"
        self.assertNotEqual(self.report()["fingerprint_sha256"],
                            self.report(sign(p))["fingerprint_sha256"])
    def test_different_origins_never_aliased_same_id(self):
        p=copy.deepcopy(self.p)
        row=p["all_35_original_article_review_work_orders_NOT_APPROVED"][1][
            "all_original_integrated_citation_and_reading_evidence_UNABRIDGED"][0]
        for x in (row,row["unabridged_original_source_reading_NOT_HUMAN_CHECKED"],
                  row["unabridged_original_relationship_NOT_HUMAN_CHECKED"]):
            x["source_id" if "source_id" in x else "id"]="source-alpha"
        self.assertEqual(self.report(sign(p))["counts"][
            "distinct_original_CITED_source_origin_and_id_pairs"],3)
    def test_csv_one_row_per_identity(self):
        self.assertEqual(len(list(csv.DictReader(io.StringIO(
            r66.task_csv(self.report()))))),3)
    def test_csv_review_states_pending(self):
        self.assertTrue(all(row["QUALIFIED_SAFETY_NOT_REVIEWED"]=="NOT_REVIEWED"
               for row in csv.DictReader(io.StringIO(r66.task_csv(self.report())))))
    def test_csv_source_sha_present(self):
        self.assertTrue(all(len(row["original_reading_sha256"])==64
               for row in csv.DictReader(io.StringIO(r66.task_csv(self.report())))))
    def test_csv_formula_equals_neutralized(self):
        self.assertEqual(r66._spreadsheet_cell("=1+1"),"'=1+1")
    def test_csv_formula_plus_neutralized(self):
        self.assertEqual(r66._spreadsheet_cell("+1+1"),"'+1+1")
    def test_csv_formula_minus_neutralized(self):
        self.assertEqual(r66._spreadsheet_cell("-1+1"),"'-1+1")
    def test_csv_formula_at_neutralized(self):
        self.assertEqual(r66._spreadsheet_cell("@sum(1)"),"'@sum(1)")
    def test_csv_formula_whitespace_neutralized(self):
        self.assertEqual(r66._spreadsheet_cell("  =a"),"'  =a")
    def test_csv_https_unchanged(self):
        self.assertEqual(r66._spreadsheet_cell("https://example.invalid"),"https://example.invalid")
    def test_csv_rejects_tamper(self):
        r=self.report()
        r["fingerprint_sha256"]="0"*64
        with self.assertRaises(r66.SourceIdentityHold): r66.task_csv(r)
    def test_csv_rejects_forged_approval(self):
        r=self.report()
        r["may_publish"]=True
        sign(r)
        with self.assertRaises(r66.SourceIdentityHold): r66.task_csv(r)


# Each adversarial case recomputes the self-reported digest, so the structural
# and publication HOLD gates must still catch tampering beyond checksum mismatch.
CASES = {
"schema":(["schema"],"fabricated"),
"status":(["release_state"],"PASS"),
"machine_only":(["machine_only"],False),
"publish":(["may_publish"],True),
"qd_approved":(["independent_QD_approval"],True),
"safety_approved":(["qualified_safety_clearance"],True),
"links_approved":(["human_source_links_verified"],True),
"doc_count":(["counts","integrated_articles"],1),
"tool_count":(["counts","original_water_planning_tools"],0),
"citations_total":(["counts","integrated_citation_occurrences"],3),
"article_citations":(["counts","original_article_citation_occurrences"],2),
"tool_citations":(["counts","original_water_tool_citation_occurrences"],2),
"missing_articles":(["all_35_original_article_review_work_orders_NOT_APPROVED"],[]),
"missing_tool":(["original_water_planning_tool_review_work_order_NOT_APPROVED"],None),
"article_slug_blank":(["all_35_original_article_review_work_orders_NOT_APPROVED",0,"article_slug"],""),
"doc_status_approved":(["all_35_original_article_review_work_orders_NOT_APPROVED",0,"human_source_review"],"VERIFIED"),
"doc_safety_approved":(["all_35_original_article_review_work_orders_NOT_APPROVED",0,"qualified_safety_review"],"APPROVED"),
"html_sha_fake":(["all_35_original_article_review_work_orders_NOT_APPROVED",0,"integrated_article_html_sha256"],"bad"),
"flags_missing":(["all_35_original_article_review_work_orders_NOT_APPROVED",0,"review_flags_NOT_SAFETY_VERDICTS"],[]),
"flags_unsorted":(["all_35_original_article_review_work_orders_NOT_APPROVED",0,"review_flags_NOT_SAFETY_VERDICTS"],["z","a"]),
"citations_missing":(["all_35_original_article_review_work_orders_NOT_APPROVED",0,"all_original_integrated_citation_and_reading_evidence_UNABRIDGED"],[]),
"citation_id_blank":(["all_35_original_article_review_work_orders_NOT_APPROVED",0,"all_original_integrated_citation_and_reading_evidence_UNABRIDGED",0,"source_id"],""),
"citation_origin_blank":(["all_35_original_article_review_work_orders_NOT_APPROVED",0,"all_original_integrated_citation_and_reading_evidence_UNABRIDGED",0,"source_origin"],""),
"citation_sha_bad":(["all_35_original_article_review_work_orders_NOT_APPROVED",0,"all_original_integrated_citation_and_reading_evidence_UNABRIDGED",0,"R58_work_order_sha256"],"bad"),
"citation_offset_neg":(["all_35_original_article_review_work_orders_NOT_APPROVED",0,"all_original_integrated_citation_and_reading_evidence_UNABRIDGED",0,"original_codepoint_offset"],-1),
"citation_offset_bool":(["all_35_original_article_review_work_orders_NOT_APPROVED",0,"all_original_integrated_citation_and_reading_evidence_UNABRIDGED",0,"original_codepoint_offset"],True),
"citation_context_missing":(["all_35_original_article_review_work_orders_NOT_APPROVED",0,"all_original_integrated_citation_and_reading_evidence_UNABRIDGED",0,"unabridged_original_visible_context_NOT_SUPPORT_PROOF"],None),
"source_reading_missing":(["all_35_original_article_review_work_orders_NOT_APPROVED",0,"all_original_integrated_citation_and_reading_evidence_UNABRIDGED",0,"unabridged_original_source_reading_NOT_HUMAN_CHECKED"],None),
"relationship_missing":(["all_35_original_article_review_work_orders_NOT_APPROVED",0,"all_original_integrated_citation_and_reading_evidence_UNABRIDGED",0,"unabridged_original_relationship_NOT_HUMAN_CHECKED"],None),
"reading_id_wrong":(["all_35_original_article_review_work_orders_NOT_APPROVED",0,"all_original_integrated_citation_and_reading_evidence_UNABRIDGED",0,"unabridged_original_source_reading_NOT_HUMAN_CHECKED","id"],"other"),
"reading_origin_wrong":(["all_35_original_article_review_work_orders_NOT_APPROVED",0,"all_original_integrated_citation_and_reading_evidence_UNABRIDGED",0,"unabridged_original_source_reading_NOT_HUMAN_CHECKED","_origin"],"other"),
"reading_url_invalid_type":(["all_35_original_article_review_work_orders_NOT_APPROVED",0,"all_original_integrated_citation_and_reading_evidence_UNABRIDGED",0,"unabridged_original_source_reading_NOT_HUMAN_CHECKED","url"],3),
"relationship_slug_wrong":(["all_35_original_article_review_work_orders_NOT_APPROVED",0,"all_original_integrated_citation_and_reading_evidence_UNABRIDGED",0,"unabridged_original_relationship_NOT_HUMAN_CHECKED","slug"],"other"),
"relationship_id_wrong":(["all_35_original_article_review_work_orders_NOT_APPROVED",0,"all_original_integrated_citation_and_reading_evidence_UNABRIDGED",0,"unabridged_original_relationship_NOT_HUMAN_CHECKED","source_id"],"other"),
"relationship_origin_wrong":(["all_35_original_article_review_work_orders_NOT_APPROVED",0,"all_original_integrated_citation_and_reading_evidence_UNABRIDGED",0,"unabridged_original_relationship_NOT_HUMAN_CHECKED","source_origin"],"other"),
"tool_slug_wrong":(["original_water_planning_tool_review_work_order_NOT_APPROVED","article_slug"],"other-tool"),
"tool_approval":(["original_water_planning_tool_review_work_order_NOT_APPROVED","human_source_review"],"PASS"),
"tool_safety":(["original_water_planning_tool_review_work_order_NOT_APPROVED","qualified_safety_review"],"PASS"),
"tool_html_sha_invalid":(["original_water_planning_tool_review_work_order_NOT_APPROVED","integrated_article_html_sha256"],"bad"),
"tool_citations_dropped":(["original_water_planning_tool_review_work_order_NOT_APPROVED","all_original_integrated_citation_and_reading_evidence_UNABRIDGED"],[]),
}


def make_negative(name,path,value):
    def run(self):
        p=copy.deepcopy(self.p)
        target=p
        for seg in path[:-1]: target=target[seg]
        target[path[-1]]=value
        with self.assertRaises(r66.SourceIdentityHold,msg=name):
            self.report(sign(p))
    return run


for name,(path,value) in CASES.items():
    setattr(R66Tests,"test_reject_"+name,make_negative(name,path,value))


if __name__=="__main__":
    unittest.main()
