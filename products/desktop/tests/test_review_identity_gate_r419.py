"""R419 synthetic premium audit identity guards; no payments or executable release."""
from __future__ import annotations

import unittest
from fvs_suite.review_identity_gate_r419 import (
    require_canonical_digest, require_native_choice, require_native_string,
)


class ReviewIdentityGateR419Tests(unittest.TestCase):
    def test_real_sha256_is_unchanged(self):
        original = 'a' * 64
        self.assertIs(require_canonical_digest(original), original)

    def test_other_valid_canonical_sha256_bytes(self):
        self.assertEqual(require_canonical_digest('0123456789abcdef' * 4),
                         '0123456789abcdef' * 4)

    def test_uppercase_sha256_rejected(self):
        with self.assertRaisesRegex(ValueError, 'canonical'):
            require_canonical_digest('A' * 64)

    def test_malformed_sha256_rejected(self):
        for value in ('', '0' * 63, '0' * 65, 'g' * 64, '💳' * 64, '\x00' * 64,
                      None, b'a' * 64, 12, ['a'] * 64):
            with self.subTest(type=type(value).__name__):
                with self.assertRaisesRegex(ValueError, 'canonical'):
                    require_canonical_digest(value)

    def test_subclass_with_forged_equality_never_called_for_sha(self):
        class ForgedHash(str):
            def __eq__(self, other):
                raise AssertionError('PRIVATE_REPORT_HASH_HOOK')
            def __hash__(self):
                raise AssertionError('PRIVATE_REPORT_HASH_HOOK')
            def __len__(self):
                raise AssertionError('PRIVATE_REPORT_HASH_HOOK')
        with self.assertRaisesRegex(ValueError, 'canonical') as raised:
            require_canonical_digest(ForgedHash('a' * 64))
        self.assertNotIn('PRIVATE_REPORT_HASH_HOOK', str(raised.exception))

    def test_native_decisions_accepted(self):
        allowed = ('needs_evidence', 'escalated', 'reviewed')
        for value in allowed:
            self.assertIs(require_native_choice(value, allowed, 'Invalid decision'), value)

    def test_native_products_accepted(self):
        for value in ('grants', 'procurement'):
            self.assertEqual(require_native_choice(value, ('grants', 'procurement'), 'Invalid product'), value)

    def test_unknown_decision_and_product_fail(self):
        for value, choices in (('approved', ('needs_evidence', 'reviewed')),
                               ('paid', ('needs_evidence', 'reviewed')),
                               ('ledger', ('grants', 'procurement')),
                               ('', ('grants', 'procurement'))):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, 'Invalid'):
                    require_native_choice(value, choices, 'Invalid choice')

    def test_subclass_overriding_equality_never_called_for_choice(self):
        class ForgedDecision(str):
            def __eq__(self, other):
                raise AssertionError('PRIVATE_DECISION_HOOK')
        with self.assertRaisesRegex(ValueError, 'Invalid') as raised:
            require_native_choice(ForgedDecision('approved'), ('reviewed',), 'Invalid choice')
        self.assertNotIn('PRIVATE_DECISION_HOOK', str(raised.exception))

    def test_nonnative_source_case_id_rejected_without_hooks(self):
        class ForgedId(str):
            def __hash__(self):
                raise AssertionError('PRIVATE_CASE_ID')
            def __eq__(self, other):
                raise AssertionError('PRIVATE_CASE_ID')
        with self.assertRaisesRegex(ValueError, '^Invalid case id$'):
            require_native_string(ForgedId('a' * 64), 'Invalid case id')
        self.assertEqual(require_native_string('plain', 'Invalid case id'), 'plain')

    def test_nonnative_choice_has_fixed_error(self):
        class Hostile:
            def __eq__(self, other):
                raise AssertionError('PRIVATE_VALUE')
            def __str__(self):
                raise AssertionError('PRIVATE_VALUE')
        with self.assertRaisesRegex(ValueError, '^Invalid choice$'):
            require_native_choice(Hostile(), ('grants',), 'Invalid choice')


if __name__ == '__main__':
    unittest.main()
