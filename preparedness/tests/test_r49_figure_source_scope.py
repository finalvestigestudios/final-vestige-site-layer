#!/usr/bin/env python3
"""R49 independent synthetic/offline source-scope and numeric-triage tests."""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import unittest

SRC = Path(__file__).resolve().parents[1] / "tools/figure_source_scope_triage_gate.py"
spec = importlib.util.spec_from_file_location("r49_figure_source_scope", SRC)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

URL = "https://example.org/original-source"
class FakeLibrary:
    def __init__(self, body="<p>Store 1 gallon of water per person {{cite:a}}.</p>"):
        self.articles = {"sample": {"slug": "sample", "track": "modern",
                                    "kind": "article", "_body": body,
                                    "safety_review": {"state": "pending"}}}
        self.slate = {"sample": {"gate": True}}
        self.sources = {"a": {"id": "a", "url": URL,
                              "_origin": "original-cluster",
                              "notes": "Original limited reading scope."}}
    def source_for(self, meta, sid):
        return self.sources[sid]

def sample():
    lib = FakeLibrary()
    fig = gate.extract_original_claims(lib)
    assert len(fig) == 1, fig
    fig[0].update(status="ALL_FIGURES_FOUND", missing=[],
                  tested_sources=["a"], untested_sources=[])
    acc = [{"url": URL, "ok": True, "kind": "html", "sha256": "e"*64}]
    return lib, fig, acc

def run(lib, figures, access, expected=None):
    if expected is None:
        expected = (len(figures), len(access), sum(r.get("ok") is True for r in access),
                    sum(r.get("ok") is False for r in access))
    return gate.audit(lib, figures, access, expected=expected)

