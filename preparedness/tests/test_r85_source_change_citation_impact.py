"""R85 private HOLD: adversarial source-history and retained-citation impact tests."""
from __future__ import annotations

from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "r85_under_test", ROOT / "tools" / "r85_source_change_citation_impact.py")
r85 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r85)
r84 = r85.parent()


def reading(url="https://example.org/a", sid="s", **extra):
    return {"id": sid, "url": url, "kind": "synthetic", "publisher": "test",
            "human_link_check": False, "supports": "synthetic research", **extra}


def source(stage="current", origin="water", data=None):
    obj = data if data is not None else reading()
    return {
        "stage": stage, "origin": origin, "literal_source_ID": obj["id"],
        "reading_sha256": r85.digest(obj), "reading_ordinal": 0,
        "complete_original_reading_UNABRIDGED_NOT_APPROVED": deepcopy(obj),
        "url_observation": r84.url_observation(obj["url"]),
        "human_source_review": "NOT_REVIEWED",
        "qualified_safety_review": "NOT_REVIEWED", "may_publish": False,
    }


def anchor(text="Original instruction.", ordinal=0, sid="s"):
    return {"raw_source_id": sid, "ordinal": ordinal,
            "container_text_digest": r85.digest(text),
            "complete_container_text_UNABRIDGED": text,
            "source_scope_state": "ONE_SCOPED_CANDIDATE_NOT_CLAIM_PROOF"}


def edge(stage="current", original=None, item=None, origin="water", path="a"):
    original = original if original is not None else anchor()
    item = item if item is not None else source(stage, origin)
    return {"stage": stage, "article_origin": origin, "article_path": path,
            "citation_ordinal": original["ordinal"],
            "literal_raw_source_ID": original["raw_source_id"],
            "R83_complete_anchor_sha256": r85.digest(original),
            "exact_source_edges_NOT_LINK_OR_CLAIM_APPROVED": [{
                "origin": item["origin"], "literal_source_ID": item["literal_source_ID"],
                "reading_sha256": item["reading_sha256"],
                "literal_URL_UNVERIFIED_UNCHANGED":
                    item["url_observation"]["literal_URL_UNVERIFIED_UNCHANGED"],
                "URL_review_cues_NOT_VERDICTS": [],
                "human_claim_support": "NOT_REVIEWED",
                "qualified_safety_review": "NOT_REVIEWED"}],
            "review_cues_NOT_VERDICTS": [],
            "human_claim_support": "NOT_REVIEWED",
            "qualified_safety_review": "NOT_REVIEWED", "may_publish": False}


def review(before=None, after=None, origin="water", path="a", sid="s"):
    return {"origin": origin, "path": path,
            "current_TO_rc_occurrence_rank_review": [{
                "raw_source_id": sid, "within_ID_occurrence": 1,
                "before_FULL_ANCHOR": before, "after_FULL_ANCHOR": after,
                "review_cues_NOT_VERDICTS": [],
                "human_claim_support_review": "NOT_REVIEWED",
                "qualified_safety_review": "NOT_REVIEWED", "may_publish": False}]}


