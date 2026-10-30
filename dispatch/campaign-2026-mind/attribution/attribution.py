"""Offline, aggregate-only Dispatch attribution. NO network, no sender, no collection."""
from __future__ import annotations
import argparse
import csv
import html
import io
import json
import re
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parent
COLUMNS = ["issue", "wp_recipients", "wp_unique_email_clickers", "first_party_page_views",
           "outbound_merchant_clicks", "verified_merchant_purchases",
           "send_approval_ref", "merchant_report_ref"]
PRIVATE_FIELDS = re.compile(r"email|address|name|phone|ip|cookie|user.?id|order.?id|token|secret|key", re.I)
PROOF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/#-]{7,90}$")


def plan() -> dict:
    data = json.loads((ROOT / "plan.json").read_text(encoding="utf-8"))
    records = data["editions"]
    if [v["issue"] for v in records] != ["01", "02", "03", "04", "05", "06"]:
        raise ValueError("six fixed campaign editions required")
    for v in records:
        if v["merchant_affiliate_url"] is not None or v["state"] != "HOLD_UNSENT":
            raise ValueError("commercial activation or live send is forbidden")
        if v["issue"] in ("03", "05"):
            if v["guide_url"] is not None or v["kind"] != "commercial_review_pending":
                raise ValueError("commercial guides must remain blocked")
        elif v["kind"] != "editorial" or not v["guide_url"].startswith("https://finalvestige.com/"):
            raise ValueError("editorial URLs must be published first-party routes")
    return data


def proposed_first_party_url(issue: str) -> str | None:
    """A *proposal*, not a deployed link, tracking mechanism or merchant redirect."""
    rec = next((x for x in plan()["editions"] if x["issue"] == issue), None)
    if rec is None:
        raise ValueError("unknown issue")
    if rec["guide_url"] is None:
        return None
    parts = urlsplit(rec["guide_url"])
    if parts.scheme != "https" or parts.netloc != "finalvestige.com" or not parts.path.startswith("/") or parts.fragment:
        raise ValueError("unapproved outbound route")
    args = dict(parse_qsl(parts.query, keep_blank_values=True))
    if any(x.startswith("utm_") for x in args):
        raise ValueError("no inherited UTM parameters")
    args.update(utm_source="the_dispatch", utm_medium="email", utm_campaign="mind_archive_pilot",
                utm_content=f"issue_{issue}")
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(args), ""))


def _count(raw: str, field: str, *, optional: bool = False) -> int | None:
    raw = raw.strip()
    if raw == "" and optional:
        return None
    if not re.fullmatch(r"0|[1-9][0-9]{0,7}", raw):
        raise ValueError(f"{field}: expected nonnegative integer, not estimate")
    return int(raw)


def _proof(value: str, field: str, *, required: bool) -> str | None:
    value = value.strip()
    if not value and not required:
        return None
    if not PROOF.fullmatch(value) or "@" in value or "?" in value:
        raise ValueError(f"{field}: private/internal opaque receipt only, no names/emails/URLs")
    if value.lower().startswith(("http", "mailto", "test", "fake", "example")):
        raise ValueError(f"{field}: do not treat links or synthetic labels as approvals")
    return value


def parse_rows(payload: str) -> list[dict]:
    """Accept only individually verified aggregate exports; never raw subscribers/orders."""
    reader = csv.DictReader(io.StringIO(payload))
    if reader.fieldnames is None:
        return []
    if reader.fieldnames != COLUMNS or any(PRIVATE_FIELDS.search(col) for col in reader.fieldnames if col not in COLUMNS):
        raise ValueError("unexpected data column; raw PII and order IDs prohibited")
    if len(set(reader.fieldnames)) != len(reader.fieldnames):
        raise ValueError("duplicate columns")
    known = {v["issue"]: v for v in plan()["editions"]}
    seen = set()
    out = []
    for line in reader:
        if None in line or line.get(None) is not None:
            raise ValueError("unexpected column/value")
        issue = line["issue"].strip()
        if issue not in known or issue in seen:
            raise ValueError("unknown or duplicate issue")
        seen.add(issue)
        recipients = _count(line["wp_recipients"], "wp_recipients")
        clickers = _count(line["wp_unique_email_clickers"], "wp_unique_email_clickers")
        views = _count(line["first_party_page_views"], "first_party_page_views", optional=True)
        outbound = _count(line["outbound_merchant_clicks"], "outbound_merchant_clicks", optional=True)
        sales = _count(line["verified_merchant_purchases"], "verified_merchant_purchases", optional=True)
        approval = _proof(line["send_approval_ref"], "send_approval_ref", required=True)
        report_ref = _proof(line["merchant_report_ref"], "merchant_report_ref", required=sales is not None)
        if clickers > recipients:
            raise ValueError("unique email clickers cannot exceed WP recipient count")
        if known[issue]["kind"] == "editorial" and (outbound not in (None, 0) or sales not in (None, 0)):
            raise ValueError("merchant attribution forbidden for editorial-only editions")
        if (outbound is not None or sales is not None) and known[issue]["kind"] == "commercial_review_pending":
            if report_ref is None:
                raise ValueError("merchant observations need independent proof; no click-to-sale inference")
        out.append(dict(issue=issue, wp_recipients=recipients, wp_unique_email_clickers=clickers,
                        first_party_page_views=views, outbound_merchant_clicks=outbound,
                        verified_merchant_purchases=sales, send_approval_ref=approval,
                        merchant_report_ref=report_ref))
    return out


