"""R51: exact-source, review-only alternative Total Focus copy safety tests."""
from pathlib import Path
import hashlib, html, json, re, unittest
from html.parser import HTMLParser
from urllib.parse import urlsplit
ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "r51-total-focus-claim-contract"
REG = json.loads((PACK / "claim_register.json").read_text(encoding="utf8"))
SOURCE = (ROOT / "issues/05-before-you-press-play.md").read_text(encoding="utf8")
MAN = json.loads((ROOT / "manifest.json").read_text(encoding="utf8"))
MD = (PACK / "issue05-candidate-C.md").read_text(encoding="utf8")
TXT = (PACK / "issue05-candidate-C.txt").read_text(encoding="utf8")
WEB = (PACK / "issue05-candidate-C.html").read_text(encoding="utf8")
CTA = "[[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]]"
POSTAL = "[[VALID_POSTAL_ADDRESS_REQUIRED]]"
UNSUB = "[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]"
class LinkReader(HTMLParser):
    def __init__(self): super().__init__(); self.links=[]; self.scripts=[]; self.forms=0
    def handle_starttag(self, tag, attrs):
        if tag=="a": self.links.extend(v for k,v in attrs if k=="href" and v)
        if tag in ("script","iframe","img","video"): self.scripts.append(tag)
        if tag=="form": self.forms+=1
def blob(s):
    b=s.encode("utf8"); return hashlib.sha1(b"blob "+str(len(b)).encode()+bytes((0,))+b).hexdigest()
def is_merchant(link):
    h=(urlsplit(link).hostname or "").lower()
    return any(h==d or h.endswith("."+d) for d in ("inspire3.com","zen12.com","hypnosislive.com"))
