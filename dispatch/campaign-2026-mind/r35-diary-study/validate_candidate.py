"""R35 independent, read-only source-precision/format guard. NEVER sends."""
from __future__ import annotations
import json
import pathlib
import re
from html.parser import HTMLParser
from urllib.parse import urlsplit

HERE = pathlib.Path(__file__).resolve().parent
CAMPAIGN = HERE.parent
CTA = "https://finalvestige.com/focus/"
SOURCE = "https://pmc.ncbi.nlm.nih.gov/articles/PMC111114/"
ADDRESS = "[[VALID_POSTAL_ADDRESS_REQUIRED]]"
UNSUB = "[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"
SUBJECT = "What did seven days of attention reveal?"
PREHEADER = "A diary timestamp can look precise. Here is what the underlying evidence really measured."

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            self.links.append(dict(attrs).get("href", ""))

def packet():
    return {
        "markdown": (HERE / "ISSUE_06_REVIEW_CANDIDATE.md").read_text(encoding="utf-8"),
        "html": (HERE / "ISSUE_06_REVIEW_CANDIDATE.html").read_text(encoding="utf-8"),
        "plaintext": (HERE / "ISSUE_06_REVIEW_CANDIDATE.txt").read_text(encoding="utf-8"),
        "ledger": json.loads((HERE / "CLAIM_REGISTER.json").read_text(encoding="utf-8")),
        "manifest": json.loads((CAMPAIGN / "manifest.json").read_text(encoding="utf-8")),
    }

def validate_packet(p=None):
    p = packet() if p is None else p
    problems = []
    def expect(ok, label):
        if not ok:
            problems.append(label)
    m, h, t = p["markdown"], p["html"], p["plaintext"]
    ledger, manifest = p["ledger"], p["manifest"]
    texts = (m, h, t)
    expect(ledger.get("release_state") == "HOLD_UNSENT", "ledger release state")
    expect(ledger.get("review_candidate", {}).get("state") == "HOLD_EDITORIAL_REVIEW", "candidate hold state")
    expect(ledger.get("review_candidate", {}).get("replaces_canonical") is False, "candidate must not replace manuscript")
    expect(ledger.get("review_candidate", {}).get("commercial_links") == 0, "no commercial links")
    expect(ledger.get("verified_wp_read_only", {}).get("unique_eligible_recipients") is None, "audience unknown")
    expect(ledger.get("verified_wp_read_only", {}).get("welcome_received") is False, "welcome not attested")
    issues = manifest.get("issues", [])
    expect(len(issues) == 6, "must keep six issues")
    expect(sum(i.get("kind") == "editorial" for i in issues) == 4, "must keep four editorials")
    expect(sum(i.get("kind") == "commercial-review-pending" for i in issues) == 2, "must keep two commercial holds")
    expect(all(i.get("publish_state") == "hold" and i.get("merchant_affiliate_url") is None for i in issues), "no manifest activation")
    expect(manifest.get("status") == "DRAFT_UNSENT_NO_SCHEDULING", "no schedule")
    expect(len(ledger.get("issue_claims", [])) == 6, "source ledger has six claims")
    for idx, source in enumerate(texts):
        key = ("markdown", "html", "plaintext")[idx]
        expect(SUBJECT in source, key + " subject")
        expect(PREHEADER in source, key + " preheader")
        for fact in ("90%", "11%", "30-minute", "40 participants", "binder"):
            expect(fact in source, key + " methodological fact " + fact)
        expect("not" in source.lower() and "written" in source.lower(), key + " measurement limitation")
        expect(CTA in source, key + " editorial CTA")
        expect(SOURCE in source, key + " primary source")
        expect(ADDRESS in source and UNSUB in source, key + " legal placeholders")
        expect("DO NOT PUBLISH" in source or "DO NOT SEND" in source, key + " visible draft warning")
        expect(not re.search(r"(?i)https?://(?:www\.)?(?:zen12\.com|hypnosislive\.com|affiliates\.inspire3\.com)", source), key + " no commerce destination")
        expect(not re.search(r"(?i)\b(?:price|discount)\s*[:=]\s*[$£€]\d", source), key + " no price")
        expect("2003" not in source, key + " correct 2002 study")
        expect(not re.search(r"(?i)\b(?:guarantee(?:d)?|clinically proven to improve attention)\b", source), key + " no efficacy guarantee")
    expect('lang="en"' in h and 'role="presentation"' in h, "email accessible layout")
    expect("<script" not in h.lower() and "onload=" not in h.lower(), "email no active script")
    expect('display:none!important' in h, "hidden preview preheader")
    expect("<h1" in h and "<h2" in h, "heading hierarchy")
    links = Links()
    links.feed(h)
    expect(links.links == [CTA, SOURCE], "one CTA plus one primary research link")
    expect(t.count(CTA) == 1, "one plaintext CTA")
    expect(m.count("](" + CTA + ")") == 1, "one markdown CTA")
    expect(ledger.get("review_candidate", {}).get("editorial_cta") == CTA, "ledger CTA parity")
    for url in links.links:
        u = urlsplit(url)
        expect(u.scheme == "https" and u.hostname in {"finalvestige.com", "pmc.ncbi.nlm.nih.gov"}, "link allowlist")
    expect("Unsubscribe:" in t and "Sender:" in t, "plaintext footer")
    return {"static_integrity": not problems, "errors": problems,
            "release_status": "HOLD_UNSENT",
            "email_sent_or_authorized": False,
            "real_jetpack_render_verified": False}

if __name__ == "__main__":
    result = validate_packet()
    print(json.dumps(result, indent=2))
    # Intended fail-closed exit, EVEN when static integrity passes. Never a send-ready signal.
    raise SystemExit(2 if result["static_integrity"] else 1)
