import unittest
from email.message import EmailMessage
from received_email_gate import audit

ADDR = "42 Example Lane, Sample City, CA 00000"  # SYNTHETIC: never use as real FV address
CTA = "https://finalvestige.com/mind/"
UNSUB = "https://wordpress.com/email-subscriptions/unsubscribe/?fixture=1"

def make_email(*, html=True, plain=True, cta=True, unsubscribe=True, address=True,
               disclosure=True, sender="donotreply@wordpress.com", unsafe=False, header=True, far_disclosure=False):
    m = EmailMessage()
    m["From"] = f"Final Vestige <{sender}>"
    m["To"] = "synthetic@example.invalid"
    m["Subject"] = "A genuine question about attention"
    if header:
        m["List-Unsubscribe"] = f"<{UNSUB}>"
    c = CTA if cta else "https://finalvestige.com/focus/"
    footer = f"Unsubscribe: {UNSUB}" if unsubscribe else "Subscription options"
    p = f"Try a free experiment. {c}\nMay earn a commission. {ADDR if address else 'No address here'}\n{footer}"
    h = (f"<html><body><p>Try a free experiment.</p><p><a href='{c}'>Read the independent review</a></p>"
         + ("<p>May earn a commission.</p>" if disclosure else "<p>No commercial relationship discussed.</p>")
         + f"<p>{ADDR if address else 'No address here'}</p>"
         + (f"<p><a href='{UNSUB}'>Unsubscribe</a></p>" if unsubscribe else "<p>Subscription options</p>")
         + ("<script>alert('fixture')</script>" if unsafe else "") + "</body></html>")
    if not disclosure:
        p = p.replace("May earn a commission.", "No commission disclosure.")
    if far_disclosure:
        p = p.replace("May earn a commission.", ("filler " * 400) + "May earn a commission.")
        h = h.replace("<p>May earn a commission.</p>", "<p>" + ("filler " * 400) + "May earn a commission.</p>")
    if plain:
        m.set_content(p)
    else:
        m.set_content(" ")
    if html:
        m.add_alternative(h, subtype="html")
    return m.as_bytes()

class EmailAuditTests(unittest.TestCase):
    def test_commercial_structural_pass_is_still_hard_hold(self):
        r = audit(make_email(), edition="03", expected_path="/mind/", publisher_address=ADDR)
        self.assertTrue(r["structural_pass"])
        self.assertFalse(r["campaign_release_ready"])
        self.assertFalse(r["native_jetpack_received_email_provenance_verified"])
        self.assertFalse(r["unsubscribe_functionality_verified"])
        self.assertFalse(r["independent_paid_sale_verified"])
        self.assertIn("HOLD_MERCHANT", r["release_status"])
    def test_all_six_edition_codes(self):
        for ed in ["01", "02", "03", "04", "05", "06"]:
            self.assertIn("release_status", audit(make_email(), edition=ed, expected_path="/mind/", publisher_address=ADDR))
    def test_wrong_cta_fails(self):
        self.assertFalse(audit(make_email(cta=False), edition="01", expected_path="/mind/", publisher_address=ADDR)["structural_checks"]["intended_first_party_cta_visible"])
    def test_missing_unsubscribe_fails(self):
        self.assertFalse(audit(make_email(unsubscribe=False), edition="01", expected_path="/mind/", publisher_address=ADDR)["structural_checks"]["visible_unsubscribe_url_present"])
    def test_list_header_missing_fails(self):
        self.assertFalse(audit(make_email(header=False), edition="01", expected_path="/mind/", publisher_address=ADDR)["structural_checks"]["list_unsubscribe_header_present"])
    def test_unknown_postal_fails(self):
        self.assertFalse(audit(make_email(), edition="01", expected_path="/mind/")["structural_checks"]["verified_publisher_postal_address_present"])
    def test_incorrect_postal_fails(self):
        self.assertFalse(audit(make_email(address=False), edition="01", expected_path="/mind/", publisher_address=ADDR)["structural_checks"]["verified_publisher_postal_address_present"])
    def test_automattic_not_fv(self):
        self.assertFalse(audit(make_email(), edition="01", expected_path="/mind/", publisher_address="Automattic, 42 Example Lane")["structural_checks"]["verified_publisher_postal_address_present"])
    def test_missing_commercial_disclosure_fails(self):
        self.assertFalse(audit(make_email(disclosure=False), edition="03", expected_path="/mind/", publisher_address=ADDR)["structural_checks"]["commercial_disclosure_in_present_mime_parts"])
    def test_near_disclosure_positive(self):
        r = audit(make_email(), edition="03", expected_path="/mind/", publisher_address=ADDR)
        self.assertTrue(r["structural_checks"]["commercial_disclosure_near_first_party_cta"])
    def test_disclosure_only_far_away_fails(self):
        r = audit(make_email(far_disclosure=True), edition="03", expected_path="/mind/", publisher_address=ADDR)
        self.assertTrue(r["structural_checks"]["commercial_disclosure_in_present_mime_parts"])
        self.assertFalse(r["structural_checks"]["commercial_disclosure_near_first_party_cta"])
        self.assertFalse(r["structural_pass"])
    def test_editorial_does_not_require_affiliate_disclosure(self):
        self.assertTrue(audit(make_email(disclosure=False), edition="01", expected_path="/mind/", publisher_address=ADDR)["structural_checks"]["commercial_disclosure_in_present_mime_parts"])
    def test_email_safe_html(self):
        self.assertFalse(audit(make_email(unsafe=True), edition="01", expected_path="/mind/", publisher_address=ADDR)["structural_checks"]["email_html_has_no_unsafe_elements_or_unlabeled_images"])
    def test_wrong_sender(self):
        self.assertFalse(audit(make_email(sender="bad@example.invalid"), edition="01", expected_path="/mind/", publisher_address=ADDR)["structural_checks"]["sender_matches_configured_wordpress_sender"])
    def test_reject_unknown_edition(self):
        with self.assertRaises(ValueError): audit(make_email(), edition="99", expected_path="/mind/")
    def test_reject_external_intended_path(self):
        with self.assertRaises(ValueError): audit(make_email(), edition="01", expected_path="https://elsewhere.test")
    def test_reject_query_in_intended_path(self):
        with self.assertRaises(ValueError): audit(make_email(), edition="01", expected_path="/mind/?user=test")
    def test_reject_oversize(self):
        with self.assertRaises(ValueError): audit(b"x"*2000001, edition="01", expected_path="/mind/")
    def test_never_records_personal_data(self):
        r = audit(make_email(), edition="03", expected_path="/mind/", publisher_address=ADDR)
        self.assertNotIn("synthetic@example.invalid",str(r))
        self.assertNotIn(ADDR,str(r))
        self.assertNotIn("fixture=1",str(r))
    def test_plain_only_is_not_full_multipart(self):
        r = audit(make_email(html=False),edition="01",expected_path="/mind/",publisher_address=ADDR)
        self.assertFalse(r["structural_checks"]["html_body_present"])

if __name__ == "__main__": unittest.main()
