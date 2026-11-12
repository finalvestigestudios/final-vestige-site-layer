#!/usr/bin/env python3
"""R327 Preparedness source-to-offer fail-closed contract. Draft only, no external verification."""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
from preparedness.tools import r319_three_way_custody_hold as custody
from preparedness.tools import r323_full_slate_identity_crosswalk_hold as crosswalk

SCHEMA = "fv-preparedness-r327-source-to-offer-hard-hold-v1"
HOLD = {"publication_authorized": False, "independent_qd_pass": False,
        "qualified_safety_approved": False, "child_privacy_approved": False,
        "merchant_order_verified": False, "paid_offer_approved": False}
STEPS = ["qualified_human_session", "landing_visit", "relevant_cta_click",
         "confirmed_lead", "merchant_confirmed_order", "refunds_and_fees", "realized_net_revenue"]

def strict_hold(value, expected):
    return type(value) is dict and set(value) == set(expected) and all(value[k] is False for k in expected)

def first_party(url):
    if type(url) is not str or not url.isascii() or any(ord(c) <= 32 for c in url):
        return False
    try:
        p = urlsplit(url)
        return (p.scheme == "https" and p.netloc == "finalvestige.com" and
                p.port is None and not p.username and not p.password and
                not p.query and not p.fragment and p.path.startswith("/preparedness/") and
                "//" not in p.path and "\\" not in p.path and "%" not in p.path and
                not any(x in (".", "..") for x in p.path.split("/")) and
                not any(x in p.path.lower() for x in ("water-guide", "water-freebie", "water-ebook")))
    except ValueError:
        return False

def blank():
    """No SKU, offer link, creator asset, confirmed lead or revenue is assumed."""
    return {"schema": SCHEMA, "release": HOLD.copy(),
            "social": {"platform": None, "asset_id": None, "published_url": None,
                       "utm_campaign": None, "externally_verified": False},
            "free": {"url": "https://finalvestige.com/preparedness/",
                     "guide_slug": "family-communication-plan",
                     "guide_url": None, "source_safety_approved": False},
            "tool": {"slug": "family-reunification-card", "number": 104,
                     "cta_url": None, "privacy_approved": False,
                     "emergency_advice_approved": False, "print_approved": False},
            "paid": {"sku": None, "checkout_url": None, "rights_approved": False,
                     "merchant_approved": False, "delivery_approved": False,
                     "refunds_approved": False, "founder_approved": False},
            "metrics": {"steps": STEPS.copy(), "cohorts": [7, 30], "qualified_sessions": None,
                        "paid_orders": None, "gross": None, "fees": None,
                        "refunds": None, "realized_net": None}}

