"""R66 contract tests; no site access, secrets, sends or list mutations."""
import importlib.util
import pathlib
import unittest

SRC = pathlib.Path(__file__).resolve().parents[1] / "r66-actual-inbox-contract" / "inbox_contract_audit.py"
spec = importlib.util.spec_from_file_location("r66_inbox_audit", SRC)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

class TestR66ExactEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest, cls.optional = audit.read_campaign()
        cls.rows = audit.audit_data(cls.manifest, cls.optional)

    def test_six(self):
        self.assertEqual(len(self.rows), 6)
        self.assertEqual([i["issue"] for i in self.rows], [1,2,3,4,5,6])

    def test_mix_still_four_and_two(self):
        self.assertEqual(sum(i["kind"]=="commercial-review-pending" for i in self.rows), 2)

    def test_commercial_still_numbers_three_and_five(self):
        self.assertEqual([i["issue"] for i in self.rows if "commercial" in i["kind"]],[3,5])

    def test_parent_manifest_is_unsent(self):
        self.assertEqual(self.manifest["status"],"DRAFT_UNSENT_NO_SCHEDULING")

    def test_optional_excerpt_is_not_approved(self):
        self.assertEqual(self.optional["status"],"ALL_HOLD_UNSENT")

    def test_first_55_is_not_header(self):
        self.assertTrue(self.rows[0]["default_55_word_surrogate"].startswith("A stranger stops you"))

    def test_limit_is_enforced(self):
        self.assertLessEqual(len(self.rows[2]["default_55_word_surrogate"].split()),55)

    def test_negative_and_zero_limit_rejected(self):
        for val in (0,-2,"55"):
            with self.assertRaises(audit.EvidenceError):
                audit.first_words("any text",val)

    def test_commercial_disclosure_lost_in_default(self):
        self.assertFalse(self.rows[2]["default_surrogate_has_commission_disclosure"])
        self.assertFalse(self.rows[4]["default_surrogate_has_commission_disclosure"])

    def test_optional_both_disclose(self):
        self.assertTrue(self.rows[2]["optional_excerpt_contains_commission_note"])
        self.assertTrue(self.rows[4]["optional_excerpt_contains_commission_note"])

    def test_optional_guides_still_no_live_url(self):
        self.assertIsNone(self.rows[2]["optional_cta_url"])
        self.assertIsNone(self.rows[4]["optional_cta_url"])

    def test_canonical_links_still_placeholders(self):
        for index in (2,4):
            self.assertTrue(self.rows[index]["canonical_cta"].startswith("[["))

    def test_subject_fourteen_unsupported(self):
        self.assertIn("seventeen seconds",self.rows[3]["canonical_subject"].lower())
        self.assertIn("17.1 seconds",self.rows[3]["default_55_word_surrogate"].lower())

    def test_optional_subject_already_differs_issue04(self):
        self.assertTrue(self.rows[3]["subject_exact_match"])

    def test_no_alternative_approved_by_default(self):
        self.assertFalse(audit.audit()["founder_approved"])

    def test_no_email_test_verified(self):
        self.assertFalse(audit.audit()["real_received_email_verified"])

    def test_six_hard_holds(self):
        self.assertTrue(all("HOLD_" in row["hold"] for row in self.rows))

    def test_disallowed_canonical_activation_fails_closed(self):
        import copy
        v=copy.deepcopy(self.manifest)
        v["issues"][2]["merchant_affiliate_url"]="https://example.org/unapproved"
        self.assertRaises(audit.EvidenceError,lambda: audit.audit_data(v,self.optional))

    def test_mismatched_issue_kind_rejected(self):
        import copy
        p=copy.deepcopy(self.optional)
        p["issues"][4]["kind"]="editorial"
        self.assertRaises(audit.EvidenceError,lambda: audit.audit_data(self.manifest,p))

    def test_broken_date_count_rejected(self):
        import copy
        p=copy.deepcopy(self.optional)
        p["issues"].pop()
        self.assertRaises(audit.EvidenceError,lambda: audit.audit_data(self.manifest,p))

    def test_no_network_or_write_code_in_inspector(self):
        code=SRC.read_text(encoding="utf-8")
        for token in ("requests.get(", "urllib.request.urlopen", "smtplib", "write_text(", "write_bytes(", "subprocess.run("):
            self.assertNotIn(token,code)

if __name__ == "__main__":
    unittest.main()
