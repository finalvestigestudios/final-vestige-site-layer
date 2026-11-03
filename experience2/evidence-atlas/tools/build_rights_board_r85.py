#!/usr/bin/env python3
"""R85 independent source/rights board. Offline, deterministic, never publication authorization."""
from __future__ import annotations
import hashlib
import html
import json
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[3]
SOURCES = {
    "crosswalk": ("experience2/research-desk/sources/R37_PHOTO_CUSTODY_CROSSWALK.json",
                  "ca00a51d8d47d02f9ccc2fbb55df31a0ed36e7ea"),
    "nasa": ("experience2/evidence-atlas/sources/R79_NASA_PAGE_AUDIT.json",
             "a3f9d8fe7a237e7b3b8aecb0bcc8aaec055e96d6"),
    "rights": ("experience2/evidence-atlas/sources/NASA_PAGE_RIGHTS_AUDIT_R55.json",
               "12f7019678a1e6afb7a813a51524bca29a5b522b"),
}
IDS = tuple(f"{i:02d}" for i in range(1, 7))
STYLE = Path(__file__).with_name("rights_board_r85.css")


def check(predicate: bool, code: str) -> None:
    if not predicate:
        raise ValueError("R85_SOURCE_HOLD:" + code)


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def load_sources(root: Path = ROOT) -> dict:
    sources = {}
    for key, (relpath, expected) in SOURCES.items():
        data = (root / relpath).read_bytes()
        check(git_blob(data) == expected, key.upper() + "_SOURCE_PIN_DRIFT")
        sources[key] = json.loads(data)
    return sources


def nasa_url(value: str) -> bool:
    try:
        parsed = urlsplit(value)
        return (parsed.scheme == "https" and parsed.netloc == "www.nasa.gov"
                and parsed.path.startswith("/image-detail/") and not parsed.query
                and not parsed.fragment and not parsed.username and not parsed.password)
    except (ValueError, TypeError, AttributeError):
        return False


def verify(sources: dict) -> list[dict]:
    x, n, r = (sources[key] for key in ("crosswalk", "nasa", "rights"))
    check(x["schema"] == "fv.ex2.apollo.photo_custody.r37.v1", "CROSSWALK_SCHEMA")
    check(n["schema"] == "fv.ex2.apollo.nasa-page-audit.r79.v1", "NASA_SCHEMA")
    check(r["schema"] == "fv.ex2.apollo.nasa-page-rights.r55.v1", "RIGHTS_SCHEMA")
    check(x["release"] == n["release"] == r["status"] == "STAGING_HOLD", "RELEASE_DRIFT")
    check(n["reusable_media_assessments_completed"] == 0 and n["images_embedded"] == 0
          and n["geographic_pins"] == 0 and n["speculative_edges"] == 0
          and r["policy"]["independent_rights_clearance"] == "NOT_COMPLETE",
          "MEDIA_STATUS_DRIFT")
    check(r["crosswalk_blob_git_sha1"] == SOURCES["crosswalk"][1], "CROSSWALK_REFERENCE")
    check(all(len(s["records"]) == 6 for s in (x, n, r)), "RECORD_COUNT")
    result = []
    for i, number in enumerate(IDS):
        a, b, c = (s["records"][i] for s in (x, n, r))
        check(a["id"] == b["id"] == c["id"] == number, "ID_" + number)
        check(a["catalog"] == b["catalog_claim"] == c["crosswalk_catalog"],
              "CATALOG_" + number)
        check(nasa_url(a["photo_url"]) and
              a["photo_url"] == b["nasa_url"] == c["nasa_page"], "LINK_" + number)
        check(a["date"] == b["taken_date"], "DATE_" + number)
        check(a["media_rights"] == b["reuse_status"] == "INDIVIDUAL_REVIEW_REQUIRED"
              and c["rights_status"] == "INDIVIDUAL_REVIEW_PENDING"
              and c["downloaded_or_embedded"] is False
              and c["human_link_check"] is False, "RIGHTS_" + number)
        check(len(b["evidence_scope"]) >= 16 and len(b["limitation"]) >= 16,
              "EXPLANATION_" + number)
        if number == "01":
            check(b["date_precision"] == "MONTH_ONLY" and b["taken_date"] == "1967-01"
                  and b["identity_status"] == "PROVISIONAL_NO_PAGE_PIA"
                  and b["nasa_page_pia"] is None
                  and c["catalog_display"] == "not_displayed_on_linked_nasa_page",
                  "UNRESOLVED_CREW_IDENTITY")
        else:
            check(b["date_precision"] == "DAY"
                  and re.fullmatch(r"\d{4}-\d{2}-\d{2}", b["taken_date"]) is not None
                  and b["identity_status"] == "PIA_ON_OFFICIAL_PAGE"
                  and b["nasa_page_pia"] == a["catalog"]
                  and c["catalog_display"] == "displayed_as_PIA_number",
                  "DAY_AND_PIA_" + number)
        result.append({
            "id": number, "catalog": a["catalog"], "url": a["photo_url"],
            "title": b["nasa_page_title"], "date": b["date_display"],
            "precision": b["date_precision"], "identity": b["identity_status"],
            "credit": b["credit_on_page"] or c["image_credit_as_displayed"]
                      or "Not stated on NASA detail page",
            "scope": b["evidence_scope"], "limitation": b["limitation"],
            "role": a["photo_role"], "identity_note": a["identity_note"],
        })
    check(result[3]["date"] == result[5]["date"] == "January 24, 2017",
          "SAME_DAY_NOT_SEQUENCE")
    return result


