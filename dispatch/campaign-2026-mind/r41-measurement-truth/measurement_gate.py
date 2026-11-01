#!/usr/bin/env python3
"""Offline, fail-closed measurement/attribution audit for the six unsent Dispatch letters.

There are no APIs, live event collectors, tracking links, emails, subscribers,
WordPress mutations or affiliate activations in this module. Input fixtures
cannot establish actual marketing results.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = Path(__file__).with_name("AUTHENTICATED_READ_ONLY_SNAPSHOT.json")
CHANNEL_METRICS = {
    "jetpack": frozenset(("reported_sent", "reported_delivered", "reported_opens",
                          "email_readmore_clicks", "reported_unsubscribes")),
    "site_analytics": frozenset(("guide_page_views", "onsite_cta_clicks",
                                  "outbound_affiliate_clicks")),
    "merchant": frozenset(("confirmed_orders", "net_commission_usd")),
}
PERSONAL_KEYS = re.compile(
    r"^(?:email|email_address|recipient|recipient_email|recipient_id|"
    r"subscriber_email|subscriber_id|customer_id|ip_address|user_agent|"
    r"phone|phone_number|cookie|cookie_id|password|access_token|"
    r"session_id|click_id|visitor_id|person_id|contact_id|"
    r"transaction_id|auth_token)$", re.I)
EMAIL_LIKE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
TOKEN_URL = re.compile(r"https?://[^\s\"']+[?&](?:token|key|auth|uid|email|"
                       r"customer|subscriber)=", re.I)


class EvidenceError(ValueError):
    """Unsupported, unverifiable or unsafe claim."""


def _read(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise EvidenceError("Expected JSON object")
    return value


def reject_identifiers(value: object) -> None:
    """Never accept PII or tokens from fixture trees."""
    if isinstance(value, dict):
        for key, item in value.items():
            if PERSONAL_KEYS.search(str(key)):
                raise EvidenceError("Personal or secret field")
            reject_identifiers(item)
    elif isinstance(value, list):
        for item in value:
            reject_identifiers(item)
    elif isinstance(value, str):
        if EMAIL_LIKE.search(value) or TOKEN_URL.search(value):
            raise EvidenceError("Personal address or tokenized URL")


def canonical(manifest_path: Path = ROOT / "manifest.json",
              evidence_path: Path = EVIDENCE) -> tuple[list[dict], dict]:
    manifest, evidence = _read(manifest_path), _read(evidence_path)
    reject_identifiers(evidence)
    issues = manifest.get("issues", [])
    if manifest.get("status") != "DRAFT_UNSENT_NO_SCHEDULING":
        raise EvidenceError("Manifest must remain unsent")
    if [r.get("number") for r in issues] != [1, 2, 3, 4, 5, 6]:
        raise EvidenceError("Expected six ordered issues")
    if [r.get("kind") for r in issues] != [
        "editorial", "editorial", "commercial-review-pending",
        "editorial", "commercial-review-pending", "editorial"
    ]:
        raise EvidenceError("Founder 4:2 allocation drift")
    for r in issues:
        if r.get("publish_state") != "hold" or r.get("merchant_affiliate_url") is not None:
            raise EvidenceError("Unapproved issue or affiliate activation")
        cta = r.get("editorial_cta", "")
        if r["number"] in (3, 5):
            if not cta.startswith("[[APPROVED_") or not cta.endswith("_REQUIRED]]"):
                raise EvidenceError("Commercial guide not permitted to activate")
        elif not cta.startswith("https://finalvestige.com/"):
            raise EvidenceError("Editorial CTA no longer first party")
    s = evidence.get("newsletter", {})
    if evidence.get("site") != "finalvestige.com" or evidence.get("source") != "AUTHENTICATED_WORDPRESS_READ_ONLY":
        raise EvidenceError("Wrong site or evidence source")
    if (s.get("enabled") is not True or s.get("auto_new_post_emails") is not False
            or s.get("delivery") != "excerpt" or s.get("recent_sends") != []):
        raise EvidenceError("WordPress setting drift; re-observe")
    if s.get("diagnostic_counters") != {"total": 2, "confirmed": 2, "unconfirmed": 2}:
        raise EvidenceError("Re-observe subscriber diagnostics privately")
    if evidence.get("unique_consent_eligible") != "UNKNOWN" or evidence.get("lifetime_sends") != "UNKNOWN":
        raise EvidenceError("Recent empty send window cannot prove lifetime count or consent")
    proofs = evidence.get("release_evidence", {})
    if not isinstance(proofs, dict) or not proofs or any(v is not False for v in proofs.values()):
        raise EvidenceError("Release proof forged or absent")
    return issues, evidence


def validate_synthetic_aggregate(payload: dict) -> dict:
    """Validate privacy and dimensionality, never platform truth."""
    reject_identifiers(payload)
    if set(payload) != {"edition", "channel", "observed_utc",
                        "evidence_ref", "metrics", "synthetic"}:
        raise EvidenceError("Unexpected fields")
    if type(payload["edition"]) is not int or payload["edition"] not in range(1, 7):
        raise EvidenceError("Edition outside pilot")
    channel = payload["channel"]
    if channel not in CHANNEL_METRICS:
        raise EvidenceError("Unknown platform")
    if payload["synthetic"] is not True:
        raise EvidenceError("Live observations require authenticated independent verification")
    if not isinstance(payload["evidence_ref"], str) or not re.fullmatch(
            r"synthetic:[a-z0-9_-]{3,48}", payload["evidence_ref"]):
        raise EvidenceError("Synthetic source label required")
    try:
        dt = datetime.fromisoformat(payload["observed_utc"].replace("Z", "+00:00"))
        if dt.tzinfo is None:
            raise ValueError()
    except (ValueError, TypeError, AttributeError):
        raise EvidenceError("Timestamp must include timezone") from None
    metrics = payload["metrics"]
    if not isinstance(metrics, dict) or not metrics or not set(metrics).issubset(CHANNEL_METRICS[channel]):
        raise EvidenceError("Metric not supported by source")
    for name, number in metrics.items():
        if name == "net_commission_usd":
            if type(number) not in (int, float) or not 0 <= number <= 1_000_000:
                raise EvidenceError("Invalid synthetic commission")
        elif type(number) is not int or not 0 <= number <= 1_000_000:
            raise EvidenceError("Invalid aggregate count")
    if channel == "jetpack":
        sent, delivered = metrics.get("reported_sent"), metrics.get("reported_delivered")
        if sent is not None and delivered is not None and delivered > sent:
            raise EvidenceError("Delivered exceeds sent")
        if delivered == 0 and metrics.get("email_readmore_clicks", 0) > 0:
            raise EvidenceError("Impossible clicks")
    return {"edition": payload["edition"], "channel": channel,
            "result": "STRUCTURE_ONLY_SYNTHETIC_NOT_PLATFORM_PROOF",
            "privacy": "NO_ROW_IDENTIFIERS", "metrics": metrics}


def cautious_ratio(numerator: int | None, denominator: int | None) -> dict:
    if (type(numerator) is not int or type(denominator) is not int or
            denominator <= 0 or numerator < 0 or numerator > denominator):
        return {"state": "UNAVAILABLE", "rate": None}
    if denominator < 30:
        return {"state": "SUPPRESSED_SMALL_DENOMINATOR", "rate": None}
    return {"state": "ILLUSTRATIVE_NOT_OBSERVED", "rate": round(numerator / denominator, 4)}


def report(manifest_path: Path = ROOT / "manifest.json",
           evidence_path: Path = EVIDENCE) -> dict:
    issues, evidence = canonical(manifest_path, evidence_path)
    return {
        "program": "FV_DISPATCH_2026_SIX_ISSUE_PILOT",
        "mode": "OFFLINE_READ_ONLY_NO_SEND_NO_TRACKING",
        "source_observed_utc": evidence["observed_utc"],
        "founder_mix": {"editorial": 4, "commercial": 2},
        "platform_reality": {
            "recent_send_entries": 0,
            "lifetime_sends": "UNKNOWN_NOT_ZERO",
            "unique_consent_eligible": "UNKNOWN",
            "subscriber_counts": "NONADDITIVE_2_2_2",
            "native_format": "EXCERPT_READ_MORE_NOT_DIRECT_CTA",
            "welcome_receipt": "UNVERIFIED",
            "preheader_rendering": "UNVERIFIED",
        },
        "attribution": {
            "email_read_more_distinct_from_onsite_cta": True,
            "guide_view_does_not_prove_purchase": True,
            "outbound_click_does_not_prove_sale": True,
            "opens_can_be_prefetched": True,
            "tracking_deployed": False,
            "recipient_matching_authorized": False,
        },
        "metric_definitions": {k: sorted(v) for k, v in CHANNEL_METRICS.items()},
        "observed_edition_metrics": "NONE_VERIFIED",
        "issues": [
            {
                "edition": i["number"], "kind": i["kind"],
                "cta": i["editorial_cta"] if i["kind"] == "editorial" else "UNPUBLISHED_HOLD",
                "sends": "UNKNOWN_PER_EDITION", "clicks": "UNKNOWN",
                "orders": "UNKNOWN_NOT_ZERO", "rates": "NOT_COMPUTED",
                "release": "HOLD_UNSENT" if i["kind"] == "editorial"
                           else "HOLD_UNSENT_AND_MERCHANT"
            } for i in issues
        ],
        "founder_final_send_approval": False,
        "all_six_held": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    outcome = report()
    if args.json:
        print(json.dumps(outcome, indent=2, ensure_ascii=False))
    else:
        print("R41: Six UNSENT draft letters (4 editorial, 2 commercial).")
        print("No recent send entries; lifetime totals and consent audience UNKNOWN.")
        print("No verified campaign performance, attribution, sales, or send approval.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
