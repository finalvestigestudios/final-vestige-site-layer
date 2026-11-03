#!/usr/bin/env python3
"""R89 offline integrated Apollo review; source custody first, publication always blocked."""
from __future__ import annotations
import hashlib
import html
import importlib.util
import json
import re
import shutil
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CSS = HERE / "review_hub_r89.css"
SOURCES = (
    "experience2/evidence-atlas/tools/build_review_hub_r89.py",
    "experience2/evidence-atlas/tools/review_hub_r89.css",
    "experience2/evidence-atlas/tests/test_review_hub_r89.py",
    "experience2/evidence-atlas/tests/browser_review_hub_r89.py",
    "experience2/evidence-atlas/R89_INTEGRATED_REVIEW_STAGING_HOLD.md",
    ".github/workflows/ex2-apollo-r89-review-hub.yml",
)
PAGES = ("R89_REVIEW_HUB.html", "R88_READING_ROOM.html",
         "R87_PHOTOGRAPH_DATE_RAIL.html", "R85_NASA_SOURCE_REVIEW.html")
POLICY_URL = "https://www.nasa.gov/nasa-brand-center/"

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def escape(value) -> str:
    return html.escape(str(value), quote=True)

def module(filename, key):
    spec = importlib.util.spec_from_file_location(key, HERE / filename)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[key] = obj
    spec.loader.exec_module(obj)
    return obj

class MarkupAudit(HTMLParser):
    """Read the actual final HTML and verify every local link resolves."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.hrefs = []
        self.scripts = []
        self.media = []
        self.duplicates = []
    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        identity = data.get("id")
        if identity:
            if identity in self.ids:
                self.duplicates.append(identity)
            self.ids.add(identity)
        if tag == "a" and "href" in data:
            self.hrefs.append(data["href"])
        if tag == "script":
            self.scripts.append(data.get("src", "INLINE"))
        if tag in ("img", "picture", "video", "iframe", "source", "audio"):
            self.media.append(tag)
        if any(k in data for k in ("data-lat", "data-lon", "data-geo-edge")):
            self.media.append("GEO")

def audit_pages(folder: Path, allowed_sources: set[str]):
    checks = {}
    parsed = {}
    for name in PAGES:
        document = (folder / name).read_text("utf8")
        reader = MarkupAudit()
        reader.feed(document)
        reader.close()
        if reader.duplicates or reader.media:
            raise ValueError("R89_UNAPPROVED_DUPLICATE_MEDIA_OR_GEO:" + name)
        if name == PAGES[0] and reader.scripts:
            raise ValueError("R89_HUB_MUST_WORK_WITHOUT_JS")
        if name == PAGES[1] and reader.scripts != ["reading_room_r88.js"]:
            raise ValueError("R89_R88_ENHANCEMENT_DRIFT")
        if name != PAGES[1] and reader.scripts:
            raise ValueError("R89_UNEXPECTED_SCRIPT:" + name)
        parsed[name] = reader
    for name, reader in parsed.items():
        linked_sources = []
        for link in reader.hrefs:
            if link.startswith("https://"):
                if link != POLICY_URL and link not in allowed_sources:
                    raise ValueError("R89_UNREVIEWED_EXTERNAL_LINK:" + name)
                if link in allowed_sources:
                    linked_sources.append(link)
            else:
                target = urlsplit(link)
                if target.scheme or target.netloc or target.query:
                    raise ValueError("R89_UNREVIEWED_LINK:" + name)
                destination = target.path or name
                if "/" in destination or "\\" in destination or destination.startswith("."):
                    raise ValueError("R89_BAD_LOCAL_LINK:" + name)
                if destination.endswith(".html"):
                    if destination not in parsed:
                        raise ValueError("R89_MISSING_HTML_DESTINATION:" + destination)
                    if target.fragment and target.fragment not in parsed[destination].ids:
                        raise ValueError("R89_BROKEN_CROSS_DOCUMENT_ANCHOR:" + target.fragment)
                elif destination.endswith((".css", ".js")):
                    if not (folder / destination).is_file():
                        raise ValueError("R89_MISSING_ASSET:" + destination)
                elif destination != name:
                    raise ValueError("R89_INVALID_LOCAL_DESTINATION:" + destination)
                elif target.fragment and target.fragment not in reader.ids:
                    raise ValueError("R89_BROKEN_LOCAL_ANCHOR:" + target.fragment)
        if len(linked_sources) != 6 or set(linked_sources) != allowed_sources:
            raise ValueError("R89_SIX_DISTINCT_NASA_LINKS_REQUIRED:" + name)
        checks[name] = {"sha256": digest((folder / name).read_bytes()),
                        "nasa_source_links": len(linked_sources),
                        "local_links_validated": len(reader.hrefs) - len(linked_sources)}
    for i in range(1, 7):
        rid = f"{i:02}"
        if any(key not in parsed[page].ids for page, key in (
            (PAGES[0], "r89-source-" + rid), (PAGES[1], "r88-" + rid),
            (PAGES[2], "r87-record-" + rid), (PAGES[3], "r85-source-" + rid))):
            raise ValueError("R89_SOURCE_DEEP_LINK_MISSING:" + rid)
    return checks

def hub(records):
    rows = []
    for record in records:
        rid, url = escape(record["id"]), escape(record["url"])
        uncertainty = ("Month-only; day unknown; identity provisional" if rid == "01"
                       else "Day-specific photograph date (not an accident date)")
        rows.append(f"""<article class="source" id="r89-source-{rid}" aria-labelledby="r89-title-{rid}">
