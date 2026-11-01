#!/usr/bin/env python3
"""R54 private reviewer workbooks: deterministic, safety and adversarial checks."""
from __future__ import annotations

import copy
import csv
import importlib.util
import io
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "r54_private_review_export_tests", ROOT / "tools" / "r54_action_review_export.py")
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)
COUNTS = (2, 3, 1, 2, 2, 1)


def order(slug, ordinal, citations, source_ids=None):
    bodyhash = ("%064x" % (ordinal + 13))
    flaghash = ("%064x" % (ordinal + 38))
    key = {
        "slug": slug,
        "block_ordinal": ordinal,
        "original_article_html_sha256": bodyhash,
        "original_R13_flag_sha256": flaghash,
        "citation_source_id_occurrences": citations,
    }
    sources = []
    for sid in dict.fromkeys(citations):
        sources.append({
            "source_id": sid,
            "citation_occurrences_in_block": citations.count(sid),
            "original_url": "https://example.org/shared-record",
            "article_contributor_origin": slug,
            "source_contributor_origin": slug,
            "original_source_record_sha256": ("%064x" % (ordinal + 100)),
            "original_source_use": "=a \r\n detailed study of article " + slug,
            "original_source_reading_scope": "Original long reading \u202e notes\nline 2",
            "original_source_supports_note": "Other scope, not proof",
            "shared_url_group_requires_human_review": True,
            "base_fallback_requires_human_review": False,
            "historically_machine_inaccessible_source_id": sid == "s2",
            "independent_source_scope_verified": False,
            "human_source_link_checked": False,
            "claim_supported_by_source_verified": False,
        })
    return {
        "work_order_id_sha256": gate.digest(key),
        "article": slug, "block_ordinal": ordinal,
        "original_article_html_sha256": bodyhash,
        "original_R13_flag_sha256": flaghash,
        "block_tag": "p", "risk_families_machine_flags": ["water-treatment"],
        "machine_priority_not_safety_diagnosis":
            "HIGH_MACHINE_REVIEW_PRIORITY" if not citations else "STANDARD_MACHINE_REVIEW_PRIORITY",
        "excerpt_not_factually_verified": "Follow instructions? \u202e =SUM(1)",
        "excerpt_truncated": False,
        "citation_source_id_occurrences": citations,
        "source_readings_in_article_scope": sources,
        "uncited_in_same_visible_block": not citations,
        "article_historical_safety_review_state_not_qualified_approval": "approved",
        "claim_support_verified": False, "qualified_safety_clearance": False,
        "independent_QD_approval": False, "may_publish": False,
        "review_state": gate.STATE,
    }


def fixture():
    r = {
        "schema": gate.R53_SCHEMA, "issue": 136, "release_state": "HOLD",
        "machine_authority": "R13_HEURISTIC_RETRIAGE_PLUS_ORIGINAL_CONTRIBUTOR_SOURCE_SCOPE",
        "article_count": 2,
        "may_publish": False, "qualified_safety_clearance": False,
        "independent_QD_approval": False, "human_source_links_verified": False,
        "claim_accuracy_verified": False,
        "counts": {"uncited_action_blocks": 1, "cited_action_blocks": 2,
                   "open_safety_exceptions": 2, "unresolved_historic_source_ids": 1},
        "work_orders": [
            order("a", 1, ["s1", "s1"]),
            order("a", 2, []),
            order("b", 1, ["s2"]),
        ],
        "open_safety_incidents": [
            {"id": "SX-01", "severity": "HIGH", "state": "HOLD"},
            {"id": "SX-02", "severity": "MEDIUM", "state": "HOLD"},
        ],
        "blocked_historical_source_ids_not_current_link_failures": ["s2"],
        "limitations": "Not a safety assessment",
    }
    repin(r)
    return r


def repin(report):
    report["fingerprint_sha256"] = gate.digest({
        k: v for k, v in report.items() if k != "fingerprint_sha256"
    })


