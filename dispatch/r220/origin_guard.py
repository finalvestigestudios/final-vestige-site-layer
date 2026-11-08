"""R220 offline subscriber-origin guard. No provider/API access, no sending, no PII.

Structural conformance does NOT authenticate an asserted provider event. The only
production-verified proof is a read from the authorized provider, outside this code.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlsplit
import re

ENTRYPOINTS = frozenset({"focus_form", "dispatch_form", "post_end_block", "comment_subscribe_checkbox", "wordpress_reader", "unattributed"})
NON_LEAD = frozenset({"pdf_view", "gift_visible", "form_submit", "subscribe_url", "comment_notification", "reader_follow", "cta_click", "affiliate_click"})
KEYS = frozenset({"utm_source", "utm_medium", "utm_campaign", "utm_content"})
CLEAN_VALUE = re.compile(r"^[a-z0-9][a-z0-9_-]{1,70}$")


def utc_time(value):
    if not isinstance(value, str) or not value:
        raise ValueError("timestamp required")
    try:
        t = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as e:
        raise ValueError("invalid timestamp") from e
    if t.tzinfo is None:
        raise ValueError("timezone required")
    return t.astimezone(timezone.utc)


def safe_attribution(url, channel):
    """Only known owned landing routes and non-identifying UTMs, no PII or secrets."""
    p = urlsplit(url)
    if p.scheme != "https" or p.hostname not in ("finalvestige.com", "www.finalvestige.com"):
        raise ValueError("destination not owned HTTPS")
    if p.username or p.password or p.port or p.fragment or "//" in p.path or "\\" in p.path:
        raise ValueError("ambiguous/credentialed URL")
    pairs = parse_qsl(p.query, keep_blank_values=True)
    if len(pairs) != 4 or {k for k, _ in pairs} != KEYS:
        raise ValueError("must have four unique UTM keys only")
    args = dict(pairs)
    if any(not CLEAN_VALUE.fullmatch(v) for v in args.values()):
        raise ValueError("UTM value must be non-identifying slug")
    if channel == "dispatch":
        if (args["utm_source"], args["utm_medium"]) != ("dispatch", "email"):
            raise ValueError("incorrect Dispatch channel")
    elif channel == "grok":
        if args["utm_medium"] != "organic_social" or args["utm_source"] not in ("youtube", "tiktok", "instagram", "facebook", "x", "bluesky"):
            raise ValueError("incorrect social channel")
        if not args["utm_content"].startswith("asset_"):
            raise ValueError("requires actual asset-id-shaped content")
    else:
        raise ValueError("unrecognized channel")
    return {"owned_path": p.path, "tags": args, "verified_live_asset": False,
            "verified_session": False, "verified_paid_sale": False}


def classify_lead(event):
    """Evidence stage classifier. NEVER treats submitted/referral/gift UX as confirmed.

    'proof_candidate' is a schema claim only, not authentication or a counted lead.
    Origin attribution requires independently joined evidence; this code cannot do it.
    """
    if not isinstance(event, dict):
        raise ValueError("event must be object")
    if any(k in event for k in ("email", "email_hash", "ip", "phone", "subscriber_name", "cookie", "token")):
        raise ValueError("personal or secret data must not enter this module")
    k = event.get("kind")
    if k in NON_LEAD:
        return {"stage": "NON_LEAD", "attributable_to_focus": False, "countable_real_lead": False}
    if k != "provider_subscription_transition":
        return {"stage": "UNKNOWN", "attributable_to_focus": False, "countable_real_lead": False}
    if event.get("entrypoint") not in ENTRYPOINTS:
        return {"stage": "INVALID_ENTRYPOINT", "attributable_to_focus": False, "countable_real_lead": False}
    if event.get("source") != "authenticated_jetpack_provider" or event.get("new_status") != "subscribed" or event.get("old_status") not in ("not_confirmed", "absent"):
        return {"stage": "PROVIDER_PROOF_MISSING", "attributable_to_focus": False, "countable_real_lead": False}
    if not isinstance(event.get("provider_private_ref"), str) or not event["provider_private_ref"].startswith("private-only:"):
        return {"stage": "PROVIDER_PROOF_MISSING", "attributable_to_focus": False, "countable_real_lead": False}
    try:
        utc_time(event.get("at"))
    except ValueError:
        return {"stage": "INVALID_TIME", "attributable_to_focus": False, "countable_real_lead": False}
    # A source claim is not a cryptographic or provider-verified linkage.
    return {"stage": "PROVIDER_RECORD_SHAPED_UNAUTHENTICATED", "attributable_to_focus": False,
            "countable_real_lead": False, "requires_private_provider_authentication": True}


def summarize_public_sources(snapshot):
    """Distinct provider/site entrypoints. No inference from nonadditive counters."""
    required = ("newsletter_enabled", "default_auto_send", "post_end_subscribe", "comment_site_subscribe",
                "comment_reply_notifications", "focus_has_form", "dispatch_has_form", "newsletter_categories_enabled")
    if any(type(snapshot.get(k)) is not bool for k in required):
        raise ValueError("missing or non-boolean observation")
    for k in ("total", "confirmed", "unconfirmed", "followers_wpcom", "followers_email"):
        if type(snapshot.get(k)) is not int or snapshot[k] < 0:
            raise ValueError("invalid nonadditive counter")
    origin_candidates = [k for k, field in (("focus_form", "focus_has_form"),
                                             ("dispatch_form", "dispatch_has_form"),
                                             ("post_end_block", "post_end_subscribe"),
                                             ("comment_subscribe_checkbox", "comment_site_subscribe")) if snapshot[field]]
    return {"observable_subscription_entrypoints": origin_candidates,
            "comment_notification_is_not_newsletter_signup": bool(snapshot["comment_reply_notifications"]),
            "reader_follow_is_not_email_delivery": True,
            "confirmed_count_is_not_new_signup_delta": True,
            "eligible_email_recipient_count": None,
            "attributed_focus_confirmed_signups": None,
            "source_counts_nonadditive": {k: snapshot[k] for k in ("total", "confirmed", "unconfirmed", "followers_wpcom", "followers_email")},
            "newsletter_sends_authorized": False,
            "actual_qualifying_paid_sales": None}


def guarded_cohort(event_rows, cohort_days):
    """No false paid conversion from browser/CTA events. Does not compute money."""
    if cohort_days not in (7, 30):
        raise ValueError("only requested 7/30-day cohorts")
    statuses = Counter()
    for row in event_rows:
        state = classify_lead(row)
        statuses[state["stage"]] += 1
    return {"cohort_days": cohort_days, "synthetic_or_unverified_stage_counts": dict(sorted(statuses.items())),
            "provider_confirmed_leads": None, "paid_orders": None,
            "realized_net_revenue_per_1000_qualified_sessions": None,
            "status": "NOT_COMPUTABLE", "can_send": False}