class SourceHistories(unittest.TestCase):
    def test_four_stages_never_collapse(self):
        rows = [source(stage) for stage in r85.STAGES]
        result = r85.source_histories(rows, [])
        self.assertEqual(len(result), 1)
        self.assertEqual(sum(x is not None for x in result[0][
            "four_complete_original_source_snapshots_UNABRIDGED_NOT_APPROVED"].values()), 4)
        self.assertFalse(result[0]["may_publish"])

    def test_origin_scoping_keeps_same_id_distinct(self):
        rows = [source("current", a) for a in ("food", "water", "health")]
        result = r85.source_histories(rows, [])
        self.assertEqual(len(result), 3)
        self.assertEqual({x["origin"] for x in result}, {"food", "water", "health"})

    def test_literal_url_change_flag_not_truth(self):
        rows = [source("current"), source("rc", data=reading("https://example.org/new"))]
        result = r85.source_histories(rows, [])
        self.assertIn("EXACT_LITERAL_URL_CHANGED_REVIEW",
                      result[0]["current_TO_rc_review_cues_NOT_VERDICTS"])
        self.assertIn("COMPLETE_SOURCE_READING_CHANGED_REVIEW",
                      result[0]["current_TO_rc_review_cues_NOT_VERDICTS"])

    def test_addition_without_guessed_earlier_snapshot(self):
        item = r85.source_histories([source("rc")], [])[0]
        self.assertIsNone(item[
            "four_complete_original_source_snapshots_UNABRIDGED_NOT_APPROVED"]["current"])
        self.assertIn("SOURCE_ADDED_OR_REMOVED_CURRENT_TO_RC_REVIEW",
                      item["current_TO_rc_review_cues_NOT_VERDICTS"])

    def test_removal_without_reassigning_source(self):
        item = r85.source_histories([source("current")], [])[0]
        self.assertIsNone(item[
            "four_complete_original_source_snapshots_UNABRIDGED_NOT_APPROVED"]["rc"])
        self.assertIn("SOURCE_ADDED_OR_REMOVED_CURRENT_TO_RC_REVIEW",
                      item["current_TO_rc_review_cues_NOT_VERDICTS"])

    def test_metadata_only_change_not_labeled_url_drift(self):
        rows = [source("current"), source("rc", data=reading(notes="changed"))]
        cues = r85.source_histories(rows, [])[0]["current_TO_rc_review_cues_NOT_VERDICTS"]
        self.assertIn("COMPLETE_SOURCE_READING_CHANGED_REVIEW", cues)
        self.assertNotIn("EXACT_LITERAL_URL_CHANGED_REVIEW", cues)

    def test_same_source_exact_match_no_auto_approval(self):
        item = r85.source_histories([source("current"), source("rc")], [])[0]
        self.assertEqual(item["current_TO_rc_review_cues_NOT_VERDICTS"], [])
        self.assertEqual(item["human_claim_support"], "NOT_REVIEWED")
        self.assertFalse(item["may_publish"])

    def test_duplicate_same_stage_origin_id_fails(self):
        with self.assertRaises(r85.Hold):
            r85.source_histories([source(), source()], [])

    def test_source_digest_tampering_rejected(self):
        item = source()
        item["reading_sha256"] = "0" * 64
        with self.assertRaises(r85.Hold):
            r85.source_histories([item], [])

    def test_source_body_tampering_rejected(self):
        item = source()
        item["complete_original_reading_UNABRIDGED_NOT_APPROVED"]["supports"] = "false"
        with self.assertRaises(r85.Hold):
            r85.source_histories([item], [])

    def test_source_id_mutation_rejected(self):
        item = source()
        item["literal_source_ID"] = "different"
        with self.assertRaises(r85.Hold):
            r85.source_histories([item], [])

    def test_original_url_rewriting_rejected(self):
        item = source()
        item["url_observation"]["literal_URL_UNVERIFIED_UNCHANGED"] = "http://wrong"
        with self.assertRaises(r85.Hold):
            r85.source_histories([item], [])

    def test_cited_source_keeps_original_occurrence(self):
        a = anchor()
        s = source()
        hits = r85.source_histories([s], [edge(original=a, item=s)])
        self.assertEqual(hits[0]["all_exact_citation_impacts_BY_STAGE_NOT_APPROVED"][
            "current"][0]["citation_ordinal"], 0)

    def test_source_edge_digest_mismatch_fails(self):
        s = source()
        e = edge(item=s)
        e["exact_source_edges_NOT_LINK_OR_CLAIM_APPROVED"][0]["reading_sha256"] = "1"*64
        with self.assertRaises(r85.Hold):
            r85.source_histories([s], [e])

    def test_source_edge_url_mismatch_fails(self):
        s = source()
        e = edge(item=s)
        e["exact_source_edges_NOT_LINK_OR_CLAIM_APPROVED"][0][
            "literal_URL_UNVERIFIED_UNCHANGED"] = "https://attacker"
        with self.assertRaises(r85.Hold):
            r85.source_histories([s], [e])

    def test_source_edge_missing_original_reading_fails(self):
        with self.assertRaises(r85.Hold):
            r85.source_histories([], [edge()])

    def test_citation_source_id_mismatch_fails(self):
        e = edge()
        e["exact_source_edges_NOT_LINK_OR_CLAIM_APPROVED"][0]["literal_source_ID"] = "z"
        with self.assertRaises(r85.Hold):
            r85.source_histories([source()], [e])

    def test_double_citation_source_edge_fails(self):
        s = source()
        e = edge(item=s)
        with self.assertRaises(r85.Hold):
            r85.source_histories([s], [e, deepcopy(e)])

    def test_original_source_reading_unabridged(self):
        original = reading(notes="A" * 6000)
        result = r85.source_histories([source(data=original)], [])
        preserved = result[0][
            "four_complete_original_source_snapshots_UNABRIDGED_NOT_APPROVED"]["current"]
        self.assertEqual(preserved["complete_original_reading_UNABRIDGED_NOT_APPROVED"], original)

    def test_multiple_stages_all_uses_preserved(self):
        ss = [source(x) for x in r85.STAGES]
        es = [edge(stage=x, item=s) for x,s in zip(r85.STAGES,ss)]
        histories = r85.source_histories(ss, es)
        self.assertEqual([len(histories[0]["all_exact_citation_impacts_BY_STAGE_NOT_APPROVED"][x])
                          for x in r85.STAGES], [1,1,1,1])


