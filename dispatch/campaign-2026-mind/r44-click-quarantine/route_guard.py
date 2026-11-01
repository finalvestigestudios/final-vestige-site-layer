"""R44 unsent commercial preview clickpath auditor. Read-only, never authorizes mailing."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlsplit
import json
import re

CAMPAIGN = Path(__file__).resolve().parents[1]
MERCHANT_HOSTS = ("zen12.com", "hypnosislive.com", "inspire3.com")
REDIRECT_KEYS = frozenset({"url", "u", "redirect", "redirect_url", "redirect_uri",
                           "destination", "dest", "target", "next", "to", "continue"})
REVIEW_INPUTS = {
    "03_canonical_markdown": ("issues/03-the-twelve-minute-question.md", "md"),
    "03_original_html": ("previews/03-the-twelve-minute-question.html", "html"),
    "03_original_gutenberg": ("wordpress-post-bridge-r23/proofs/issue-03.blocks.html", "html"),
    "05_canonical_markdown": ("issues/05-before-you-press-play.md", "md"),
    "05_original_html": ("previews/05-before-you-press-play.html", "html"),
    "05_original_gutenberg": ("wordpress-post-bridge-r23/proofs/issue-05.blocks.html", "html"),
    "03_optional_r37": ("r37-merchant-route-proof/ISSUE_03_NO_MERCHANT_ROUTE_REVIEW.html", "html"),
    "05_optional_r38": ("r38-totalfocus-single-cta/ISSUE_05_REVIEW_CANDIDATE.html", "html"),
}

@dataclass(frozen=True)
class Finding:
    rendition: str
    reason: str
    href: str

class LinkReader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() in {"a", "area"}:
            self.links.extend(value for key, value in attrs if key and key.lower() == "href" and value)

def extract_links(text, kind):
    if kind == "html":
        reader = LinkReader()
        reader.feed(text)
        reader.close()
        return reader.links
    if kind == "md":
        return re.findall(r"\[[^\]]+\]\((https?://[^\s)]+)\)", text)
    raise ValueError("Unknown rendition")

def classify_link(href, depth=0):
    """Flag direct seller routes, client-side execution schemes and redirect parameters."""
    if depth > 3:
        return "nested_redirect_exceeds_limit"
    raw = unescape(href).strip()
    if not raw:
        return None
    if re.match(r"(?i)^\s*(javascript|data|vbscript)\s*:", raw):
        return "active_non_http_scheme"
    try:
        parts = urlsplit(raw)
        host = unquote((parts.hostname or "").lower().rstrip("."))
    except ValueError:
        return "unparseable_href"
    if any(host == d or host.endswith("." + d) for d in MERCHANT_HOSTS):
        return "clickable_merchant_destination"
    for key, value in parse_qsl(parts.query, keep_blank_values=True):
        if key.lower() in REDIRECT_KEYS:
            decoded = unquote(value)
            if decoded.lower().startswith(("https://", "http://", "//")):
                nested = classify_link(decoded, depth + 1)
                if nested:
                    return "redirect_to_" + nested
    return None

def inspect_text(content, rendition, kind):
    return [Finding(rendition, reason, href) for href in extract_links(content, kind)
            if (reason := classify_link(href))]

def current_report():
    manifest = json.loads((CAMPAIGN / "manifest.json").read_text(encoding="utf-8"))
    rows = {}
    for name, (relative_path, kind) in REVIEW_INPUTS.items():
        content = (CAMPAIGN / relative_path).read_text(encoding="utf-8")
        findings = inspect_text(content, name, kind)
        rows[name] = {
            "source": relative_path, "release": "HOLD_REVIEW",
            "active_merchant_or_risky_links": len(findings),
            "findings": [asdict(f) for f in findings]
        }
    originals = {k: v for k, v in rows.items() if "optional" not in k}
    optional = {k: v for k, v in rows.items() if "optional" in k}
    return {
        "purpose": "UNSENT static link audit, not email delivery evidence",
        "mix": manifest["mix"],
        "status": manifest["status"],
        "original_commercial_routes": sum(x["active_merchant_or_risky_links"] for x in originals.values()),
        "originals": originals,
        "optional_unapproved_candidates": optional,
        "release": {str(i).zfill(2): "HOLD_UNSENT_AND_MERCHANT" if i in (3, 5) else "HOLD_UNSENT"
                    for i in range(1, 7)},
        "not_verified": [
            "Final Vestige affiliate acceptance for each product",
            "specific permission to promote each product by EMAIL",
            "current tracking link, creative license, checkout and refund",
            "published founder-approved independent buyer guides",
            "Final Vestige physical postal address and working unsubscribe in received email",
            "deduplicated consent-eligible audience and actual Jetpack email preview",
            "explicit founder authorization for final campaign send"
        ]
    }

if __name__ == "__main__":
    print(json.dumps(current_report(), indent=2, ensure_ascii=False))