def packet(report=None):
    return gate.make_packet(fixture() if report is None else report, expected=COUNTS)


class Positive(unittest.TestCase):
    def test_private_packet_has_six_files(self):
        self.assertEqual(set(packet()), set(gate.TABLES) | {
            "original_evidence.json", "manifest.json",
        })

    def test_action_rows_are_all_preserved(self):
        p = packet()
        rows = list(csv.DictReader(io.StringIO(
            p["action_review.csv"].decode("utf-8"), newline="")))
        self.assertEqual(len(rows), 3)
        self.assertEqual([r["block_ordinal"] for r in rows], ["1", "2", "1"])
        self.assertEqual([r["uncited_in_same_visible_block"] for r in rows],
                         ["false", "true", "false"])

    def test_repeated_same_block_citation_not_lost(self):
        rows = list(csv.DictReader(io.StringIO(
            packet()["action_review.csv"].decode("utf-8"), newline="")))
        self.assertEqual(json.loads(rows[0]["citation_source_id_occurrences_json"]),
                         ["s1", "s1"])
        self.assertEqual(rows[0]["same_block_citation_count"], "2")

    def test_cited_reading_rows_keep_same_url_separate(self):
        rows = list(csv.DictReader(io.StringIO(
            packet()["scoped_source_review.csv"].decode("utf-8"), newline="")))
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(set(r["original_url"] for r in rows)), 1)
        self.assertEqual({r["article_contributor_origin"] for r in rows}, {"a", "b"})
        self.assertEqual({r["source_id"] for r in rows}, {"s1", "s2"})

    def test_all_human_fields_blank_and_stays_hold(self):
        p = packet()
        for name in gate.TABLES:
            for row in csv.DictReader(io.StringIO(p[name].decode("utf-8"), newline="")):
                self.assertTrue(all(not v for k, v in row.items() if k.endswith("_blank")))
                self.assertEqual(row.get("review_state", "NOT_REVIEWED"), "NOT_REVIEWED")
        manifest = json.loads(p["manifest.json"])
        self.assertEqual(manifest["release_state"], "HOLD")
        for key in gate.FALSE_FLAGS:
            self.assertIs(manifest[key], False)

    def test_unmodified_original_json(self):
        p = packet()
        raw = json.loads(p["original_evidence.json"])
        self.assertEqual(raw, fixture())
        self.assertIn("\u202e", raw["work_orders"][0]["source_readings_in_article_scope"][0]
                      ["original_source_reading_scope"])

    def test_bidi_rendered_escape_but_original_json_preserved(self):
        p = packet()
        csvout = p["scoped_source_review.csv"].decode()
        self.assertNotIn("\u202e", csvout)
        self.assertIn("\\u202e", csvout)
        self.assertIn("\u202e", p["original_evidence.json"].decode())

    def test_formula_neutralization_in_notes(self):
        rows = list(csv.DictReader(io.StringIO(
            packet()["scoped_source_review.csv"].decode("utf-8"), newline="")))
        self.assertTrue(rows[0]["original_source_use"].startswith("'=a"))
        self.assertIn("\\r\\n", rows[0]["original_source_use"])

    def test_manifest_files_hashed_and_counted(self):
        p = packet()
        manifest = json.loads(p["manifest.json"])
        self.assertEqual(manifest["parent_R53_report_sha256"], fixture()["fingerprint_sha256"])
        for name, evidence in manifest["files"].items():
            self.assertEqual(evidence["sha256"], gate.sha_bytes(p[name]))
            self.assertEqual(evidence["bytes"], len(p[name]))
        self.assertEqual(manifest["files"]["action_review.csv"]["rows"], 3)
        self.assertEqual(manifest["files"]["scoped_source_review.csv"]["rows"], 2)
        self.assertEqual(manifest["files"]["open_safety_exceptions.csv"]["rows"], 2)
        self.assertEqual(manifest["files"]["historical_source_access_hold.csv"]["rows"], 1)

    def test_packet_is_deterministic(self):
        self.assertEqual(packet(), packet())

    def test_packet_read_only_not_input_mutation(self):
        src = fixture()
        before = copy.deepcopy(src)
        packet(src)
        self.assertEqual(src, before)

    def test_verify_packet_rejects_tampering(self):
        src = fixture()
        p = packet(src)
        self.assertTrue(gate.verify_packet(src, p, expected=COUNTS))
        p["action_review.csv"] += b"x"
        with self.assertRaises(gate.PacketHold):
            gate.verify_packet(src, p, expected=COUNTS)

    def test_export_spreadsheet_formula_prefixes(self):
        for value in ["=1+1", "+cmd", "-2", "@sum(2)", "   =HYPERLINK(1)",
                      "\ufeff=calc", "\u200b@calc", "\u2060+calc", "\u00a0-calc"]:
            with self.subTest(value=value):
                self.assertTrue(gate._safe_cell(value).startswith("'"))

    def test_control_unicode_preserved_only_in_original(self):
        self.assertEqual(gate._safe_cell("line\r\nnext"), "line\\r\\nnext")
        self.assertEqual(gate._safe_cell("x\tfoo"), "x\\tfoo")
        self.assertEqual(gate._safe_cell("x\\test"), "x\\\\test")
        self.assertEqual(gate._safe_cell("a\u202e=z"), "a\\u202e=z")

    def test_csv_rows_exact_schema(self):
        p = packet()
        for name, schema in gate.TABLES.items():
            rows = list(csv.reader(io.StringIO(p[name].decode("utf-8"), newline="")))
            self.assertEqual(rows[0], list(schema))
            self.assertTrue(all(len(row) == len(schema) for row in rows))

    def test_no_current_access_claim_for_historical_blockers(self):
        p = packet()
        rows = list(csv.DictReader(io.StringIO(
            p["historical_source_access_hold.csv"].decode("utf-8"), newline="")))
        self.assertEqual(rows[0]["historical_machine_failure_only"], "true")
        self.assertEqual(rows[0]["human_current_link_check_blank"], "")


