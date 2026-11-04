"""Offline, privacy-minimal QA for commercial CTA and attribution contracts.

Consumes an already-authorized, sanitized HTML snapshot. NEVER fetches a website,
executes scripts, records visitor identifiers, or calls a checkout. A finding
about DOM/source order is NOT browser, merchant, conversion or revenue proof.
"""
from __future__ import annotations
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

AFFILIATE_HOSTS = {"www.awin1.com", "awin1.com"}
MERCHANT_HOSTS = {"payhip.com", "www.payhip.com"}


def _host(href: str) -> str:
    return urlsplit(href).hostname or ""


class LinkAndDisclosureParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links: list[dict] = []
        self.disclosures: list[int] = []
        self.subscribe_blocks = 0
        self._tag_index = 0

    def handle_starttag(self, tag: str, attrs):
        self._tag_index += 1
        a = dict(attrs)
        classes = set((a.get("class") or "").split())
        if "wp-block-jetpack-subscriptions" in classes:
            self.subscribe_blocks += 1
        if tag == "p" and "fv-affiliate-note" in classes:
            self.disclosures.append(self._tag_index)
        if tag != "a":
            return
        href = a.get("href") or ""
        host = _host(href)
        rel = set((a.get("rel") or "").split())
        self.links.append({
            "position": self._tag_index,
            "is_affiliate": host in AFFILIATE_HOSTS or "sponsored" in rel,
            "is_payhip": host in MERCHANT_HOSTS or host.endswith(".payhip.com"),
            "is_focus": urlsplit(href).path.rstrip("/") == "/focus",
            "has_sponsored_rel": "sponsored" in rel,
        })


def audit_html(html: str) -> dict:
    p = LinkAndDisclosureParser()
    p.feed(html)
    affiliates = [x for x in p.links if x["is_affiliate"]]
    payhip = [x for x in p.links if x["is_payhip"]]
    first_disclosure = min(p.disclosures, default=None)
    # A structural audit only; neither rendering, visibility nor compliance is proven.
    before = sum(first_disclosure is None or x["position"] < first_disclosure for x in affiliates)
    return {
        "evidence_level": "HTML_SOURCE_ONLY_NOT_BROWSER_OR_SALE",
        "affiliate_cta_count": len(affiliates),
        "affiliate_ctas_before_first_inline_disclosure": before,
        "affiliate_ctas_missing_sponsored_rel": sum(not x["has_sponsored_rel"] for x in affiliates),
        "payhip_cta_count": len(payhip),
        "focus_link_count": sum(x["is_focus"] for x in p.links),
        "native_subscription_block_nodes": p.subscribe_blocks,
        "merchant_checkout_tested": False,
        "merchant_confirmed_orders": None,
        "realized_net_revenue": None,
        "genuine_signup_confirmation_verified": False,
    }


def audit_campaign_utm(url: str) -> dict:
    """Validate *proposed* per-asset campaign URL; no network or attribution claim."""
    q = parse_qs(urlsplit(url).query, keep_blank_values=True)
    expected = ("utm_source", "utm_medium", "utm_campaign", "utm_content")
    issues = [f"missing_or_duplicated_{k}" for k in expected if len(q.get(k, [])) != 1 or not q[k][0]]
    if q.get("utm_medium", [None]) != ["organic_social"]:
        issues.append("medium_must_be_organic_social")
    for k in q:
        if k.lower() in {"email", "phone", "user_id", "visitor_id", "customer_id"}:
            issues.append("PII_query_key_present")
    if urlsplit(url).hostname not in {"finalvestige.com", "www.finalvestige.com"}:
        issues.append("landing_host_not_finalvestige")
    return {"valid": not issues, "issues": sorted(set(issues)), "attribution_verified": False}


def commercial_outcome_status(*, external_clicks: int, leads: int, verified_paid_orders=None, verified_net_revenue=None) -> dict:
    """Do not promote clicks, newsletter counts or pageviews into a paid outcome."""
    if verified_paid_orders is None or verified_net_revenue is None:
        return {"paid_orders": None, "net_revenue": None, "status": "NOT_OBSERVABLE"}
    if verified_paid_orders < 0 or verified_net_revenue < 0:
        raise ValueError("nonnegative reconciled values required")
    return {"paid_orders": verified_paid_orders, "net_revenue": verified_net_revenue, "status": "SOURCE_REPORTED_ONLY"}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("html", type=Path, help="Local, sanitized HTML snapshot; no URL fetch")
    ap.add_argument("--proposed-utm", help="Optional synthetic campaign URL to validate")
    args = ap.parse_args()
    report = audit_html(args.html.read_text(encoding="utf-8"))
    if args.proposed_utm:
        report["proposed_utm"] = audit_campaign_utm(args.proposed_utm)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
