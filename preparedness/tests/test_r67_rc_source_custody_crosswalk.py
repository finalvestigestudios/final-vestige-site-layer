"""R67 synthetic/adversarial source-change review: independent private unittest suite."""
from __future__ import annotations

import copy
import csv
import importlib.util
import io
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[1] / "tools" / "r67_rc_source_custody_crosswalk.py"
spec = importlib.util.spec_from_file_location("r67_crosswalk_under_test",path)
r67 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r67)

EXPECTED = (3,4,2,3,1,1,2,1,1,0)
URL_SHARED = "https://example.invalid/kept-exact"
URL_OTHER = "https://example.invalid/other"


def source(sid, url, note):
    return {"id":sid, "url":url, "notes":note,
            "supports":"Precisely bounded contributor research note",
            "human_link_check":False, "verified_on":"2026-10-29"}


def signed(ledger):
    ledger["fingerprint_sha256"] = r67.digest({
        k:v for k,v in ledger.items() if k != "fingerprint_sha256"})
    return ledger


def fixture():
    original = {k:[] for k in r67.ORIGIN_FILES}
    original["base"] = [
        source("registered-1",URL_SHARED,"original full register reading"),
        source("registered-2",URL_OTHER,"uncited record full notes")]
    original["food"] = [
        source("food-1",URL_SHARED,"entire original source reading different depth")]
    candidate = copy.deepcopy(original)
    candidate["food"][0]["notes"] = "changed candidate full reading; unreviewed"
    candidate["base"].append(source("new-1",URL_SHARED,"additional unreviewed RC source"))
    cited_rows = []
    for origin,id,n in (("base","registered-1",1),("food","food-1",2)):
        original_reading = next(r for r in original[origin] if r["id"] == id)
        cited_rows.append({
            "source_origin":origin,"source_id":id,
            "source_record_sha256":r67.digest({**original_reading,"_origin":origin}),
            "original_unabridged_source_record_NOT_HUMAN_VERIFIED":
                {**original_reading,"_origin":origin},
            "all_original_citation_occurrences_AND_RELATIONSHIPS_UNABRIDGED":
                [{"original_visible_claim_context_UNABRIDGED_NOT_SUPPORT_PROOF":
                  "Exact original context; not fact-checked", "original_offset":i}
                 for i in range(n)],
            "human_source_retrieval_state":"NOT_REVIEWED",
            "human_claim_support_state":"NOT_REVIEWED",
            "qualified_safety_review_state":"NOT_REVIEWED",
        })
    ledger = signed({
        "schema":"r66-private-original-cited-source-identity-ledger-v1",
        "release_state":"HOLD", "machine_only":True,
        "counts":{"all_original_citation_occurrences":3},
        "all_cited_original_source_identitites_NOT_APPROVED":cited_rows,
        **{key:False for key in r67.HOLD},
    })
    probes = [
        {"url":URL_SHARED,"ok":True,"status":200,
         "title":"Machine-read test only","sha256":"a"*64},
        {"url":URL_OTHER,"ok":False,"error":"machine blocked"},
    ]
    return original,candidate,ledger,probes


