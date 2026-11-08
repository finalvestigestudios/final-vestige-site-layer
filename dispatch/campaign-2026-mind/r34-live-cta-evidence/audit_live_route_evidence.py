"""Fail-closed comparison of a dated, redacted WP read-only snapshot to Dispatch manifest.

Purely offline: never calls WordPress, email, tracking or affiliate services.
Successful checks are NOT proof of live delivery, permission or legal compliance.
"""
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = Path(__file__).with_name("LIVE_ROUTE_EVIDENCE.json")
MANIFEST = ROOT / "manifest.json"

class EvidenceError(ValueError):
    pass

def require(ok, why):
    if not ok:
        raise EvidenceError(why)

def acceptable_url(s):
    if not isinstance(s, str):
        return False
    try:
        p = urlsplit(s)
        return p.scheme == "https" and p.hostname == "finalvestige.com" and p.port is None and not (
            p.username or p.password or p.query or p.fragment
        )
    except ValueError:
        return False

def audit(manifest, evidence):
    require(evidence.get("schema") == "fv-dispatch-r34-live-destination-evidence-v1", "schema")
    require(evidence.get("as_of_utc") == "2026-11-01T03:32:58Z", "dated observation must not be silently restamped")
    require(evidence.get("snapshot_not_live_requery") is True, "snapshot must not claim a live re-query")
    require(evidence.get("no_send_authorization") is True and evidence.get("no_wordpress_writes") is True,
            "no sending and no WordPress mutation")
    require(evidence.get("no_merchant_links") is True and evidence.get("release") == "HOLD_UNSENT"
            and evidence.get("commercial_release") == "HOLD_MERCHANT_03_05", "hard holds required")
    require(manifest.get("status") == "DRAFT_UNSENT_NO_SCHEDULING", "manifest release status")
    issues = manifest.get("issues", [])
    require(len(issues) == 6 and {i.get("number") for i in issues} == set(range(1, 7)),
            "six distinct canonical issues")
    imap = {i["number"]: i for i in issues}
    require(sum(i.get("kind") == "editorial" for i in issues) == 4 and
            sum(i.get("kind") == "commercial-review-pending" for i in issues) == 2,
            "approved four editorial / two commercial split")
    require(all(i.get("publish_state") == "hold" and i.get("merchant_affiliate_url") is None
                for i in issues), "activated send or earning link is forbidden")
    rows = evidence.get("routes", [])
    require(isinstance(rows, list) and len(rows) == 6 and
            {r.get("number") for r in rows} == set(range(1, 7)), "six unique records required")
    live_editorial = 0
    held_commercial = 0
    for r in rows:
        i = imap[r["number"]]
        require(r.get("kind") == i.get("kind"), "category mismatch")
        if i["kind"] == "editorial":
            require(r.get("status") == "publish" and r.get("wp_type") in ("page", "post")
                    and type(r.get("wp_id")) is int and r["wp_id"] > 0, "published WP id missing")
            require(acceptable_url(r.get("url")) and r["url"] == i.get("editorial_cta"),
                    "untrusted or mismatched editorial destination")
            live_editorial += 1
        else:
            require(r.get("status") == "exact_slug_not_found"
                    and r.get("wp_type") is None and r.get("wp_id") is None
                    and r.get("url") is None and r.get("partner_email_permission_verified") is False,
                    "commercial page/email permission not attested")
            require(isinstance(i.get("editorial_cta"), str)
                    and i["editorial_cta"].startswith("[[")
                    and i["editorial_cta"].endswith("]]"), "inactive commercial CTA mandatory")
            held_commercial += 1
    require(evidence.get("subscriber_counts_nonadditive") ==
            {"total": 2, "confirmed": 2, "unconfirmed": 2, "suppressed": 0, "paid": 0},
            "subscriber categories are nonadditive")
    require(evidence.get("eligible_unique_recipients") == "UNKNOWN",
            "audience cannot be inferred from counters")
    n = evidence.get("newsletter", {})
    require(n.get("enabled") is True and n.get("new_post_automatic_email") is False
            and n.get("content_format") == "excerpt" and n.get("recent_sends") == 0
            and n.get("welcome_received_verified") is False, "newsletter configuration / welcome proof")
    def no_private_keys(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                require(not re.search(r"recipient.?email|subscriber.?email|personal.?address|"
                                      r"postal.?line|unsubscribe.?token|affiliate.?earning.?url",
                                      k, re.I), "private or link-token data prohibited")
                no_private_keys(v)
        elif isinstance(obj, list):
            for v in obj:
                no_private_keys(v)
    no_private_keys(evidence)
    return {
        "schema": "fv-dispatch-r34-route-review-v1",
        "snapshot_as_of": evidence["as_of_utc"],
        "editorial_ctas_published_on_snapshot": live_editorial,
        "commercial_ctas_verified_live": 0,
        "commercial_ctas_blocked": held_commercial,
        "real_jetpack_email_received": False,
        "eligible_audience_verified": False,
        "founder_final_approval": False,
        "release": "HOLD_UNSENT",
        "merchant_release": "HOLD_MERCHANT"
    }

if __name__ == "__main__":
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    print(json.dumps(audit(manifest, evidence), indent=2, sort_keys=True))
    raise SystemExit(2)
