"""R76 review-only custody tests; all samples synthetic, never modify corpus."""
from __future__ import annotations

from copy import deepcopy
import csv
import importlib.util
import io
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


gate = load(ROOT/"tools"/"r76_source_impact_crosswalk.py","r76_under_test")
previous = load(ROOT/"tests"/"test_r75_qualifier_scope_citation_custody.py",
                "r75_fixture_for_r76")
N = previous.N


def parent():
    """Use the existing sealed four-block / three-source synthetic R75 graph."""
    return previous.gate.construct(previous.sample(),expected=N)


def reseal(obj):
    obj["fingerprint_sha256"] = gate.digest({
        k:v for k,v in obj.items() if k!="fingerprint_sha256"})
    return obj


def make(p=None):
    return gate.construct(parent() if p is None else p,expected=N)


def cited(p):
    return next(b for b in p["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"]
                if b["local_citations_NOT_CLAIM_SUPPORT_PROOF"])


def citation(p):
    return cited(p)["local_citations_NOT_CLAIM_SUPPORT_PROOF"][0]


def changed(value):
    return "__INVALID_CHANGED_VALUE__" if value != "__INVALID_CHANGED_VALUE__" else "__INVALID_2__"


def alter_block(p,key,value):
    b=p["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"][0]
    b[key]=value
    b["task_sha256"]=gate.digest({k:v for k,v in b.items() if k!="task_sha256"})


def alter_citation(p,key,value):
    b=cited(p)
    b["local_citations_NOT_CLAIM_SUPPORT_PROOF"][0][key]=value
    b["task_sha256"]=gate.digest({k:v for k,v in b.items() if k!="task_sha256"})


def alter_variant(p,key,value):
    b=cited(p)
    b["local_citations_NOT_CLAIM_SUPPORT_PROOF"][0][
        "origin_scoped_source_variants_NOT_ALIASED"][0][key]=value
    b["task_sha256"]=gate.digest({k:v for k,v in b.items() if k!="task_sha256"})


def alter_review(p,key,value):
    row=p["action_or_quantity_qualifier_context_queue_NOT_APPROVED"][0]
    row[key]=value
    row["packet_sha256"]=gate.digest({k:v for k,v in row.items() if k!="packet_sha256"})


def alter_source(p,key,value):
    p["all_244_unabridged_source_readings_NOT_REVIEWED"][0][key]=value


def append_to(p,key,value):
    p[key].append(value)


