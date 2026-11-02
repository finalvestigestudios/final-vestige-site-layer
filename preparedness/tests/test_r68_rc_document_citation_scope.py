"""R68: synthetic and hostile-input tests, no source/network/CMS writes."""
from __future__ import annotations
from copy import deepcopy
import csv
import importlib.util
import io
from pathlib import Path
import unittest

TOOL = Path(__file__).resolve().parents[1] / "tools" / "r68_rc_document_citation_scope.py"
spec = importlib.util.spec_from_file_location("r68_private_test_gate", TOOL)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

N = (2,2,3,3,2)
HOLD = {k:False for k in gate.HOLD}


def seal(record):
    record.pop("fingerprint_sha256",None)
    record["fingerprint_sha256"]=gate.digest(record)
    return record


def candidate_meta(slug, section, source_id):
    return {
        "slug":slug,"section":section,
        "status":{"editorial":"drafted","publish":"draft"},
        "safety_review":{"state":"pending","reviewer":None,"date":None},
        "source_use":{source_id:"Unreviewed complete source-use explanation."},
    }


def original_doc(slug,body,sid):
    return {
        "original_slug":slug,
        "original_html_sha256":gate.raw_sha(body),
        "unabridged_original_citation_identity_order":[{
            "source_id":sid,
            "original_offset_codepoints":body.index("{{cite:"),
        }],
        "human_source_review":"NOT_REVIEWED",
        "qualified_safety_review":"NOT_REVIEWED",
    }


def fixtures():
    original_corpus = [
        ("article","a-guide","start-here","s1","base"),
        ("article","b-guide","food","s2","food"),
        ("tool","water-planner","field-tools","s1","base"),
        ("tool","quick-card","field-tools","s3",None),
    ]
    docs=[]
    old=[]
    for kind,slug,section,sid,origin in original_corpus:
        body="Original Unicode café / "+slug+" {{cite:"+sid+"}} Original context"
        docs.append({"kind":kind,"slug":slug,"metadata":candidate_meta(slug,section,sid),
                     "body_html":body})
        if slug!="quick-card":
            old.append(original_doc(slug,body,sid))
    original=seal({"schema":"r66-private-original-cited-source-identity-ledger-v1",
       "release_state":"HOLD","machine_only":True,**HOLD,
       "counts":{"all_original_citation_occurrences":3},
       "all_35_original_articles_plus_water_tool_NOT_APPROVED":old})
    source=[]
    for origin,sid in [("base","s1"),("food","s2"),("shelter","s3")]:
        rec={"id":sid,"url":"https://example.org/"+sid,
             "notes":"Complete human-unverified reading "+sid,
             "human_link_check":False}
        source.append({
            "source_origin":origin,"source_id":sid,
            "candidate_complete_reading_UNABRIDGED":rec,
            "candidate_record_sha256":gate.digest(rec),
            "human_link_review":"NOT_REVIEWED",
            "human_claim_support_review":"NOT_REVIEWED",
            "qualified_safety_review":"NOT_REVIEWED",
            "independent_QD_review":"NOT_REVIEWED"})
    custody=seal({"schema":"r67-original-to-release-candidate-source-custody-v1",
       "release_state":"HOLD","machine_only":True,**HOLD,
       "original_R66_fingerprint_sha256":original["fingerprint_sha256"],
       "counts":{"original_citation_occurrences":3,"RC_all_source_rows":3},
       "all_original_and_RC_source_review_work_orders_NOT_APPROVED":source})
    crosswalk={
        "status":"DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED",
        "article_origins":{"a-guide":"base","b-guide":"food",
                           "water-planner":"base"}}
    return custody,original,docs,crosswalk


def reseal_bundle(bundle):
    custody,old,docs,crosswalk=bundle
    seal(old)
    custody["original_R66_fingerprint_sha256"]=old["fingerprint_sha256"]
    seal(custody)
    return bundle


def run(bundle):
    custody,old,docs,crosswalk=bundle
    return gate.construct(custody,old,docs,crosswalk,expected=N)


