"""R189 pure-Python regression tests for HTML node boundary release hold."""
from __future__ import annotations

import unittest
from catalog_fragment_custody_r189 import check_fragmented_claims


class CatalogFragmentCustodyR189(unittest.TestCase):
    def reject(self, *chunks):
        with self.assertRaises(ValueError) as cm:
            check_fragmented_claims(list(chunks))
        self.assertNotIn("SECRET", str(cm.exception))
        self.assertNotIn("customer", str(cm.exception))

    def test_existing_text_allowed(self):
        check_fragmented_claims([
            "No downloads are available until builds pass testing, security review and verification.",
            "The premium editions are in private development preview.",
            "Contact Final Vestige about a pilot",
        ])

    def test_empty_allowed(self):
        check_fragmented_claims([])

    def test_repeated_determinism(self):
        sample = ["Request a confidential pilot discussion."]
        self.assertIsNone(check_fragmented_claims(sample))
        self.assertIsNone(check_fragmented_claims(sample))

    def test_download_word_split_and_heading_adjacent(self):
        self.reject("Down", "load ", "now", "Pilot with us")

    def test_download_single_letter_nodes(self):
        self.reject("D", "o", "w", "n", "l", "o", "a", "d", " ", "n", "o", "w")

    def test_download_split_in_two_places(self):
        self.reject("Do", "wn", "load h", "ere", "Pilot with us")

    def test_purchase_split_across_nodes(self):
        self.reject("Pur", "chase ", "to", "day")

    def test_buy_now_at_boundary(self):
        self.reject("Buy ", "now", "Other section")

    def test_get_here_node_separator(self):
        self.reject("Get", "here", "Pilot")

    def test_available_for_download_fragmented(self):
        self.reject("Avail", "able", " for ", "down", "load", "Pilot")

    def test_available_for_purchase_fragmented(self):
        self.reject("Available ", "for ", "pur", "chase", "Pilot")

    def test_available_now_split(self):
        self.reject("Av", "ailable ", "no", "w", "Pilot")

    def test_direct_download_split(self):
        self.reject("Direct ", "down", "load", "Pilot")

    def test_public_download_split(self):
        self.reject("Pub", "lic", " ", "down", "load", "Pilot")

    def test_instant_download_split(self):
        self.reject("Instant ", "down", "load", "Pilot")

    def test_released_fragmented(self):
        self.reject("Re", "leased", "Pilot")

    def test_for_sale_fragmented(self):
        self.reject("For ", "sa", "le", "Pilot")

    def test_on_sale_fragmented(self):
        self.reject("On", "sale", "Pilot")

    def test_exe_extension_split_then_heading(self):
        self.reject("GrantAudit.e", "x", "e", "Pilot with us")

    def test_msix_suffix_followed_by_heading(self):
        self.reject("ProcureGuard.msix", "Pilot with us")

    def test_msi_suffix_split(self):
        self.reject("ProcureGuard.m", "s", "i", "Pilot")

    def test_msixbundle_suffix_split(self):
        self.reject("ProcureGuard.msix", "bundle", "Pilot")

    def test_zip_extension_split(self):
        self.reject("private.z", "ip", "Pilot")

    def test_7z_extension_split(self):
        self.reject("private.7", "z", "Pilot")

    def test_pkg_extension_split(self):
        self.reject("private.pk", "g", "Pilot")

    def test_uppercase_artifact(self):
        self.reject("PRIVATE.E", "XE", "Pilot")

    def test_normal_visible_prose_not_rejected(self):
        check_fragmented_claims(["Get ", "a status update ", "about our development roadmap."])

    def test_nonrelease_status_not_rejected(self):
        check_fragmented_claims(["Pricing and availability have not been announced."])

    def test_dotted_plain_abbreviation_allowed(self):
        check_fragmented_claims(["A .example domain is not a link in this static text."])

    def test_separator_codepoint_from_input_rejected(self):
        self.reject("Contains \ue000 SECRET")

    def test_invalid_tuple_shape_rejected(self):
        with self.assertRaises(ValueError):
            check_fragmented_claims(("download", "now"))

    def test_invalid_str_subclass_rejected(self):
        class Fake(str):
            def __str__(self):
                raise RuntimeError("user hook")
        self.reject(Fake("customer SECRET"))

    def test_chunk_limit_rejected(self):
        with self.assertRaises(ValueError):
            check_fragmented_claims([""] * 10001)

    def test_character_limit_rejected(self):
        self.reject("customer SECRET" * 10000)

    def test_no_data_change_to_input(self):
        raw = ["Private", " pilot review"]
        before = raw.copy()
        check_fragmented_claims(raw)
        self.assertEqual(raw, before)


if __name__ == "__main__":
    unittest.main()


class CatalogFragmentHTMLParserR189(unittest.TestCase):
    """Real Python HTMLParser node boundaries, including nested inline tags."""
    def run_markup(self, markup):
        from html.parser import HTMLParser
        class Capture(HTMLParser):
            def __init__(self):
                super().__init__(convert_charrefs=True)
                self.chunks = []
            def handle_data(self, data):
                self.chunks.append(data)
        parser = Capture()
        parser.feed(markup)
        parser.close()
        return check_fragmented_claims(parser.chunks)

    def test_real_html_split_download(self):
        with self.assertRaises(ValueError):
            self.run_markup('<p>Down<strong>load </strong><strong>now</strong></p><h2>Pilot with us</h2>')

    def test_real_html_split_release(self):
        with self.assertRaises(ValueError):
            self.run_markup('<p>Re<strong>leased</strong></p><h2>Pilot with us</h2>')

    def test_real_html_split_installer(self):
        with self.assertRaises(ValueError):
            self.run_markup('<p>GrantAudit.e<strong>x</strong>e</p><h2>Pilot with us</h2>')

    def test_real_html_split_msix(self):
        with self.assertRaises(ValueError):
            self.run_markup('<p>ProcureGuard.m<strong>six</strong></p><h2>Pilot with us</h2>')

    def test_real_html_entity_decoded_phrase(self):
        with self.assertRaises(ValueError):
            self.run_markup('<p>Down<strong>load &#x6e;ow</strong></p>')

    def test_real_html_available_now_split(self):
        with self.assertRaises(ValueError):
            self.run_markup('<p>Avail<strong>able </strong><strong>now</strong></p><h2>Pilot with us</h2>')

    def test_real_html_release_claim_across_blocks(self):
        with self.assertRaises(ValueError):
            self.run_markup('<p>Get</p><p>here</p><h2>Pilot with us</h2>')

    def test_real_html_legitimate_discussion(self):
        self.assertIsNone(self.run_markup('<p>Development is in progress.</p><p>Contact about private pilot review.</p>'))
