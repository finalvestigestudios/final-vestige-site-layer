"""Read-only Release Contract QA for six proposed Jetpack custom excerpts.

Never calls WordPress, sends mail, writes configuration, or classifies a draft
as a verified or legally compliant received message.
"""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent

def evaluate(data: dict) -> list[str]:
    errors = []
    if data.get("release_state") != "HOLD_UNSENT" or data.get("future_email_approved") is not False:
        errors.append("release must remain HOLD_UNSENT without future send approval")
    if data.get("future_email_scheduled") is not False:
        errors.append("any schedule is disallowed")
    channel = data.get("channel", {})
    if channel.get("email_content_format") != "excerpt" or channel.get("new_post_auto_send") is not False:
        errors.append("channel snapshot must document excerpt mode and auto-send off")
    if any(channel.get(k) != "NOT_VERIFIED" for k in ("preheader_editable_control", "received_email", "unsubscribe_functional", "publisher_physical_address", "welcome_receipt")):
        errors.append("no inference of received email, address, footer, or editable preheader")
    if channel.get("reported_counts", {}).get("send_eligible") != "UNKNOWN":
        errors.append("eligible recipients remain unknown, counts must not be added")
    rights = data.get("commercial_permissions", {})
    if rights.get("buyer_guide_published") is not False or rights.get("private_buyer_data_processing_plan_approved") is not False:
        errors.append("buyer guides and buyer-data handling are not approved")
    for k in ("zen12_email", "total_focus_email", "specific_affiliate_acceptance", "affiliate_earning_url", "affiliate_creative_rights"):
        if rights.get(k) != "UNVERIFIED":
            errors.append("merchant permission or earning link cannot be assumed")
    issues = data.get("editions", [])
    if len(issues) != 6 or sorted(e.get("number") for e in issues) != list(range(1, 7)):
        errors.append("six numbered editions required")
        return errors
    if sum(e.get("kind") == "editorial" for e in issues) != 4 or sum(e.get("kind") == "commercial-review-pending" for e in issues) != 2:
        errors.append("founder four-to-two editorial/commercial balance must remain")
    for e in issues:
        n = e["number"]
        if e.get("send_approved") is not False or e.get("production_excerpt_installed") is not False or e.get("original_full_manuscript_modified") is not False:
            errors.append(f"{n}: not approved, installed, or substituted")
        for key in ("subject", "preheader_intent", "intro"):
            value = e.get(key)
            if not isinstance(value, str) or not value.strip() or any(ord(c)<32 for c in value):
                errors.append(f"{n}: invalid {key}")
        if len(e.get("subject", "")) > 70 or len(e.get("preheader_intent", "")) > 155:
            errors.append(f"{n}: subject/preheader length out of bounds")
        intro = e.get("intro", "")
        if len(intro.split()) < 55 or len(intro.split()) > 175:
            errors.append(f"{n}: excerpt needs adequate substantive length")
        for banned in ("100% guaranteed", "clinical proof of Zen12", "buy now", "only today", "as seen on", "we tested this product", "guaranteed results"):
            if banned in intro.lower():
                errors.append(f"{n}: unsupported or manipulative copy")
        if any(x in intro.lower() for x in ("http://", "https://", "utm_", "clickid=", "aff_id=")):
            errors.append(f"{n}: no active URL or affiliate tracking in custom excerpt")
        sources=e.get("source_urls", [])
        if not sources or any(urlparse(s).scheme != "https" or not urlparse(s).netloc for s in sources):
            errors.append(f"{n}: full official/research HTTPS source references required")
        if n in (3,5):
            if e.get("kind") != "commercial-review-pending" or e.get("planned_cta") is not None or e.get("guide_url") is not None:
                errors.append(f"{n}: commercial guide must remain inactive")
            first55 = " ".join(intro.lower().split()[:55])
            if "may receive a commission" not in first55 or "no buying link is active" not in first55 and "no purchase link is active" not in first55:
                errors.append(f"{n}: full disclosure/hold must appear within first 55 words")
        elif e.get("kind") == "editorial":
            url=e.get("planned_cta")
            if not isinstance(url,str) or urlparse(url).netloc != "finalvestige.com":
                errors.append(f"{n}: editorial CTA must use published Final Vestige destination")
            if e.get("guide_url") is not None:
                errors.append(f"{n}: no merchant guide in editorial edition")
    return errors

def main() -> int:
    data = json.loads((HERE / "candidates.json").read_text(encoding="utf-8"))
    issues = evaluate(data)
    if issues:
        print("REVIEW CONTRACT INVALID — HOLD_UNSENT; " + "; ".join(issues))
        return 1
    print("SIX CUSTOM EXCERPTS STRUCTURALLY VERIFIED — NOT APPROVED / NOT INSTALLED / NOT RECEIVED; HOLD_UNSENT")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
