#!/usr/bin/env python3
"""R52: independently mutating private render/source evidence MUST stay HOLD."""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
GATE_PATH = ROOT / "preparedness/tools/r52_rendered_citation_custody_gate.py"
SPEC = importlib.util.spec_from_file_location("r52_rendered_gate", GATE_PATH)
assert SPEC is not None and SPEC.loader is not None
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class TestR52RenderedCitationCustody(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.layout, cls.deep, cls.boxes, cls.report = gate.load_packet(ROOT)

    def reject(self, *, rows=None, layout=None, deep=None, boxes=None, report=None):
        with self.assertRaises(gate.EvidenceHold):
            gate.verify_packet(
                self.rows if rows is None else rows,
                self.layout if layout is None else layout,
                self.deep if deep is None else deep,
                self.boxes if boxes is None else boxes,
                self.report if report is None else report,
            )

    def test_native_corpus_36_rendered_citation_sources(self):
        result = gate.verify(ROOT)
        self.assertEqual((result["articles"], result["water_planner"]), (35, 1))
        self.assertEqual((result["preview_pages"], result["viewport_measurements"]), (45, 225))
        self.assertEqual((result["visible_citation_links"], result["visible_article_source_entries"]), (1959, 367))
        self.assertEqual(result["reported_automated_axe_runs"], 90)
        self.assertEqual(result["release_state"], "HOLD")
        for field in ("may_publish", "human_source_links_verified",
                      "qualified_safety_clearance", "independent_QD_approval"):
            self.assertIs(result[field], False)

    def test_global_citation_loss_caught(self):
        p = copy.deepcopy(self.layout)
        p["pages"]["water-planner"]["widths"]["390"]["citeLinks"] -= 1
        self.reject(layout=p)

    def test_duplicate_article_slug_caught(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["slug"] = rows[1]["slug"]
        self.reject(rows=rows)

    def test_human_source_link_approval_caught(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["human_link_checked"] = "1"
        self.reject(rows=rows)

    def test_qd_approval_caught(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["independent_QD"] = "yes"
        self.reject(rows=rows)

    def test_publication_approval_caught(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["publication_eligible"] = "YES"
        self.reject(rows=rows)

    def test_article_draft_status_removed_caught(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["publish_state"] = "published"
        self.reject(rows=rows)

    def test_medical_approval_invented_caught(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["safety_review"] = "clinically_safe"
        self.reject(rows=rows)

    def test_live_wp_qa_claim_caught(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["rendered_qa_this_pass"] = "complete: live WordPress verified"
        self.reject(rows=rows)

    def test_one_of_fortyfive_pages_missing_caught(self):
        p = copy.deepcopy(self.layout)
        del p["pages"]["hub-water"]
        self.reject(layout=p)

    def test_unexpected_category_duplicate_page_caught(self):
        p = copy.deepcopy(self.layout)
        p["pages"]["hub-unverified"] = p["pages"]["hub-water"]
        self.reject(layout=p)

    def test_one_of_five_widths_missing_caught(self):
        p = copy.deepcopy(self.layout)
        del p["pages"]["household-emergency-plan"]["widths"]["360"]
        self.reject(layout=p)

    def test_broken_visible_source_anchor_caught(self):
        p = copy.deepcopy(self.layout)
        p["pages"]["making-water-safer"]["widths"]["390"]["brokenCiteAnchors"] = 1
        self.reject(layout=p)

    def test_hidden_unreferenced_source_caught(self):
        p = copy.deepcopy(self.layout)
        p["pages"]["making-water-safer"]["widths"]["390"]["unreferencedSources"] = 1
        self.reject(layout=p)

    def test_viewport_citation_count_drift_caught(self):
        p = copy.deepcopy(self.layout)
        p["pages"]["making-water-safer"]["widths"]["768"]["citeLinks"] -= 1
        self.reject(layout=p)

    def test_hidden_draft_warning_caught(self):
        p = copy.deepcopy(self.layout)
        p["pages"]["making-water-safer"]["widths"]["390"]["draftBadge"] = False
        self.reject(layout=p)

    def test_axe_violation_record_drift_caught(self):
        p = copy.deepcopy(self.deep)
        p["axe"]["household-emergency-plan@390"]["violations"].append({"id": "new-unreviewed"})
        self.reject(deep=p)

    def test_missing_nojs_page_check_caught(self):
        p = copy.deepcopy(self.deep)
        del p["no_js"]["water-planner"]
        self.reject(deep=p)

    def test_unfixed_planner_claimed_noscript_fixed_caught(self):
        p = copy.deepcopy(self.deep)
        p["no_js"]["water-planner"]["noscript"] = True
        self.reject(deep=p)

    def test_unfixed_action_box_claimed_visible_caught(self):
        p = copy.deepcopy(self.boxes)
        p["390"]["rows"]["water-planner"]["actTop"] = 1
        self.reject(boxes=p)

    def test_open_findings_removed_from_report_caught(self):
        self.reject(report=self.report.replace("QA-F1", "FIXED"))

    def test_hub_invented_sources_caught(self):
        p = copy.deepcopy(self.layout)
        p["pages"]["hub-water"]["widths"]["390"]["sourceItems"] = 1
        self.reject(layout=p)

    def test_duplicate_visible_id_caught(self):
        p = copy.deepcopy(self.layout)
        p["pages"]["household-emergency-plan"]["widths"]["390"]["dupIds"] = ["src-1"]
        self.reject(layout=p)

    def test_preview_error_caught(self):
        p = copy.deepcopy(self.layout)
        p["pages"]["household-emergency-plan"]["widths"]["390"]["consoleErrors"] = ["boom"]
        self.reject(layout=p)

    def test_redistributed_source_entries_cannot_hide_in_global_total(self):
        p = copy.deepcopy(self.layout)
        p["pages"]["household-emergency-plan"]["widths"]["390"]["sourceItems"] -= 1
        p["pages"]["three-day-kit"]["widths"]["390"]["sourceItems"] += 1
        self.reject(layout=p)

    def test_reviewer_hold_text_cannot_be_reinterpreted_as_pass(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["blockers"] = rows[0]["blockers"].replace(
            "independent QD pass not recorded", "independent QD pass granted")
        self.reject(rows=rows)


def make_original_article_source_test(slug: str):
    def test_case(self):
        # Each independently named case detects a missing source item in a
        # DIFFERENT article/tool; no global count alone can mask the loss.
        p = copy.deepcopy(self.layout)
        self.assertGreater(p["pages"][slug]["widths"]["390"]["sourceItems"], 0)
        p["pages"][slug]["widths"]["390"]["sourceItems"] -= 1
        self.reject(layout=p)
    return test_case


ORIGINAL_SLUGS = [r["slug"] for r in gate.load_packet(ROOT)[0]]
for slug in ORIGINAL_SLUGS:
    name = "test_original_article_source_parity_" + slug.replace("-", "_")
    setattr(TestR52RenderedCitationCustody, name, make_original_article_source_test(slug))


def make_original_blob_test(relative: str, original_sha: str):
    def test_case(self):
        p = ROOT / gate.R48_DIR / relative
        payload = p.read_bytes()
        self.assertEqual(gate.git_blob_sha(payload), original_sha)
        gate.verify_blob(payload, original_sha, relative)
        with self.assertRaises(gate.EvidenceHold):
            gate.verify_blob(payload + b"\x00", original_sha, relative)
    return test_case


for relative, expected_sha in gate.PINS.items():
    clean = relative.replace("/", "_").replace(".", "_").replace("-", "_")
    setattr(TestR52RenderedCitationCustody, "test_pin_" + clean,
            make_original_blob_test(relative, expected_sha))


if __name__ == "__main__":
    unittest.main()
