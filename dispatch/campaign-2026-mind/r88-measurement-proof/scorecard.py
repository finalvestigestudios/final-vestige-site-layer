#!/usr/bin/env python3
"""Fail-closed, offline campaign measurement evidence, never a sender or tracker."""
import argparse
import html
import json
import pathlib
import re

METRIC_SOURCES = {
    "recipients": "jetpack_email_run",
    "sent": "jetpack_email_run",
    "opens": "jetpack_email_run",
    "email_clicks": "jetpack_email_run",
    "guide_views": "wordpress_stats",
    "guide_cta_clicks": "first_party_analytics",
    "merchant_outbound_clicks": "first_party_analytics",
    "affiliate_sales": "verified_partner_report",
    "commission_usd_cents": "verified_partner_report"
}
EXPECTED = ("01", "02", "03", "04", "05", "06")
COMMERCIAL = {"03", "05"}
MAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
TRACK_RE = re.compile(r"(?:utm_|fbclid|gclid|ref=|aff(?:iliate)?[_-]?id=)", re.I)
SOURCE_REF = re.compile(r"^[A-Za-z0-9/_:.#-]{8,150}$")


class UnsafeEvidence(ValueError):
    pass


def _integer(v):
    return type(v) is int and v >= 0


def validate(data):
    """Validation is strict even on future-looking aggregate documents."""
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True)
    if MAIL_RE.search(raw):
        raise UnsafeEvidence("Recipient or sender identifier prohibited")
    if TRACK_RE.search(raw):
        raise UnsafeEvidence("Tracking or private affiliate identifiers prohibited")
    if data.get("schema_version") != 1 or data.get("site") != "https://finalvestige.com":
        raise UnsafeEvidence("Wrong schema or site")
    if data.get("report_type") != "RESEARCH_ONLY_NO_SEND":
        raise UnsafeEvidence("Report can never represent send approval")
    if not re.fullmatch(r"2026-\d\d-\d\dT\d\d:\d\d:\d\dZ", data.get("as_of_utc", "")):
        raise UnsafeEvidence("UTC source timestamp required")
    if set(data.get("source_paths", {})) != {"newsletter", "followers"}:
        raise UnsafeEvidence("Two independently identified sources required")
    n = data.get("newsletter", {})
    f = data.get("followers", {})
    if not all(_integer(n.get(k)) for k in ("count_total", "count_confirmed", "count_unconfirmed", "suppressed")):
        raise UnsafeEvidence("Subscriber counters cannot be negative, absent or boolean")
    if not all(_integer(f.get(k)) for k in ("total", "email", "wpcom")):
        raise UnsafeEvidence("Follower counters cannot be negative, absent or boolean")
    if type(f.get("partial")) is not bool:
        raise UnsafeEvidence("Follower partial flag required")
    for k, expected in {
        "enabled": True, "site_can_send": True, "new_post_default_send": False,
        "welcome_pdf_configured": True, "welcome_receipt_verified": False
    }.items():
        if n.get(k) is not expected:
            raise UnsafeEvidence("Read-only operating observation drift: " + k)
    if n.get("email_content_format") != "excerpt" or n.get("reply_to") != "no-reply":
        raise UnsafeEvidence("Transport observation drift")
    post_ids = n.get("recent_post_ids_never_sent_opted_out")
    if not isinstance(post_ids, list) or len(post_ids) != 5 or any(not _integer(v) for v in post_ids) or len(set(post_ids)) != 5:
        raise UnsafeEvidence("Specific opted-out history must be preserved")
    if data.get("email_eligible_audience") is not None:
        raise UnsafeEvidence("Eligible audience not established by competing aggregate systems")
    for k in ("real_received_email_verified", "real_unsubscribe_verified",
              "publisher_postal_verified", "founder_send_approval",
              "affiliate_email_permission_verified", "affiliate_guides_live",
              "attribution_activated"):
        if data.get(k) is not False:
            raise UnsafeEvidence("Missing external authorization cannot be promoted: " + k)
    records = data.get("issues")
    if not isinstance(records, list) or tuple(i.get("id") for i in records) != EXPECTED:
        raise UnsafeEvidence("Must preserve six original campaign issues in order")
    for issue in records:
        commercial = issue["id"] in COMMERCIAL
        if issue.get("kind") != ("commercial_reserved" if commercial else "editorial"):
            raise UnsafeEvidence("Founder 4:2 mix must remain")
        if issue.get("merchant_url") is not None:
            raise UnsafeEvidence("Unapproved merchant destination")
        cta = "merchant_guide_unpublished" if commercial else "first_party_live"
        if issue.get("cta_state") != cta:
            raise UnsafeEvidence("CTA destination must not be silently enabled")
        if not isinstance(issue.get("subject"), str) or len(issue["subject"].strip()) < 10:
            raise UnsafeEvidence("Original subject provenance missing")
        metrics = issue.get("metrics", {})
        if set(metrics) - set(METRIC_SOURCES):
            raise UnsafeEvidence("Unknown measurement field")
        for name, obs in metrics.items():
            if not isinstance(obs, dict) or set(obs) != {"value", "source", "proof_ref", "observed_at"}:
                raise UnsafeEvidence("Metrics need typed observation plus provenance")
            val = obs["value"]
            if not _integer(val) or obs["source"] != METRIC_SOURCES[name]:
                raise UnsafeEvidence("Metric value/source mismatch")
            if not isinstance(obs["proof_ref"], str) or not SOURCE_REF.fullmatch(obs["proof_ref"]):
                raise UnsafeEvidence("Opaque verifiable reference required, never recipient data")
            if not re.fullmatch(r"20\d\d-\d\d-\d\dT\d\d:\d\d:\d\dZ", obs["observed_at"] or ""):
                raise UnsafeEvidence("Observed metric requires exact time")
        if "affiliate_sales" in metrics and "merchant_outbound_clicks" not in metrics:
            raise UnsafeEvidence("Partner revenue must be distinguished from click evidence")
        if "sent" in metrics and "recipients" in metrics and metrics["sent"]["value"] > metrics["recipients"]["value"]:
            raise UnsafeEvidence("More sent than recipients")
        if "opens" in metrics and "sent" in metrics and metrics["opens"]["value"] > metrics["sent"]["value"]:
            raise UnsafeEvidence("More unique opens than sends")
    return True


