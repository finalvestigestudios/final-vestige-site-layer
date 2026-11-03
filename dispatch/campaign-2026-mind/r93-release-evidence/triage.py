"""Read-only, zero-PII Dispatch production-proof classifier.

This tool cannot approve a send. It accepts only aggregate snapshots and opaque
attestation references. No network, CMS, subscriber lookups or merchant links.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parent
PATH = ROOT / "proofs.json"
HOLD = "HOLD_UNSENT"
MERCHANT = "HOLD_MERCHANT"

REQUIRED_GLOBAL = (
    "qualified_final_vestige_postal_address",
    "native_jetpack_email_preview",
    "actual_received_mime_and_optout",
    "eligible_subscriber_count_reconciled_privately",
    "final_founder_campaign_approval",
)
REQUIRED_COMMERCIAL = (
    "fv_account_affiliate_acceptance",
    "product_specific_email_permission",
    "approved_link_and_creative",
    "approved_published_warmup_guide",
    "current_merchant_checkout_and_refund_terms",
    "product_claims_and_buyer_privacy_review",
)

class InvalidProof(ValueError):
    pass


def load(path: pathlib.Path = PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def review(doc: dict[str, Any]) -> dict[str, Any]:
    """Fail-closed: entirely advisory; never returns SEND/READY authorization."""
    if not isinstance(doc, dict) or doc.get("campaign_state") != "DRAFT_UNSENT":
        raise InvalidProof("Expected an explicitly unsent draft")
    if doc.get("original_master_sha") != "d57ccdba3aee8f065e143e101c2945f4f3d01647":
        raise InvalidProof("Original campaign provenance changed")
    evidence = doc.get("evidence")
    if not isinstance(evidence, dict):
        raise InvalidProof("Missing proof ledger")
    expected = set(REQUIRED_GLOBAL) | set(REQUIRED_COMMERCIAL)
    if set(evidence) != expected:
        raise InvalidProof("Proof keys absent or unexpected")
    for name, record in evidence.items():
        if not isinstance(record, dict) or set(record) != {"verified", "proof_ref"}:
            raise InvalidProof("Invalid proof shape: " + name)
        if type(record["verified"]) is not bool:
            raise InvalidProof("Proof must be true/false, not a string or integer")
        ref = record["proof_ref"]
        if ref is not None and (not isinstance(ref, str) or not re.fullmatch(r"[A-Z0-9][A-Z0-9_-]{3,59}", ref)):
            raise InvalidProof("Proof reference must be a non-identifying opaque code")
        if record["verified"] and ref is None:
            raise InvalidProof("Verified claims need an independently reviewed proof reference")
    # Stored positive flags are review signals, not authorization in this tool.
    counts = doc.get("aggregates")
    if not isinstance(counts, dict) or set(counts) != {"newsletter_total", "newsletter_confirmed", "newsletter_unconfirmed", "stats_email", "stats_wpcom"}:
        raise InvalidProof("Counts must be exact five public aggregate fields")
    if any(type(x) is not int or x < 0 for x in counts.values()):
        raise InvalidProof("Counts must be nonnegative integers")
    if (counts["newsletter_total"], counts["newsletter_confirmed"], counts["newsletter_unconfirmed"], counts["stats_email"], counts["stats_wpcom"]) != (2, 2, 2, 0, 2):
        raise InvalidProof("Observed aggregates changed; collect new evidence before review")
    if doc.get("recipient_count") is not None:
        raise InvalidProof("Eligible recipients not established by aggregate totals")
    if doc.get("mode") != "excerpt" or doc.get("email_new_posts_by_default") is not False:
        raise InvalidProof("Live Jetpack transport drift")
    if doc.get("native_preview_requires_editor_send_toggle") is not True:
        raise InvalidProof("Official preview dependency must remain explicit")
    if doc.get("preview_toggle_authorized") is not False:
        raise InvalidProof("No silent newsletter preview/toggle authorization")
    if doc.get("send_or_publish_authorized") is not False:
        raise InvalidProof("This is not a release authorization")
    issues = doc.get("issues")
    if not isinstance(issues, list) or len(issues) != 6:
        raise InvalidProof("Six original issues required")
    kinds = [issue.get("kind") for issue in issues if isinstance(issue, dict)]
    if kinds != ["editorial", "editorial", "commercial", "editorial", "commercial", "editorial"]:
        raise InvalidProof("Original 4 editorial / 2 merchant reservation changed")
    if any(issue.get("number") != i or issue.get("cta_live") is not False for i, issue in enumerate(issues, 1)):
        raise InvalidProof("No dynamic CTA may be certified live here")
    blockers = [key for key in REQUIRED_GLOBAL if not evidence[key]["verified"]]
    commercial = [key for key in REQUIRED_COMMERCIAL if not evidence[key]["verified"]]
    # Deliberately no API, mail, file or platform action and no SEND_READY result.
    return {
        "status": HOLD,
        "commercial_status": MERCHANT,
        "editorial_issues": [1, 2, 4, 6],
        "commercial_issues": [3, 5],
        "global_blockers": blockers,
        "commercial_blockers": commercial,
        "eligible_recipients": "UNKNOWN",
        "observed_aggregate_count_conflict": True,
        "native_preview_authorization": "NOT_GRANTED",
        "can_publish_or_send": False,
    }


def main() -> int:
    try:
        result = review(load())
        print(json.dumps(result, indent=2, sort_keys=True))
    except (InvalidProof, ValueError, KeyError, TypeError) as error:
        print("HOLD_UNSENT: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
