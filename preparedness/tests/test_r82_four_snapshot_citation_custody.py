"""R82 PRIVATE HOLD: 50+ synthetic/adversarial four-snapshot provenance tests."""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

FILE = Path(__file__).resolve().parents[1] / "tools" / "r82_four_snapshot_citation_custody.py"
SPEC = importlib.util.spec_from_file_location("r82_under_test", FILE)
r82 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r82)

ORIGINS = ("start", "shelter", "food", "health", "hist-food",
           "hist-home", "hist-field")


def as_bytes(obj):
    return json.dumps(obj, ensure_ascii=False).encode("utf-8")


def fake_sources(origin, stage, sid=None, url="https://example.invalid/source",
                 supports="Synthetic evidence only", extra=None):
    record = {"id": sid or "ref-" + origin, "url": url,
              "supports": supports, "human_link_check": False,
              "notes": "Not a human fact check."}
    if extra:
        record.update(extra)
    return r82.fragment(as_bytes({"sources": [record]}), origin, stage)


def fake_article(origin, slug, stage, sources=None, body=None, meta=None):
    raw_body = (body if body is not None else
                ("<p>Synthetic " + stage + " {{cite:ref-" + origin + "}}</p>\n"))
    raw_meta = meta if meta is not None else {
        "slug": slug, "status": {"editorial": "drafted", "publish": "draft"},
        "safety_review": {"state": "pending", "reviewer": None, "date": None}}
    return r82.article(raw_body.encode("utf-8"), as_bytes(raw_meta), origin,
                       "preparedness/content/articles/" + slug + ".body.html",
                       stage, sources or {})


def fake_suite():
    fragments = [fake_sources(origin, stage)
                 for origin in ORIGINS for stage in r82.STAGES]
    snapshots = []
    for number in range(29):
        origin = ORIGINS[number % 7]
        slug = "synthetic-" + str(number)
        for stage in r82.STAGES:
            snapshots.append(fake_article(origin, slug, stage))
    parent = {"branch_reviews": [{"origin": v} for v in ORIGINS],
              "counts": {"rc_fragment_source_readings_UNREVIEWED": 7},
              "sha256_seal": "f" * 64,
              "separate_rc_commit": "a" * 40}
    return snapshots, fragments, parent


def reseal(report):
    report["sha256_seal"] = r82.sha(r82.canonical(
        {k: v for k, v in report.items() if k != "sha256_seal"}))


class CoreConservation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.samples = fake_suite()
        cls.report = r82.construct(*cls.samples)
        r82.verify(cls.report)

    def test_four_snapshot_count(self):
        self.assertEqual(self.report["counts"]["unabridged_article_snapshots"], 116)

    def test_seven_source_fragments_each_stage(self):
        self.assertEqual(self.report["counts"]["unabridged_source_fragments"], 28)

    def test_29_authored_articles_not_claimed_as_35(self):
        self.assertEqual(self.report["counts"]["authored_article_groups"], 29)

    def test_seven_source_readings_not_claimed_as_full_archive(self):
        self.assertEqual(self.report["counts"]["origin_scoped_RC_readings"], 7)

    def test_no_source_alias_across_origins(self):
        groups = self.report["all_four_snapshot_source_histories_NOT_ALIASED"]
        self.assertEqual(len(groups), 7)
        self.assertEqual(len({(g["origin"], g["literal_source_id"])
                              for g in groups}), 7)

    def test_all_four_bodies_retained(self):
        group = self.report["all_29_article_citation_metadata_histories_UNABRIDGED"][0]
        stages = group["four_unabridged_HTML_and_metadata_snapshots"]
        self.assertEqual(set(stages), set(r82.STAGES))
        self.assertIn("<p>Synthetic", stages["rc"]["complete_HTML_UTF8"])

    def test_rc_is_not_fact_check(self):
        self.assertEqual(self.report["human_source_approvals"], 0)
        self.assertEqual(self.report["qualified_safety_approvals"], 0)

    def test_seal_deterministic(self):
        a = r82.construct(*fake_suite())
        self.assertEqual(a["sha256_seal"], self.report["sha256_seal"])

    def test_review_csv_count(self):
        import csv
        import io
        rows = list(csv.DictReader(io.StringIO(r82.reviewer_csv(self.report))))
        self.assertEqual(len(rows), 29 + 7)
        self.assertTrue(all(r["release"] == "HOLD" for r in rows))

    def test_refuse_missing_article(self):
        docs, frags, parent = fake_suite()
        with self.assertRaises(r82.Hold):
            r82.construct(docs[:-1], frags, parent)

    def test_refuse_missing_fragment(self):
        docs, frags, parent = fake_suite()
        with self.assertRaises(r82.Hold):
            r82.construct(docs, frags[:-1], parent)

    def test_refuse_duplicate_article_key(self):
        docs, frags, parent = fake_suite()
        docs[-1] = deepcopy(docs[0])
        with self.assertRaises(r82.Hold):
            r82.construct(docs, frags, parent)

    def test_refuse_duplicate_fragment_key(self):
        docs, frags, parent = fake_suite()
        frags[-1] = deepcopy(frags[0])
        with self.assertRaises(r82.Hold):
            r82.construct(docs, frags, parent)

    def test_refuse_mismatched_RC_source_total(self):
        docs, frags, parent = fake_suite()
        parent["counts"]["rc_fragment_source_readings_UNREVIEWED"] = 210
        with self.assertRaises(r82.Hold):
            r82.construct(docs, frags, parent)

    def test_source_metadata_is_unabridged(self):
        source = self.report["all_four_snapshot_source_fragments_UNABRIDGED"][0]
        self.assertEqual(source["source_readings_UNABRIDGED"][0][
            "complete_reading_UNABRIDGED_NOT_APPROVED"]["notes"],
            "Not a human fact check.")


