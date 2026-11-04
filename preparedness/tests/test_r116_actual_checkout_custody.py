"""Actual-checkout R116 custody check for the complete regression suite.

This is deliberately NOT an editorial, QD, medical or publication approval.
The 71 synthetic tests exercise behavior separately; this one protects the
35 original metadata byte identities in a populated repository checkout.
"""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / 'preparedness/tools/r116_frozen_metadata_and_roster_gate.py'
spec = importlib.util.spec_from_file_location('r116_checkout_gate', PATH)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class R116ActualCheckoutCustody(unittest.TestCase):
    def test_all_35_original_metadata_exact_and_release_held(self):
        result = gate.audit_checkout(ROOT)
        self.assertEqual(result['original_metadata_git_blobs_verified'], 35)
        self.assertEqual(result['paired_article_bodies_in_inventory'], 35)
        self.assertEqual(result['article_scoped_source_use_ids_NOT_GLOBAL_UNIQUE'], 364)
        self.assertEqual(result['release_state'], 'HOLD')
        self.assertIs(result['may_publish'], False)
        self.assertIs(result['independent_QD_PASS'], False)
        self.assertIs(result['medical_safety_verified'], False)


if __name__ == '__main__':
    unittest.main()
