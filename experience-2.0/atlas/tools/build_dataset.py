#!/usr/bin/env python3
"""Assemble atlas/data/atlas.json from three inputs, then validate it.

  wp_snapshot.json   ingested published posts (identity, URL, taxonomy, content hash, outbound sources)
  apollo1.json       reviewed Apollo 1 records, images and claim crosswalk
  curation.json      hand-authored events, places and relationships

`--check` fails when the committed atlas.json differs from a fresh assembly.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATLAS = HERE.parent
sys.path.insert(0, str(HERE))
from validate_atlas import validate  # noqa: E402

DATA = ATLAS / "data"
APOLLO = ATLAS.parent / "data" / "apollo1.json"
OUT = DATA / "atlas.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def assemble() -> dict:
    snap, apollo, cur = _load(DATA / "wp_snapshot.json"), _load(APOLLO), _load(DATA / "curation.json")
    events_by_inv: dict[int, list[str]] = {}
    for ev in cur["events"]:
        events_by_inv.setdefault(ev["investigation"], []).append(ev["id"])

    investigations, sources = [], []
    for post in snap["posts"]:
        pid = post["wordpress_post_id"]
        investigations.append({
            "id": f"inv-{pid}", "wordpress_post_id": pid, "url": post["url"], "slug": post["slug"],
            "title": html.unescape(post["title"]), "published": post["published"][:10], "modified_at_ingest": post["modified"],
            "themes": [c["slug"] for c in post["categories"]], "theme_labels": [c["name"] for c in post["categories"]],
            "event_ids": events_by_inv.get(pid, []), "content_sha256": post["content_sha256"],
            "outbound_source_count": len(post["outbound_sources"]), "editorial_status": "published", "review_status": "unreviewed",
        })
        sources.append({"id": f"src-wp-{pid}", "kind": "published_article", "title": html.unescape(post["title"]),
                        "institution": "Final Vestige Studios", "url": post["url"], "retrieved_on": snap["retrieved_at"][:10]})

    events = []
    for ev in cur["events"]:
        events.append({"id": ev["id"], "investigation_id": f"inv-{ev['investigation']}", "label": ev["label"], "date_from": ev["date_from"],
                       "date_to": ev["date_to"], "date_precision": ev["date_precision"], "date_status": ev["date_status"],
                       "date_source_ids": ev["date_source_ids"], "place_id": ev["place_id"]})

    places = []
    for pl in cur["places"]:
        places.append({"id": pl["id"], "display_name": pl["display_name"], "reference_text": pl["reference_text"],
                       "location_status": pl["location_status"], "geometry": None, "precision_note": "Not geocoded. Place reference only.",
                       "geography_source_ids": [], "review": {"status": "unreviewed", "reviewer": None, "reviewed_on": None}})

    report = apollo["primary_report"]
    policy = apollo["rights_policy"]
    sources.append({"id": "src-nasa-board-report", "kind": "institutional_report", "title": report["title"], "institution": "NASA",
                    "url": report["url"], "retrieved_on": policy["retrieved_on"]})
    for cs in apollo.get("claim_sources", []):
        sources.append({"id": cs["id"], "kind": cs["kind"], "title": cs["title"], "institution": cs["institution"], "url": cs["url"],
                        "retrieved_on": cs["retrieved_on"]})
    documents = [{"id": "doc-board-report", "title": report["title"], "institution": "NASA", "archive_id": "Apollo 204 Review Board Final Report",
                  "original_url": report["url"], "document_type": "report", "date_text": "1967", "evidence_class": "original_document",
                  "rights_basis": policy["basis_title"], "review_status": "unreviewed"}]
    claims = []
    for rec in apollo["records"]:
        img = rec["image"]
        nid = img["nasa_id"]
        sources.append({"id": f"src-nasa-{nid}", "kind": "archive_record", "title": f"NASA image record {nid}", "institution": "NASA",
                        "url": img["record_url"], "retrieved_on": policy["retrieved_on"]})
        documents.append({"id": f"doc-{nid}", "title": img["caption"], "institution": "NASA", "archive_id": nid, "original_url": img["record_url"],
                          "document_type": "photograph", "date_text": img["date_text"],
                          "evidence_class": "later_depiction" if img["role"] == "exhibit" else "original_document",
                          "depicts_event": img["depicts_event"], "credit": img["credit"], "rights_basis": policy["basis_title"],
                          "rights_status": policy["status"], "review_status": "unreviewed"})
        for n, row in enumerate(rec["crosswalk"], 1):
            cited = row.get("source_ids") or (["src-nasa-board-report"] if row["status"] in {"verified", "partial"} else ["src-wp-434"])
            claims.append({"id": f"clm-{rec['id']}-{n}", "investigation_id": "inv-434", "text": row["claim"], "status": row["status"],
                           "source_ids": cited, "caveat": row["source"]})
    documents.append({"id": "doc-apollo1-chronology", "title": apollo["chronology"]["title"], "institution": "Final Vestige Studios",
                      "archive_id": apollo["chronology"]["id"], "original_url": None, "document_type": "chronology",
                      "date_text": "1967-01-27", "evidence_class": "editorial_reconstruction",
                      "derived_from_source_ids": ["src-nasa-board-report"], "review_status": "unreviewed"})

    return {
        "schema_version": "0.1.0",
        "generated_from": {"wp_snapshot_sha256": _sha(DATA / "wp_snapshot.json"), "apollo1_sha256": _sha(APOLLO), "curation_sha256": _sha(DATA / "curation.json"),
                           "snapshot_retrieved_at": snap["retrieved_at"]},
        "investigations": investigations, "events": events, "places": places, "sources": sources,
        "documents": documents, "claims": claims, "relationships": cur["relationships"],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    ds = assemble()
    errors = validate(ds)
    if errors:
        print("FAIL: assembled dataset is invalid", *errors, sep="\n  ")
        return 1
    text = json.dumps(ds, indent=2, ensure_ascii=False, sort_keys=False) + "\n"
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print("STALE: atlas.json differs from a fresh assembly (run build_dataset.py)")
            return 1
        print("OK: atlas.json matches a fresh assembly")
        return 0
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.name}: " + ", ".join(f"{len(ds[c])} {c}" for c in ["investigations", "events", "places", "sources", "documents", "claims", "relationships"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