REPORT_MUTATIONS = [
    ("release_pass", lambda r: r.__setitem__("release_state", "PASS")),
    ("approve_publish", lambda r: r.__setitem__("may_publish", True)),
    ("approve_safety", lambda r: r.__setitem__("qualified_safety_clearance", True)),
    ("approve_qd", lambda r: r.__setitem__("independent_QD_approval", True)),
    ("approve_human_links", lambda r: r.__setitem__("human_source_links_verified", True)),
    ("approve_claim_accuracy", lambda r: r.__setitem__("claim_accuracy_verified", True)),
    ("wrong_machine_authority", lambda r: r.__setitem__("machine_authority", "HUMAN_VERIFIED")),
    ("wrong_schema", lambda r: r.__setitem__("schema", "new")),
    ("wrong_issue", lambda r: r.__setitem__("issue", 137)),
    ("wrong_articles_count", lambda r: r.__setitem__("article_count", 1)),
    ("drop_order", lambda r: r["work_orders"].pop()),
    ("duplicate_order", lambda r: r["work_orders"].append(copy.deepcopy(r["work_orders"][0]))),
    ("swap_ordinal", lambda r: r["work_orders"][0].__setitem__("block_ordinal", 2)),
    ("change_article", lambda r: r["work_orders"][0].__setitem__("article", "z")),
    ("change_article_sha", lambda r: r["work_orders"][0].__setitem__(
        "original_article_html_sha256", "0" * 64)),
    ("change_flag_sha", lambda r: r["work_orders"][0].__setitem__(
        "original_R13_flag_sha256", "0" * 64)),
    ("change_cite_occurrence", lambda r: r["work_orders"][0].__setitem__(
        "citation_source_id_occurrences", ["s1"])),
    ("change_citation_type", lambda r: r["work_orders"][0].__setitem__(
        "citation_source_id_occurrences", [True])),
    ("drop_source_reading", lambda r: r["work_orders"][0]
     ["source_readings_in_article_scope"].pop()),
    ("duplicate_source_reading", lambda r: r["work_orders"][0]
     ["source_readings_in_article_scope"].append(copy.deepcopy(
         r["work_orders"][0]["source_readings_in_article_scope"][0]))),
    ("wrong_source_id", lambda r: r["work_orders"][0]
     ["source_readings_in_article_scope"][0].__setitem__("source_id", "s2")),
    ("wrong_source_count", lambda r: r["work_orders"][0]
     ["source_readings_in_article_scope"][0].__setitem__("citation_occurrences_in_block", 1)),
    ("unsafe_source_url", lambda r: r["work_orders"][0]
     ["source_readings_in_article_scope"][0].__setitem__("original_url", "javascript:alert(1)")),
    ("source_credentials_url", lambda r: r["work_orders"][0]
     ["source_readings_in_article_scope"][0].__setitem__("original_url", "https://evil:pass@example.org/")),
    ("source_hash_forgery", lambda r: r["work_orders"][0]
     ["source_readings_in_article_scope"][0].__setitem__("original_source_record_sha256", "NOT_A_SHA")),
    ("source_use_missing", lambda r: r["work_orders"][0]
     ["source_readings_in_article_scope"][0].pop("original_source_use")),
    ("source_review_forgery", lambda r: r["work_orders"][0]
     ["source_readings_in_article_scope"][0].__setitem__("human_source_link_checked", True)),
    ("source_scope_forgery", lambda r: r["work_orders"][0]
     ["source_readings_in_article_scope"][0].__setitem__("independent_source_scope_verified", True)),
    ("source_claim_forgery", lambda r: r["work_orders"][0]
     ["source_readings_in_article_scope"][0].__setitem__("claim_supported_by_source_verified", True)),
    ("order_claim_forgery", lambda r: r["work_orders"][0].__setitem__("claim_support_verified", True)),
    ("order_qd_forgery", lambda r: r["work_orders"][0].__setitem__("independent_QD_approval", True)),
    ("order_safety_forgery", lambda r: r["work_orders"][0].__setitem__("qualified_safety_clearance", True)),
    ("order_publish_forgery", lambda r: r["work_orders"][0].__setitem__("may_publish", True)),
    ("order_state_forgery", lambda r: r["work_orders"][0].__setitem__("review_state", "VERIFIED")),
    ("order_uncited_mismatch", lambda r: r["work_orders"][1].__setitem__(
        "uncited_in_same_visible_block", False)),
    ("order_excerpt_type", lambda r: r["work_orders"][0].__setitem__(
        "excerpt_not_factually_verified", None)),
    ("order_risk_type", lambda r: r["work_orders"][0].__setitem__(
        "risk_families_machine_flags", "water")),
    ("order_priority_forgery", lambda r: r["work_orders"][0].__setitem__(
        "machine_priority_not_safety_diagnosis", "SAFE")),
    ("incident_closed", lambda r: r["open_safety_incidents"][0].__setitem__("state", "CLOSED")),
    ("incident_severity", lambda r: r["open_safety_incidents"][0].__setitem__("severity", "SAFE")),
    ("incident_duplicate", lambda r: r["open_safety_incidents"].append(
        copy.deepcopy(r["open_safety_incidents"][0]))),
    ("historic_duplicate", lambda r: r["blocked_historical_source_ids_not_current_link_failures"]
     .append("s2")),
    ("historic_missing", lambda r: r["blocked_historical_source_ids_not_current_link_failures"]
     .pop()),
    ("wrong_cited_count", lambda r: r["counts"].__setitem__("cited_action_blocks", 20)),
    ("wrong_uncited_count", lambda r: r["counts"].__setitem__("uncited_action_blocks", 0)),
    ("wrong_incident_count", lambda r: r["counts"].__setitem__("open_safety_exceptions", 1)),
    ("wrong_historic_count", lambda r: r["counts"].__setitem__(
        "unresolved_historic_source_ids", 8)),
]


