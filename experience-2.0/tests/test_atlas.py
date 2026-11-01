"""Atlas model, validator invariants and ingestion tests. No browser, no network."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest

import support
from build_dataset import assemble
from ingest_wp import diff, normalise, outbound_links
from validate_atlas import map_eligible, validate

ATLAS = support.EX2 / "atlas"


def dataset() -> dict:
    return json.loads((ATLAS / "data" / "atlas.json").read_text(encoding="utf-8"))


class Dataset(unittest.TestCase):
    def test_committed_dataset_is_valid_and_current(self):
        ds = dataset()
        self.assertEqual(validate(ds), [])
        self.assertEqual(json.dumps(ds, ensure_ascii=False, indent=2) + "\n", json.dumps(assemble(), ensure_ascii=False, indent=2) + "\n",
                         "atlas.json is stale; run atlas/tools/build_dataset.py")

    def test_no_place_is_mappable_today(self):
        ds = dataset()
        self.assertEqual([p["id"] for p in ds["places"] if map_eligible(p)], [])
        for p in ds["places"]:
            self.assertEqual(p["location_status"], "unverified_reference")
            self.assertIsNone(p["geometry"], p["id"])

    def test_no_coordinates_anywhere(self):
        text = (ATLAS / "data" / "atlas.json").read_text(encoding="utf-8")
        for key in ('"latitude"', '"longitude"', '"coordinates"', '"lat"', '"lon"'):
            self.assertNotIn(key, text)

    def test_all_six_investigations_present(self):
        self.assertEqual(sorted(i["wordpress_post_id"] for i in dataset()["investigations"]), [37, 269, 370, 433, 434, 621])

    def test_documents_separate_originals_from_reconstruction(self):
        classes = {d["id"]: d["evidence_class"] for d in dataset()["documents"]}
        self.assertEqual(classes["doc-apollo1-chronology"], "editorial_reconstruction")
        self.assertEqual(classes["doc-KSC-20170124-PH_KLS01_0129"], "later_depiction")
        self.assertEqual(classes["doc-S67-21294"], "original_document")

    def test_context_images_are_interpretive_not_documented(self):
        rels = {r["id"]: r for r in dataset()["relationships"]}
        self.assertEqual(rels["rel-s66-58038-context"]["basis"], "interpretive")
        self.assertEqual(rels["rel-s67-21294-depicts-fire"]["basis"], "documented")


class Invariants(unittest.TestCase):
    """Each editorial rule has a rejecting case."""

    def reject(self, mutate, needle):
        ds = copy.deepcopy(dataset())
        mutate(ds)
        errors = validate(ds)
        self.assertTrue(any(needle in e for e in errors), f"expected an error containing {needle!r}; got {errors}")

    def test_point_on_unverified_place(self):
        self.reject(lambda d: d["places"][0].__setitem__("geometry", {"type": "Point", "coordinates": [-80.5, 28.5]}), "must not carry geometry")

    def test_verified_requires_everything(self):
        def mutate(d):
            p = d["places"][0]
            p.update(location_status="verified_coordinate", geometry={"type": "Point", "coordinates": [-80.5, 28.5]})
        ds = copy.deepcopy(dataset())
        mutate(ds)
        errors = " | ".join(validate(ds))
        self.assertIn("geography_source_ids", errors)
        self.assertIn("approved review", errors)
        self.assertFalse(map_eligible(ds["places"][0]))

    def test_out_of_range_coordinate(self):
        self.reject(lambda d: d["places"][0].update(location_status="verified_coordinate", geometry={"type": "Point", "coordinates": [200, 95]}), "valid [lon, lat]")

    def test_approximate_region_cannot_be_a_point(self):
        self.reject(lambda d: d["places"][0].update(location_status="approximate_region", geometry={"type": "Point", "coordinates": [1, 1]}), "never a Point")

    def test_forbidden_predicates(self):
        for pred in ("caused_by", "shares_location", "shares_date", "adjacent_to"):
            self.reject(lambda d, p=pred: d["relationships"][0].__setitem__("predicate", p), "forbidden")

    def test_co_occurrence_is_not_a_basis(self):
        self.reject(lambda d: d["relationships"][0].__setitem__("justification", "Both events happened in the same place and the same year."), "shared place or date")

    def test_relationship_needs_source_and_reason(self):
        self.reject(lambda d: d["relationships"][0].__setitem__("source_ids", []), "at least one source")
        self.reject(lambda d: d["relationships"][0].__setitem__("justification", "ok"), "justification")

    def test_interpretive_predicates_must_be_labelled(self):
        self.reject(lambda d: d["relationships"][2].__setitem__("basis", "documented"), "must have basis 'interpretive'")

    def test_cross_investigation_must_be_interpretive(self):
        def mutate(d):
            d["relationships"].append({"id": "rel-x", "subject": "evt-apollo1-fire", "predicate": "corroborates", "object": "evt-halifax-explosion", "basis": "documented",
                                       "justification": "A claimed documented link between two unrelated investigations.", "source_ids": ["src-wp-434"], "review_status": "unreviewed"})
        self.reject(mutate, "across investigations must be interpretive")

    def test_unknown_references_and_duplicates(self):
        self.reject(lambda d: d["relationships"][0].__setitem__("object", "evt-nope"), "unknown object")
        self.reject(lambda d: d["events"][0].__setitem__("place_id", "place-nope"), "unknown place")
        self.reject(lambda d: d["events"].append(copy.deepcopy(d["events"][0])), "duplicate id")

    def test_documented_date_needs_source(self):
        self.reject(lambda d: d["events"][0].__setitem__("date_source_ids", []), "documented date needs")

    def test_reconstruction_must_name_derivation(self):
        def mutate(d):
            for doc in d["documents"]:
                if doc["evidence_class"] == "editorial_reconstruction":
                    doc["derived_from_source_ids"] = []
        self.reject(mutate, "must name derived_from_source_ids")

    def test_claim_needs_source(self):
        self.reject(lambda d: d["claims"][0].__setitem__("source_ids", []), "at least one source")


class Ingestion(unittest.TestCase):
    POSTS = [{"id": 1, "link": "https://finalvestige.com/a/", "slug": "a", "date": "2026-01-01T00:00:00", "modified": "2026-01-02T00:00:00",
              "title": {"rendered": "A"}, "excerpt": {"rendered": ""}, "categories": [5], "tags": [],
              "content": {"rendered": '<p><a href="https://www.nasa.gov/x">NASA</a> <a href="http://insecure.test/y">no</a> '
                                       '<a href="https://finalvestige.com/inner">inner</a> <a href="https://unknown.example/z">other</a> '
                                       '<a href="https://www.nasa.gov/x">dup</a></p>'}}]

    def test_outbound_links_are_https_external_deduped_and_not_guessed(self):
        links = outbound_links(self.POSTS[0]["content"]["rendered"])
        self.assertEqual([l["url"] for l in links], ["https://www.nasa.gov/x", "https://unknown.example/z"])
        self.assertEqual(links[0]["institution"], "NASA")
        self.assertIsNone(links[1]["institution"], "unknown hosts must stay unclassified")

    def test_diff_reports_changes_for_re_review(self):
        old = normalise(self.POSTS, {5: {"name": "Cat", "slug": "cat"}})
        changed = copy.deepcopy(self.POSTS)
        changed[0]["content"]["rendered"] += "<p>edited</p>"
        new = normalise(changed, {5: {"name": "Cat", "slug": "cat"}})
        self.assertEqual(diff(old, old), [])
        notes = diff(old, new)
        self.assertEqual(len(notes), 1)
        self.assertIn("re-review required", notes[0])
        self.assertTrue(any("MISSING" in n for n in diff(old, {"posts": []})))

    def test_cli_validate_entrypoint(self):
        proc = subprocess.run([sys.executable, "-I", str(ATLAS / "tools" / "validate_atlas.py")], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("0 map-eligible places", proc.stdout)


if __name__ == "__main__":
    unittest.main()
