"""R65 isolated synthetic/adversarial tests: no network, CMS, approval or publication."""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import unittest

TOOLS = Path(__file__).resolve().parents[1] / "tools"
r64_path = TOOLS / "r64_article_source_dependency_review.py"
r64_spec = importlib.util.spec_from_file_location("r65_test_original_r64", r64_path)
r64 = importlib.util.module_from_spec(r64_spec)
r64_spec.loader.exec_module(r64)
r65_path = TOOLS / "r65_integrated_citation_conservation.py"
spec = importlib.util.spec_from_file_location("r65_tested", r65_path)
r65 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r65)
EXPECTED = (35, 29, 35, 29, 29, 6)


def sign(obj):
    obj.pop("fingerprint_sha256", None)
    obj["fingerprint_sha256"] = r65.digest(obj)
    return obj


def fixtures():
    def token(sid="alpha", offset=5):
        return {"source_id": sid, "offset_codepoints": offset,
                "unabridged_local_context": "Original context, not claim support",
                "human_claim_support_state": "NOT_REVIEWED"}
    def version():
        return {"body_sha256": "c"*64, "metadata_sha256": "d"*64,
                "status_as_recorded_NOT_REVIEWED": {"editorial":"draft"},
                "safety_review_as_recorded_NOT_CLEARED": {"state":"pending"},
                "full_source_use_mapping_UNABRIDGED": {"alpha":"full original reading note"},
                "citation_occurrences_in_original_order": [token()]}
    articles=[]
    for i in range(29):
        slug="original-article-%02d" % (i+1)
        articles.append({"cluster":"food", "slug":slug, "review_state":"NOT_REVIEWED",
                         "versions":{"frozen":version(), "observed":version()}})
    lin=sign({"schema":"r61-private-contributor-two-version-lineage-v1",
              "release_state":"HOLD","machine_only":True,
              "counts":{"original_contributor_articles":29,
                        "old_citation_occurrences":29,
                        "observed_citation_occurrences_UNVERIFIED":29},
              "per_article_citation_and_context_lineage_NOT_REVIEWED": articles,
              **{x:False for x in r65.HOLD}})
    reading={"id":"alpha", "url":"https://example.invalid/same-url",
             "notes":"Full original source reading depth preserved"}
    srcrow={"cluster":"food","source_id":"alpha",
            "work_order_sha256":"f"*64,
            "change_kind":"UNCHANGED_NOT_REVERIFIED",
            "human_source_review":"NOT_REVIEWED",
            "qualified_claim_safety_review":"NOT_REVIEWED",
            "versions":{}}
    for v in ("frozen","observed"):
        srcrow["versions"][v]={
            "record_sha256":r65.digest(reading),
            "unabridged_contributor_reading_NOT_HUMAN_CHECKED":reading,
            "same_exact_url_distinct_identity_NOT_ALIAS":False,
            "candidate_citation_occurrences_NOT_SUPPORT_PROOF":[],
            "article_source_use_notes_UNABRIDGED_NOT_SUPPORT_PROOF":[]}
    source_report={"fingerprint_sha256":"3"*64,
                   "source_work_orders_ALL_IDENTITIES_BOTH_VERSIONS":[srcrow]}
    r62_docket={"fingerprint_sha256":"2"*64}
    dep=r64._construct(lin,r62_docket,source_report)
    original_tasks=[]
    for i in range(35):
        slug="original-article-%02d"%(i+1) if i<29 else "other-article-%02d"%(i-28)
        sid="alpha" if i<29 else "other-%02d"%(i-28)
        origin="food" if i<29 else "base"
        record={"id":sid, "_origin":origin, "url":"https://example.invalid/same-url",
                "notes":"The entire original source reading, not validated by this tool"}
        item={"slug":slug, "source_id":sid,"source_origin":origin,
              "citation_ordinal_within_article_source":1,
              "token_offset_codepoints_in_original_html":5,
              "frozen_article_html_sha256":("c" if i<29 else "e")*64,
              "original_source_record_sha256":r65.digest(record)}
        original_tasks.append({
            "citation_occurrence_work_order_id_sha256":r65.digest(item),
            "exact_original_token_identity":item,
            "original_unabridged_visible_context":"Exact editorial evidence: {{cite:"+sid+"}}",
            "original_unabridged_contributor_source_record":record,
            "original_unabridged_article_source_relationship":{
                "slug":slug,"source_id":sid,"source_origin":origin,
                "original_source_record_as_selected":record,
                "all_citation_contexts_for_human_claim_review":["Original unabridged context"]},
            "human_source_retrieval_state":"NOT_REVIEWED",
            "human_claim_support_state":"NOT_REVIEWED",
            "qualified_hazard_safety_state":"NOT_REVIEWED"})
    full=sign({"schema":"r58-private-exact-citation-occurrence-docket-v1",
               "release_state":"HOLD","machine_only":True,
               "counts":{"original_articles":35, "water_tools":1,
                         "exact_citation_occurrence_work_orders":35},
               "individual_original_citation_occurrence_review_queue":original_tasks,
               **{x:False for x in r65.HOLD}})
    return [full,lin,dep]