class ValidEvidence(unittest.TestCase):
    def test_original_evidence_retained_no_human_approval(self):
        lib, figures, access = sample()
        r = run(lib, figures, access)
        self.assertEqual(r["release_state"], "HOLD")
        self.assertFalse(r["may_publish"])
        self.assertFalse(r["qualified_safety_clearance"])
        self.assertFalse(r["human_source_links_verified"])
        self.assertFalse(r["source_claim_accuracy_verified"])
        self.assertEqual(len(r["review_tasks"]), 1)
        self.assertEqual(r["review_tasks"][0]["state"], gate.HOLD)

    def test_all_figures_found_does_not_count_as_proven(self):
        lib, figures, access = sample()
        r = run(lib, figures, access)
        self.assertIn("NUMBER_TOKEN_IS_NOT_CLAIM_OR_UNIT_VERIFICATION",
                      r["review_tasks"][0]["review_flags"])
        self.assertFalse(r["review_tasks"][0]["source_claim_accuracy_verified"])

    def test_original_source_variant_and_note_sha_retained(self):
        lib, figures, access = sample()
        r = run(lib, figures, access)
        s = r["review_tasks"][0]["original_source_variants"][0]
        self.assertEqual(s["article_source_origin"], "original-cluster")
        self.assertEqual(s["original_source_record_sha256"], gate.digest(lib.sources["a"]))
        self.assertEqual(s["original_url"], URL)

    def test_read_only_deterministic(self):
        lib, figures, access = sample()
        before = copy.deepcopy((figures, access, lib.articles, lib.sources))
        a = run(lib, figures, access); b = run(lib, figures, access)
        self.assertEqual(a, b)
        self.assertEqual((figures, access, lib.articles, lib.sources), before)
        self.assertEqual(a["fingerprint_sha256"],
                         gate.digest({k: v for k, v in a.items() if k != "fingerprint_sha256"}))

    def test_same_url_two_original_source_records_not_collapsed(self):
        lib = FakeLibrary("<p>Store 1 gallon of water {{cite:a}}{{cite:b}}.</p>")
        lib.sources["b"] = {"id": "b", "url": URL, "_origin": "different-cluster",
                            "notes": "Different original reading depth."}
        fig = gate.extract_original_claims(lib)
        fig[0].update(status="ALL_FIGURES_FOUND", missing=[],
                      tested_sources=["a", "b"], untested_sources=[])
        result = run(lib, fig, [{"url": URL, "ok": True,
                                 "kind": "html", "sha256": "b"*64}])
        row = result["review_tasks"][0]
        self.assertEqual(len(row["original_source_variants"]), 2)
        self.assertNotEqual(row["original_source_variants"][0]["original_source_record_sha256"],
                            row["original_source_variants"][1]["original_source_record_sha256"])
        self.assertIn("MULTIPLE_CITED_SOURCES_NEED_INDIVIDUAL_ATTRIBUTION",
                      row["review_flags"])

    def test_duplicate_citation_occurrences_remain_visible(self):
        lib = FakeLibrary("<p>Keep 1 gallon of water {{cite:a}} per person {{cite:a}}.</p>")
        fig = gate.extract_original_claims(lib)
        fig[0].update(status="ALL_FIGURES_FOUND", missing=[],
                      tested_sources=["a", "a"], untested_sources=[])
        r = run(lib, fig, [{"url": URL, "ok": True, "kind": "html"}])
        self.assertEqual(r["counts"]["original_citation_occurrences_in_numeric_blocks"], 2)
        self.assertEqual(len(r["review_tasks"][0]["original_source_variants"]), 2)

    def test_blocked_source_stays_unverified(self):
        lib, fig, acc = sample()
        acc[0] = {"url": URL, "ok": False, "status": 403, "error": "HTTP 403"}
        fig[0].update(status="NO_TESTABLE_SOURCE", missing=[],
                      tested_sources=[], untested_sources=["a"])
        r = run(lib, fig, acc)
        self.assertEqual(r["counts"]["unavailable_source_urls"], 1)
        self.assertIn("AT_LEAST_ONE_CITED_SOURCE_INACCESSIBLE",
                      r["review_tasks"][0]["review_flags"])

    def test_accessible_browser_text_without_hash_stays_unpinned(self):
        lib, fig, acc = sample()
        del acc[0]["sha256"]
        r = run(lib, fig, acc)
        self.assertIn("ACCESSIBLE_EXTRACT_WITHOUT_RECORDED_CONTENT_SHA256",
                      r["review_tasks"][0]["review_flags"])
        self.assertFalse(r["human_source_reviews_completed"])

    def test_numeric_mismatch_is_a_review_task_not_automatic_contradiction(self):
        lib, fig, acc = sample()
        fig[0].update(status="NO_FIGURES_FOUND", missing=["1 gallon"])
        r = run(lib, fig, acc)
        self.assertIn("NUMBER_TOKEN_NOT_LOCATED_NOT_NECESSARILY_CONTRADICTED",
                      r["review_tasks"][0]["review_flags"])

    def test_non_actionable_historical_track_not_mislabeled_safe(self):
        lib, fig, acc = sample()
        lib.articles["sample"]["track"] = "lost-ways"
        fig[0]["track"] = "lost-ways"
        r = run(lib, fig, acc)
        self.assertFalse(r["qualified_safety_clearance"])

    def test_original_raw_article_change_requires_retriage(self):
        lib, fig, acc = sample()
        lib.articles["sample"]["_body"] = lib.articles["sample"]["_body"].replace("1 gallon", "2 gallons")
        with self.assertRaises(gate.TriageHold):
            run(lib, fig, acc)

    def test_all_original_figure_rows_extracted(self):
        lib = FakeLibrary("<p>Use 1 gallon {{cite:a}}.</p><p>Wait 20 seconds {{cite:a}}.</p>")
        rows = gate.extract_original_claims(lib)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["figs"], ["1 gallon"])
        self.assertEqual(rows[1]["figs"], ["20 seconds"])

# Independent adversarial cases, each discoverable by unittest and counting
# as a separate native regression (not a combined subTest). They mutate only
# synthetic data. No temporary files, network, symlinks or working-tree writes.
def mutate_fig(field, value):
    def fn(lib, figures, access, expected):
        figures[0][field] = value
    return fn

def mutate_access(field, value):
    def fn(lib, figures, access, expected):
        access[0][field] = value
    return fn

def omit_fig(field):
    def fn(lib, figures, access, expected):
        figures[0].pop(field, None)
    return fn

def omit_access(field):
    def fn(lib, figures, access, expected):
        access[0].pop(field, None)
    return fn

def changed_source(lib, figures, access, expected):
    lib.sources["a"]["url"] = "https://example.org/not-original"