class SyntheticRCReview(unittest.TestCase):
    def setUp(self):
        self.bundle=fixtures()

    def test_base_35_plus_tools_synthetic_conservation(self):
        result=run(self.bundle)
        self.assertEqual(result["release_state"],"HOLD")
        self.assertEqual(result["counts"]["candidate_tools"],2)
        self.assertEqual(result["counts"]["original_articles_conserved"],2)
        self.assertEqual(result["counts"]["RC_citation_occurrences_UNREVIEWED"],4)
        self.assertEqual(result["counts"]["original_citations_preserved_under_R66"],3)
        self.assertEqual(result["counts"]["human_source_or_claim_checks_performed_BY_R68"],0)
        self.assertFalse(result["may_publish"])

    def test_determinism_and_evidence_fingerprint(self):
        a,b=run(self.bundle),run(self.bundle)
        self.assertEqual(a,b)
        self.assertEqual(a["fingerprint_sha256"],gate.digest({
            k:v for k,v in a.items() if k!="fingerprint_sha256"}))

    def test_unabridged_original_candidate_reading_and_unicode_offsets(self):
        result=run(self.bundle)
        a=next(x for x in result[
            "all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED"]
               if x["slug"]=="a-guide")
        self.assertEqual(a["RC_body_HTML_UNABRIDGED_NOT_SAFETY_CLEARED"],
                         self.bundle[2][0]["body_html"])
        self.assertIn("café",a["RC_body_HTML_UNABRIDGED_NOT_SAFETY_CLEARED"])
        self.assertEqual(a["all_RC_citation_occurrences_NOT_CLAIM_SUPPORT"][0][
            "unicode_codepoint_offset_in_candidate_html"],
            self.bundle[2][0]["body_html"].index("{{cite:"))
        self.assertIn("Complete human-unverified reading",
            str(a["all_RC_source_uses_and_unabridged_readings_NOT_APPROVED"]))

    def test_new_tool_kept_unreviewed_and_original_water_tool_preserved(self):
        result=run(self.bundle)
        rows={x["slug"]:x for x in result[
            "all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED"]}
        self.assertIsNone(rows["quick-card"]["original_R66_document_evidence_NOT_APPROVED"])
        self.assertEqual(rows["quick-card"]["origin_mapping_FROM_FROZEN_CROSSWALK_OR_NULL"],None)
        self.assertIsNotNone(rows["water-planner"]["original_R66_document_evidence_NOT_APPROVED"])
        self.assertEqual(result["counts"]["additional_RC_tools_without_frozen_origin"],1)

    def test_metadata_approved_is_open_not_independent_clearance(self):
        self.bundle[2][0]["metadata"]["safety_review"]["state"]="approved"
        result=run(self.bundle)
        self.assertEqual(result["counts"]["historical_safety_labels_NOT_INDEPENDENTLY_REVIEWED"],1)
        self.assertFalse(result["qualified_safety_clearance"])
        self.assertIn("RC_RECORDED_SAFETY_LABEL_NOT_INDEPENDENTLY_VERIFIED",
            result["all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED"][0][
                "review_flags_NOT_SAFETY_VERDICTS"])

    def test_changed_html_with_identical_citation_still_requires_review(self):
        self.bundle[2][0]["body_html"]="Added potentially consequential advice. "+self.bundle[2][0]["body_html"]
        result=run(self.bundle)
        self.assertEqual(result["counts"]["original_document_bodies_changed_or_needing_review"],1)
        row=next(x for x in result["all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED"]
                 if x["slug"]=="a-guide")
        self.assertIn("ORIGINAL_VS_RC_BODY_CHANGED_RECHECK_EVERY_CLAIM",
                      row["review_flags_NOT_SAFETY_VERDICTS"])

    def test_shared_url_retains_two_different_source_identities(self):
        source=self.bundle[0]["all_original_and_RC_source_review_work_orders_NOT_APPROVED"]
        source[1]["candidate_complete_reading_UNABRIDGED"]["url"]="https://example.org/s1"
        source[1]["candidate_record_sha256"]=gate.digest(
            source[1]["candidate_complete_reading_UNABRIDGED"])
        seal(self.bundle[0])
        result=run(self.bundle)
        row=next(x for x in result["all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED"]
                 if x["slug"]=="b-guide")
        self.assertIn("EXACT_URL_SHARED_BUT_SEPARATE_SOURCE_RECORDS",
            row["all_RC_source_uses_and_unabridged_readings_NOT_APPROVED"][0][
                "flags_NOT_SAFETY_VERDICTS"])

    def test_source_id_variants_keep_original_reading_separate(self):
        source=self.bundle[0]["all_original_and_RC_source_review_work_orders_NOT_APPROVED"]
        old=source[2]
        old["source_id"]="s1"
        old["candidate_complete_reading_UNABRIDGED"]["id"]="s1"
        old["candidate_record_sha256"]=gate.digest(
            old["candidate_complete_reading_UNABRIDGED"])
        self.bundle[2][3]["metadata"]["source_use"]={"s1":"Distinct evidence"}
        self.bundle[2][3]["body_html"]="new {{cite:s1}}"
        seal(self.bundle[0])
        result=run(self.bundle)
        row=next(x for x in result["all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED"]
                 if x["slug"]=="quick-card")
        variants=row["all_RC_source_uses_and_unabridged_readings_NOT_APPROVED"][0][
            "all_candidate_source_variants_UNABRIDGED_NOT_APPROVED"]
        self.assertEqual(len(variants),2)
        self.assertEqual(result["counts"]["candidate_citations_with_duplicate_id_variants"],2)
        self.assertIn("UNSCOPED_SOURCE_ID_HUMAN_SELECTION_REQUIRED",
            row["all_RC_source_uses_and_unabridged_readings_NOT_APPROVED"][0][
                "flags_NOT_SAFETY_VERDICTS"])

    def test_private_csv_produces_four_unapproved_rows(self):
        report=run(self.bundle)
        rows=list(csv.DictReader(io.StringIO(gate.task_csv(report))))
        self.assertEqual(len(rows),4)
        self.assertEqual({x["slug"] for x in rows},
                         {"a-guide","b-guide","quick-card","water-planner"})
        self.assertTrue(all(x["HUMAN_CLAIM_CHECK_NOT_REVIEWED"]=="NOT_REVIEWED"
                            and x["SAFETY_REVIEW_NOT_REVIEWED"]=="NOT_REVIEWED"
                            for x in rows))

    def test_csv_rejects_unsigned_or_released_forgery(self):
        r=run(self.bundle)
        r["may_publish"]=True
        with self.assertRaises(gate.ReviewHold):
            gate.task_csv(r)

    def test_csv_formula_neutralization(self):
        self.bundle[2][3]["metadata"]["section"]="-unsafe"
        with self.assertRaises(gate.ReviewHold):
            run(self.bundle)

    def test_non_cited_source_use_remains_visible(self):
        self.bundle[2][0]["metadata"]["source_use"]["s2"]="Non-cited source use."
        result=run(self.bundle)
        row=next(x for x in result["all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED"]
                 if x["slug"]=="a-guide")
        self.assertEqual(len(row["all_RC_source_uses_and_unabridged_readings_NOT_APPROVED"]),2)
        source=next(x for x in row["all_RC_source_uses_and_unabridged_readings_NOT_APPROVED"]
                    if x["source_id"]=="s2")
        self.assertIn("SOURCE_USE_NOT_CITED_IN_BODY",source["flags_NOT_SAFETY_VERDICTS"])

    def test_cited_without_source_use_is_visible_not_approved(self):
        self.bundle[2][0]["metadata"]["source_use"]={}
        row=next(x for x in run(self.bundle)[
            "all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED"]
                 if x["slug"]=="a-guide")
        self.assertIn("CITED_WITHOUT_SOURCE_USE_EXPLANATION",row[
            "all_RC_source_uses_and_unabridged_readings_NOT_APPROVED"][0][
                "flags_NOT_SAFETY_VERDICTS"])

    def test_malformed_source_use_approval_not_substituted_for_source(self):
        self.bundle[2][0]["metadata"]["source_use"]["s1"]="Approved!" 
        report=run(self.bundle)
        self.assertFalse(report["human_source_links_verified"])
        self.assertFalse(report["qualified_safety_clearance"])

    def test_new_tool_with_no_citations_still_has_source_use_custody(self):
        self.bundle[2][3]["body_html"]="Tool markup contains no citation tokens."
        report=run(self.bundle)
        self.assertEqual(report["counts"]["RC_citation_occurrences_UNREVIEWED"],3)
        self.assertTrue(next(x for x in report[
            "all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED"]
            if x["slug"]=="quick-card")[
            "all_RC_source_uses_and_unabridged_readings_NOT_APPROVED"])