class Baseline(unittest.TestCase):
    def test_parent_is_valid_r75(self):
        previous.gate.sealed(parent(),previous.gate.SCHEMA)

    def test_output_seal(self):
        gate.sealed(make())

    def test_deterministic_report(self):
        self.assertEqual(make(),make())

    def test_original_fingerprint_pinned(self):
        p=parent()
        self.assertEqual(make(p)["original_R75_fingerprint_sha256"],
                         p["fingerprint_sha256"])

    def test_original_sources_unabridged(self):
        p=parent()
        self.assertEqual(make(p)["all_244_unabridged_source_readings_NOT_REVIEWED"],
                         p["all_244_unabridged_source_readings_NOT_REVIEWED"])

    def test_original_dom_text_unabridged(self):
        p=parent()
        self.assertEqual(make(p)["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"],
                         p["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"])

    def test_original_document_orders(self):
        p=parent()
        self.assertEqual(make(p)["all_document_block_orders_NOT_REVIEWED"],
                         p["all_document_block_orders_NOT_REVIEWED"])

    def test_original_review_packets(self):
        p=parent()
        self.assertEqual(make(p)["original_R75_action_quantity_qualifier_queue_NOT_APPROVED"],
                         p["action_or_quantity_qualifier_context_queue_NOT_APPROVED"])

    def test_original_unresolved_collisions(self):
        p=parent();r=make(p)
        for key in ("shared_URL_scope_collisions_NOT_REVIEWED",
                    "reused_ID_scope_collisions_NOT_REVIEWED",
                    "uncited_source_readings_NOT_REVIEWED",
                    "citations_without_DOM_block_UNRESOLVED"):
            self.assertEqual(r[key],p[key])

    def test_no_permissions(self):
        r=make()
        self.assertEqual(r["release_state"],"HOLD")
        self.assertTrue(all(r[k] is False for k in gate.HOLD_KEYS))
        self.assertEqual(r["counts"]["qualified_safety_reviews"],0)

    def test_source_impact_rows_cover_every_reading(self):
        r=make()
        self.assertEqual(r["counts"]["complete_source_impact_packets"],N[2])
        self.assertEqual(len(r["all_origin_scoped_source_impact_packets_NOT_REVIEWED"]),N[2])

    def test_citation_occurrences_not_variant_edges(self):
        r=make()
        self.assertEqual(r["counts"]["citation_occurrences"],N[3])
        self.assertGreaterEqual(r["counts"]["citation_source_variant_edges_NOT_CLAIM_COUNT"],
                                r["counts"]["attached_citation_occurrences"])

    def test_source_variant_bindings_preserved(self):
        r=make()
        sources={(s["source_origin"],s["source_id"]):s for s in
                 r["all_origin_scoped_source_impact_packets_NOT_REVIEWED"]}
        for c in r["every_attached_citation_crosswalk_NOT_SOURCE_SUPPORT_PROOF"]:
            for v in c["source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT"]:
                s=sources[(v["source_origin"],v["source_id"])]
                self.assertEqual(v["complete_source_reading_sha256"],
                                 s["complete_source_reading_sha256"])
                self.assertEqual(v["exact_URL_NOT_CANONICALIZED"],
                                 s["exact_URL_NOT_CANONICALIZED"])

    def test_review_work_order_contains_every_source(self):
        r=make()
        self.assertEqual({(s["source_origin"],s["source_id"]) for s in
            r["human_source_review_work_order_NOT_PRIORITY_AS_RISK"]},
            {(s["source_origin"],s["source_id"]) for s in
            r["all_origin_scoped_source_impact_packets_NOT_REVIEWED"]})

    def test_source_work_order_sorting_is_deterministic(self):
        r=make()
        work=r["human_source_review_work_order_NOT_PRIORITY_AS_RISK"]
        self.assertEqual(work,sorted(work,key=lambda p:(
            -p["consequential_citation_variant_edges_NOT_VERDICT"],
            -len(p["distinct_documents_citing_source_NOT_VERIFIED"]),
            -p["all_citation_variant_edges_NOT_VERDICT"],
            p["source_origin"],p["source_id"])))

    def test_no_automatic_approval_in_packets(self):
        r=make()
        for s in r["all_origin_scoped_source_impact_packets_NOT_REVIEWED"]:
            self.assertIs(s["human_link_check"],False)
            self.assertEqual(s["human_source_and_claim_review"],"NOT_REVIEWED")
            self.assertEqual(s["qualified_safety_review"],"NOT_REVIEWED")

    def test_crosswalk_all_packets_sealed(self):
        r=make()
        for coll in ("all_origin_scoped_source_impact_packets_NOT_REVIEWED",
                     "every_attached_citation_crosswalk_NOT_SOURCE_SUPPORT_PROOF"):
            for row in r[coll]:
                self.assertEqual(row["packet_sha256"],
                                 gate.digest({k:v for k,v in row.items()
                                              if k!="packet_sha256"}))

    def test_readonly_export_one_row_per_origin_scoped_source(self):
        r=make()
        rows=list(csv.DictReader(io.StringIO(gate.csv_review_work_order(r))))
        self.assertEqual(len(rows),N[2])
        self.assertTrue(all(row["human_source_and_claim_review"]=="NOT_REVIEWED"
                            for row in rows))

    def test_csv_bytes_deterministic(self):
        r=make()
        self.assertEqual(gate.csv_review_work_order(r),
                         gate.csv_review_work_order(r))

    def test_csv_formula_injection_neutralized(self):
        r=make()
        # Tamper a valid-looking report and re-seal to test presentation escaping.
        row=r["human_source_review_work_order_NOT_PRIORITY_AS_RISK"][0]
        row["source_origin"]=" =1+1"
        reseal(r)
        rows=list(csv.DictReader(io.StringIO(gate.csv_review_work_order(r))))
        self.assertTrue(any(x["source_origin"].startswith("' =")
                            for x in rows))

    def test_custody_parent_not_mutated(self):
        p=parent();before=deepcopy(p)
        make(p)
        self.assertEqual(p,before)

    def test_document_citation_ordinals_unique(self):
        r=make()
        edges=r["every_attached_citation_crosswalk_NOT_SOURCE_SUPPORT_PROOF"]
        self.assertEqual(len({(e["kind"],e["slug"],e["citation_ordinal"])
                              for e in edges}),len(edges))


