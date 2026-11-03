#!/usr/bin/env python3
"""R78 privacy-preserving evidence reconciliation. This can NEVER authorize a send."""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
SCHEMA = "fv_dispatch_audience_cross_api_v1"
TOP = {"schema", "recorded_utc", "newsletter_status", "jetpack_followers",
       "newsletter_settings", "private_operator_attestations",
       "named_product_permissions", "observed_source"}
NEWS = {"as_of", "total", "confirmed", "unconfirmed", "suppressed", "recent_sends", "site_can_send"}
FOLLOW = {"email", "wpcom", "comment", "total", "partial", "publicize"}
SETTINGS = {"email_new_posts_by_default", "email_content_format", "from_name", "welcome_fieldbook_configured"}
PRIVATE = {"email_subscribed_and_sending_count", "bounced_or_paused_count",
           "received_mail_proven", "unsubscribe_functional",
           "valid_publisher_postal_address", "final_founder_send_approval"}
OFFERS = {"zen12_email", "total_focus_email"}

class EvidenceError(ValueError):
    pass

def keys(obj, expected, where):
    if type(obj) is not dict or set(obj) != expected:
        raise EvidenceError("invalid schema at " + where)

def nonnegative_int(value):
    return type(value) is int and value >= 0

def checkbox(value):
    return type(value) is bool

def validate(s):
    keys(s, TOP, "root")
    if s["schema"] != SCHEMA:
        raise EvidenceError("unsupported evidence schema")
    if type(s["recorded_utc"]) is not str or not re.fullmatch(r"2026-11-0[23]T\d{2}:\d{2}:\d{2}\+00:00", s["recorded_utc"]):
        raise EvidenceError("invalid record timestamp")
    keys(s["newsletter_status"], NEWS, "newsletter_status")
    n=s["newsletter_status"]
    if type(n["as_of"]) is not str or not n["as_of"].startswith("2026-11-03T"):
        raise EvidenceError("invalid status source timestamp")
    for name in ("total", "confirmed", "unconfirmed", "suppressed", "recent_sends"):
        if not nonnegative_int(n[name]):
            raise EvidenceError("invalid numeric counter: " + name)
    if not checkbox(n["site_can_send"]):
        raise EvidenceError("site_can_send must be boolean")
    keys(s["jetpack_followers"], FOLLOW, "jetpack_followers")
    f=s["jetpack_followers"]
    for name in ("email", "wpcom", "comment", "total"):
        if not nonnegative_int(f[name]):
            raise EvidenceError("invalid followers counter: " + name)
    if not checkbox(f["partial"]):
        raise EvidenceError("partial must be boolean")
    if type(f["publicize"]) is not dict:
        raise EvidenceError("invalid publicize shape")
    for name, count in f["publicize"].items():
        if type(name) is not str or not re.fullmatch(r"[a-z][a-z0-9_-]{0,30}", name) or not nonnegative_int(count):
            raise EvidenceError("invalid publicize counter")
    if not f["partial"] and f["total"] != (f["email"]+f["wpcom"]+f["comment"]+sum(f["publicize"].values())):
        raise EvidenceError("followers aggregate inconsistent")
    keys(s["newsletter_settings"], SETTINGS, "newsletter_settings")
    e=s["newsletter_settings"]
    if not checkbox(e["email_new_posts_by_default"]) or not checkbox(e["welcome_fieldbook_configured"]):
        raise EvidenceError("invalid settings flags")
    if e["email_content_format"] not in ("excerpt", "full") or e["from_name"] != "Final Vestige":
        raise EvidenceError("incorrect live sender or format")
    keys(s["private_operator_attestations"], PRIVATE, "private attestations")
    p=s["private_operator_attestations"]
    for name in ("email_subscribed_and_sending_count", "bounced_or_paused_count"):
        if p[name] is not None and not nonnegative_int(p[name]):
            raise EvidenceError("invalid count-only private attestation")
    for name in PRIVATE-{"email_subscribed_and_sending_count", "bounced_or_paused_count"}:
        if not checkbox(p[name]):
            raise EvidenceError("invalid attestation flag")
    keys(s["named_product_permissions"], OFFERS, "named products")
    if not all(checkbox(x) for x in s["named_product_permissions"].values()):
        raise EvidenceError("invalid merchant permissions")
    if s["observed_source"] != ("Authenticated WordPress newsletter.status, newsletter.get_settings, and "
                               "wpcom_jetpack_stats_followers; separate APIs, not a verified subscriber row export."):
        raise EvidenceError("unknown source provenance")