# Each named case creates a fresh, independently re-signed hostile input. A
# changed fingerprint alone is not enough: the checks must survive attacker
# re-signing and then fail for the violated custody invariant.
def change(case, bundle):
    custody,old,docs,crosswalk=bundle
    rows=custody["all_original_and_RC_source_review_work_orders_NOT_APPROVED"]
    orig=old["all_35_original_articles_plus_water_tool_NOT_APPROVED"]
    if case=="R67_unsigned": custody["counts"]["RC_all_source_rows"]=999; return
    if case=="R66_unsigned": old["counts"]["all_original_citation_occurrences"]=999; return
    if case=="R67_release": custody["release_state"]="READY"
    elif case=="R66_release": old["release_state"]="READY"
    elif case=="R67_not_machine": custody["machine_only"]=False
    elif case=="R66_not_machine": old["machine_only"]=False
    elif case=="R67_publish": custody["may_publish"]=True
    elif case=="R66_publish": old["may_publish"]=True
    elif case=="R67_QD": custody["independent_QD_approval"]=True
    elif case=="R66_QD": old["independent_QD_approval"]=True
    elif case=="R67_safety": custody["qualified_safety_clearance"]=True
    elif case=="R66_safety": old["qualified_safety_clearance"]=True
    elif case=="R67_human": custody["human_source_links_verified"]=True
    elif case=="R66_human": old["human_source_links_verified"]=True
    elif case=="R67_schema": custody["schema"]="changed-schema"
    elif case=="R66_schema": old["schema"]="changed-schema"
    elif case=="R67_source_count": rows.pop()
    elif case=="R67_duplicate_source": rows[1]=deepcopy(rows[0])
    elif case=="R67_missing_origin": rows[0]["source_origin"]=None
    elif case=="R67_missing_id": rows[0]["source_id"]=None
    elif case=="R67_fake_source_reviewer": rows[0]["human_link_review"]="APPROVED"
    elif case=="R67_fake_claim_review": rows[0]["human_claim_support_review"]="APPROVED"
    elif case=="R67_fake_safety_review": rows[0]["qualified_safety_review"]="APPROVED"
    elif case=="R67_fake_QD_review": rows[0]["independent_QD_review"]="APPROVED"
    elif case=="RC_human_link_approval": rows[0]["candidate_complete_reading_UNABRIDGED"]["human_link_check"]=True
    elif case=="RC_changed_reading": rows[0]["candidate_complete_reading_UNABRIDGED"]["notes"]="Changed."
    elif case=="RC_changed_record_id": rows[0]["candidate_complete_reading_UNABRIDGED"]["id"]="other"
    elif case=="RC_missing_source_url": rows[0]["candidate_complete_reading_UNABRIDGED"]["url"]=None
    elif case=="RC_empty_source_url": rows[0]["candidate_complete_reading_UNABRIDGED"]["url"]=""
    elif case=="R66_missing_original": orig.pop()
    elif case=="R66_duplicate_original": orig[1]=deepcopy(orig[0])
    elif case=="R66_source_reviewer": orig[0]["human_source_review"]="APPROVED"
    elif case=="R66_safety_reviewer": orig[0]["qualified_safety_review"]="APPROVED"
    elif case=="R66_missing_slug": orig[0]["original_slug"]=None
    elif case=="R66_missing_sha": orig[0]["original_html_sha256"]=None
    elif case=="R66_missing_citations": orig[0]["unabridged_original_citation_identity_order"]=None
    elif case=="R66_original_count": old["counts"]["all_original_citation_occurrences"]=4
    elif case=="R67_original_count": custody["counts"]["original_citation_occurrences"]=4
    elif case=="R67_candidate_count": custody["counts"]["RC_all_source_rows"]=4
    elif case=="crosswalk_status": crosswalk["status"]="APPROVED"
    elif case=="crosswalk_map_missing": crosswalk.pop("article_origins")
    elif case=="crosswalk_missing_original": crosswalk["article_origins"].pop("a-guide")
    elif case=="crosswalk_null_origin": crosswalk["article_origins"]["a-guide"]=None
    elif case=="missing_candidate_doc": docs.pop()
    elif case=="duplicate_candidate_doc": docs[1]=deepcopy(docs[0])
    elif case=="unknown_candidate_article": docs[0]["slug"]="new-article"; docs[0]["metadata"]["slug"]="new-article"
    elif case=="article_collides_with_tool": docs[3]["slug"]="a-guide"; docs[3]["metadata"]["slug"]="a-guide"
    elif case=="candidate_bad_kind": docs[0]["kind"]="essay"
    elif case=="candidate_bad_slug": docs[0]["slug"]="../hostile"
    elif case=="candidate_mismatched_meta": docs[0]["metadata"]["slug"]="wrong"
    elif case=="candidate_missing_section": docs[0]["metadata"].pop("section")
    elif case=="candidate_bad_section": docs[0]["metadata"]["section"]="/bad"
    elif case=="candidate_published": docs[0]["metadata"]["status"]["publish"]="published"
    elif case=="candidate_missing_safety": docs[0]["metadata"].pop("safety_review")
    elif case=="candidate_safety_bad_state": docs[0]["metadata"]["safety_review"]["state"]="certified"
    elif case=="candidate_empty_body": docs[0]["body_html"]=""
    elif case=="candidate_missing_body": docs[0].pop("body_html")
    elif case=="candidate_bad_metadata": docs[0]["metadata"]=[]
    elif case=="candidate_bad_source_use": docs[0]["metadata"]["source_use"]=[]
    elif case=="candidate_non_string_use": docs[0]["metadata"]["source_use"]["s1"]=True
    elif case=="candidate_unavailable_source": docs[0]["body_html"]+=" {{cite:unknown-source}}"
    elif case=="candidate_invalid_token": docs[0]["body_html"]+=" {{cite:s1"
    elif case=="candidate_bad_source_use_id": docs[0]["metadata"]["source_use"]["../bad"]="Unsafe"
    elif case=="candidate_missing_original_tool": docs[2]["slug"]="new-tool"; docs[2]["metadata"]["slug"]="new-tool"
    elif case=="candidate_original_body_changed_without_citation": docs[0]["body_html"]="NO citation"
    else: raise AssertionError("unknown hostile case "+case)
    reseal_bundle(bundle)