# Each scenario is a distinct actual unittest; never writes source fixture files.
_MUTATIONS = [
    ("wrong_schema",lambda p: p.__setitem__("schema","not-r75")),
    ("not_hold",lambda p: p.__setitem__("release_state","PASS")),
    ("not_machine_only",lambda p: p.__setitem__("machine_only",False)),
    ("may_publish",lambda p: p.__setitem__("may_publish",True)),
    ("qd_approval",lambda p: p.__setitem__("independent_QD_approval",True)),
    ("qualified_safety_approval",lambda p: p.__setitem__("qualified_safety_clearance",True)),
    ("human_links_verified",lambda p: p.__setitem__("human_source_links_verified",True)),
    ("article_census",lambda p: p["counts"].__setitem__("articles",99)),
    ("tool_census",lambda p: p["counts"].__setitem__("tools",99)),
    ("citation_census",lambda p: p["counts"].__setitem__("citation_occurrences",99)),
    ("source_census",lambda p: p["counts"].__setitem__("complete_origin_scoped_source_readings",99)),
    ("dom_census",lambda p: p["counts"].__setitem__("unabridged_DOM_blocks",99)),
    ("fake_human_review",lambda p: p["counts"].__setitem__("human_claim_support_reviews",1)),
    ("fake_qualified_review",lambda p: p["counts"].__setitem__("qualified_safety_reviews",1)),
    ("fake_qd",lambda p: p["counts"].__setitem__("independent_QD_approvals",1)),
    ("missing_source",lambda p: p["all_244_unabridged_source_readings_NOT_REVIEWED"].pop()),
    ("missing_block",lambda p: p["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"].pop()),
    ("missing_document",lambda p: p["all_document_block_orders_NOT_REVIEWED"].pop()),
    ("missing_review_task",lambda p: p["action_or_quantity_qualifier_context_queue_NOT_APPROVED"].pop()),
    ("source_origin_changed",lambda p: alter_source(p,"source_origin","bogus-origin")),
    ("source_id_changed",lambda p: alter_source(p,"source_id","bogus-id")),
    ("source_url_changed",lambda p: alter_source(p,"exact_URL_NO_ALIAS","https://bogus.invalid")),
    ("source_sha_changed",lambda p: alter_source(p,"candidate_reading_sha256","0"*64)),
    ("source_approval_changed",lambda p: alter_source(p,"human_source_and_claim_review","PASS")),
    ("source_safety_changed",lambda p: alter_source(p,"qualified_safety_review","PASS")),
    ("historical_reading_sha_changed",lambda p: alter_source(p,"original_reading_sha256","0"*64)),
    ("block_id_changed",lambda p: alter_block(p,"block_id","bogus-block")),
    ("block_route_changed",lambda p: alter_block(p,"private_draft_url","/preparedness/elsewhere/")),
    ("block_sha_changed",lambda p: alter_block(p,"DOM_text_sha256","0"*64)),
    ("block_review_changed",lambda p: alter_block(p,"qualified_safety_review","APPROVED")),
    ("document_route_changed",lambda p: p["all_document_block_orders_NOT_REVIEWED"][0].__setitem__("draft_url_NOT_PUBLIC","/preparedness/other/")),
    ("document_approval_changed",lambda p: p["all_document_block_orders_NOT_REVIEWED"][0].__setitem__("reviewer_state","APPROVED")),
    ("duplicate_dom_order",lambda p: p["all_document_block_orders_NOT_REVIEWED"][0]["block_ids_in_original_order"].append(
        p["all_document_block_orders_NOT_REVIEWED"][0]["block_ids_in_original_order"][0])),
    ("citation_ordinal_changed",lambda p: alter_citation(p,"ordinal",999)),
    ("citation_id_changed",lambda p: alter_citation(p,"source_id","bogus-citation-id")),
    ("citation_review_changed",lambda p: alter_citation(p,"human_claim_support_review","APPROVED")),
    ("citation_variants_dropped",lambda p: alter_citation(p,"origin_scoped_source_variants_NOT_ALIASED",[])),
    ("variant_url_changed",lambda p: alter_variant(p,"exact_URL_NOT_ALIAS","https://bad.invalid/")),
    ("variant_sha_changed",lambda p: alter_variant(p,"complete_source_reading_sha256","0"*64)),
    ("variant_id_changed",lambda p: alter_variant(p,"source_id","bogus-variant-id")),
    ("variant_review_changed",lambda p: alter_variant(p,"human_source_and_claim_review","APPROVED")),
    ("review_packet_sha_changed",lambda p: p["action_or_quantity_qualifier_context_queue_NOT_APPROVED"][0].__setitem__("packet_sha256","0"*64)),
    ("review_block_sha_changed",lambda p: alter_review(p,"original_R72_block_sha256","0"*64)),
    ("review_citations_changed",lambda p: alter_review(p,"source_citations_NOT_CLAIM_SUPPORT",[])),
    ("review_qualifiers_changed",lambda p: alter_review(p,"same_block_qualifiers_NOT_SAFETY_PROOF",[{"bogus":True}])),
    ("review_approval_changed",lambda p: alter_review(p,"qualified_safety_review","APPROVED")),
    ("review_both_flags_off",lambda p: (alter_review(p,"action_language_TRIAGE_NOT_VERDICT",False),
                                         alter_review(p,"numeric_units_TRIAGE_NOT_DOSAGE_CHECK",False))),
    ("shared_url_inventory_phantom",lambda p: append_to(p,"shared_URL_scope_collisions_NOT_REVIEWED",{"bogus":True})),
    ("reused_id_inventory_phantom",lambda p: append_to(p,"reused_ID_scope_collisions_NOT_REVIEWED",{"bogus":True})),
    ("uncited_inventory_phantom",lambda p: append_to(p,"uncited_source_readings_NOT_REVIEWED",["phantom","id"])),
    ("unattached_citation_phantom",lambda p: append_to(p,"citations_without_DOM_block_UNRESOLVED",{
        "kind":"article","slug":"phantom","citation_ordinal":1,
        "source_id":"ghost","review_state":"NOT_REVIEWED"})),
    ("shared_collision_changed_same_count",lambda p:
        p["shared_URL_scope_collisions_NOT_REVIEWED"][0].__setitem__(
            "value","https://invented.invalid/source")),
    ("reused_id_collision_changed_same_count",lambda p:
        p["reused_ID_scope_collisions_NOT_REVIEWED"][0].__setitem__(
            "value","invented-source-id")),
    ("source_doc_scope_lost",lambda p:
        p["all_document_block_orders_NOT_REVIEWED"][0].__setitem__(
            "origin_scoped_sources_USED_NOT_SUPPORT_APPROVED",[])),
    ("review_action_flag_inverted",lambda p: alter_review(p,
        "action_language_TRIAGE_NOT_VERDICT",not p[
            "action_or_quantity_qualifier_context_queue_NOT_APPROVED"][0][
            "action_language_TRIAGE_NOT_VERDICT"])),
    ("review_quantity_flag_inverted",lambda p: alter_review(p,
        "numeric_units_TRIAGE_NOT_DOSAGE_CHECK",not p[
            "action_or_quantity_qualifier_context_queue_NOT_APPROVED"][0][
            "numeric_units_TRIAGE_NOT_DOSAGE_CHECK"])),
    ("citation_variant_duplicated",lambda p: alter_citation(p,
        "origin_scoped_source_variants_NOT_ALIASED",
        p["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"][0][
            "local_citations_NOT_CLAIM_SUPPORT_PROOF"][0][
            "origin_scoped_source_variants_NOT_ALIASED"]*2)),
]


def _register_mutation(name,mutate):
    def scenario(self):
        p=parent()
        mutate(p)
        reseal(p)
        with self.assertRaises((gate.Hold,ValueError,TypeError,KeyError,AttributeError)):
            make(p)
    scenario.__name__="test_reject_"+name
    setattr(Adversarial,scenario.__name__,scenario)


class Adversarial(unittest.TestCase):
    """One test per independent sabotage mode, including re-sealed parent rows."""


for _name,_mutation in _MUTATIONS:
    _register_mutation(_name,_mutation)


if __name__=="__main__":
    unittest.main()