def report(s):
    validate(s)
    n=s["newsletter_status"]; f=s["jetpack_followers"]; p=s["private_operator_attestations"]
    mismatch = n["confirmed"] != f["email"]
    # This is intentionally not the newsletter recipient count.
    # The two APIs serve different endpoints / semantics, and no row-level audit exists.
    return {
        "schema":SCHEMA,
        "recorded_utc":s["recorded_utc"],
        "newsletter_status_total":n["total"],
        "newsletter_status_confirmed":n["confirmed"],
        "newsletter_status_unconfirmed":n["unconfirmed"],
        "newsletter_status_suppressed":n["suppressed"],
        "followers_email":f["email"],
        "followers_wpcom":f["wpcom"],
        "followers_total":f["total"],
        "newsletter_status_counts_are_nonadditive":True,
        "newsletter_status_vs_followers_email_mismatch":mismatch,
        "interpretation":("COUNTER_DISAGREEMENT_NOT_PROOF_OF_ZERO_RECIPIENTS" if mismatch
                           else "COUNTERS_MATCH_STILL_NOT_DELIVERABILITY_PROOF"),
        "eligible_recipients":None,
        "privately_attested_email_subscribed_count":p["email_subscribed_and_sending_count"],
        "previewed_jetpack_email":False,
        "received_jetpack_email_verified":False,
        "unsubscribe_verified":False,
        "founder_send_approval":False,
        "offer_03":"HOLD_MERCHANT",
        "offer_05":"HOLD_MERCHANT",
        "campaign_status":"HOLD_UNSENT",
        "send_authorized":False,
        "next_evidence":"Read only Jetpack Newsletter > Subscribers; filter Email Subscription = Subscribed, separately check Not sending (any reason). Record aggregate counts only. No subscriber export or contact."
    }

def text_report(r):
    return ("FINAL VESTIGE DISPATCH — R78 CROSS-API AUDIENCE EVIDENCE\n"
            "Campaign: HOLD_UNSENT | Commercial 03/05: HOLD_MERCHANT\n"
            "Newsletter status: total %d; confirmed %d; unconfirmed %d; suppressed %d (NONADDITIVE)\n"
            "Jetpack followers: email %d; WordPress.com %d; total %d (DIFFERENT ENDPOINT)\n"
            "Cross-API comparison: %s\n"
            "Email-eligible audience: UNKNOWN (not 0, not 2, not 4)\n"
            "Real email receipt/unsubscribe/postal/merchant email rights: NOT VERIFIED\n"
            "No sends, tests, imports, changes, payouts, or inferred analytics.\n"
            "Required next: %s\n" %
            (r["newsletter_status_total"],r["newsletter_status_confirmed"],
             r["newsletter_status_unconfirmed"],r["newsletter_status_suppressed"],
             r["followers_email"],r["followers_wpcom"],r["followers_total"],
             r["interpretation"],r["next_evidence"]))

def html_report(r):
    rows=[
      ("Newsletter status total",str(r["newsletter_status_total"])),
      ("Status confirmed",str(r["newsletter_status_confirmed"])),
      ("Status unconfirmed",str(r["newsletter_status_unconfirmed"])),
      ("Jetpack followers email",str(r["followers_email"])),
      ("Jetpack followers WordPress.com",str(r["followers_wpcom"])),
      ("Cross-API interpretation",r["interpretation"]),
      ("Verified email recipients","UNKNOWN"),
      ("Release authorization","HOLD_UNSENT"),
      ("Offer issues 03 and 05","HOLD_MERCHANT")
    ]
    trs="".join("<tr><th scope='row'>%s</th><td>%s</td></tr>"%
                (html.escape(k),html.escape(v)) for k,v in rows)
    return ("""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dispatch R78 — Source disagreement / HOLD</title>
<style>body{background:#090a0a;color:#f4efe6;font:16px/1.65 system-ui,sans-serif;max-width:880px;margin:auto;padding:26px}
a{color:#e3c695} th,td{text-align:left;border-bottom:1px solid #484440;padding:12px;vertical-align:top}
table{border-collapse:collapse;width:100%%}th{width:46%%}
:focus-visible{outline:3px solid white;outline-offset:4px}
.notice{border-left:5px solid #e3c695;padding:15px;background:#191817}
@media(max-width:500px){th,td{display:block;width:auto;padding:7px}}</style></head>
<body><main><h1>Dispatch: count discrepancy</h1><p class="notice"><strong>HOLD_UNSENT.</strong>
The subscriber audience cannot be inferred from two incompatible API counters.
This is a source reconciliation report—not an email preview or release approval.</p>
<table><caption>Authenticated WordPress counter observations, November 2, 2026</caption>
<tbody>%s</tbody></table><h2>What must happen next</h2><p>%s</p>
<p>Do not infer zero deliverable subscribers from an email-follower count of zero,
and do not add 2 confirmed to 2 unconfirmed. Do not expose names, addresses, or
private subscription tokens.</p><p>Source of record: WordPress account APIs.
<a href="https://wordpress.com/support/subscribers/">Subscriber status documentation</a>.
<a href="https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business">FTC CAN-SPAM guidance</a>.</p>
</main></body></html>""" % (trs,html.escape(r["next_evidence"])))

def main():
    ap=argparse.ArgumentParser(description="Read-only cross-API audience reconciliation. Never sends.")
    ap.add_argument("--input",type=Path,default=ROOT/"source_snapshot.json")
    ap.add_argument("--format",choices=("text","html","json"),default="text")
    args=ap.parse_args()
    try:
        data=json.loads(args.input.read_text(encoding="utf-8"))
        r=report(data)
        out=html_report(r) if args.format=="html" else (
            json.dumps(r,indent=2,sort_keys=True) if args.format=="json" else text_report(r))
        print(out)
    except (EvidenceError, OSError, ValueError, TypeError):
        print("HOLD_UNSENT: evidence validation failed (no private input echoed)",file=sys.stderr)
        return 2
    return 0

if __name__=="__main__":
    raise SystemExit(main())