class CitationEdges(unittest.TestCase):
    def test_link_uses_exact_anchor_digest(self):
        a=anchor()
        e=edge(original=a)
        self.assertEqual(r85.linked_edge(a,"current","water","a",
                         r85.edge_index([e])),e)

    def test_modified_claim_context_cannot_reuse_old_edge(self):
        e=edge(original=anchor("Drink untested water"))
        with self.assertRaises(r85.Hold):
            r85.linked_edge(anchor("Do not drink untested water"),
                            "current","water","a",r85.edge_index([e]))

    def test_wrong_article_origin_fails(self):
        e=edge()
        with self.assertRaises(r85.Hold):
            r85.linked_edge(anchor(),"current","food","a",r85.edge_index([e]))

    def test_wrong_ordinal_fails(self):
        with self.assertRaises(r85.Hold):
            r85.linked_edge(anchor(ordinal=2),"current","water","a",
                            r85.edge_index([edge()]))

    def test_wrong_stage_fails(self):
        with self.assertRaises(r85.Hold):
            r85.linked_edge(anchor(),"rc","water","a",r85.edge_index([edge()]))

    def test_missing_original_anchor_has_no_citation(self):
        self.assertIsNone(r85.linked_edge(None,"rc","water","a",{}))

    def test_duplicate_same_occurrence_fails(self):
        with self.assertRaises(r85.Hold):
            r85.edge_index([edge(),edge()])

    def test_unreviewed_state_enforced(self):
        e=edge()
        e["human_claim_support"]="APPROVED"
        with self.assertRaises(r85.Hold):
            r85.edge_index([e])

    def test_may_publish_fails_closed(self):
        e=edge()
        e["may_publish"]=True
        with self.assertRaises(r85.Hold):
            r85.edge_index([e])

    def test_source_variant_is_not_url_alias(self):
        a=edge()
        b=deepcopy(a)
        b["exact_source_edges_NOT_LINK_OR_CLAIM_APPROVED"][0][
            "literal_URL_UNVERIFIED_UNCHANGED"] = "https://example.org/case"
        self.assertNotEqual(r85.candidate_fingerprint(a),
                            r85.candidate_fingerprint(b))


