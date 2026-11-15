"""Pure, offline Final Vestige Focus/Dispatch consent QA; performs NO I/O or event emission.

This module does not authenticate a Jetpack subscriber, contact a subscriber,
produce an actual confirmed_signup event, or assert that any purchase occurred.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Mapping

# Observed in the live /focus/ WordPress page's fvf-gift-v2 on 2026-11-12.
CURRENT_QUERY_DENYLIST = frozenset({
    "invalid_email", "error", "blocked_email", "opted_out", "blocked"
})


@dataclass(frozen=True)
class Status:
    signal: str
    permitted_interpretation: str
    event: None = None  # This offline helper NEVER emits a signup or purchase.


def existing_gift_visibility(subscribe: str | None, is_subscriber_class: bool) -> bool:
    """Reproduce the live JS's permissive query/class display decision, not consent."""
    return bool(subscribe and subscribe not in CURRENT_QUERY_DENYLIST) or bool(is_subscriber_class)


def classify_client_signal(signal: str, value: object = None) -> Status:
    """A client-side display, interaction or URL query cannot confirm a subscriber."""
    allowed = {"subscribe_query", "is_subscriber_css", "form_submit",
               "fieldbook_click", "gift_visible", "page_visit", "email_open",
               "newsletter_click", "reader_follow", "welcome_configured"}
    if signal not in allowed:
        return Status("UNRECOGNIZED_CLIENT_SIGNAL", "NO_CONFIRMED_SIGNUP")
    return Status("CLIENT_ONLY", "NO_CONFIRMED_SIGNUP")


def provider_transition_candidate(evidence: Mapping[str, object]) -> Status:
    """Strict contract, not proof. Must be authenticated by Claude/provider outside it."""
    if not isinstance(evidence, Mapping):
        return Status("INVALID_PROVIDER_EVIDENCE", "NO_CONFIRMED_SIGNUP")
    # Do not accept identifiable subscriber data in client/log/PR evidence.
    disallowed = {"email", "email_address", "name", "ip", "ip_address", "subscriber_id", "user_id", "address"}
    if any(str(k).lower() in disallowed for k in evidence):
        return Status("PII_IN_EVIDENCE", "NO_CONFIRMED_SIGNUP")
    required = {
        "provider": "jetpack", "status": "Subscribed",
        "source": "authenticated_provider_server", "consent_scope": "dispatch_newsletter",
        "confirmation": "confirmed_email_link", "is_new_transition": True,
        "dedupe_applied": True, "opted_out": False,
        "bounced": False, "emails_paused": False,
    }
    if any(evidence.get(k) != v for k, v in required.items()):
        return Status("INSUFFICIENT_PROVIDER_EVIDENCE", "NO_CONFIRMED_SIGNUP")
    key = evidence.get("opaque_dedupe_ref")
    if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z0-9_-]{20,120}", key):
        return Status("MISSING_PRIVATE_DEDUP_REF", "NO_CONFIRMED_SIGNUP")
    return Status("STRUCTURAL_CANDIDATE_ONLY", "REQUIRES_INDEPENDENT_PROVIDER_AUTHENTICATION")


def release_decision(evidence: Mapping[str, bool]) -> dict[str, str]:
    """Offline fail-closed status, never SEND or approval; no implicit release."""
    core = ("founder_final_campaign_approval", "founder_post_publication_approval",
            "founder_send_approval", "native_preview_verified",
            "received_email_footer_verified", "valid_fv_postal_address_verified",
            "working_unsubscribe_verified", "eligible_provider_status_verified",
            "welcome_receipt_verified", "exact_per_post_toggle_verified",
            "copy_source_verified")
    commercial = ("affiliate_publisher_accepted", "email_channel_permission_verified",
                  "issued_earning_url_verified", "approved_live_guide_verified",
                  "specific_offer_claims_verified", "adjacent_disclosure_verified")
    # This package is designed for editorial review and cannot release anything.
    return {"editorial": "HOLD_UNSENT", "commercial": "HOLD_MERCHANT",
            "editorial_missing": ",".join(k for k in core if evidence.get(k) is not True),
            "commercial_missing": ",".join(k for k in commercial if evidence.get(k) is not True)}
