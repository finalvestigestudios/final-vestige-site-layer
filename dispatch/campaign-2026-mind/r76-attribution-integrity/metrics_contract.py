"""Aggregate-only, fail-closed Dispatch analytics desk. No network, mail or tracking."""
from datetime import date
from html import escape
from pathlib import Path
import argparse
import json
import sys

class InvalidEvidence(ValueError): pass

def check(d):
    def bad(): raise InvalidEvidence("INVALID_AGGREGATE_EVIDENCE")
    if type(d) is not dict or set(d) != {"schema", "periods", "newsletter", "merchants"}: bad()
    if d["schema"] != "fv-dispatch-r76-sitewide": bad()
    if type(d["periods"]) is not list or len(d["periods"]) != 3: bad()
    prev = None
    for index, period in enumerate(d["periods"]):
        if type(period) is not dict or set(period) != {"start","end","complete","views","visitors"}: bad()
        try:
            first, last = date.fromisoformat(period["start"]), date.fromisoformat(period["end"])
        except (ValueError, TypeError): bad()
        if (last-first).days != (6 if index < 2 else 0): bad()
        if prev is not None and (first-prev).days != 1: bad()
        prev = last
        if type(period["complete"]) is not bool or period["complete"] != (index < 2): bad()
        for key in ("views","visitors"):
            if type(period[key]) is not int or period[key] < 0: bad()
    n=d["newsletter"]
    if type(n) is not dict or set(n) != {"total","confirmed","unconfirmed","suppressed","eligible","recent_sends","auto_send","format","welcome_received"}: bad()
    for key in ("total","confirmed","unconfirmed","suppressed","recent_sends"):
        if type(n[key]) is not int or n[key] < 0: bad()
    if n["eligible"] is not None:
        if type(n["eligible"]) is not int or not 0 <= n["eligible"] <= n["total"]: bad()
    if type(n["auto_send"]) is not bool or type(n["welcome_received"]) is not bool or n["format"] not in ("excerpt","full"): bad()
    if type(d["merchants"]) is not dict or set(d["merchants"]) != {"03","05"}: bad()
    if any(type(v) is not bool for v in d["merchants"].values()): bad()
    return d

def assess(d):
    x=check(d); old,new,partial=x["periods"]; n=x["newsletter"]
    return {"state":"HOLD_UNSENT","send_allowed":False,
        "commercial_issues":{"03":"HOLD_MERCHANT","05":"HOLD_MERCHANT"},
        "sitewide_complete_weeks":[{"views":p["views"],"visitors":p["visitors"]} for p in (old,new)],
        "sitewide_view_change":new["views"]-old["views"],
        "sitewide_visitor_change":new["visitors"]-old["visitors"],
        "today_is_partial":True,
        "email_eligible":n["eligible"],
        "nonadditive_subscriber_counters":{"total":n["total"],"confirmed":n["confirmed"],"unconfirmed":n["unconfirmed"]},
        "recent_send_count":n["recent_sends"],
        "newsletter_attribution":{key:None for key in ("email_opens","referred_visits","fieldbook_downloads","guide_clicks","affiliate_sales","ab_winner")},
        "attribution_status":"NOT_OBSERVED",
        "warning":"Site-wide views and visitor counts cannot prove Dispatch referrals, human readership, or affiliate purchases; may include repeated/automated traffic.",
        "unverified":"Real eligible email count, Jetpack received MIME/unsubscribe, Final Vestige postal address, merchant-specific EMAIL rights, published guides, founder final sending approval."}

def text_report(r):
    old,new=r["sitewide_complete_weeks"]
    return ("FINAL VESTIGE | HOLD_UNSENT | NO EMAIL\n"
        +"Prior complete week: "+str(old["views"])+" views; "+str(old["visitors"])+" visitors.\n"
        +"Recent complete week: "+str(new["views"])+" views; "+str(new["visitors"])+" visitors.\n"
        +"Changes are SITE-WIDE ONLY, not Dispatch attribution. Nov 2 excluded as partial.\n"
        +"Newsletter opens/clicks, Fieldbook downloads, affiliate sales, A/B winner: NOT_OBSERVED.\n"
        +"Subscriber counters overlap; eligible audience unknown. #03/#05 HOLD_MERCHANT.\n")

def html_report(r):
    old,new=r["sitewide_complete_weeks"]
    return ("""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive">
<title>Dispatch | Aggregate evidence only</title>
<style>*{box-sizing:border-box}body{margin:0;background:#0a0e0f;color:#f3eadf;font:16px/1.6 system-ui}main{max-width:900px;margin:auto;padding:clamp(18px,4vw,48px)}
h1{font:normal clamp(2rem,5vw,3.4rem)/1.1 Georgia,serif}h2{font:normal 1.7rem Georgia,serif}
table{width:100%;border-collapse:collapse}th,td{padding:12px;text-align:left;border-bottom:1px solid #7d7366}
p{max-width:68ch}@media(max-width:540px){th,td{padding:6px;font-size:.9rem}}</style></head>
<body><main><strong>HOLD_UNSENT / NO TRACKING</strong><h1>More views do not mean newsletter conversions.</h1>
<p>Authenticated WordPress statistics. Two complete site-wide weeks; no observed Dispatch email response.</p>
<section aria-labelledby="measured"><h2 id="measured">Measured on the site</h2>
<table><caption>Site-wide traffic, not attributed to Dispatch</caption><thead><tr><th scope="col">Week</th><th scope="col">Views</th><th scope="col">Visitors</th></tr></thead><tbody>
<tr><th scope="row">Oct 19–25</th><td>""" + str(old["views"]) + "</td><td>" + str(old["visitors"]) + """</td></tr>
<tr><th scope="row">Oct 26–Nov 1</th><td>""" + str(new["views"]) + "</td><td>" + str(new["visitors"]) + """</td></tr></tbody></table>
<p>Nov 2 is partial and excluded. QA/automated traffic may affect counts.</p></section>
<section aria-labelledby="notmeasured"><h2 id="notmeasured">Not measured</h2>
<p>Newsletter opens, site referrals from Dispatch, Fieldbook downloads, affiliate clicks and sales are NOT_OBSERVED, not zero.</p></section>
<section aria-labelledby="holds"><h2 id="holds">Holds</h2>
<p>All six issues HOLD_UNSENT; #03/#05 HOLD_MERCHANT. Email-active audience, publisher postal address,
received Jetpack email, functional unsubscribe, approved live guides, and named-product partner email permission remain unverified.</p>
<p>No subscriber identities, active links, pixels, scripts, email sends or production changes.</p></section></main></body></html>""")

def main(argv=None):
    p=argparse.ArgumentParser(description="Offline aggregate-only Dispatch QA")
    p.add_argument("--input",required=True);p.add_argument("--output-dir",required=True);args=p.parse_args(argv)
    try:r=assess(json.loads(Path(args.input).read_text(encoding="utf-8")))
    except (InvalidEvidence, OSError, ValueError, KeyError, TypeError):
        print("INVALID_AGGREGATE_EVIDENCE",file=sys.stderr);return 2
    dest=Path(args.output_dir);dest.mkdir(parents=True,exist_ok=True)
    (dest/"report.json").write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8")
    (dest/"report.txt").write_text(text_report(r),encoding="utf-8")
    (dest/"report.html").write_text(html_report(r),encoding="utf-8")
    print("HOLD_UNSENT / AGGREGATE_ONLY");return 0

if __name__=="__main__":raise SystemExit(main())