def _value(issue, name, minimum=5):
    obs = issue["metrics"].get(name)
    if obs is None:
        return "UNKNOWN"
    number = obs["value"]
    return "SUPPRESSED (<5)" if number < minimum else str(number)


def scorecard(data):
    validate(data)
    anomaly = data["newsletter"]["count_confirmed"] + data["newsletter"]["count_unconfirmed"] != data["newsletter"]["count_total"]
    return {
        "status": "HOLD_UNSENT",
        "merchant_status": "HOLD_MERCHANT",
        "audience": "UNKNOWN",
        "counter_conflict": anomaly,
        "source_time": data["as_of_utc"],
        "rows": [
            {"id": i["id"], "subject": i["subject"],
             "status": "HOLD_MERCHANT" if i["id"] in COMMERCIAL else "HOLD_UNSENT",
             "recipients": _value(i, "recipients"),
             "email_clicks": _value(i, "email_clicks"),
             "guide_views": _value(i, "guide_views"),
             "affiliate_sales": _value(i, "affiliate_sales")}
            for i in data["issues"]
        ]
    }


def render_text(board):
    lines = [
        "FINAL VESTIGE | DISPATCH EVIDENCE SCORECARD | REVIEW ONLY",
        "Source as-of UTC: " + board["source_time"],
        "All six: HOLD_UNSENT; commercial 03/05: HOLD_MERCHANT.",
        "Email-eligible audience: UNKNOWN. Sources disagree on classifications.",
        "WordPress follower email=0 does not establish zero eligible recipients.",
        "A recent-post status list is NOT an all-time zero-email certificate.",
        "No delivered message, product-specific email permission, postal or opt-out proof.",
        "UNKNOWN means no verified measurement; SUPPRESSED means count <5.",
        "Opens (if ever verified) are directional, not proof of readership.",
        "No click-to-sale inference. No A/B tests with this audience.", ""
    ]
    for r in board["rows"]:
        lines.append("{id} | {subject} | {status} | recipients={recipients} | email_clicks={email_clicks} | guide_views={guide_views} | affiliate_sales={affiliate_sales}".format(**r))
    lines.extend(["", "READ ONLY. Not an email, a campaign authorization or affiliate dashboard."])
    return "\n".join(lines) + "\n"


