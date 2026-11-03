"""R100: offline, fail-closed claim/disclosure gate for one UNSENT alternative.
This is a static editorial safety check, not approval or a WordPress sender.
"""
from __future__ import annotations
import copy
import html.parser
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
CAMPAIGN = ROOT.parent
MERCHANT = ("hypnosislive.com", "zen12.com", "inspire3.com", "affiliates.inspire3.com")
FLAGS = (
    "named_final_vestige_affiliate_acceptance",
    "exact_sku_email_promotion_permission",
    "approved_partner_deep_link",
    "approved_merchant_creatives",
    "aggregate_only_purchaser_reporting_contract",
    "exact_guide_live_and_approved",
    "current_checkout_terms_verified",
    "publisher_postal_address_verified",
    "received_jetpack_email_footer_verified",
    "unsubscribe_functional_verified",
    "eligible_audience_reconciled",
    "founder_final_campaign_send_approval",
)
POSTAL = "[[VALID_POSTAL_ADDRESS_REQUIRED]]"
UNSUB = "[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"
CTA = "[[APPROVED_LIVE_TOTAL_FOCUS_GUIDE_URL_REQUIRED]]"

class EmailHTML(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.media = []
        self.scripts = []
        self.forms = []
        self.tables = []
        self.headings = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a": self.links.append(a.get("href"))
        if tag in ("img", "iframe", "video", "audio", "source", "pixel"): self.media.append(tag)
        if tag == "script": self.scripts.append(tag)
        if tag == "form": self.forms.append(tag)
        if tag == "table": self.tables.append(a)
        if tag in ("h1","h2"): self.headings.append(tag)

def load():
    return (
        json.loads((ROOT / "exact_product_claim_and_permissions.json").read_text(encoding="utf-8")),
        (ROOT / "05-total-focus-exact-product-candidate.md").read_text(encoding="utf-8"),
        (ROOT / "05-total-focus-exact-product-candidate.txt").read_text(encoding="utf-8"),
        (ROOT / "05-total-focus-static-review.html").read_text(encoding="utf-8"),
        json.loads((CAMPAIGN / "manifest.json").read_text(encoding="utf-8")),
    )

def validate(ledger, md, plain, html, manifest):
    errors = []
    def check(test, message):
        if not test: errors.append(message)
    check(ledger.get("issue") == 5, "wrong reserved edition")
    check(ledger.get("campaign_state") == "HOLD_UNSENT", "send state must HOLD")
    check(ledger.get("merchant_state") == "HOLD_MERCHANT", "merchant state must HOLD")
    check(ledger.get("exact_product") == "Hypnosis Live / Total Focus", "unexpected SKU")
    check(ledger.get("mix") == {"editorial":[1,2,4,6],"commercial_reserved":[3,5]}, "4:2 mix changed")
    check(manifest.get("status") == "DRAFT_UNSENT_NO_SCHEDULING", "original master moved")
    check([e["kind"] for e in manifest["issues"]] == [
        "editorial","editorial","commercial-review-pending",
        "editorial","commercial-review-pending","editorial"
    ], "original mix changed")
    check(all(e["publish_state"]=="hold" and e["merchant_affiliate_url"] is None for e in manifest["issues"]), "original item activated")
    check(ledger.get("sku_or_partner_tracking_id_verified") is False, "unverified SKU id claimed")
    check(ledger.get("approved_affiliate_merchant_url") is None, "merchant link inserted")
    check(ledger.get("approved_live_buyer_guide_url") is None, "unapproved guide inserted")
    check(ledger.get("verified_eligible_recipients") is None, "fake audience count")
    check(ledger.get("sent_count_this_run") == 0, "false send count")
    check(ledger.get("new_post_default_send") is False, "auto sending claimed")
    check(ledger.get("native_preheader_field_verified") is False, "native preheader not verified")
    flags = ledger.get("blocked_permissions") or {}
    check(set(flags)==set(FLAGS), "approval ledger incomplete")
    for f in FLAGS: check(flags.get(f) is False, "unsupported permission: "+f)
    sources = ledger.get("sources") or []
    check({s.get("key") for s in sources} >= {"total_focus","faq","terms","privacy","affiliate_portal","ftc"}, "essential primary sources missing")
    for s in sources: check(str(s.get("url","")).startswith("https://"), "insecure source")
    check("44 minutes" not in md and "40-minute" not in md, "generic duration substituted for exact SKU")
    for text in [md,plain,html]:
        check("HOLD_UNSENT" in text and "HOLD_MERCHANT" in text, "unsent labels absent")
        check("Total Focus" in text and "33-minute" in text and "47 MB" in text, "specific product description missing")
        check("commission" in text.lower(), "commission disclosure missing")
        check(POSTAL in text and UNSUB in text, "unverified legal footer fabricated")
        check(CTA in text, "missing inactive offer guide CTA")
        check(not re.search(r"(?i)(cures anxiety|results guaranteed|scientifically proven to|instant focus guarantee|\b100% razor-sharp\b)",text), "unverified efficacy guarantee")
        check(not re.search(r"\$\s*\d+",text), "unstable price embedded")
        check(not re.search(r"(?i)utm_|subid=|clickid=|affiliate_id=",text), "tracking parameter inserted")
    check("HOLD_UNSENT" in md.splitlines()[1], "status buried")
    check("14-day" in md and "five" in md and "twelve-month" in md, "refund caveats omitted")
    check("aggregate-only" in md and "privacy" in md.lower(), "privacy limitation omitted")
    check(md.find("Commercial disclosure") > md.find("buyer\'s guide"), "commercial disclosure not near CTA")
    check(md.find("Commercial disclosure") - md.find("buyer\'s guide") < 900, "commercial disclosure too far from CTA")
    excerpt=ledger.get("email_excerpts",{}).get("commercial_first_350_char_candidate","")
    check(excerpt.startswith("Commercial note: "), "excerpt disclosure absent at start")
    check(len(excerpt) > 150 and len(excerpt) < 500, "excerpt unrealistic")
    check(not any(q in excerpt for q in ("http://","https://","[[","]]")), "excerpt contains dead placeholder/link")
    parse=EmailHTML();parse.feed(html)
    check(not parse.links, "active link found in static email; possible direct offsite/merchant CTA")
    check(not parse.media and not parse.scripts and not parse.forms, "unsafe remote media/scripts/forms")
    check(len(parse.tables) >= 2 and all(t.get("role")=="presentation" for t in parse.tables), "email tables not presentational")
    check("h1" in parse.headings and "h2" in parse.headings, "heading hierarchy absent")
    check('lang="en"' in html and 'name="viewport"' in html, "a11y/mobile metadata absent")
    check("NOT A JETPACK RECEIVED EMAIL" in html and "not a verified native Jetpack" in html, "static preview misrepresented")
    check(html.index("Commercial disclosure") - html.index("PROPOSED SINGLE PRIMARY CTA") < 1400, "email disclosure not adjacent")
    check("href=" not in html.lower() and "<button" not in html.lower(), "hidden live action in static email")
    # NEVER infer release approval from this validator: all valid packages remain blocked.
    return errors

def main():
    errors=validate(*load())
    if errors:
        for e in errors: print("FAIL_CLOSED:", e)
        return 1
    print("PASS static copy/claim/HTML check; 4:2; all six HOLD_UNSENT; 03/05 HOLD_MERCHANT")
    print("NOT VERIFIED: live guide, real Jetpack MIME, legal postal/unsub, active recipients, merchant approval, send authorization")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