def markup(records: list[dict]) -> str:
    check(len(records) == 6 and all(r["id"] == IDS[i]
          and nasa_url(r["url"]) for i, r in enumerate(records)), "RENDER_INPUT")
    e = lambda value: html.escape(str(value), quote=True)
    cards = []
    for r in records:
        provisional = " — provisional association" if r["id"] == "01" else ""
        precision = "day unknown" if r["precision"] == "MONTH_ONLY" else "day recorded"
        cards.append(f'''<article class="card" id="r85-source-{e(r["id"])}" aria-labelledby="r85-title-{e(r["id"])}">
<div class="card-kicker"><span>NASA SOURCE {e(r["id"])} / 06</span><span class="badge">REUSE REVIEW PENDING</span></div>
<h3 id="r85-title-{e(r["id"])}">{e(r["title"])}</h3>
<dl><dt>Catalog claim</dt><dd>{e(r["catalog"])}{provisional}</dd>
<dt>Photograph date</dt><dd>{e(r["date"])} ({precision})</dd>
<dt>Source-page credit</dt><dd>{e(r["credit"])}</dd>
<dt>What it actually shows</dt><dd>{e(r["scope"])}</dd></dl>
<p class="provenance"><strong>Evidence boundary:</strong> {e(r["limitation"])}</p>
<details><summary>Inspect provenance and unresolved rights questions</summary>
<p><strong>Link is not a reproduction:</strong> the source is an external NASA page. No photo is embedded, individually cleared or licensed for this site.</p>
<p><strong>Identification caveat:</strong> {e(r["identity_note"])}</p><p><strong>Context:</strong> {e(r["role"])}</p>
<ol><li>Confirm exact photo and credit on the linked official page.</li>
<li>Review third-party rights and recognizable-person implications for this use.</li>
<li>Check NASA insignia, identity and no-endorsement restrictions.</li>
<li>Record separate editorial and rights approval before any image reuse.</li></ol></details>
<a class="buttonlink" href="{e(r["url"])}" rel="noopener noreferrer" target="_blank">Inspect NASA primary source {e(r["id"])} ↗</a>
</article>''')
    nav = "".join(f'<a href="#r85-source-{r["id"]}">Source {r["id"]}</a>'
                  for r in records)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>Apollo 1 | Source Review Board — STAGING HOLD</title>