def render_html(board):
    rows = "\n".join(
        "<tr><th scope='row'>{}</th><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            html.escape(r["id"]), html.escape(r["subject"]), html.escape(r["status"]),
            html.escape(r["recipients"]), html.escape(r["email_clicks"]), html.escape(r["affiliate_sales"]))
        for r in board["rows"])
    return """<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Dispatch evidence-only scorecard</title><style>
body{background:#0b0d0e;color:#f3eee7;font:1rem/1.6 system-ui,sans-serif;margin:0}
main{max-width:75rem;margin:auto;padding:clamp(1rem,4vw,3rem)}
a{color:#f2ca87}a:focus-visible{outline:3px solid #fff;outline-offset:3px}
p{max-width:75ch}table{border-collapse:collapse;width:100%;min-width:44rem}
th,td{border:1px solid #746b5e;padding:.7rem;text-align:left;vertical-align:top}
thead{background:#242322} .scroller{overflow-x:auto}
small{color:#dfd4c2} .tag{font-weight:700;color:#f2ca87} </style></head><body><main>
<h1>Dispatch: evidence-only scorecard</h1>
<p class='tag'>ALL SIX HOLD_UNSENT · ISSUES 03/05 HOLD_MERCHANT</p>
<p>Verified source observation: __AS_OF__. Eligible email audience: <strong>UNKNOWN</strong>. Newsletter and follower counters classify their audience differently; totals are not additive. No send, recipient export, link activation or affiliate attribution has occurred.</p>
<p>UNKNOWN means unverified; SUPPRESSED means a verified aggregate below five is hidden. Never interpret WordPress Reader followers as deliverable email recipients. Opens are directional only and cannot substitute for confirmed delivery or sales.</p>
<div class='scroller' tabindex='0' role='region' aria-label='Per-edition evidence table'><table>
<caption>Six-issue pilot — no fabricated measurements or release authorizations</caption><thead><tr><th scope='col'>Issue</th><th scope='col'>Original subject</th><th scope='col'>Gate</th><th scope='col'>Recipients</th><th scope='col'>Email clicks</th><th scope='col'>Partner sales</th></tr></thead><tbody>__ROWS__</tbody></table></div>
<p><small>Source: connected WordPress newsletter status and follower stats, separately, November 3, 2026. Founder-approved 4:2 editorial/commercial allocation unchanged. This static review is neither a genuine Jetpack received email nor proof of legal compliance.</small></p>
</main></body></html>""".replace("__AS_OF__", html.escape(board["source_time"])).replace("__ROWS__", rows)


def main():
    parser = argparse.ArgumentParser(description="Offline evidence-only Dispatch scorecard")
    parser.add_argument("--snapshot", type=pathlib.Path, default=pathlib.Path(__file__).with_name("snapshot.json"))
    parser.add_argument("--output", type=pathlib.Path, default=None, help="Optional output directory, never WordPress")
    args = parser.parse_args()
    board = scorecard(json.loads(args.snapshot.read_text(encoding="utf-8")))
    if args.output:
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "REVIEW.html").write_text(render_html(board), encoding="utf-8")
        (args.output / "REVIEW.txt").write_text(render_text(board), encoding="utf-8")
    else:
        print(render_text(board), end="")


if __name__ == "__main__":
    main()
