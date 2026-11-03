"""R84 PRIVATE HOLD: synthetic/adversarial URL and exact source citation custody."""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "r84_source_url_citation_edge_custody.py"
SPEC = importlib.util.spec_from_file_location("r84_under_test", TOOL)
r84 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r84)
r83, r82 = r84.parent_modules()


def source(sid="s", url="https://example.org/a", extra=None):
    return {"id": sid, "url": url, "kind": "government", "publisher": "synthetic",
            "human_link_check": False, **(extra or {})}


def fragment(origin="water", stage="rc", records=None):
    raw = json.dumps({"sources": records if records is not None
                      else [source()]}, ensure_ascii=False).encode("utf-8")
    return r82.fragment(raw, origin, stage)


def fixture_index(origins=("water",), stage="rc", url=None):
    fragments = [fragment(origin, stage, [source(url=url or
                 "https://example.org/one")]) for origin in origins]
    return r84.catalog(fragments)


def anchor(sid="s", variants=None, scope=None, visible=True, text="Claim {{cite:s}}"):
    variants = [] if variants is None else variants
    scope = scope or ("OUTSIDE_SEVEN_FRAGMENT_SCOPE" if not variants
                     else "MULTIPLE_ORIGIN_VARIANTS_UNRESOLVED"
                     if len(variants) > 1 else "ONE_SCOPED_CANDIDATE_NOT_CLAIM_PROOF")
    return {"ordinal": 0, "raw_source_id": sid,
            "source_candidates_NOT_ALIASED": variants, "source_scope_state": scope,
            "scope_state": ("VISIBLE_CONTAINER_NOT_SUPPORT_PROOF" if visible
                            else "UNMAPPED_OR_NONVISIBLE_REVIEW"),
            "complete_container_text_UNABRIDGED": text}


def variant(row):
    return {"origin": row["origin"], "literal_source_id": row["literal_source_ID"],
            "reading_sha256": row["reading_sha256"]}


class URLObservations(unittest.TestCase):
    def test_literal_preservation(self):
        url = "HTTPS://Example.ORG/Case?A=1#Part"
        obs = r84.url_observation(url)
        self.assertEqual(obs["literal_URL_UNVERIFIED_UNCHANGED"], url)
        self.assertEqual(obs["human_link_review"], "NOT_REVIEWED")
        self.assertFalse(obs["may_publish"])

    def test_never_links_out_or_marks_verified(self):
        obs = r84.url_observation("https://example.com/?credential=no")
        self.assertNotIn("HTTP_status", str(obs))
        self.assertNotIn("verified_on", str(obs))
        self.assertEqual(obs["human_link_review"], "NOT_REVIEWED")

    def test_reject_non_string(self):
        for url in (None, 123, [], {}):
            with self.subTest(url=url), self.assertRaises(r84.Hold):
                r84.url_observation(url)

    def test_url_split_preserves_query_and_fragment(self):
        obs = r84.url_observation("https://example.org/a?x=1#chapter")
        self.assertEqual(obs["parsed_observation_NOT_LINK_CHECK"]["query"], "x=1")
        self.assertEqual(obs["parsed_observation_NOT_LINK_CHECK"]["fragment"], "chapter")

    def test_only_review_flags_are_generated(self):
        for url in ("https://example.org", "http://example.org",
                    "https://user:pass@example.org", "ftp://example.org"):
            self.assertTrue(all(x.endswith("_REVIEW") for x in
                                r84.url_observation(url)["review_cues_NOT_VERDICTS"]))