def inspect(candidate, audited):
    errors = []
    def issue(msg):
        errors.append(msg)
    expected = blank()
    if type(candidate) is not dict or set(candidate) != set(expected):
        issue("CONTRACT_SHAPE_INVALID")
        candidate = {}
    if candidate.get("schema") != SCHEMA or not strict_hold(candidate.get("release"), HOLD):
        issue("SCHEMA_OR_RELEASE_HOLD_INVALID")
    if (type(audited) is not dict or audited.get("schema") != crosswalk.SCHEMA or
            audited.get("state") != "DRAFT_HARD_HOLD" or audited.get("errors") != [] or
            audited.get("source_conflicts_held") != 15 or
            not strict_hold(audited.get("release"), crosswalk.RELEASE)):
        issue("NATIVE_CROSSWALK_REQUIRED")
    entries = audited.get("entries") if type(audited) is dict else None
    if type(entries) is not list or len(entries) != 41:
        issue("FORTY_ONE_SOURCE_IDENTITIES_REQUIRED")
        entries = []
    ids, urls = set(), set()
    for row in entries:
        if type(row) is not dict or type(row.get("slug")) is not str or row["slug"] in ids or \
                not first_party(row.get("canonical")) or row.get("canonical") in urls or \
                row.get("publication") != "draft" or row.get("type") not in ("articles", "tools") or \
                type(row.get("number")) is not int or \
                not re.fullmatch("[0-9a-f]{40}", str(row.get("body_git_blob"))) or \
                not re.fullmatch("[0-9a-f]{40}", str(row.get("metadata_git_blob"))):
            issue("SOURCE_IDENTITY_OR_ROUTE_DRIFT")
        else:
            ids.add(row["slug"])
            urls.add(row["canonical"])
    if len(ids) != 41 or sum(row.get("type") == "articles" for row in entries if type(row) is dict) != 35:
        issue("SLATE_COVERAGE_LOST")
    lookup = {row["slug"]: row for row in entries if type(row) is dict and type(row.get("slug")) is str}
    for slug, number in (("reunification-plan", 102), ("family-reunification-card", 104)):
        if lookup.get(slug, {}).get("type") != "tools" or type(lookup.get(slug, {}).get("number")) is not int or \
                lookup[slug]["number"] != number:
            issue("TOOL_102_104_IDENTITY_COLLISION")
    def section(name):
        value = candidate.get(name)
        if type(value) is not dict or set(value) != set(expected[name]):
            issue(name.upper() + "_FIELDS_INVALID")
            return {}
        return value
    social = section("social")
    if social.get("externally_verified") is not False:
        issue("SELF_ATTESTED_SOCIAL_NOT_PROOF")
    if social.get("asset_id") is None:
        if any(social.get(k) is not None for k in ("platform", "published_url", "utm_campaign")):
            issue("PARTIAL_SOCIAL_ATTRIBUTION")
    else:
        asset = social["asset_id"]
        if (type(asset) is not str or not re.fullmatch("[A-Za-z0-9_-]{11}", asset) or
                social.get("platform") != "youtube_shorts" or
                social.get("published_url") != "https://www.youtube.com/shorts/" + asset or
                social.get("utm_campaign") != "prep-reunification-" + asset):
            issue("ASSET_ID_URL_CAMPAIGN_MISMATCH")
    free = section("free")
    if not first_party(free.get("url")) or free.get("url") != "https://finalvestige.com/preparedness/":
        issue("PUBLIC_GUIDE_DESTINATION_MISMATCH")
    guide = lookup.get("family-communication-plan", {})
    if (guide.get("type") != "articles" or free.get("guide_slug") != "family-communication-plan" or
            free.get("guide_url") != guide.get("canonical") or
            free.get("source_safety_approved") is not False):
        issue("UNREVIEWED_GUIDE_CLAIM_OR_URL")
    tool = section("tool")
    if (tool.get("slug") != "family-reunification-card" or type(tool.get("number")) is not int or
            tool["number"] != 104 or tool.get("cta_url") is not None or
            any(tool.get(k) is not False for k in ("privacy_approved", "emergency_advice_approved", "print_approved"))):
        issue("TOOL_104_PRIVACY_EMERGENCY_HOLD")
    paid = section("paid")
    if (paid.get("sku") is not None or paid.get("checkout_url") is not None or
            any(paid.get(k) is not False for k in ("rights_approved", "merchant_approved",
                                                    "delivery_approved", "refunds_approved", "founder_approved"))):
        issue("NO_AUTHENTICATED_PAID_PREPAREDNESS_OFFER")
    metrics = section("metrics")
    if (metrics.get("steps") != STEPS or metrics.get("cohorts") != [7, 30] or
            any(metrics.get(k) is not None for k in ("qualified_sessions", "paid_orders",
                                                     "gross", "fees", "refunds", "realized_net"))):
        issue("UNVERIFIED_METRICS_NOT_REVENUE")
    errors = sorted(set(errors))
    return {"schema": SCHEMA, "state": "INVALID_HARD_HOLD" if errors else "DRAFT_HARD_HOLD",
            "errors": errors, "entries_checked": len(ids), "conflicts_held": 15,
            "offer": "UNVERIFIED_NO_PAID_CTA", "source_guide": "REVIEW_ONLY",
            "tool_104": "REVIEW_ONLY", "asset": "EXTERNAL_VERIFICATION_REQUIRED",
            "net_revenue_per_1000_qualified_sessions": None,
            "release": HOLD.copy()}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    root = p.parse_args().root.resolve()
    try:
        manifest = crosswalk.strict_json((root / custody.MANIFEST_PATH).read_bytes())
        docket = crosswalk.strict_json((root / "preparedness/audits/r320_conflict_adjudication_docket.json").read_bytes())
        taxonomy = crosswalk.strict_json((root / "preparedness/taxonomy.json").read_bytes())
        def read(path):
            value = custody.safe_bytes(root, path)
            if value is None:
                raise OSError("incomplete or symlinked native source")
            return value
        audit = crosswalk.audit(manifest, docket, taxonomy, read)
        if custody.validate_manifest(manifest, root)["errors"]:
            raise ValueError("custody drift")
        c = blank()
        c["free"]["guide_url"] = next((r["canonical"] for r in audit.get("entries", [])
                                      if r["slug"] == "family-communication-plan"), None)
        report = inspect(c, audit)
    except (OSError, ValueError, KeyError, TypeError, UnicodeError):
        report = {"schema": SCHEMA, "state": "INVALID_HARD_HOLD",
                  "errors": ["AUTHENTIC_COMPLETE_REPOSITORY_REQUIRED"], "release": HOLD.copy(),
                  "net_revenue_per_1000_qualified_sessions": None}
    print(json.dumps(report, sort_keys=True, indent=2))
    return 1 if report["state"] == "INVALID_HARD_HOLD" else 2

if __name__ == "__main__":
    raise SystemExit(main())