def removed_source(lib, figures, access, expected):
    lib.sources.clear()
def removed_source_url(lib, figures, access, expected):
    lib.sources["a"].pop("url")
def changed_html(lib, figures, access, expected):
    lib.articles["sample"]["_body"] = "<p>Fake 9 gallons {{cite:a}}.</p>"
def changed_slug(lib, figures, access, expected):
    lib.articles["sample"]["slug"] = "another"
def duplicate_access(lib, figures, access, expected):
    access.append(copy.deepcopy(access[0]))
def no_access(lib, figures, access, expected):
    access.clear()
def no_figures(lib, figures, access, expected):
    figures.clear()
def wrong_expected(lib, figures, access, expected):
    expected[:] = [1, 2, 1, 1]
def invalid_expected(lib, figures, access, expected):
    expected[:] = [1, -1, 1, 0]
def changed_error_without_reason(lib, figures, access, expected):
    access[0] = {"url": URL, "ok": False}
def testable_wrong_access(lib, figures, access, expected):
    access[0] = {"url": URL, "ok": False, "error": "HTTP 403"}
def spoofed_source_id(lib, figures, access, expected):
    figures[0]["cites"] = ["fake"]
def repeated_source_id(lib, figures, access, expected):
    figures[0]["cites"] = ["a", "a"]
def extra_tested_source(lib, figures, access, expected):
    figures[0]["tested_sources"] = ["a", "a"]
def extra_untested_source(lib, figures, access, expected):
    figures[0]["untested_sources"] = ["a"]
def missing_tested_source(lib, figures, access, expected):
    figures[0]["tested_sources"] = []
def reported_blocked_as_tested(lib, figures, access, expected):
    access[0] = {"url": URL, "ok": False, "error": "HTTP 403"}
    figures[0]["untested_sources"] = ["a"]
def duplicate_figs(lib, figures, access, expected):
    figures[0]["figs"] = ["1 gallon", "1 gallon"]
def duplicate_missing(lib, figures, access, expected):
    figures[0]["missing"] = ["1 gallon", "1 gallon"]
def missing_unknown_token(lib, figures, access, expected):
    figures[0]["missing"] = ["40 gallons"]
def no_figs_list(lib, figures, access, expected):
    figures[0]["figs"] = []
def no_cites_list(lib, figures, access, expected):
    figures[0]["cites"] = []
def invalid_urls_list(lib, figures, access, expected):
    access[0]["url"] = "javascript:evil()"
def unexpected_kind(lib, figures, access, expected):
    access[0]["kind"] = "pdf"
def status_all_but_missing(lib, figures, access, expected):
    figures[0]["missing"] = ["1 gallon"]
def status_some_but_none_missing(lib, figures, access, expected):
    figures[0]["status"] = "SOME_FIGURES_NOT_FOUND"
def status_none_but_none_missing(lib, figures, access, expected):
    figures[0]["status"] = "NO_FIGURES_FOUND"
def status_no_source_when_source_tested(lib, figures, access, expected):
    figures[0]["status"] = "NO_TESTABLE_SOURCE"
def numeric_error_status(lib, figures, access, expected):
    figures[0]["status"] = 123
def status_unknown(lib, figures, access, expected):
    figures[0]["status"] = "HUMAN_VERIFIED"
def invalid_track(lib, figures, access, expected):
    figures[0]["track"] = "approved"
def altered_context(lib, figures, access, expected):
    figures[0]["text"] = figures[0]["text"].replace("1 gallon", "2 gallons")
def changed_source_digest(lib, figures, access, expected):
    figures[0]["figs"] = ["1 liter"]
def missing_claim_ref(lib, figures, access, expected):
    figures[0].pop("cites")
def source_boolean_is_string(lib, figures, access, expected):
    access[0]["ok"] = "true"
def source_boolean_is_number(lib, figures, access, expected):
    access[0]["ok"] = 1
def switch_source_article_origin(lib, figures, access, expected):
    figures[0]["slug"] = "other"
def remove_article(lib, figures, access, expected):
    lib.articles.clear()
def unsafe_missing_access_url(lib, figures, access, expected):
    access[0]["url"] = "http://example.org/original-source"
def access_reason_missing(lib, figures, access, expected):
    access[0].pop("ok")
