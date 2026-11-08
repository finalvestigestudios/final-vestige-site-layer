"""R37 independent, read-only merchant citation route audit.

Audit source, generated email-preview markup and Gutenberg proof. Known existing
legacy seller hyperlinks are a release blocker, not an approval. This script is
incapable of sending email, changing WordPress, or activating earning links.
"""
from __future__ import annotations
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

RELATIVE_ROOT = Path(__file__).resolve().parents[1]
CANONICAL = RELATIVE_ROOT / "issues"
PREVIEW = RELATIVE_ROOT / "previews"
GUTENBERG = RELATIVE_ROOT / "wordpress-post-bridge-r23/proofs"
CANDIDATE = Path(__file__).resolve().parent
KNOWN_MERCHANT_HOSTS = frozenset({
    "zen12.com", "www.zen12.com", "hypnosislive.com",
    "www.hypnosislive.com", "affiliates.inspire3.com",
    "go.inspire3.com", "hop.clickbank.net",
})
SOURCE_URLS = (
    "https://zen12.com/",
    "https://zen12.com/about",
)


def is_merchant_url(raw: str) -> bool:
    """Check parsed hostname, not attacker-controlled string containment."""
    try:
        p = urlsplit(raw.strip())
        h = (p.hostname or "").lower().rstrip(".")
        return p.scheme.lower() in {"http", "https"} and h in KNOWN_MERCHANT_HOSTS
    except ValueError:
        return False


class AnchorReader(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.targets: list[str] = []

    def handle_starttag(self, tag, attrs) -> None:
        if tag.lower() == "a":
            for key, value in attrs:
                if key.lower() == "href" and value:
                    self.targets.append(value)


def html_links(source: str) -> list[str]:
    p = AnchorReader()
    p.feed(source)
    p.close()
    return p.targets


def md_links(source: str) -> list[str]:
    return re.findall(r"\[[^\]\n]+\]\((https?://[^\s)]+)\)", source)


def raw_merchant_urls(source: str) -> list[str]:
    # Detect plain URLs, which some email clients may automatically hyperlink.
    urls = re.findall(r"https?://[^\s<>'\"\)]+", source, re.I)
    return [u.rstrip(".,;") for u in urls if is_merchant_url(u.rstrip(".,;"))]


def route_report(source: str, fmt: str) -> dict:
    anchors = html_links(source) if fmt == "html" else md_links(source) if fmt == "md" else []
    risky = [u for u in anchors if is_merchant_url(u)]
    # Plaintext has no explicit link syntax; raw URLs are potentially clickable.
    if fmt == "txt":
        risky = raw_merchant_urls(source)
    return {
        "merchant_route_count": len(risky),
        "merchant_hosts": sorted(set((urlsplit(u).hostname or "").lower() for u in risky)),
        "contains_research_link": "www.nccih.nih.gov" in source,
        "approved_merchant_link_exists": False,
    }


def inspect(root: Path = RELATIVE_ROOT) -> dict:
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    errors: list[str] = []
    if manifest.get("status") != "DRAFT_UNSENT_NO_SCHEDULING" or manifest.get("mix") != {"editorial": 4, "commercial_review_pending": 2}:
        errors.append("campaign_hold_or_4_2_mix_modified")
    records = []
    for i, info in enumerate(manifest["issues"], 1):
        slug = info["slug"]
        if info.get("number") != i or info.get("publish_state") != "hold" or info.get("merchant_affiliate_url") is not None:
            errors.append(f"issue_{i:02d}_activated_or_reordered")
        md = (root / "issues" / f"{i:02d}-{slug}.md").read_text(encoding="utf-8")
        ht = (root / "previews" / f"{i:02d}-{slug}.html").read_text(encoding="utf-8")
        rec = {"issue": i, "kind": info["kind"], "source": route_report(md, "md"), "email_preview": route_report(ht, "html"), "send_authorized": False}
        if i == 3:
            gut = (root / "wordpress-post-bridge-r23/proofs/issue-03.blocks.html").read_text(encoding="utf-8")
            rec["gutenberg_candidate"] = route_report(gut, "html")
            if [rec["source"]["merchant_route_count"], rec["email_preview"]["merchant_route_count"], rec["gutenberg_candidate"]["merchant_route_count"]] != [2, 2, 2]:
                errors.append("legacy_issue_03_seller_route_changed_review_again")
            if "**Commercial disclosure:**" not in md or "[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]" not in md:
                errors.append("zen12_disclosure_or_guide_hold_lost")
        elif rec["source"]["merchant_route_count"] or rec["email_preview"]["merchant_route_count"]:
            errors.append(f"new_merchant_bypass_issue_{i:02d}")
        records.append(rec)
    cand = {}
    for filename, fmt in [
        ("ISSUE_03_NO_MERCHANT_ROUTE_REVIEW.md", "md"),
        ("ISSUE_03_NO_MERCHANT_ROUTE_REVIEW.html", "html"),
        ("ISSUE_03_NO_MERCHANT_ROUTE_REVIEW.txt", "txt"),
        ("ISSUE_03_GUTENBERG_NO_MERCHANT_ROUTE_REVIEW.blocks.html", "html"),
    ]:
        source = (root / "r37-merchant-route-proof" / filename).read_text(encoding="utf-8")
        audit = route_report(source, fmt)
        if audit["merchant_route_count"] or raw_merchant_urls(source):
            errors.append(f"candidate_merchant_bypass_{filename}")
        if "APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED" not in source and "GUIDE NOT LIVE" not in source:
            errors.append(f"candidate_guide_hold_missing_{filename}")
        cand[filename] = audit
    return {
        "status": "HOLD_UNSENT_AND_MERCHANT",
        "finding": "Legacy Issue 03 links directly to Zen12 selling pages, bypassing unpublished first-party guide.",
        "existing_legacy_issue_03_seller_links_across_three_surfaces": 6,
        "legacy_risks": records,
        "no_merchant_link_review_candidate": cand,
        "regression_errors": errors,
        "current_legacy_route_requires_editorial_repair": True,
        "merchant_permission_verified": False,
        "live_warmup_guide_verified": False,
        "postal_unsubscribe_in_received_email_verified": False,
        "founder_send_approval": False,
        "send_authorized": False,
        "site_mutation_or_send_performed": False,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=RELATIVE_ROOT)
    args = p.parse_args(argv)
    result = inspect(args.root)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not result["regression_errors"] else 1  # never send-ready


if __name__ == "__main__":
    raise SystemExit(main())
