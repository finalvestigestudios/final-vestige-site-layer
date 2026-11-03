"""R103 30 shared-URL / 35+1 draft reviewer-export tests.

Source changes are in-memory only. Never create source fixtures in the shared
working tree. These tests do NOT authorize factual, medical or QD approval.
"""
from __future__ import annotations

import copy
import csv
import io
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build
import r102_author_scoped_collision_workorder as parent
import r103_collision_offline_reviewer_handoff as gate


class RealCorpus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = build.Library()
        cls.upstream = parent.workorder(cls.lib)
        cls.docket = gate.packet(cls.upstream, parent.workorder(build.Library()))
        cls.slugs = sorted(cls.lib.articles)

    def test_full_original_inventory_exact(self):
        self.assertEqual(len(self.slugs), 36)
        self.assertEqual(self.docket["literal_url_groups"], 30)
        self.assertEqual(self.docket["missing_planned_tools"], 5)
        self.assertEqual(self.docket["variant_rows"] +
                         self.docket["collision_citation_occurrences"],
                         self.docket["rows_total"])

    def test_independent_parent_replay(self):
        gate.verified_parent(self.upstream, parent.workorder(build.Library()))

    def test_seal_exact(self):
        self.assertEqual(self.docket["sha256_seal"],
                         parent.digest({k: v for k,v in self.docket.items()
                                        if k != "sha256_seal"}))

    def test_no_new_claim_or_safety_approvals(self):
        for flag in ("human_source_and_claim_review", "qualified_safety_review",
                     "independent_QD", "browser_and_wordpress_QA"):
            self.assertEqual(self.docket[flag], "NOT_REVIEWED")
        self.assertIs(self.docket["may_publish"], False)
        self.assertIs(self.docket["may_merge"], False)

    def test_html_is_offline_static_no_active_links(self):
        output = gate.html_text(self.docket)
        self.assertIn("PRIVATE DRAFT", output)
        self.assertIn("Content-Security-Policy", output)
        self.assertNotIn("<script", output)
        self.assertNotIn("<iframe", output)
        self.assertNotIn("<a href", output)
        self.assertNotIn("<form", output)
        self.assertEqual(output.count("<section>"), 30)
        self.assertEqual(output.count("</section>"), 30)

    def test_html_preserves_unverified_labels(self):
        s = gate.html_text(self.docket)
        self.assertIn("No source or claim has been approved", s)
        self.assertIn("exact source edition", s)
        self.assertIn("Original authored citation occurrence", s)
        self.assertIn("Distinct source variant", s)

    def test_csv_full_source_variant_census(self):
        content = gate.csv_text(self.docket, "SOURCE_VARIANT")
        rows = list(csv.DictReader(io.StringIO(content)))
        self.assertEqual(len(rows), self.docket["variant_rows"])
        self.assertEqual([r["record_kind"] for r in rows],
                         ["SOURCE_VARIANT"]*len(rows))
        self.assertTrue(all(r["human_source_review"] == "NOT_REVIEWED"
                            for r in rows))

    def test_csv_full_citation_occurrence_census(self):
        content = gate.csv_text(self.docket, "CITATION_OCCURRENCE")
        rows = list(csv.DictReader(io.StringIO(content)))
        self.assertEqual(len(rows), self.docket["collision_citation_occurrences"])
        self.assertTrue(all(r["human_claim_review"] == "NOT_REVIEWED"
                            for r in rows))

    def test_csv_exact_quoted_headers(self):
        for kind in ("SOURCE_VARIANT", "CITATION_OCCURRENCE"):
            x = gate.csv_text(self.docket, kind)
            self.assertTrue(x.startswith('"group_number","group_sha256"'))
            self.assertIn('"may_publish"',x)

    def test_source_details_recoverable_without_truncation(self):
        for g in self.docket["groups"]:
            for row in g["rows"]:
                self.assertEqual(row["original_record_sha256"],
                                 parent.digest(json.loads(
                                     row["source_or_context_original_json_NOT_VERIFIED"])))
                self.assertEqual(len(row["original_record_sha256"]),64)

    def test_source_record_not_claim_verified(self):
        for group in self.docket["groups"]:
            for row in group["rows"]:
                self.assertEqual(row["qualified_safety_review"], "NOT_REVIEWED")
                self.assertIs(row["may_publish"], False)
                self.assertEqual(row["group_sha256"],group["group_sha256"])

    def test_all_original_group_data_preserved(self):
        for g,original in zip(self.docket["groups"],self.upstream["groups"]):
            self.assertEqual(g["group_sha256"],parent.digest(original))
            self.assertEqual(g["variant_count"],len(original["variants"]))
            self.assertEqual(g["citation_occurrences"],
                             len(original["author_bound_citation_contexts"]))
            self.assertEqual(g["literal_url_NOT_VERIFIED"],original["literal_url"])

    def test_legacy_approvals_do_not_become_new_approval(self):
        self.assertTrue(all(row["human_claim_review"] == "NOT_REVIEWED"
                            for g in self.docket["groups"] for row in g["rows"]))

    def test_no_implicit_url_normalization(self):
        self.assertEqual([g["literal_url_NOT_VERIFIED"]
                          for g in self.docket["groups"]],
                         [g["literal_url"] for g in self.upstream["groups"]])

    def test_both_csvs_are_deterministic(self):
        for kind in ("SOURCE_VARIANT", "CITATION_OCCURRENCE"):
            self.assertEqual(gate.csv_text(self.docket,kind),
                             gate.csv_text(self.docket,kind))

    def test_html_deterministic(self):
        self.assertEqual(gate.html_text(self.docket),gate.html_text(self.docket))

    def test_citation_records_carry_source_use(self):
        rows=[r for g in self.docket["groups"] for r in g["rows"]
              if r["record_kind"]=="CITATION_OCCURRENCE"]
        self.assertTrue(all(r["author_source_use_or_recorded_support"]
                            for r in rows))
        self.assertTrue(all(r["article_slug"] in self.lib.articles for r in rows))

    def test_csv_injection_payload_protection(self):
        dangerous=("=1+1"," +cmd()","-SUM(1,2)","@A1","\t=malicious",
                   "\r=evil","\n=evil","\ufeff=cmd","\u200b=cmd")
        for value in dangerous:
            with self.subTest(value=value):
                self.assertTrue(gate.neutralize(value).startswith("'"))
        self.assertEqual(gate.neutralize("https://example.org/"),"https://example.org/")
        self.assertEqual(gate.neutralize("Regular source"),"Regular source")

    def test_html_entity_escape_adversarial_string(self):
        fake=copy.deepcopy(self.docket)
        fake["groups"][0]["rows"][0]["source_or_context_original_json_NOT_VERIFIED"] = (
            '</pre><script>alert("unsafe")</script><a href="https://evil/">x</a>')
        output=gate.html_text(fake)
        self.assertNotIn("<script>", output)
        self.assertNotIn("<a href=", output)
        self.assertIn("&lt;script&gt;", output)
        self.assertIn("&lt;/pre&gt;", output)

    def test_unknown_csv_kind_denied(self):
        with self.assertRaises(gate.Gate):
            gate.csv_text(self.docket,"OTHER")


