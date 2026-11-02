#!/usr/bin/env python3
"""Render ONLY the redacted R70 inspector schema as accessible offline HTML/text.

Do not feed this a raw .eml; it accepts the inspector's intentionally sparse JSON.
Every view remains clearly labeled HOLD and is NOT an email preview.
"""
from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import re

SCHEMA = "fv-dispatch-received-eml-readonly-v1"
DISPLAY = (
    ("subject_present", "Received MIME contains a subject"),
    ("subject_matches_selected_copy", "Subject matches independently approved reference"),
    ("wordpress_sending_domain_heuristic", "Sender contains WordPress domain (heuristic only)"),
    ("plain_text_part_present", "Plain-text MIME body present"),
    ("html_part_present", "HTML MIME body present"),
    ("visible_body_present", "Visible message text present"),
    ("html_lang_en_present", "HTML declares English"),
    ("html_interactive_markup_detected", "Unexpected interactive/script markup detected"),
    ("remote_image_present", "Remote image or tracker-capable asset present"),
    ("unsubscribe_labeled_https_link_present", "Labeled HTTPS opt-out link appears in HTML"),
    ("plain_text_optout_and_https_present", "Opt-out text and HTTPS present in plaintext"),
    ("list_unsubscribe_header_present", "List-Unsubscribe header present"),
    ("list_unsubscribe_post_one_click_declared", "One-click header declared (not exercised)"),
    ("postal_text_matches_private_publisher_reference", "Text matches privately supplied publisher-address reference"),
    ("commercial_disclosure_within_first_55_visible_words", "Commercial disclosure appears in first 55 visible words"),
    ("merchant_domain_link_detected", "Merchant-domain link detected; never automatically approved"),
    ("hard_stop_placeholder_detected", "Unresolved release placeholder detected"),
)

def clean(report: dict) -> dict:
    if not isinstance(report, dict) or report.get("schema") != SCHEMA:
        raise ValueError("Not an R70 redacted inspector report")
    if report.get("release_status") != "HOLD_UNSENT" or report.get("send_allowed") is not False:
        raise ValueError("Refuse to present any purported approval")
    edition = report.get("edition")
    if edition not in ("01", "02", "03", "04", "05", "06"):
        raise ValueError("Unexpected issue number")
    original = report.get("signals")
    if not isinstance(original, dict):
        raise ValueError("Signals missing")
    sig = {}
    for key, label in DISPLAY:
        val = original.get(key)
        if val is not None and not isinstance(val, bool) and not (key == "html_links_count" and type(val) is int):
            raise ValueError("Unrecognized signal value")
        sig[key] = val
    nlinks = original.get("html_links_count")
    if type(nlinks) is not int or nlinks < 0 or nlinks > 100000:
        raise ValueError("Invalid link count")
    sig["html_links_count"] = nlinks
    blockers = report.get("blockers")
    if not isinstance(blockers, list) or not blockers or len(blockers) > 50:
        raise ValueError("Blockers invalid or missing")
    for item in blockers:
        if not isinstance(item, str) or not re.fullmatch(r"[A-Z0-9_]{3,90}", item):
            raise ValueError("Unexpected blocker label")
    return {"edition": edition, "signals": sig, "blockers": list(blockers)}

def state(v):
    if v is True:
        return "DETECTED / TRUE"
    if v is False:
        return "NOT DETECTED / FALSE"
    if v is None:
        return "UNKNOWN / NOT TESTED"
    return "COUNT " + str(v)

def text_report(report: dict) -> str:
    r = clean(report)
    lines = [
        "FINAL VESTIGE / DISPATCH - PRIVATE REDACTED RECEIVED-MIME REVIEW",
        "ISSUE " + r["edition"] + " | HOLD_UNSENT | SEND ALLOWED: NO",
        "Not a delivered Jetpack preview or legal certification.",
        "No actual recipient, sender address, opt-out token or message content is shown.",
        "",
        "Signal inventory (presence and syntax only):",
    ]
    for key, label in DISPLAY:
        lines.append("  " + label + ": " + state(r["signals"][key]))
    lines.append("  HTML links count: " + str(r["signals"]["html_links_count"]))
    lines.append("")
    lines.append("UNRESOLVED REQUIREMENTS:")
    lines.extend("  - " + b.replace("_", " ").title() for b in r["blockers"])
    lines.append("")
    lines.append("Always require founder final campaign approval, verified recipient consent,")
    lines.append("the qualified Final Vestige postal address and a real functional opt-out test.")
    return "\n".join(lines) + "\n"