class SourceDrift(unittest.TestCase):
    def test_no_change(self):
        a = fake_sources("start", "current")
        b = fake_sources("start", "rc")
        rows = r82.compare_sources({("start", "current"): a, ("start", "rc"): b})
        self.assertFalse(rows[0]["comparison"]["current_TO_rc"]["different_reading"])

    def test_url_changed_but_id_kept(self):
        a = fake_sources("start", "current")
        b = fake_sources("start", "rc", url="https://other.invalid/doc")
        rows = r82.compare_sources({("start", "current"): a, ("start", "rc"): b})
        self.assertEqual(rows[0]["comparison"]["current_TO_rc"]["changed_fields"],
                         ["url"])
        self.assertEqual(rows[0]["four_distinct_snapshot_readings"]["current"][
            "literal_url_UNVERIFIED"], "https://example.invalid/source")

    def test_same_URL_supports_changed(self):
        a = fake_sources("start", "current")
        b = fake_sources("start", "rc", supports="Rewritten claim reading")
        rows = r82.compare_sources({("start", "current"): a, ("start", "rc"): b})
        self.assertEqual(rows[0]["comparison"]["current_TO_rc"]["changed_fields"],
                         ["supports"])

    def test_source_id_added(self):
        a = fake_sources("start", "current", sid="old")
        b = fake_sources("start", "rc", sid="new")
        rows = r82.compare_sources({("start", "current"): a, ("start", "rc"): b})
        states = sorted(x["comparison"]["current_TO_rc"]["presence"] for x in rows)
        self.assertEqual(states, ["ADDED", "REMOVED"])

    def test_cross_origin_same_id_is_not_merged(self):
        a = fake_sources("start", "rc", sid="shared")
        b = fake_sources("food", "rc", sid="shared")
        rows = r82.compare_sources({("start", "rc"): a, ("food", "rc"): b})
        self.assertEqual(len(rows), 2)
        self.assertEqual({r["origin"] for r in rows}, {"food", "start"})

    def test_missing_old_record(self):
        before, after = None, {"reading_sha256": "f"}
        self.assertEqual(r82.record_changes(before, after)["presence"], "ADDED")

    def test_removed_record(self):
        before, after = {"reading_sha256": "f"}, None
        self.assertEqual(r82.record_changes(before, after)["presence"], "REMOVED")

    def test_order_field_changes_complete(self):
        one = fake_sources("start", "frozen", extra={"published": "2020"})
        two = fake_sources("start", "current", extra={"published": "2022"})
        rows = r82.compare_sources({("start", "frozen"): one,
                                    ("start", "current"): two})
        self.assertIn("published", rows[0]["comparison"]["frozen_TO_current"][
            "changed_fields"])