def group_test(i):
    def test(self):
        g=self.docket["groups"][i]
        source=self.upstream["groups"][i]
        self.assertEqual(g["literal_url_NOT_VERIFIED"],source["literal_url"])
        self.assertEqual(g["group_number"],i+1)
        self.assertEqual(len(g["rows"]),
                         len(source["variants"])+len(source["author_bound_citation_contexts"]))
        self.assertEqual(sum(r["record_kind"]=="CITATION_OCCURRENCE"
                             for r in g["rows"]),source["citation_occurrences"])
        self.assertTrue(all(r["group_sha256"]==g["group_sha256"] for r in g["rows"]))
        self.assertEqual(g["human_review"],"NOT_REVIEWED")
    return test

for _i in range(30):
    setattr(RealCorpus, f"test_corpus_shared_url_group_{_i+1:02d}", group_test(_i))


def article_test(i):
    def test(self):
        slug=self.slugs[i]
        meta=self.lib.articles[slug]
        article_uses=[r for g in self.docket["groups"] for r in g["rows"]
                      if r["article_slug"]==slug]
        self.assertEqual(meta["status"]["publish"],"draft")
        self.assertTrue(all(r["record_kind"]=="CITATION_OCCURRENCE" for r in article_uses))
        self.assertTrue(all(r["author_source_use_or_recorded_support"]==
                            meta["source_use"][r["literal_source_id"]]
                            for r in article_uses))
        self.assertTrue(all(r["article_origin"]==self.lib.article_origins[slug]
                            for r in article_uses))
    return test

for _i in range(36):
    setattr(RealCorpus, f"test_original_draft_author_scope_{_i+1:02d}", article_test(_i))


