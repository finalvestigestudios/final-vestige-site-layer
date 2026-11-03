#!/usr/bin/env python3
"""R79 NASA source-page custody and deterministic source-only staging exhibit.

This audits six official NASA image-detail pages, not their photograph rights.
No image binaries, speculative geographies, WordPress writes or network fetches.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import re
import subprocess
import zipfile
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ATLAS = Path("experience2/evidence-atlas")
CROSSWALK = Path("experience2/research-desk/sources/R37_PHOTO_CUSTODY_CROSSWALK.json")
AUDIT = ATLAS / "sources/R79_NASA_PAGE_AUDIT.json"
STYLE = ATLAS / "staging/r79-source-review.css"
CROSSWALK_BLOB = "ca00a51d8d47d02f9ccc2fbb55df31a0ed36e7ea"
EXPECTED = {
 "01": ("S67-19766", None, "1967-01", None, "NASA", "PROVISIONAL_NO_PAGE_PIA", "apollo-1-crew-honored", "2023-03-26"),
 "02": ("S67-15717", "S67-15717", "1967-01-03", "JSC", None, "PIA_ON_OFFICIAL_PAGE", "amf-s67-15717", "2024-06-06"),
 "03": ("S66-58038", "S66-58038", "1966-10-18", "JSC", None, "PIA_ON_OFFICIAL_PAGE", "amf-s66-58038", "2024-06-06"),
 "04": ("KSC-20170124-PH_KLS01_0164", "KSC-20170124-PH_KLS01_0164", "2017-01-24", "KSC", "NASA/Kim Shiflett", "PIA_ON_OFFICIAL_PAGE", "amf-ksc-20170124-ph_kls01_0164", "2023-05-04"),
 "05": ("S67-21294", "S67-21294", "1967-01-28", "JSC", None, "PIA_ON_OFFICIAL_PAGE", "amf-s67-21294", "2024-06-06"),
 "06": ("KSC-20170124-PH_KLS01_0090", "KSC-20170124-PH_KLS01_0090", "2017-01-24", "KSC", "NASA/Kim Shiflett", "PIA_ON_OFFICIAL_PAGE", "amf-ksc-20170124-ph_kls01_0090", "2024-06-12"),
}
RECORD_KEYS = frozenset(("id", "catalog_claim", "identity_status", "nasa_page_pia", "nasa_url",
 "nasa_page_title", "taken_date", "date_precision", "date_display", "producer_on_page",
 "credit_on_page", "nasa_page_last_updated", "evidence_scope", "limitation", "reuse_status"))

def blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def safe_nasa_url(value: str, slug: str) -> bool:
    if not isinstance(value, str):
        return False
    try:
        u = urlsplit(value)
        return (u.scheme == "https" and u.netloc == "www.nasa.gov"
                and u.path == f"/image-detail/{slug}/"
                and not u.query and not u.fragment and not u.username and not u.password)
    except ValueError:
        return False

def validate(root: Path, audit: dict | None = None, crosswalk: dict | None = None) -> list[dict]:
    root = Path(root)
    raw = (root / CROSSWALK).read_bytes()
    if blob(raw) != CROSSWALK_BLOB:
        raise ValueError("R79_R37_ORIGINAL_BLOB_CHANGED")
    crosswalk = crosswalk if crosswalk is not None else json.loads(raw)
    audit = audit if audit is not None else json.loads((root / AUDIT).read_text())
    if audit.get("schema") != "fv.ex2.apollo.nasa-page-audit.r79.v1" or audit.get("release") != "STAGING_HOLD":
        raise ValueError("R79_SCHEMA_OR_RELEASE")
    if audit.get("review_date") != "2026-11-02" or audit.get("media_guidelines") != "https://www.nasa.gov/nasa-brand-center/":
        raise ValueError("R79_SOURCE_GUIDANCE_CHANGED")
    for key in ("reusable_media_assessments_completed", "images_embedded", "geographic_pins", "speculative_edges"):
        if type(audit.get(key)) is not int or audit[key] != 0:
            raise ValueError("R79_UNCLEARED_MEDIA_OR_GEO_CLAIM")
    if "not media reuse clearance" not in audit.get("review_method", "").lower():
        raise ValueError("R79_MISLEADING_REVIEW_METHOD")
    if crosswalk.get("schema") != "fv.ex2.apollo.photo_custody.r37.v1" or crosswalk.get("release") != "STAGING_HOLD":
        raise ValueError("R79_R37_CROSSWALK_UNEXPECTED")
    rows = audit.get("records", [])
    prior = crosswalk.get("records", [])
    if not isinstance(rows, list) or not isinstance(prior, list) or len(rows) != 6 or len(prior) != 6:
        raise ValueError("R79_RECORD_COUNT")
    for i, (row, old) in enumerate(zip(rows, prior), 1):
        eid = f"{i:02d}"
        if not isinstance(row, dict) or frozenset(row) != RECORD_KEYS or row.get("id") != eid or old.get("id") != eid:
            raise ValueError("R79_RECORD_SHAPE_ORDER_OR_DUPLICATE")
        catalog, pia, dated, producer, credit, identity, slug, updated = EXPECTED[eid]
        required = (("catalog_claim", catalog), ("nasa_page_pia", pia), ("taken_date", dated),
                    ("producer_on_page", producer), ("credit_on_page", credit),
                    ("identity_status", identity), ("nasa_page_last_updated", updated),
                    ("date_precision", "MONTH_ONLY" if eid == "01" else "DAY"),
                    ("reuse_status", "INDIVIDUAL_REVIEW_REQUIRED"))
        if any(row.get(k) != v for k, v in required):
            raise ValueError("R79_NASA_PAGE_OBSERVATION_MUTATED")
        if not safe_nasa_url(row["nasa_url"], slug):
            raise ValueError("R79_NASA_URL_UNTRUSTED")
        if (old.get("catalog") != catalog or old.get("photo_url") != row["nasa_url"]
            or old.get("date") != dated or old.get("media_rights") != "INDIVIDUAL_REVIEW_REQUIRED"):
            raise ValueError("R79_R37_SOURCE_CROSSWALK_MISMATCH")
        for key in ("nasa_page_title", "date_display", "evidence_scope", "limitation"):
            val = row.get(key)
            if not isinstance(val, str) or not 4 <= len(val) <= 280 or any(t in val.lower() for t in
                ("nasa approved", "copyright cleared", "unrestricted reuse", "public domain licensed")):
                raise ValueError("R79_UNSUPPORTED_EDITORIAL_ASSERTION")
        if date.fromisoformat(updated) > date(2026, 11, 2):
            raise ValueError("R79_FUTURE_SOURCE_UPDATE")
        if dated != "1967-01":
            date.fromisoformat(dated)
    if "provisional" not in audit.get("identity_note", "").lower():
        raise ValueError("R79_CATALOG_UNCERTAINTY_LOST")
    return rows

def esc(value) -> str:
    return html.escape(str(value), quote=True)

def render_html(root: Path) -> str:
    rows = validate(root)
    css = (Path(root) / STYLE).read_text()
    if "@import" in css or "url(" in css:
        raise ValueError("R79_CSS_REMOTE_RESOURCE")
    by_id = {row["id"]: row for row in rows}
    # Chronology sorts source photographs; a month-only date cannot be asserted within January.
    order = ("03", "02", "01", "05", "04", "06")
    rail = "\n".join(f'<li><a href="#record-{idx}"><time>{esc(by_id[idx]["date_display"])}</time></a></li>' for idx in order)
    cards = []
    for row in rows:
        idx = row["id"]
        status = "Catalog not verified on this page" if idx == "01" else "PIA catalog on NASA page"
        custody = (
            ("NASA page title", row["nasa_page_title"]),
            ("Source photograph date", row["date_display"]),
            ("PIA field on NASA page", row["nasa_page_pia"] or "Not present; proposed catalog association remains provisional"),
            ("Producer explicitly identified", row["producer_on_page"] or "Not stated on linked NASA page"),
            ("Image credit explicitly identified", row["credit_on_page"] or "Not stated on linked NASA page"),
            ("NASA page updated", row["nasa_page_last_updated"]),
            ("What the photograph can establish", row["evidence_scope"]),
            ("What it cannot establish", row["limitation"]),
            ("Image reuse", "Individual media-rights assessment NOT completed. NASA page access is not permission to claim NASA endorsement."),
            ("NASA source URL", row["nasa_url"]),
        )
        dl = "\n".join(f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>" for k, v in custody)
        printed = " | ".join(f"{k}: {v}" for k, v in custody)
        cards.append(f"""<article class="card{' provisional' if idx == '01' else ''}" id="record-{idx}" aria-labelledby="heading-{idx}">