class SourceCatalog(unittest.TestCase):
    def test_catalog_preserves_complete_reading(self):
        original = source(extra={"supports": "A" * 6000, "notes": "Human check pending"})
        rows, index, collisions = r84.catalog([fragment(records=[original])])
        self.assertEqual(rows[0]["complete_original_reading_UNABRIDGED_NOT_APPROVED"],
                         original)
        self.assertIn("A" * 6000, str(rows[0]))
        self.assertEqual(len(index), 1)
        self.assertEqual(collisions, [])

    def test_exact_repeated_URL_does_not_merge_sources(self):
        a, index, groups = fixture_index(("a", "b"))
        self.assertEqual(len(a), 2)
        self.assertEqual(len(index), 2)
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0]["distinct_origin_scoped_readings_NOT_MERGED"]), 2)
        self.assertFalse(groups[0]["may_publish"])

    def test_case_variant_URL_not_alias(self):
        rows, _, groups = r84.catalog([fragment("a", records=[source("a",
             "https://Example.org/x"), source("b", "https://example.org/x")])])
        self.assertEqual(len(rows), 2)
        self.assertEqual(groups, [])

    def test_source_ID_same_across_stages_preserved(self):
        rows, idx, groups = r84.catalog(
            [fragment("x", "frozen"), fragment("x", "rc")])
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(idx), 2)
        self.assertEqual(groups, [])

    def test_same_ID_different_origins_no_alias(self):
        rows, idx, _ = fixture_index(("water", "food", "shelter"))
        self.assertEqual(len({r["origin"] for r in rows}), 3)
        self.assertEqual(len(idx), 3)

    def test_differing_URLs_on_same_origin_ID_stages_preserved(self):
        rows, _, groups = r84.catalog([fragment("water", "frozen",
            [source(url="https://example.org/old")]),
            fragment("water", "rc", [source(url="https://example.org/new")])])
        self.assertEqual([r["url_observation"]["literal_URL_UNVERIFIED_UNCHANGED"]
                          for r in rows],
                         ["https://example.org/old", "https://example.org/new"])
        self.assertEqual(groups, [])

    def test_cannot_reuse_exact_origin_id_in_stage(self):
        with self.assertRaises(r84.Hold):
            r84.catalog([fragment("x"), fragment("x")])

    def test_source_reading_sha_is_checked(self):
        altered = fragment()
        altered["source_readings_UNABRIDGED"][0]["reading_sha256"] = "a" * 64
        with self.assertRaises(r84.Hold):
            r84.catalog([altered])

    def test_source_record_id_cannot_be_reidentified(self):
        altered = fragment()
        altered["source_readings_UNABRIDGED"][0][
            "complete_reading_UNABRIDGED_NOT_APPROVED"]["id"] = "other"
        with self.assertRaises(r84.Hold):
            r84.catalog([altered])

    def test_missing_url_refused_not_guessed(self):
        with self.assertRaises(r84.Hold):
            r84.catalog([fragment(records=[{"id": "s", "kind": "nonprofit"}])])

    def test_no_source_human_approval(self):
        rows, _, _ = fixture_index()
        self.assertTrue(all(x["human_source_review"] == "NOT_REVIEWED"
                            and x["qualified_safety_review"] == "NOT_REVIEWED"
                            and not x["may_publish"] for x in rows))