def unknown_extra_access(lib, figures, access, expected):
    access.append({"url":"https://example.org/not-cited","ok":True,"kind":"html"})
def invalid_figure_type(lib, figures, access, expected):
    figures[0]["figs"] = ["1 gallon", 5]
def status_nonlist_figs(lib, figures, access, expected):
    figures[0]["figs"] = "1 gallon"
def invalid_tested_type(lib, figures, access, expected):
    figures[0]["tested_sources"] = "a"
def invalid_missing_type(lib, figures, access, expected):
    figures[0]["missing"] = "1 gallon"
def invalid_untested_type(lib, figures, access, expected):
    figures[0]["untested_sources"] = "a"
def invalid_source_record(lib, figures, access, expected):
    lib.sources["a"] = None

BAD_CASES = {
    "orphan_article_slug": mutate_fig("slug", "not-in-archive"),
    "invented_track": invalid_track,
    "changed_claim_context": altered_context,
    "changed_quantified_measure": changed_source_digest,
    "lost_original_citation": omit_fig("cites"),
    "unknown_source_identifier": spoofed_source_id,
    "duplicate_original_citation": repeated_source_id,
    "status_claims_human_approval": status_unknown,
    "status_not_text": numeric_error_status,
    "missing_figure_array": omit_fig("figs"),
    "missing_missing_tokens_array": omit_fig("missing"),
    "missing_tested_sources_array": omit_fig("tested_sources"),
    "missing_untested_sources_array": omit_fig("untested_sources"),
    "figures_nonlist": status_nonlist_figs,
    "figures_empty": no_figs_list,
    "citation_occurrences_empty": no_cites_list,
    "figure_census_duplicate": duplicate_figs,
    "missing_figure_census_duplicate": duplicate_missing,
    "missing_nonexistent_figure": missing_unknown_token,
    "all_found_but_missing": status_all_but_missing,
    "some_missing_but_none": status_some_but_none_missing,
    "none_found_but_missing_empty": status_none_but_none_missing,
    "no_testable_source_when_available": status_no_source_when_source_tested,
    "tested_source_omitted": missing_tested_source,
    "tested_source_repeated": extra_tested_source,
    "untested_source_forged": extra_untested_source,
    "source_blocked_but_reported_tested": testable_wrong_access,
    "source_record_url_changes": changed_source,
    "source_record_disappears": removed_source,
    "source_record_loses_url": removed_source_url,
    "original_article_body_changes": changed_html,
    "original_article_slug_changes": changed_slug,
    "duplicate_url_record": duplicate_access,
    "source_accessibility_disappears": no_access,
    "figure_list_disappears": no_figures,
    "invalid_expected_counts": invalid_expected,
    "unexpected_expected_counts": wrong_expected,
    "source_block_without_failure_reason": changed_error_without_reason,
    "url_is_not_https": invalid_urls_list,
    "unexpected_pdf_kind": unexpected_kind,
    "url_becomes_http": unsafe_missing_access_url,
    "accessibility_status_removed": access_reason_missing,
    "unbound_url_added": unknown_extra_access,
    "figure_nonstring": invalid_figure_type,
    "tested_sources_not_list": invalid_tested_type,
    "missing_tokens_not_list": invalid_missing_type,
    "untested_sources_not_list": invalid_untested_type,
    "source_ok_string_spoof": source_boolean_is_string,
    "source_ok_number_spoof": source_boolean_is_number,
    "source_id_article_mismatch": switch_source_article_origin,
    "article_missing": remove_article,
    "source_record_none": invalid_source_record,
}
class RejectedSyntheticEvidence(unittest.TestCase):
    pass

def make_case(name, fn):
    def test(self):
        lib, figs, access = sample()
        expected = [1, 1, 1, 0]
        fn(lib, figs, access, expected)
        with self.assertRaises((gate.TriageHold, KeyError, TypeError, ValueError)):
            gate.audit(lib, figs, access, expected=tuple(expected))
    test.__name__ = "test_reject_" + name
    return test

for name, fn in BAD_CASES.items():
    setattr(RejectedSyntheticEvidence, "test_reject_" + name, make_case(name, fn))

if __name__ == "__main__":
    unittest.main()
