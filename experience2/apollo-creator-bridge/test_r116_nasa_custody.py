"""R116 NASA source custody regression and negative controls; executable stdlib tests."""
import copy
import json
from pathlib import Path
import unittest

from qa_r116_nasa_custody import CustodyError, validate

BASE = Path(__file__).resolve().parent
HTML = (BASE / "landing-preview.html").read_text(encoding="utf-8")
LEDGER = json.loads((BASE / "nasa-source-custody-r116.json").read_text(encoding="utf-8"))


class NASAProvenanceContracts(unittest.TestCase):
    def reject(self, html=HTML, ledger=None):
        with self.assertRaises(CustodyError):
            validate(html, LEDGER if ledger is None else ledger)

    def test_actual_staging_html_passes_source_contract_only(self):
        result = validate(HTML, LEDGER)
        self.assertEqual(result["records"], 6)
        self.assertEqual(result["release"], "STAGING_HOLD")
        self.assertEqual(result["confirmed_catalog_ids"], 5)
        self.assertEqual(result["browser_axe_wordpress_merchant"], "NOT_TESTED")

    def test_low_contrast_print_credit_fails(self):
        self.reject(HTML.replace("small,.muted{color:#111!important}", ""))

    def test_missing_nasa_source_credits_fail(self):
        self.reject(HTML.replace("Image Credit: NASA/Kim Shiflett", "Credit unverified", 1))

    def test_unconfirmed_crew_id_cannot_be_upgraded(self):
        changed = copy.deepcopy(LEDGER)
        changed["records"][0]["catalog_status"] = "CONFIRMED_ON_CITED_PAGE"
        self.reject(ledger=changed)

    def test_wrong_photo_date_fails(self):
        self.reject(HTML.replace("Jan 28, 1967", "Jan 27, 1967", 1))

    def test_link_change_fails(self):
        self.reject(HTML.replace("https://www.nasa.gov/image-detail/amf-s66-58038/",
                                 "https://example.org/bogus-image/", 1))

    def test_duplicate_photo_source_row_fails(self):
        self.reject(HTML.replace('id="photo-source-06"', 'id="photo-source-05"', 1))

    def test_invented_geo_pin_fails(self):
        changed = copy.deepcopy(LEDGER)
        changed["records"][0]["latitude"] = 28.0
        self.reject(ledger=changed)

    def test_invented_relationship_edge_fails(self):
        changed = copy.deepcopy(LEDGER)
        changed["records"][1]["relationship_edges"] = ["caused_fire"]
        self.reject(ledger=changed)

    def test_rights_status_cannot_claim_approval(self):
        changed = copy.deepcopy(LEDGER)
        changed["records"][2]["commercial_photo_reuse"] = "APPROVED"
        self.reject(ledger=changed)

    def test_embedded_nasa_photo_is_not_approved(self):
        self.reject(HTML.replace("</main>", '<img src="https://www.nasa.gov/example.jpg" alt="Unreviewed image"></main>'))

    def test_unreviewed_commercial_link_is_not_approved(self):
        self.reject(HTML.replace("</main>", '<a href="https://payhip.com/b/unverified">Buy</a></main>'))

    def test_additional_capture_form_is_not_approved(self):
        self.reject(HTML.replace("</main>", '<form><input type="email"></form></main>'))

    def test_second_primary_action_is_not_approved(self):
        self.reject(HTML.replace("</main>", '<a href="#classroom-preview" data-fv-primary-cta>More</a></main>'))

    def test_official_url_host_must_be_exact(self):
        changed = copy.deepcopy(LEDGER)
        changed["records"][0]["official_url"] = "https://www.nasa.gov.evil.example/image-detail/apollo-1-crew-honored/"
        self.reject(ledger=changed)

    def test_rail_target_mismatch_fails(self):
        self.reject(HTML.replace('href="#photo-source-06" data-fv-photo-record="06"',
                                 'href="#photo-source-05" data-fv-photo-record="06"', 1))


if __name__ == "__main__":
    unittest.main()