class R67Positive(unittest.TestCase):
    def setUp(self):
        self.e = fixture()
        self.r = r67.construct(*self.e,expected=EXPECTED)
    def order(self,origin,sid):
        return next(x for x in self.r[
            "all_original_and_RC_source_review_work_orders_NOT_APPROVED"]
            if (x["source_origin"],x["source_id"]) == (origin,sid))
    def test_all_original_records(self):
        self.assertEqual(self.r["counts"]["original_all_source_rows"],3)
    def test_candidate_records(self):
        self.assertEqual(self.r["counts"]["RC_all_source_rows"],4)
    def test_preserve_original_cited_identity(self):
        self.assertEqual(self.r["counts"]["distinct_original_cited_source_records"],2)
    def test_all_citations_preserved(self):
        self.assertEqual(self.r["counts"]["original_citation_occurrences"],3)
    def test_uncited_source_preserved(self):
        self.assertEqual(self.r["counts"]["original_uncited_source_records_NOT_DROPPED"],1)
    def test_machine_probe_two(self):
        self.assertEqual(self.r["counts"]["RC_machine_probed_urls_NOT_HUMAN_CHECKS"],2)
    def test_probe_ok_not_human(self):
        self.assertEqual(self.r["counts"]["RC_machine_probe_ok_NOT_HUMAN_VERIFICATION"],1)
    def test_probe_failed_not_human(self):
        self.assertEqual(self.r["counts"]["RC_machine_probe_failed_NOT_A_HUMAN_LINK_VERDICT"],1)
    def test_new_source_quarantined(self):
        self.assertEqual(self.order("base","new-1")["state_NOT_EDITORIAL_VERDICT"],
                         "ADDED_TO_RC_NOT_REVIEWED")
    def test_changed_source_quarantined(self):
        self.assertEqual(self.order("food","food-1")["state_NOT_EDITORIAL_VERDICT"],
                         "SOURCE_READING_CHANGED_NOT_REVIEWED")
    def test_unchanged_source_unreviewed(self):
        self.assertEqual(self.order("base","registered-1")["state_NOT_EDITORIAL_VERDICT"],
                         "IDENTICAL_RECORD_STILL_NOT_HUMAN_VERIFIED")
    def test_zero_removed(self):
        self.assertEqual(self.r["counts"]["removed_original_source_records"],0)
    def test_original_shared_exact_url(self):
        self.assertEqual(self.r["counts"]["original_shared_exact_url_groups"],1)
    def test_rc_shared_exact_url(self):
        self.assertEqual(self.r["counts"]["RC_shared_exact_url_groups"],1)
    def test_three_distinct_identities_at_rc_url(self):
        self.assertEqual(len(self.order("base","registered-1")[
            "candidate_distinct_identities_sharing_exact_url"]),3)
    def test_original_source_full_notes_retained(self):
        self.assertEqual(self.order("food","food-1")[
            "original_complete_reading_UNABRIDGED"]["notes"],
            "entire original source reading different depth")
    def test_candidate_source_full_notes_retained(self):
        self.assertIn("changed candidate full reading",self.order("food","food-1")[
            "candidate_complete_reading_UNABRIDGED"]["notes"])
    def test_changed_record_keys(self):
        self.assertEqual(self.order("food","food-1")[
            "changed_record_keys_REVIEW_REQUIRED"],["notes"])
    def test_exact_source_citation_reading_retained(self):
        self.assertEqual(len(self.order("food","food-1")[
            "original_cited_R66_evidence_UNABRIDGED_NOT_VERIFIED"]
            ["all_original_citation_occurrences_AND_RELATIONSHIPS_UNABRIDGED"]),2)
    def test_uncited_explicit_none(self):
        self.assertIsNone(self.order("base","registered-2")[
            "original_cited_R66_evidence_UNABRIDGED_NOT_VERIFIED"])
    def test_no_machine_probe_on_unmatched_source(self):
        self.assertIsNotNone(self.order("base","registered-2")[
            "candidate_machine_probe_URL_ONLY_NOT_HUMAN_VERIFIED"])
    def test_no_forged_human_approvals(self):
        self.assertTrue(all(x["human_link_review"]=="NOT_REVIEWED" and
            x["human_claim_support_review"]=="NOT_REVIEWED" and
            x["qualified_safety_review"]=="NOT_REVIEWED" for x in
            self.r["all_original_and_RC_source_review_work_orders_NOT_APPROVED"]))
    def test_hold_mandatory(self):
        self.assertEqual(self.r["release_state"],"HOLD")
        self.assertTrue(all(self.r[x] is False for x in r67.HOLD))
    def test_same_inputs_deterministic_fingerprint(self):
        self.assertEqual(r67.construct(*copy.deepcopy(self.e),expected=EXPECTED)
                         ["fingerprint_sha256"],self.r["fingerprint_sha256"])
    def test_reorder_input_records_is_stable(self):
        a,b,c,d=copy.deepcopy(self.e)
        a["base"].reverse(); b["base"].reverse(); d.reverse()
        self.assertEqual(r67.construct(a,b,c,d,expected=EXPECTED),
                         self.r)
    def test_every_source_has_exact_work_order(self):
        self.assertEqual(len({row["work_order_sha256"] for row in
            self.r["all_original_and_RC_source_review_work_orders_NOT_APPROVED"]}),4)
    def test_csv_rows_count(self):
        rows=list(csv.DictReader(io.StringIO(r67.task_csv(self.r))))
        self.assertEqual(len(rows),4)
    def test_csv_does_not_grant_verification(self):
        rows=list(csv.DictReader(io.StringIO(r67.task_csv(self.r))))
        self.assertTrue(all(r["HUMAN_LINK_CHECK_NOT_REVIEWED"]=="NOT_REVIEWED"
                         for r in rows))
    def test_csv_includes_modified_source(self):
        self.assertIn("SOURCE_READING_CHANGED_NOT_REVIEWED",r67.task_csv(self.r))
    def test_csv_injection_neutralized(self):
        a,b,c,d=fixture()
        for x in (a,b):
            for record in x["base"]:
                if record["id"]=="registered-2":
                    record["url"]="=HYPERLINK(1,2)"
        # A controlled bad URL is preserved, but a new probe must reference it.
        d[1]["url"]="=HYPERLINK(1,2)"
        result=r67.construct(a,b,c,d,expected=EXPECTED)
        csvstr=r67.task_csv(result)
        self.assertIn("'=HYPERLINK(1,2)",csvstr)
    def test_machine_probes_preserved_without_reinterpretation(self):
        self.assertEqual(self.r["RC_machine_source_accessibility_probes_NOT_HUMAN_CHECKS"]
                         [1]["error"],"machine blocked")
    def test_url_exactness_case_sensitive_no_alias(self):
        a,b,c,d=fixture()
        b["base"][-1]["url"]="HTTPS://EXAMPLE.INVALID/KEPT-EXACT"
        x = r67.construct(a,b,c,d,expected=(3,4,2,3,1,1,2,1,1,0))
        self.assertNotEqual(x["all_original_and_RC_source_review_work_orders_NOT_APPROVED"]
                            [-1]["candidate_exact_url_NO_ALIAS"],URL_SHARED)