def html_report(report: dict) -> str:
    r = clean(report)
    rows = []
    for key, label in DISPLAY:
        val = r["signals"][key]
        css = "good" if val is True else ("warn" if val is None else "muted")
        # A true signal is never permission; e.g., true remote-image or hard-stop is bad.
        if key in ("html_interactive_markup_detected", "remote_image_present",
                   "merchant_domain_link_detected", "hard_stop_placeholder_detected"):
            css = "warn" if val is True else "muted"
        rows.append("<tr><th scope='row'>" + escape(label) + "</th><td class='" + css + "'>" +
                    escape(state(val)) + "</td></tr>")
    rows.append("<tr><th scope='row'>HTML links, count only</th><td>" +
                str(r["signals"]["html_links_count"]) + "</td></tr>")
    items = "".join("<li>" + escape(b.replace("_", " ").title()) + "</li>" for b in r["blockers"])
    return ("""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive"><title>Dispatch received MIME | HOLD</title>
<style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#090b0b;color:#eee9e1;font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}
main{width:min(900px,calc(100% - 32px));margin:0 auto;padding:42px 0 80px}
a{color:#efd09b}:focus-visible{outline:3px solid #ffdc85;outline-offset:4px}
.eyebrow{font-weight:700;letter-spacing:.16em;color:#d2ab77;text-transform:uppercase;font-size:.75rem}
h1{font-family:Georgia,serif;letter-spacing:-.02em;font-weight:400;line-height:1.13;font-size:clamp(2rem,6vw,3.8rem);margin:.5rem 0 1rem}
h2{font:400 clamp(1.5rem,3.2vw,2rem) Georgia,serif;margin:32px 0 12px}
p{max-width:72ch;color:#d2cbc0}.hold{border:2px solid #efc178;background:#281e14;padding:16px 20px;color:#fff0d8;font-weight:700;margin:24px 0}
table{width:100%;border-collapse:collapse;table-layout:fixed}th,td{text-align:left;border-bottom:1px solid #454139;padding:12px 8px;vertical-align:top;overflow-wrap:anywhere}th{width:64%;font-weight:500}td{font-size:.9rem;color:#ddd5c9}
.good{color:#a6e6b5}.warn{color:#ffd08b}.muted{color:#b2b3b3}li{margin:8px 0;overflow-wrap:anywhere}
.small{font-size:.875rem;color:#bdb6ab}footer{border-top:1px solid #454139;padding-top:20px;margin-top:36px}
@media(max-width:560px){main{width:min(100% - 24px,900px);padding-top:24px}th,td{display:block;width:100%;border:0;padding:7px 2px}td{border-bottom:1px solid #454139;padding-bottom:16px}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style></head><body><main><p class="eyebrow">Final Vestige / reviewer-only evidence</p>
<h1>Received MIME inspection — edition """ + escape(r["edition"]) + """</h1>
<p>This is a redacted, static report of locally inspected MIME properties. It is <strong>not</strong> a received-mail screenshot, live Jetpack preview, legal certificate, validated unsubscribe or permission to send. No personal addresses, URLs, raw email or tracking tokens are included.</p>
<div class="hold" role="status" aria-live="off">HOLD_UNSENT · No campaign or test send approved by this report</div>
<section aria-labelledby="signals"><h2 id="signals">What the parser could see</h2>
<table><caption class="small">Boolean observations are not functional verification.</caption><tbody>""" +
    "".join(rows) + """</tbody></table></section>
<section aria-labelledby="gates"><h2 id="gates">Outstanding release evidence</h2><ol>""" + items + """</ol></section>
<footer><p class="small">Synthetic fixtures or user-supplied private MIME can generate this same appearance. A reviewer must independently establish actual receipt, sender identity, qualified postal ownership, working opt-out, eligible audience, approved merchant rights and explicit founder approval.</p></footer>
</main></body></html>
""")

def main(argv=None):
    p = argparse.ArgumentParser(description="Render a redacted R70 JSON report to local static HTML and text")
    p.add_argument("--report-json", required=True, type=Path)
    p.add_argument("--html-out", required=True, type=Path)
    p.add_argument("--text-out", required=True, type=Path)
    a = p.parse_args(argv)
    try:
        if a.report_json.is_symlink() or a.report_json.stat().st_size > 32768:
            raise ValueError("Input missing or too large")
        r = json.loads(a.report_json.read_text(encoding="utf-8"))
        html = html_report(r)
        plain = text_report(r)
        a.html_out.write_text(html, encoding="utf-8")
        a.text_out.write_text(plain, encoding="utf-8")
    except (OSError, ValueError, TypeError):
        print("RENDER_FAILED_INPUT_OR_OUTPUT_INVALID")
        return 2
    print("RENDERED_REDACTED_HOLD_REPORT_ONLY")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
