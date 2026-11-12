"""R383: customer-side offline license reader, synthetic filesystem canaries only."""
from __future__ import annotations

import contextlib
import io
import pathlib
import traceback
import unittest
from unittest.mock import Mock

from fvs_suite.entitlement_reader_privacy_r383 import read_private_entitlement

CANARY = '/operator/private/acme-customer/salary-file/secret.fvslicense'


class ClientError(ValueError):
    pass


class ClientEntitlementPrivacyR383Tests(unittest.TestCase):
    def setUp(self):
        self.source = pathlib.Path(CANARY)

    def read(self, reader):
        return read_private_entitlement(self.source, 8192, reader, ClientError)

    def denied(self, exception, expected):
        reader = Mock(side_effect=exception)
        with self.assertRaises(ClientError) as found:
            self.read(reader)
        caught = found.exception
        self.assertEqual(str(caught), expected)
        self.assertIsNone(caught.__cause__)
        self.assertIsNone(caught.__context__)
        self.assertNotIn(CANARY, ''.join(traceback.format_exception(caught)))
        self.assertNotIn(CANARY, str(caught.args))
        reader.assert_called_once_with(self.source, 8192, 'Entitlement file')

    def test_success_preserves_exact_bytes_and_one_local_read(self):
        data = b'{"test":"synthetic"}\n'
        reader = Mock(return_value=data)
        self.assertIs(self.read(reader), data)
        reader.assert_called_once_with(self.source, 8192, 'Entitlement file')

    def test_limit_error_preserves_existing_public_size_message(self):
        self.denied(ValueError('Entitlement file exceeds its allowed size: ' + CANARY),
                    'Entitlement file exceeds the size limit')

    def test_nonregular_error_drops_path_from_display_and_context(self):
        self.denied(ValueError('Entitlement file must be one regular file: ' + CANARY),
                    'Entitlement must be a stable, distinct regular file')

    def test_changed_path_error_is_fail_closed(self):
        self.denied(ValueError('Entitlement file path changed during access: ' + CANARY),
                    'Entitlement must be a stable, distinct regular file')

    def test_permission_denied_path_is_not_retained(self):
        self.denied(PermissionError(13, 'private data', CANARY),
                    'Entitlement file is inaccessible or changed during verification')

    def test_missing_file_path_is_not_retained(self):
        self.denied(FileNotFoundError(2, 'private data', CANARY),
                    'Entitlement file is inaccessible or changed during verification')

    def test_directory_error_path_is_not_retained(self):
        self.denied(IsADirectoryError(21, 'private data', CANARY),
                    'Entitlement file is inaccessible or changed during verification')

    def test_nested_os_exception_in_valueerror_is_not_retained(self):
        original = OSError(CANARY)
        source = ValueError('private read failed: ' + CANARY)
        source.__cause__ = original
        self.denied(source, 'Entitlement must be a stable, distinct regular file')

    def test_nested_valueerror_context_is_not_retained(self):
        original = OSError(CANARY)
        source = ValueError('Entitlement file exceeds size: ' + CANARY)
        source.__context__ = original
        self.denied(source, 'Entitlement file exceeds the size limit')

    def test_source_path_with_unicode_is_not_echoed(self):
        self.source = pathlib.Path(CANARY + '-東京')
        self.denied(OSError(CANARY),
                    'Entitlement file is inaccessible or changed during verification')

    def test_same_failure_is_deterministic_across_both_premium_apps(self):
        for product in ('grants', 'procurement'):
            with self.subTest(product=product):
                # The verifier binds product identity after this common read.
                self.denied(OSError(f'{product}: {CANARY}'),
                            'Entitlement file is inaccessible or changed during verification')

    def test_no_stdout_or_stderr_on_read_failure(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.denied(OSError(CANARY),
                        'Entitlement file is inaccessible or changed during verification')
        self.assertEqual((out.getvalue(), err.getvalue()), ('', ''))

    def test_does_not_retry_after_ambiguous_os_failure(self):
        reader = Mock(side_effect=[OSError(CANARY), b'do not accept'])
        with self.assertRaises(ClientError):
            self.read(reader)
        self.assertEqual(reader.call_count, 1)

    def test_interrupt_is_not_swallowed_or_misreported(self):
        with self.assertRaises(KeyboardInterrupt):
            self.read(Mock(side_effect=KeyboardInterrupt()))

    def test_typeerror_programming_fault_not_disguised_as_corrupt_file(self):
        with self.assertRaises(TypeError):
            self.read(Mock(side_effect=TypeError('programming fault')))

    def test_str_source_passed_through_unchanged(self):
        input_path = CANARY
        reader = Mock(return_value=b'signed bytes')
        result = read_private_entitlement(input_path, 8192, reader, ClientError)
        self.assertEqual(result, b'signed bytes')
        reader.assert_called_once_with(input_path, 8192, 'Entitlement file')


if __name__ == '__main__':
    unittest.main()
