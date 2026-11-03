"""R101 read-only claim/permissions/static-format gate. Does not send or publish."""
import json, pathlib, re
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parent
POSTAL="[[VALID_POSTAL_ADDRESS_REQUIRED]]"
UNSUB="[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"
TOKEN="[[APPROVED_LIVE_ZEN12_GUIDE_URL_REQUIRED]]"
class Markup(HTMLParser):
    def __init__(self):
        super().__init__(); self.tags=[]; self.hrefs=[]; self.scripts=[]; self.media=[]
    def handle_starttag(self,tag,attrs):
        self.tags.append(tag); d=dict(attrs)
        if "href" in d:self.hrefs.append(d["href"])
        if tag in ("script","iframe","form"):self.scripts.append(tag)
        if tag in ("img","video","audio","source"):self.media.append(tag)
def load():
    return (json.loads((ROOT/"claim_ledger.json").read_text(encoding="utf8")),
            (ROOT/"03-zen12-candidate.md").read_text(encoding="utf8"),
            (ROOT/"03-zen12-candidate.txt").read_text(encoding="utf8"),
            (ROOT/"03-zen12-review.html").read_text(encoding="utf8"))
def validate(ledger,md,txt,html):
    errors=[]
    if ledger.get("status")!="HOLD_UNSENT_HOLD_MERCHANT" or ledger.get("send_authorized") is not False or ledger.get("sends_this_run")!=0:errors.append("release gate changed")
    if ledger.get("mix")!={"editorial":[1,2,4,6],"commercial_reserved":[3,5]}:errors.append("4:2 mix changed")
    if ledger.get("edition")!=3 or ledger.get("original_master_pr")!=175:errors.append("master identity changed")
    if ledger.get("approved_live_buyer_guide_url") is not None or ledger.get("approved_affiliate_merchant_url") is not None:errors.append("unauthorized offer url")
    if any(x is not False for x in ledger.get("affiliate_permissions",{}).values()) or len(ledger.get("affiliate_permissions",{}))!=5:errors.append("affiliate approval asserted")
    if any(x is not False for x in ledger.get("delivery_evidence",{}).values()) or len(ledger.get("delivery_evidence",{}))!=6:errors.append("delivery approval asserted")
    if ledger.get("wp_settings_snapshot",{}).get("verified_eligible_recipients") is not None:errors.append("recipient eligibility fabricated")
    if ledger.get("wp_settings_snapshot",{}).get("new_post_default_send") is not False:errors.append("post auto send altered")
    if ledger.get("native_preheader_verified") is not False:errors.append("preheader falsely verified")
    e=ledger.get("excerpt","").lower()
    if not e.startswith("commercial note:") or "commission" not in e or "no earning link" not in e:errors.append("unsafe commercial excerpt")
    if "[[" in e or "https:" in e:errors.append("excerpt includes placeholder/link")
    if not 20<=len(ledger.get("subject",""))<=72:errors.append("subject length")
    for x in (md,txt,html):
        low=x.lower()
        for term in ("zen12","twelve","48 mp3s","24 mp3s","one-year","commission","seller","not established","aggregate-only",TOKEN.lower(),POSTAL.lower(),UNSUB.lower()):
            if term not in low:errors.append("missing "+term)
        if x.count(TOKEN)!=1:errors.append("unapproved CTA count")
        if x.index(TOKEN)>x.index("commercial disclosure:") or "commission" not in x[x.index(TOKEN):x.index(TOKEN)+450].lower():errors.append("disclosure not next to CTA")
        if re.search(r"\\$\\s*\\d+",x):errors.append("fixed price in copy")
        for banned in ("clinically proven","guaranteed results","free trial","dozens of proven health gains","48 mp3s in every tier","buy now","one hour of meditation in twelve minutes is proven"):
            if banned in low:errors.append("unsubstantiated/hype phrase "+banned)
    h=Markup();h.feed(html)
    if h.hrefs or h.scripts or h.media:errors.append("active or dynamic content in static email")
    if "lang=\"en\"" not in html or "name=\"viewport\"" not in html or "role=\"presentation\"" not in html:errors.append("markup accessibility")
    if "NOT A JETPACK RECEIVED EMAIL" not in html:errors.append("static review misrepresented")
    if len(ledger.get("sources",[]))<6 or not all(s.get("url","").startswith("https://") and len(s.get("limitations",""))>30 for s in ledger.get("sources",[])):errors.append("source ledger incomplete")
    return errors
if __name__=="__main__":
    a=validate(*load());print("R101 STATIC DRAFT: "+("OK — HOLD ONLY" if not a else "; ".join(a)));raise SystemExit(bool(a))