class CitationChanges(unittest.TestCase):
    def test_retained_citation_changed_passage_flag(self):
        a,b=anchor("A sentence"),anchor("A different sentence")
        s=source()
        index=r85.edge_index([edge(original=a,item=s),
                              edge("rc",original=b,item=source("rc"))])
        result=r85.citation_changes([review(a,b)],index)
        self.assertIn("RETAINED_CITATION_CHANGED_PASSAGE_REVIEW",
                      result[0]["review_cues_NOT_VERDICTS"])

    def test_retained_citation_changed_source_url_flag(self):
        a,b=anchor(),anchor()
        index=r85.edge_index([edge(original=a),edge("rc",original=b,
            item=source("rc",data=reading("https://example.org/new")))])
        row=r85.citation_changes([review(a,b)],index)[0]
        self.assertIn("LITERAL_SOURCE_URL_SCOPE_DRIFT_REVIEW",row[
            "review_cues_NOT_VERDICTS"])

    def test_source_reading_changed_same_url_flag(self):
        a,b=anchor(),anchor()
        index=r85.edge_index([edge(original=a),edge("rc",original=b,
                    item=source("rc",data=reading(notes="changed")))])
        cues=r85.citation_changes([review(a,b)],index)[0][
            "review_cues_NOT_VERDICTS"]
        self.assertIn("EXACT_SOURCE_READING_OR_LITERAL_URL_DRIFT_REVIEW",cues)
        self.assertNotIn("LITERAL_SOURCE_URL_SCOPE_DRIFT_REVIEW",cues)

    def test_source_cue_for_human_review_no_verdict(self):
        a,b=anchor(),anchor()
        e=edge()
        e["review_cues_NOT_VERDICTS"]=["NOT_LITERAL_HTTPS_REVIEW"]
        index=r85.edge_index([e,edge("rc")])
        row=r85.citation_changes([review(a,b)],index)[0]
        self.assertIn("ORIGINAL_SOURCE_URL_OR_SCOPE_CUE_REVIEW",
                      row["review_cues_NOT_VERDICTS"])
        self.assertEqual(row["human_claim_review"],"NOT_REVIEWED")

    def test_added_citation_retains_null_original(self):
        b=anchor()
        rows=r85.citation_changes([review(None,b)],
                                  r85.edge_index([edge("rc",original=b)]))
        self.assertIsNone(rows[0]["exact_current_source_edges_NOT_APPROVED"])
        self.assertIn("CITATION_ADDED_OR_REMOVED_REVIEW",rows[0][
            "review_cues_NOT_VERDICTS"])

    def test_removed_citation_retains_null_rc(self):
        a=anchor()
        rows=r85.citation_changes([review(a,None)],r85.edge_index([edge()]))
        self.assertIsNone(rows[0]["exact_RC_source_edges_NOT_APPROVED"])
        self.assertIn("CITATION_ADDED_OR_REMOVED_REVIEW",
                      rows[0]["review_cues_NOT_VERDICTS"])

    def test_no_change_does_not_mean_approved(self):
        a,b=anchor(),anchor()
        rows=r85.citation_changes([review(a,b)],r85.edge_index([
                                 edge(),edge("rc")]))
        self.assertFalse(rows[0]["review_cues_NOT_VERDICTS"])
        self.assertEqual(rows[0]["human_claim_review"],"NOT_REVIEWED")
        self.assertFalse(rows[0]["may_publish"])

    def test_repeated_rank_review_cannot_double_count(self):
        a=anchor()
        p=review(a,a)
        with self.assertRaises(r85.Hold):
            r85.citation_changes([p,deepcopy(p)],
                                 r85.edge_index([edge(),edge("rc")]))

    def test_distinct_source_id_reviews_not_conflated(self):
        a=anchor()
        b=anchor(sid="x",ordinal=1)
        ix=r85.edge_index([edge(original=a),edge(original=b,
            item=source(data=reading(sid="x")))])
        # Two independent review packets share article path but not ID.
        rows=r85.citation_changes([review(a,None),review(b,None,sid="x")],ix)
        self.assertEqual(len(rows),2)