BAD_CASES = [
    "R67_unsigned","R66_unsigned","R67_release","R66_release",
    "R67_not_machine","R66_not_machine","R67_publish","R66_publish",
    "R67_QD","R66_QD","R67_safety","R66_safety","R67_human","R66_human",
    "R67_schema","R66_schema","R67_source_count","R67_duplicate_source",
    "R67_missing_origin","R67_missing_id","R67_fake_source_reviewer",
    "R67_fake_claim_review","R67_fake_safety_review","R67_fake_QD_review",
    "RC_human_link_approval","RC_changed_reading","RC_changed_record_id",
    "RC_missing_source_url","RC_empty_source_url","R66_missing_original",
    "R66_duplicate_original","R66_source_reviewer","R66_safety_reviewer",
    "R66_missing_slug","R66_missing_sha","R66_missing_citations",
    "R66_original_count","R67_original_count","R67_candidate_count",
    "crosswalk_status","crosswalk_map_missing","crosswalk_missing_original",
    "crosswalk_null_origin","missing_candidate_doc","duplicate_candidate_doc",
    "unknown_candidate_article","article_collides_with_tool",
    "candidate_bad_kind","candidate_bad_slug","candidate_mismatched_meta",
    "candidate_missing_section","candidate_bad_section","candidate_published",
    "candidate_missing_safety","candidate_safety_bad_state","candidate_empty_body",
    "candidate_missing_body","candidate_bad_metadata","candidate_bad_source_use",
    "candidate_non_string_use","candidate_unavailable_source",
    "candidate_invalid_token","candidate_bad_source_use_id",
    "candidate_missing_original_tool",
]


def named_adversarial_test(case):
    def test(self):
        bundle=fixtures()
        change(case,bundle)
        with self.assertRaises(gate.ReviewHold,msg=case):
            run(bundle)
    test.__name__="test_adversarial_"+case.lower()
    return test


for case in BAD_CASES:
    setattr(SyntheticRCReview,"test_adversarial_"+case.lower(),
            named_adversarial_test(case))


if __name__=="__main__":
    unittest.main()
