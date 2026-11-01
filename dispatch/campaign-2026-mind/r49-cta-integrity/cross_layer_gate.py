"""Fail-closed cross-layer consistency check for the ORIGINAL six Dispatch issues.

Runs offline, reads only repository files and never sends, schedules or publishes.
Source manifest is authoritative; fixtures and reviewer material must agree.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from html import escape
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "number", "slug", "subject", "preheader", "kind",
    "editorial_cta", "publish_state", "merchant_affiliate_url",
)
LEGAL = ("[[VALID_POSTAL_ADDRESS_REQUIRED]]", "[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]")
COMMERCIAL = {3, 5}
EDITORIAL = {1, 2, 4, 6}


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def audit(manifest: dict, fixture: dict, ledger: dict, manuscripts: dict[int, str],
          board: str = "") -> dict:
    """Report source drift independently of the always-closed send authorization."""
    errors: list[str] = []
    original = manifest.get("issues", [])
    copies = fixture.get("issues", [])
    entries = ledger.get("entries", [])
    ids = list(range(1, 7))
    if [e.get("number") for e in original] != ids: errors.append("canonical_six_order")
    if [e.get("number") for e in copies] != ids: errors.append("fixture_six_order")
    if [e.get("number") for e in entries] != ids: errors.append("ledger_six_order")
    if manifest.get("mix") != {"editorial": 4, "commercial_review_pending": 2}:
        errors.append("mix_drift")
    if len(original) != 6 or len(copies) != 6 or len(entries) != 6:
        return {"source_errors": errors, "send_authorized": False, "status": "HOLD_UNSENT"}
    for original_item, replica, ledger_item in zip(original, copies, entries):
        n = original_item["number"]
        for field in REQUIRED:
            if original_item.get(field) != replica.get(field):
                errors.append(f"issue_{n}_fixture_{field}_drift")
        if ledger_item.get("cta_expected") != original_item.get("editorial_cta"):
            errors.append(f"issue_{n}_ledger_cta_drift")
        commercial = n in COMMERCIAL
        wanted = "commercial-review-pending" if commercial else "editorial"
        if original_item.get("kind") != wanted:
            errors.append(f"issue_{n}_kind_drift")
        if original_item.get("publish_state") != "hold" or original_item.get("merchant_affiliate_url") is not None:
            errors.append(f"issue_{n}_publication_or_affiliate_activation")
        target = original_item.get("editorial_cta", "")
        if commercial:
            if not target.startswith("[[APPROVED_") or not target.endswith("_REQUIRED]]"):
                errors.append(f"issue_{n}_guide_not_held")
        elif target.startswith("[[") or urlparse(target).scheme != "https" or urlparse(target).netloc != "finalvestige.com":
            errors.append(f"issue_{n}_editorial_destination_invalid")
        body = manuscripts.get(n, "")
        if f"**Subject:** {original_item.get('subject')}" not in body:
            errors.append(f"issue_{n}_manuscript_subject_drift")
        if f"**Preheader:** {original_item.get('preheader')}" not in body:
            errors.append(f"issue_{n}_manuscript_preheader_drift")
        if target not in body:
            errors.append(f"issue_{n}_manuscript_primary_cta_drift")
        if any(token not in body for token in LEGAL):
            errors.append(f"issue_{n}_missing_legal_hard_stop")
        if "STATUS: UNSENT DRAFT" not in body:
            errors.append(f"issue_{n}_unsafe_draft_header")
        if commercial and "Commercial disclosure:" not in body:
            errors.append(f"issue_{n}_missing_commercial_disclosure")
        if board:
            if escape(original_item.get("preheader", ""), quote=True).replace("&#x27;", "&#x27;") not in board:
                errors.append(f"issue_{n}_reviewer_preheader_drift")
            if ledger_item.get("destination_status", "") not in board:
                errors.append(f"issue_{n}_reviewer_destination_drift")
    if board and board.count('class="card ') != 6:
        errors.append("reviewer_not_six_cards")
    return {
        "source_errors": sorted(set(errors)),
        "send_authorized": False,
        "status": "HOLD_UNSENT",
        "commercial_issues": [3, 5],
        "verified_unique_eligible_recipients": None,
        "actual_received_jetpack_email_verified": False,
        "merchant_product_specific_email_rights_verified": False,
        "physical_postal_address_verified": False,
        "unsubscribe_received_email_verified": False,
        "founder_final_send_approval": False,
    }


def load_and_audit(root: Path = ROOT) -> dict:
    manifest = read(root / "manifest.json")
    fixture = read(root / "readiness/fixtures/manifest_snapshot.json")
    ledger = read(root / "readiness/canonical_cta_ledger.json")
    manuscripts = {
        item["number"]: (root / "issues" / f"{item['number']:02d}-{item['slug']}.md").read_text(encoding="utf-8")
        for item in manifest["issues"]
    }
    board = (root / "readiness/review_board.html").read_text(encoding="utf-8")
    return audit(manifest, fixture, ledger, manuscripts, board)


if __name__ == "__main__":
    result = load_and_audit()
    print(json.dumps(result, sort_keys=True, indent=2))
    raise SystemExit(1 if result["source_errors"] else 0)