<div class="topline"><span>NASA Source {esc(idx)} / 06</span><span>{esc(status)}</span></div>
<h2 id="heading-{idx}">{esc(row['nasa_page_title'])}</h2>
<p><strong>Reference:</strong> {esc(row['catalog_claim'])} · {esc(row['date_display'])}</p>
<p>{esc(row['evidence_scope'])}</p>
<a class="source-link" href="{esc(row['nasa_url'])}">Read original NASA image-detail record ↗</a>
<details class="source-drawer"><summary>Inspect source custody and media-rights status</summary><dl>{dl}</dl></details>
<p class="print-custody">{esc(printed)}</p>
</article>""")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>Apollo 1 NASA Source Pages · Final Vestige Staging</title>
<style>{css}</style></head><body><main class="wrap" id="top">
<div class="mast"><span>Final Vestige / Apollo 1 Evidence Atlas</span><span>Editorial provenance lab · 02 Nov 2026</span></div>
<header class="hero"><p class="status">STAGING ONLY · RIGHTS REVIEW INCOMPLETE</p>
<h1>Six sources. Five catalog matches. One unresolved identity.</h1>
<p>Source-page evidence for Apollo 1, read from official NASA image-detail records. These are dates of photographs, not a sequence of events during the fire. The crew portrait is dated only to January 1967; its relative order within January is not established.</p>
<p>No NASA photograph has been reproduced here. <strong>All six photographs require individual reuse review</strong>; neither an active NASA source link nor a NASA catalog number establishes publishing permission or NASA endorsement.</p></header>
<nav class="rail" aria-label="Apollo photograph source chronology"><h2>Photographic source chronology</h2>
<p>Dates describe when photographs were taken. This is not an instrument timeline or fire reconstruction. January 1967 contains one undated-within-the-month image, so positions within that month are illustrative, not established ordering.</p>
<ol>{rail}</ol></nav>
<section aria-label="Six NASA source page audits" class="cards">{''.join(cards)}</section>
<footer><p><strong>Editorial evidence gate:</strong> Five PIA fields match their linked official NASA pages. The January 1967 crew image lacks a matching structured PIA field on its NASA page. All photographic reuse reviews remain pending.</p>
<p>NASA's <a href="https://www.nasa.gov/nasa-brand-center/">media and identity guidance</a> prohibits misleading endorsement and requires review of third-party and personal rights. This document makes no clearance determination. No geographic relationships are asserted.</p>
<p><a href="#top">Return to source chronology</a></p></footer></main></body></html>"""

