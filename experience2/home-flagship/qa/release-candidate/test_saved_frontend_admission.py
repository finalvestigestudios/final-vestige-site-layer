"""Dependency-free adversarial tests of exact saved-page browser guards."""
import unittest
from verify_saved_frontend_admission import validate_saved_preview, require_checks


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


if __name__ == '__main__':
    unittest.main()
