"""Read-only, fail-closed check of independently observed affiliate landing evidence.

No requests, cookies, tracking clicks, purchases, or production integrations.
This tests offer/landing relevance, NOT affiliate eligibility or sales.
"""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlparse


def assess(evidence: dict, today: date, max_age_days: int = 7) -> dict:
    reasons = []
    try:
        observed = date.fromisoformat(evidence["observed_on"])
        source = urlparse(evidence["affiliate_url"])
        destination = urlparse(evidence["resolved_url"])
        expected_host = evidence["expected_merchant_host"].lower()
        offer = evidence["featured_offer"]
        stock = offer["availability"]
        landing_type = evidence["landing_type"]
        cta = evidence["cta_copy"]
    except (KeyError, TypeError, ValueError) as exc:
        return {"status": "HOLD_EVIDENCE_INVALID", "reasons": [str(exc)]}

    if not isinstance(cta, str) or not cta.strip():
        reasons.append("CTA text is missing")
    if source.scheme != "https" or source.hostname != "www.awin1.com":
        reasons.append("Tracked link is not the verified HTTPS Awin origin")
    if destination.scheme != "https" or destination.hostname != expected_host:
        reasons.append("Redirect did not resolve to the expected HTTPS merchant host")
    if (today - observed).days > max_age_days or observed > today:
        reasons.append("Merchant stock evidence is stale or future-dated")
    if stock not in ("in_stock", "sold_out", "unknown"):
        reasons.append("Featured-offer availability is unsupported")
    if landing_type not in ("specific_edition", "catalog", "product"):
        reasons.append("Landing-page type is unsupported")

    if reasons:
        return {"status": "HOLD_ROUTE_OR_EVIDENCE", "reasons": reasons}

    if stock != "in_stock" and landing_type in ("specific_edition", "product"):
        return {"status": "HOLD_OFFER_MATCH", "reasons": [
            "The primary featured item at the tracked destination is not confirmed purchasable",
            "Available adjacent catalog items do not establish purchase availability for the promoted edition",
        ]}

    return {"status": "PASS_ROUTE_ONLY", "reasons": [
        "HTTPS affiliate redirect and a recent, in-stock featured offer were observed",
        "No checkout, purchase, commission, refund, or seller authorization has been verified",
    ]}


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python merchant_route_gate.py evidence.json", file=sys.stderr)
        return 2
    evidence = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    report = assess(evidence, date.fromisoformat(evidence["checked_on"]))
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "PASS_ROUTE_ONLY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