class CitationCrosswalk(unittest.TestCase):
    def setUp(self):
        self.rows, self.index, _ = fixture_index(("water",))
        self.candidate = variant(self.rows[0])

    def get(self, obj):
        return r84.citation_edge(obj, self.index, "rc", "water",
                                 "preparedness/content/articles/a.body.html")

    def test_exact_record_link_not_source_approval(self):
        edge = self.get(anchor(variants=[self.candidate]))
        self.assertEqual(len(edge["exact_source_edges_NOT_LINK_OR_CLAIM_APPROVED"]), 1)
        self.assertEqual(edge["human_claim_support"], "NOT_REVIEWED")
        self.assertEqual(edge["qualified_safety_review"], "NOT_REVIEWED")
        self.assertFalse(edge["may_publish"])

    def test_url_is_literal_not_rewritten(self):
        edge = self.get(anchor(variants=[self.candidate]))
        self.assertEqual(edge["exact_source_edges_NOT_LINK_OR_CLAIM_APPROVED"][0]
                         ["literal_URL_UNVERIFIED_UNCHANGED"],
                         "https://example.org/one")

    def test_missing_candidate_is_explicit_unknown(self):
        edge = self.get(anchor())
        self.assertEqual(edge["exact_source_edges_NOT_LINK_OR_CLAIM_APPROVED"], [])
        self.assertIn("OUTSIDE_SEVEN_FRAGMENT_SCOPE_REVIEW",
                      edge["review_cues_NOT_VERDICTS"])

    def test_no_silent_candidate_drop(self):
        with self.assertRaises(r84.Hold):
            self.get(anchor(variants=[self.candidate],
                            scope="OUTSIDE_SEVEN_FRAGMENT_SCOPE"))

    def test_no_guessed_candidate_from_matching_id(self):
        edge = self.get(anchor(sid="s"))
        self.assertEqual(edge["source_scope_state"], "OUTSIDE_SEVEN_FRAGMENT_SCOPE")
        self.assertFalse(edge["exact_source_edges_NOT_LINK_OR_CLAIM_APPROVED"])

    def test_candidate_missing_from_original_fails(self):
        bad = {**self.candidate, "reading_sha256": "1" * 64}
        with self.assertRaises(r84.Hold):
            self.get(anchor(variants=[bad]))

    def test_different_literal_source_id_fails(self):
        bad = {**self.candidate, "literal_source_id": "other"}
        with self.assertRaises(r84.Hold):
            self.get(anchor(variants=[bad]))

    def test_repeated_candidate_not_merged(self):
        with self.assertRaises(r84.Hold):
            self.get(anchor(variants=[self.candidate, self.candidate]))

    def test_multi_origin_citations_unresolved(self):
        rows, index, _ = fixture_index(("water", "food"))
        obj = anchor(variants=[variant(row) for row in rows])
        edge = r84.citation_edge(obj, index, "rc", "water", "a")
        self.assertEqual(len(edge["exact_source_edges_NOT_LINK_OR_CLAIM_APPROVED"]), 2)
        self.assertIn("MULTIPLE_SOURCE_VARIANTS_REVIEW",
                      edge["review_cues_NOT_VERDICTS"])

    def test_multi_origin_must_not_be_deemed_single(self):
        rows, index, _ = fixture_index(("water", "food"))
        obj = anchor(variants=[variant(row) for row in rows],
                     scope="ONE_SCOPED_CANDIDATE_NOT_CLAIM_PROOF")
        with self.assertRaises(r84.Hold):
            r84.citation_edge(obj, index, "rc", "water", "a")

    def test_wrong_stage_fails(self):
        with self.assertRaises(r84.Hold):
            r84.citation_edge(anchor(variants=[self.candidate]), self.index,
                              "frozen", "water", "a")

    def test_unmapped_citation_is_reviewed(self):
        edge = self.get(anchor(variants=[self.candidate], visible=False))
        self.assertIn("NONVISIBLE_OR_UNMAPPED_CITATION_REVIEW",
                      edge["review_cues_NOT_VERDICTS"])

    def test_original_context_digest_changes_on_claim_edit(self):
        left = self.get(anchor(variants=[self.candidate], text="Never drink it {{cite:s}}"))
        right = self.get(anchor(variants=[self.candidate], text="Drink it {{cite:s}}"))
        self.assertNotEqual(left["R83_complete_anchor_sha256"],
                            right["R83_complete_anchor_sha256"])
        self.assertNotEqual(left["R83_complete_container_text_sha256"],
                            right["R83_complete_container_text_sha256"])

    def test_absent_context_is_null_not_false_claim(self):
        obj = anchor(variants=[self.candidate])
        obj["complete_container_text_UNABRIDGED"] = None
        edge = self.get(obj)
        self.assertIsNone(edge["R83_complete_container_text_sha256"])

    def test_provenance_digest_does_not_mean_safe(self):
        obj = anchor(variants=[self.candidate])
        edge = self.get(obj)
        self.assertEqual(len(edge["R83_complete_anchor_sha256"]), 64)
        self.assertNotIn("SAFE", edge["human_claim_support"])

    def test_odd_url_flags_travel_to_downstream_citation(self):
        rows, index, _ = fixture_index(("water",), url="http://127.0.0.1/a")
        obj = anchor(variants=[variant(rows[0])])
        edge = r84.citation_edge(obj, index, "rc", "water", "a")
        self.assertIn("NOT_LITERAL_HTTPS_REVIEW", edge["review_cues_NOT_VERDICTS"])
        self.assertIn("NON_GLOBAL_IP_HOST_REVIEW", edge["review_cues_NOT_VERDICTS"])


