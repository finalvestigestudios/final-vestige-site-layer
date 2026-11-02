"""Dependency-free adversarial tests of exact saved-page browser guards."""
import unittest
from verify_saved_frontend_admission import (validate_saved_preview, require_checks,
                                              allowed_archive_url, ARCHIVAL_MEDIA)


class SavedFrontendGuards(unittest.TestCase):
    def test_exact_local_preview_allowed(self):
        validate_saved_preview('http://127.0.0.1:9400/?page_id=42&preview=true', 42)

    def test_wrong_page_rejected(self):
        with self.assertRaisesRegex(ValueError, 'ORIGIN_REQUIRED'):
            validate_saved_preview('http://127.0.0.1:9400/?page_id=43&preview=true', 42)

    def test_hostile_preview_urls_denied(self):
        bad = (
            'https://finalvestige.com/?page_id=42&preview=true',
            'http://127.0.0.1:9400.evil.test/?page_id=42&preview=true',
            'http://localhost:9400/?page_id=42&preview=true',
            'http://127.0.0.1:9401/?page_id=42&preview=true',
            'http://user:password@127.0.0.1:9400/?page_id=42&preview=true',
            'http://127.0.0.1:9400/?page_id=42&preview=true&token=secret',
            'http://127.0.0.1:9400/?page_id=42&preview=true&token=',
            'http://127.0.0.1:9400/?page_id=42&preview=true&preview=',
            'http://127.0.0.1:9400/?page_id=42&page_id=99&preview=true',
            'http://127.0.0.1:9400/wp-admin/?page_id=42&preview=true',
            'http://127.0.0.1:9400/?page_id=42&preview=true#fragment',
            'http://127.0.0.1:9400/?page_id=42&preview=false',
        )
        for url in bad:
            with self.subTest(url=url), self.assertRaisesRegex(ValueError, 'ORIGIN_REQUIRED'):
                validate_saved_preview(url, 42)

    def test_invalid_ids_rejected(self):
        for page_id in (True, 0, -1, '42', None):
            with self.subTest(page_id=page_id), self.assertRaises(ValueError):
                validate_saved_preview('http://127.0.0.1:9400/?page_id=42&preview=true', page_id)

    def test_fail_closed_check_types_and_failures(self):
        require_checks({'native_saved': True, 'axe_aa': True})
        for value in (None, 'PASS', 1, 0, [], {}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                require_checks({'native_saved': value})
        with self.assertRaisesRegex(ValueError, 'GATE_FAILED'):
            require_checks({'native_saved': True, 'rights_safe': False})
        with self.assertRaisesRegex(ValueError, 'NOT_BOOLEAN'):
            require_checks({})

    def test_allow_only_audited_original_image_ids_and_wp_derivatives(self):
        good = (
            ('https://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp',
             'apollo'),
            ('https://i0.wp.com/finalvestige.com/wp-content/uploads/2026/08/'
             'Franklinexpeditionnote.jpg?fit=768%2C1221&ssl=1', 'franklin'),
        )
        for url, case in good:
            with self.subTest(url=url):
                self.assertTrue(allowed_archive_url(url, case))
        bad = (
            ('https://evil.test/wp-content/uploads/2026/08/s67-19766.webp', 'apollo'),
            ('https://finalvestige.com/wp-content/uploads/2026/08/5003296.jpg', 'apollo'),
            ('https://finalvestige.com/wp-content/uploads/2026/09/s67-19766.webp', 'apollo'),
            ('http://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp', 'apollo'),
            ('https://i0.wp.com/evil.test/wp-content/uploads/2026/08/s67-19766.webp', 'apollo'),
            ('https://finalvestige.com/wp-content/uploads/2026/08/Franklinexpeditionnote.jpg', 'apollo'),
            ('https://finalvestige.com:8443/wp-content/uploads/2026/08/s67-19766.webp', 'apollo'),
            ('https://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp#wrong', 'apollo'),
        )
        for url, case in bad:
            with self.subTest(url=url):
                self.assertFalse(allowed_archive_url(url, case))

    def test_expected_media_identity_contract(self):
        self.assertEqual(ARCHIVAL_MEDIA, {'apollo': 's67-19766.webp',
                                         'franklin': 'Franklinexpeditionnote.jpg'})
        self.assertFalse(allowed_archive_url('https://finalvestige.com/wp-content/uploads/'
                                             '2026/08/s67-19766.webp', 'malbone'))


if __name__ == '__main__':
    unittest.main()
