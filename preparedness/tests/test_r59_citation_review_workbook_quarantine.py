#!/usr/bin/env python3
"""R59: synthetic, adversarial, and real-corpus private citation CSV tests."""
from __future__ import annotations

import copy
import csv
import importlib.util
import io
import json
from pathlib import Path
import unittest

import test_r58_exact_citation_occurrence_docket as prior

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "r59_private_csv_under_test",
    ROOT / "tools" / "r59_citation_review_workbook_quarantine.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def fixed():
    bridge = prior.private_bridge()
    docket = prior.docket(bridge)
    return bridge, docket


def text_csv(rows):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, quoting=csv.QUOTE_ALL, lineterminator="\n")
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def rows_csv(data):
    return list(csv.reader(io.StringIO(data.decode("utf-8"), newline=""),
                           strict=True))


class OriginalWorkbook(unittest.TestCase):
    def setUp(self):
        self.bridge, self.docket = fixed()
        self.packet = gate.make_packet(
            self.bridge, self.docket, expected=prior.EXPECTED)
        self.raw = self.packet["citation_occurrences_UNREVIEWED.csv"]

    def test_r58_exact_census(self):
        self.assertEqual(len(rows_csv(self.raw)) - 1, 4)

    def test_r58_original_evidence_unabridged(self):
        data = json.loads(self.packet["original_complete_R58_evidence.json"])
        self.assertEqual(data, self.docket)

    def test_original_source_records_not_compacted(self):
        data = json.loads(self.packet["original_complete_R58_evidence.json"])
        originals = data["individual_original_citation_occurrence_review_queue"]
        self.assertEqual(len(originals), 4)
        self.assertIn("notes", originals[0][
            "original_unabridged_contributor_source_record"])

    def test_parent_sha_in_manifest(self):
        manifest = json.loads(self.packet["manifest.json"])
        self.assertEqual(manifest["parent_R58_docket_sha256"],
                         self.docket["fingerprint_sha256"])

    def test_manifest_rejects_publicity(self):
        manifest = json.loads(self.packet["manifest.json"])
        for key in gate.HOLD_FLAGS:
            self.assertIs(manifest[key], False)
        self.assertEqual(manifest["release_state"], "HOLD")

    def test_immutable_header_order(self):
        self.assertEqual(rows_csv(self.raw)[0], list(gate.HEADERS))

    def test_source_and_article_identity_separate(self):
        rows = rows_csv(self.raw)
        self.assertNotEqual(rows[1][0], rows[4][0])
        self.assertEqual(rows[1][gate.HEADERS.index("source_url_display")],
                         rows[4][gate.HEADERS.index("source_url_display")])

    def test_repeated_citations_have_distinct_task_ids(self):
        rows = rows_csv(self.raw)
        self.assertEqual(len(set(r[0] for r in rows[1:])), 4)

    def test_no_prepopulated_review_notes(self):
        rows = rows_csv(self.raw)
        for row in rows[1:]:
            self.assertEqual(row[-len(gate.ANNOTATIONS):], [""] * 4)

    def test_all_machine_states_unreviewed(self):
        rows = rows_csv(self.raw)
        for row in rows[1:]:
            for col in ("human_source_retrieval_state",
                        "human_claim_support_state",
                        "qualified_hazard_safety_state"):
                self.assertEqual(row[gate.HEADERS.index(col)],
                                 "NOT_REVIEWED")

    def test_spreadsheet_formula_prevention_in_display(self):
        for formula in ("=NOW()", " +SUM(1,2)", "\t@cmd", "-2+3", "@link"):
            self.assertTrue(gate.display(formula, 500).startswith("'"))

    def test_preview_honestly_discloses_truncation(self):
        result = gate.display("x" * 500, 100)
        self.assertIn("PREVIEW TRUNCATED", result)
        self.assertEqual(result[:100], "x" * 100)

    def test_citation_context_is_preview_not_source(self):
        self.assertIn("PREVIEW_ONLY", gate.HEADERS)

    def test_determinism(self):
        other = gate.make_packet(self.bridge, self.docket,
                                 expected=prior.EXPECTED)
        self.assertEqual(self.packet, other)

    def test_packet_verification(self):
        self.assertTrue(gate.verify_packet(
            self.bridge, self.docket, self.packet, expected=prior.EXPECTED))

    def test_empty_return_makes_zero_untrusted_notes(self):
        report = gate.quarantine_return(self.bridge, self.docket, self.raw,
                                        expected=prior.EXPECTED)
        self.assertEqual(report["untrusted_annotated_rows"], 0)
        self.assertFalse(report["qualified_safety_clearance"])

    def test_normal_unicode_note_remains_untrusted(self):
        values = rows_csv(self.raw)
        values[1][gate.HEADERS.index(
            "reviewer_untrusted_notes")] = "À vérifier: source, scope; 🚧"
        result = gate.quarantine_return(
            self.bridge, self.docket, text_csv(values),
            expected=prior.EXPECTED)
        self.assertEqual(result["untrusted_annotated_rows"], 1)
        self.assertEqual(result["annotations_NOT_VERIFIED"][0][
            "review_verdict"], "UNTRUSTED_NOT_REVIEWED")
        self.assertFalse(result["independent_QD_approval"])

    def test_apparent_approval_text_not_authoritative(self):
        values = rows_csv(self.raw)
        values[1][-1] = "approved by physician (unverified note)"
        result = gate.quarantine_return(self.bridge, self.docket,
                                        text_csv(values), expected=prior.EXPECTED)
        self.assertFalse(result["qualified_safety_clearance"])
        self.assertFalse(result["may_publish"])
        self.assertEqual(result["annotations_NOT_VERIFIED"][0][
            "review_verdict"], "UNTRUSTED_NOT_REVIEWED")

    def test_two_annotations_same_source_kept_distinct(self):
        values = rows_csv(self.raw)
        pos = gate.HEADERS.index("reviewer_untrusted_notes")
        values[1][pos], values[2][pos] = "First use", "Second use"
        result = gate.quarantine_return(self.bridge, self.docket,
                                        text_csv(values), expected=prior.EXPECTED)
        self.assertEqual(result["untrusted_annotated_rows"], 2)
        ids = [r["citation_work_order_id_sha256"] for r in
               result["annotations_NOT_VERIFIED"]]
        self.assertEqual(len(set(ids)), 2)

    def test_full_original_census_requires_real_expected(self):
        with self.assertRaises(prior.gate.DocketHold):
            gate.make_packet(self.bridge, self.docket)

    def test_rejects_packet_missing_evidence(self):
        packet = dict(self.packet)
        packet.pop("original_complete_R58_evidence.json")
        with self.assertRaises(gate.WorkbookHold):
            gate.verify_packet(self.bridge, self.docket, packet,
                               expected=prior.EXPECTED)

    def test_rejects_packet_changed_csv(self):
        packet = dict(self.packet)
        packet["citation_occurrences_UNREVIEWED.csv"] += b"tamper"
        with self.assertRaises(gate.WorkbookHold):
            gate.verify_packet(self.bridge, self.docket, packet,
                               expected=prior.EXPECTED)

    def test_rejects_packet_modified_manifest(self):
        packet = dict(self.packet)
        packet["manifest.json"] = b"{}"
        with self.assertRaises(gate.WorkbookHold):
            gate.verify_packet(self.bridge, self.docket, packet,
                               expected=prior.EXPECTED)

    def test_rejects_modified_r58_evidence_even_self_resigned(self):
        doc = copy.deepcopy(self.docket)
        doc["individual_original_citation_occurrence_review_queue"][0][
            "human_claim_support_state"] = "APPROVED"
        doc["fingerprint_sha256"] = prior.gate.digest({
            k: v for k, v in doc.items() if k != "fingerprint_sha256"})
        with self.assertRaises(prior.gate.DocketHold):
            gate.make_packet(self.bridge, doc, expected=prior.EXPECTED)


