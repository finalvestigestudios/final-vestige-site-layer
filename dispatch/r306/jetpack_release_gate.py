"""Offline, evidence-only Jetpack post/email readiness gate. NO network, sender or credentials.

Do NOT import this as a WordPress publishing integration. A green preview capability
is never a send authorization. Publisher release requires human approval.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Any

EDITORIAL = {1, 2, 4, 6}
COMMERCIAL = {3, 5}


@dataclass(frozen=True)
class Decision:
    issue: int
    kind: str
    status: str
    reasons: tuple[str, ...]
    post_email_risk: str
    sender_authorized: bool = False
    verified_paid_orders: int | None = None
    realized_net_revenue: int | None = None

    def as_dict(self):
        return vars(self).copy()


def evaluate(issue: int, settings: Mapping[str, Any], proof: Mapping[str, Any]):
    """Evaluate a proposed *post-based* Jetpack email without sending or writing.

    An absent or invalid proof always fails closed. Treat this as a review aid,
    not a substitute for founder-controlled production approvals.
    """
    if isinstance(issue, bool) or not isinstance(issue, int) or issue not in EDITORIAL | COMMERCIAL:
        raise ValueError("Unknown six-issue campaign edition")
    if not isinstance(settings, Mapping) or not isinstance(proof, Mapping):
        raise TypeError("Expected mappings")
    commercial = issue in COMMERCIAL
    reasons = []
    def need(condition: bool, code: str):
        if not condition:
            reasons.append(code)

    # Snapshot alone does NOT prove that an individual post cannot email.
    need(settings.get("subscriptions") is True, "newsletter_disabled")
    need(settings.get("email_content_format") == "full", "rendering_contract_not_verified")
    need(settings.get("email_new_posts_by_default") is False,
         "global_auto_send_default_must_remain_off")
    need(proof.get("master_original_unchanged") is True,
         "original_campaign_integrity_not_proven")
    need(proof.get("founder_reviewed_exact_issue") is True,
         "founder_creative_review_missing")
    need(proof.get("subscriber_status_eligible_proven") is True,
         "recipient_eligibility_unverified")
    need(proof.get("subscriber_consent_proven") is True,
         "subscriber_consent_unverified")
    need(proof.get("welcome_receipt_proven") is True,
         "welcome_delivery_unverified")
    need(proof.get("fieldbook_access_proven") is True,
         "fieldbook_delivery_unverified")
    need(proof.get("native_jetpack_preview_verified") is True,
         "native_preview_unverified")
    need(proof.get("received_email_mime_verified") is True,
         "real_received_mime_unverified")
    need(proof.get("fv_postal_address_in_received_email") is True,
         "publisher_postal_address_unverified")
    need(proof.get("functional_unsubscribe_in_received_email") is True,
         "unsubscribe_not_verified")
    need(proof.get("subject_matches_actual_post_title") is True,
         "subject_not_checked_against_post_title")
    need(proof.get("preheader_in_received_email_verified") is True,
         "preheader_not_native_verified")
    need(proof.get("destination_live_and_claim_checked") is True,
         "first_party_destination_unverified")
    need(proof.get("single_primary_cta_verified") is True,
         "primary_cta_not_checked")

    # Publish is an irreversible dispatch opportunity; do not infer from ability to preview.
    post_state = proof.get("post_state")
    toggle = proof.get("post_send_subscription")
    if post_state != "unpublished_draft":
        reasons.append("unpublished_wordpress_post_not_verified")
    if toggle is not False:
        reasons.append("post_send_toggle_must_be_off_during_review")
    if commercial:
        for label, key in (
            ("publisher_specific_affiliate_approval_missing", "publisher_approval_verified"),
            ("merchant_email_promotion_rights_missing", "product_email_permission_verified"),
            ("issued_earning_link_missing", "issued_earning_link_verified"),
            ("first_party_warmup_guide_not_live", "approved_guide_live_verified"),
            ("merchant_claim_review_missing", "product_specific_claim_review_current"),
            ("merchant_checkout_terms_unverified", "price_refund_format_checked"),
            ("near_offer_disclosure_missing", "adjacent_commercial_disclosure_verified"),
        ):
            need(proof.get(key) is True, label)

    # This code intentionally provides no send operation or automatic approval path.
    need(proof.get("founder_final_campaign_send_approval") is True,
         "founder_final_send_approval_missing")
    need(proof.get("approved_audience_and_schedule") is True,
         "final_audience_schedule_approval_missing")

    # Evidence about currently published posts is not proof of future delivery.
    if post_state == "published" and toggle is True:
        risk = "POSSIBLE_DISPATCH_ALREADY_OCCURRED_CHECK_PROVIDER"
    elif post_state in {"unpublished_draft", "scheduled"} and toggle is True:
        risk = "WOULD_EMAIL_ON_NEW_POST_PUBLICATION"
    elif toggle is False:
        risk = "POST_OPTED_OUT_NO_SEND_EXPECTED"
    else:
        risk = "UNKNOWN_FAIL_CLOSED"
    return Decision(issue, "commercial" if commercial else "editorial",
                    "HOLD_MERCHANT" if commercial and any("affiliate" in r or "merchant" in r or "warmup" in r for r in reasons)
                    else "HOLD_UNSENT" if reasons else "READY_FOR_FOUNDER_MANUAL_RELEASE_CHECK",
                    tuple(reasons), risk)


def evaluate_campaign(settings: Mapping[str, Any], by_issue: Mapping[int, Mapping[str, Any]]):
    return [evaluate(i, settings, by_issue.get(i, {})).as_dict() for i in range(1, 7)]
