"""Adversarial tests of R92's fail-closed excerpt model; no network or email."""
import copy
import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("excerpt_contract", HERE / "excerpt_contract.py")
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)

class ExcerptContractTests(unittest.TestCase):
    def setUp(self):
        self.doc = adapter.load()
    def reject(self, mutate):
        x = copy.deepcopy(self.doc)
        mutate(x)
        self.assertTrue(adapter.validate(x))
    def test_clean_candidates_valid(self): self.assertEqual([], adapter.validate(self.doc))
    def test_six_issues(self): self.assertEqual(6,len(self.doc["issues"]))
    def test_mix(self): self.assertEqual((4,2),(sum(i["kind"]=="editorial" for i in self.doc["issues"]),sum(i["kind"]=="commercial-review-pending" for i in self.doc["issues"])))
    def test_all_hold(self): self.assertTrue(all(i["status"]=="HOLD_UNSENT" for i in self.doc["issues"]))
    def test_offline_only(self): self.assertNotIn("send(", pathlib.Path(adapter.__file__).read_text(encoding="utf-8"))
    def test_draft_gate(self): self.reject(lambda d:d.update(campaign_state="APPROVED"))
    def test_master_reference(self): self.reject(lambda d:d.update(master_sha="wrong"))
    def test_excerpt_mode_guard(self): self.reject(lambda d:d["settings_snapshot"].update(email_content_format="full"))
    def test_auto_email_guard(self): self.reject(lambda d:d["settings_snapshot"].update(email_new_posts_by_default=True))
    def test_unknown_recipients(self): self.reject(lambda d:d["settings_snapshot"].update(eligible_email_recipients=2))
    def test_conflicting_count_guard(self): self.reject(lambda d:d["settings_snapshot"].update(subscriber_unconfirmed=0))
    def test_address_gate(self): self.reject(lambda d:d["settings_snapshot"].update(qualified_publisher_postal_address_verified=True))
    def test_preview_gate(self): self.reject(lambda d:d["settings_snapshot"].update(actual_jetpack_email_preview_verified=True))
    def test_unsubscribe_gate(self): self.reject(lambda d:d["settings_snapshot"].update(received_email_unsubscribe_verified=True))
    def test_founder_gate(self): self.reject(lambda d:d["settings_snapshot"].update(founder_final_send_approval=True))
    def test_preheader_unverified(self): self.reject(lambda d:d["native_wordpress_expectation"].update(custom_preheader_control_verified=True))
    def test_prevent_active_link(self): self.reject(lambda d:d["issues"][2].update(active_affiliate_url="https://example.org/sale"))
    def test_prevent_approval(self): self.reject(lambda d:d["issues"][2].update(merchant_approval=True))
    def test_prevent_guide_url(self): self.reject(lambda d:d["issues"][2].update(approved_guide_url="https://finalvestige.com/mind/guide"))
    def test_prevent_status(self): self.reject(lambda d:d["issues"][0].update(status="READY"))
    def test_prevent_commercial_shuffle(self): self.reject(lambda d:d["issues"][1].update(kind="commercial-review-pending"))
    def test_prevent_missing_disclosure(self): self.reject(lambda d:d["issues"][2].update(excerpt_text="Try short sessions each morning and compare how you feel throughout the next week, without making clinical claims about effectiveness."))
    def test_prevent_hidden_disclosure(self): self.reject(lambda d:d["issues"][2].update(excerpt_text=d["issues"][2]["excerpt_text"].replace("Commercial note:", ""))
    def test_prevent_vendor_guarantee(self): self.reject(lambda d:d["issues"][2].update(excerpt_text=d["issues"][2]["excerpt_text"]+" Guaranteed benefits."))
    def test_prevent_url_in_excerpt(self): self.reject(lambda d:d["issues"][0].update(excerpt_text=d["issues"][0]["excerpt_text"]+" https://inspire3.com"))
    def test_prevent_tracking(self): self.reject(lambda d:d["issues"][0].update(excerpt_text=d["issues"][0]["excerpt_text"]+" utm_source=mail"))
    def test_prevent_bad_subject(self): self.reject(lambda d:d["issues"][3].update(subject_candidate="Fourteen seconds. A much longer explanation."))
    def test_editorial_link_internal(self): self.reject(lambda d:d["issues"][0].update(editorial_source_url="https://evil.example/"))
    def test_prevent_candidate_overlong(self): self.reject(lambda d:d["issues"][0].update(excerpt_text="word "*95))
    def test_escape_untrusted_markup(self):
        d=copy.deepcopy(self.doc)
        d["issues"][0]["subject_candidate"]="A title with & a character"
        output=adapter.render_html(d)
        self.assertIn("&amp;",output)
    def test_renderer_labels_simulation(self):
        self.assertIn("Not a genuine received email",adapter.render_html(self.doc))
        self.assertNotIn("mailto:",adapter.render_html(self.doc))
    def test_source_has_no_email(self):
        text=(HERE/"candidate_excerpts.json").read_text(encoding="utf-8")
        self.assertNotIn("@gmail.com",text)
        self.assertNotIn("@yahoo.com",text)

if __name__=="__main__": unittest.main()
