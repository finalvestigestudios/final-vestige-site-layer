"""R74 isolated synthetic tests using pre-existing signed R73/R72 fixtures.

No real articles, sources, URLs, files, or human approval states are modified.
"""
from __future__ import annotations
from copy import deepcopy
import csv
import importlib.util
import io
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

gate=load(ROOT/"tools"/"r74_quantity_context_custody.py","r74_under_test")
prior=load(ROOT/"tests"/"test_r73_consequential_language_review.py","r73_fixture_for_r74")
N=(1,1,3,3,4)

def sample():
    return prior.gate.construct(prior.sample(),expected=N)

def reseal(row,key="fingerprint_sha256"):
    row.pop(key,None)
    row[key]=gate.digest(row)
    return row

def change_source(p,key,val):
    p["all_244_unabridged_source_readings_NOT_REVIEWED"][0][key]=val

def change_block(p,key,val):
    item=p["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"][0]
    item[key]=val
    reseal(item,"task_sha256")

def change_doc(p,key,val):
    p["all_document_block_orders_NOT_REVIEWED"][0][key]=val

def remove_first_real_citation(p):
    # R73 synthetic fixture's first block has no citation. Mutate a real edge.
    item=next(b for b in p["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"]
              if b["local_citations_NOT_CLAIM_SUPPORT_PROOF"])
    item["local_citations_NOT_CLAIM_SUPPORT_PROOF"]=[]
    reseal(item,"task_sha256")

def change_action(p,key,val):
    item=p["consequential_action_wording_review_packets_NOT_APPROVED"][0]
    item[key]=val
    reseal(item,"packet_sha256")

