"""Read-only Jetpack audience-count and release-proof classifier.

This module never accesses subscribers, sends email, or treats summary counts as
consent. Synthetic inputs only; no email addresses or private identifiers.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Snapshot:
    total: int
    confirmed: int
    unconfirmed: int
    wpcom_followers: int
    direct_email_followers: int
    auto_send: bool
    newsletter_enabled: bool
    eligible_inboxes: Optional[int] = None
    eligible_source: Optional[str] = None


def classify(snapshot: Snapshot) -> dict:
    counts = (snapshot.total, snapshot.confirmed, snapshot.unconfirmed,
              snapshot.wpcom_followers, snapshot.direct_email_followers)
    if any(type(value) is not int or value < 0 for value in counts):
        raise ValueError("Counts must be nonnegative integers")
    if snapshot.eligible_inboxes is not None and (
        type(snapshot.eligible_inboxes) is not int or snapshot.eligible_inboxes < 0
    ):
        raise ValueError("Eligible count must be a nonnegative integer")
    if snapshot.eligible_inboxes is not None and snapshot.eligible_source != "provider_eligibility_attestation":
        raise ValueError("Eligible count requires authoritative private provider proof")
    if snapshot.eligible_inboxes is None and snapshot.eligible_source is not None:
        raise ValueError("Do not cite an eligibility source without a measured count")
    if type(snapshot.auto_send) is not bool or type(snapshot.newsletter_enabled) is not bool:
        raise ValueError("Toggle values must be booleans")
    inconsistent = snapshot.confirmed + snapshot.unconfirmed > snapshot.total
    return {
        "total_displayed": snapshot.total,
        "confirmed_displayed": snapshot.confirmed,
        "unconfirmed_displayed": snapshot.unconfirmed,
        "classification_overlap_or_denominator_mismatch": inconsistent,
        "reader_followers": snapshot.wpcom_followers,
        "direct_email_followers": snapshot.direct_email_followers,
        "eligible_inboxes": snapshot.eligible_inboxes,
        "email_eligibility_verified": snapshot.eligible_inboxes is not None,
        "may_infer_consent_from_summary": False,
        "may_infer_welcome_received_from_settings": False,
        "safe_to_send": False,
        "auto_send_off": not snapshot.auto_send,
        "newsletter_enabled": snapshot.newsletter_enabled,
        "next_private_proof": "provider-level confirmed, subscribed, email-enabled, unsuppressed unique audience snapshot; no public identities",
    }


def commercial_release(evidence: dict) -> dict:
    """Fail closed unless every independent named proof is present; never sends."""
    common = ("founder_final_approval", "provider_consent", "welcome_delivery",
              "native_jetpack_preview", "fv_postal_address", "working_unsubscribe")
    partner = ("partner_acceptance", "email_permission", "sku_link",
               "sku_checkout_terms", "live_vetted_guide", "adjacent_disclosure")
    required = common + partner
    valid = all(isinstance(evidence.get(key), dict)
                and evidence[key].get("verified") is True
                and isinstance(evidence[key].get("opaque_proof_id"), str)
                and len(evidence[key]["opaque_proof_id"].strip()) >= 12
                for key in required)
    return {"evidence_complete": valid,
            "missing": [key for key in required if not (
                isinstance(evidence.get(key), dict)
                and evidence[key].get("verified") is True
                and isinstance(evidence[key].get("opaque_proof_id"), str)
                and len(evidence[key]["opaque_proof_id"].strip()) >= 12)],
            "safe_to_send": False,
            "decision": "FOUNDER_RELEASE_REVIEW_REQUIRED" if valid else "HOLD_MERCHANT_AND_MAIL"}