class ArticleCitationDrift(unittest.TestCase):
    def test_same_citation_but_new_wording_requires_review(self):
        old = fake_article("start", "same", "current",
                           body="<p>Old claim {{cite:x}}</p>")
        new = fake_article("start", "same", "rc",
                           body="<p>Changed claim {{cite:x}}</p>")
        group = r82.compare_articles({"current": old, "rc": new,
                                      "frozen": old, "integrated": old})
        self.assertTrue(group["current_TO_rc"][
            "wording_changed_without_citation_sequence_change_REVIEW"])

    def test_added_citation(self):
        old = fake_article("start", "same", "current", body="<p>No citation</p>")
        new = fake_article("start", "same", "rc",
                           body="<p>New citation {{cite:new}}</p>")
        group = r82.compare_articles({"current": old, "rc": new,
                                      "frozen": old, "integrated": old})
        self.assertEqual(group["current_TO_rc"]["citation_counts_added"],
                         {"new": 1})

    def test_removed_citation(self):
        old = fake_article("start", "same", "current",
                           body="<p>Removed {{cite:removed}}</p>")
        new = fake_article("start", "same", "rc",
                           body="<p>Removed</p>")
        group = r82.compare_articles({"current": old, "rc": new,
                                      "frozen": old, "integrated": old})
        self.assertEqual(group["current_TO_rc"]["citation_counts_removed"],
                         {"removed": 1})

    def test_reordered_citations(self):
        old = fake_article("start", "same", "current",
                           body="<p>{{cite:a}}{{cite:b}}</p>")
        new = fake_article("start", "same", "rc",
                           body="<p>{{cite:b}}{{cite:a}}</p>")
        group = r82.compare_articles({"current": old, "rc": new,
                                      "frozen": old, "integrated": old})
        self.assertTrue(group["current_TO_rc"]["citation_order_changed"])
        self.assertEqual(group["current_TO_rc"]["citation_counts_removed"], {})

    def test_unknown_scope_is_not_declared_missing(self):
        item = fake_article("start", "same", "rc")
        self.assertEqual(item["citations_in_original_order"][0]["scope_state"],
                         "OUTSIDE_SEVEN_FRAGMENT_SCOPE")

    def test_two_source_origins_remain_unresolved(self):
        sources = {"shared": [{"origin": "start", "source_id": "shared",
                               "reading_sha256": "a"},
                              {"origin": "food", "source_id": "shared",
                               "reading_sha256": "b"}]}
        item = fake_article("start", "same", "rc", sources=sources,
                            body="<p>{{cite:shared}}</p>")
        self.assertEqual(item["citations_in_original_order"][0]["scope_state"],
                         "MULTIPLE_ORIGIN_VARIANTS_UNRESOLVED")
        self.assertEqual(len(item["citations_in_original_order"][0][
            "distinct_scoped_source_variants_NOT_ALIASED"]), 2)

    def test_literal_byte_offsets(self):
        results = r82.citations("café\n{{cite:x}} \n{{cite:y}}".encode("utf-8"))
        self.assertEqual(results[0]["byte_offset"], len("café\n".encode("utf-8")))
        self.assertEqual([x["line_number"] for x in results], [2, 3])

    def test_never_approve_citations(self):
        events = r82.citations(b"{{cite:test}}")
        self.assertEqual(events[0]["claim_support_review"], "NOT_REVIEWED")

    def test_metadata_drift_without_body_change(self):
        old = fake_article("start", "same", "current")
        candidate = fake_article("start", "same", "rc",
                                 body=old["complete_HTML_UTF8"],
                                 meta={"slug": "same", "status": {"publish": "draft"},
                                       "safety_review": {"state": "pending"},
                                       "extra": "Changed editorial metadata"})
        group = r82.compare_articles({"current": old, "rc": candidate,
                                      "frozen": old, "integrated": old})
        self.assertTrue(group["current_TO_rc"]["metadata_changed"])
        self.assertFalse(group["current_TO_rc"]["body_changed"])


class AdversarialTampering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = r82.construct(*fake_suite())

    def test_digest_detects_changed_article(self):
        report = deepcopy(self.base)
        report["all_29_article_citation_metadata_histories_UNABRIDGED"][0][
            "four_unabridged_HTML_and_metadata_snapshots"]["rc"]["complete_HTML_UTF8"] += "x"
        with self.assertRaises(r82.Hold):
            r82.verify(report)

    def test_digest_detects_publish_flip(self):
        report = deepcopy(self.base)
        report["may_publish"] = True
        reseal(report)
        with self.assertRaises(r82.Hold):
            r82.verify(report)

    def test_digest_detects_false_safety_approval(self):
        report = deepcopy(self.base)
        report["qualified_safety_approvals"] = 1
        reseal(report)
        with self.assertRaises(r82.Hold):
            r82.verify(report)

    def test_digest_detects_false_QD_approval(self):
        report = deepcopy(self.base)
        report["independent_QD_approvals"] = 1
        reseal(report)
        with self.assertRaises(r82.Hold):
            r82.verify(report)

    def test_digest_detects_deleted_fragment_even_if_resealed(self):
        report = deepcopy(self.base)
        report["all_four_snapshot_source_fragments_UNABRIDGED"].pop()
        reseal(report)
        with self.assertRaises(r82.Hold):
            r82.verify(report)

    def test_digest_detects_deleted_article_even_if_resealed(self):
        report = deepcopy(self.base)
        report["all_29_article_citation_metadata_histories_UNABRIDGED"].pop()
        reseal(report)
        with self.assertRaises(r82.Hold):
            r82.verify(report)

    def test_digest_detects_wrong_article_count(self):
        report = deepcopy(self.base)
        report["counts"]["authored_article_groups"] = 35
        reseal(report)
        with self.assertRaises(r82.Hold):
            r82.verify(report)