class Baseline(unittest.TestCase):
    def make(self,p=None):
        return gate.construct(sample() if p is None else p,expected=N)

    def test_baseline_signed(self):
        gate.sealed(self.make(),gate.SCHEMA)

    def test_source_census(self):
        r=self.make()
        self.assertEqual(r["counts"]["complete_origin_scoped_source_readings"],3)

    def test_citation_census(self):
        self.assertEqual(self.make()["counts"]["citation_occurrences"],3)

    def test_block_census(self):
        self.assertEqual(self.make()["counts"]["unabridged_DOM_blocks"],4)

    def test_article_tool_census(self):
        r=self.make()
        self.assertEqual((r["counts"]["articles"],r["counts"]["tools"]),(1,1))

    def test_machine_only_hold(self):
        r=self.make()
        self.assertEqual(r["release_state"],"HOLD")
        self.assertTrue(all(r[k] is False for k in gate.HOLD))
        self.assertEqual(r["counts"]["human_qualified_safety_reviews"],0)

    def test_immutable_full_research_source_readings(self):
        p=sample();out=self.make(p)
        self.assertEqual(p["all_244_unabridged_source_readings_NOT_REVIEWED"],
                         out["all_244_unabridged_source_readings_NOT_REVIEWED"])

    def test_immutable_full_unicode_dom_blocks(self):
        p=sample();out=self.make(p)
        self.assertEqual(p["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"],
                         out["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"])

    def test_immutable_action_packets(self):
        p=sample();out=self.make(p)
        self.assertEqual(p["consequential_action_wording_review_packets_NOT_APPROVED"],
                         out["all_975_action_triage_packets_NOT_APPROVED"])

    def test_complete_source_collision_custody(self):
        p=sample();out=self.make(p)
        self.assertEqual(p["shared_URL_scope_collisions_NOT_REVIEWED"],
                         out["shared_URL_scope_collisions_NOT_REVIEWED"])
        self.assertEqual(p["reused_ID_scope_collisions_NOT_REVIEWED"],
                         out["reused_ID_scope_collisions_NOT_REVIEWED"])

    def test_no_parent_modification(self):
        p=sample();original=deepcopy(p)
        self.make(p)
        self.assertEqual(p,original)

    def test_output_no_mutable_alias(self):
        p=sample();out=self.make(p)
        p["all_document_block_orders_NOT_REVIEWED"][0]["slug"]="tampered"
        self.assertNotEqual(p["all_document_block_orders_NOT_REVIEWED"],
                            out["all_document_block_orders_NOT_REVIEWED"])

    def test_same_parent_gives_same_output(self):
        p=sample()
        self.assertEqual(self.make(p),self.make(p))

    def test_private_csv_never_approval(self):
        r=self.make()
        rows=list(csv.DictReader(io.StringIO(gate.csv_review_packets(r))))
        self.assertEqual(len(rows),r["counts"]["DOM_blocks_with_matching_numeric_units"])
        self.assertTrue(all(x["review_status"]=="NOT_REVIEWED" for x in rows))

    def test_csv_untrusted_formula_prefix(self):
        r=self.make()
        # A standalone synthetic work order, never an imported approval.
        fake={"kind":"article","slug":"first","draft_URL_PRIVATE":"/preparedness/first/",
              "block_id":"synthetic-only","full_DOM_text_UNABRIDGED_NOT_VERIFIED":"\u2060=2+2",
              "quantities_EXACT_TEXT_NO_UNIT_CONVERSION":[],
              "local_cited_source_variants_NOT_CLAIM_SUPPORT":[],
              "caution_wording_PRESENT_NOT_SUFFICIENT":False}
        r["exact_quantity_review_packets_NOT_APPROVED"].insert(0,fake)
        reseal(r)
        rows=list(csv.DictReader(io.StringIO(gate.csv_review_packets(r))))
        self.assertTrue(rows[0]["full_DOM_text_UNVERIFIED"].startswith("'"))

    def test_unicode_offsets_and_unabridged_context(self):
        r=self.make()
        for p in r["exact_quantity_review_packets_NOT_APPROVED"]:
            for span in p["quantities_EXACT_TEXT_NO_UNIT_CONVERSION"]:
                self.assertEqual(p["full_DOM_text_UNABRIDGED_NOT_VERIFIED"][
                    span["start_unicode"]:span["end_unicode"]],span["exact_text_NOT_ADVICE"])

    def test_unicode_temperature_tokens(self):
        self.assertEqual([x["exact_text_NOT_ADVICE"] for x in
                          gate.quantities("20°C or 40°F")],["20°C","40°F"])

    def test_fraction_and_en_dash_range(self):
        self.assertEqual([x["exact_text_NOT_ADVICE"] for x in
                          gate.quantities("Use 1/2 gallon or 3–4 liters.")],
                         ["1/2 gallon","3–4 liters"])

    def test_singular_plural_route_only(self):
        self.assertEqual(gate.unit_route("gallons"),gate.unit_route("gallon"))

    def test_no_cross_unit_conversion(self):
        self.assertNotEqual(gate.unit_route("gallons"),gate.unit_route("liters"))
        self.assertNotEqual(gate.unit_route("mg"),gate.unit_route("g"))

    def test_no_conclusion_from_numerical_phrase(self):
        self.assertEqual(gate.quantities("Review the guide before acting."),[])

    def test_not_authorized_from_caution_wording(self):
        r=self.make()
        self.assertTrue(all(p["qualified_safety_review"]=="NOT_REVIEWED"
                            for p in r["exact_quantity_review_packets_NOT_APPROVED"]))

    def test_wrong_expected_tuple_fails(self):
        for n in ([1,1,3,3,4],(True,1,3,3,4),(1,1,3,3,0),None):
            with self.subTest(n=n),self.assertRaises(gate.Hold):
                gate.construct(sample(),expected=n)

