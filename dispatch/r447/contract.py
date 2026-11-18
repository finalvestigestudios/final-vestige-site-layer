"""Source-only Dispatch acceptance checks. Never sends, subscribes, publishes or tracks users."""
from decimal import Decimal, InvalidOperation

COMMERCIAL_ISSUES = frozenset((3, 5))
SHARED_GATES = (
    "founder_final_campaign_approval", "native_jetpack_preview_witness",
    "fv_physical_postal_verified", "rendered_unsubscribe_verified",
    "optout_process_verified", "audience_eligibility_witness",
    "welcome_delivery_witness", "copy_claim_and_cta_approved",
)
MERCHANT_GATES = (
    "named_affiliate_acceptance", "email_channel_permission",
    "sku_and_issued_link_verified", "live_vetted_first_party_guide",
    "current_checkout_refund_terms", "near_offer_disclosure_verified",
)


def snapshot_counts(snapshot):
    """Unconfirmed may be a separate bucket: never sum it into eligible recipients."""
    values = [snapshot.get(k) for k in ("total", "confirmed", "unconfirmed", "email_subscribed")]
    if any(type(n) is not int or n < 0 for n in values):
        raise ValueError("counts must be nonnegative integers")
    total, confirmed, unconfirmed, email = values
    if confirmed > total or email > confirmed:
        raise ValueError("contradictory provider counts")
    return {"confirmed_email_eligible": email,
            "unconfirmed_excluded": unconfirmed,
            "independent_new_leads": None,
            "delivered_welcomes": None,
            "paid_customers": None}


def new_confirmed_signup(before, after, provider_witness):
    """True only for a new authoritative email-subscribed state transition."""
    if not provider_witness or provider_witness.get("origin") != "jetpack_provider":
        return False
    if not provider_witness.get("same_private_recipient") or not provider_witness.get("timestamp"):
        return False
    if after.get("status") != "Subscribed" or after.get("email_subscriber") is not True:
        return False
    if before.get("status") == "Subscribed" and before.get("email_subscriber") is True:
        return False
    return True


def release_reasons(issue, proofs):
    """Returns unresolved reasons, never a send authorization."""
    if type(issue) is not int or issue not in range(1, 7):
        raise ValueError("issue must be 1..6")
    required = SHARED_GATES + (MERCHANT_GATES if issue in COMMERCIAL_ISSUES else ())
    unresolved = [key for key in required if proofs.get(key) is not True]
    if proofs.get("campaign_status") != "HOLD_UNSENT":
        unresolved.append("canonical_hold_status_missing")
    if issue in COMMERCIAL_ISSUES and proofs.get("merchant_product") != ("Zen12" if issue == 3 else "Hypnosis Live"):
        unresolved.append("wrong_canonical_product")
    return unresolved


def net_per_1000(cohort):
    """Compute only with settled orders and a positively audited human denominator."""
    if not cohort.get("human_sessions_audited") or not cohort.get("settlement_report_verified"):
        return None
    if cohort.get("window_days") not in (7, 30):
        return None
    if cohort.get("source_window") != cohort.get("settlement_window"):
        return None
    sessions = cohort.get("qualified_human_sessions")
    if type(sessions) is not int or sessions <= 0:
        return None
    orders = cohort.get("orders")
    if not isinstance(orders, list):
        return None
    total = Decimal("0")
    for order in orders:
        if order.get("status") != "settled" or order.get("merchant_report_verified") is not True:
            return None
        try:
            gross, refunds, fees = (Decimal(str(order[k])) for k in ("commission", "refunds", "fees"))
        except (KeyError, InvalidOperation, ValueError):
            return None
        if not all(x.is_finite() for x in (gross, refunds, fees)):
            return None
        if gross < 0 or refunds < 0 or fees < 0:
            return None
        total += gross - refunds - fees
    return (total * Decimal("1000") / Decimal(sessions)).quantize(Decimal("0.01"))
