"""Read-only parity between candidate Jetpack excerpts and explicitly observed native drafts.

NEVER publishes, schedules, sends, reads subscriber records or provides release clearance.
"""
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

IDS = ("01", "02", "03", "04", "05", "06")
FIELDS = {"issue", "status", "title", "custom_excerpt", "send_to_subscribers",
          "scheduled_for", "primary_cta_url", "affiliate_urls"}

def fail(message):
    raise ValueError(message)

def _first_party(url):
    if not isinstance(url, str):
        return False
    p = urlsplit(url)
    return (p.scheme == "https" and p.hostname == "finalvestige.com"
            and not p.username and not p.password and not p.query and not p.fragment)

def compare(expected, observed):
    if expected.get("policy") != "REVIEW_ONLY_HOLD_UNSENT" or expected.get("release_clearance") is not False:
        fail("source policy is not fail-closed")
    rows = expected.get("expected_posts", [])
    if not isinstance(rows, list) or tuple(c.get("issue") for c in rows) != IDS:
        fail("unexpected source campaign allocation")
    if [c["issue"] for c in rows if c["allocation"] == "commercial_reserved"] != ["03", "05"]:
        fail("reserved offer placement drift")
    if not isinstance(observed, dict) or set(observed) != {"site", "observed_drafts"}:
        fail("unexpected observation keys; private recipient data not accepted")
    if observed["site"] != "https://finalvestige.com" or not isinstance(observed["observed_drafts"], list):
        fail("observation site or list invalid")

    by_id = {}
    for item in observed["observed_drafts"]:
        if not isinstance(item, dict) or set(item) != FIELDS:
            fail("observation fields invalid; never store subscriber identifiers")
        issue = item["issue"]
        if issue not in IDS or issue in by_id:
            fail("unknown or duplicate issue")
        if item["send_to_subscribers"] is not None and type(item["send_to_subscribers"]) is not bool:
            fail("email toggle must be a boolean or null")
        if item["affiliate_urls"] is not None and not isinstance(item["affiliate_urls"], list):
            fail("affiliate URLs field invalid")
        by_id[issue] = item

    outcomes = []
    for c in rows:
        item = by_id.get(c["issue"])
        blockers = []
        if item is None:
            blockers.append("NO_NATIVE_POST_OBSERVED")
        else:
            if item["status"] != "draft":
                blockers.append("NOT_NONPUBLISHED_DRAFT")
            if item["send_to_subscribers"] is not False:
                blockers.append("POST_EMAIL_TOGGLE_NOT_PROVEN_OFF")
            if item["scheduled_for"] is not None:
                blockers.append("SCHEDULED_OR_SCHEDULE_UNKNOWN")
            if item["title"] != c["editor_title"]:
                blockers.append("NATIVE_TITLE_NOT_EQUAL_TO_CANDIDATE")
            if item["custom_excerpt"] != c["editor_custom_excerpt"]:
                blockers.append("NATIVE_EXCERPT_NOT_EQUAL_TO_CANDIDATE")
            if c["allocation"] == "editorial":
                if item["primary_cta_url"] != c["primary_cta_url"] or not _first_party(c["primary_cta_url"]):
                    blockers.append("FIRST_PARTY_EDITORIAL_CTA_MISMATCH")
            elif item["primary_cta_url"] is not None:
                blockers.append("UNPUBLISHED_COMMERCIAL_GUIDE_LINK_PRESENT")
            if item["affiliate_urls"] != []:
                blockers.append("AFFILIATE_URLS_NOT_ALLOWED")
        structural_match = not blockers
        if c["allocation"] == "commercial_reserved":
            blockers.append("MERCHANT_EMAIL_RIGHTS_AND_GUIDE_UNVERIFIED")
        blockers.append("LEGAL_DELIVERY_SUBSCRIBER_AND_FOUNDER_GATES_NOT_CLEARED")
        outcomes.append({"issue": c["issue"], "allocation": c["allocation"],
                         "structure_matches": structural_match,
                         "status": "HOLD_UNSENT", "blockers": blockers})

    return {"status": "HOLD_UNSENT",
            "type": "STATIC_SOURCE_TO_DRAFT_PARITY_ONLY_NOT_EMAIL_PREVIEW",
            "observed_drafts": len(by_id),
            "recipient_eligibility": "UNKNOWN",
            "real_received_jetpack_email": "UNVERIFIED",
            "verified_publisher_postal_address": False,
            "delivered_unsubscribe_functionality": "UNVERIFIED",
            "founder_final_send_approval": False,
            "outcomes": outcomes}

def main():
    parser = argparse.ArgumentParser(description="Offline / NO SEND / redacted native post parity")
    parser.add_argument("--expected", type=Path, default=Path(__file__).with_name("EXPECTED.json"))
    parser.add_argument("--observed", type=Path, default=Path(__file__).with_name("OBSERVATIONS.json"))
    args = parser.parse_args()
    try:
        expected = json.loads(args.expected.read_text(encoding="utf-8"))
        observed = json.loads(args.observed.read_text(encoding="utf-8"))
        print(json.dumps(compare(expected, observed), indent=2, ensure_ascii=False))
    except (ValueError, OSError, json.JSONDecodeError):
        print('{"status":"HOLD_UNSENT","error":"INVALID_OR_UNAVAILABLE_EVIDENCE"}')
        raise SystemExit(2)

if __name__ == "__main__":
    main()