<link rel="stylesheet" href="rights_board_r85.css"></head><body>
<div class="container"><div class="mast">FINAL VESTIGE STUDIOS / APOLLO EVIDENCE STUDIO / INDEPENDENT REVIEW</div>
<header class="header"><span class="kicker">EVIDENCE IS THE EXPERIENCE · CLEARANCE WORKBENCH</span>
<h1>Six records.<br><em>Zero permissions assumed.</em></h1>
<p class="lede">A no-JavaScript source review board for Apollo 1 Research Desk and Evidence Atlas. Each record links to NASA, distinguishes evidence from interpretation, and identifies the media-use decision that remains outstanding.</p>
<div class="warning" role="note"><strong>STAGING HOLD — NOT FOR PUBLICATION</strong>0 of 6 photographs have completed image-specific reuse assessments. NASA's general guidance does not establish individual rights, an endorsement, or clearance of third-party interests. No NASA images are embedded. The proposed S67-19766 association remains provisional.</div>
<div class="meta"><span>OFFICIAL NASA LINKS: 6/6</span><span>MEDIA REVIEWS: 0/6</span><span>GEO PINS: 0</span><span>JS: NOT REQUIRED</span></div></header>
<nav class="jump" aria-label="Jump to NASA source records">{nav}</nav>
<main><h2>Source custody and unresolved decisions</h2>
<p>The cards are ordered by evidence record number, <strong>not fire chronology</strong>. The crew portrait's day is unknown; both 2017 photos share one verified date without a verified time order.</p>
<div class="cards">{''.join(cards)}</div></main>
<footer class="footer"><p>Official policy: <a href="https://www.nasa.gov/nasa-brand-center/">NASA Brand Center and media-use conditions ↗</a>. This working review does not claim NASA approval, image ownership, or commercial endorsement.</p>
<p>Generated from byte-pinned R37 crosswalk, R79 NASA-page audit and R55 rights audit. Independent editorial, individual-rights, accessibility, hosted compatibility and founder reviews remain necessary.</p></footer></div></body></html>
'''


def build(out: Path, sources: dict | None = None) -> dict:
    records = verify(sources if sources is not None else load_sources())
    source_html = markup(records)
    check(not re.search(r"<img\b|<iframe\b|data-lat\b|data-lon\b|data-geo-edge\b",
                        source_html, re.I), "UNREVIEWED_MEDIA_OR_GEO")
    out.mkdir(parents=True, exist_ok=True)
    (out / "R85_NASA_SOURCE_REVIEW.html").write_bytes(source_html.encode("utf8"))
    shutil.copyfile(STYLE, out / "rights_board_r85.css")
    receipt = {
        "schema": "fv.apollo.r85.source-rights-review.v1",
        "release": "STAGING_HOLD", "rights_cleared": 0, "images_embedded": 0,
        "geographic_pins": 0, "speculative_edges": 0,
        "hosted_wordpress_tested": False, "release_approved": False,
        "source_git_blobs": {key: pair[1] for key, pair in SOURCES.items()},
        "html_sha256": hashlib.sha256(source_html.encode("utf8")).hexdigest(),
        "css_sha256": hashlib.sha256(STYLE.read_bytes()).hexdigest(),
        "records": [{
            "id": r["id"], "catalog": r["catalog"], "date_precision": r["precision"],
            "identity": r["identity"], "url": r["url"],
            "media_review": "INDIVIDUAL_REVIEW_REQUIRED"
        } for r in records],
    }
    (out / "R85_RIGHTS_RECEIPT.json").write_text(
        json.dumps(receipt, sort_keys=True, indent=2) + "\n", encoding="utf8")
    return receipt


if __name__ == "__main__":
    try:
        destination = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dist/apollo-r85")
        result = build(destination)
        print("R85 STAGING_HOLD: 6 NASA sources, 0 photo rights certified, 0 embedded images")
    except Exception:
        print("R85_SOURCE_HOLD: verification failed; publication forbidden", file=sys.stderr)
        sys.exit(1)