def summarize(rows: list[dict]) -> dict:
    verified = {x["issue"]: x for x in rows}
    items = []
    for v in plan()["editions"]:
        x = verified.get(v["issue"])
        n = x["wp_recipients"] if x else None
        k = x["wp_unique_email_clickers"] if x else None
        items.append(dict(issue=v["issue"], subject=v["subject"], kind=v["kind"],
                          state="OBSERVED_AGGREGATE_NEEDS_HUMAN_AUDIT" if x else "NO_APPROVED_SEND_DATA",
                          wp_recipients=n, unique_email_clickers=k,
                          descriptive_click_rate=f"{100*k/n:.1f}%" if n is not None and n>=20 else None,
                          first_party_views=x["first_party_page_views"] if x else None,
                          outbound_merchant_clicks=x["outbound_merchant_clicks"] if x else None,
                          verified_merchant_purchases=x["verified_merchant_purchases"] if x else None))
    return dict(status="PRIVATE_OFFLINE_PREVIEW_ONLY", privacy="NO_PERSON_LEVEL_DATA", observed_issues=len(rows),
                caveat="Recipients are not necessarily delivered; site views and merchant clicks may be different cohorts; never infer sales from clicks or statistical lift from tiny samples.", issues=items)


def html_report(report: dict) -> str:
    rows = []
    for x in report["issues"]:
        def cell(value):
            return html.escape("Not measured" if value is None else str(value))
        rows.append("<tr><th scope='row'>"+cell(x["issue"])+"</th><td>"+cell(x["subject"])+"</td>"+
                    "<td>"+cell(x["wp_recipients"])+"</td><td>"+cell(x["unique_email_clickers"])+"</td>"+
                    "<td>"+cell(x["descriptive_click_rate"])+"</td><td>"+cell(x["verified_merchant_purchases"])+"</td></tr>")
    return ("<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>"
            "<title>The Dispatch — measurement readiness (offline)</title><style>body{background:#10171b;color:#eee6d8;font:17px/1.6 Georgia,serif;margin:auto;max-width:1140px;padding:clamp(16px,4vw,60px)}h1{font-size:clamp(2.1rem,5vw,4rem);line-height:1.1} .eyebrow{color:#e0b978;letter-spacing:.13em;text-transform:uppercase;font:700 12px Arial,sans-serif} .scroll{overflow-x:auto}table{width:100%;border-collapse:collapse;min-width:720px}th,td{border-bottom:1px solid #415058;padding:.8rem;text-align:left}th{color:#f5cf8e}tr:focus-within{outline:2px solid #f5cf8e}p{max-width:78ch} .note{border-left:3px solid #f5cf8e;padding:8px 18px;background:#1e2c30} @media(prefers-reduced-motion:reduce){*{scroll-behavior:auto}}</style></head><body>"
            "<p class='eyebrow'>Final Vestige Studios / The Dispatch / private review</p><h1>Measure what actually happened.</h1>"
            "<p class='note'>No sends, sales or conversions are asserted here. This is an offline review tool, not a live analytics integration.</p>"
            "<p>WordPress recipients do not establish delivered emails. Email clickers, site views, outbound merchant clicks and partner-verified purchases are separate observations. Small audiences do not justify conversion-rate promises or significance tests.</p>"
            "<div class='scroll' role='region' aria-label='Email campaign aggregate metrics' tabindex='0'><table><caption>Six draft editions: verified aggregate counts only</caption>"
            "<thead><tr><th scope='col'>Edition</th><th scope='col'>Subject</th><th scope='col'>WP recipients</th><th scope='col'>Unique email clickers</th><th scope='col'>Descriptive click rate (N ≥ 20)</th><th scope='col'>Merchant-confirmed purchases</th></tr></thead><tbody>"
            +"".join(rows)+"</tbody></table></div><p>Inspire3 offers #03/#05 are currently held pending account-specific partner permission, public guide publication and legal approval. No raw subscriber or buyer data are accepted.</p></body></html>")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--aggregate-csv", type=Path, help="local hand-reviewed aggregate-only CSV; no PII")
    p.add_argument("--html", type=Path, help="output local static review page (never uploads/publishes)")
    p.add_argument("--proposed-urls", action="store_true", help="print first-party proposed UTM links only")
    args = p.parse_args()
    if args.proposed_urls:
        print(json.dumps({f"issue_{i:02d}": proposed_first_party_url(f"{i:02d}") for i in range(1, 7)}, indent=2))
        return
    rows = parse_rows(args.aggregate_csv.read_text(encoding="utf-8-sig")) if args.aggregate_csv else []
    report = summarize(rows)
    if args.html:
        args.html.write_text(html_report(report), encoding="utf-8")
        print(f"Wrote offline review: {args.html}")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
