"""Dependency-free, read-only lint for the unposted Dispatch short-form creative pack."""
import json
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"social_launch_pack.json"
CANONICAL="https://finalvestige.com/dispatch/"

class SocialCreativeChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack=json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.assets=cls.pack["assets"]

    def test_six_original_unposted_slots(self):
        self.assertEqual(cls_ids := [x["edition"] for x in self.assets], list(range(1,7)))
        self.assertEqual(len(set(x["topic"] for x in self.assets)),6)
        self.assertTrue(all(x["edit_status"]=="not_recorded_not_published" and x["approval_required"] for x in self.assets))

    def test_single_existing_list_destination(self):
        self.assertEqual(self.pack["primary_destination"],CANONICAL)
        self.assertTrue(all(x["cta_url"]==CANONICAL for x in self.assets))

    def test_no_direct_seller_links_or_tracking(self):
        dumped=json.dumps(self.pack,ensure_ascii=False).lower()
        for bad in ("https://zen12.com/", "https://hypnosislive.com/", "affiliates.inspire3.com", "clickid=", "utm_campaign=", "pixel.gif"):
            self.assertNotIn(bad,dumped)

    def test_no_offer_claims_or_affiliate_selling_in_shorts(self):
        self.assertTrue(all(not x["inspire3_mention"] for x in self.assets))
        for x in self.assets:
            narration=x["narration"].lower()
            for banned in ("guaranteed wealth","hour of meditation in twelve minutes","cures anxiety","scientifically proven to cure","only today","limited-time offer"):
                self.assertNotIn(banned,narration)

    def test_production_is_accessible_and_provenance_noted(self):
        for x in self.assets:
            self.assertEqual(len(x["overlay"]),4)
            self.assertTrue(all(4<=len(s)<95 for s in x["overlay"]))
            self.assertGreater(len(x["rights_note"]),25)
            self.assertGreater(len(x["source_urls"]),0)

    def test_scripts_are_short_and_speakable(self):
        for x in self.assets:
            self.assertTrue(45<=len(x["narration"].split())<=110,(x["edition"],len(x["narration"].split())))
            self.assertTrue(5<=len(x["hook"].split())<=13)
            self.assertIn("finalvestige.com/dispatch", x["caption"].lower())

    def test_first_party_and_authoritative_sources(self):
        for x in self.assets:
            self.assertTrue(any(s.startswith("https://finalvestige.com/") or s.startswith("https://www.nccih.nih.gov/") or s.startswith("https://www.nasa.gov/") or s.startswith("https://pubmed.ncbi.nlm.nih.gov/") for s in x["source_urls"]))
            self.assertTrue(all(s.startswith("https://") for s in x["source_urls"]))

    def test_offer_subjects_keep_free_option(self):
        for n in (3,5):
            x=self.assets[n-1]
            self.assertIn("dispatch",x["caption"].lower())
            self.assertNotIn("buy",x["hook"].lower())

    def test_pack_does_not_claim_approval_or_publishing(self):
        self.assertEqual(self.pack["status"],"UNPUBLISHED_SOCIAL_CREATIVE_DRAFT")
        self.assertTrue(all(x["approval_required"] for x in self.assets))

if __name__=="__main__":
    unittest.main()