def adversarial(name, mutation):
    def test(self):
        r = fixture()
        mutation(r)
        repin(r)  # Attackers can rehash JSON; check meaning and row identity.
        with self.assertRaises(gate.PacketHold, msg=name):
            gate.make_packet(r, expected=COUNTS)
    test.__name__ = "test_reject_" + name
    return test


class Negative(unittest.TestCase):
    def test_fingerprint_without_repin_rejected(self):
        r = fixture()
        r["counts"]["cited_action_blocks"] = 4
        with self.assertRaises(gate.PacketHold):
            gate.make_packet(r, expected=COUNTS)

    def test_missing_csv_file_rejected(self):
        r = fixture()
        p = packet(r)
        p.pop("scoped_source_review.csv")
        with self.assertRaises(gate.PacketHold):
            gate.verify_packet(r, p, expected=COUNTS)

    def test_added_approval_file_rejected(self):
        r = fixture()
        p = packet(r)
        p["QD_PASS.txt"] = b"FAKE"
        with self.assertRaises(gate.PacketHold):
            gate.verify_packet(r, p, expected=COUNTS)

    def test_changed_manifest_bytes_rejected(self):
        r = fixture()
        p = packet(r)
        p["manifest.json"] = b"{}"
        with self.assertRaises(gate.PacketHold):
            gate.verify_packet(r, p, expected=COUNTS)

    def test_expected_non_tuple_rejected(self):
        r = fixture()
        for val in ([2, 3, 1, 2, 2, 1], (2, 3, -1, 2, 2, 1),
                    (2, True, 1, 2, 2, 1), (2, 3)):
            with self.subTest(val=val), self.assertRaises(gate.PacketHold):
                gate.make_packet(r, expected=val)

    def test_csv_table_requires_exact_fields(self):
        with self.assertRaises(gate.PacketHold):
            gate.csv_table(("a", "b"), [{"a": "x"}])

    def test_invalid_url_rejected(self):
        for url in ("http://x.example", "https://user:pw@x.example",
                    "https://x.example\nEvil", "https://"):
            self.assertFalse(gate.simple_https(url))

    def test_verification_requires_bytes(self):
        r = fixture()
        p = packet(r)
        p["action_review.csv"] = p["action_review.csv"].decode()
        with self.assertRaises(gate.PacketHold):
            gate.verify_packet(r, p, expected=COUNTS)

    def test_unverified_approval_survives_never(self):
        p = packet()
        self.assertNotIn(b"QD_PASS", p["manifest.json"])
        self.assertIn(b'"may_publish": false', p["manifest.json"])


for name, mutate in REPORT_MUTATIONS:
    setattr(Negative, "test_reject_" + name, adversarial(name, mutate))


class RealCorpus(unittest.TestCase):
    def test_exact_private_35_article_corpus(self):
        if not (ROOT / "sources" / "register.json").is_file():
            self.skipTest("source archive not mounted")
        report = gate.original_report(ROOT.parent)
        self.assertEqual(report["article_count"], 36)
        self.assertEqual(len(report["work_orders"]), 779)
        p = gate.make_packet(report)
        self.assertTrue(gate.verify_packet(report, p))
        manifest = json.loads(p["manifest.json"])
        self.assertEqual(manifest["files"]["action_review.csv"]["rows"], 779)
        self.assertEqual(manifest["files"]["open_safety_exceptions.csv"]["rows"], 15)
        self.assertEqual(manifest["files"]["historical_source_access_hold.csv"]["rows"], 25)
        self.assertEqual(len(p), 6)
        self.assertNotIn("QD_PASS", json.dumps(manifest))


if __name__ == "__main__":
    unittest.main()