def resign(args):
    sign(args[0])
    sign(args[1])
    args[2]["parent_R61_sha256"]=args[1]["fingerprint_sha256"]
    sign(args[2])
    return args


class R65ConservationTests(unittest.TestCase):
    def setUp(self):
        self.args=fixtures()

    def report(self, args=None):
        return r65.construct(*(self.args if args is None else args),expected=EXPECTED)

    def test_35_integrated_original_articles(self):
        self.assertEqual(self.report()["counts"]["integrated_articles"],35)

    def test_29_original_contributors(self):
        self.assertEqual(self.report()["counts"]["frozen_contributor_articles"],29)

    def test_6_outside_seven_clusters(self):
        self.assertEqual(self.report()["counts"]["six_other_integrated_articles"],6)

    def test_original_water_planning_tool_not_discarded(self):
        self.assertEqual(self.report()["counts"]["original_water_planning_tools"],1)

    def test_original_citation_census_preserved(self):
        self.assertEqual(self.report()["counts"]["integrated_citation_occurrences"],35)

    def test_full_original_source_reading_kept_for_six_other_articles(self):
        row=self.report()["all_35_original_article_review_work_orders_NOT_APPROVED"][0]
        self.assertIn("entire original source reading",str(row).lower())

    def test_exact_candidate_links_are_not_claim_support(self):
        self.assertEqual(self.report()["counts"][
            "exact_R58_to_frozen_R61_candidate_tokens_NOT_CLAIM_SUPPORT"],29)

    def test_no_unmatched_frozen_tokens_in_exact_fixture(self):
        self.assertEqual(self.report()["counts"][
            "unpaired_frozen_contributor_tokens_NEED_HUMAN_REVIEW"],0)

    def test_stable_deterministic_report(self):
        self.assertEqual(self.report(),self.report())

    def test_report_fingerprint_protects_original_context(self):
        a=self.report()
        b=copy.deepcopy(self.args)
        b[0]["individual_original_citation_occurrence_review_queue"][0][
            "original_unabridged_visible_context"]="Preserved other original claim"
        self.assertNotEqual(a["fingerprint_sha256"],self.report(resign(b))["fingerprint_sha256"])

    def test_release_always_hold(self):
        obj=self.report()
        self.assertEqual(obj["release_state"],"HOLD")
        self.assertTrue(all(obj[k] is False for k in r65.HOLD))

    def test_all_source_records_unreviewed(self):
        self.assertTrue(all(x["human_source_review"]=="NOT_REVIEWED"
                            for x in self.report()["all_35_original_article_review_work_orders_NOT_APPROVED"]))

    def test_29_contributor_records_retained(self):
        rows=self.report()["all_35_original_article_review_work_orders_NOT_APPROVED"]
        self.assertEqual(sum(x["frozen_and_proposed_contributor_custody_OR_NULL"] is not None
                             for x in rows),29)

    def test_6_separate_records_retained(self):
        rows=self.report()["all_35_original_article_review_work_orders_NOT_APPROVED"]
        self.assertEqual(sum(x["frozen_and_proposed_contributor_custody_OR_NULL"] is None
                             for x in rows),6)

    def test_sha_change_does_not_fake_exact_link(self):
        args=copy.deepcopy(self.args)
        args[0]["individual_original_citation_occurrence_review_queue"][0][
            "exact_original_token_identity"]["frozen_article_html_sha256"]="f"*64
        obj=self.report(resign(args))
        self.assertEqual(obj["counts"][
            "exact_R58_to_frozen_R61_candidate_tokens_NOT_CLAIM_SUPPORT"],28)
        self.assertEqual(obj["counts"][
            "unpaired_frozen_contributor_tokens_NEED_HUMAN_REVIEW"],1)

    def test_altered_proposed_article_body_flagged_not_approved(self):
        args=copy.deepcopy(self.args)
        args[1]["per_article_citation_and_context_lineage_NOT_REVIEWED"][0][
            "versions"]["observed"]["body_sha256"]="f"*64
        report=self.report(resign(args))
        self.assertIn("CONTRIBUTOR_BODY_CHANGED_UNREVIEWED",
                      report["counts"]["review_flags_NOT_SAFETY_VERDICTS"])

    def test_changed_contributor_metadata_flagged_not_approved(self):
        args=copy.deepcopy(self.args)
        args[1]["per_article_citation_and_context_lineage_NOT_REVIEWED"][0][
            "versions"]["observed"]["metadata_sha256"]="f"*64
        report=self.report(resign(args))
        self.assertIn("CONTRIBUTOR_METADATA_CHANGED_UNREVIEWED",
                      report["counts"]["review_flags_NOT_SAFETY_VERDICTS"])

    def test_similar_urls_never_prove_support(self):
        self.assertIn("NOT proof",self.report()["limitations"])

    def test_rearranged_original_work_orders_preserves_article_accounting(self):
        args=copy.deepcopy(self.args)
        args[0]["individual_original_citation_occurrence_review_queue"].reverse()
        a=self.report()["all_35_original_article_review_work_orders_NOT_APPROVED"]
        b=self.report(resign(args))["all_35_original_article_review_work_orders_NOT_APPROVED"]
        self.assertEqual(a,b)


