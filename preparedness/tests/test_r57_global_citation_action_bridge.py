#!/usr/bin/env python3
"""R57 source variant / global fallback private HOLD adversarial regression."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


gate = module("r57_global_bridge_test", ROOT / "tools" /
              "r57_global_citation_action_bridge.py")
CENSUS = (2, 0, 4, 3, 1, 1)
INVENTORY = (4, 3, 1, 0)
ACTIONS = (2, 1, 1, 0, 0)
SHARED = "https://example.org/full-source"


def signed(doc):
    doc["fingerprint_sha256"] = gate.digest({
        k: v for k, v in doc.items() if k != "fingerprint_sha256"
    })
    return doc


def fixture():
    a = {"id": "s1", "_origin": "base", "url": SHARED,
         "notes": "baseline reading\nhuman confirmation pending",
         "supports": "unreviewed original source scope"}
    b = {"id": "s2", "_origin": "hist-food", "url": SHARED,
         "notes": "another original contributor \u202e note",
         "supports": "alternate claim reading; not interchangeable"}
    c = {"id": "s3", "_origin": "start",
         "url": "https://example.org/unique", "notes": "individual",
         "supports": "cited separately"}
    d = {"id": "s4", "_origin": "base",
         "url": "https://example.org/uncited", "notes": "uncited source",
         "supports": "not an article citation"}
    group = {"url": SHARED,
             "review_status": "pending-human-source-and-reading-scope-review",
             "reviewer": None, "reviewed_on": None,
             "variants": [{"source": {k: v for k, v in x.items()
                                      if k != "_origin"},
                           "origin": x["_origin"]} for x in (a, b)]}
    lib = SimpleNamespace(
        source_variants={"s1": [a], "s2": [b], "s3": [c], "s4": [d]},
        crosswalk_groups={SHARED: group},
        article_origins={"a": "start", "b": "hist-food"},
    )
    def relation(slug, variant, source_use, occurrences, fallback, shared):
        return {
            "slug": slug, "article_origin": lib.article_origins[slug],
            "source_id": variant["id"], "source_origin": variant["_origin"],
            "source_url": variant["url"],
            "original_source_record_sha256": gate.digest(variant),
            "original_source_record_as_selected": copy.deepcopy(variant),
            "article_source_use_as_recorded": source_use,
            "base_fallback_requires_human_scope_review": fallback,
            "shared_url_group_requires_human_review": shared,
            "citation_occurrences": occurrences,
            "all_citation_contexts_for_human_claim_review":
                ["original text evidence"] * occurrences,
            "human_link_checked_by_this_gate": False,
            "human_claim_reviewed_by_this_gate": False,
        }
    cited = signed({
        "schema_version": 1, "issue": 136, "release_state": "HOLD",
        "machine_authority": "STRUCTURAL_CITATION_TO_SOURCE_REVIEW_QUEUE_ONLY",
        "may_publish": False, "independent_QD_approval": False,
        "qualified_safety_clearance": False,
        "human_source_reviews_completed": False,
        "source_claim_accuracy_verified": False,
        "counts": dict(zip((
            "articles", "tools", "citations", "relationships",
            "base_fallback_relationships", "shared_url_groups_unreviewed"),
            CENSUS)),
        "review_queue": [
            relation("a", a, "read carefully", 2, True, True),
            relation("a", c, "other cited source", 1, False, False),
            relation("b", b, "independent historical reading", 1, False, True),
        ],
    })
    scope = {
        "work_order_id_sha256": "A", "article": "a", "block_ordinal": 1,
        "source_id": "s1", "review_state": "NOT_REVIEWED",
        "article_contributor_origin": "start",
        "source_contributor_origin": "base",
        "original_url": SHARED,
        "original_source_record_sha256": gate.digest(a),
        "original_source_use": "read carefully",
        "original_source_reading_scope": a["notes"],
        "original_source_supports_note": a["supports"],
        "base_fallback_requires_human_review": True,
        "shared_url_group_requires_human_review": True,
    }
    action = signed({
        "schema": "r56-private-unverified-action-source-crosswalk-v1",
        "issue": 136, "release_state": "HOLD", "machine_only": True,
        "may_publish": False, "independent_QD_approval": False,
        "qualified_safety_clearance": False,
        "human_source_links_verified": False,
        "claim_accuracy_verified": False,
        "counts": {
            "all_original_action_work_orders": 2,
            "uncited_consequential_action_blocks": 1,
            "cited_consequential_action_blocks": 1,
            "open_safety_exceptions_without_authenticated_clearance": 0,
            "historical_machine_access_holds_not_current_link_failures": 0,
        },
        "original_unreviewed_action_rows": [
            {"work_order_id_sha256": "A", "article": "a",
             "block_ordinal": 1, "review_state": "NOT_REVIEWED",
             "source_readings_count": 1},
            {"work_order_id_sha256": "B", "article": "b",
             "block_ordinal": 2, "review_state": "NOT_REVIEWED",
             "source_readings_count": 0},
        ],
        "original_unreviewed_action_source_rows": [scope],
        "open_safety_exceptions_without_verified_article_mapping": [],
        "historical_access_hold_queue": [],
    })
    return lib, cited, action


def audit(parts=None):
    args = fixture() if parts is None else parts
    return gate.bridge(*args, census=CENSUS, inventory=INVENTORY,
                       action_census=ACTIONS)


class Positive(unittest.TestCase):
    def test_all_original_groups(self):
        self.assertEqual(audit()["counts"]["all_global_shared_url_groups_even_uncited"], 1)

    def test_preserve_all_original_source_variants(self):
        group = audit()["all_global_shared_url_groups_unreviewed"][0]
        self.assertEqual([x["id"] for x in group["all_original_contributor_records"]],
                         ["s1", "s2"])

    def test_preserve_unabridged_unicode_and_reading_depth(self):
        group = audit()["all_global_shared_url_groups_unreviewed"][0]
        self.assertIn("\u202e", group["all_original_contributor_records"][1]["notes"])
        self.assertIn("\nhuman confirmation", group["all_original_contributor_records"][0]["notes"])

    def test_only_one_of_three_relationships_is_fallback(self):
        self.assertEqual(audit()["counts"]["all_base_fallback_source_relationships"], 1)

    def test_unflagged_fallback_is_kept(self):
        x = audit()
        self.assertEqual(len(x["all_base_fallback_relationships_unreviewed"]), 1)
        self.assertEqual(len(x["all_original_cited_relationships_unreviewed"]), 3)

    def test_cited_not_equivalent_to_supported(self):
        self.assertFalse(audit()["source_claim_accuracy_verified"])

    def test_same_block_citation_does_not_clear_safety(self):
        self.assertFalse(audit()["qualified_safety_clearance"])

    def test_no_uncited_source_variant_collapsed(self):
        self.assertEqual(audit()["all_global_shared_url_groups_unreviewed"][0]
                         ["unreviewed_original_crosswalk_group"]["variants"][1]
                         ["source"]["id"], "s2")

    def test_relationships_keep_repeated_citations(self):
        self.assertEqual(audit()["counts"]["all_citation_occurrences"], 4)
        self.assertEqual(audit()["all_original_cited_relationships_unreviewed"][0]
                         ["citation_occurrences"], 2)

    def test_original_action_row_count(self):
        self.assertEqual(len(audit()["all_original_consequential_action_orders_unreviewed"]), 2)

    def test_no_citation_action_still_kept(self):
        self.assertEqual(audit()["all_original_consequential_action_orders_unreviewed"][1]
                         ["source_readings_count"], 0)

    def test_action_scope_is_exact(self):
        self.assertEqual(audit()["all_original_action_source_rows_unreviewed"][0]
                         ["original_source_use"], "read carefully")

    def test_full_group_links_both_cited_source_variants(self):
        group = audit()["all_global_shared_url_groups_unreviewed"][0]
        self.assertEqual({x["source_id"] for x in
                          group["all_cited_relationships_not_only_high_risk"]},
                         {"s1", "s2"})

    def test_unflagged_cited_source_not_silently_removed(self):
        x = audit()
        self.assertEqual(x["counts"]["all_original_article_source_relationships"], 3)

    def test_original_notes_not_modified(self):
        args = fixture()
        frozen = copy.deepcopy(args)
        audit(args)
        self.assertEqual(args, frozen)

    def test_deterministic(self):
        self.assertEqual(audit(), audit())

    def test_release_flags_all_false(self):
        for f in gate.FLAGS:
            self.assertIs(audit()[f], False)

    def test_output_recomputes(self):
        args = fixture()
        result = audit(args)
        self.assertTrue(gate.verify_bridge(*args, result,
                        census=CENSUS, inventory=INVENTORY,
                        action_census=ACTIONS))

    def test_no_global_source_group_auto_clearance(self):
        self.assertEqual(audit()["all_global_shared_url_groups_unreviewed"][0]
                         ["human_source_scope_review"], "NOT_STARTED")

    def test_citation_and_action_parent_sha_present(self):
        x = audit()
        self.assertEqual(x["parent_R25_cited_source_sha256"], fixture()[1]["fingerprint_sha256"])
        self.assertEqual(x["parent_R56_action_source_sha256"], fixture()[2]["fingerprint_sha256"])

    def test_fingerprint(self):
        x = audit()
        self.assertEqual(x["fingerprint_sha256"],
                         gate.digest({k: v for k, v in x.items()
                                      if k != "fingerprint_sha256"}))

    def test_real_original_corpus_if_available(self):
        if not (ROOT / "sources" / "register.json").is_file():
            self.skipTest("original source corpus not present")
        r54 = gate.module("r54_action_review_export.py")
        r56 = gate.module("r56_unreviewed_action_source_crosswalk.py")
        build = gate.module("build.py")
        r25 = gate.module("citation_fallback_review_gate.py")
        lib = build.Library(ROOT)
        r53 = r54.original_report(ROOT.parent)
        action = r56.crosswalk(r53)
        r56.verify_crosswalk(r53, action)
        cited = r25.audit(lib)
        x = gate.bridge(lib, cited, action)
        self.assertEqual(x["counts"]["all_global_shared_url_groups_even_uncited"], 30)
        self.assertEqual(x["counts"]["all_base_fallback_source_relationships"], 43)
        self.assertEqual(x["counts"]["all_citation_occurrences"], 1959)
        self.assertEqual(x["counts"]["all_original_article_source_relationships"], 367)
        self.assertFalse(x["may_publish"])


class Negative(unittest.TestCase):
    def assert_rejected(self, fn):
        args = fixture()
        fn(*args)
        with self.assertRaises(gate.BridgeHold):
            audit(args)

    def test_remove_global_group(self):
        self.assert_rejected(lambda lib, cited, action: lib.crosswalk_groups.clear())

    def test_shortened_url_variant(self):
        self.assert_rejected(lambda lib, cited, action:
            lib.source_variants["s2"][0].__setitem__("notes", "truncated"))

    def test_missing_uncited_variant(self):
        self.assert_rejected(lambda lib, cited, action:
            lib.source_variants.pop("s4"))

    def test_source_url_change(self):
        self.assert_rejected(lambda lib, cited, action:
            lib.source_variants["s1"][0].__setitem__("url", "https://other.org"))

    def test_forged_global_review(self):
        self.assert_rejected(lambda lib, cited, action:
            lib.crosswalk_groups[SHARED].__setitem__("reviewer", "approved"))

    def test_crosswalk_variant_deleted(self):
        self.assert_rejected(lambda lib, cited, action:
            lib.crosswalk_groups[SHARED]["variants"].pop())

    def test_article_origin_swapped(self):
        self.assert_rejected(lambda lib, cited, action:
            lib.article_origins.__setitem__("a", "base"))

    def test_bad_article_source_id(self):
        def f(lib,cited,action):
            cited["review_queue"][0]["source_id"] = "s2"
            signed(cited)
        self.assert_rejected(f)

    def test_repeated_citation_count_changed(self):
        def f(lib,cited,action):
            cited["review_queue"][0]["citation_occurrences"] = 1
            signed(cited)
        self.assert_rejected(f)

    def test_discard_cited_relationship(self):
        def f(lib,cited,action):
            cited["review_queue"].pop()
            signed(cited)
        self.assert_rejected(f)

    def test_promote_human_source_check(self):
        def f(lib,cited,action):
            cited["review_queue"][0]["human_link_checked_by_this_gate"] = True
            signed(cited)
        self.assert_rejected(f)

    def test_invent_qualified_approval(self):
        def f(lib,cited,action):
            action["qualified_safety_clearance"] = True
            signed(action)
        self.assert_rejected(f)

    def test_forged_original_source_scope(self):
        def f(lib,cited,action):
            action["original_unreviewed_action_source_rows"][0][
                "original_source_use"] = "changed source scope"
            signed(action)
        self.assert_rejected(f)

    def test_forged_r56_record_sha(self):
        def f(lib,cited,action):
            action["original_unreviewed_action_source_rows"][0][
                "original_source_record_sha256"] = "f" * 64
            signed(action)
        self.assert_rejected(f)

    def test_forged_r56_link_article(self):
        def f(lib,cited,action):
            action["original_unreviewed_action_source_rows"][0]["article"] = "b"
            signed(action)
        self.assert_rejected(f)

    def test_missing_action_scope(self):
        def f(lib,cited,action):
            action["original_unreviewed_action_source_rows"].clear()
            signed(action)
        self.assert_rejected(f)

    def test_source_variant_origin_collision(self):
        self.assert_rejected(lambda lib,cited,action:
            lib.source_variants["s4"][0].__setitem__("_origin", "start"))

    def test_missing_historic_provenance(self):
        self.assert_rejected(lambda lib,cited,action:
            lib.source_variants["s2"][0].__setitem__("_origin", ""))

    def test_action_report_invalid_fingerprint(self):
        self.assert_rejected(lambda lib,cited,action:
            action.__setitem__("fingerprint_sha256", "f"*64))

    def test_citation_report_invalid_fingerprint(self):
        self.assert_rejected(lambda lib,cited,action:
            cited.__setitem__("fingerprint_sha256", "f"*64))


# 40 independently named adversarial output mutations; original inputs unchanged.
# Even a recomputed/self-hashed forged output is not a substitute for recomputation.
OUTPUT_TAMPERS = [
    ("schema",), ("issue",), ("release_state",), ("machine_only",),
    ("parent_R25_cited_source_sha256",), ("parent_R56_action_source_sha256",),
    ("counts","articles"), ("counts","water_tools"),
    ("counts","all_citation_occurrences"),
    ("counts","all_original_article_source_relationships"),
    ("counts","all_global_shared_url_groups_even_uncited"),
    ("counts","all_base_fallback_source_relationships"),
    ("counts","all_high_consequence_action_orders"),
    ("counts","action_scoped_source_reading_rows"),
    ("counts","shared_groups_with_no_high_consequence_action"),
    ("counts","fallbacks_with_no_high_consequence_action"),
    ("all_global_shared_url_groups_unreviewed",0,"source_url_exact_no_canonicalization"),
    ("all_global_shared_url_groups_unreviewed",0,"unreviewed_original_crosswalk_group",
     "review_status"),
    ("all_global_shared_url_groups_unreviewed",0,"all_original_contributor_records",0,
     "notes"),
    ("all_global_shared_url_groups_unreviewed",0,"all_original_contributor_records",1,
     "supports"),
    ("all_global_shared_url_groups_unreviewed",0,"all_cited_relationships_not_only_high_risk",
     0,"source_id"),
    ("all_global_shared_url_groups_unreviewed",0,"consequential_action_source_rows_if_any",
     0,"original_source_use"),
    ("all_global_shared_url_groups_unreviewed",0,"human_source_scope_review"),
    ("all_global_shared_url_groups_unreviewed",0,"qualified_safety_review"),
    ("all_base_fallback_relationships_unreviewed",0,"full_original_fallback_relationship",
     "citation_occurrences"),
    ("all_base_fallback_relationships_unreviewed",0,"consequential_action_source_rows_if_any",
     0,"source_id"),
    ("all_base_fallback_relationships_unreviewed",0,"human_source_scope_review"),
    ("all_base_fallback_relationships_unreviewed",0,"qualified_safety_review"),
    ("all_original_cited_relationships_unreviewed",0,"source_id"),
    ("all_original_cited_relationships_unreviewed",1,"source_url"),
    ("all_original_cited_relationships_unreviewed",2,"article_source_use_as_recorded"),
    ("all_original_consequential_action_orders_unreviewed",0,"article"),
    ("all_original_consequential_action_orders_unreviewed",1,"source_readings_count"),
    ("all_original_action_source_rows_unreviewed",0,"source_id"),
    ("all_original_action_source_rows_unreviewed",0,"original_url"),
    ("all_original_action_source_rows_unreviewed",0,"original_source_reading_scope"),
    ("may_publish",), ("qualified_safety_clearance",),
    ("independent_QD_approval",), ("human_source_links_verified",),
    ("claim_accuracy_verified",), ("human_source_reviews_completed",),
    ("source_claim_accuracy_verified",), ("limitations",),
    ("fingerprint_sha256",),
]


def output_mutation(path):
    def test(self):
        args = fixture()
        output = audit(args)
        obj = output
        for k in path[:-1]:
            obj = obj[k]
        key = path[-1]
        old = obj[key]
        obj[key] = (not old if type(old) is bool else
                    old + 1 if type(old) is int else
                    "FORGED_REVIEWED" if type(old) is str else [])
        if path != ("fingerprint_sha256",):
            output["fingerprint_sha256"] = gate.digest({
                k: v for k, v in output.items() if k != "fingerprint_sha256"
            })
        with self.assertRaises(gate.BridgeHold):
            gate.verify_bridge(*args, output,
                census=CENSUS, inventory=INVENTORY, action_census=ACTIONS)
    return test


for i, path in enumerate(OUTPUT_TAMPERS, 1):
    setattr(Negative, "test_forged_output_%02d_%s" % (i, path[-1]),
            output_mutation(path))


if __name__ == "__main__":
    unittest.main()
