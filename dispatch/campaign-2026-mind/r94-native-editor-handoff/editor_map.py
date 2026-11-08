"""Read-only Jetpack editor field map for six UNSENT Dispatch editions.

Consumes the original PR #175 manifest and R92's optional excerpt candidates.
Never calls a network/API, creates WordPress objects, or permits sending.
Run: python -I dispatch/campaign-2026-mind/r94-native-editor-handoff/editor_map.py
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parent
MASTER = CAMPAIGN / "manifest.json"
R92 = CAMPAIGN / "r92-excerpt-mode-truth" / "candidate_excerpts.json"
MASTER_SHA = "d57ccdba3aee8f065e143e101c2945f4f3d01647"
COMMERCIAL = {3, 5}
EXPECTED = [1, 2, 3, 4, 5, 6]
SOURCE_FILES = {
    1: "issues/01-the-mind-is-not-a-camera.md",
    2: "issues/02-before-hypnosis-had-a-name.md",
    3: "issues/03-the-twelve-minute-question.md",
    4: "issues/04-the-hatch-and-the-spark.md",
    5: "issues/05-before-you-press-play.md",
    6: "issues/06-the-evidence-log.md",
}

class ContractError(ValueError):
    pass

def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def verified_first_party(url: str) -> bool:
    parsed = urlsplit(url)
    return parsed.scheme == "https" and parsed.hostname == "finalvestige.com" and not (
        parsed.username or parsed.password or parsed.port or parsed.query or parsed.fragment
    )

def build(master: dict, r92: dict) -> dict:
    if master.get("status") != "DRAFT_UNSENT_NO_SCHEDULING":
        raise ContractError("Master release state changed")
    if r92.get("master_sha") != MASTER_SHA or r92.get("campaign_state") != "DRAFT_NO_SEND":
        raise ContractError("Pin mismatch or R92 release state changed")
    original = master.get("issues", [])
    proposed = r92.get("issues", [])
    if [i.get("number") for i in original] != EXPECTED or [i.get("number") for i in proposed] != EXPECTED:
        raise ContractError("Missing, repeated, or reordered campaign edition")
    kinds = [i.get("kind") for i in original]
    if kinds.count("editorial") != 4 or [i["number"] for i in original if i["kind"] == "commercial-review-pending"] != [3, 5]:
        raise ContractError("Original 4:2 allocation changed")
    native = r92["native_wordpress_expectation"]
    settings = r92["settings_snapshot"]
    if settings["email_content_format"] != "excerpt" or settings["email_new_posts_by_default"] is not False:
        raise ContractError("Expected Jetpack sending/excerpt setting drift")
    if native["custom_preheader_control_verified"] is not False or native["actual_mime_verified"] is not False:
        raise ContractError("Inbox rendering evidence has changed: reacquire proof")
    if settings["eligible_email_recipients"] is not None:
        raise ContractError("Unverified email recipient count inserted")
    if settings["founder_final_send_approval"] is not False:
        raise ContractError("Unexpected release authorization")
    entries = []
    for x, p in zip(original, proposed):
        n = x["number"]
        if x["kind"] != p["kind"] or p["status"] != "HOLD_UNSENT":
            raise ContractError(f"Issue {n}: category or hold state mismatch")
        if x["merchant_affiliate_url"] is not None or p["active_affiliate_url"] is not None:
            raise ContractError(f"Issue {n}: a commercial link was activated")
        title = p["subject_candidate"]
        excerpt = p["excerpt_text"]
        if not isinstance(title, str) or not isinstance(excerpt, str):
            raise ContractError(f"Issue {n}: missing copy")
        if not 16 <= len(title) <= 90 or "\n" in title or "[[" in title:
            raise ContractError(f"Issue {n}: unsafe proposed post title")
        if not 60 <= len(excerpt) <= 750 or "[[" in excerpt or "]]" in excerpt:
            raise ContractError(f"Issue {n}: incomplete excerpt candidate")
        if any(s in excerpt.lower() for s in ("https://", "http://", "utm_", "guaranteed to")):
            raise ContractError(f"Issue {n}: merchant/tracking claims or links in excerpt")
        if not (CAMPAIGN / SOURCE_FILES[n]).is_file():
            raise ContractError(f"Issue {n}: original manuscript missing")
        if n in COMMERCIAL:
            if not excerpt.startswith("Commercial note:") or not p["commercial_note"] or not excerpt.startswith(p["commercial_note"]):
                raise ContractError(f"Issue {n}: pre-recommendation disclosure absent")
            if p["approved_guide_url"] is not None or p["editorial_source_url"] is not None:
                raise ContractError(f"Issue {n}: nonlive product guide activated")
            source_destination = None
        else:
            source_destination = p["editorial_source_url"]
            if not verified_first_party(source_destination):
                raise ContractError(f"Issue {n}: invalid first-party destination")
            if p["commercial_note"] is not None:
                raise ContractError(f"Issue {n}: editorial issue unexpectedly commercial")
        entries.append({
            "edition": n,
            "purpose": "commercial review reserved; NOT authorized" if n in COMMERCIAL else "editorial only",
            "source_manuscript": SOURCE_FILES[n],
            "canonical_original_subject": x["subject"],
            "alternative_post_title_for_review": title,
            "alternative_subject_change_requires_approval": title != x["subject"],
            "alternative_post_excerpt_for_review": excerpt,
            "editor_post_type_if_authorized_later": "post",
            "draft_post_state_if_authorized_later": "draft",
            "must_leave_send_to_subscribers_off": True,
            "publisher_post_permalink": None,
            "native_inbox_read_more_target": "future WordPress post permalink; NOT the source URL",
            "source_article_for_post_body_only": source_destination,
            "custom_inbox_preheader": None,
            "custom_preheader_supported_by_this_site": "NOT VERIFIED",
            "affiliate_tracking_url": None,
            "affiliate_promotion_authorized": False,
            "guide_link_authorized": False,
            "is_wordpress_api_payload": False,
            "is_authorized_to_create_wordpress_draft": False,
            "is_authorized_to_send_test_or_real_email": False,
            "release_decision": "HOLD_UNSENT",
        })
    return {
        "package": "r94-read-only-human-editor-handoff",
        "source_master_pr": 175,
        "source_master_commit": MASTER_SHA,
        "source_candidate_pr": 796,
        "all_six": "HOLD_UNSENT",
        "merchant_issue_numbers": [3, 5],
        "these_are_editor_notes_not_valid_wp_api_payloads": True,
        "per_post_send_toggle_must_remain_off": True,
        "site_can_send_messages_even_when_auto_new_post_default_off": True,
        "subscriber_eligibility": "UNKNOWN",
        "actual_jetpack_preview_and_received_mime": "NOT VERIFIED",
        "publisher_postal_address_and_unsubscribe": "NOT VERIFIED",
        "inbox_subject_is_based_on_post_title": True,
        "campaign_preheaders_are_editing_candidates_not_confirmed_inbox_fields": True,
        "original_manuscripts_are_NOT_inbox_content_when_jetpack_mode_excerpt": True,
        "source_to_guide_redirect_is_NOT_the_jetpack_read_more_destination": True,
        "founder_final_campaign_approval": False,
        "entries": entries,
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="print HUMAN REVIEW map; not a WordPress API payload")
    ns = parser.parse_args()
    try:
        result = build(read_json(MASTER), read_json(R92))
    except (KeyError, TypeError, ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(f"HOLD: cannot assemble editorial review map: {type(exc).__name__}: {exc}")
        return 1
    if ns.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("PASS: six offline human-review cards assembled; 4 editorial + 2 commercial slots")
        print("ALL HOLD_UNSENT; NO WordPress API payload, post, subscriber action, test email or send")
        print("NEEDS: explicit approval of any revised titles/excerpts, delivery format and actual native preview")
        for issue in result["entries"]:
            print(f'{issue["edition"]:02d} {issue["alternative_post_title_for_review"]} — HOLD')
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
