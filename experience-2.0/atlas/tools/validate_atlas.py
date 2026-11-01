#!/usr/bin/env python3
"""Validate the Atlas dataset: structure, referential integrity, and the editorial invariants.

Invariants (each has a rejecting test in tests/test_atlas.py):
  * a place is mappable only with a verified coordinate, a stated precision, geography sources and an approved review;
  * an unverified location reference carries no geometry;
  * a relationship is documented (cited) or interpretive (labelled); co-occurrence of place or date is never a basis;
  * causal and adjacency predicates are forbidden;
  * a relationship across investigations must be interpretive and cited.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ATLAS = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ATLAS / "schema" / "atlas.schema.json").read_text(encoding="utf-8"))
ENUMS = SCHEMA["x-enums"]
COLLECTIONS = ["investigations", "events", "places", "sources", "documents", "claims", "relationships"]
CO_OCCURRENCE = re.compile(r"^\s*(both|same|shares?|shared|they)\b.*\b(place|location|date|day|year|time|area|region)\b", re.I)


def map_eligible(place: dict) -> bool:
    """The only gate through which a place may become a map pin."""
    geom = place.get("geometry")
    return bool(
        place.get("location_status") == "verified_coordinate"
        and isinstance(geom, dict) and geom.get("type") == "Point"
        and _valid_lonlat(geom.get("coordinates"))
        and place.get("precision_note")
        and place.get("geography_source_ids")
        and (place.get("review") or {}).get("status") == "approved"
    )


def _valid_lonlat(coords) -> bool:
    return (isinstance(coords, list) and len(coords) == 2 and all(isinstance(c, (int, float)) and not isinstance(c, bool) for c in coords)
            and -180 <= coords[0] <= 180 and -90 <= coords[1] <= 90)


def validate(ds: dict) -> list[str]:
    errors: list[str] = []
    for key in SCHEMA["required"]:
        if key not in ds:
            errors.append(f"missing top-level key {key!r}")
    if errors:
        return errors

    ids: dict[str, str] = {}
    for coll in COLLECTIONS:
        for item in ds[coll]:
            iid = item.get("id")
            if not iid:
                errors.append(f"{coll}: item without id")
            elif iid in ids:
                errors.append(f"duplicate id {iid!r} ({ids[iid]} and {coll})")
            else:
                ids[iid] = coll
    by = {c: {i["id"]: i for i in ds[c] if i.get("id")} for c in COLLECTIONS}

    def need_ref(owner: str, ref: str, coll: str) -> None:
        if ref not in by[coll]:
            errors.append(f"{owner}: unknown {coll[:-1]} {ref!r}")

    def enum(owner: str, field: str, value, name: str) -> None:
        if value not in ENUMS[name]:
            errors.append(f"{owner}: {field}={value!r} not in {ENUMS[name]}")

    for inv in ds["investigations"]:
        for eid in inv.get("event_ids", []):
            need_ref(inv["id"], eid, "events")
            if eid in by["events"] and by["events"][eid]["investigation_id"] != inv["id"]:
                errors.append(f"{inv['id']}: event {eid} belongs to another investigation")
        if not str(inv.get("url", "")).startswith("https://finalvestige.com/"):
            errors.append(f"{inv['id']}: canonical url must be on finalvestige.com")
    for ev in ds["events"]:
        need_ref(ev["id"], ev["investigation_id"], "investigations")
        need_ref(ev["id"], ev["place_id"], "places")
        enum(ev["id"], "date_precision", ev["date_precision"], "date_precision")
        enum(ev["id"], "date_status", ev["date_status"], "date_status")
        if ev["date_status"] == "documented" and not ev.get("date_source_ids"):
            errors.append(f"{ev['id']}: a documented date needs date_source_ids")
        if ev["date_precision"] == "unknown" and ev.get("date_from"):
            errors.append(f"{ev['id']}: precision 'unknown' must not carry a date")
        for sid in ev.get("date_source_ids", []):
            need_ref(ev["id"], sid, "sources")
    for pl in ds["places"]:
        pid, status, geom = pl["id"], pl.get("location_status"), pl.get("geometry")
        enum(pid, "location_status", status, "location_status")
        for sid in pl.get("geography_source_ids", []):
            need_ref(pid, sid, "sources")
        review = (pl.get("review") or {}).get("status")
        enum(pid, "review.status", review, "review_status")
        if status == "unverified_reference" and geom is not None:
            errors.append(f"{pid}: an unverified location reference must not carry geometry")
        if status == "verified_coordinate":
            if not (isinstance(geom, dict) and geom.get("type") == "Point" and _valid_lonlat(geom.get("coordinates"))):
                errors.append(f"{pid}: verified_coordinate requires a Point with valid [lon, lat]")
            if not pl.get("precision_note"):
                errors.append(f"{pid}: verified_coordinate requires precision_note")
            if not pl.get("geography_source_ids"):
                errors.append(f"{pid}: verified_coordinate requires geography_source_ids")
            if review != "approved":
                errors.append(f"{pid}: verified_coordinate requires an approved review")
        if status == "approximate_region":
            if not (isinstance(geom, dict) and geom.get("type") in {"Polygon", "MultiPolygon", "BBox"}):
                errors.append(f"{pid}: approximate_region requires Polygon, MultiPolygon or BBox geometry (never a Point)")
            if not pl.get("precision_note") or not pl.get("geography_source_ids"):
                errors.append(f"{pid}: approximate_region requires precision_note and geography_source_ids")
    for src in ds["sources"]:
        enum(src["id"], "kind", src["kind"], "source_kind")
        if not str(src.get("url", "")).startswith("https://"):
            errors.append(f"{src['id']}: url must be https")
    for doc in ds["documents"]:
        enum(doc["id"], "evidence_class", doc["evidence_class"], "evidence_class")
        enum(doc["id"], "review_status", doc["review_status"], "review_status")
        if doc["evidence_class"] != "editorial_reconstruction" and not str(doc.get("original_url") or "").startswith("https://"):
            errors.append(f"{doc['id']}: a document needs an https original_url unless it is an editorial reconstruction")
        if doc["evidence_class"] == "editorial_reconstruction" and not doc.get("derived_from_source_ids"):
            errors.append(f"{doc['id']}: an editorial reconstruction must name derived_from_source_ids")
        for sid in doc.get("derived_from_source_ids", []):
            need_ref(doc["id"], sid, "sources")
    for cl in ds["claims"]:
        need_ref(cl["id"], cl["investigation_id"], "investigations")
        enum(cl["id"], "status", cl["status"], "claim_status")
        if not cl.get("source_ids"):
            errors.append(f"{cl['id']}: a claim needs at least one source")
        for sid in cl.get("source_ids", []):
            need_ref(cl["id"], sid, "sources")
    all_ids = set(ids)
    event_inv = {e["id"]: e["investigation_id"] for e in ds["events"]}
    for rel in ds["relationships"]:
        rid = rel["id"]
        for end in ("subject", "object"):
            if rel[end] not in all_ids:
                errors.append(f"{rid}: unknown {end} {rel[end]!r}")
        pred = rel["predicate"]
        if pred in ENUMS["forbidden_predicates"]:
            errors.append(f"{rid}: predicate {pred!r} is forbidden (no causal or co-location edges)")
        else:
            enum(rid, "predicate", pred, "predicate")
        enum(rid, "basis", rel["basis"], "relationship_basis")
        enum(rid, "review_status", rel["review_status"], "review_status")
        just = (rel.get("justification") or "").strip()
        if len(just) < 20:
            errors.append(f"{rid}: justification must explain the basis (>= 20 characters)")
        if CO_OCCURRENCE.search(just):
            errors.append(f"{rid}: shared place or date is not a basis for a relationship")
        if not rel.get("source_ids"):
            errors.append(f"{rid}: every relationship needs at least one source")
        for sid in rel.get("source_ids", []):
            need_ref(rid, sid, "sources")
        if pred in ENUMS["interpretive_only_predicates"] and rel["basis"] != "interpretive":
            errors.append(f"{rid}: {pred!r} is an interpretation and must have basis 'interpretive'")
        a, b = event_inv.get(rel["subject"]), event_inv.get(rel["object"])
        if a and b and a != b and rel["basis"] != "interpretive":
            errors.append(f"{rid}: a relationship across investigations must be interpretive")
    return errors


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ATLAS / "data" / "atlas.json"
    ds = json.loads(path.read_text(encoding="utf-8"))
    errors = validate(ds)
    pins = [p["id"] for p in ds["places"] if map_eligible(p)]
    if errors:
        print(f"FAIL: {len(errors)} error(s) in {path.name}", *errors, sep="\n  ")
        return 1
    print(f"OK: {path.name} valid; {len(ds['investigations'])} investigations, {len(ds['events'])} events, "
          f"{len(ds['relationships'])} relationships; {len(pins)} map-eligible places")
    return 0


if __name__ == "__main__":
    sys.exit(main())
