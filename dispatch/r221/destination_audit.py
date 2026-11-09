"""R221 non-sending Dispatch route/attribution reviewer. NOT a live verification service."""
from __future__ import annotations
import re
from urllib.parse import urlsplit, parse_qsl

# WordPress read-only evidence 2026-11-09T00:35Z; published routes, not approvals.
PUBLISHED = {
    "/focus/": 1579,
    "/dispatch/": 523,
    "/the-missing-caption/": 1122,
    "/free-resources/puysegurs-animal-magnetism-files/": 1377,
    "/2026/08/20/the-hatch-opened-inward-apollo-1/": 434,
    "/2026/11/02/change-blindness/": 1922,
}
EDITORIAL_CTA = {1: "/the-missing-caption/", 2: "/free-resources/puysegurs-animal-magnetism-files/", 4: "/2026/08/20/the-hatch-opened-inward-apollo-1/", 6: "/focus/"}
COMMERCIAL = {3: "ZEN12_GUIDE_NOT_LIVE", 5: "TOTAL_FOCUS_GUIDE_NOT_LIVE"}
ALLOWED_UTMS = frozenset(("utm_source", "utm_medium", "utm_campaign", "utm_content"))
SLUG = re.compile(r"^[a-z][a-z0-9_-]{1,70}$")


def review_url(url: str, channel: str, issue: int | None = None) -> dict:
    """Validate intended PUBLIC landing only. This NEVER verifies consent, sessions or money.

    Fail closed on percent-encoded paths, unapproved/new CMS paths, and off-brand
    issue destinations. These guards prevent *false reporting* of eligible links;
    they do not establish a click, a published social asset or a paid conversion.
    """
    if not isinstance(url, str) or not isinstance(channel, str):
        raise ValueError("URL and channel must be strings")
    p = urlsplit(url)
    if (p.scheme != "https" or p.netloc not in ("finalvestige.com", "www.finalvestige.com")
            or p.username or p.password or p.port or p.fragment):
        raise ValueError("unowned, ambiguous or credentialed destination")
    if (not p.path.startswith("/") or "%" in p.path or "\\" in p.path
            or "//" in p.path or "/./" in p.path or "/../" in p.path
            or any(ord(c) < 33 or ord(c) > 126 for c in p.path)):
        raise ValueError("path must be exact, ASCII and unencoded")
    if p.path not in PUBLISHED:
        raise ValueError("not a verified published Dispatch landing")
    if not p.query:
        raise ValueError("source attribution requires four clear UTMs")
    try:
        pairs = parse_qsl(p.query, keep_blank_values=True, strict_parsing=True, max_num_fields=4)
    except ValueError as exc:
        raise ValueError("invalid UTM query") from exc
    if len(pairs) != 4 or {k for k, _ in pairs} != ALLOWED_UTMS:
        raise ValueError("missing, repeated or extraneous attribution parameter")
    params = dict(pairs)
    if any(not SLUG.fullmatch(v) for v in params.values()):
        raise ValueError("PII-bearing or malformed UTM")
    if channel == "grok":
        if params["utm_medium"] != "organic_social" or params["utm_source"] not in {"youtube", "tiktok", "instagram", "facebook", "x", "bluesky"}:
            raise ValueError("not a Grok owned-channel attribution")
        if not re.fullmatch(r"asset_[a-z0-9][a-z0-9_-]{2,60}", params["utm_content"]):
            raise ValueError("Grok content must have asset-id-shaped token")
        if issue is not None:
            raise ValueError("Dispatch issue must not be attributed as Grok asset")
    elif channel == "dispatch":
        if type(issue) is not int or issue not in set(EDITORIAL_CTA) | set(COMMERCIAL):
            raise ValueError("specific valid issue required")
        if params["utm_source"] != "dispatch" or params["utm_medium"] != "email":
            raise ValueError("wrong email source")
        if params["utm_content"] != f"issue_{issue:02d}":
            raise ValueError("issue CTA attribution mismatch")
        if issue in COMMERCIAL:
            raise ValueError("commercial guide not live or eligible, hard hold")
        if p.path != EDITORIAL_CTA[issue]:
            raise ValueError("issue CTA differs from approved original manifest")
    else:
        raise ValueError("unknown acquisition channel")
    return {"path": p.path, "wordpress_id_observed": PUBLISHED[p.path], "kind": channel,
            "syntactically_allowed": True, "actual_asset_authenticated": False,
            "provider_confirmed_signup": None, "actual_paid_order": None,
            "send_authorized": False, "realized_net_revenue": None}


def commercial_hold(issue: int) -> dict:
    """No affiliate link, seller permission, subscriber evidence or postal QA received."""
    if type(issue) is not int or issue not in COMMERCIAL:
        raise ValueError("not a reserved commercial issue")
    return {"issue": issue, "guide_status": COMMERCIAL[issue],
            "affiliate_email_permission_verified": False, "affiliate_link_verified": False,
            "checkout_refund_terms_verified": False, "live_guide_verified": False,
            "postal_footer_verified": False, "unsubscribe_received_verified": False,
            "newsletter_send_authorized": False, "paid_revenue": None}