class R51TotalFocusClaimContract(unittest.TestCase):
    def test_01_canonical_05_bytes_unchanged(self):
        self.assertEqual(blob(SOURCE),REG["original_campaign"]["canonical_issue05_blob"])
    def test_02_manifest_bytes_unchanged(self):
        raw=(ROOT/"manifest.json").read_text(encoding="utf8")
        self.assertEqual(blob(raw),REG["original_campaign"]["manifest_blob"])
    def test_03_original_six_holds_and_4_to_2(self):
        self.assertEqual(MAN["mix"],{"editorial":4,"commercial_review_pending":2})
        self.assertEqual(len(MAN["issues"]),6)
        self.assertTrue(all(x["publish_state"]=="hold" and x["merchant_affiliate_url"] is None for x in MAN["issues"]))
    def test_04_candidate_not_selected(self):
        self.assertFalse(REG["original_campaign"]["candidate_selected"])
        self.assertTrue(REG["original_campaign"]["all_issues_hold_unsent"])
        self.assertTrue(REG["original_campaign"]["commercial_03_05_hold_merchant"])
    def test_05_single_disabled_guide_cta_in_all_formats(self):
        for name,s in (("md",MD),("txt",TXT),("html",WEB)):
            with self.subTest(name=name): self.assertEqual(s.count(CTA),1)
    def test_06_both_legal_hard_stop_tokens_in_all_formats(self):
        for s in (MD,TXT,WEB):
            for marker in (POSTAL,UNSUB): self.assertIn(marker,s)
    def test_07_early_near_offer_disclosure(self):
        for s in (MD,TXT,WEB):
            self.assertLess(s.index("Commercial disclosure:"),s.index(CTA))
            self.assertLess(s.index(CTA)-s.index("Commercial disclosure:"),600)
    def test_08_offer_still_not_live(self):
        for s in (MD,TXT,WEB):
            self.assertIn("NOT LIVE",s)
            self.assertIn("not published",s)
    def test_09_product_description_precise_in_all_formats(self):
        for s in (MD,TXT,WEB):
            self.assertIn("33-minute",s); self.assertIn("47 MB",s)
            self.assertIn("J. A. Amos",s)
    def test_10_no_guaranteed_benefit_statement(self):
        for forbidden in ("will reprogram","proven to improve your concentration","guaranteed concentration","100% razor-sharp"):
            self.assertNotIn(forbidden,MD.lower())
    def test_11_no_active_seller_anchors(self):
        p=LinkReader();p.feed(WEB);p.close()
        self.assertEqual(p.scripts,[])
        self.assertEqual(p.forms,0)
        self.assertGreaterEqual(len(p.links),1)
        self.assertFalse(any(is_merchant(link) for link in p.links))
    def test_12_no_merchant_domains_in_reader_formats(self):
        for s in (MD,TXT,WEB):
            self.assertNotRegex(s.lower(),r"https?://(?:[a-z0-9-]+\\.)*(?:hypnosislive|zen12|inspire3)\\.com")
    def test_13_no_trackers_or_hidden_autoloads(self):
        for s in (MD,TXT,WEB):
            for bad in ("utm_source=","affiliate_id=","fbclid=","gclid=","hop.clickbank.net","<script","<form","<iframe","<img"):
                self.assertNotIn(bad,s.lower())
    def test_14_case_specific_research_limit_not_an_endorsement(self):
        for s in (MD,TXT,WEB):
            self.assertIn("https://www.nccih.nih.gov/health/hypnosis",s)
            self.assertIn("does not test or endorse Total Focus",s)
    def test_15_subject_and_preheader_not_surrogates_for_native_email(self):
        self.assertTrue(30<=len(REG["candidate"]["subject"])<=70)
        self.assertTrue(35<=len(REG["candidate"]["preheader"])<=100)
        self.assertFalse(REG["candidate"]["native_preheader_field_verified"])
        self.assertIn(REG["candidate"]["subject"],MD)
        self.assertIn(REG["candidate"]["preheader"],MD)
    def test_16_zero_external_release_evidence(self):
        self.assertFalse(REG["external_release_evidence_present"])
        for k,v in REG["candidate"].items():
            if k.endswith("_verified") or k in ("founder_final_campaign_approval","live_warmup_guide"):
                self.assertIs(v,False,k)
    def test_17_no_active_affiliate_link(self):
        self.assertIsNone(REG["candidate"]["merchant_affiliate_link"])
        self.assertIn(CTA,MAN["issues"][4]["editorial_cta"])
    def test_18_custom_excerpt_not_installed(self):
        self.assertFalse(REG["candidate"]["proposed_excerpt_installed"])
        self.assertNotIn("[[",REG["candidate"]["proposed_custom_excerpt"])
    def test_19_excerpt_relationship_early(self):
        e=REG["candidate"]["proposed_custom_excerpt"]
        self.assertIn("commercial product",e.lower())
        self.assertIn("commission",e.lower())
        self.assertLess(e.lower().index("commission"),350)
    def test_20_excerpt_does_not_offer_unpublished_destination(self):
        e=REG["candidate"]["proposed_custom_excerpt"].lower()
        self.assertIn("not live",e)
        self.assertIn("no purchase",e)
        self.assertNotIn("https://",e)
    def test_21_exact_official_sources_and_limitations(self):
        byid={x["id"]:x for x in REG["source_register"]}
        self.assertEqual(len(byid),6)
        self.assertEqual(byid["S1"]["url"],"https://hypnosislive.com/mental-skills/total-focus")
        self.assertEqual(byid["S2"]["url"],"https://www.nccih.nih.gov/health/hypnosis")
        self.assertIn("Final Vestige Total Focus email rights",byid["S3"]["not_supported"])
    def test_22_wordpress_snapshot_keeps_unknown_audience(self):
        wp=REG["wordpress"]
        self.assertEqual((wp["subscribers_total"],wp["subscribers_confirmed"],wp["subscribers_unconfirmed"]),(2,2,2))
        self.assertEqual(wp["unique_eligible"],"UNKNOWN")
        self.assertFalse(wp["welcome_received_verified"])
        self.assertFalse(wp["email_new_posts_by_default"])
        self.assertEqual(wp["email_content_format"],"excerpt")
    def test_23_all_formats_flag_internal_not_a_real_email(self):
        for s in (MD,TXT,WEB):
            self.assertTrue("REVIEW" in s.upper() and "UNSENT" in s.upper())
    def test_24_mobile_email_container_has_valid_semantics(self):
        self.assertIn('lang="en"',WEB)
        self.assertIn('role="presentation"',WEB)
        self.assertIn('name="viewport"',WEB)
        self.assertIn("max-width:640px",WEB)
        self.assertNotIn("<marquee",WEB.lower())
    def test_25_named_product_not_a_general_brand_endorsement(self):
        self.assertIn("one",MD.lower())
        self.assertIn("Total Focus",MD)
        self.assertNotIn("Hypnosis Live endorses",MD)
    def test_26_subject_contains_no_discount_framing(self):
        self.assertFalse(any(x in REG["candidate"]["subject"].lower() for x in ("free","guaranteed","sale","deal","%")))
    def test_27_readme_owns_high_impact_gaps(self):
        notes=(PACK/"README.md").read_text(encoding="utf8")
        for phrase in ("postal address","unsubscribe","merchant","approval","WordPress","excerpt","received","HOLD"):
            self.assertIn(phrase.lower(),notes.lower())
    def test_29_historical_source_is_rendered_not_merely_registered(self):
        source="https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/"
        for label,s in (("markdown",MD),("plaintext",TXT),("email_html",WEB)):
            with self.subTest(label=label): self.assertEqual(s.count(source),1)
        self.assertIn("Puységur's 1784 accounts",MD)
        self.assertEqual(REG["source_register"][5]["id"],"S6")
    def test_28_original_editorial_not_promoted_to_offer(self):
        self.assertEqual([x["kind"] for x in MAN["issues"]],["editorial","editorial","commercial-review-pending","editorial","commercial-review-pending","editorial"])
if __name__=="__main__":unittest.main()
