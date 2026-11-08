"""Read-only R95 merchant-authorization and claim-conflict review for Dispatch 03/05.

Completeness check only: cannot verify real permissions or authorize sending.
No network, subscriber data, email, merchant traffic, or WordPress operations.
"""
from __future__ import annotations
import json
from pathlib import Path
from urllib.parse import urlsplit

EXPECTED = {"03": "zen12", "05": "hypnosis-live-total-focus"}
REQUIRED = (
    "named_final_vestige_acceptance", "email_channel_permission_for_this_product",
    "approved_link_format", "creative_reuse_terms", "verified_guide_live",
    "buyer_pii_exclusion_in_writing", "price_and_terms_reconfirmed",
    "publisher_postal_and_unsubscribe_received", "qualified_email_recipients_verified",
    "final_founder_campaign_approval", "genuine_jetpack_received_preview",
)
SOURCE_HOSTS = {"zen12.com", "hypnosislive.com", "inspire3.com", "affiliates.inspire3.com"}
DANGEROUS = {"affiliate_url", "tracking_url", "coupon", "buyer_email", "buyer_name",
             "subscriber_email", "phone_number", "address", "password", "token"}

class EvidenceError(ValueError):
    pass

def inspect(data: dict) -> dict:
    if not isinstance(data, dict) or data.get("project") != "fv-dispatch-r95-proof-hold":
        raise EvidenceError("unknown project or invalid ledger")
    if data.get("campaign_mix") != {"editorial": [1, 2, 4, 6], "commercial_reserved": [3, 5]}:
        raise EvidenceError("canonical 4:2 mix drift")
    if data.get("all_issues_status") != "HOLD_UNSENT":
        raise EvidenceError("campaign status must remain HOLD_UNSENT")
    if data.get("recipient_eligibility") is not None:
        raise EvidenceError("subscriber count not established")
    slots = data.get("product_slots")
    if not isinstance(slots, list) or [str(s.get("edition")) for s in slots] != list(EXPECTED):
        raise EvidenceError("exact 03/05 merchant slots required")
    results = []
    for item in slots:
        n = str(item["edition"])
        if item.get("product_key") != EXPECTED[n]:
            raise EvidenceError("product mismatch")
        if item.get("approval_state") != "NOT_VERIFIED" or item.get("affiliate_url") is not None:
            raise EvidenceError("affiliate not approved")
        proofs = item.get("proofs")
        if not isinstance(proofs, dict) or set(proofs) != set(REQUIRED):
            raise EvidenceError("missing or unexpected proof fields")
        if any(v is not False for v in proofs.values()):
            raise EvidenceError("unverified external proof promoted to verified")
        sources = item.get("merchant_sources")
        if not isinstance(sources, list) or len(sources) < 2:
            raise EvidenceError("source-of-truth merchant pages absent")
        for url in sources:
            if not isinstance(url, str):
                raise EvidenceError("source must be URL")
            p = urlsplit(url)
            if p.scheme != "https" or p.hostname not in SOURCE_HOSTS or p.username or p.password or p.fragment:
                raise EvidenceError("merchant source invalid")
        findings = item.get("material_claim_conflicts")
        if not isinstance(findings, list) or not findings or any(
            not isinstance(x, dict) or x.get("resolution") != "NOT_VERIFIED" or not x.get("finding")
            for x in findings
        ):
            raise EvidenceError("merchant differences must remain unresolved")
        results.append({
            "edition": int(n), "product_key": item["product_key"],
            "approval": "HOLD_MERCHANT", "missing_external_proofs": list(REQUIRED),
            "source_count": len(sources), "open_claim_conflicts": len(findings)
        })
    dumped = json.dumps(data, ensure_ascii=False).lower()
    for k in DANGEROUS - {"affiliate_url"}:
        if f'"{k}"' in dumped:
            raise EvidenceError("private/activated field forbidden")
    return {
        "campaign": "HOLD_UNSENT", "real_delivery_evidence": "NOT_VERIFIED",
        "external_merchant_authorization": "NOT_VERIFIED", "ready_to_send": False,
        "editions": results
    }

def main():
    data = json.loads((Path(__file__).parent / "merchant_evidence.json").read_text(encoding="utf-8"))
    print(json.dumps(inspect(data), indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