class R67Adversarial(unittest.TestCase):
    def assert_hold(self,mutate,expected=EXPECTED):
        data=list(fixture())
        mutate(data)
        with self.assertRaises((r67.SourceCustodyHold,ValueError,KeyError,TypeError)):
            r67.construct(*data,expected=expected)
    def test_refuse_forged_parent_hash(self):
        self.assert_hold(lambda d:d[2].update(fingerprint_sha256="0"*64))
    def test_refuse_forged_parent_human_approval(self):
        def edit(d):
            d[2]["may_publish"]=True
            signed(d[2])
        self.assert_hold(edit)
    def test_refuse_changed_cited_reading(self):
        def edit(d):
            d[2]["all_cited_original_source_identitites_NOT_APPROVED"][0]["original_unabridged_source_record_NOT_HUMAN_VERIFIED"]["notes"]="FAKE"
            signed(d[2])
        self.assert_hold(edit)
    def test_refuse_invalid_r66_schema(self):
        def edit(d):
            d[2]["schema"]="impostor"; signed(d[2])
        self.assert_hold(edit)
    def test_refuse_missing_probes(self):
        self.assert_hold(lambda d:d[3].pop())
    def test_refuse_duplicate_probe(self):
        self.assert_hold(lambda d:d[3].__setitem__(1,copy.deepcopy(d[3][0])))
    def test_refuse_unknown_probe_url(self):
        self.assert_hold(lambda d:d[3][0].update(url="https://unreferenced.invalid/"))
    def test_refuse_fake_machine_human_check(self):
        self.assert_hold(lambda d:d[3][0].update(human_link_check=True))
    def test_refuse_false_human_approval_original(self):
        self.assert_hold(lambda d:d[0]["base"][0].update(human_link_check=True))
    def test_refuse_false_human_approval_candidate(self):
        self.assert_hold(lambda d:d[1]["food"][0].update(human_link_check=True))
    def test_refuse_wrong_original_source_id(self):
        self.assert_hold(lambda d:d[0]["base"][0].update(id="new-original-id"))
    def test_refuse_missing_original_source(self):
        self.assert_hold(lambda d:d[0]["food"].clear())
    def test_refuse_duplicate_candidate_source_id(self):
        self.assert_hold(lambda d:d[1]["base"].append(copy.deepcopy(d[1]["base"][0])))
    def test_refuse_origin_injection(self):
        self.assert_hold(lambda d:d[1]["base"][0].update(_origin="override"))
    def test_refuse_missing_origin(self):
        self.assert_hold(lambda d:d[0].pop("health"))
    def test_refuse_unknown_origin(self):
        self.assert_hold(lambda d:d[1].update(unknown=[]))
    def test_refuse_non_list_fragment(self):
        self.assert_hold(lambda d:d[1].update(food={}))
    def test_refuse_non_dict_record(self):
        self.assert_hold(lambda d:d[0]["food"].__setitem__(0,None))
    def test_refuse_proposed_extra_record(self):
        self.assert_hold(lambda d:d[1]["base"].append(
            source("rogue","https://new.invalid","unreviewed")))
    def test_refuse_unreviewed_original_reading_drift(self):
        self.assert_hold(lambda d:d[0]["food"][0].update(notes="changed frozen baseline"))
    def test_refuse_invalid_candidate_url_type(self):
        self.assert_hold(lambda d:d[1]["food"][0].update(url=None))
    def test_refuse_empty_candidate_url(self):
        self.assert_hold(lambda d:d[1]["food"][0].update(url=""))
    def test_refuse_invalid_human_link_state(self):
        self.assert_hold(lambda d:d[0]["base"][0].update(human_link_check="false"))
    def test_refuse_duplicate_cited_identity(self):
        def edit(d):
            d[2]["all_cited_original_source_identitites_NOT_APPROVED"][1]=copy.deepcopy(
                d[2]["all_cited_original_source_identitites_NOT_APPROVED"][0])
            signed(d[2])
        self.assert_hold(edit)
    def test_refuse_modified_original_citation_count(self):
        def edit(d):
            d[2]["counts"]["all_original_citation_occurrences"]=4; signed(d[2])
        self.assert_hold(edit)
    def test_refuse_source_probe_boolean_string(self):
        self.assert_hold(lambda d:d[3][0].update(ok="true"))
    def test_refuse_probes_reviewer_claim(self):
        self.assert_hold(lambda d:d[3][1].update(reviewer="self-proclaimed"))
    def test_refuse_probes_publication_claim(self):
        self.assert_hold(lambda d:d[3][0].update(may_publish=True))
    def test_refuse_missing_cited_context(self):
        def edit(d):
            d[2]["all_cited_original_source_identitites_NOT_APPROVED"][1].pop(
                "all_original_citation_occurrences_AND_RELATIONSHIPS_UNABRIDGED")
            signed(d[2])
        self.assert_hold(edit)
    def test_refuse_fake_cited_source_safety_state(self):
        def edit(d):
            d[2]["all_cited_original_source_identitites_NOT_APPROVED"][0][
                "qualified_safety_review_state"]="APPROVED"
            signed(d[2])
        self.assert_hold(edit)
    def test_refuse_dropped_r66_cited_record(self):
        def edit(d):
            d[2]["all_cited_original_source_identitites_NOT_APPROVED"].pop()
            signed(d[2])
        self.assert_hold(edit)
    def test_refuse_rc_group_census_drift(self):
        self.assert_hold(lambda d:d[1]["base"][-1].update(
            url="https://different.invalid/new-source"))
    def test_refuse_orig_group_census_drift(self):
        self.assert_hold(lambda d:d[0]["food"][0].update(url=URL_OTHER))
    def test_refuse_candidate_record_count_drift(self):
        self.assert_hold(lambda d:d[1]["base"].pop())
    def test_refuse_reclassification_as_source_deleted(self):
        self.assert_hold(lambda d:d[1]["food"].clear())
    def test_refuse_parent_machine_only_removed(self):
        def edit(d):
            d[2]["machine_only"]=False; signed(d[2])
        self.assert_hold(edit)
    def test_refuse_parent_false_QD_PASS(self):
        def edit(d):
            d[2]["independent_QD_approval"]=True; signed(d[2])
        self.assert_hold(edit)
    def test_refuse_malformed_expected(self):
        self.assert_hold(lambda d:None,expected=(3,4,2))
    def test_refuse_human_source_review_forged(self):
        def edit(d):
            d[2]["all_cited_original_source_identitites_NOT_APPROVED"][0][
                "human_source_retrieval_state"]="COMPLETE"; signed(d[2])
        self.assert_hold(edit)
    def test_refuse_repeated_original_id_even_with_same_url(self):
        self.assert_hold(lambda d:d[0]["food"].append(copy.deepcopy(d[0]["food"][0])))
    def test_refuse_probe_duplicate_with_modified_payload(self):
        self.assert_hold(lambda d:d[3][1].update(url=URL_SHARED,ok=False))


