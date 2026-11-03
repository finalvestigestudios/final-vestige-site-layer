"""Deterministic cross-cluster evidence and draft-publication HOLD gates.

All tests are local-only. They do not modify any real source fragments, publish
to WordPress, create GitHub reviews or claim independent human safety approval.
"""
import copy
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import validate  # noqa: E402


class PreparednessCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = build.Library()

    def test_integrates_all_35_editorial_drafts_plus_private_planner(self):
        articles = {slug: m for slug, m in self.lib.articles.items() if m.get("kind") != "tool"}
        tools = {slug: m for slug, m in self.lib.articles.items() if m.get("kind") == "tool"}
        self.assertEqual(len(articles), 35)
        self.assertEqual(set(articles), set(self.lib.slate))
        self.assertEqual(set(tools), {"water-planner", "home-fire-escape-worksheet", "power-outage-planner",
                                    "family-reunification-card", "reunification-plan", "kit-builder"})
        self.assertEqual({m["status"]["publish"] for m in self.lib.articles.values()}, {"draft"})

    def test_every_canonical_path_is_unique(self):
        paths = [self.lib.url_path(slug) for slug in self.lib.articles]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertTrue(all(url.startswith("/preparedness/") for url in paths))

    def test_raw_source_rows_not_discarded(self):
        raw = sum(len(versions) for versions in self.lib.source_variants.values())
        self.assertEqual(raw, self.lib.crosswalk["raw_source_rows"])
        self.assertEqual(raw, 244, "Snapshot must not silently lose contributor rows")
        self.assertEqual(len(self.lib.crosswalk["source_files"]), 8)

    def test_crosswalk_exhaustively_records_all_shared_urls(self):
        by_url = {}
        for versions in self.lib.source_variants.values():
            for row in versions:
                by_url.setdefault(row["url"], []).append(row)
        actual = {url for url, rows in by_url.items() if len(rows) > 1}
        self.assertEqual(actual, set(self.lib.crosswalk_groups))
        self.assertEqual(len(actual), 32)
        self.assertEqual(len(by_url), 202)

    def test_every_shared_scope_preserves_full_original_record(self):
        for url, group in self.lib.crosswalk_groups.items():
            self.assertEqual(group["review_status"], "pending-human-source-and-reading-scope-review")
            observed = [row for versions in self.lib.source_variants.values()
                        for row in versions if row["url"] == url]
            expected = [v["source"] for v in group["variants"]]
            self.assertEqual(
                sorted(json.dumps({k: v for k, v in row.items() if k != "_origin"}, sort_keys=True)
                       for row in observed),
                sorted(json.dumps(row, sort_keys=True) for row in expected),
                url,
            )
            self.assertFalse(any(s.get("human_link_check") for s in expected),
                             "Do not turn machine-read into human-checked without evidence")

    def test_shared_id_is_selected_by_article_specific_reading_scope(self):
        hist_food = self.lib.articles["pioneer-travel-rations"]
        hist_field = self.lib.articles["pioneer-supply-chains-failed"]
        first = self.lib.source_for(hist_food, "loc-pioneer-diaries")
        second = self.lib.source_for(hist_field, "loc-pioneer-diaries")
        self.assertEqual(first["_origin"], "hist-food")
        self.assertEqual(second["_origin"], "hist-field")
        self.assertNotEqual(first["supports"], second["supports"])

    def test_unverified_base_cannot_borrow_a_food_cluster_check(self):
        base = self.lib.articles["making-water-safer"]
        original = self.lib.source_for(base, "nchfp-jerky")
        self.assertIsNone(original.get("verified_on"))
        self.assertEqual(original["_origin"], "base")
        self.assertTrue(self.lib.register["nchfp-jerky"]["verified_on"],
                        "The food-cluster verification remains preserved separately")

    def test_every_citation_is_verified_in_its_own_origin(self):
        for slug, meta in self.lib.articles.items():
            cited = set(re.findall(r"\{\{cite:([a-z0-9\-]+)\}\}", meta["_body"]))
            self.assertGreaterEqual(len(cited), 2, slug)
            for sid in cited:
                source = self.lib.source_for(meta, sid)
                self.assertTrue(source.get("verified_on"), f"{slug}: {sid} is not source-checked")

    def test_all_35_article_bodies_remain_complete_longform(self):
        for slug, meta in self.lib.articles.items():
            if meta.get("kind") == "tool":
                continue
            words = build.word_count(meta["_body"])
            self.assertGreaterEqual(words, 1800, f"{slug}: original long-form body was lost")

    def test_unresolved_shared_url_blocks_any_published_citation(self):
        lib = build.Library()
        meta = lib.articles["pioneer-travel-rations"]
        meta["status"]["publish"] = "published"
        meta["status"]["editorial"] = "reviewed"
        errors, _ = validate.validate(lib)
        self.assertTrue(any("CANNOT be published with unresolved shared-source scope" in e for e in errors), errors)

    def test_claim_scope_tampering_requires_crosswalk_reaudit(self):
        lib = build.Library()
        row = next(s for s in lib.source_variants["loc-pioneer-diaries"]
                   if s["_origin"] == "hist-field")
        row["supports"] += " UNREVIEWED NEW CLAIM"
        errors, _ = validate.validate(lib)
        self.assertTrue(any("source crosswalk mismatch" in e for e in errors), errors)

    def test_unrecorded_duplicate_url_is_rejected(self):
        lib = build.Library()
        duplicate = {
            "id": "test-unapproved-duplicate", "_origin": "test",
            "title": "Unapproved synthetic duplicate", "publisher": "Test",
            "kind": "regulator", "url": "https://www.cdc.gov/water-emergency/about/",
            "verified_on": None, "supports": None, "human_link_check": False,
        }
        lib.source_variants[duplicate["id"]] = [duplicate]
        lib.register[duplicate["id"]] = duplicate
        errors, _ = validate.validate(lib)
        self.assertTrue(any("duplicate url without source crosswalk" in e for e in errors), errors)

    def test_marking_shared_url_resolved_without_human_record_fails(self):
        lib = build.Library()
        url = next(iter(lib.crosswalk_groups))
        lib.crosswalk_groups[url]["review_status"] = "resolved"
        errors, _ = validate.validate(lib)
        self.assertTrue(any("marked-resolved shared source lacks reviewer" in e for e in errors), errors)

    def test_unlisted_article_origin_blocks_validation(self):
        lib = build.Library()
        del lib.article_origins["pioneer-travel-rations"]
        errors, _ = validate.validate(lib)
        self.assertTrue(any("origin map must contain every article" in e for e in errors), errors)

    def test_start_here_safety_repair_remains_included(self):
        lib = self.lib
        article = lib.articles["household-emergency-plan"]["_body"]
        self.assertIn("Do not switch off the main breaker", article)
        medicine = lib.articles["three-day-kit"]["_body"].lower()
        self.assertIn("refrigerated", medicine)
        self.assertIn("pharmacist", medicine)
        for slug in ("go-bags", "household-emergency-plan",
                     "preparedness-real-households", "three-day-kit"):
            self.assertTrue(lib.slate[slug]["gate"], slug)
            self.assertEqual(lib.articles[slug]["safety_review"]["state"], "pending")

    def test_human_link_check_is_required_before_publication(self):
        lib = build.Library()
        meta = lib.articles["making-water-safer"]
        meta["status"]["publish"] = "published"
        meta["status"]["editorial"] = "reviewed"
        errors, _ = validate.validate(lib)
        self.assertTrue(any("human source-link verification" in e for e in errors), errors)

    def test_independent_release_signoff_is_required_even_after_editorial_review(self):
        lib = build.Library()
        meta = lib.articles["making-water-safer"]
        meta["status"]["publish"] = "published"
        meta["status"]["editorial"] = "reviewed"
        errors, _ = validate.validate(lib)
        self.assertTrue(any("independent QD/release sign-off" in e for e in errors), errors)

    def test_build_manifest_explicitly_reports_hold_and_no_human_links(self):
        lib = build.Library()
        # Build manifest is constructed at build.main; assert the source inputs
        # that must drive its HOLD state without generating or writing outputs.
        self.assertTrue(any(m["status"]["publish"] == "draft" for m in lib.articles.values()))
        self.assertTrue(any(g["review_status"] != "resolved" for g in lib.crosswalk_groups.values()))
        self.assertEqual(
            sum(s.get("human_link_check") is True
                for versions in lib.source_variants.values() for s in versions),
            0,
        )


    def test_builder_rejects_unsafe_published_state_before_writing(self):
        import contextlib
        import io
        from unittest import mock
        lib = build.Library()
        lib.articles["go-bags"]["status"]["publish"] = "published"
        lib.articles["go-bags"]["status"]["editorial"] = "reviewed"
        with mock.patch.object(build, "Library", return_value=lib), \
             mock.patch.object(Path, "mkdir", side_effect=AssertionError("unsafe build must write nothing")), \
             contextlib.redirect_stderr(io.StringIO()) as stderr:
            result = build.main([])
        self.assertEqual(result, 2)
        self.assertIn("PREPAREDNESS BUILD HOLD", stderr.getvalue())

    def test_source_notes_and_human_check_state_survive_rendering(self):
        lib = build.Library()
        for slug in ("pioneer-travel-rations", "pioneer-supply-chains-failed"):
            meta = lib.articles[slug]
            built = build.build_article(lib, slug)["inner"]
            source = lib.source_for(meta, "loc-pioneer-diaries")
            self.assertIn("Human source-link check pending", built)
            self.assertIn("Shared-source reading scope: independent review pending", built)
            self.assertIn(build.esc(source["notes"]), built,
                          "A source's original reading-depth notes must remain visible on its own article")


    def test_specific_start_here_publication_requires_human_safety(self):
        """Retain PR #157's four repaired Start Here negative safety gates."""
        for slug in ("household-emergency-plan", "three-day-kit", "go-bags",
                     "preparedness-real-households"):
            lib = build.Library()
            meta = lib.articles[slug]
            self.assertTrue(lib.slate[slug]["gate"], slug)
            self.assertEqual(meta["safety_review"]["state"], "pending", slug)
            meta["status"]["publish"] = "published"
            meta["status"]["editorial"] = "reviewed"
            errors, _ = validate.validate(lib)
            self.assertTrue(
                any(slug in error and "CANNOT be published while a safety review is pending" in error
                    for error in errors),
                f"unsafe Start Here publication should be rejected: {slug}",
            )



if __name__ == "__main__":
    unittest.main()
