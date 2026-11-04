"""R188: independent fail-closed catalog visible-text guard regression tests."""
from __future__ import annotations

import unittest
from catalog_visible_hold_r188 import check_visible_hold


class CatalogVisibleHoldR188(unittest.TestCase):
    def assert_blocked(self, *chunks):
        with self.assertRaises(ValueError) as cm:
            check_visible_hold(list(chunks))
        # Never echo an accidentally pasted premium entitlement URL or token.
        self.assertNotIn('SECRET', str(cm.exception))
        self.assertNotIn('example', str(cm.exception))

    def test_genuine_unreleased_copy_and_contact_label(self):
        check_visible_hold([
            'No downloads are available until builds pass testing, security review and verification.',
            'Pricing and availability have not been announced.',
            'Contact Final Vestige about a pilot',
            'PREMIUM · PRIVATE DEVELOPMENT PREVIEW',
            'No mandatory account, no upload of your records.',
        ])

    def test_empty_copy(self):
        check_visible_hold([])

    def test_repeat_determinism(self):
        text = ['Four free and two premium products in development.']
        self.assertIsNone(check_visible_hold(text))
        self.assertIsNone(check_visible_hold(text))

    def test_http_visible_bare_link(self):
        self.assert_blocked('Private: http://example.test/SECRET')

    def test_https_premium_visible_bare_link(self):
        self.assert_blocked('Access premium at https://example.test/SECRET')

    def test_https_casefold_scheme(self):
        self.assert_blocked('HTTPS://example.test/SECRET')

    def test_https_split_inline_nodes(self):
        self.assert_blocked('h', 't', 't', 'p', 's', ':', '//example.test/SECRET')

    def test_ftp_destination(self):
        self.assert_blocked('ftp://example.test/SECRET')

    def test_file_destination(self):
        self.assert_blocked('file:///home/SECRET')

    def test_gs_destination(self):
        self.assert_blocked('gs://bucket/SECRET')

    def test_s3_destination(self):
        self.assert_blocked('s3://bucket/SECRET')

    def test_www_plaintext(self):
        self.assert_blocked('www.example.test/SECRET')

    def test_mailto_visible_text(self):
        self.assert_blocked('mailto:private@example.test')

    def test_javascript_scheme(self):
        self.assert_blocked('javascript:alert(1)')

    def test_data_uri(self):
        self.assert_blocked('data:application/octet-stream;base64,SECRET')

    def test_windows_exe_filename(self):
        self.assert_blocked('GrantAuditStudioPro.exe')

    def test_msi_filename(self):
        self.assert_blocked('/premium/ProcureGuard.msi')

    def test_msix_bundle(self):
        self.assert_blocked('ProcureGuard.msixbundle')

    def test_archive_zip(self):
        self.assert_blocked('binary.zip')

    def test_archive_7z(self):
        self.assert_blocked('binary.7z')

    def test_executable_extension_split_nodes(self):
        self.assert_blocked('Windows', 'Utility', '.', 'exe')

    def test_extension_at_node_boundary(self):
        self.assert_blocked("installer.msix", "Pilot with us")

    def test_release_phrase_at_node_boundary(self):
        self.assert_blocked("Download ", "now", "Pilot with us")

    def test_download_now(self):
        self.assert_blocked('Download now')

    def test_download_here(self):
        self.assert_blocked('Download here!')

    def test_buy_today(self):
        self.assert_blocked('Buy today')

    def test_purchase_here(self):
        self.assert_blocked('Purchase here')

    def test_available_now(self):
        self.assert_blocked('Available now')

    def test_available_for_download(self):
        self.assert_blocked('Available for download')

    def test_public_download(self):
        self.assert_blocked('PUBLIC DOWNLOAD')

    def test_released_claim(self):
        self.assert_blocked('Released!')

    def test_on_sale(self):
        self.assert_blocked('The premium editions are on sale')

    def test_zero_width_space_scheme(self):
        self.assert_blocked('http\u200bs://example.test/SECRET')

    def test_soft_hyphen(self):
        self.assert_blocked('Down\u00adload now')

    def test_bidi_override(self):
        self.assert_blocked('hello\u202eworld')

    def test_paragraph_separator(self):
        self.assert_blocked('hello\u2029world')

    def test_nul(self):
        self.assert_blocked('hello\0world')

    def test_unpaired_surrogate(self):
        self.assert_blocked('hello\ud800world')

    def test_regular_combining_accent_is_allowed(self):
        check_visible_hold(['Our premie\u0300re release is still in development.'])

    def test_untrusted_string_subclass_rejected(self):
        class Spy(str):
            def __str__(self):
                raise AssertionError('must not run')
        self.assert_blocked(Spy('SECRET'))

    def test_untrusted_container_rejected(self):
        with self.assertRaises(ValueError):
            check_visible_hold(('plaintext',))

    def test_many_chunks_rejected(self):
        with self.assertRaises(ValueError):
            check_visible_hold(['x'] * 10001)

    def test_content_size_rejected(self):
        with self.assertRaises(ValueError):
            check_visible_hold(['x' * 81921])


if __name__ == '__main__':
    unittest.main()