URL_DRIFTS = tuple(
    "https://example.org/" + x for x in (
        "b", "A", "a?x=1", "a#frag", "a/", "a%2f", "a%2F",
        "a?c=2", "a?c=3", "a?x=a", "a%20b", "a%2e",
        "a/../b", "a/./b", "a?q=abc", "a?q=ABC",
        "a#section-2", "a#section-3", "a?q=%20",
        "a?q=%2F", "a?ref=archive", "a?ref=RC"))


class URLDriftAdversarialMatrix(unittest.TestCase):
    pass


def url_case(url):
    def test(self):
        histories=r85.source_histories([
            source("current"),source("rc",data=reading(url))],[])
        h=histories[0]
        self.assertIn("EXACT_LITERAL_URL_CHANGED_REVIEW",
                      h["current_TO_rc_review_cues_NOT_VERDICTS"])
        self.assertEqual(h[
            "four_complete_original_source_snapshots_UNABRIDGED_NOT_APPROVED"][
                "rc"]["url_observation"]["literal_URL_UNVERIFIED_UNCHANGED"],url)
        self.assertEqual(h["human_source_identity_review"],"NOT_REVIEWED")
    return test


for i,url in enumerate(URL_DRIFTS,1):
    setattr(URLDriftAdversarialMatrix,"test_literal_url_drift_%02d"%i,url_case(url))


META_DRIFTS = (
    ("title","different"), ("publisher","second"), ("kind","fictional"),
    ("supports","specific claim changed"), ("notes","new context"),
    ("published","2022-01-01"), ("updated","2023-01-01"),
    ("reviewed","2024-01-01"), ("verified_on",None),
    ("research_note","has caveat"), ("work","different book"),
    ("chapter","XIV"), ("volume","III"), ("edition","special"),
    ("accessed","2026-11-02"), ("abstract","changed abstract"),
    ("date","2010-04-02"), ("rights","public domain claimed"))


class ReadingDriftAdversarialMatrix(unittest.TestCase):
    pass


def metadata_case(key,value):
    def test(self):
        histories=r85.source_histories([
            source("current"),source("rc",data=reading(**{key:value}))],[])
        cues=histories[0]["current_TO_rc_review_cues_NOT_VERDICTS"]
        self.assertIn("COMPLETE_SOURCE_READING_CHANGED_REVIEW",cues)
        self.assertNotIn("EXACT_LITERAL_URL_CHANGED_REVIEW",cues)
        self.assertFalse(histories[0]["may_publish"])
    return test


for i,(key,value) in enumerate(META_DRIFTS,1):
    setattr(ReadingDriftAdversarialMatrix,"test_source_metadata_drift_%02d"%i,
            metadata_case(key,value))


class LiveFourStageCustody(unittest.TestCase):
    def test_full_live_sealed_seven_cluster_source_impact(self):
        # Requires all exact pinned historical Git objects on hosted checkout.
        r83,r82=r84.parent_modules()
        p82=r82.live_report()
        p83=r83.construct(p82)
        p84=r84.construct(p82,p83)
        report=r85.construct(p82,p83,p84)
        self.assertEqual(report["counts"]["four_stage_source_readings"],
                         p84["counts"]["source_reading_snapshots"])
        self.assertEqual(report["counts"]["four_stage_citation_occurrences"],
                         p84["counts"]["complete_citation_source_crosswalk_rows"])
        self.assertEqual(report["counts"]["exact_citation_to_source_variant_edges"],
                         p84["counts"]["citation_edges_to_known_scoped_variants"])
        self.assertEqual(report["counts"]["current_TO_rc_citation_rank_rows"],
                         p83["counts"]["current_rc_review_occurrence_rows"])
        self.assertEqual(report["human_source_approvals"],0)
        self.assertEqual(report["independent_QD_approvals"],0)
        self.assertFalse(report["may_publish"])
        self.assertEqual(report["sha256_seal"],r85.digest({
            k:v for k,v in report.items() if k!="sha256_seal"}))


if __name__=="__main__":
    unittest.main()