class ReturnedWorkbookAttacks(unittest.TestCase):
    def setUp(self):
        self.bridge, self.docket = fixed()
        self.baseline = gate.make_packet(
            self.bridge, self.docket, expected=prior.EXPECTED)[
                "citation_occurrences_UNREVIEWED.csv"]

    def reject(self, mutation):
        data = rows_csv(self.baseline)
        mutation(data)
        with self.assertRaises(gate.WorkbookHold):
            gate.quarantine_return(
                self.bridge, self.docket, text_csv(data),
                expected=prior.EXPECTED)

    def test_drop_source_row(self):
        self.reject(lambda rows: rows.pop())

    def test_duplicate_source_row(self):
        self.reject(lambda rows: rows.append(rows[-1][:]))

    def test_reorder_source_rows(self):
        self.reject(lambda rows: rows.reverse())

    def test_missing_header(self):
        self.reject(lambda rows: rows[0].pop())

    def test_duplicate_header(self):
        self.reject(lambda rows: rows[0].append(rows[0][0]))

    def test_extra_column(self):
        self.reject(lambda rows: rows[1].append("unsupported"))

    def test_missing_column(self):
        self.reject(lambda rows: rows[1].pop())

    def test_unexpected_header_order(self):
        self.reject(lambda rows: rows[0].reverse())

    def test_truncated_csv(self):
        with self.assertRaises(gate.WorkbookHold):
            gate.quarantine_return(self.bridge, self.docket,
                                   self.baseline[:50], expected=prior.EXPECTED)

    def test_non_utf8(self):
        with self.assertRaises(gate.WorkbookHold):
            gate.quarantine_return(self.bridge, self.docket, b"\xff",
                                   expected=prior.EXPECTED)

    def test_utf8_bom_injection(self):
        with self.assertRaises(gate.WorkbookHold):
            gate.quarantine_return(
                self.bridge, self.docket, b"\xef\xbb\xbf" + self.baseline,
                expected=prior.EXPECTED)

    def test_nul_byte(self):
        with self.assertRaises(gate.WorkbookHold):
            gate.quarantine_return(self.bridge, self.docket,
                                   self.baseline + b"\x00", expected=prior.EXPECTED)

    def test_bytes_limit(self):
        with self.assertRaises(gate.WorkbookHold):
            gate.quarantine_return(self.bridge, self.docket,
                                   b"X" * 16_000_001, expected=prior.EXPECTED)

    def test_nonbytes(self):
        with self.assertRaises(gate.WorkbookHold):
            gate.quarantine_return(self.bridge, self.docket, "",
                                   expected=prior.EXPECTED)

    def test_oversized_note(self):
        def mutate(rows):
            rows[1][gate.HEADERS.index("reviewer_untrusted_notes")] = "a" * 4001
        self.reject(mutate)

    def test_4000_character_note_accepted_as_untrusted(self):
        data = rows_csv(self.baseline)
        data[1][gate.HEADERS.index("reviewer_untrusted_notes")] = "a" * 4000
        report = gate.quarantine_return(self.bridge, self.docket,
                                        text_csv(data), expected=prior.EXPECTED)
        self.assertEqual(report["untrusted_annotated_rows"], 1)

    def test_recorded_returned_checksum(self):
        data = rows_csv(self.baseline)
        data[1][-1] = "citation needs manual check"
        raw = text_csv(data)
        report = gate.quarantine_return(self.bridge, self.docket, raw,
                                        expected=prior.EXPECTED)
        self.assertEqual(report["raw_returned_csv_sha256"],
                         gate.sha_bytes(raw))