def build(root: Path, dest: Path, head: str | None = None) -> dict:
    root = Path(root).resolve(strict=True)
    dest = Path(dest).resolve()
    if dest == root or root in dest.parents:
        raise ValueError("R79_OUTPUT_MUST_BE_OUTSIDE_REPO")
    if head is not None:
        if not re.fullmatch(r"[0-9a-f]{40}", head):
            raise ValueError("R79_INVALID_HEAD")
        def git(*args):
            return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.DEVNULL)
        if git("rev-parse", "HEAD").decode().strip() != head or git("status", "--porcelain").strip():
            raise ValueError("R79_NOT_CLEAN_EXACT_HEAD")
        for name in (AUDIT, STYLE, Path("experience2/evidence-atlas/tests/build_nasa_gallery_r79.py"), CROSSWALK):
            data = (root / name).read_bytes()
            if (root / name).is_symlink() or git("show", head + ":" + name.as_posix()) != data:
                raise ValueError("R79_NOT_EXACT_SOURCE_BYTES")
    markup = render_html(root).encode("utf-8")
    if any(token in markup for token in (b"<img", b"<script", b"data-lat=", b"data-geo-edge=")):
        raise ValueError("R79_FORBIDDEN_MEDIA_OR_GEO")
    source, css = (root / AUDIT).read_bytes(), (root / STYLE).read_bytes()
    outputs = {"R79_NASA_SOURCE_GALLERY.html": markup, "R79_NASA_PAGE_AUDIT.json": source, "r79-source-review.css": css}
    manifest = {
        "schema": "fv.ex2.apollo.nasa-gallery.r79.v1", "release": "STAGING_HOLD",
        "head": head, "nasa_official_page_reviews": 6, "nasa_catalog_matches": 5,
        "provisional_catalog_associations": 1, "image_reuse_cleared": 0,
        "wordPress_installed": False, "hosted_field_cwv": False, "production_deployed": False,
        "outputs": {name: hashlib.sha256(payload).hexdigest() for name, payload in outputs.items()}
    }
    outputs["R79_MANIFEST.json"] = (json.dumps(manifest, sort_keys=True, indent=2) + "\n").encode()
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, payload in sorted(outputs.items()):
            item = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            item.external_attr = 0o100644 << 16
            item.compress_type = zipfile.ZIP_STORED
            archive.writestr(item, payload)
    return {"zip_sha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
            "html_sha256": hashlib.sha256(markup).hexdigest(), "head": head, "release": "STAGING_HOLD"}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--head", default=None)
    args = p.parse_args()
    print(json.dumps(build(args.repo, args.out, args.head), sort_keys=True))

if __name__ == "__main__":
    main()
