#!/usr/bin/env python3
"""Privacy-safe, read-only promise alignment audit. Never an email authorization."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
CAMPAIGN = ROOT.parent

MANDATORY_PROOFS = (
    "unique_eligible_audience",
    "native_mime",
    "actual_unsubscribe",
    "valid_publisher_address",
    "zen12_email_permission",
    "total_focus_email_permission",
    "approved_offer_guides",
    "founder_final_approval",
)
EXPECTED_KIND = [
    "editorial", "editorial", "commercial-review-pending",
    "editorial", "commercial-review-pending", "editorial",
]


def audit(snapshot: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    """Return bounded factual findings without subscriber identifiers or ready/sent assertions."""
    findings: list[str] = []
    hard_stops: list[str] = []
    p = snapshot.get("pages", {})
    d = p.get("dispatch", {})
    f = p.get("focus", {})
    w = snapshot.get("welcome", {})
    n = snapshot.get("newsletter", {})
    pilot = snapshot.get("pilot", {})
    proofs = snapshot.get("proof_flags", {})
    issues = manifest.get("issues", [])

    if not d.get("published") or not f.get("published"):
        hard_stops.append("source-page-status-unknown")
    if not f.get("commission_notice_present") or "commission" not in f.get("near_form_promise", "").lower():
        hard_stops.append("focus-commission-promise-missing-or-drifted")
    if not d.get("commission_notice_present"):
        findings.append("dispatch-opt-in-commission-language-absent")
    if d.get("commission_notice_present") != f.get("commission_notice_present"):
        findings.append("same-list-opt-in-promise-asymmetry")
    if not w.get("commission_notice_present"):
        findings.append("welcome-omits-commercial-evaluation-notice")
    if not w.get("actual_receipt_verified"):
        hard_stops.append("received-fieldbook-welcome-unverified")
    if n.get("counts", {}).get("total") == 2 and n.get("counts", {}).get("confirmed") == 2 and n.get("counts", {}).get("unconfirmed") == 2:
        findings.append("nonadditive-counts-2-2-2-no-unique-audience-inference")
    if n.get("unique_consent_eligible") != "VERIFIED":
        hard_stops.append("unique-subscriber-eligibility-unverified")
    if n.get("auto_new_post_emails") is False and n.get("manual_per_post_email_possible") is True:
        findings.append("auto-email-default-off-does-not-preclude-manual-per-post-send")
    if n.get("content_format") == "excerpt":
        hard_stops.append("actual-excerpt-email-render-unverified")
    if not n.get("real_received_email_verified"):
        hard_stops.append("real-received-message-unverified")
    if not n.get("valid_publisher_postal_address_verified"):
        hard_stops.append("publisher-postal-address-unverified")
    if not n.get("received_email_unsubscribe_verified"):
        hard_stops.append("unsubscribe-in-received-message-unverified")
    if n.get("can_send") is True:
        findings.append("provider-sendable-is-not-editorial-or-legal-authorization")
    if len(issues) != 6 or [i.get("kind") for i in issues] != EXPECTED_KIND:
        hard_stops.append("canonical-four-editorial-two-commercial-structure-drift")
    if any(i.get("publish_state") != "hold" or i.get("merchant_affiliate_url") is not None for i in issues):
        hard_stops.append("canonical-manifest-release-or-merchant-link-drift")
    if pilot.get("all_unsent") is not True:
        hard_stops.append("pilot-unsent-status-drift")
    if set(proofs) != set(MANDATORY_PROOFS):
        hard_stops.append("proof-schema-missing-or-extra")
    for field in MANDATORY_PROOFS:
        if proofs.get(field) is not True:
            hard_stops.append("missing-proof:" + field)
    if snapshot.get("sensitive_data_present") is not False:
        hard_stops.append("snapshot-sensitive-data-status-invalid")
    if snapshot.get("release_state") != "HOLD_UNSENT_AND_03_05_HOLD_MERCHANT":
        hard_stops.append("snapshot-release-state-drift")

    # Even a future record with all flags true requires separately approved, live
    # WordPress/merchant evidence, a real received email and final human sign-off.
    # No automated static snapshot is competent to remove the sending hold.
    hard_stops.append("static-snapshot-never-authorizes-sending")
    return {
        "audit_type": "READ_ONLY_SOURCE_CAPTURE_NOT_A_LIVE_DELIVERY_TEST",
        "site_id": snapshot.get("site_id"),
        "observed_utc": snapshot.get("observed_utc"),
        "findings": sorted(set(findings)),
        "hard_stops": sorted(set(hard_stops)),
        "release_decision": "HOLD_UNSENT",
        "commercial_03_05": "HOLD_MERCHANT",
        "ready_for_send": False,
        "subscriber_addresses_examined": False,
        "new_list_created": False,
        "production_changed": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Read-only Dispatch promise and hold audit")
    ap.add_argument("--snapshot", type=Path, default=ROOT / "observations.json")
    ap.add_argument("--manifest", type=Path, default=CAMPAIGN / "manifest.json")
    ns = ap.parse_args()
    # No network calls, no private data, no email.
    s = json.loads(ns.snapshot.read_text(encoding="utf-8"))
    m = json.loads(ns.manifest.read_text(encoding="utf-8"))
    print(json.dumps(audit(s, m), indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