class Adversarial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=parent.workorder(build.Library())

    def mutated(self,change):
        tamper=copy.deepcopy(self.original)
        change(tamper)
        tamper["sha256_seal"]=parent.digest({k:v for k,v in tamper.items()
                                             if k != "sha256_seal"})
        return tamper

    def assert_hold(self,change):
        with self.assertRaises(gate.Gate):
            gate.packet(self.mutated(change),self.original)

    def test_resealed_source_support_forgery_rejected(self):
        self.assert_hold(lambda a:a["groups"][0]["variants"][0].update(
            {"supports_as_recorded_not_independently_verified":"Approved!"}))

    def test_resealed_url_replacement_rejected(self):
        self.assert_hold(lambda a:a["groups"][0].update(
            {"literal_url":"https://untrusted.example/"}))

    def test_resealed_false_source_review_rejected(self):
        self.assert_hold(lambda a:a["groups"][0].update({"human_review":"APPROVED"}))

    def test_resealed_independent_qd_rejected(self):
        self.assert_hold(lambda a:a.update({"independent_QD":"PASS"}))

    def test_resealed_publish_rejected(self):
        self.assert_hold(lambda a:a.update({"may_publish":True}))

    def test_resealed_merge_rejected(self):
        self.assert_hold(lambda a:a.update({"may_merge":True}))

    def test_resealed_deleted_group_rejected(self):
        self.assert_hold(lambda a:a["groups"].pop())

    def test_resealed_deleted_variant_rejected(self):
        self.assert_hold(lambda a:a["groups"][0]["variants"].pop())

    def test_resealed_deleted_citation_rejected(self):
        target=next((g for g in self.original["groups"]
                     if g["author_bound_citation_contexts"]),None)
        self.assertIsNotNone(target)
        ix=self.original["groups"].index(target)
        self.assert_hold(lambda a:a["groups"][ix]["author_bound_citation_contexts"].pop())

    def test_resealed_safety_state_rejected(self):
        self.assert_hold(lambda a:a.update({"qualified_safety_review":"APPROVED"}))

    def test_resealed_claim_review_rejected(self):
        self.assert_hold(lambda a:a.update({"source_claim_support_review":"APPROVED"}))

    def test_resealed_count_manipulation_rejected(self):
        self.assert_hold(lambda a:a.update({"original_article_drafts":41}))

    def test_unsealed_report_rejected(self):
        x=copy.deepcopy(self.original)
        x["sha256_seal"]="0"*64
        with self.assertRaises(gate.Gate):
            gate.verified_parent(x,x)

    def test_fake_self_replayed_report_rejects_state(self):
        x=self.mutated(lambda a:a.update({"qualified_safety_review":"APPROVED"}))
        with self.assertRaises(gate.Gate):
            gate.verified_parent(x,x)

    def test_fake_self_replayed_count_rejected(self):
        x=self.mutated(lambda a:a.update({"actual_buildable_tools":6}))
        with self.assertRaises(gate.Gate):
            gate.verified_parent(x,x)

    def test_formula_ordinary_punctuation_allowed(self):
        self.assertEqual(gate.neutralize("Research — priorities"),"Research — priorities")
        self.assertEqual(gate.neutralize("2026-11-03"),"2026-11-03")

    def test_csv_kind_selection_distinct(self):
        doc=gate.packet(self.original,self.original)
        v=gate.csv_text(doc,"SOURCE_VARIANT")
        c=gate.csv_text(doc,"CITATION_OCCURRENCE")
        self.assertNotEqual(v,c)

    def test_source_excerpt_quote_escape_is_data(self):
        doc=gate.packet(self.original,self.original)
        fake=copy.deepcopy(doc)
        fake["groups"][0]["rows"][0]["source_or_context_original_json_NOT_VERIFIED"]='=HYPERLINK("http://evil")'
        csvout=gate.csv_text(fake,"SOURCE_VARIANT")
        rows=list(csv.DictReader(io.StringIO(csvout)))
        self.assertEqual(rows[0]["source_or_context_original_json_NOT_VERIFIED"],
                         '\'=HYPERLINK("http://evil")')

    def test_parent_immutability_during_export(self):
        before=parent.digest(self.original)
        doc=gate.packet(self.original,self.original)
        gate.html_text(doc)
        gate.csv_text(doc,"SOURCE_VARIANT")
        self.assertEqual(parent.digest(self.original),before)


if __name__=="__main__":
    unittest.main()