BAD = {
    "r58_status":(0,["release_state"],"PASS"),
    "r61_status":(1,["release_state"],"READY"),
    "r64_status":(2,["release_state"],"RELEASE"),
    "r58_publish":(0,["may_publish"],True),
    "r61_link_approval":(1,["human_source_links_verified"],True),
    "r64_safety":(2,["qualified_safety_clearance"],True),
    "r58_schema":(0,["schema"],"fake"),
    "r61_schema":(1,["schema"],"fake"),
    "r64_schema":(2,["schema"],"fake"),
    "original_article_census":(0,["counts","original_articles"],34),
    "original_water_census":(0,["counts","water_tools"],0),
    "original_token_census":(0,["counts","exact_citation_occurrence_work_orders"],34),
    "contributor_count":(1,["counts","original_contributor_articles"],28),
    "frozen_count":(1,["counts","old_citation_occurrences"],28),
    "proposed_count":(1,["counts","observed_citation_occurrences_UNVERIFIED"],30),
    "original_work_order_approved":(0,["individual_original_citation_occurrence_review_queue",0,
                                      "human_claim_support_state"],"VERIFIED"),
    "original_medical_approved":(0,["individual_original_citation_occurrence_review_queue",0,
                                   "qualified_hazard_safety_state"],"APPROVED"),
    "original_source_access_approved":(0,["individual_original_citation_occurrence_review_queue",0,
                                         "human_source_retrieval_state"],"VERIFIED"),
    "original_source_record_missing":(0,["individual_original_citation_occurrence_review_queue",0,
                                        "original_unabridged_contributor_source_record"],None),
    "original_source_origin_swapped":(0,["individual_original_citation_occurrence_review_queue",0,
                                        "original_unabridged_contributor_source_record","_origin"],"base"),
    "original_source_id_swapped":(0,["individual_original_citation_occurrence_review_queue",0,
                                    "original_unabridged_contributor_source_record","id"],"other"),
    "original_source_sha_swapped":(0,["individual_original_citation_occurrence_review_queue",0,
                                     "exact_original_token_identity","original_source_record_sha256"],"f"*64),
    "original_slug_empty":(0,["individual_original_citation_occurrence_review_queue",0,
                              "exact_original_token_identity","slug"],""),
    "original_id_empty":(0,["individual_original_citation_occurrence_review_queue",0,
                            "exact_original_token_identity","source_id"],""),
    "original_offset_negative":(0,["individual_original_citation_occurrence_review_queue",0,
                                    "exact_original_token_identity","token_offset_codepoints_in_original_html"],-1),
    "original_offset_bool":(0,["individual_original_citation_occurrence_review_queue",0,
                                "exact_original_token_identity","token_offset_codepoints_in_original_html"],True),
    "original_ordinal_zero":(0,["individual_original_citation_occurrence_review_queue",0,
                                "exact_original_token_identity","citation_ordinal_within_article_source"],0),
    "original_fp_fake":(0,["individual_original_citation_occurrence_review_queue",0,
                           "citation_occurrence_work_order_id_sha256"],"fake"),
    "original_body_fp_fake":(0,["individual_original_citation_occurrence_review_queue",0,
                                "exact_original_token_identity","frozen_article_html_sha256"],"fake"),
    "original_context_dropped":(0,["individual_original_citation_occurrence_review_queue",0,
                                   "original_unabridged_visible_context"],None),
    "original_relation_dropped":(0,["individual_original_citation_occurrence_review_queue",0,
                                    "original_unabridged_article_source_relationship"],None),
    "original_relation_slug":(0,["individual_original_citation_occurrence_review_queue",0,
                                 "original_unabridged_article_source_relationship","slug"],"other"),
    "original_relation_id":(0,["individual_original_citation_occurrence_review_queue",0,
                               "original_unabridged_article_source_relationship","source_id"],"other"),
    "original_relation_origin":(0,["individual_original_citation_occurrence_review_queue",0,
                                   "original_unabridged_article_source_relationship","source_origin"],"base"),
    "contributor_review_approved":(1,["per_article_citation_and_context_lineage_NOT_REVIEWED",0,
                                     "review_state"],"PASS"),
    "contributor_slug_forged":(1,["per_article_citation_and_context_lineage_NOT_REVIEWED",0,
                                  "slug"],"not-in-integrated"),
    "contributor_token_dropped":(1,["per_article_citation_and_context_lineage_NOT_REVIEWED",0,
                                    "versions","frozen","citation_occurrences_in_original_order"],[]),
    "contributor_token_id_empty":(1,["per_article_citation_and_context_lineage_NOT_REVIEWED",0,
                                     "versions","frozen","citation_occurrences_in_original_order",0,"source_id"],""),
    "contributor_token_offset_neg":(1,["per_article_citation_and_context_lineage_NOT_REVIEWED",0,
                                      "versions","frozen","citation_occurrences_in_original_order",0,"offset_codepoints"],-1),
    "contributor_token_support_approved":(1,["per_article_citation_and_context_lineage_NOT_REVIEWED",0,
                                            "versions","frozen","citation_occurrences_in_original_order",0,
                                            "human_claim_support_state"],"PASS"),
    "contributor_token_context_lost":(1,["per_article_citation_and_context_lineage_NOT_REVIEWED",0,
                                         "versions","frozen","citation_occurrences_in_original_order",0,
                                         "unabridged_local_context"],None),
    "contributor_body_fp_missing":(1,["per_article_citation_and_context_lineage_NOT_REVIEWED",0,
                                    "versions","frozen","body_sha256"],None),
    "contributor_source_uses_missing":(1,["per_article_citation_and_context_lineage_NOT_REVIEWED",0,
                                        "versions","frozen","full_source_use_mapping_UNABRIDGED"],None),
    "dependency_cluster_swapped":(2,["article_source_dependency_work_orders_ALL_NOT_APPROVED",0,
                                     "article_cluster"],"historic-food"),
    "dependency_slug_swapped":(2,["article_source_dependency_work_orders_ALL_NOT_APPROVED",0,
                                  "article_slug"],"missing"),
    "dependency_source_id_swapped":(2,["article_source_dependency_work_orders_ALL_NOT_APPROVED",0,
                                      "source_id"],"missing"),
    "dependency_human_approved":(2,["article_source_dependency_work_orders_ALL_NOT_APPROVED",0,
                                    "human_claim_support"],"VERIFIED"),
    "dependency_safety_approved":(2,["article_source_dependency_work_orders_ALL_NOT_APPROVED",0,
                                     "qualified_safety_review"],"PASS"),
    "dependency_frozen_token_dropped":(2,["article_source_dependency_work_orders_ALL_NOT_APPROVED",0,
                                          "versions","frozen","citation_occurrences_UNABRIDGED_NOT_SUPPORT_PROOF"],[]),
    "dependency_source_use_changed":(2,["article_source_dependency_work_orders_ALL_NOT_APPROVED",0,
                                       "versions","frozen","source_use_present"],False),
    "dependency_source_note_changed":(2,["article_source_dependency_work_orders_ALL_NOT_APPROVED",0,
                                        "versions","frozen","source_use_note_UNABRIDGED_NOT_SUPPORT_PROOF"],"rewritten"),
}


