"""R417 read-only, deny-by-default buyer-surface/permission audit. Does not send or activate URLs."""
from __future__ import annotations
import json
import pathlib
import re
from urllib.parse import urlsplit

REQUIRED_PRIVATE = (
    "first_party_guide", "earning_link", "affiliate_acceptance_document",
    "email_channel_authorization", "named_account_owner",
    "referred_checkout_capture", "merchant_payout_record",
)
REQUIRED_GLOBAL = (
    "publisher_physical_address_rendered", "native_jetpack_preview_witness",
    "functional_unsubscribe_witness", "eligible_recipient_deduplication",
    "welcome_receipt_witness", "founder_final_send_approval",
)
APPROVED_SOURCE_HOSTS = {"zen12.com", "hypnosislive.com", "affiliates.inspire3.com"}


def audit(record: dict) -> dict:
    """Reject public-copy-as-permission, mixed SKUs, stale price assertions and send readiness."""
    if not isinstance(record, dict) or record.get("schema") != "fv-dispatch-offer-surface-v1":
        raise ValueError("Unrecognized evidence schema")
    sources = record.get("sources", {})
    offers = record.get("offers", {})
    if set(offers) != {"issue03_zen12", "issue05_total_focus"}:
        raise ValueError("Campaign must preserve two original commercial slots")
    results = {}
    for key, offer in offers.items():
        if offer.get("issue") != (3 if key == "issue03_zen12" else 5):
            raise ValueError("Commercial issue number mismatched")
        problems = []
        for field in REQUIRED_PRIVATE:
            value = offer.get(field)
            if not isinstance(value, dict) or not value.get("authenticated") or not value.get("verified_by"):
                problems.append("MISSING_AUTHENTICATED_" + field.upper())
        if offer.get("price_message_allowed"):
            problems.append("PRICE_CANNOT_BE_CLAIMED_FROM_PUBLIC_SURFACE")
        if offer.get("refund_message_allowed"):
            problems.append("REFUND_NOT_VERIFIED_AT_REFERRED_CHECKOUT")
        if offer.get("efficacy_claim_allowed"):
            problems.append("SKU_SPECIFIC_EFFICACY_NOT_VERIFIED")
        prices = set()
        contexts = set()
        for surface in offer.get("surfaces", []):
            source = sources.get(surface.get("source_key"), "")
            host = (urlsplit(source).hostname or "").lower()
            if host not in APPROVED_SOURCE_HOSTS or urlsplit(source).scheme != "https":
                raise ValueError("Merchant source not an official HTTPS merchant host")
            if not surface.get("description") or not surface.get("buyer_decision"):
                problems.append("MISSING_SURFACE_CONTEXT")
            for p in surface.get("displayed_prices_usd", []):
                if not re.fullmatch(r"[0-9]+\.[0-9]{2}", str(p)):
                    raise ValueError("Price format not numeric decimal")
                prices.add(str(p))
            contexts.add(surface.get("description", ""))
        if len(prices) > 1:
            problems.append("MULTIPLE_PUBLIC_PRICE_CONTEXTS_NOT_REFERRED_CHECKOUT")
        if not contexts:
            problems.append("NO_MERCHANT_SURFACE_OBSERVATIONS")
        if offer.get("earning_link") and not isinstance(offer["earning_link"], dict):
            problems.append("PUBLIC_URL_IS_NOT_AFFILIATE_ACCOUNT_EVIDENCE")
        results[key] = {"decision": "HOLD_MERCHANT", "problems": sorted(set(problems)),
                        "public_price_context_count": len(prices)}
    for global_key in REQUIRED_GLOBAL:
        if record.get("global_release_proofs", {}).get(global_key) is not True:
            for entry in results.values():
                entry["problems"].append("GLOBAL_" + global_key.upper() + "_UNVERIFIED")
    return {"decision": "HOLD_UNSENT", "offers": results,
            "note": "No code path authorizes a send, creates a link or calls a provider."}


def main() -> None:
    path = pathlib.Path(__file__).with_name("OFFER_SURFACE_SNAPSHOT.json")
    print(json.dumps(audit(json.loads(path.read_text(encoding="utf-8"))), indent=2))


if __name__ == "__main__":
    main()
