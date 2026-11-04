"""R190: compatibility-Unicode release-copy and premium-link privacy hold."""
from __future__ import annotations

import unittest
from html.parser import HTMLParser
from catalog_visible_hold_r188 import check_visible_hold


class CatalogCompatibilityR190(unittest.TestCase):
    def blocked(self, *chunks):
        with self.assertRaises(ValueError) as cm:
            check_visible_hold(list(chunks))
        self.assertNotIn("SECRET", str(cm.exception))
        self.assertNotIn("customer", str(cm.exception))

    def test_fullwidth_download_now(self):
        self.blocked("Ｄｏｗｎｌｏａｄ ｎｏｗ")

    def test_fullwidth_purchase_today(self):
        self.blocked("Ｐｕｒｃｈａｓｅ ｔｏｄａｙ")

    def test_circled_download_now(self):
        self.blocked("Ⓓⓞⓦⓝⓛⓞⓐⓓ ⓝⓞⓦ")

    def test_math_bold_download_now(self):
        self.blocked("𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝 𝐧𝐨𝐰")

    def test_fullwidth_release_status(self):
        self.blocked("Ｒｅｌｅａｓｅｄ")

    def test_fullwidth_available_for_download(self):
        self.blocked("Ａｖａｉｌａｂｌｅ ｆｏｒ ｄｏｗｎｌｏａｄ")

    def test_fullwidth_extension(self):
        self.blocked("customer SECRET Studio.ｅｘｅ")

    def test_circled_extension(self):
        self.blocked("private.ⓜⓢⓘⓧ")

    def test_fullwidth_dot_and_extension(self):
        self.blocked("GrantAudit．ｍｓｉ")

    def test_fullwidth_url_scheme_and_colon(self):
        self.blocked("ｈｔｔｐｓ：//example.test/SECRET")

    def test_fullwidth_www_dot(self):
        self.blocked("ｗｗｗ．example.test/SECRET")

    def test_fullwidth_s3_bucket(self):
        self.blocked("ｓ３：//private/SECRET")

    def test_fullwidth_data_scheme(self):
        self.blocked("ｄａｔａ：payloadSECRET")

    def test_nonbreaking_space_in_claim(self):
        self.blocked("Download\u00a0now")

    def test_fullwidth_split_word_at_node_boundary(self):
        self.blocked("Ｄｏｗ", "ｎｌｏａｄ ", "ｎｏｗ", "Pilot")

    def test_mixed_fullwidth_ascii_extension_at_boundary(self):
        self.blocked("GrantAudit．ｅ", "x", "ｅ", "Pilot")

    def test_nonbreaking_space_between_nodes(self):
        self.blocked("Ａｖａｉｌａｂｌｅ", "\u00a0for ", "download", "Pilot")

    def test_mixed_fullwidth_across_nodes(self):
        self.blocked("Down", "ｌｏａｄ ", "ｎｏｗ", "Pilot")

    def test_real_html_fullwidth_claim(self):
        self.blocked(*self.parse('<p>Ｄｏｗ<strong>ｎｌｏａｄ </strong><strong>ｎｏｗ</strong></p>'))

    def test_real_html_fullwidth_filename(self):
        self.blocked(*self.parse('<p>GrantAudit．ｅ<strong>ｘ</strong>ｅ</p>'))

    def test_real_html_circled_entities(self):
        self.blocked(*self.parse('<p>&#x24B9;&#x24DE;&#x24E6;&#x24DD;&#x24DB;&#x24DE;&#x24D0;&#x24D3; now</p>'))

    def test_original_input_not_mutated(self):
        src = ["No downloads are available until builds pass testing.", "Ｐｒｉｖａｔｅ pilot"]
        original = src.copy()
        self.assertIsNone(check_visible_hold(src))
        self.assertEqual(src, original)

    def test_actual_unreleased_copy_allowed(self):
        self.assertIsNone(check_visible_hold([
            "No downloads are available until builds pass testing, security review and verification.",
            "Pricing and availability have not been announced.",
            "Four focused tools. No mandatory account, no upload of your records.",
        ]))

    def test_legitimate_fullwidth_ordinary_copy_allowed(self):
        self.assertIsNone(check_visible_hold(["Ｐｒｉｖａｔｅ pilot discussions are in development."]))

    def test_normal_combining_accents_allowed(self):
        self.assertIsNone(check_visible_hold(["Re\u0301sum\u0301e of proposed improvements."]))

    def test_repeat_deterministic(self):
        sample = ["Ｐｒｉｖａｔｅ pilot only"]
        self.assertIsNone(check_visible_hold(sample))
        self.assertIsNone(check_visible_hold(sample))

    def test_shape_check_precedes_normalization(self):
        class Trap(str):
            def __str__(self):
                raise RuntimeError("untrusted hook")
        self.blocked(Trap("customer SECRET"))

    def test_normalization_expansion_over_limit_fails(self):
        # U+3300 compatibility expansion: normalization can enlarge text.
        self.blocked("㌀" * 40000)

    def test_compatibility_cannot_hide_control_character(self):
        self.blocked("Ｆｏｏ\u202eＳＥＣＲＥＴ")

    @staticmethod
    def parse(markup):
        class Capture(HTMLParser):
            def __init__(self):
                super().__init__(convert_charrefs=True)
                self.chunks = []
            def handle_data(self, text):
                self.chunks.append(text)
        reader = Capture()
        reader.feed(markup)
        reader.close()
        return reader.chunks


if __name__ == "__main__":
    unittest.main()