def make_negative(name, modification):
    def test(self):
        args=copy.deepcopy(self.args)
        index, path, value=modification
        obj=args[index]
        for key in path[:-1]:
            obj=obj[key]
        obj[path[-1]]=value
        resign(args)
        with self.assertRaises(r65.ConservationHold, msg=name):
            self.report(args)
    return test


for name, change in BAD.items():
    setattr(R65ConservationTests, "test_reject_"+name, make_negative(name, change))


class R65AttackCases(unittest.TestCase):
    def test_unsigned_mutated_original_rejected(self):
        args=fixtures()
        args[0]["individual_original_citation_occurrence_review_queue"].pop()
        with self.assertRaises(r65.ConservationHold):
            r65.construct(*args,expected=EXPECTED)

    def test_duplicate_original_citation_work_order_rejected(self):
        args=fixtures()
        args[0]["individual_original_citation_occurrence_review_queue"][1]=copy.deepcopy(
            args[0]["individual_original_citation_occurrence_review_queue"][0])
        resign(args)
        with self.assertRaises(r65.ConservationHold):
            r65.construct(*args,expected=EXPECTED)

    def test_two_different_original_article_html_shas_rejected(self):
        args=fixtures()
        row=copy.deepcopy(args[0]["individual_original_citation_occurrence_review_queue"][0])
        row["exact_original_token_identity"]["token_offset_codepoints_in_original_html"]=8
        row["exact_original_token_identity"]["frozen_article_html_sha256"]="f"*64
        row["citation_occurrence_work_order_id_sha256"]=r65.digest(row["exact_original_token_identity"])
        args[0]["individual_original_citation_occurrence_review_queue"][1]=row
        resign(args)
        with self.assertRaises(r65.ConservationHold):
            r65.construct(*args,expected=EXPECTED)

    def test_deleted_dependency_source_relation_rejected(self):
        args=fixtures()
        args[2]["article_source_dependency_work_orders_ALL_NOT_APPROVED"].pop()
        resign(args)
        with self.assertRaises(r65.ConservationHold):
            r65.construct(*args,expected=EXPECTED)

    def test_invented_approval_cannot_be_signed(self):
        args=fixtures()
        args[0]["human_source_links_verified"]=True
        resign(args)
        with self.assertRaises(r65.ConservationHold):
            r65.construct(*args,expected=EXPECTED)


if __name__ == "__main__":
    unittest.main()
