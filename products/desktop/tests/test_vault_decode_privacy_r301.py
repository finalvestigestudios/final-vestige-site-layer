"""R301 synthetic encrypted archive privacy tests (no customer data)."""
from __future__ import annotations

import base64
import json
import unittest

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fvs_suite.vault_decode_privacy import (
    decode_evidence_b64, decrypt_evidence, parse_evidence_json,
)


KEY = bytes(range(32))
NONCE = b'123456789012'
PREFIX = b'FVS-EVIDENCE-VAULT-v1\0SALT-TEST'
PRIVATE = 'CLIENT-LEDGER-SECRET-74291'


def unique_pairs(pairs):
    result = {}
    for k, v in pairs:
        if k in result:
            raise ValueError('Duplicate encrypted evidence field')
        result[k] = v
    return result


class VaultDecodePrivacyR301Tests(unittest.TestCase):
    def assert_private_error(self, operation, message):
        try:
            operation()
        except ValueError as exc:
            self.assertEqual(str(exc), message)
            self.assertIsNone(exc.__cause__)
            self.assertIsNone(exc.__context__)
            self.assertNotIn(PRIVATE, repr(exc))
        else:
            self.fail('Expected a sanitized ValueError')

    def test_good_authenticated_decrypt_returns_exact_bytes(self):
        clear = PRIVATE.encode() + b'\x00\xff'
        sealed = AESGCM(KEY).encrypt(NONCE, clear, PREFIX)
        self.assertEqual(decrypt_evidence(KEY, NONCE, sealed, PREFIX), clear)

    def test_bad_key_no_exception_chain(self):
        sealed = AESGCM(KEY).encrypt(NONCE, PRIVATE.encode(), PREFIX)
        self.assert_private_error(lambda: decrypt_evidence(b'Z' * 32, NONCE, sealed, PREFIX),
                                  'Wrong passphrase or encrypted archive was altered')

    def test_bad_ciphertext_no_exception_chain(self):
        sealed = bytearray(AESGCM(KEY).encrypt(NONCE, PRIVATE.encode(), PREFIX))
        sealed[1] ^= 1
        self.assert_private_error(lambda: decrypt_evidence(KEY, NONCE, bytes(sealed), PREFIX),
                                  'Wrong passphrase or encrypted archive was altered')

    def test_wrong_aad_no_exception_chain(self):
        sealed = AESGCM(KEY).encrypt(NONCE, PRIVATE.encode(), PREFIX)
        self.assert_private_error(lambda: decrypt_evidence(KEY, NONCE, sealed, PREFIX+b'X'),
                                  'Wrong passphrase or encrypted archive was altered')

    def test_malformed_json_contains_private_string_without_chain(self):
        self.assert_private_error(lambda: parse_evidence_json(
            ('{"private":"' + PRIVATE + '",bad}').encode(), unique_pairs),
            'Encrypted evidence has invalid JSON')

    def test_unclosed_json_contains_private_string_without_chain(self):
        self.assert_private_error(lambda: parse_evidence_json(
            ('{"private":"' + PRIVATE + '"').encode(), unique_pairs),
            'Encrypted evidence has invalid JSON')

    def test_utf8_error_contains_raw_private_bytes_without_chain(self):
        self.assert_private_error(lambda: parse_evidence_json(PRIVATE.encode() + b'\xff', unique_pairs),
                                  'Encrypted evidence has invalid JSON')

    def test_bad_utf8_middle_of_json_no_chain(self):
        self.assert_private_error(lambda: parse_evidence_json(b'{"x":"' + PRIVATE.encode() + b'\xff"}', unique_pairs),
                                  'Encrypted evidence has invalid JSON')

    def test_valid_json_returns_mapping(self):
        self.assertEqual(parse_evidence_json(b'{"b":2,"a":1}', unique_pairs), {'b':2, 'a':1})

    def test_duplicates_remain_rejected(self):
        self.assert_private_error(lambda: parse_evidence_json(b'{"x":1,"x":2}', unique_pairs),
                                  'Duplicate encrypted evidence field')

    def test_invalid_json_constant_remains_rejected(self):
        self.assert_private_error(lambda: parse_evidence_json(b'{"n":NaN}', unique_pairs),
                                  'Invalid JSON constant')

    def test_valid_plain_base64(self):
        self.assertEqual(decode_evidence_b64(base64.b64encode(PRIVATE.encode())), PRIVATE.encode())

    def test_bad_base64_type_does_not_retain_value(self):
        self.assert_private_error(lambda: decode_evidence_b64({PRIVATE:'text'}),
                                  'Malformed encrypted evidence bytes')

    def test_invalid_base64_text_does_not_retain_input(self):
        self.assert_private_error(lambda: decode_evidence_b64(PRIVATE + '#'),
                                  'Malformed encrypted evidence bytes')

    def test_base64_wrong_padding(self):
        self.assert_private_error(lambda: decode_evidence_b64(b'Z'),
                                  'Malformed encrypted evidence bytes')

    def test_empty_base64_is_valid_no_journal_case(self):
        self.assertEqual(decode_evidence_b64(''), b'')

    def test_invalid_base64_unicode(self):
        self.assert_private_error(lambda: decode_evidence_b64(PRIVATE+'\u2603'),
                                  'Malformed encrypted evidence bytes')

    def test_authentic_decrypt_then_malformed_private_json(self):
        clear = ('{"s":"' + PRIVATE + '"}{').encode()
        sealed = AESGCM(KEY).encrypt(NONCE, clear, PREFIX)
        authenticated = decrypt_evidence(KEY, NONCE, sealed, PREFIX)
        self.assertEqual(authenticated, clear)
        self.assert_private_error(lambda: parse_evidence_json(authenticated, unique_pairs),
                                  'Encrypted evidence has invalid JSON')


if __name__ == '__main__':
    unittest.main()
