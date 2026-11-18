"""Fail-closed offline release and attribution contract for FV Dispatch.
No network, CMS, email, subscriber identifiers, or direct send path.
"""
from dataclasses import dataclass
from typing import Mapping
from urllib.parse import urlparse, parse_qs

ISSUES = (1, 2, 3, 4, 5, 6)
COMMERCIAL = frozenset((3, 5))
ISSUE_PRODUCTS = {3: "Zen12", 5: "Hypnosis Live"}
MUST_WITNESS = (
    "named_publisher_postal_address_rendered",
    "working_unsubscribe_rendered",
    "native_jetpack_non_sending_preview_witnessed",
    "post_title_matches_intended_subject",
    "subject_and_preheader_clean",
    "confirmed_email_audience_reconciled",
    "founder_campaign_approval",
)
PARTNER_WITNESS = (
    "named_account_accepted",
    "product_authorized",
    "email_channel_permitted_in_writing",
    "merchant_issued_earning_url_confirmed",
    "current_referred_checkout_and_refund_witnessed",
    "first_party_warmup_guide_live_approved",
    "near_offer_disclosure_rendered",
)

@dataclass(frozen=True)
class Result:
    status: str
    edition: int
    reasons: tuple[str, ...]
    kind: str


def release_review(edition: int, proofs: Mapping[str, object], *, product: str | None = None) -> Result:
    """Never authorizes a send: only a human review candidate when all attestations are true."""
    if edition not in ISSUES:
        raise ValueError("Edition outside the approved six-issue pilot")
    kind = "commercial-reserved" if edition in COMMERCIAL else "editorial"
    missing = [key for key in MUST_WITNESS if proofs.get(key) is not True]
    if proofs.get("subscriber_data_exported") is True:
        missing.append("prohibited_subscriber_export")
    if proofs.get("new_post_auto_send_enabled") is True:
        missing.append("prohibited_automatic_post_send")
    if edition in COMMERCIAL:
        if product != ISSUE_PRODUCTS[edition]:
            missing.append("incorrect_exact_offer_product")
        missing.extend(key for key in PARTNER_WITNESS if proofs.get(key) is not True)
    elif product is not None or proofs.get("affiliate_url_active") is True:
        missing.append("unsanctioned_commercial_placement")
    return Result(
        "HOLD_UNSENT" if missing else "HUMAN_REVIEW_CANDIDATE_ONLY",
        edition, tuple(missing), kind
    )


def classify_audience(newsletter: Mapping[str, object], subscribers: Mapping[str, object], followers: Mapping[str, object]):
    """No count is merged across incompatible provider endpoints."""
    c = newsletter.get("confirmed")
    u = newsletter.get("unconfirmed")
    se = subscribers.get("email")
    sr = subscribers.get("reader")
    fe = followers.get("email")
    fr = followers.get("reader")
    vals = (c, u, se, sr, fe, fr)
    if any(type(x) is not int or x < 0 for x in vals):
        return {"status": "INVALID_SOURCE_COUNTS", "counts": vals}
    discrepancy = se != fe or sr != fr or (c != se)
    return {
        "status": "SOURCE_CLASSIFICATION_DISAGREEMENT" if discrepancy else "SURFACES_AGREE_NOT_DELIVERY_PROOF",
        "newsletter_confirmed": c,
        "newsletter_unconfirmed_excluded": u,
        "stats_subscribers_email": se,
        "stats_subscribers_reader": sr,
        "stats_followers_email": fe,
        "stats_followers_reader": fr,
        "new_external_confirmed_signups": None,
        "welcome_received": None,
    }


def validate_grok_attribution(url: str, allowed_platforms=frozenset(("youtube", "tiktok", "instagram", "facebook", "x", "bluesky", "pinterest"))):
    """Validate a *proposed* source-tagged URL without contacting the site."""
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc.lower() != "finalvestige.com":
        return False
    q = parse_qs(parsed.query, keep_blank_values=True)
    fields = ("utm_source", "utm_medium", "utm_campaign", "utm_content")
    if any(len(q.get(key, [])) != 1 or not q[key][0].strip() for key in fields):
        return False
    if q["utm_source"][0] not in allowed_platforms or q["utm_medium"][0] != "organic_social":
        return False
    if not q["utm_campaign"][0].endswith("_pilot_2026_11"):
        return False
    return True


def realized_net_revenue_per_thousand(qualified_human_sessions, independently_settled_net):
    """Unknown is not zero. Never derives sales from views/clicks/leads."""
    if type(qualified_human_sessions) is not int or qualified_human_sessions <= 0:
        return None
    if independently_settled_net is None or isinstance(independently_settled_net, bool):
        return None
    if not isinstance(independently_settled_net, (int, float)):
        return None
    return round(1000 * independently_settled_net / qualified_human_sessions, 2)
