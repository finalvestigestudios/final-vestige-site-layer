#!/usr/bin/env python3
"""R50 offline synthetic adversity plus real original-corpus safety register gate."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parents[1]
P = HERE / "tools/safety_exception_custody_gate.py"
spec = importlib.util.spec_from_file_location("r50_safety_exception_gate", P)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

class SyntheticLibrary:
    def __init__(self):
        self.articles = {"sample": {
            "slug": "sample", "track": "modern",
            "_body": "<p>Only private original evidence; no human safety verdict.</p>"}}
        self.source_variants = {}
        for name in ["sample-source"] + [f"blocked-{i:02d}" for i in range(1, 26)]:
            self.source_variants[name] = [{
                "id": name, "url": "https://example.org/" + name,
                "_origin": "synthetic", "notes": "distinct original reading scope"}]
        self.register = {k: v[0] for k, v in self.source_variants.items()}
    def source_for(self, meta, sid):
        if sid not in self.source_variants:
            raise KeyError(sid)
        return self.source_variants[sid][0]

def make_fixture():
    hold = "**No exception below is closed.** Every entry is " + chr(96) + "OPEN" + chr(96)
    lines = ["# Synthetic PRIVATE safety register", hold, "## Register",
             "| ID | Sev | Notes |", "|---|---|---|"]
    for sid, sev in gate.SEVERITIES.items():
        lines.append("| " + sid + " | " + sev + " | Needs qualified reviewer |")
    lines += ["## Appendix A: machine candidates", "| ID | Note |",
              "|---|---|"]
    for sid in sorted(gate.REVIEWABLE):
        lines.append("| " + sid + " | NOT human verified |")
    lines += ["## Appendix B: 25 source blockers", "| source id | result | URL |",
              "|---|---|---|"]
    for i in range(1, 26):
        sid = f"blocked-{i:02d}"
        tick = chr(96)
        lines.append("| " + tick + sid + tick +
                     " | failed machine access | https://example.org/" + sid + " |")
    items = []
    for sid in sorted(gate.IDS):
        placeholder = sid == "B09"
        items.append({
            "id": sid, "article": "sample",
            "file": "preparedness/content/articles/sample.body.html",
            "line": None if placeholder else 2,
            "section_anchor": "test",
            "note": "placeholder" if placeholder else "synthetic",
            "excerpt": None if placeholder else "Not independently verified.",
            "keys": ["test"], "status": "ALL_KEYS_FOUND_IN_CITED_SOURCES",
            "sources_with_hits": {"sample-source": ["test"]},
            "sources_not_in_corpus": [],
        })
    return SyntheticLibrary(), "\n".join(lines) + "\n", items, []

def audited(args=None):
    if args is None:
        args = make_fixture()
    return gate.audit(*args[:3], access=args[3])

class Positive(unittest.TestCase):
    def test_private_no_false_approval(self):
        r = audited()
        self.assertEqual(r["release_state"], "HOLD")
        self.assertFalse(r["may_publish"])
        self.assertFalse(r["qualified_safety_clearance"])
        self.assertFalse(r["human_source_links_verified"])
        self.assertFalse(r["independent_QD_approval"])
        self.assertFalse(r["claim_accuracy_verified"])

    def test_exact_candidate_census(self):
        r = audited()
        self.assertEqual(r["counts"]["open_incidents"], 15)
        self.assertEqual(r["counts"]["historically_blocked_sources"], 25)
        self.assertEqual(r["counts"]["reviewable_candidates"], 28)
        self.assertEqual(r["counts"]["placeholder_B09"], 1)
        self.assertEqual(len(r["candidate_workorders"]), 29)

    def test_open_incident_severities(self):
        r = audited()
        self.assertEqual([x["severity"] for x in r["open_incidents"]].count("HIGH"), 5)
        self.assertEqual([x["severity"] for x in r["open_incidents"]].count("MEDIUM"), 7)
        self.assertEqual([x["severity"] for x in r["open_incidents"]].count("LOW"), 3)

    def test_read_only_and_repeatable(self):
        args = make_fixture()
        before = copy.deepcopy((args[0].articles, args[0].source_variants,
                                args[0].register, args[1:]))
        a = audited(args)
        self.assertEqual(a, audited(args))
        self.assertEqual((args[0].articles, args[0].source_variants,
                          args[0].register, args[1:]), before)
        self.assertEqual(a["fingerprint_sha256"], gate.digest({
            k: v for k, v in a.items() if k != "fingerprint_sha256"}))

    def test_the_29th_row_is_unevaluated_placeholder(self):
        r = audited()
        row = next(x for x in r["candidate_workorders"] if x["candidate"] == "B09")
        self.assertTrue(row["unevaluated_placeholder"])
        self.assertFalse(row["in_r48_reviewed_appendix"])
        self.assertFalse(row["qualified_human_review_completed"])
        self.assertFalse(row["may_publish"])

    def test_keyword_found_is_not_claim_support(self):
        r = audited()
        one = r["candidate_workorders"][0]["source_records"][0]
        self.assertFalse(one["human_claim_support_verified"])
        self.assertGreater(one["extracted_keyword_hits_not_claim_support"], 0)

    def test_distinct_same_url_source_variants_remain_distinct(self):
        args = list(make_fixture())
        src = args[0].source_variants["sample-source"][0]
        args[0].source_variants["sample-source"].append(
            {**src, "_origin": "other-contributor",
             "notes": "Different original reading depth"})
        out = audited(args)
        record = out["candidate_workorders"][0]["source_records"][0]
        self.assertEqual(len(record["all_original_contributor_variants"]), 2)
        self.assertNotEqual(record["all_original_contributor_variants"][0]["original_source_sha256"],
                            record["all_original_contributor_variants"][1]["original_source_sha256"])

    def test_machine_accessibility_does_not_clear_blocker(self):
        args = list(make_fixture())
        args[3] = [{"url": "https://example.org/blocked-01", "ok": True}]
        r = audited(args)
        b = r["unresolved_source_access"][0]
        self.assertTrue(b["r48_machine_access_observations"][0]["ok"])
        self.assertFalse(b["human_link_check_complete"])
        self.assertEqual(b["review_state"], "HOLD")

    def test_original_source_record_hash_changes_on_variant_edit(self):
        a = list(make_fixture())
        b = copy.deepcopy(a)
        b[0].source_variants["sample-source"][0]["notes"] = "changed reading scope"
        self.assertNotEqual(audited(a)["fingerprint_sha256"],
                            audited(b)["fingerprint_sha256"])

class Negative(unittest.TestCase):
    def reject(self, args):
        with self.assertRaises(gate.SafetyHold):
            audited(args)

    def test_removing_hold_warning_is_rejected(self):
        a = list(make_fixture())
        a[1] = a[1].replace("**No exception below is closed.**", "")
        self.reject(a)

    def test_claiming_incidents_not_open_is_rejected(self):
        a = list(make_fixture())
        a[1] = a[1].replace("Every entry is " + chr(96) + "OPEN" + chr(96),
                            "Every entry is approved")
        self.reject(a)

    def test_replacing_appendix_a_is_rejected(self):
        a = list(make_fixture())
        a[1] = a[1].split("## Appendix A:")[0]
        self.reject(a)

    def test_source_failure_without_original_provenance_is_rejected(self):
        a = list(make_fixture())
        del a[0].source_variants["blocked-01"]
        del a[0].register["blocked-01"]
        self.reject(a)

    def test_url_reassignment_of_blocked_source_is_rejected(self):
        a = list(make_fixture())
        a[0].source_variants["blocked-01"][0]["url"] = "https://other.org/false"
        self.reject(a)

    def test_missing_article_is_rejected(self):
        a = list(make_fixture())
        del a[0].articles["sample"]
        self.reject(a)

    def test_forged_b09_excerpt_cannot_be_presented_as_a_review(self):
        a = list(make_fixture())
        next(x for x in a[2] if x["id"] == "B09")["excerpt"] = "Made-up support"
        self.reject(a)

    def test_b09_renamed_to_real_case_is_rejected(self):
        a = list(make_fixture())
        next(x for x in a[2] if x["id"] == "B09")["note"] = "verified"
        self.reject(a)

    def test_missing_article_source_is_rejected(self):
        a = list(make_fixture())
        a[2][0]["sources_with_hits"] = {"not-in-original-research": ["x"]}
        self.reject(a)

    def test_missing_source_candidate_lists_rejected(self):
        a = list(make_fixture())
        a[2][0].pop("sources_not_in_corpus")
        self.reject(a)

    def test_duplicate_machine_access_url_rejected(self):
        a = list(make_fixture())
        a[3] = [{"url": "https://example.org/blocked-01", "ok": True}] * 2
        self.reject(a)

    def test_untyped_machine_access_status_rejected(self):
        a = list(make_fixture())
        a[3] = [{"url": "https://example.org/blocked-01", "ok": "True"}]
        self.reject(a)

    def test_unrecognized_machine_keyword_status_rejected(self):
        a = list(make_fixture())
        a[2][0]["status"] = "HUMAN_VERIFIED"
        self.reject(a)

    def test_mismatched_article_file_path_rejected(self):
        a = list(make_fixture())
        a[2][0]["file"] = "../../outside.html"
        self.reject(a)

    def test_empty_original_excerpt_rejected(self):
        a = list(make_fixture())
        a[2][0]["excerpt"] = ""
        self.reject(a)

    def test_untrusted_boolean_line_number_rejected(self):
        a = list(make_fixture())
        a[2][0]["line"] = True
        self.reject(a)

    def test_source_id_cannot_repeat_across_hit_and_missing(self):
        a = list(make_fixture())
        a[2][0]["sources_not_in_corpus"] = ["sample-source"]
        self.reject(a)

# Each independently named hostile mutation is an actual unittest method.
# This is more than the requested minimum of 36 tests.
for _sid in sorted(gate.SEVERITIES):
    def _missing(self, sid=_sid):
        a = list(make_fixture())
        a[1] = a[1].replace("| " + sid + " |", "| SX-99 |", 1)
        self.reject(a)
    _missing.__name__ = "test_reject_missing_incident_" + _sid.replace("-", "_")
    setattr(Negative, _missing.__name__, _missing)

    def _severity(self, sid=_sid):
        a = list(make_fixture())
        old = "| " + sid + " | " + gate.SEVERITIES[sid] + " |"
        a[1] = a[1].replace(old, "| " + sid + " | WRONG |", 1)
        self.reject(a)
    _severity.__name__ = "test_reject_incident_severity_change_" + _sid.replace("-", "_")
    setattr(Negative, _severity.__name__, _severity)

for _n in range(1, 26):
    def _blocked(self, n=_n):
        a = list(make_fixture())
        a[1] = a[1].replace("blocked-" + f"{n:02d}",
                            "unknown-source-" + f"{n:02d}", 1)
        self.reject(a)
    _blocked.__name__ = "test_reject_dropped_blocked_original_" + f"{_n:02d}"
    setattr(Negative, _blocked.__name__, _blocked)

for _sid in sorted(gate.REVIEWABLE):
    def _appendix(self, sid=_sid):
        a = list(make_fixture())
        a[1] = a[1].replace("| " + sid + " | NOT human verified |", "", 1)
        self.reject(a)
    _appendix.__name__ = "test_reject_missing_appended_candidate_" + _sid
    setattr(Negative, _appendix.__name__, _appendix)

for _sid in sorted(gate.IDS):
    def _candidate(self, sid=_sid):
        a = list(make_fixture())
        a[2] = [x for x in a[2] if x["id"] != sid]
        self.reject(a)
    _candidate.__name__ = "test_reject_missing_machine_candidate_" + _sid
    setattr(Negative, _candidate.__name__, _candidate)

class ExactRepositoryCensus(unittest.TestCase):
    def test_native_original_repository_15_25_29_hold(self):
        root = HERE.parent
        spec = importlib.util.spec_from_file_location(
            "r50_real_archive_builder", HERE / "tools/build.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        lib = module.Library(HERE)
        docs = HERE / "docs/r48"
        md = (docs / "SAFETY-EXCEPTION-REGISTER-2026-11-01.md").read_text(encoding="utf-8")
        candidates = json.loads((docs / "SAFETY-CANDIDATES-2026-11-01.json")
                                .read_text(encoding="utf-8"))
        access = json.loads((docs / "SOURCE-ACCESSIBILITY-2026-11-01.json")
                            .read_text(encoding="utf-8"))
        r = gate.audit(lib, md, candidates, access)
        self.assertEqual((r["counts"]["open_incidents"],
                          r["counts"]["historically_blocked_sources"],
                          r["counts"]["candidate_rows"]), (15, 25, 29))
        self.assertFalse(r["qualified_safety_clearance"])
        self.assertFalse(r["may_publish"])
        self.assertTrue(all(not x["human_link_check_complete"]
                            for x in r["unresolved_source_access"]))

if __name__ == "__main__":
    unittest.main()
