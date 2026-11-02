"""R70: synthetic and adversarial source URL/citation custody checks; no network."""
from __future__ import annotations

from copy import deepcopy
import csv
import importlib.util
import io
from pathlib import Path
import unittest

FILE = Path(__file__).resolve().parents[1] / "tools" / "r70_rc_source_url_citation_custody.py"
spec = importlib.util.spec_from_file_location("r70_test_module", FILE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
N = (1, 1, 3, 3)


def seal(x):
    x.pop("fingerprint_sha256",None)
    x["fingerprint_sha256"] = gate.digest(x)
    return x


def fixture():
    records = [
        ("base", "alpha", "https://www.cdc.gov/a", "CDC"),
        ("base", "beta", "https://www.ready.gov/b", "Ready"),
        ("food", "alpha", "https://www.fda.gov/c", "FDA"),
    ]
    rows = []
    for origin,sid,url,title in records:
        reading = {"id":sid,"url":url,"title":title,
                   "human_link_check":False,"supports":"synthetic reading"}
        rows.append({"source_origin":origin,"source_id":sid,
            "candidate_complete_reading_UNABRIDGED":reading,
            "candidate_record_sha256":gate.digest(reading),
            "candidate_exact_url_NO_ALIAS":url,
            "original_complete_reading_UNABRIDGED":None,
            "original_record_sha256":None,
            **{k:"NOT_REVIEWED" for k in (
                "human_link_review","human_claim_support_review",
                "qualified_safety_review","independent_QD_review")}})
    r67 = seal({"schema":gate.R67_SCHEMA,"release_state":"HOLD",
        "machine_only":True,"counts":{"RC_all_source_rows":3,
            "RC_shared_exact_url_groups":0,
            "human_link_checks_performed_BY_THIS_TOOL":0},
        "all_original_and_RC_source_review_work_orders_NOT_APPROVED":rows,
        "RC_shared_exact_URL_groups_UNRESOLVED":[],
        **{k:False for k in gate.HOLD}})
    by_id = {
        "alpha":[rows[0],rows[2]],
        "beta":[rows[1]]
    }
    def make_doc(kind,slug,ids):
        occurrences = []
        for i,sid in enumerate(ids,1):
            occurrences.append({
                "ordinal":i,"source_id":sid,
                "unicode_codepoint_offset_in_candidate_html":i*8,
                "exact_citation_token":"{{cite:"+sid+"}}",
                "scoped_candidate_source_identity_OR_NULL":["base",sid],
                "all_possible_origin_and_id_pairs_NOT_MERGED":
                    [["base",sid],["food",sid]] if sid=="alpha"
                    else [["base",sid]],
                "human_claim_support":"NOT_REVIEWED"})
        uses = []
        for sid in sorted(set(ids)):
            uses.append({"source_id":sid,
                "all_candidate_source_variants_UNABRIDGED_NOT_APPROVED":by_id[sid],
                "review_state":"NOT_REVIEWED"})
        doc = {"kind":kind,"slug":slug,
            "proposed_WordPress_url_DRAFT_ONLY":"/preparedness/"+kind+"/"+slug+"/",
            "RC_body_utf8_sha256":"a"*64,
            "all_RC_citation_occurrences_NOT_CLAIM_SUPPORT":occurrences,
            "all_RC_source_uses_and_unabridged_readings_NOT_APPROVED":uses,
            **{k:"NOT_REVIEWED" for k in (
                "human_claim_review","human_source_review",
                "qualified_safety_review","independent_QD_review")}}
        doc["task_sha256"]=gate.digest(doc)
        rows69=[{"ordinal":i,"source_id":c["source_id"],
            "unicode_codepoint_offset":c["unicode_codepoint_offset_in_candidate_html"],
            "literal_token":c["exact_citation_token"],
            "candidate_source_identity_OR_NULL":
                c["scoped_candidate_source_identity_OR_NULL"],
            "all_source_identity_variants_NOT_ALIASED":
                c["all_possible_origin_and_id_pairs_NOT_MERGED"],
            "DOM_CLASSIFICATION_NOT_BROWSER_PROOF":
                "DOM_TEXT_POTENTIALLY_VISIBLE_NOT_BROWSER_VERIFIED",
            "human_claim_support_review":"NOT_REVIEWED"}
            for i,c in enumerate(occurrences,1)]
        d69 = {"kind":kind,"slug":slug,
            "R68_task_sha256":doc["task_sha256"],
            "R68_HTML_sha256":doc["RC_body_utf8_sha256"],
            "proposed_url_PRIVATE_DRAFT_ONLY":
                doc["proposed_WordPress_url_DRAFT_ONLY"],
            "citation_visibility_audit_NOT_BROWSER_PROOF":rows69,
            **{k:"NOT_REVIEWED" for k in (
                "human_source_review","qualified_safety_review",
                "independent_QD_review")}}
        return doc,d69
    d1,e1=make_doc("article","first",["alpha","alpha"])
    d2,e2=make_doc("tool","planner",["beta"])
    r68=seal({"schema":gate.R68_SCHEMA,"release_state":"HOLD",
        "machine_only":True,
        "source_R67_custody_fingerprint_sha256":r67["fingerprint_sha256"],
        "counts":{"original_articles_conserved":1,
                  "candidate_tools":1,
                  "RC_citation_occurrences_UNREVIEWED":3,
                  "human_source_or_claim_checks_performed_BY_R68":0},
        "all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED":[d1,d2],
        **{k:False for k in gate.HOLD}})
    r69=seal({"schema":gate.R69_SCHEMA,"release_state":"HOLD",
        "machine_only":True,
        "R68_exact_original_RC_custody_fingerprint_sha256":r68["fingerprint_sha256"],
        "counts":{"candidate_articles":1,"candidate_tools":1,
                  "candidate_citation_occurrences_accounted_for":3,
                  "human_claim_or_safety_checks_performed_BY_R69":0},
        "all_document_DOM_text_and_citation_review_orders_NOT_APPROVED":[e1,e2],
        **{k:False for k in gate.HOLD}})
    return r67,r68,r69


def execute(r=None):
    return gate.construct(*(r if r is not None else fixture()),expected=N)


def reseal_document_reports(items,*,source=False,doc=False):
    if source:
        seal(items[0])
        items[1]["source_R67_custody_fingerprint_sha256"] = items[0]["fingerprint_sha256"]
    if doc or source:
        seal(items[1])
        items[2]["R68_exact_original_RC_custody_fingerprint_sha256"] = items[1]["fingerprint_sha256"]
    seal(items[2])
    return items


class IntegrationCases(unittest.TestCase):
    def test_conserve_every_source_and_citation(self):
        r=execute()
        self.assertEqual((r["counts"]["source_records_conserved"],
                          r["counts"]["citation_occurrences_conserved"]),(3,3))

    def test_held_sealed_fingerprint(self):
        r=execute()
        self.assertEqual(r["fingerprint_sha256"],gate.digest(
            {k:v for k,v in r.items() if k!="fingerprint_sha256"}))
        self.assertFalse(r["may_publish"])

    def test_deterministic_repeated_run(self):
        self.assertEqual(execute(),execute())

    def test_complete_reading_and_url_retained(self):
        r=execute()
        self.assertTrue(all(x["candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"]["supports"] ==
                            "synthetic reading" for x in
                            r["all_244_source_URL_and_reading_work_orders_NOT_APPROVED"]))

    def test_two_same_id_different_origin_not_aliased(self):
        r=execute()
        citations=r["all_2173_citation_URL_identity_work_orders_NOT_APPROVED"]
        self.assertEqual(len(citations[0]["all_candidate_origin_scoped_identities_NOT_ALIASED"]),2)
        self.assertEqual(len(citations[0]["all_candidate_exact_urls_NOT_DEDUPLICATED"]),2)

    def test_distinct_urls_and_groups(self):
        self.assertEqual(execute()["counts"]["RC_distinct_exact_URLs_NOT_ALIASED"],3)
        self.assertEqual(execute()["counts"]["RC_shared_exact_URL_groups_NOT_RESOLVED"],0)

    def test_zero_approval_operations(self):
        self.assertEqual(execute()["counts"]["human_url_or_claim_checks_performed_BY_R70"],0)

    def test_source_csv_all_unreviewed(self):
        rows=list(csv.DictReader(io.StringIO(gate.csv_tasks(execute()))))
        self.assertEqual(len(rows),3)
        self.assertTrue(all(x["HUMAN_SOURCE_CHECK_NOT_REVIEWED"]=="NOT_REVIEWED" for x in rows))

    def test_citation_csv_all_unreviewed(self):
        rows=list(csv.DictReader(io.StringIO(gate.csv_tasks(execute(),citations=True))))
        self.assertEqual(len(rows),3)
        self.assertTrue(all(x["HUMAN_CLAIM_SUPPORT_NOT_REVIEWED"]=="NOT_REVIEWED" for x in rows))

    def test_csv_formula_injection_neutralized(self):
        r=execute()
        r["all_244_source_URL_and_reading_work_orders_NOT_APPROVED"][0]["source_id"]="=2+2"
        seal(r)
        rows=list(csv.DictReader(io.StringIO(gate.csv_tasks(r))))
        self.assertTrue(rows[0]["source_id"].startswith("'="))

    def test_same_url_distinct_identities_without_alias(self):
        parts=list(fixture())
        source=parts[0]
        item=source["all_original_and_RC_source_review_work_orders_NOT_APPROVED"][2]
        item["candidate_complete_reading_UNABRIDGED"]["url"]="https://www.cdc.gov/a"
        item["candidate_exact_url_NO_ALIAS"]="https://www.cdc.gov/a"
        item["candidate_record_sha256"]=gate.digest(item["candidate_complete_reading_UNABRIDGED"])
        source["counts"]["RC_shared_exact_url_groups"]=1
        source["RC_shared_exact_URL_groups_UNRESOLVED"]=[{
            "exact_url_NOT_ALIASED":"https://www.cdc.gov/a",
            "distinct_origin_scoped_identities_NOT_MERGED":[
                {"source_origin":"base","source_id":"alpha"},
                {"source_origin":"food","source_id":"alpha"}],
            "human_review_state":"NOT_REVIEWED"}]
        reseal_document_reports(parts,source=True)
        # R68 cached variants must be reconciled to the edited R67 source rows.
        for d in parts[1]["all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED"]:
            for use in d["all_RC_source_uses_and_unabridged_readings_NOT_APPROVED"]:
                if use["source_id"]=="alpha":
                    use["all_candidate_source_variants_UNABRIDGED_NOT_APPROVED"][1]=item
            d["task_sha256"]=gate.digest({k:v for k,v in d.items() if k!="task_sha256"})
        for d68,d69 in zip(parts[1]["all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED"],
                          parts[2]["all_document_DOM_text_and_citation_review_orders_NOT_APPROVED"]):
            d69["R68_task_sha256"]=d68["task_sha256"]
        reseal_document_reports(parts,doc=True)
        r=execute(parts)
        self.assertEqual(r["counts"]["RC_shared_exact_URL_groups_NOT_RESOLVED"],1)
        self.assertEqual(len(r["all_2173_citation_URL_identity_work_orders_NOT_APPROVED"][0]
                             ["all_candidate_exact_urls_NOT_DEDUPLICATED"]),2)

    def test_missing_source_ref_fails(self):
        r=list(fixture())
        r[0]["all_original_and_RC_source_review_work_orders_NOT_APPROVED"].pop()
        reseal_document_reports(r,source=True)
        with self.assertRaises(gate.ReviewHold):
            execute(r)

    def test_fake_source_human_approval_fails(self):
        r=list(fixture())
        r[0]["all_original_and_RC_source_review_work_orders_NOT_APPROVED"][0]["human_link_review"]="APPROVED"
        reseal_document_reports(r,source=True)
        with self.assertRaises(gate.ReviewHold):
            execute(r)

    def test_fake_source_metadata_human_link_fails(self):
        r=list(fixture())
        s=r[0]["all_original_and_RC_source_review_work_orders_NOT_APPROVED"][0]
        s["candidate_complete_reading_UNABRIDGED"]["human_link_check"]=True
        s["candidate_record_sha256"]=gate.digest(s["candidate_complete_reading_UNABRIDGED"])
        reseal_document_reports(r,source=True)
        with self.assertRaises(gate.ReviewHold):
            execute(r)

    def test_forged_fingerprint_fails(self):
        r=list(fixture())
        r[0]["fingerprint_sha256"]="0"*64
        with self.assertRaises(gate.ReviewHold):
            execute(r)

    def test_forged_release_state_fails(self):
        r=list(fixture())
        r[1]["may_publish"]=True
        seal(r[1])
        with self.assertRaises(gate.ReviewHold):
            execute(r)

    def test_wrong_custody_parent_pointer_fails(self):
        r=list(fixture())
        r[2]["R68_exact_original_RC_custody_fingerprint_sha256"]="0"*64
        seal(r[2])
        with self.assertRaises(gate.ReviewHold):
            execute(r)

    def test_changed_document_task_requires_new_dom_pointer(self):
        r=list(fixture())
        r[1]["all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED"][0]["RC_body_utf8_sha256"]="b"*64
        d=r[1]["all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED"][0]
        d["task_sha256"]=gate.digest({k:v for k,v in d.items() if k!="task_sha256"})
        reseal_document_reports(r,doc=True)
        with self.assertRaises(gate.ReviewHold):
            execute(r)

    def test_changed_citation_offset_fails(self):
        r=list(fixture())
        r[2]["all_document_DOM_text_and_citation_review_orders_NOT_APPROVED"][0]["citation_visibility_audit_NOT_BROWSER_PROOF"][0]["unicode_codepoint_offset"]=7
        seal(r[2])
        with self.assertRaises(gate.ReviewHold):
            execute(r)

    def test_changed_citation_source_id_fails(self):
        r=list(fixture())
        r[2]["all_document_DOM_text_and_citation_review_orders_NOT_APPROVED"][0]["citation_visibility_audit_NOT_BROWSER_PROOF"][0]["source_id"]="beta"
        seal(r[2])
        with self.assertRaises(gate.ReviewHold):
            execute(r)

    def test_unsanctioned_merged_source_variant_fails(self):
        r=list(fixture())
        r[2]["all_document_DOM_text_and_citation_review_orders_NOT_APPROVED"][0]["citation_visibility_audit_NOT_BROWSER_PROOF"][0]["all_source_identity_variants_NOT_ALIASED"]=[["base","alpha"]]
        seal(r[2])
        with self.assertRaises(gate.ReviewHold):
            execute(r)

    def test_changed_preferred_source_fails(self):
        r=list(fixture())
        r[2]["all_document_DOM_text_and_citation_review_orders_NOT_APPROVED"][0]["citation_visibility_audit_NOT_BROWSER_PROOF"][0]["candidate_source_identity_OR_NULL"]=["food","alpha"]
        seal(r[2])
        with self.assertRaises(gate.ReviewHold):
            execute(r)

    def test_duplicate_draft_url_fails(self):
        r=list(fixture())
        first=r[1]["all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED"][0]
        second=r[1]["all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED"][1]
        second["proposed_WordPress_url_DRAFT_ONLY"]=first["proposed_WordPress_url_DRAFT_ONLY"]
        second["task_sha256"]=gate.digest({k:v for k,v in second.items() if k!="task_sha256"})
        reseal_document_reports(r,doc=True)
        with self.assertRaises(gate.ReviewHold):
            execute(r)

    def test_removed_dom_task_fails(self):
        r=list(fixture())
        r[2]["all_document_DOM_text_and_citation_review_orders_NOT_APPROVED"].pop()
        seal(r[2])
        with self.assertRaises(gate.ReviewHold):
            execute(r)

    def test_removed_citation_fails(self):
        r=list(fixture())
        r[2]["all_document_DOM_text_and_citation_review_orders_NOT_APPROVED"][0]["citation_visibility_audit_NOT_BROWSER_PROOF"].pop()
        seal(r[2])
        with self.assertRaises(gate.ReviewHold):
            execute(r)

    def test_false_dom_approval_fails(self):
        r=list(fixture())
        r[2]["all_document_DOM_text_and_citation_review_orders_NOT_APPROVED"][0]["human_source_review"]="APPROVED"
        seal(r[2])
        with self.assertRaises(gate.ReviewHold):
            execute(r)

    def test_wrong_shared_url_group_fails(self):
        r=list(fixture())
        r[0]["counts"]["RC_shared_exact_url_groups"]=1
        r[0]["RC_shared_exact_URL_groups_UNRESOLVED"]=[{
            "exact_url_NOT_ALIASED":"https://www.cdc.gov/a",
            "distinct_origin_scoped_identities_NOT_MERGED":[
                {"source_origin":"base","source_id":"alpha"}],
            "human_review_state":"NOT_REVIEWED"}]
        reseal_document_reports(r,source=True)
        with self.assertRaises(gate.ReviewHold):
            execute(r)

    def test_no_aliasing_case_changed_url(self):
        r=list(fixture())
        s=r[0]["all_original_and_RC_source_review_work_orders_NOT_APPROVED"][2]
        s["candidate_complete_reading_UNABRIDGED"]["url"]="https://WWW.FDA.gov/c"
        s["candidate_exact_url_NO_ALIAS"]="https://WWW.FDA.gov/c"
        s["candidate_record_sha256"]=gate.digest(s["candidate_complete_reading_UNABRIDGED"])
        # Source documentation must be fresh; do not bless an old snapshot.
        reseal_document_reports(r,source=True)
        with self.assertRaises(gate.ReviewHold):
            execute(r)

    def test_non_https_is_review_blocker_not_human_result(self):
        blocked,signals=gate.classify_url("http://www.cdc.gov/a")
        self.assertIn("NON_HTTPS_OR_MISSING_HOST",blocked)
        self.assertNotIn("REVIEWED", signals)

    def test_url_lexical_does_not_bless_redirects(self):
        b,s=gate.classify_url("https://example.gov/?redirect=https%3A%2F%2Fother.org")
        self.assertIn("REDIRECT_PARAMETER_NEEDS_TARGET_REVIEW",s)


# Each case is an independently reported unittest, not a single giant loop.
URL_CASES = [
    ("normal_https","https://www.cdc.gov/water",None),
    ("https_case","HTTPS://example.gov/a","NON_HTTPS_OR_MISSING_HOST"),
    ("http","http://www.cdc.gov/a","NON_HTTPS_OR_MISSING_HOST"),
    ("relative","/records/entry","NON_HTTPS_OR_MISSING_HOST"),
    ("javascript","javascript:alert(1)","NON_HTTPS_OR_MISSING_HOST"),
    ("mailto","mailto:editor@example.gov","NON_HTTPS_OR_MISSING_HOST"),
    ("empty","", "MISSING_SOURCE_URL"),
    ("userinfo","https://user:pass@example.gov/a","URL_CONTAINS_USERINFO"),
    ("userinfo_at","https://user@example.gov/a","URL_CONTAINS_USERINFO"),
    ("loopback_ipv4","https://127.0.0.1/a","NON_PUBLIC_IP_ADDRESS"),
    ("loopback_ipv6","https://[::1]/a","NON_PUBLIC_IP_ADDRESS"),
    ("private_ipv4","https://192.168.1.1/a","NON_PUBLIC_IP_ADDRESS"),
    ("linklocal","https://169.254.169.254/latest","NON_PUBLIC_IP_ADDRESS"),
    ("localhost","https://localhost/a","PRIVATE_OR_LOCAL_HOSTNAME"),
    ("dotlocal","https://printer.local/a","PRIVATE_OR_LOCAL_HOSTNAME"),
    ("dotinternal","https://portal.internal/a","PRIVATE_OR_LOCAL_HOSTNAME"),
    ("dottest","https://example.test/a","PRIVATE_OR_LOCAL_HOSTNAME"),
    ("single_label","https://intranet/a","SINGLE_LABEL_HOSTNAME"),
    ("double_dot","https://foo..com/a","INVALID_DNS_HOST_LABEL"),
    ("leading_hyphen","https://-example.org/a","INVALID_DNS_HOST_LABEL"),
    ("trailing_hyphen","https://example-.org/a","INVALID_DNS_HOST_LABEL"),
    ("newline","https://example.gov/a\nb","UNSAFE_RAW_URL_CHARACTERS_OR_LENGTH"),
    ("space","https://example.gov/some page","UNSAFE_RAW_URL_CHARACTERS_OR_LENGTH"),
    ("tab","https://example.gov/a\tb","UNSAFE_RAW_URL_CHARACTERS_OR_LENGTH"),
    ("quote","https://example.gov/a\"b","UNSAFE_RAW_URL_CHARACTERS_OR_LENGTH"),
    ("html_markup","https://example.gov/<img>","UNSAFE_RAW_URL_CHARACTERS_OR_LENGTH"),
    ("encoded_newline","https://example.gov/%0a","PERCENT_DECODED_CONTROL_OR_MARKUP_CHARACTER"),
    ("encoded_quote","https://example.gov/%22","PERCENT_DECODED_CONTROL_OR_MARKUP_CHARACTER"),
    ("encoded_space","https://example.gov/a%20b",None),
    ("bad_port","https://example.gov:bad/a","MALFORMED_URL_AUTHORITY"),
    ("broken_ipv6","https://[::1/a","MALFORMED_URL_AUTHORITY"),
    ("ftp","ftp://example.gov/a","NON_HTTPS_OR_MISSING_HOST"),
    ("file","file:///etc/passwd","NON_HTTPS_OR_MISSING_HOST"),
    ("protocol_relative","//example.gov/a","NON_HTTPS_OR_MISSING_HOST"),
    ("percent_bad_utf8","https://example.gov/%FF","INVALID_PERCENT_ENCODING_UTF8"),
    ("empty_host","https:///missing","NON_HTTPS_OR_MISSING_HOST"),
    ("control_zero","https://example.gov/\x00","UNSAFE_RAW_URL_CHARACTERS_OR_LENGTH"),
    ("backslash","https://example.gov/a\\b","UNSAFE_RAW_URL_CHARACTERS_OR_LENGTH"),
    ("apostrophe","https://example.gov/'a'","UNSAFE_RAW_URL_CHARACTERS_OR_LENGTH"),
    ("ftp_password","ftp://u:p@example.org/a","NON_HTTPS_OR_MISSING_HOST"),
    ("private_ipv6","https://[fd00::1]/a","NON_PUBLIC_IP_ADDRESS"),
    ("long_url","https://example.gov/"+("a"*8200),"UNSAFE_RAW_URL_CHARACTERS_OR_LENGTH"),
    ("bad_label","https://exam_ple.gov/a","INVALID_DNS_HOST_LABEL"),
    ("host_unicode","https://exämple.gov/a",None),
    ("query_credential","https://example.gov/a?api_key=abc",None),
    ("redirect","https://example.gov/a?next=%2Ffoo",None),
    ("deep_fragment","https://example.gov/a#paragraph",None),
    ("trailing_dot","https://example.gov./a",None),
    ("https_port_443","https://example.gov:443/a",None),
    ("https_port_8443","https://example.gov:8443/a",None),
    ("public_ip","https://8.8.8.8/a",None),
]


def generate_url_test(url,expected):
    def run(self):
        blocked,review=gate.classify_url(url)
        if expected is None:
            self.assertEqual(blocked,[],(url,blocked))
        else:
            self.assertIn(expected,blocked,(url,blocked))
        self.assertIsInstance(review,list)
    return run


for test_name,url,expected in URL_CASES:
    setattr(IntegrationCases,"test_url_"+test_name,generate_url_test(url,expected))


if __name__=="__main__":
    unittest.main()
