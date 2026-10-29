"""Pure-stdlib offline tests. Run: python -m unittest discover -s qa/focus -v"""
import importlib.util
import pathlib
import unittest

spec = importlib.util.spec_from_file_location("focus_audit", pathlib.Path(__file__).with_name("fieldbook_funnel_preflight.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

PDF = "https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf"


def fixture():
    return {
        "pages": {
            "focus": {"status": "publish", "content": '<!-- wp:jetpack/subscriptions /--><a href="' + PDF + '">Download</a>'},
            "home": {"status": "publish", "content": '<a href="/focus/">Get free Focus Fieldbook</a>'},
            "dispatch": {"status": "publish", "content": '<!-- wp:jetpack/subscriptions /-->'},
        },
        "navigation": {"content": '<!-- wp:navigation-link {"label":"Free Focus Fieldbook","url":"https://finalvestige.com/focus/"} /-->'},
        "retired_pages": {"/72-hours-without-the-tap/": "draft", "/collection/water-resilience-field-manual/": "draft"},
        "media": {"mime_type": "application/pdf", "source_url": PDF},
        "newsletter": {"subscriptions": True, "welcome_message": "Welcome. Get the complete edition: " + PDF},
        "delivery_evidence": {"public_form_submit": True, "confirmation_received": True, "confirmation_clicked": True, "welcome_received": True, "public_pdf_download": True, "mobile_rendered": True},
    }


def codes(s):
    return [f["code"] for f in mod.inspect(s)]


class FocusFunnelTests(unittest.TestCase):
    def test_healthy_snapshot(self):
        self.assertEqual(codes(fixture()), [])

    def test_retired_nav_link_to_draft_page(self):
        s = fixture()
        s["navigation"]["content"] += '<!-- wp:navigation-link {"url":"https://finalvestige.com/collection/water-resilience-field-manual/"} /-->'
        self.assertIn("RETIRED_NAV_LINK", codes(s))

    def test_retired_page_not_draft_not_flagged_as_broken(self):
        s = fixture()
        s["retired_pages"]["/collection/water-resilience-field-manual/"] = "publish"
        s["navigation"]["content"] += '<!-- wp:navigation-link {"url":"https://finalvestige.com/collection/water-resilience-field-manual/"} /-->'
        self.assertNotIn("RETIRED_NAV_LINK", codes(s))

    def test_missing_homepage_cta(self):
        s = fixture()
        s["pages"]["home"]["content"] = "Nothing linked"
        self.assertIn("HOME_CTA_MISSING", codes(s))

    def test_missing_navigation_cta(self):
        s = fixture()
        s["navigation"]["content"] = "nothing"
        self.assertIn("NAV_CTA_MISSING", codes(s))

    def test_disabled_subscriptions(self):
        s = fixture()
        s["newsletter"]["subscriptions"] = False
        self.assertIn("SUBSCRIPTIONS_DISABLED", codes(s))

    def test_wrong_pdf_link_in_email(self):
        s = fixture()
        s["newsletter"]["welcome_message"] = "Welcome, no attachment."
        self.assertIn("WELCOME_PDF_MISMATCH", codes(s))

    def test_wrong_pdf_link_on_landing(self):
        s = fixture()
        s["pages"]["focus"]["content"] = '<!-- wp:jetpack/subscriptions /-->'
        self.assertIn("FOCUS_PDF_MISMATCH", codes(s))

    def test_duplicate_focus_signup(self):
        s = fixture()
        s["pages"]["focus"]["content"] += '<!-- wp:jetpack/subscriptions /-->'
        self.assertIn("FOCUS_DUPLICATE_FORM", codes(s))

    def test_absent_proof_never_inferred_from_configuration(self):
        s = fixture()
        s["delivery_evidence"].pop("welcome_received")
        self.assertIn("DELIVERY_NOT_VERIFIED", codes(s))

    def test_unverified_query_param_source_behavior_is_nonblocking(self):
        s = fixture()
        s["pages"]["focus"]["content"] += "if(q&&bad.indexOf(q)<0){show();}"
        f = mod.inspect(s)
        self.assertEqual([i["level"] for i in f if i["code"] == "QUERY_SUCCESS_HEURISTIC"], ["P2"])

    def test_legacy_water_in_welcome_fails(self):
        s = fixture()
        s["newsletter"]["welcome_message"] += " Also 72 Hours Without the Tap"
        self.assertIn("LEGACY_WELCOME", codes(s))

    def test_draft_focus_fails(self):
        s = fixture()
        s["pages"]["focus"]["status"] = "draft"
        self.assertIn("FOCUS_NOT_PUBLISHED", codes(s))


if __name__ == "__main__":
    unittest.main()
