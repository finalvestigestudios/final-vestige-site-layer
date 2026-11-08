"""Fail-closed, *offline* verification of R84's first-party editorial route.
This program never calls the network, writes WordPress, sends email, or approves release.
"""
import html
import json
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
EXPECTED_NEW_URL = "https://finalvestige.com/2026/11/02/change-blindness/"
EXPECTED_MASTER_URL = "https://finalvestige.com/the-missing-caption/"
EXPECTED_R80_URL = "https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"

class EvidenceRejected(ValueError):
    pass

def _require(condition, reason):
    if not condition:
        raise EvidenceRejected(reason)

def _clean_first_party_url(url):
    _require(type(url) is str, "URL must be string")
    try:
        parsed = urlsplit(url)
    except ValueError as exc:
        raise EvidenceRejected("Malformed URL") from exc
    _require(parsed.scheme == "https" and parsed.netloc == "finalvestige.com", "Only exact first-party HTTPS URLs allowed")
    _require(not parsed.query and not parsed.fragment and not parsed.username and not parsed.password, "No tracking, fragments or credentials")
    _require(parsed.path.startswith("/") and parsed.path.endswith("/"), "Canonical slash-delimited route required")
    return url

def validate(evidence):
    _require(type(evidence) is dict, "Invalid evidence")
    _require(evidence.get("schema") == "fv-dispatch-r84-issue01-route-proof-v1", "Schema unknown")
    _require(evidence.get("evidence_mode") == "READ_ONLY_AUTHENTICATED_WORDPRESS_METADATA", "Source not authenticated")
    _require(evidence.get("observed_on_utc_date") == "2026-11-03", "Snapshot drift")
    _require(evidence.get("analysis_not_publication") is True, "Must remain review only")
    p = evidence["source_control"]
    _require((p["issue"], p["companion"], p["master_pr"], p["first_gate_pr"], p["stacked_parent_pr"]) == (174, 171, 175, 201, 735), "Cross-lane provenance changed")
    c = evidence["campaign"]
    _require(c["release"] == "HOLD_UNSENT", "No release permitted")
    _require(c["mix"] == {"editorial":["01","02","04","06"],"commercial_reserved":["03","05"]}, "Founder's 4:2 ratio changed")
    for flag in ("founder_final_creative_approval","founder_send_approval","newsletter_test_send_approved","mail_scheduled","commercial_permissions_verified"):
        _require(c[flag] is False, "Unauthorised approval claim: " + flag)
    pages = evidence["live_pages"]
    for item in pages.values():
        _require(item["status"] == "publish", "First-party destination not published")
        _clean_first_party_url(item["url"])
    new = pages["change_blindness"]
    _require(new["post_id"] == 1922 and new["slug"] == "change-blindness", "New source post identity drift")
    _require(new["url"] == EXPECTED_NEW_URL, "Exact current destination mismatch")
    _require(new["newsletter_status"] == "never_sent_opted_out", "Do not invent send status")
    _require(new["contains_interactive_flicker_test"] is True and new["interactive_test_requires_browser"] is True, "Browser/transport claim mismatch")
    _require(new["original_lab_test_reproduction"] is False, "False original-lab reproduction")
    _require(pages["missing_caption"]["page_id"] == 1122 and pages["missing_caption"]["url"] == EXPECTED_MASTER_URL, "Original CTA not preserved")
    _require(pages["puysegur"]["page_id"] == 1377 and pages["puysegur"]["url"] == EXPECTED_R80_URL, "R80 CTA not preserved")
    choices = evidence["issue01_cta_options"]
    _require([x["version"] for x in choices] == ["PR175_MASTER", "R80_UNAPPROVED_ALTERNATE", "R84_CANDIDATE"], "Missing exact alternatives")
    _require([x["destination"] for x in choices] == [EXPECTED_MASTER_URL, EXPECTED_R80_URL, EXPECTED_NEW_URL], "CTA option was silently modified")
    _require(all(x["status"] == "PUBLISHED_FIRST_PARTY" for x in choices), "Unpublished CTA option")
    _require([x["approval"] for x in choices] == ["ORIGINAL_DRAFT_ONLY","NOT_APPROVED","NOT_APPROVED"], "Do not claim founder approval")
    issue = evidence["issue01_proposed"]
    _require(issue["single_cta_url"] == EXPECTED_NEW_URL and issue["single_cta_text"] == "Explore the change-blindness evidence and demo", "CTA diverged")
    _require(issue["primary_study"] == "https://doi.org/10.3758/BF03208840", "Study reference changed")
    _require(issue["affiliate_offer"] is False and issue["demonstrated_product_effectiveness"] is False, "No affiliate or efficacy claims")
    _require(issue["preheader_status"] == "UNVERIFIED_JETPACK_CONTROL" and issue["custom_excerpt_status"] == "REVIEW_ONLY_NOT_IN_WORDPRESS", "Invented Jetpack preview")
    _require("1998" in issue["custom_excerpt"] and "demonstration" in issue["custom_excerpt"], "Excerpt does not align with current post")
    channel = evidence["channel"]
    _require(channel["jetpack_enabled"] is True and channel["auto_email_new_posts"] is False and channel["email_content_format"] == "excerpt", "Newsletter setting drift")
    _require(channel["eligible_recipients"] == "UNKNOWN" and channel["subscriber_counts"] == {"total":2,"confirmed":2,"unconfirmed":2}, "Inferred eligible recipient count")
    _require(channel["followers"] == {"email":0,"wpcom":2}, "Followers classification changed")
    for flag in ("welcome_received_verified","real_received_jetpack_email_verified","publisher_postal_verified","unsubscribe_rendered_and_tested"):
        _require(channel[flag] is False, "Transport/legal evidence falsely approved")
    _require(all(v is False for v in evidence["commercial_holds"].values()), "Commercial approval invented")
    _require(evidence["performance"] == {"email_opens":"UNOBSERVED","email_clicks":"UNOBSERVED","affiliate_sales":"UNOBSERVED"}, "Synthetic performance")
    _require(evidence["actual_outbound_campaign_emails_sent"] == 0, "Campaign send invented")
    return "HOLD_UNSENT: Issue 01 R84 offers a published same-topic destination for founder review only."

def preview(evidence):
    decision = validate(evidence)
    choice = evidence["issue01_proposed"]
    return (
        "FINAL VESTIGE DISPATCH | R84 REVIEW ONLY\\n"
        + decision + "\\n"
        + "SUBJECT: " + choice["subject"] + "\\n"
        + "EXCERPT (NOT A RECEIVED EMAIL): " + choice["custom_excerpt"] + "\\n"
        + "SINGLE CTA: " + choice["single_cta_text"] + " — " + choice["single_cta_url"] + "\\n"
        + "RECIPIENT ELIGIBILITY: UNKNOWN; ALL COMMERCIAL OFFERS: HOLD_MERCHANT\\n"
    )

def main():
    evidence = json.loads((HERE / "ROUTE-EVIDENCE.json").read_text(encoding="utf-8"))
    print(preview(evidence))

if __name__ == "__main__":
    main()