<p class="index">SOURCE {rid} / 06 · IMAGE REUSE HOLD</p>
<h3 id="r89-title-{rid}">{escape(record["title"])}</h3>
<p><strong>NASA catalog claim:</strong> {escape(record["catalog"])}</p>
<p><strong>Photograph date:</strong> {escape(record["date"])}</p>
<p><strong>Certainty:</strong> {uncertainty}</p>
<p><strong>Evidence limitation:</strong> {escape(record["limitation"])}</p>
<details><summary>Open documented source custody</summary><p>{escape(record["scope"])}</p>
<p><strong>Rights:</strong> INDIVIDUAL REVIEW REQUIRED; this link is not image permission.</p>
<p class="raw">Official source: {url}</p></details>
<nav class="per-source" aria-label="Evidence views for source {rid}">
<a href="R88_READING_ROOM.html#r88-{rid}">Research Desk · {rid}</a>
<a href="R87_PHOTOGRAPH_DATE_RAIL.html#r87-record-{rid}">Photo-date rail · {rid}</a>
<a href="R85_NASA_SOURCE_REVIEW.html#r85-source-{rid}">Rights review · {rid}</a>
<a href="{url}" target="_blank" rel="noopener noreferrer">NASA primary source · {rid} ↗</a>
</nav></article>""")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Apollo 1 · Integrated Evidence Review · STAGING HOLD</title>
<link rel="stylesheet" href="review_hub_r89.css"></head><body>
<a class="skip" href="#review-records">Skip to the six source records</a>
<div class="wrap"><header><p class="brand">FINAL VESTIGE STUDIOS / APOLLO EVIDENCE STUDIO / ISOLATED REVIEW</p>
<p class="eyebrow">EVIDENCE IS THE EXPERIENCE / CROSS-COMPONENT REVIEW</p>
<h1>Trace every claim<br><em>back to its source.</em></h1>
<p class="lead">One source trail across the Research Reading Room, photograph-date ChronologyRail
and NASA image-rights review. Explore six verified references without invented relationships or a map.</p>
<p class="warning" role="note"><strong>NOT FOR PUBLICATION · STAGING HOLD.</strong>
Zero of six photo-specific rights reviews completed. The proposed S67-19766 identity remains provisional;
the crew portrait has no verified day in January 1967. Both 2017 tribute photos share a date without an
established sequence. Photo dates do not reconstruct the January 27, 1967 fire.</p>
<nav class="primary" aria-label="Three evidence views">
<a href="R88_READING_ROOM.html">Enter Research Reading Room</a>
<a href="R87_PHOTOGRAPH_DATE_RAIL.html">Inspect photograph-date rail</a>
<a href="R85_NASA_SOURCE_REVIEW.html">Inspect photo rights review</a>
<a href="#review-records">Jump to six-source custody</a></nav></header>
<main id="review-records"><h2>Six records, one verified trail.</h2>
<p>The following order is custody-register order, <strong>not accident chronology</strong>.
Each route lands on the same individual record in a separately verified source-controlled page.</p>
<div class="records">{''.join(rows)}</div>
<section class="method" aria-labelledby="method-title"><h2 id="method-title">What the verification does — and does not do</h2>
<p>The build checks the actual Research Desk, generated Evidence Atlas, official NASA page audit,
photograph-date precision and rights-review register before generating this offline review.
Every internal cross-document anchor must resolve. All external source links must match the six
verified NASA destinations or the official NASA policy reference.</p>
<p><strong>Not proven:</strong> permission to reproduce photographs, NASA endorsement, hosted WordPress
compatibility, manual screen-reader performance, physical-device testing, or production Web Vitals.</p>
<p><a href="{POLICY_URL}">NASA Brand Center and media guidance ↗</a></p></section>
</main><footer><strong>STAGING ONLY · REVIEW HOLD</strong> — no images, geo pins, inferred edges,
external scripts, WordPress writes, merges or deployments.</footer></div></body></html>"""

