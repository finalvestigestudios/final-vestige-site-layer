"""R73 isolated synthetic tests: NO real source/file mutation and NO approvals."""
from __future__ import annotations

from copy import deepcopy
import csv
import importlib.util
import io
from pathlib import Path
import unittest

BASE = Path(__file__).resolve().parents[1]


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gate=load(BASE/"tools"/"r73_consequential_language_review.py","r73_under_test")
parent_test=load(BASE/"tests"/"test_r72_source_scope_collision_impact.py",
                 "r72_synthetic_fixture_for_r73")
N=(1,1,3,3,4)


def sample():
    return parent_test.gate.construct(parent_test.baseline(), expected=parent_test.N)


def sign(report):
    report.pop("fingerprint_sha256",None)
    report["fingerprint_sha256"]=gate.sha(report)
    return report


def source(r,n=0):
    return r["all_complete_source_readings_NOT_APPROVED"][n]


def block(r,n=0):
    return r["all_unabridged_DOM_block_citation_tasks_NOT_APPROVED"][n]


def documents(r):
    return r["all_document_impact_orders_NOT_APPROVED"]


def edge(r,n=1):
    return block(r,n)["local_citations_NOT_CLAIM_SUPPORT_PROOF"][0]


class R73LanguageDocketTests(unittest.TestCase):
    def make(self,r=None):
        return gate.construct(sample() if r is None else r,expected=N)

    def test_baseline_counts(self):
        report=self.make()
        self.assertEqual((report["counts"]["articles"],report["counts"]["tools"]), (1,1))
        self.assertEqual(report["counts"]["citation_occurrences"],3)
        self.assertEqual(report["counts"]["unabridged_DOM_review_tasks"],4)
        self.assertEqual(report["counts"]["complete_distinct_origin_scoped_source_readings"],3)

    def test_action_keyword_packets_are_explicitly_unapproved(self):
        rows=self.make()["consequential_action_wording_review_packets_NOT_APPROVED"]
        self.assertEqual(len(rows),3)
        self.assertTrue(all(row["human_claim_support_review"]=="NOT_REVIEWED" for row in rows))
        self.assertTrue(all(row["qualified_safety_review"]=="NOT_REVIEWED" for row in rows))

    def test_preserves_complete_source_readings(self):
        r=sample();x=self.make(r)
        self.assertEqual(r["all_complete_source_readings_NOT_APPROVED"],
                         x["all_244_unabridged_source_readings_NOT_REVIEWED"])

    def test_preserves_all_full_dom_readings_even_nonaction(self):
        r=sample();x=self.make(r)
        self.assertEqual(r["all_unabridged_DOM_block_citation_tasks_NOT_APPROVED"],
                         x["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"])

    def test_preserves_disjoint_article_and_tool_context(self):
        rows=self.make()["consequential_action_wording_review_packets_NOT_APPROVED"]
        self.assertEqual({x["kind"] for x in rows},{"article","tool"})
        self.assertEqual({x["slug"] for x in rows},{"first","planner"})

    def test_shared_url_source_not_aliased(self):
        r=self.make();p=r["consequential_action_wording_review_packets_NOT_APPROVED"][0]
        cited=p["local_citations_NO_CLAIM_SUPPORT_ASSUMED"][0]
        self.assertEqual(len(cited["origin_scoped_source_readings_NOT_MERGED"]),2)
        self.assertEqual(len({(x["origin"],x["source_id"])
            for x in cited["origin_scoped_source_readings_NOT_MERGED"]}),2)

    def test_uncited_block_retained(self):
        p=self.make()["all_4070_unabridged_DOM_tasks_NOT_REVIEWED"][0]
        self.assertEqual(p["block_id"],"block-1")
        self.assertEqual(p["local_citations_NOT_CLAIM_SUPPORT_PROOF"],[])

    def test_unabridged_claim_and_source_hashes_retained(self):
        r=self.make()
        p=r["consequential_action_wording_review_packets_NOT_APPROVED"][0]
        self.assertEqual(p["original_DOM_text_sha256"],
                         gate.text_sha(p["full_DOM_text_UNABRIDGED_NOT_SAFETY_VERIFIED"]))
        self.assertEqual(p["packet_sha256"],
                         gate.sha({k:v for k,v in p.items() if k!="packet_sha256"}))

    def test_completely_unapproved(self):
        r=self.make()
        self.assertEqual(r["release_state"],"HOLD")
        self.assertTrue(all(r[k] is False for k in gate.HOLD))
        self.assertEqual(r["counts"]["human_qualified_safety_reviews"],0)
        self.assertEqual(r["counts"]["independent_QD_approvals"],0)

    def test_unique_document_urls_conserved(self):
        r=self.make()
        self.assertEqual(len({x["draft_url_NOT_PUBLIC"]
            for x in r["all_document_block_orders_NOT_REVIEWED"]}),2)

    def test_repeated_construction_is_deterministic(self):
        r=sample()
        a=self.make(r);b=self.make(r)
        self.assertEqual(a,b)
        gate.sealed(a,gate.SCHEMA)

    def test_construct_does_not_mutate_parent(self):
        r=sample();before=deepcopy(r)
        self.make(r)
        self.assertEqual(before,r)

    def test_output_is_not_mutable_alias_of_parent(self):
        r=sample();out=self.make(r)
        source(r)["candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"]["title"]="changed"
        self.assertNotEqual(source(r),out["all_244_unabridged_source_readings_NOT_REVIEWED"][0])

    def test_action_detection_is_triage_not_safety(self):
        cue=gate.cues("Do not boil water if fuel contamination is suspected.")
        self.assertIn("ACTION_WORDING_REVIEW_NOT_INSTRUCTION_VERDICT",cue)
        self.assertIn("QUALIFYING_LANGUAGE_CONTEXT_ONLY_NOT_SAFETY_PROOF",cue)

    def test_numeric_language_is_only_triage(self):
        cue=gate.cues("Store 2 gallons for 4 days.")
        self.assertIn("OPERATIONAL_QUANTITY_REVIEW_NOT_DOSAGE_ADVICE",cue)
        self.assertIn("ACTION_WORDING_REVIEW_NOT_INSTRUCTION_VERDICT",cue)

    def test_cues_do_not_invent_a_qualified_review(self):
        self.assertEqual(gate.cues("Water chemistry is complex."),[])

    def test_docket_references_exact_origin_scoped_urls(self):
        p=self.make()["consequential_action_wording_review_packets_NOT_APPROVED"][0]
        source_urls=[x["exact_URL_NOT_EQUIVALENCE"]
            for y in p["local_citations_NO_CLAIM_SUPPORT_ASSUMED"]
            for x in y["origin_scoped_source_readings_NOT_MERGED"]]
        self.assertEqual(source_urls,["https://www.example.org/alpha"]*2)

    def test_csv_retains_full_reading_with_embedded_newline(self):
        r=self.make()
        rows=list(csv.DictReader(io.StringIO(gate.csv_action_packets(r))))
        self.assertEqual(len(rows),3)
        self.assertEqual(rows[0]["claim_review_NOT_REVIEWED"],"NOT_REVIEWED")

    def test_csv_spreadsheet_formula_neutralized(self):
        r=self.make()
        p=r["consequential_action_wording_review_packets_NOT_APPROVED"][0]
        p["full_DOM_text_UNABRIDGED_NOT_SAFETY_VERIFIED"]="  \ufeff=2+2"
        sign(r)
        rows=list(csv.DictReader(io.StringIO(gate.csv_action_packets(r))))
        self.assertTrue(rows[0]["full_unabridged_DOM_text_UNVERIFIED"].startswith("'"))

    def test_csv_invisible_prefix_neutralized(self):
        r=self.make();p=r["consequential_action_wording_review_packets_NOT_APPROVED"][0]
        p["full_DOM_text_UNABRIDGED_NOT_SAFETY_VERIFIED"]="\u2060@COMPUTE"
        sign(r)
        rows=list(csv.DictReader(io.StringIO(gate.csv_action_packets(r))))
        self.assertTrue(rows[0]["full_unabridged_DOM_text_UNVERIFIED"].startswith("'"))

    def test_source_collision_groups_retained(self):
        r=sample();x=self.make(r)
        self.assertEqual(x["shared_URL_scope_collisions_NOT_REVIEWED"],
                         r["shared_exact_URL_collision_review_orders_NOT_APPROVED"])
        self.assertEqual(x["reused_ID_scope_collisions_NOT_REVIEWED"],
                         r["reused_source_ID_collision_review_orders_NOT_APPROVED"])

    def test_invalid_expected_tuple_fails_closed(self):
        for item in ((True,1,3,3,4),(1,1,3,3,0),(1,1,3,3),
                     ["1",1,3,3,4],None):
            with self.subTest(item=item),self.assertRaises(gate.Hold):
                gate.construct(sample(),expected=item)


