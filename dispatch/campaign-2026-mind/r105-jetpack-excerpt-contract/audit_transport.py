"""R105 read-only, fail-closed audit of the proposed Jetpack excerpt transport.
No network, email, WordPress, or GitHub write operations.
"""
import json
import pathlib
import re
import sys

PATH = pathlib.Path(__file__).with_name("transport_contract.json")
EXPECTED_SUBJECTS = ["The mind is not a camera","Before hypnosis had a name","The twelve-minute meditation question","Fourteen seconds. A much longer explanation.","Before you press play on a hypnosis audio","What did seven days of attention reveal?"]
EXPECTED_PREHEADERS = ["What an old record can teach us about the difference between seeing and knowing.","The eighteenth-century witnesses who left behind a problem of proof.","An honest way to evaluate a short audio practice before you spend anything.","Apollo 1, the surviving record, and why a tidy cause can mislead.","Three questions that matter more than an impressive promise.","A small experiment, a useful notebook, and no miracle claims."]
ISSUE_KINDS = ("editorial", "editorial", "commercial_review_pending",
               "editorial", "commercial_review_pending", "editorial")

def inspect(doc):
    errors = []
    if doc.get("id") != "R105_JETPACK_EXCERPT_REVIEW_ONLY":
        errors.append("contract identifier altered")
    if doc.get("source_pr_175_exact_sha") != "d57ccdba3aee8f065e143e101c2945f4f3d01647":
        errors.append("original creative SHA altered")
    if doc.get("source_manifest_blob") != "86df98ad8a84e583ff5df64ddbf8c0eaa1335b00":
        errors.append("original manifest SHA altered")
    if doc.get("transport_choice") != "NO_SEND_NO_CHANGE":
        errors.append("transport approval attempt")
    if doc.get("merchant_email_permission") != "NOT_VERIFIED":
        errors.append("unauthorized merchant permission claim")
    if doc.get("privacy_aggregate_only_reporting") != "NOT_VERIFIED":
        errors.append("unverified private-buyer-data sharing permission")
    e = doc.get("transport_evidence", {})
    for key, expected in (
        ("jetpack_enabled", True), ("site_can_send", True),
        ("default_post_email_enabled", False), ("content_format", "excerpt"),
        ("welcome_fieldbook_52_pages_configured", True),
        ("welcome_actual_receipt_verified", False),
        ("newsletter_subscriber_total", 2), ("newsletter_confirmed", 2),
        ("newsletter_unconfirmed", 2), ("jetpack_email_followers", 0),
        ("jetpack_wpcom_followers", 2),
        ("eligible_recipients", None),
        ("five_recent_events", "never_sent_opted_out"),
        ("actual_received_campaign_email_verified", False),
        ("footer_address_verified", False),
        ("unsubscribe_operation_verified", False),
        ("editorial_version_approved", False),
        ("final_founder_send_approval", False),
    ):
        if e.get(key, object()) != expected or type(e.get(key)) != type(expected):
            errors.append("tampered or unverified WordPress evidence: " + key)
    rows = doc.get("issues", [])
    if not isinstance(rows, list) or len(rows) != 6:
        errors.append("must preserve exactly six editions")
        return errors
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append("issue row malformed")
            continue
        prefix = f"issue {index+1}: "
        expected_id = f"{index+1:02d}"
        if row.get("issue") != expected_id or row.get("kind") != ISSUE_KINDS[index]:
            errors.append(prefix + "4 editorial / 2 commercial source order altered")
        if row.get("subject") != EXPECTED_SUBJECTS[index]:
            errors.append(prefix + "original subject drift")
        if row.get("preheader") != EXPECTED_PREHEADERS[index]:
            errors.append(prefix + "original preheader drift")
        if row.get("status") != "HOLD_UNSENT":
            errors.append(prefix + "attempted send state")
        if row.get("merchant_hold") is not (index in (2, 4)):
            errors.append(prefix + "merchant hold changed")
        for f in ("warmup_guide_live", "approved_email_permission"):
            if row.get(f) is not False:
                errors.append(prefix + "unverified commercial prerequisite " + f)
        if row.get("affiliate_url") is not None:
            errors.append(prefix + "affiliate link activated")
        if row.get("natural_first55_loses_primary_cta") is not True:
            errors.append(prefix + "default excerpt finding altered")
        if row.get("natural_first55_loses_commercial_disclosure") is not (index in (2, 4)):
            errors.append(prefix + "commercial truncation finding altered")
        snippet = row.get("proposed_custom_excerpt", "")
        if not isinstance(snippet, str) or len(snippet.split()) > 55 or len(snippet.split()) < 28:
            errors.append(prefix + "custom excerpt outside review word range")
        elif re.search(r"https?://|href\\s*=|@|\\[\\[|<[^>]*>|guaranteed|clinically proven|buy now|limited time|special price", snippet, re.I):
            errors.append(prefix + "unsafe excerpt / link / claim")
    return errors

def main():
    data = json.loads(PATH.read_text(encoding="utf-8"))
    errors = inspect(data)
    print("Final Vestige Dispatch R105 transport audit")
    print("Status: HOLD_UNSENT; commercial 03/05 HOLD_MERCHANT")
    print("Transport: ACTUAL EXCERPT / candidates are OFFLINE ONLY")
    print("Evidence findings: six native-first-55 excerpts omit the primary CTA; both commercial disclaimers omitted")
    if errors:
        for error in errors:
            print("FAIL:", error)
        return 1
    print("PASS: source/version, 4:2, excerpt safety, false release attestations, privacy, subscriber ambiguity")
    print("No received email inspected; no send or WordPress change authorized.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
