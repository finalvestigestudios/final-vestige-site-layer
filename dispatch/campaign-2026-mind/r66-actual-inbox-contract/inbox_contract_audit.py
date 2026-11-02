"""Read-only approximation of the actual Jetpack excerpt risk; never sends email.

Run from the repository root:
python -I dispatch/campaign-2026-mind/r66-actual-inbox-contract/inbox_contract_audit.py
WordPress's real renderer MUST be checked separately. No auth, network, PII or writes.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
MASTER = ROOT / "manifest.json"
R61 = ROOT / "r61-excerpt-consent" / "excerpt_packet.json"
ISSUES = ROOT / "issues"

class EvidenceError(ValueError):
    """Unsafe, internally contradictory campaign evidence."""

def read_campaign():
    manifest = json.loads(MASTER.read_text(encoding="utf-8"))
    optional = json.loads(R61.read_text(encoding="utf-8"))
    if len(manifest["issues"]) != 6 or len(optional["issues"]) != 6:
        raise EvidenceError("Expected six canonical and six optional editions")
    if manifest.get("status") != "DRAFT_UNSENT_NO_SCHEDULING":
        raise EvidenceError("Canonical campaign is no longer held")
    if any(i.get("publish_state") != "hold" or i.get("merchant_affiliate_url") is not None for i in manifest["issues"]):
        raise EvidenceError("Publication/merchant activation would invalidate this audit")
    if optional.get("status") != "ALL_HOLD_UNSENT":
        raise EvidenceError("Optional excerpts are not held")
    return manifest, optional

def body_from_markdown(source):
    """Start at editorial body, not DRAFT preflight/header or legal placeholder."""
    parts = re.split(r"\n---\s*\n", source, maxsplit=1)
    if len(parts) < 2:
        raise EvidenceError("Missing canonical editorial body separator")
    body = re.split(r"\n---\s*\n", parts[1], maxsplit=1)[0]
    if not body.strip():
        raise EvidenceError("Missing editorial body")
    body = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", body)
    body = re.sub(r"(?m)^\s*[-*]\s+", "", body)
    body = re.sub(r"[*_#]", "", body)
    return re.sub(r"\s+", " ", body).strip()

def first_words(body, limit=55):
    """Editorial surrogate only: NOT WordPress/JETPACK browser/email rendering."""
    if not isinstance(limit, int) or limit < 1:
        raise EvidenceError("Unsafe word limit")
    return " ".join(body.split()[:limit])

def audit_data(manifest, options):
    original = sorted(manifest["issues"], key=lambda x:x["number"])
    optional = sorted(options["issues"], key=lambda x:x["number"])
    if [z["number"] for z in original] != [1,2,3,4,5,6]:
        raise EvidenceError("Canonical issue numbering invalid")
    if [z["number"] for z in optional] != [1,2,3,4,5,6]:
        raise EvidenceError("Optional excerpt numbering invalid")
    out = []
    for entry, proposed in zip(original, optional):
        number = entry["number"]
        file = next(iter(sorted(ISSUES.glob(f"{number:02d}-*.md"))), None)
        if file is None:
            raise EvidenceError(f"Missing canonical file for {number}")
        source = file.read_text(encoding="utf-8")
        if entry["subject"] not in source:
            raise EvidenceError(f"Subject mismatch between canonical manifest and file {number}")
        sample = first_words(body_from_markdown(source))
        commercial = entry["kind"] == "commercial-review-pending"
        same_kind = proposed.get("kind") == entry["kind"]
        if not same_kind:
            raise EvidenceError(f"Optional excerpt changed issue class {number}")
        opt_text = proposed.get("excerpt", "")
        opt_link = proposed.get("cta_url")
        if not opt_text or not isinstance(opt_text, str):
            raise EvidenceError(f"Missing optional preview excerpt {number}")
        if commercial and (opt_link is not None or entry["merchant_affiliate_url"] is not None):
            raise EvidenceError(f"Commercial route activated {number}")
        sample_disclosure = "commercial disclosure:" in sample.lower() or "commission" in sample.lower()
        opt_disclosure = "commission" in opt_text.lower()
        out.append({
            "issue":number,
            "kind":entry["kind"],
            "canonical_subject":entry["subject"],
            "optional_subject":proposed.get("subject"),
            "subject_exact_match":entry["subject"] == proposed.get("subject"),
            "default_55_word_surrogate":sample,
            "default_surrogate_has_commission_disclosure":sample_disclosure,
            "optional_custom_excerpt":opt_text,
            "optional_excerpt_contains_commission_note":opt_disclosure,
            "optional_cta_url":opt_link,
            "canonical_cta":entry["editorial_cta"],
            "risk":"LATE_DISCLOSURE_AND_UNPUBLISHED_GUIDE" if commercial else "FULL_BODY_AND_CTA_NOT_GUARANTEED",
            "hold":"HOLD_MERCHANT_AND_UNSENT" if commercial else "HOLD_UNSENT"
        })
    return out

def audit():
    manifest, options = read_campaign()
    data = audit_data(manifest, options)
    commercial = [row for row in data if row["kind"]=="commercial-review-pending"]
    if len(commercial) != 2 or [i["issue"] for i in commercial] != [3, 5]:
        raise EvidenceError("Original 4:2 mix has changed")
    if any(i["default_surrogate_has_commission_disclosure"] for i in commercial):
        raise EvidenceError("Expected late-disclosure issue changed; independently review before reusing")
    if any(not i["optional_excerpt_contains_commission_note"] for i in commercial):
        raise EvidenceError("Proposed commercial excerpt lacks commission disclosure")
    if "fourteen" not in data[3]["canonical_subject"].lower():
        raise EvidenceError("Apollo subject was modified; review the changed premise")
    return {
      "mode":"READ_ONLY_SIMULATION_NOT_JETPACK_MIME",
      "source":"canonical PR #175 + R61 proposal; actual live email_content_format=excerpt",
      "as_of":"2026-11-02",
      "release":"ALL_6_HOLD_UNSENT",
      "commercial":"03_AND_05_HOLD_MERCHANT",
      "founder_approved":False,
      "real_received_email_verified":False,
      "pending_jetpack_preview":True,
      "issue_count":6,
      "issue_rows":data
    }

if __name__ == "__main__":
    print(json.dumps(audit(), ensure_ascii=False, indent=2))
