#!/usr/bin/env python3
"""R451 read-only proof gate. Integrity and eligibility are NOT editorial or sale verification."""
from pathlib import Path
from urllib.parse import urlsplit
import hashlib
import json
import re

BASE = Path(__file__).resolve().parents[2]
SOURCE = BASE / "apollo-r448/manifest.json"
R450 = BASE / "apollo-r450/QA/BROWSER.json"
PIN = "744ec9c2ca46693f116c7ea5a1edf4ec3416083384e11ade0d0b63ca900a9411"
URLS = (
    "https://www.nasa.gov/gallery/apollo-1/",
    "https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/",
    "https://www.nasa.gov/news-release/nasa-unveils-tribute-to-crew-of-apollo-1/",
    "https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/",
)
IDS = ("training", "review-board", "memorial", "flammability")
DATES = ("1966-10-18", "1967-01-27", "2017-01-27", "2018-02-14")
FREE = "https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"

def source_contract(source=SOURCE):
    if not source.is_file() or source.is_symlink() or hashlib.sha256(source.read_bytes()).hexdigest() != PIN:
        raise ValueError("HOLD: source bytes differ from reviewed R448")
    data = json.loads(source.read_text(encoding="utf-8"))
    rows = data.get("claims", [])
    if (data.get("schema") != "fv-apollo-claim-custody-v1"
        or data.get("release_approved") is not False
        or data.get("editorial_approval") != "PENDING_INDEPENDENT_QD"
        or data.get("paid_offer_status") != "NO_VERIFIED_APOLLO_SKU"
        or not isinstance(rows, list) or len(rows) != 4):
        raise ValueError("HOLD: source custody contract changed")
    if tuple(r.get("id") for r in rows) != IDS or tuple(r.get("date") for r in rows) != DATES:
        raise ValueError("HOLD: chronology or custody IDs changed")
    if tuple(r.get("source_url") for r in rows) != URLS:
        raise ValueError("HOLD: source destination changed")
    for row in rows:
        for name in ("title", "date_context", "supported", "not_supported", "rights"):
            if not isinstance(row.get(name), str) or not row[name].strip():
                raise ValueError("HOLD: missing source interpretation/limitation")
    return rows

def creator_contract(evidence):
    """Even an apparently valid URL does not prove actual publication or linked attribution."""
    needs = ("asset_id", "platform_post_url", "published_date", "approved_landing_url",
             "independent_praxxis_review_ref")
    gaps = [x for x in needs if not isinstance(evidence.get(x), str) or not evidence[x].strip()]
    url = urlsplit(evidence.get("platform_post_url") or "")
    if url.scheme != "https" or url.hostname not in (
        "www.youtube.com", "youtube.com", "youtu.be", "www.tiktok.com", "tiktok.com"
    ) or url.username or url.password:
        gaps.append("authentic allowed platform URL")
    if evidence.get("verified_publication") is not True: gaps.append("verified published asset")
    if evidence.get("approved_landing_url") != "https://finalvestige.com/apollo-1-evidence-atlas/":
        gaps.append("approved exact landing destination")
    if not re.fullmatch(r"20\d{2}-\d{2}-\d{2}", evidence.get("published_date") or ""):
        gaps.append("publication date")
    return gaps

def commerce_contract(evidence):
    """Structural gate only, NEVER authorizes payment or infers sales from clicks."""
    needed = ("seller_ref", "sku", "rights_ref", "checkout_url", "fulfillment_ref",
              "refunds_and_fees_ref", "founder_approval_ref")
    gaps = [x for x in needed if not isinstance(evidence.get(x), str) or not evidence[x].strip()]
    url = urlsplit(evidence.get("checkout_url") or "")
    if url.scheme != "https" or not url.hostname or url.username or url.password:
        gaps.append("verified HTTPS merchant destination")
    if evidence.get("status") != "AUTHENTICATED_PAYABLE": gaps.append("authenticated sellable SKU")
    if evidence.get("commercial_cta_enabled") is not False:
        gaps.append("commercial CTA cannot be enabled from QA")
    return gaps

def run(creator=None, commerce=None):
    source_contract()
    prior = json.loads(R450.read_text(encoding="utf-8"))
    if (prior.get("status") != "PASS" or prior.get("mode", "").find("page.set_content") < 0
        or prior.get("axe_core") != "NOT_RUN"
        or prior.get("navigated_LCP_CLS") != "NOT_RUN"):
        raise ValueError("HOLD: inherited local-only QA evidence drift")
    gaps_creator = creator_contract(creator or {})
    gaps_offer = commerce_contract(commerce or {})
    return {
        "source_manifest_sha256": PIN,
        "source_record_count": 4,
        "r450_local_browser": "PASS_OFFLINE_ONLY",
        "real_wordpress_staging": "NOT_RUN",
        "axe_core": "NOT_RUN", "navigated_LCP_CLS": "NOT_RUN",
        "screen_reader": "NOT_RUN", "field_CWV": "NOT_VERIFIED",
        "creator_publication": "NOT_VERIFIED" if gaps_creator else "STRUCTURAL_ONLY",
        "payable_offer": "NOT_VERIFIED" if gaps_offer else "STRUCTURAL_ONLY",
        "net_revenue_per_1000_qualified_humans": None,
        "release": "HARD_HOLD",
        "creator_missing": gaps_creator,
        "commerce_missing": gaps_offer,
        "single_free_investigation": FREE,
        "note": "No live activation; structural proof never authorizes merchant sales, NASA media rights, or production deployment."
    }

if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