class InputSafety(unittest.TestCase):
    def test_csv_formula_escape(self):
        for value in ("=1+1", "+CMD", "-1", "@A1", " \t=foo", "\r=SUM(A:A)"):
            with self.subTest(value=value):
                self.assertTrue(r82.safe_csv(value).startswith("'"))

    def test_csv_safe_values_are_not_modified(self):
        for value in ("good", "value-with-hyphen", "https://example.invalid"):
            self.assertEqual(r82.safe_csv(value), value)

    def test_duplicate_JSON_key_rejected(self):
        with self.assertRaises(r82.Hold):
            r82.strict_json(b'{"x":1,"x":2}', "synthetic")

    def test_nested_duplicate_JSON_key_rejected(self):
        with self.assertRaises(r82.Hold):
            r82.strict_json(b'{"x":{"a":1,"a":2}}', "synthetic")

    def test_nonfinite_JSON_rejected(self):
        with self.assertRaises(r82.Hold):
            r82.strict_json(b'{"x":NaN}', "synthetic")

    def test_non_UTF8_JSON_rejected(self):
        with self.assertRaises(r82.Hold):
            r82.strict_json(b"\xff", "synthetic")

    def test_trailing_JSON_rejected(self):
        with self.assertRaises(r82.Hold):
            r82.strict_json(b"{} {}", "synthetic")

    def test_rc_source_must_not_be_human_approved(self):
        with self.assertRaises(r82.Hold):
            fake_sources("start", "rc", extra={"human_link_check": True})

    def test_rc_meta_must_not_claim_publication(self):
        with self.assertRaises(r82.Hold):
            fake_article("start", "same", "rc", meta={
                "slug": "same", "status": {"publish": "published"},
                "safety_review": {"state": "pending"}})

    def test_rc_meta_must_not_claim_safety_approval(self):
        with self.assertRaises(r82.Hold):
            fake_article("start", "same", "rc", meta={
                "slug": "same", "status": {"publish": "draft"},
                "safety_review": {"state": "approved"}})

    def test_slug_mismatch_rejected(self):
        with self.assertRaises(r82.Hold):
            fake_article("start", "same", "rc", meta={
                "slug": "wrong", "status": {"publish": "draft"},
                "safety_review": {"state": "pending"}})

    def test_missing_citation_ID_rejected(self):
        with self.assertRaises(r82.Hold):
            r82.citations(b"{{cite:}}")

    def test_leading_space_citation_ID_rejected(self):
        with self.assertRaises(r82.Hold):
            r82.citations(b"{{cite: bad}}")

    def test_invalid_UTF8_body_rejected(self):
        with self.assertRaises(r82.Hold):
            r82.citations(b"\xff{{cite:x}}")

    def test_invalid_stage_rejected(self):
        with self.assertRaises(r82.Hold):
            fake_sources("start", "publishing")


BAD_FRAGMENTS = [
    b"", b"\xff", b"null", b"[]", b"{}", b'{"sources":null}',
    b'{"sources":{}}', b'{"sources":[null]}', b'{"sources":[{}]}',
    b'{"sources":[{"id":"x"}]}',
    b'{"sources":[{"id":12,"url":"https://a"}]}',
    b'{"sources":[{"id":"x","url":3}]}',
    b'{"sources":[{"id":"x","url":""}]}',
    b'{"sources":[{"id":"x","url":"https://a"},{"id":"x","url":"https://b"}]}',
    b'{"sources":[{"id":"x","url":"https://a","human_link_check":true}]}',
    b'{"sources":[{"id":"x","url":"https://a","human_link_check":"false"}]}',
    b'{"sources":[{"id":"x","url":"https://a","human_link_check":false,"id":"x"}]}',
]
for n, raw in enumerate(BAD_FRAGMENTS):
    def malformed(self, raw=raw):
        with self.assertRaises(r82.Hold):
            r82.fragment(raw, "start", "rc")
    setattr(InputSafety, "test_invalid_fragment_%02d" % n, malformed)


BAD_CITE_IDS = [" ", "\t", " foo", "foo ", "\nfoo", "foo\n"]
for n, value in enumerate(BAD_CITE_IDS):
    def invalid_citation(self, value=value):
        with self.assertRaises(r82.Hold):
            r82.citations(("{{cite:" + value + "}}").encode("utf-8"))
    setattr(InputSafety, "test_invalid_cite_%02d" % n, invalid_citation)


if __name__ == "__main__":
    unittest.main()