# Each original source/citation coordinate is an independently frozen field.
# An attacker cannot alter a task and make the modification acceptable by
# recalculating a spreadsheet-level or self-signed SHA-256.
def tamper_field(column):
    def test(self):
        self.reject(lambda rows: rows[1].__setitem__(
            gate.HEADERS.index(column), "FORGED_CITATION_OR_APPROVAL"))
    return test


for field in gate.IMMUTABLE:
    setattr(ReturnedWorkbookAttacks, "test_frozen_%s" % field,
            tamper_field(field))


# Reviewer-provided text may not be interpreted as executable spreadsheet
# formulas, formula-prefixed URLs or invisible bidirectional approval strings.
BAD_NOTES = (
    "=SUM(1,1)", " =HYPERLINK(1,2)", "+CMD|' /C calc'!A0",
    "-2+3", "@SUM(1,2)", "\t=CMD", "\n=NOW()", "\r=NOW()",
    "\x00approval", "unsafe\x7f", "\u202ereviewed",
    "\u2066approval", "line\nbreak", "tab\tinside",
    "\u202dapproved", " \u202eapproved", " =1",
    "\u2069", "\u202a", "\u202c",
)


def formula_case(value, position):
    def test(self):
        self.reject(lambda rows: rows[1].__setitem__(
            gate.HEADERS.index(position), value))
    return test


for index, value in enumerate(BAD_NOTES, 1):
    for field in gate.ANNOTATIONS:
        setattr(ReturnedWorkbookAttacks,
                "test_unsafe_annotation_%02d_%s" % (index, field),
                formula_case(value, field))


class RealCorpus(unittest.TestCase):
    def test_original_35_articles_and_all_citations(self):
        bridge, docket = gate.upstream()
        packet = gate.make_packet(bridge, docket)
        self.assertTrue(gate.verify_packet(bridge, docket, packet))
        rows = rows_csv(packet["citation_occurrences_UNREVIEWED.csv"])
        self.assertEqual(len(rows) - 1, 1959)
        self.assertEqual(len(set(row[0] for row in rows[1:])), 1959)
        self.assertEqual(docket["counts"]["original_articles"], 35)
        self.assertEqual(docket["counts"]["water_tools"], 1)
        self.assertEqual(docket["counts"]["unreviewed_global_shared_url_groups"], 30)
        self.assertEqual(docket["counts"]["unreviewed_base_fallback_relationships"], 43)
        report = gate.quarantine_return(
            bridge, docket, packet["citation_occurrences_UNREVIEWED.csv"])
        self.assertEqual(report["untrusted_annotated_rows"], 0)
        self.assertFalse(report["may_publish"])


if __name__ == "__main__":
    unittest.main()