# Each distinct URL edge case exercises a specific parsing or review boundary.
# No network, content mutation, CMS calls, or writes to a shared working tree.
URL_CASES = (
    ("http://example.org", "NOT_LITERAL_HTTPS_REVIEW"),
    ("ftp://example.org", "NOT_LITERAL_HTTPS_REVIEW"),
    ("mailto:someone@example.org", "NO_PARSEABLE_AUTHORITY_REVIEW"),
    ("//example.org", "NOT_LITERAL_HTTPS_REVIEW"),
    ("https:///a", "NO_PARSEABLE_AUTHORITY_REVIEW"),
    ("", "EMPTY_SPACE_OR_CONTROL_REVIEW"),
    ("https://user@example.org", "AUTHORITY_USERINFO_REVIEW"),
    ("https://user:p@example.org", "AUTHORITY_USERINFO_REVIEW"),
    ("https://u@v@example.org", "MULTIPLE_USERINFO_DELIMITERS_REVIEW"),
    ("https://ex%61mple.org", "ENCODED_AUTHORITY_REVIEW"),
    ("https://example.org:8443", "EXPLICIT_PORT_REVIEW"),
    ("https://example.org:wat", "INVALID_PORT_REVIEW"),
    ("https://example.org:99999", "INVALID_PORT_REVIEW"),
    ("https://example.org.", "HOST_TRAILING_DOT_REVIEW"),
    ("https://127.0.0.1/x", "IP_ADDRESS_HOST_REVIEW"),
    ("https://192.168.1.1", "NON_GLOBAL_IP_HOST_REVIEW"),
    ("https://10.0.0.1", "NON_GLOBAL_IP_HOST_REVIEW"),
    ("https://[::1]/x", "NON_GLOBAL_IP_HOST_REVIEW"),
    ("https://localhost/x", "LOCAL_HOSTNAME_REVIEW"),
    ("https://server.local/x", "LOCAL_HOSTNAME_REVIEW"),
    ("https://server.internal/x", "LOCAL_HOSTNAME_REVIEW"),
    ("https://example.org/a#footnote", "URL_FRAGMENT_REVIEW"),
    ("https://example.org?q=value", "URL_QUERY_REVIEW"),
    ("https://example.org/a?x=1#f", "URL_QUERY_REVIEW"),
    ("https://example.org/a/../b", "DOT_SEGMENT_PATH_REVIEW"),
    ("https://example.org/a/./b", "DOT_SEGMENT_PATH_REVIEW"),
    ("https://example.org/a%2", "MALFORMED_PERCENT_ESCAPE_REVIEW"),
    ("https://example.org/%GG", "MALFORMED_PERCENT_ESCAPE_REVIEW"),
    ("https://example.org/path%", "MALFORMED_PERCENT_ESCAPE_REVIEW"),
    ("https://example.org\\@evil.test", "BACKSLASH_REVIEW"),
    ("https://example.org/a b", "EMPTY_SPACE_OR_CONTROL_REVIEW"),
    ("https://example.org/a\nb", "EMPTY_SPACE_OR_CONTROL_REVIEW"),
    ("https://example.org/a\tb", "EMPTY_SPACE_OR_CONTROL_REVIEW"),
    ("https://example.org/naïve", "NONASCII_LITERAL_REVIEW"),
    ("https://例子.测试/x", "NONASCII_LITERAL_REVIEW"),
    ("https://[bad-host", "UNPARSEABLE_URL_REVIEW"),
    ("https://[::1", "UNPARSEABLE_URL_REVIEW"),
    ("HTTPS://example.org/x", "NOT_LITERAL_HTTPS_REVIEW"),
    ("https://example.org:443/x", "EXPLICIT_PORT_REVIEW"),
    ("https://8.8.8.8/a", "IP_ADDRESS_HOST_REVIEW"),
    ("https://[2001:db8::1]/x", "NON_GLOBAL_IP_HOST_REVIEW"),
)


class URLAdversarialMatrix(unittest.TestCase):
    pass


def case(url, expected):
    def test(self):
        data = r84.url_observation(url)
        self.assertIn(expected, data["review_cues_NOT_VERDICTS"])
        self.assertEqual(data["literal_URL_UNVERIFIED_UNCHANGED"], url)
        self.assertFalse(data["may_publish"])
    return test


for i, (url, flag) in enumerate(URL_CASES, 1):
    setattr(URLAdversarialMatrix, "test_url_observation_%02d" % i,
            case(url, flag))


class LiveEvidenceReconstruction(unittest.TestCase):
    def test_full_seven_contributor_four_stage_crosswalk(self):
        # Exact git SHA reconstruction requires real checkout history; CI has it.
        r82_report = r82.live_report()
        r83_report = r83.construct(r82_report)
        report = r84.construct(r82_report, r83_report)
        self.assertEqual(report["counts"]["complete_citation_source_crosswalk_rows"],
                         r83_report["counts"]["four_stage_citation_anchors"])
        self.assertEqual(report["counts"]["source_reading_snapshots"], sum(
            f["source_count"] for f in r82_report[
                "all_four_snapshot_source_fragments_UNABRIDGED"]))
        self.assertEqual(report["R82_unabridged_provenance_sha256"],
                         r82_report["sha256_seal"])
        self.assertEqual(report["R83_unabridged_citation_context_sha256"],
                         r83_report["sha256_seal"])
        self.assertEqual(report["human_source_approvals"], 0)
        self.assertEqual(report["qualified_safety_approvals"], 0)
        self.assertFalse(report["may_publish"])
        self.assertEqual(report["sha256_seal"], r84.sha(r84.canonical({
            k: v for k, v in report.items() if k != "sha256_seal"})))


if __name__ == "__main__":
    unittest.main()