FAULTS={
    "issue_changed":lambda p:p.update(issue=9),
    "schema_changed":lambda p:p.update(schema="public"),
    "state_pass":lambda p:p.update(release_state="PASS"),
    "machine_only_false":lambda p:p.update(machine_only=False),
    "fake_publish_approval":lambda p:p.update(may_publish=True),
    "fake_qd_approval":lambda p:p.update(independent_QD_approval=True),
    "fake_safety_clearance":lambda p:p.update(qualified_safety_clearance=True),
    "fake_source_approval":lambda p:p.update(human_source_links_verified=True),
    "article_census":lambda p:p["counts"].update(articles=2),
    "tool_census":lambda p:p["counts"].update(tools=2),
    "source_census":lambda p:p["counts"].update(complete_distinct_origin_scoped_source_readings=4),
    "citation_census":lambda p:p["counts"].update(citation_occurrences=4),
    "block_census":lambda p:p["counts"].update(unabridged_DOM_review_tasks=5),
    "claim_approval_count":lambda p:p["counts"].update(human_claim_support_reviews=1),
    "safety_approval_count":lambda p:p["counts"].update(human_qualified_safety_reviews=1),
    "qd_approval_count":lambda p:p["counts"].update(independent_QD_approvals=1),
    "action_count":lambda p:p["counts"].update(consequential_action_wording_triage_packets=200),
    "action_queue_count":lambda p:p["counts"].update(topic_with_action_cue=200),
    "topic_partition_count":lambda p:p["counts"].update(general_editorial_blocks=400),
    "source_removed":lambda p:p["all_244_unabridged_source_readings_NOT_REVIEWED"].pop(),
    "source_duplicated":lambda p:p["all_244_unabridged_source_readings_NOT_REVIEWED"].__setitem__(
        1,deepcopy(p["all_244_unabridged_source_readings_NOT_REVIEWED"][0])),
    "source_reordered":lambda p:p["all_244_unabridged_source_readings_NOT_REVIEWED"].reverse(),
    "source_origin_empty":lambda p:change_source(p,"source_origin",""),
    "source_id_empty":lambda p:change_source(p,"source_id",""),
    "source_url_drift":lambda p:change_source(p,"exact_URL_NO_ALIAS","https://incorrect.example/"),
    "source_reading_sha_changed":lambda p:change_source(p,"candidate_reading_sha256","f"*64),
    "source_review_approved":lambda p:change_source(p,"human_source_and_claim_review","APPROVED"),
    "source_safety_approved":lambda p:change_source(p,"qualified_safety_review","SAFE"),
    "source_original_sha_forged":lambda p:change_source(p,"original_reading_sha256","f"*64),
    "source_original_reading_forged":lambda p:change_source(p,
        "original_reading_UNABRIDGED_NOT_HUMAN_VERIFIED",{"fake":"historical"}),
    "block_removed":lambda p:p["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"].pop(),
    "block_duplicated":lambda p:p["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"].append(
        deepcopy(p["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"][0])),
    "block_reordered":lambda p:p["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"].reverse(),
    "block_text_rewritten":lambda p:change_block(p,
        "DOM_text_UNABRIDGED_NOT_BROWSER_OR_SAFETY_VERIFIED","Changed 5 gallons."),
    "block_hash_rewritten":lambda p:change_block(p,"DOM_text_sha256","f"*64),
    "block_claim_approved":lambda p:change_block(p,"human_claim_support_review","APPROVED"),
    "block_safety_approved":lambda p:change_block(p,"qualified_safety_review","SAFE"),
    "block_qd_approved":lambda p:change_block(p,"independent_QD_review","PASS"),
    "block_slug_changed":lambda p:change_block(p,"slug","not-the-original"),
    "block_url_changed":lambda p:change_block(p,"private_draft_url","/live/"),
    "block_id_changed":lambda p:change_block(p,"block_id","not-original"),
    "block_bad_topics":lambda p:change_block(p,"topic_signals_TRIAGE_NOT_SAFETY_VERDICT",["z","a"]),
    "block_duplicate_topics":lambda p:change_block(p,"topic_signals_TRIAGE_NOT_SAFETY_VERDICT",["x","x"]),
    "block_citation_removed":lambda p:remove_first_real_citation(p),
    "doc_removed":lambda p:p["all_document_block_orders_NOT_REVIEWED"].pop(),
    "doc_slug_changed":lambda p:change_doc(p,"slug","wrong"),
    "doc_public_url":lambda p:change_doc(p,"draft_url_NOT_PUBLIC","https://published.example/"),
    "doc_duplicate_url":lambda p:change_doc(p,"draft_url_NOT_PUBLIC",
        p["all_document_block_orders_NOT_REVIEWED"][1]["draft_url_NOT_PUBLIC"]),
    "doc_block_order_missing":lambda p:change_doc(p,"block_ids_in_original_order",["not-a-block"]),
    "doc_safety_approved":lambda p:change_doc(p,"reviewer_state","APPROVED"),
    "action_removed":lambda p:p["consequential_action_wording_review_packets_NOT_APPROVED"].pop(),
    "action_wrong_text":lambda p:change_action(p,"full_DOM_text_UNABRIDGED_NOT_SAFETY_VERIFIED","Replaced"),
    "action_wrong_id":lambda p:change_action(p,"block_id","rewritten"),
    "action_fake_safety":lambda p:change_action(p,"qualified_safety_review","SAFE"),
    "action_wrong_url":lambda p:change_action(p,"private_draft_url_NOT_PUBLIC","/public/"),
}

def make_mutation_test(name,damager):
    def case(self):
        row=sample()
        damager(row)
        reseal(row)
        with self.assertRaises(gate.Hold,msg=name):
            gate.construct(row,expected=N)
    case.__name__="test_mutation_"+name
    return case

class Adversarial(unittest.TestCase):
    pass

for _name,_damager in FAULTS.items():
    setattr(Adversarial,"test_mutation_"+_name,make_mutation_test(_name,_damager))

if __name__=="__main__":
    unittest.main()