class R67ParserAdversarial(unittest.TestCase):
    def test_duplicate_key_rejected(self):
        with self.assertRaises(r67.SourceCustodyHold):
            r67.strict_json('{"sources":[],"sources":[]}')
    def test_nested_duplicate_key_rejected(self):
        with self.assertRaises(r67.SourceCustodyHold):
            r67.strict_json('{"sources":[{"id":"one","id":"two"}]}')
    def test_nan_rejected(self):
        with self.assertRaises(r67.SourceCustodyHold):
            r67.strict_json('{"value": NaN}')
    def test_infinity_rejected(self):
        with self.assertRaises(r67.SourceCustodyHold):
            r67.strict_json('{"value": Infinity}')
    def test_negative_infinity_rejected(self):
        with self.assertRaises(r67.SourceCustodyHold):
            r67.strict_json('{"value": -Infinity}')
    def test_readable_parse_roundtrip(self):
        self.assertEqual(r67.strict_json('{"sources":[]}'),{"sources":[]})
    def test_csv_refuses_bad_fingerprint(self):
        report=r67.construct(*fixture(),expected=EXPECTED)
        report["fingerprint_sha256"]="f"*64
        with self.assertRaises(r67.SourceCustodyHold):
            r67.task_csv(report)
    def test_csv_refuses_false_release_flag(self):
        report=r67.construct(*fixture(),expected=EXPECTED)
        report["qualified_safety_clearance"]=True
        report["fingerprint_sha256"]=r67.digest({
            k:v for k,v in report.items() if k!="fingerprint_sha256"})
        with self.assertRaises(r67.SourceCustodyHold):
            r67.task_csv(report)


if __name__ == "__main__":
    unittest.main()
