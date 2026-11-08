"""Strict offline guard for the six proposed Jetpack post-metadata candidates. No network or subscriber access."""
import copy
import json
import pathlib
import unittest
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parent
DATA = json.loads((ROOT / "native-post-candidates.json").read_text(encoding="utf8"))

def audit(data):
    problems = []
    issues = data.get("issues", [])
    rules = data.get("rules", {})
    if len(issues) != 6 or [x["number"] for x in issues] != list(range(1, 7)):
        problems.append("six numbered issues required")
    if [x.get("kind") for x in issues].count("editorial") != 4 or [x.get("kind") for x in issues].count("commercial-review-pending") != 2:
        problems.append("4 editorial / 2 commercial required")
    if rules.get("campaign_status") != "HOLD_UNSENT" or rules.get("merchant_status") != "HOLD_MERCHANT":
        problems.append("release hold removed")
    if rules.get("net_revenue_per_1000_qualified_sessions") is not None:
        problems.append("fabricated revenue")
    for row in issues:
        n = row.get("number", "?")
        if row.get("post_status") != "NOT_CREATED" or row.get("send_subscription") is not False:
            problems.append(f"{n}: WordPress activation")
        if row.get("preheader_mapping") != "MANUSCRIPT_ONLY_UNVERIFIED_IN_JETPACK":
            problems.append(f"{n}: unjustified Jetpack preheader claim")
        if row.get("excerpt_mapping") != "CANDIDATE_UNTESTED_NATIVE_RENDER":
            problems.append(f"{n}: preview overstated")
        if len(row.get("manual_excerpt", "")) > 350 or len(row.get("manual_excerpt", "")) < 90:
            problems.append(f"{n}: excerpt length")
        if not row.get("candidate_post_title") or len(row["candidate_post_title"]) > 80:
            problems.append(f"{n}: post subject candidate")
        if any(row.get(key) for key in ("footer_verified","merchant_email_permission_verified","newsletter_preview_verified","confirmed_email_eligibility_verified")):
            problems.append(f"{n}: unearned verified gate")
        if row.get("approved_earning_link") is not None or row.get("settled_sales_evidence") is not None:
            problems.append(f"{n}: offer or sale fabricated")
        if row["kind"] == "editorial":
            url = row.get("intended_cta")
            if not url or urlparse(url).netloc != "finalvestige.com" or urlparse(url).scheme != "https":
                problems.append(f"{n}: invalid editorial CTA")
            if row.get("official_merchant_page") is not None:
                problems.append(f"{n}: merchant in editorial slot")
        else:
            if row.get("intended_cta") is not None:
                problems.append(f"{n}: commercial CTA activated")
            if "Final Vestige may earn a commission" not in row["manual_excerpt"]:
                problems.append(f"{n}: missing excerpt-level commercial disclosure")
            if row.get("expected_approved_product") not in row["manual_excerpt"]:
                problems.append(f"{n}: exact product missing")
    return problems

class NativePostCandidateGuards(unittest.TestCase):
    def test_exact_six_issue_contract(self):
        self.assertEqual(audit(DATA), [])
    def test_commercial_link_activation_rejected(self):
        d=copy.deepcopy(DATA); d["issues"][2]["intended_cta"]="https://zen12.com/?aff=unapproved"
        self.assertTrue(any("commercial CTA" in x for x in audit(d)))
    def test_missing_commission_disclosure_rejected(self):
        d=copy.deepcopy(DATA); d["issues"][4]["manual_excerpt"]="Check the product and read the independent guide when available."
        self.assertTrue(any("disclosure" in x for x in audit(d)))
    def test_claimed_native_preheader_rejected(self):
        d=copy.deepcopy(DATA); d["issues"][0]["preheader_mapping"]="VERIFIED"
        self.assertTrue(any("preheader" in x for x in audit(d)))
    def test_fake_paid_revenue_rejected(self):
        d=copy.deepcopy(DATA); d["rules"]["net_revenue_per_1000_qualified_sessions"]=999
        self.assertIn("fabricated revenue",audit(d))
    def test_lost_hold_rejected(self):
        d=copy.deepcopy(DATA); d["rules"]["campaign_status"]="SEND_APPROVED"
        self.assertIn("release hold removed",audit(d))
    def test_wrong_site_rejected(self):
        d=copy.deepcopy(DATA); d["issues"][0]["intended_cta"]="https://attacker.example/lead"
        self.assertTrue(any("invalid editorial CTA" in x for x in audit(d)))
    def test_html_truncation_not_proven(self):
        d=copy.deepcopy(DATA); d["issues"][3]["excerpt_mapping"]="VERIFIED_NATIVE_RENDER"
        self.assertTrue(any("preview overstated" in x for x in audit(d)))
    def test_wrong_product_rejected(self):
        d=copy.deepcopy(DATA); d["issues"][4]["expected_approved_product"]="Hypnotize Yourself"
        self.assertTrue(any("exact product missing" in x for x in audit(d)))
    def test_masquerading_actual_recipient_count_rejected(self):
        self.assertIsNone(DATA["newsletter_config_observed"]["actual_eligible_recipient_count"])
    def test_no_pii_fields(self):
        text=json.dumps(DATA).lower()
        for key in ['subscriber_email', 'email_address', 'customer_name', 'recipient_id']:
            self.assertNotIn('"' + key + '"', text)

if __name__ == "__main__":
    unittest.main()
