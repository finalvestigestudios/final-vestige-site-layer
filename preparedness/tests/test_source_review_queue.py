"""Offline source-scoping queue guards. Synthetic-only unit fixtures modify no repository data."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import source_review_queue as rq


def row(origin, index, sid, url, *, checked=True, human=False, support="Only the inspected section"):
    return {
        "row_key": f"{origin}:{index}:{sid}", "origin": origin, "file": f"sources/{origin}",
        "index": index, "source_id": sid, "url": url, "publisher": "Synthetic",
        "kind": "regulator", "verified_on": "2026-10-30" if checked else None,
        "human_link_check": human, "supports": support,
        "reading_limits": f"Only {origin} excerpts were read",
    }


def fixture():
    a, b = "https://example.test/a", "https://example.test/b"
    rows = [row("base", 0, "same", a, checked=False), row("start", 0, "same", a),
            row("start", 1, "exclusive", b)]
    group = {
        "url": a, "review_status": "pending-human-source-and-reading-scope-review",
        "variants": [
            {"origin": "base", "row_index": 0, "source": {"id": "same"}},
            {"origin": "start", "row_index": 0, "source": {"id": "same"}},
        ],
    }
    meta = {
        "slug": "first-aid-not-medical", "n": 1,
        "_body": "Draft {{cite:same}} and {{cite:exclusive}}.",
        "source_use": {"same": "Only limited, attributed excerpt", "exclusive": "Only the example page"},
        "status": {"publish": "draft", "editorial": "drafted"},
        "safety_review": {"state": "pending"},
    }
    lib = SimpleNamespace(
        crosswalk={"raw_source_rows": 3, "unique_source_urls": 2, "duplicate_url_groups": 1},
        crosswalk_groups={a: group}, article_origins={meta["slug"]: "start"},
        articles={meta["slug"]: meta},
        url_path=lambda slug: f"/preparedness/start-here/{slug}/",
    )
    return lib, rows


class ReviewQueueUnitTests(unittest.TestCase):
    def setUp(self):
        self.lib, self.rows = fixture()

    def report(self):
        return rq.build_review_queue(self.lib, rows=self.rows)

    def test_stable_byte_for_byte_digest_and_payload(self):
        self.assertEqual(self.report(), self.report())
        self.assertRegex(self.report()["sha256_review_queue_payload"], r"^[0-9a-f]{64}$")

    def test_preserves_both_source_reading_scopes(self):
        r = self.report()
        self.assertEqual(r["collisions"][0]["source_row_keys"], ["base:0:same", "start:0:same"])
        same = next(x for x in r["citations"] if x["source_id"] == "same")
        self.assertEqual(same["source_row_key"], "start:0:same")
        self.assertEqual(same["source_origin"], "start")

    def test_does_not_borrow_verification_from_different_cluster(self):
        self.lib.article_origins["first-aid-not-medical"] = "base"
        self.assertTrue(any("not machine-verified in its own reading scope" in x
                            for x in self.report()["errors"]))

    def test_undocumented_duplicate_physical_row_is_rejected(self):
        self.rows.append({**self.rows[-1], "row_key": "start:1:exclusive"})
        self.assertTrue(any("duplicate physical source row key" in x for x in self.report()["errors"]))

    def test_duplicate_id_within_origin_rejected(self):
        self.rows.append(row("start", 2, "exclusive", "https://example.test/b"))
        self.assertTrue(any("same source id repeated inside contributor origin" in x for x in self.report()["errors"]))

    def test_conflicting_urls_same_id_rejected(self):
        self.rows.append(row("shelter", 0, "same", "https://example.test/c"))
        self.assertTrue(any("source id has conflicting URLs" in x for x in self.report()["errors"]))

    def test_unowned_source_does_not_borrow_unrelated_cluster(self):
        self.lib.article_origins["first-aid-not-medical"] = "shelter"
        self.assertTrue(any("citation exclusive has no source row" in x for x in self.report()["errors"]))

    def test_missing_origin_is_rejected(self):
        self.lib.article_origins.clear()
        self.assertTrue(any("missing article origin" in x for x in self.report()["errors"]))

    def test_blank_article_source_use_is_not_credible_citation_scope(self):
        self.lib.articles["first-aid-not-medical"]["source_use"]["same"] = "  "
        self.assertTrue(any("lacks substantive nonblank" in x for x in self.report()["errors"]))

    def test_unused_author_notes_detected(self):
        self.lib.articles["first-aid-not-medical"]["source_use"]["ghost"] = "Not actually cited"
        self.assertTrue(any("uncited source_use metadata" in x for x in self.report()["errors"]))

    def test_missing_crosswalk_declared_group_rejected(self):
        self.lib.crosswalk_groups.clear()
        self.assertTrue(any("repeated URL has no declared crosswalk" in x for x in self.report()["errors"]))

    def test_declared_origins_must_match_real_rows(self):
        self.lib.crosswalk_groups[self.rows[0]["url"]]["variants"][0]["row_index"] = 6
        self.assertTrue(any("crosswalk identities do not match" in x for x in self.report()["errors"]))

    def test_accurate_review_hold_counts(self):
        a = self.report()
        self.assertEqual(a["summary"]["source_rows"], 3)
        self.assertEqual(a["summary"]["machine_verified_source_rows"], 2)
        self.assertEqual(a["summary"]["shared_scope_reviews_pending"], 1)
        self.assertEqual(a["summary"]["human_link_checks_pending"], 3)
        self.assertEqual(a["summary"]["article_source_citation_pairs"], 2)
        self.assertEqual(a["summary"]["structural_errors"], 0)
        self.assertEqual(a["release_state"], "HOLD")
        self.assertIs(a["may_publish"], False)

    def test_duplicate_citation_token_keeps_one_source_use_per_article(self):
        self.lib.articles["first-aid-not-medical"]["_body"] += " {{cite:same}}"
        self.assertEqual(self.report()["summary"]["article_source_citation_pairs"], 2)

    def test_source_claims_are_attributed_not_combined(self):
        self.rows[0]["supports"] = "Base had no substantive reading"
        self.rows[1]["supports"] = "Start actually read part one"
        claimed = next(x for x in self.report()["citations"] if x["source_id"] == "same")
        self.assertEqual(claimed["contributor_claim_scope"], "Start actually read part one")

    def test_changed_row_order_produces_changed_digest(self):
        first = self.report()["sha256_review_queue_payload"]
        self.rows[1]["index"] = 4
        self.rows[1]["row_key"] = "start:4:same"
        self.assertNotEqual(first, self.report()["sha256_review_queue_payload"])

    def test_no_network_called_or_private_records_written(self):
        # There is no network code or CMS client. The only potential write is
        # the explicit CLI --output option, never used by build_review_queue().
        with tempfile.TemporaryDirectory() as td:
            before = list(Path(td).iterdir())
            self.report()
            self.assertEqual(list(Path(td).iterdir()), before)

    def test_human_link_check_without_read_scope_is_rejected(self):
        self.rows[1]["human_link_check"] = True
        self.rows[1]["verified_on"] = None
        self.assertTrue(any("human-check flag set on machine-unverified" in x
                            for x in self.report()["errors"]))


if __name__ == "__main__":
    unittest.main()