def build(destination: Path):
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("R89_OUTPUT_MUST_BE_EMPTY")
    r88 = module("build_reading_room_r88.py", "r88_r89")
    r85 = module("build_rights_board_r85.py", "r85_r89")
    _, report, groups, uncertain = r88.verified_records()
    board = r85.verify(r85.load_sources())
    if len(board) != 6 or len(groups) != 4 or [r["id"] for r in uncertain] != ["01"]:
        raise ValueError("R89_CUSTODY_AND_DATE_GATE")
    for a, b in zip(report["records"], board):
        if (a["id"], a["catalog"], a["url"], a["date"]) != (
                b["id"], b["catalog"], b["url"], b["date"]):
            raise ValueError("R89_CONCORDANCE_DRIFT")
    allowed = {r["url"] for r in board}
    if len(allowed) != 6:
        raise ValueError("R89_DUPLICATE_NASA_URL")
    with tempfile.TemporaryDirectory(prefix="fv-apollo-r89-") as t:
        stage = Path(t) / "review"
        stage.mkdir()
        r88.build(stage)
        r85.build(stage)
        (stage / "R89_REVIEW_HUB.html").write_text(hub(report["records"]), encoding="utf8")
        (stage / "review_hub_r89.css").write_bytes(CSS.read_bytes())
        audit = audit_pages(stage, allowed)
        receipt = {
            "schema": "fv.apollo.r89.integrated-review.v1", "release": "STAGING_HOLD",
            "publication_approved": False, "photo_rights_cleared": 0,
            "hosted_wordpress_verified": False, "production_cwv_verified": False,
            "images_embedded": 0, "geo_pins": 0, "inferred_edges": 0,
            "nasa_sources": 6, "verified_page_links": audit,
            "desk_atlas_source_sha256": report["sha256"],
            "source_git_blobs": {k: v[1] for k, v in r85.SOURCES.items()},
            "file_sha256": {p.name: digest(p.read_bytes()) for p in sorted(stage.iterdir())
                            if p.is_file()},
        }
        (stage / "R89_INTEGRITY_RECEIPT.json").write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf8")
        destination.mkdir(parents=True, exist_ok=True)
        for p in stage.iterdir():
            if p.is_file():
                shutil.copyfile(p, destination / p.name)
    return receipt

def package(destination: Path, archive: Path):
    payload = {"source/" + name: (ROOT / name).read_bytes() for name in SOURCES}
    payload.update({"built/" + p.name: p.read_bytes() for p in destination.iterdir()
                    if p.is_file()})
    payload["SHA256_MANIFEST.json"] = (json.dumps({
        "release": "STAGING_HOLD", "deployment_allowed": False,
        "files": {name: digest(blob) for name, blob in sorted(payload.items())},
    }, indent=2, sort_keys=True) + "\n").encode()
    archive.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(archive, "w", compression=ZIP_DEFLATED, compresslevel=9) as out:
        for name, blob in sorted(payload.items()):
            item = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            item.compress_type = ZIP_DEFLATED
            item.external_attr = 0o100644 << 16
            item.create_system = 3
            out.writestr(item, blob)
    return digest(archive.read_bytes())

if __name__ == "__main__":
    try:
        output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("dist/apollo-r89")
        build(output)
        if len(sys.argv) > 2:
            print("R89_ARCHIVE_SHA256", package(output, Path(sys.argv[2])))
        print("R89_STAGING_HOLD: 3 reviewed views, 6 NASA records, 0 rights cleared")
    except Exception:
        print("R89_CUSTODY_HOLD: review output withheld", file=sys.stderr)
        sys.exit(1)
