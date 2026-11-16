"""Fail-closed, offline evidence-index validation for one proposed commercial Dispatch issue.

No networking, subscriber access, email sending, or affiliate activation.
Valid records are only *review candidates*, never authenticated partner permission.
"""
from __future__ import annotations

from datetime import date, datetime
import re
from typing import Any

PRODUCTS = {"ZEN12": "03", "TOTAL_FOCUS": "05"}
PARTNER_KINDS = {"named_affiliate_acceptance", "email_channel_permission", "issued_product_earning_link"}
PUBLIC_KINDS = {"sku_terms", "claim_alignment"}
SITE_KINDS = {"published_guide", "email_preview", "postal_address", "operational_unsubscribe", "consent_eligibility", "welcome_receipt"}
REQUIRED = PARTNER_KINDS | PUBLIC_KINDS | SITE_KINDS
AUTHORITY = {
    "named_affiliate_acceptance": "partner_private",
    "email_channel_permission": "partner_private",
    "issued_product_earning_link": "partner_private",
    "sku_terms": "merchant_public",
    "claim_alignment": "editorial_review",
    "published_guide": "first_party_live",
    "email_preview": "native_jetpack_witness",
    "postal_address": "publisher_verified",
    "operational_unsubscribe": "actual_unsubscribe_witness",
    "consent_eligibility": "provider_attested",
    "welcome_receipt": "authorized_receipt_witness",
}
MAX_AGE_DAYS = {"sku_terms": 7, "claim_alignment": 30, "published_guide": 7,
                "email_preview": 14, "consent_eligibility": 7,
                "postal_address": 90, "operational_unsubscribe": 14,
                "welcome_receipt": 90, "named_affiliate_acceptance": 90,
                "email_channel_permission": 90, "issued_product_earning_link": 90}
RECORD_KEYS = {"kind", "product", "authority", "proof_ref", "reviewed_on", "expires_on", "email_scoped"}
INDEX_KEYS = {"schema", "as_of", "issue", "product", "records"}
SAFE_REF = re.compile(r"(?=.{12,90}\Z)[a-z][a-z0-9_-]+\Z")


def _date(value: Any) -> date:
    if type(value) is not str or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("Dates must use YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as err:
        raise ValueError("Invalid calendar date") from err


def audit(index: dict[str, Any]) -> dict[str, Any]:
    """Structural evidence only; a human must independently authenticate every record."""
    if type(index) is not dict or set(index) != INDEX_KEYS:
        raise ValueError("Index schema mismatch or unauthorized fields")
    if index["schema"] != "fv-dispatch-merchant-v1":
        raise ValueError("Unknown schema version")
    product = index["product"]
    if product not in PRODUCTS or index["issue"] != PRODUCTS[product]:
        raise ValueError("Product/issue mismatch")
    as_of = _date(index["as_of"])
    if not isinstance(index["records"], list) or len(index["records"]) > 80:
        raise ValueError("Evidence records must be a bounded array")
    blockers: list[str] = []
    found: set[str] = set()
    for record in index["records"]:
        if type(record) is not dict or set(record) != RECORD_KEYS:
            raise ValueError("Record schema mismatch or unauthorized fields")
        kind = record["kind"]
        if kind not in REQUIRED:
            raise ValueError("Unknown evidence kind")
        if record["product"] != product:
            blockers.append("CROSS_PRODUCT_EVIDENCE_" + kind.upper())
            continue
        if kind in found:
            blockers.append("DUPLICATED_EVIDENCE_KIND_" + kind.upper())
            continue
        found.add(kind)
        if record["authority"] != AUTHORITY[kind]:
            blockers.append("WRONG_AUTHORITY_" + kind.upper())
            continue
        ref = record["proof_ref"]
        if type(ref) is not str or len(ref) > 120 or not SAFE_REF.fullmatch(ref) or any(x in ref for x in ("secret", "token", "password", "sk-proj", "api-key")):
            raise ValueError("Use opaque, non-identifying proof reference only")
        if type(record["email_scoped"]) is not bool:
            raise ValueError("email_scoped must be a real boolean")
        if kind in PARTNER_KINDS and not record["email_scoped"]:
            blockers.append("NOT_EMAIL_SPECIFIC_" + kind.upper())
        reviewed, expires = _date(record["reviewed_on"]), _date(record["expires_on"])
        if reviewed > as_of:
            blockers.append("FUTURE_REVIEW_" + kind.upper())
        if expires < as_of or expires < reviewed:
            blockers.append("EXPIRED_" + kind.upper())
        if (as_of - reviewed).days > MAX_AGE_DAYS[kind]:
            blockers.append("STALE_" + kind.upper())
    for kind in sorted(REQUIRED - found):
        blockers.append("MISSING_" + kind.upper())
    return {
        "release": "HOLD_UNSENT",
        "issue": index["issue"], "product": product,
        "proof_records_present": len(found),
        "structural_review_candidate": not blockers,
        "partner_authorization_authenticated": False,
        "founder_release_approved": False,
        "mail_allowed": False,
        "blockers": sorted(set(blockers)),
        "limits": "Matching metadata cannot authenticate a partner agreement, a live URL, a postal address, recipient consent, an unsubscribe action, or an inbox preview.",
    }