# Mutations are independent, isolated synthetic R72 records. Re-signing the
# outer report ensures these tests exercise structural checks, not just SHA.
FAULTS={
 "issue_changed":lambda r:r.update(issue=7),
 "schema_changed":lambda r:r.update(schema="public-release"),
 "release_pass":lambda r:r.update(release_state="PASS"),
 "not_machine_only":lambda r:r.update(machine_only=False),
 "fake_publication_approval":lambda r:r.update(may_publish=True),
 "fake_qd_approval":lambda r:r.update(independent_QD_approval=True),
 "fake_safety_approval":lambda r:r.update(qualified_safety_clearance=True),
 "fake_link_approval":lambda r:r.update(human_source_links_verified=True),
 "article_count_drift":lambda r:r["counts"].update(articles=2),
 "tool_count_drift":lambda r:r["counts"].update(tools=2),
 "source_count_drift":lambda r:r["counts"].update(complete_distinct_origin_scoped_source_readings=4),
 "citation_count_drift":lambda r:r["counts"].update(citation_occurrences=4),
 "block_count_drift":lambda r:r["counts"].update(unabridged_DOM_block_tasks=5),
 "claim_review_fraud":lambda r:r["counts"].update(human_claim_support_reviews=1),
 "safety_review_fraud":lambda r:r["counts"].update(human_qualified_safety_reviews=1),
 "qd_review_fraud":lambda r:r["counts"].update(independent_QD_approvals=1),
 "source_removed":lambda r:r["all_complete_source_readings_NOT_APPROVED"].pop(),
 "source_duplicated_identity":lambda r:r["all_complete_source_readings_NOT_APPROVED"].__setitem__(1,deepcopy(source(r))),
 "source_order_changed":lambda r:r["all_complete_source_readings_NOT_APPROVED"].reverse(),
 "source_origin_empty":lambda r:source(r).update(source_origin=""),
 "source_id_empty":lambda r:source(r).update(source_id=""),
 "source_id_changed":lambda r:source(r).update(source_id="changed"),
 "source_candidate_url_changed":lambda r:source(r)["candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"].update(url="https://changed.example.org"),
 "source_exact_url_changed":lambda r:source(r).update(exact_URL_NO_ALIAS="https://changed.example.org"),
 "source_candidate_title_changed":lambda r:source(r)["candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"].update(title="edited"),
 "source_reading_sha_changed":lambda r:source(r).update(candidate_reading_sha256="a"*64),
 "source_review_approved":lambda r:source(r).update(human_source_and_claim_review="APPROVED"),
 "source_safety_approved":lambda r:source(r).update(qualified_safety_review="SAFE"),
 "source_fake_link_check":lambda r:source(r)["candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"].update(human_link_check=True),
 "source_old_reading_forged":lambda r:source(r).update(original_reading_UNABRIDGED_NOT_HUMAN_VERIFIED={"id":"x"}),
 "source_old_sha_forged":lambda r:source(r).update(original_reading_sha256="a"*64),
 "block_removed":lambda r:r["all_unabridged_DOM_block_citation_tasks_NOT_APPROVED"].pop(),
 "block_duplicated":lambda r:r["all_unabridged_DOM_block_citation_tasks_NOT_APPROVED"].append(deepcopy(block(r))),
 "block_sha_changed":lambda r:block(r).update(task_sha256="0"*64),
 "block_text_changed":lambda r:block(r).update(DOM_text_UNABRIDGED_NOT_BROWSER_OR_SAFETY_VERIFIED="Rewritten"),
 "block_text_sha_changed":lambda r:block(r).update(DOM_text_sha256="0"*64),
 "block_claim_approved":lambda r:block(r).update(human_claim_support_review="APPROVED"),
 "block_safety_approved":lambda r:block(r).update(qualified_safety_review="SAFE"),
 "block_qd_approved":lambda r:block(r).update(independent_QD_review="APPROVED"),
 "block_id_changed":lambda r:block(r).update(block_id="rewritten-block"),
 "block_slug_changed":lambda r:block(r).update(slug="elsewhere"),
 "block_kind_changed":lambda r:block(r).update(kind="public-page"),
 "block_url_changed":lambda r:block(r).update(private_draft_url="/preparedness/other/"),
 "block_topics_corrupted":lambda r:block(r).update(topic_signals_TRIAGE_NOT_SAFETY_VERDICT="water"),
 "block_citation_missing":lambda r:block(r,1).update(local_citations_NOT_CLAIM_SUPPORT_PROOF=[]),
 "citation_reuse_ordinal":lambda r:edge(r,2).update(ordinal=1),
 "citation_zero_ordinal":lambda r:edge(r).update(ordinal=0),
 "citation_approved":lambda r:edge(r).update(human_claim_support_review="SUPPORTED"),
 "citation_source_id_changed":lambda r:edge(r).update(source_id="synthetic-else"),
 "citation_variants_lost":lambda r:edge(r).update(origin_scoped_source_variants_NOT_ALIASED=[]),
 "citation_variant_origin_changed":lambda r:edge(r)["origin_scoped_source_variants_NOT_ALIASED"][0].update(source_origin="lost"),
 "citation_variant_sha_changed":lambda r:edge(r)["origin_scoped_source_variants_NOT_ALIASED"][0].update(complete_source_reading_sha256="e"*64),
 "citation_variant_url_changed":lambda r:edge(r)["origin_scoped_source_variants_NOT_ALIASED"][0].update(exact_URL_NOT_ALIAS="https://redirect.example.org"),
 "document_removed":lambda r:documents(r).pop(),
 "document_duplicate":lambda r:documents(r).append(deepcopy(documents(r)[0])),
 "document_url_collision":lambda r:documents(r)[1].update(draft_url_NOT_PUBLIC=documents(r)[0]["draft_url_NOT_PUBLIC"]),
 "document_review_approved":lambda r:documents(r)[0].update(reviewer_state="APPROVED"),
 "document_block_order_changed":lambda r:documents(r)[0]["block_ids_in_original_order"].reverse(),
 "document_block_missing":lambda r:documents(r)[0]["block_ids_in_original_order"].pop(),
 "document_kind_invalid":lambda r:documents(r)[0].update(kind="published"),
 "document_slug_changed":lambda r:documents(r)[0].update(slug="changed"),
 "document_url_escape":lambda r:documents(r)[0].update(draft_url_NOT_PUBLIC="/preparedness/../escape/"),
 "shared_url_group_missing":lambda r:r["shared_exact_URL_collision_review_orders_NOT_APPROVED"].pop(),
 "reused_id_group_missing":lambda r:r["reused_source_ID_collision_review_orders_NOT_APPROVED"].pop(),
 "uncited_source_forged":lambda r:r["uncited_origin_scoped_sources_NOT_REVIEWED"].append(["forged","ghost"]),
 "unattached_citation_forged":lambda r:r["citations_without_DOM_block_UNRESOLVED"].append({"kind":"article","slug":"first","citation_ordinal":45}),
}


def adversarial_factory(name,mutate):
    def test(self):
        r=sample()
        mutate(r)
        sign(r)
        with self.assertRaises(gate.Hold,msg=name):
            gate.construct(r,expected=N)
    test.__name__="test_adversarial_"+name
    return test


for _name,_fault in FAULTS.items():
    setattr(R73LanguageDocketTests,"test_adversarial_"+_name,
            adversarial_factory(_name,_fault))


if __name__=="__main__":
    unittest.main()
