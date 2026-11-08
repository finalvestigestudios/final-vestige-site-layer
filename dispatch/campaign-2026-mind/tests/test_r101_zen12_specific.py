"""R101 adversarial, fail-closed tests. No network, mail, subscriber data or WordPress writes."""
import copy,importlib.util,pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
P=ROOT/"r101-zen12-specific"
S=importlib.util.spec_from_file_location("zen12_r101_guard",P/"guard.py")
import sys
g=importlib.util.module_from_spec(S);sys.modules[S.name]=g;S.loader.exec_module(g)
class Zen12SpecificGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.l,cls.md,cls.txt,cls.html=g.load()
    def run_gate(self,l=None,md=None,txt=None,html=None):
        return g.validate(l if l is not None else self.l,md if md is not None else self.md,txt if txt is not None else self.txt,html if html is not None else self.html)
    def test_01_baseline_clean(self):self.assertEqual(self.run_gate(),[])
    def test_02_original_master_identity(self):self.assertEqual(self.l["original_master_sha"],"d57ccdba3aee8f065e143e101c2945f4f3d01647")
    def test_03_original_issue03_unchanged(self):
        orig=(ROOT/"issues"/"03-the-twelve-minute-question.md").read_text(encoding="utf8")
        self.assertIn("The twelve-minute meditation question",orig)
        self.assertNotIn(self.l["subject"],orig)
    def test_04_mix_preserved(self):self.assertEqual(self.l["mix"]["commercial_reserved"],[3,5])
    def test_05_fail_if_send_true(self):
        l=copy.deepcopy(self.l);l["send_authorized"]=True;self.assertTrue(self.run_gate(l=l))
    def test_06_fail_if_sends_nonzero(self):
        l=copy.deepcopy(self.l);l["sends_this_run"]=1;self.assertTrue(self.run_gate(l=l))
    def test_07_fail_if_mix_altered(self):
        l=copy.deepcopy(self.l);l["mix"]["editorial"].append(3);self.assertTrue(self.run_gate(l=l))
    def test_08_fail_if_named_affiliate_acceptance_asserted(self):
        l=copy.deepcopy(self.l);l["affiliate_permissions"]["final_vestige_named_acceptance"]=True;self.assertTrue(self.run_gate(l=l))
    def test_09_fail_if_email_permission_asserted(self):
        l=copy.deepcopy(self.l);l["affiliate_permissions"]["email_channel_authorized"]=True;self.assertTrue(self.run_gate(l=l))
    def test_10_fail_if_private_reporting_contract_asserted(self):
        l=copy.deepcopy(self.l);l["affiliate_permissions"]["aggregate_only_no_purchaser_pii_contract"]=True;self.assertTrue(self.run_gate(l=l))
    def test_11_fail_if_merchant_link_inserted(self):
        l=copy.deepcopy(self.l);l["approved_affiliate_merchant_url"]="https://somewhere.invalid";self.assertTrue(self.run_gate(l=l))
    def test_12_fail_if_guide_claimed_live(self):
        l=copy.deepcopy(self.l);l["approved_live_buyer_guide_url"]="https://finalvestige.com/any";self.assertTrue(self.run_gate(l=l))
    def test_13_fail_if_verified_recipient_guessed(self):
        l=copy.deepcopy(self.l);l["wp_settings_snapshot"]["verified_eligible_recipients"]=2;self.assertTrue(self.run_gate(l=l))
    def test_14_fail_if_auto_send_changed(self):
        l=copy.deepcopy(self.l);l["wp_settings_snapshot"]["new_post_default_send"]=True;self.assertTrue(self.run_gate(l=l))
    def test_15_fail_if_welcome_falsely_verified(self):
        l=copy.deepcopy(self.l);l["delivery_evidence"]["welcome_delivery_confirmed"]=True;self.assertTrue(self.run_gate(l=l))
    def test_16_fail_if_preheader_claimed_native(self):
        l=copy.deepcopy(self.l);l["native_preheader_verified"]=True;self.assertTrue(self.run_gate(l=l))
    def test_17_fail_if_disclosure_missing_excerpt(self):
        l=copy.deepcopy(self.l);l["excerpt"]="Explore Zen12 and change your life";self.assertTrue(self.run_gate(l=l))
    def test_18_fail_if_tracking_in_excerpt(self):
        l=copy.deepcopy(self.l);l["excerpt"]+=" https://bad.invalid/?uid=123";self.assertTrue(self.run_gate(l=l))
    def test_19_fail_if_replaced_postal_placeholder(self):
        self.assertTrue(self.run_gate(md=self.md.replace(g.POSTAL,"Vendor's London address")))
    def test_20_fail_if_unsubscribe_placeholder_hidden(self):
        self.assertTrue(self.run_gate(txt=self.txt.replace(g.UNSUB,"")))
    def test_21_fail_if_unauthorized_live_merchant_link(self):
        self.assertTrue(self.run_gate(html=self.html.replace("<body>","<body><a href='https://zen12.com'>Buy</a>")))
    def test_22_fail_if_mail_has_remote_image(self):
        self.assertTrue(self.run_gate(html=self.html.replace("<body>","<body><img src='https://example.com/p.png'>")))
    def test_23_fail_if_script_added(self):
        self.assertTrue(self.run_gate(html=self.html.replace("<body>","<body><script>alert(1)</script>")))
    def test_24_fail_if_claim_presented_as_proven(self):
        self.assertTrue(self.run_gate(md=self.md+"\nClinically proven to reprogram."))
    def test_25_fail_if_wrong_tier_claim(self):
        self.assertTrue(self.run_gate(md=self.md+"\n48 MP3s in every tier."))
    def test_26_fail_if_fixed_price(self):
        self.assertTrue(self.run_gate(md=self.md+"\n$67.77"))
    def test_27_fail_if_duplicate_cta(self):
        self.assertTrue(self.run_gate(md=self.md+"\n"+g.TOKEN))
    def test_28_fail_if_source_limitations_removed(self):
        l=copy.deepcopy(self.l);l["sources"][0]["limitations"]="";self.assertTrue(self.run_gate(l=l))
    def test_29_official_sources_present(self):
        urls={x["url"] for x in self.l["sources"]}
        self.assertTrue(all(x in urls for x in ["https://zen12.com/","https://inspire3.com/privacy/","https://inspire3.com/terms/"]))
    def test_30_marked_not_actual_email(self):self.assertIn("NOT A JETPACK RECEIVED EMAIL",self.html)
    def test_31_no_purchase_conversion_claim(self):
        self.assertIsNone(self.l["approved_affiliate_merchant_url"])
        self.assertIsNone(self.l["wp_settings_snapshot"]["verified_eligible_recipients"])
    def test_32_no_email_requests(self):
        self.assertEqual(self.l["sends_this_run"],0)
        self.assertFalse(self.l["send_authorized"])
if __name__=="__main__":unittest.main()
