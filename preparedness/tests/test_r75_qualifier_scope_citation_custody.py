"""R75 synthetic review-custody and adversarial tests; no production article writes."""
from __future__ import annotations

from copy import deepcopy
import csv
import importlib.util
import io
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

def load(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

gate=load(ROOT/"tools"/"r75_qualifier_scope_citation_custody.py","r75_under_test")
previous=load(ROOT/"tests"/"test_r74_quantity_context_custody.py","r74_synthetic_for_r75")
N=(1,1,3,3,4)

def sample():
    return previous.gate.construct(previous.sample(),expected=N)

def synthetic_with_numeric_context():
    """Derive a quantity-bearing fixture solely from a sealed synthetic R72 corpus."""
    r72=previous.prior.sample()
    b=r72["all_unabridged_DOM_block_citation_tasks_NOT_APPROVED"][0]
    t=b["DOM_text_UNABRIDGED_NOT_BROWSER_OR_SAFETY_VERIFIED"]+" Keep 2 days for test routing."
    b["DOM_text_UNABRIDGED_NOT_BROWSER_OR_SAFETY_VERIFIED"]=t
    b["DOM_text_sha256"]=gate.text_digest(t)
    b["task_sha256"]=gate.digest({k:v for k,v in b.items() if k!="task_sha256"})
    r72["fingerprint_sha256"]=gate.digest({k:v for k,v in r72.items() if k!="fingerprint_sha256"})
    r73=previous.prior.gate.construct(r72,expected=N)
    row=previous.gate.construct(r73,expected=N)
    assert row["exact_quantity_review_packets_NOT_APPROVED"],"synthetic numeric fixture missing"
    return row

def reseal(r,key="fingerprint_sha256"):
    r.pop(key,None)
    r[key]=gate.digest(r)
    return r

def source_mutation(p,key,value):
    p["all_244_unabridged_source_readings_NOT_REVIEWED"][0][key]=value

def block_mutation(p,key,value):
    b=p["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"][0]
    b[key]=value
    reseal(b,"task_sha256")

def doc_mutation(p,key,value):
    p["all_document_block_orders_NOT_REVIEWED"][0][key]=value

def first_cited(p):
    return next(b for b in p["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"]
                if b["local_citations_NOT_CLAIM_SUPPORT_PROOF"])

def citation_mutation(p,key,value):
    b=first_cited(p)
    b["local_citations_NOT_CLAIM_SUPPORT_PROOF"][0][key]=value
    reseal(b,"task_sha256")

def source_variant_mutation(p,key,value):
    b=first_cited(p)
    b["local_citations_NOT_CLAIM_SUPPORT_PROOF"][0][
        "origin_scoped_source_variants_NOT_ALIASED"][0][key]=value
    reseal(b,"task_sha256")

def action_mutation(p,key,value):
    a=p["all_975_action_triage_packets_NOT_APPROVED"][0]
    a[key]=value
    reseal(a,"packet_sha256")

def qty_mutation(p,key,value):
    a=p["exact_quantity_review_packets_NOT_APPROVED"][0]
    a[key]=value
    reseal(a,"packet_sha256")

class Baseline(unittest.TestCase):
    def make(self,parent=None):
        return gate.construct(sample() if parent is None else parent,expected=N)

    def test_parent_r74_sealed(self):
        gate.sealed(sample(),gate.PARENT)

    def test_output_r75_sealed(self):
        gate.sealed(self.make(),gate.SCHEMA)

    def test_four_complete_dom_blocks(self):
        self.assertEqual(self.make()["counts"]["unabridged_DOM_blocks"],4)

    def test_all_sources_preserved(self):
        p=sample()
        self.assertEqual(p["all_244_unabridged_source_readings_NOT_REVIEWED"],
                         self.make(p)["all_244_unabridged_source_readings_NOT_REVIEWED"])

    def test_all_blocks_preserved(self):
        p=sample()
        self.assertEqual(p["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"],
                         self.make(p)["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"])

    def test_all_documents_preserved(self):
        p=sample()
        self.assertEqual(p["all_document_block_orders_NOT_REVIEWED"],
                         self.make(p)["all_document_block_orders_NOT_REVIEWED"])

    def test_all_actions_preserved(self):
        p=sample()
        self.assertEqual(p["all_975_action_triage_packets_NOT_APPROVED"],
                         self.make(p)["all_975_action_triage_packets_NOT_APPROVED"])

    def test_all_quantities_preserved(self):
        p=sample()
        self.assertEqual(p["exact_quantity_review_packets_NOT_APPROVED"],
                         self.make(p)["all_numeric_unit_packets_NOT_APPROVED"])

    def test_collision_and_uncited_records_preserved(self):
        p=sample();x=self.make(p)
        for old,new in (("shared_URL_scope_collisions_NOT_REVIEWED","shared_URL_scope_collisions_NOT_REVIEWED"),
                        ("reused_ID_scope_collisions_NOT_REVIEWED","reused_ID_scope_collisions_NOT_REVIEWED"),
                        ("uncited_source_readings_NOT_REVIEWED","uncited_source_readings_NOT_REVIEWED"),
                        ("citations_without_DOM_block_UNRESOLVED","citations_without_DOM_block_UNRESOLVED")):
            self.assertEqual(p[old],x[new])

    def test_full_citation_conservation(self):
        self.assertEqual(self.make()["counts"]["citation_occurrences"],3)

    def test_all_safety_permissions_false(self):
        r=self.make()
        self.assertEqual(r["release_state"],"HOLD")
        self.assertTrue(all(r[k] is False for k in gate.HOLD_KEYS))
        self.assertEqual(r["counts"]["qualified_safety_reviews"],0)

    def test_keyword_locators_return_unicode_exact_substrings(self):
        t="ℹ️ Never use. Consult a pharmacist if in doubt."
        for span in gate.qualifier_spans(t):
            self.assertEqual(t[span["start_unicode"]:span["end_unicode"]],
                             span["literal_NOT_SAFETY_ASSESSMENT"])

    def test_prohibition_and_except_keywords(self):
        hits=gate.qualifier_spans("Do not use it, except when directed.")
        self.assertTrue(any(x["category_LEXICAL_ONLY"]=="PROHIBITION_LEXEME" for x in hits))
        self.assertTrue(any(x["category_LEXICAL_ONLY"]=="EXCEPTION_LEXEME" for x in hits))

    def test_longest_only_if_preferred_over_if(self):
        hits=gate.qualifier_spans("Only if requested.")
        self.assertEqual(len(hits),1)
        self.assertEqual(hits[0]["literal_NOT_SAFETY_ASSESSMENT"],"Only if")

    def test_empty_and_no_keyword(self):
        self.assertEqual(gate.qualifier_spans(""),[])
        self.assertEqual(gate.qualifier_spans("Ordinary archival heading."),[])

    def test_synthetic_uncertainty_lexemes_are_not_approval(self):
        self.assertIn("UNCERTAINTY_LEXEME",
                      {x["category_LEXICAL_ONLY"] for x in gate.qualifier_spans(
                       "An uncertain result may differ.")})
        self.assertEqual(self.make()["counts"]["qualified_safety_reviews"],0)

    def test_source_reader_absence_is_not_support(self):
        r=self.make()
        self.assertTrue(all(x["human_claim_support_review"]=="NOT_REVIEWED"
            for x in r["action_or_quantity_qualifier_context_queue_NOT_APPROVED"]))

    def test_union_of_previous_review_queues(self):
        p=sample();r=self.make(p)
        keys=lambda arr:{(x["kind"],x["slug"],x["block_id"]) for x in arr}
        self.assertEqual(keys(r["action_or_quantity_qualifier_context_queue_NOT_APPROVED"]),
                         keys(p["all_975_action_triage_packets_NOT_APPROVED"]) |
                         keys(p["exact_quantity_review_packets_NOT_APPROVED"]))

    def test_neighbor_custody_remains_in_same_doc(self):
        p=sample();r=self.make(p)
        index={(x["kind"],x["slug"],x["block_id"]):x for x in
               p["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"]}
        for task in r["action_or_quantity_qualifier_context_queue_NOT_APPROVED"]:
            for neighbor in task["immediate_neighbor_qualifiers_NOT_SAFETY_PROOF"]:
                original=index[(task["kind"],task["slug"],neighbor["block_id"])]
                self.assertEqual(neighbor["original_R72_block_sha256"],original["task_sha256"])
                self.assertEqual(neighbor["unabridged_nearby_text_NOT_EVIDENCE"],
                                 original["DOM_text_UNABRIDGED_NOT_BROWSER_OR_SAFETY_VERIFIED"])

    def test_no_parent_mutation(self):
        p=sample();copy=deepcopy(p);self.make(p);self.assertEqual(p,copy)

    def test_no_output_alias_to_input(self):
        p=sample();r=self.make(p)
        p["all_document_block_orders_NOT_REVIEWED"][0]["slug"]="changed-after-export"
        self.assertNotEqual(p["all_document_block_orders_NOT_REVIEWED"],
                            r["all_document_block_orders_NOT_REVIEWED"])

    def test_repeat_generation_stable(self):
        p=sample()
        self.assertEqual(self.make(p),self.make(p))

    def test_review_csv_has_no_approvals(self):
        r=self.make()
        rows=list(csv.DictReader(io.StringIO(gate.csv_review_worklist(r))))
        self.assertEqual(len(rows),r["counts"]["union_action_or_quantity_review_queue"])
        self.assertTrue(all(x["qualified_safety_review"]=="NOT_REVIEWED" for x in rows))

    def test_review_csv_formula_guard(self):
        r=self.make()
        row=deepcopy(r["action_or_quantity_qualifier_context_queue_NOT_APPROVED"][0])
        row["full_DOM_text_UNABRIDGED_NOT_SAFETY_APPROVED"]=" \u2060=IMPORTXML(A1)"
        r["action_or_quantity_qualifier_context_queue_NOT_APPROVED"].insert(0,row)
        reseal(r)
        rows=list(csv.DictReader(io.StringIO(gate.csv_review_worklist(r))))
        self.assertTrue(rows[0]["full_text_NOT_APPROVED"].startswith("'"))

    def test_synthetic_numeric_context_packet_is_generated(self):
        p=synthetic_with_numeric_context()
        self.assertGreater(p["counts"]["numeric_unit_occurrences"],0)
        self.assertTrue(gate.construct(p,expected=N)[
            "action_or_quantity_qualifier_context_queue_NOT_APPROVED"])

    def test_synthetic_numeric_context_remains_unapproved(self):
        p=synthetic_with_numeric_context()
        self.assertEqual(gate.construct(p,expected=N)["counts"]["qualified_safety_reviews"],0)

    def test_boolean_count_not_used_as_approval(self):
        r=self.make()
        self.assertIs(type(r["counts"]["union_without_same_block_lexical_qualifier_triage"]),int)
        self.assertTrue(all(x["qualified_safety_review"]=="NOT_REVIEWED"
            for x in r["all_qualifier_locator_packets_NOT_SAFETY_CLEARANCE"]))

    def test_invalid_expected_contracts_fail(self):
        for bad in (None,[1,1,3,3,4],(True,1,3,3,4),(1,1,3,3,0)):
            with self.subTest(bad=bad),self.assertRaises(gate.Hold):
                gate.construct(sample(),expected=bad)

# Every fault is applied to a fully synthetic, sealed R74 object. Re-sealing
# the parent is deliberate: tests check structural invariants beyond the envelope.
FAULTS={
    "issue_changed":lambda p:p.update(issue=0),
    "schema_changed":lambda p:p.update(schema="public"),
    "release_published":lambda p:p.update(release_state="PUBLISHED"),
    "machine_not_readonly":lambda p:p.update(machine_only=False),
    "publish_claim":lambda p:p.update(may_publish=True),
    "qd_claim":lambda p:p.update(independent_QD_approval=True),
    "human_link_claim":lambda p:p.update(human_source_links_verified=True),
    "qualified_safety_claim":lambda p:p.update(qualified_safety_clearance=True),
    "article_count":lambda p:p["counts"].update(articles=2),
    "tools_count":lambda p:p["counts"].update(tools=2),
    "source_count":lambda p:p["counts"].update(complete_origin_scoped_source_readings=4),
    "block_count":lambda p:p["counts"].update(unabridged_DOM_blocks=5),
    "citation_count":lambda p:p["counts"].update(citation_occurrences=5),
    "fake_claim_review":lambda p:p["counts"].update(human_source_or_claim_reviews=1),
    "fake_medical_review":lambda p:p["counts"].update(human_qualified_safety_reviews=1),
    "fake_qd_count":lambda p:p["counts"].update(independent_QD_approvals=1),
    "source_removed":lambda p:p["all_244_unabridged_source_readings_NOT_REVIEWED"].pop(),
    "source_duplicated":lambda p:p["all_244_unabridged_source_readings_NOT_REVIEWED"].__setitem__(
        1,deepcopy(p["all_244_unabridged_source_readings_NOT_REVIEWED"][0])),
    "source_order":lambda p:p["all_244_unabridged_source_readings_NOT_REVIEWED"].reverse(),
    "source_url":lambda p:source_mutation(p,"exact_URL_NO_ALIAS","https://wrong.example/"),
    "source_reading_sha":lambda p:source_mutation(p,"candidate_reading_sha256","f"*64),
    "source_approval":lambda p:source_mutation(p,"human_source_and_claim_review","APPROVED"),
    "source_safety":lambda p:source_mutation(p,"qualified_safety_review","SAFE"),
    "historical_reading":lambda p:source_mutation(p,
        "original_reading_UNABRIDGED_NOT_HUMAN_VERIFIED",{"missing":"context"}),
    "doc_missing":lambda p:p["all_document_block_orders_NOT_REVIEWED"].pop(),
    "doc_slug":lambda p:doc_mutation(p,"slug","incorrect"),
    "doc_duplicate_url":lambda p:doc_mutation(p,"draft_url_NOT_PUBLIC",
        p["all_document_block_orders_NOT_REVIEWED"][1]["draft_url_NOT_PUBLIC"]),
    "doc_url_published":lambda p:doc_mutation(p,"draft_url_NOT_PUBLIC","https://public.example"),
    "doc_blocks_lost":lambda p:doc_mutation(p,"block_ids_in_original_order",["different"]),
    "doc_approval":lambda p:doc_mutation(p,"reviewer_state","PASS"),
    "dom_removed":lambda p:p["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"].pop(),
    "dom_duplicated":lambda p:p["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"].append(
        deepcopy(p["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"][0])),
    "dom_reordered":lambda p:p["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"].reverse(),
    "dom_changed":lambda p:block_mutation(p,
        "DOM_text_UNABRIDGED_NOT_BROWSER_OR_SAFETY_VERIFIED","Shortened 2 days."),
    "dom_hash":lambda p:block_mutation(p,"DOM_text_sha256","f"*64),
    "dom_review":lambda p:block_mutation(p,"human_claim_support_review","PASS"),
    "dom_safety":lambda p:block_mutation(p,"qualified_safety_review","SAFE"),
    "dom_qd":lambda p:block_mutation(p,"independent_QD_review","PASS"),
    "dom_slug":lambda p:block_mutation(p,"slug","wrong"),
    "dom_block_id":lambda p:block_mutation(p,"block_id","wrong"),
    "dom_draft_url":lambda p:block_mutation(p,"private_draft_url","https://live.example/"),
    "citation_removed":lambda p:citation_mutation(p,"origin_scoped_source_variants_NOT_ALIASED",[]),
    "citation_ordinal":lambda p:citation_mutation(p,"ordinal",-2),
    "citation_approval":lambda p:citation_mutation(p,"human_claim_support_review","PASS"),
    "citation_source_id":lambda p:citation_mutation(p,"source_id","wrong-id"),
    "variant_url":lambda p:source_variant_mutation(p,"exact_URL_NOT_ALIAS","https://wrong.example/"),
    "variant_sha":lambda p:source_variant_mutation(p,"complete_source_reading_sha256","f"*64),
    "variant_origin":lambda p:source_variant_mutation(p,"source_origin","unknown"),
    "action_removed":lambda p:p["all_975_action_triage_packets_NOT_APPROVED"].pop(),
    "action_text":lambda p:action_mutation(p,
        "full_DOM_text_UNABRIDGED_NOT_SAFETY_VERIFIED","Altered context"),
    "action_safety":lambda p:action_mutation(p,"qualified_safety_review","SAFE"),
    "action_parent_sha":lambda p:action_mutation(p,"original_R72_block_sha256","f"*64),
    "quantity_removed":lambda p:p["exact_quantity_review_packets_NOT_APPROVED"].pop(),
    "quantity_unicode_span":lambda p:qty_mutation(p,
        "quantities_EXACT_TEXT_NO_UNIT_CONVERSION",[]),
    "quantity_citation":lambda p:qty_mutation(p,"original_R72_task_sha256","f"*64),
    "quantity_safety":lambda p:qty_mutation(p,"qualified_safety_review","PASS"),
    "quantity_total":lambda p:p["counts"].update(numeric_unit_occurrences=999),
    "qualifier_parent_fingerprint":lambda p:p.update(original_R73_evidence_fingerprint_sha256="not-a-sha"),
}

def fault_test(label, mutate):
    def run(self):
        p=synthetic_with_numeric_context() if label.startswith("quantity_") else sample()
        mutate(p)
        reseal(p)
        with self.assertRaises(gate.Hold,msg=label):
            gate.construct(p,expected=N)
    run.__name__="test_adversarial_"+label
    return run

class Adversarial(unittest.TestCase):
    pass

for _label,_fault in FAULTS.items():
    setattr(Adversarial,"test_adversarial_"+_label,fault_test(_label,_fault))

if __name__=="__main__":
    unittest.main()
