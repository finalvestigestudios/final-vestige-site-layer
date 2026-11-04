#!/usr/bin/env python3
"""Offline fail-closed Apollo photo source-custody checks. Not a media license or a browser pass."""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent


class CustodyError(ValueError):
    """A source, rights, or isolated-preview boundary was violated."""


class SourceDOM(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self.current = None
        self.rail = []
        self.ctas = []
        self.unsafe = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in {"img", "picture", "source", "video", "audio", "iframe", "form", "object", "embed"}:
            self.unsafe.append(tag)
        if tag == "script" and a.get("src"):
            self.unsafe.append("remote-script")
        if tag == "tr" and a.get("id", "").startswith("photo-source-"):
            if self.current is not None:
                self.unsafe.append("nested-source-row")
            self.current = {"id": a["id"][-2:], "text": [], "links": []}
        if tag == "a":
            href = a.get("href", "")
            self.links.append(href)
            if self.current is not None:
                self.current["links"].append(href)
            if a.get("data-fv-photo-record") is not None:
                self.rail.append((a["data-fv-photo-record"], href))
            if a.get("data-fv-primary-cta") is not None:
                self.ctas.append(href)

    def handle_data(self, data):
        if self.current is not None:
            self.current["text"].append(data)

    def handle_endtag(self, tag):
        if tag == "tr" and self.current is not None:
            row = self.current
            row["text"] = " ".join(" ".join(row["text"]).split())
            self.rows.append(row)
            self.current = None


def require(ok, code):
    if not ok:
        raise CustodyError(code)


def validate(html_text: str, ledger: dict) -> dict:
    require(ledger.get("schema") == "fv.apollo.photo-custody.r116.v1", "SCHEMA")
    records = ledger.get("records")
    require(isinstance(records, list) and len(records) == 6, "SIX_RECORDS")
    ids = [r.get("id") for r in records]
    require(sorted(ids) == ["01", "02", "03", "04", "05", "06"], "RECORD_IDS")
    require(len(set(r.get("official_url") for r in records)) == 6, "UNIQUE_URLS")
    require(ledger.get("rights_review_status") == "SIX_ITEM_ASSESSMENTS_PENDING", "RIGHTS_GATE")

    p = SourceDOM()
    p.feed(html_text)
    require(not p.unsafe, "MEDIA_EMBED_OR_CAPTURE")
    require(len(p.ctas) == 1 and p.ctas[0] == "#classroom-preview", "SINGLE_FREE_CTA")
    require(not any(("payhip" in u.lower() or "checkout" in u.lower() or
                     "stripe.com" in u.lower()) for u in p.links), "MERCHANT_NOT_APPROVED")
    require(len(p.rows) == 6, "SIX_SOURCE_ROWS")
    require(len(set(r["id"] for r in p.rows)) == 6, "DUPLICATE_SOURCE_ROW")
    require(len(p.rail) == 6 and sorted(x[0] for x in p.rail) == sorted(ids), "RAIL_COVERAGE")
    require(all(href == "#photo-source-" + rid for rid, href in p.rail), "RAIL_TARGET")
    require("S67-19766 (provisional)" in html_text and "0/6" in html_text,
            "UNRESOLVED_CATALOG_AND_RIGHTS")

    html_by_id = {r["id"]: r for r in p.rows}
    for r in records:
        rid = r["id"]
        require(r["rights_review"] == "INDIVIDUAL_REVIEW_REQUIRED" and
                r["commercial_photo_reuse"] == "NOT_AUTHORIZED_BY_THIS_LEDGER",
                "UNAUTHORIZED_RIGHTS:" + rid)
        require(r["latitude"] is None and r["longitude"] is None and
                r["relationship_edges"] == [], "INVENTED_GEO:" + rid)
        require(r["catalog_status"] in {"CONFIRMED_ON_CITED_PAGE",
                "UNCONFIRMED_ON_CITED_PAGE"}, "CATALOG_STATUS:" + rid)
        require(rid != "01" or r["catalog_status"] == "UNCONFIRMED_ON_CITED_PAGE",
                "CREW_ID_PREMATURELY_CONFIRMED")
        url = r["official_url"]
        parsed = urlsplit(url)
        require(parsed.scheme == "https" and parsed.netloc == "www.nasa.gov" and
                parsed.path.startswith("/image-detail/") and not parsed.query and not parsed.fragment,
                "NON_NASA_SOURCE:" + rid)
        row = html_by_id[rid]
        require(row["links"] == [url], "SOURCE_URL_MISMATCH:" + rid)
        for needle in (r["catalog_id"], r["display_date"], r["source_credit"]):
            require(isinstance(needle, str) and needle in row["text"],
                    "MISSING_PROVENANCE:" + rid + ":" + str(needle))
    require(sum(r["catalog_status"] == "CONFIRMED_ON_CITED_PAGE" for r in records) == 5,
            "CATALOG_CONFIRMATION_COUNT")
    require("NASA/Kim Shiflett" in html_text and
            "SourceDrawer: media provenance and rights limitations" in html_text,
            "RIGHTS_SOURCE_DRAWER")
    require("@media print{" in html_text and
            "small,.muted{color:#111!important}" in html_text,
            "PRINT_CREDIT_CONTRAST")

    return {
        "classification": "OFFLINE_SOURCE_CONTRACT_ONLY",
        "records": len(p.rows),
        "confirmed_catalog_ids": 5,
        "unconfirmed_catalog_ids": 1,
        "individual_commercial_reuse_reviews": "0/6",
        "browser_axe_wordpress_merchant": "NOT_TESTED",
        "release": "STAGING_HOLD",
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", type=Path, default=ROOT / "landing-preview.html")
    ap.add_argument("--ledger", type=Path, default=ROOT / "nasa-source-custody-r116.json")
    args = ap.parse_args()
    result = validate(args.html.read_text(encoding="utf-8"),
                      json.loads(args.ledger.read_text(encoding="utf-8")))
    print(json.dumps(result, sort_keys=True, indent=2))
