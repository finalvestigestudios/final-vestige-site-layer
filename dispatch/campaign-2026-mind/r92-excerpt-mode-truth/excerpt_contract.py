"""Fail-closed, offline validation and HTML rendering of Jetpack excerpt *candidates*.

This tool cannot send, post, edit settings, resolve recipients or certify actual email.
Run: python -I dispatch/campaign-2026-mind/r92-excerpt-mode-truth/excerpt_contract.py --check
"""
from __future__ import annotations
import argparse
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
SOURCE = ROOT / "candidate_excerpts.json"
COM_NOTE = "Commercial note:"

def words(text: str) -> int:
    return len(re.findall(r"\b[\w’-]+\b", text, re.UNICODE))

def load(path: pathlib.Path = SOURCE) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def validate(doc: dict) -> list[str]:
    failures = []
    def block(test, issue):
        if test: failures.append(issue)
    try:
        cfg = doc["settings_snapshot"]
        native = doc["native_wordpress_expectation"]
        issues = doc["issues"]
        block(doc["campaign_state"] != "DRAFT_NO_SEND", "release state must be draft")
        block(doc["master_sha"] != "d57ccdba3aee8f065e143e101c2945f4f3d01647", "master SHA drift")
        block(cfg["newsletter_enabled"] is not True, "newsletter status unknown")
        block(cfg["email_content_format"] != "excerpt", "actual newsletter mode changed; stop")
        block(cfg["email_new_posts_by_default"] is not False, "new-post email default must stay off")
        block(cfg["eligible_email_recipients"] is not None, "eligible count cannot be inferred")
        block(cfg["subscriber_total"] != 2 or cfg["subscriber_confirmed"] != 2 or cfg["subscriber_unconfirmed"] != 2 or cfg["stats_email_followers"] != 0 or cfg["stats_wpcom_followers"] != 2, "WordPress diagnostics differ; reread")
        for key in ("qualified_publisher_postal_address_verified", "actual_jetpack_email_preview_verified", "received_email_unsubscribe_verified", "founder_final_send_approval"):
            block(cfg[key] is not False, "unsatisfied evidence gate: "+key)
        block(native["custom_preheader_control_verified"] is not False, "Jetpack custom preheader not established")
        block(native["wpcom_documented_fallback_55_words"] is not True or native["jetpack_documented_fallback_350_characters"] is not True, "official fallback documentation divergence must remain visible")
        block(native["actual_fallback_model_verified"] is not False or native["custom_excerpt_delivery_observed"] is not False, "native site-specific excerpt rendering remains unverified")
        block(native["post_title_used_as_subject"] is not True or native["custom_excerpt_can_supply_email_intro"] is not True, "WordPress contract changed")
        block(len(issues) != 6 or doc["editorial_count"] != 4 or doc["commercial_count"] != 2, "4:2 mix invalid")
        block([i["number"] for i in issues] != [1,2,3,4,5,6], "edition order invalid")
        block([i["number"] for i in issues if i["kind"]=="commercial-review-pending"] != [3,5], "commercial placement changed")
        for i in issues:
            n = str(i["number"])
            subj = i["subject_candidate"]
            excerpt = i["excerpt_text"]
            block(i["status"] != "HOLD_UNSENT", n+": send status activated")
            block(i["merchant_approval"] is not False or i["active_affiliate_url"] is not None or i["approved_guide_url"] is not None, n+": unverified commercial activation")
            block(not 15 <= len(subj) <= 77 or "\n" in subj, n+": unacceptable subject")
            block(not 25 <= words(excerpt) <= 85, n+": custom excerpt length exceeds review range")
            block("[[" in excerpt or "]]" in excerpt or "<" in excerpt or ">" in excerpt, n+": unrendered token/markup")
            block(bool(re.search(r"\b(?:guaranteed|clinically proven|life changing|100%|limitless powers)\b", excerpt, re.I)), n+": unsubstantiated claim")
            block(bool(re.search(r"https?://|www\.|utm_|@", excerpt, re.I)), n+": URL/tracking/address in excerpt")
            block("fourteen seconds" in subj.lower(), n+": unsupported numeric Apollo subject")
            if i["kind"] == "commercial-review-pending":
                block(not excerpt.startswith(COM_NOTE), n+": commercial note must lead excerpt")
                block(i["commercial_note"] is None or not excerpt.startswith(i["commercial_note"]), n+": disclosure mismatch")
                block(i["editorial_source_url"] is not None, n+": merchant editions must not have a live guide destination")
            else:
                block(i["commercial_note"] is not None, n+": editorial edition unexpectedly commercial")
                block(not str(i["editorial_source_url"]).startswith("https://finalvestige.com/"), n+": editorial research URL must be first-party")
    except (KeyError, TypeError, ValueError) as exc:
        failures.append("invalid / incomplete evidence document: "+type(exc).__name__)
    return failures

def render_html(doc: dict) -> str:
    failures = validate(doc)
    if failures:
        raise ValueError("HOLD: " + "; ".join(failures))
    part = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Excerpt reviewer — not Jetpack</title></head><body><main><h1>STATIC REVIEW ONLY / NOT SENT</h1><p>Not a genuine received email; no delivery or compliant footer verified.</p>']
    for i in doc["issues"]:
        part.append('<section><h2>Issue '+str(i["number"])+': '+html.escape(i["subject_candidate"])+'</h2><p>'+html.escape(i["excerpt_text"])+'</p><p>HOLD_UNSENT</p></section>')
    return "".join(part) + "</main></body></html>"

def main() -> int:
    cli = argparse.ArgumentParser()
    cli.add_argument("--check", action="store_true", help="read-only verification")
    cli.add_argument("--preview-html", action="store_true", help="write sanitized offline HTML to stdout ONLY")
    ns = cli.parse_args()
    doc = load()
    errors = validate(doc)
    if errors:
        for err in errors: print("HOLD: "+err)
        return 1
    if ns.preview_html:
        print(render_html(doc))
    else:
        print("PASS: six custom-excerpt candidates, 4 editorial / 2 commercial; ALL HOLD_UNSENT")
        print("NOT VERIFIED: actual Jetpack email, affiliate permission, address, unsub, recipients, preheader, send approval")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
