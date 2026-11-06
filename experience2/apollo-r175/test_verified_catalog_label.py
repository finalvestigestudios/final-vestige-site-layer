import copy
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from verified_catalog_label import rewrite, blob, ORIGINAL, REPLACEMENT, FIRST_RECORD, PROVENANCE

HERE=Path(__file__).resolve().parents[1]
CANONICAL=HERE/'apollo-r174'/'research-desk-provenance-candidate-UNPUBLISHED.html'
FALLBACK=HERE/'evidence'/'R174_SOURCE_DERIVED_FIXTURE_ONLY.html'
FIXTURE=CANONICAL if CANONICAL.exists() else FALLBACK
class R175Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=FIXTURE.read_text(encoding='utf-8')
        cls.pin=blob(cls.source)
    def use(self, s): return rewrite(s,expected_blob=blob(s))
    def test_pinned_fixture_roundtrip(self):
        result, audit = rewrite(self.source,expected_blob=self.pin)
        self.assertIn(REPLACEMENT,result)
        self.assertEqual(result.replace(REPLACEMENT,ORIGINAL,1),self.source)
        self.assertTrue(audit['source_roundtrip'])
        self.assertEqual(audit['links_added'],0)
    def test_real_repo_candidate_if_available(self):
        # GitHub branch R175 stacks on R174; this runs against the ACTUAL source there.
        actual=Path(__file__).resolve().parents[1]/'apollo-r174'/'research-desk-provenance-candidate-UNPUBLISHED.html'
        if not actual.exists():
            self.skipTest('R174 canonical file not mounted locally; fixture-only evidence')
        result,audit=rewrite(actual.read_text(encoding='utf-8'))
        self.assertEqual(audit['records_preserved'],6)
        self.assertEqual(audit['base_blob'], 'b23879150024b3b667679ff4dd7faae1e37cfc07')
        self.assertIn(REPLACEMENT,result)

    def test_actual_source_pin_required(self):
        with self.assertRaisesRegex(ValueError,'Git blob'):rewrite(self.source+' unexpected mutation')
    def test_source_drift_closed(self):
        with self.assertRaisesRegex(ValueError,'Git blob'):
            rewrite(self.source.replace('NASA S67-19766','NASA S67-00000',1),expected_blob=self.pin)
    def test_duplicate_or_missing_original(self):
        candidate,_=self.use(self.source)
        with self.assertRaisesRegex(ValueError,'label missing'):self.use(candidate)
        with self.assertRaisesRegex(ValueError,'label missing'):self.use(self.source.replace(ORIGINAL,'',1))
    def test_missing_provenance_fails(self):
        mutated=self.source.replace('Catalog ID not established on linked NASA page','Catalog ID verified',1)
        with self.assertRaisesRegex(ValueError,'uncertainty'):self.use(mutated)
    def test_source_destination_drift_fails(self):
        mutated=self.source.replace('https://www.nasa.gov/image-detail/apollo-1-crew-honored/','https://example.test/checkout',1)
        with self.assertRaisesRegex(ValueError,'NASA image source'):self.use(mutated)
    def test_six_record_gate(self):
        mutated=self.source.replace('data-fvx-r174-media-custody="06"','data-fvx-damaged="06"',1)
        with self.assertRaisesRegex(ValueError,'six-source'):self.use(mutated)
    def test_no_new_commerce_or_source_links(self):
        result,audit=self.use(self.source)
        self.assertEqual(audit['scripts_added'],0)
        self.assertNotIn('<form',result.lower())
        self.assertNotIn('utm_campaign',REPLACEMENT)
        self.assertFalse(audit['media_rights_cleared'])
if __name__=='__main__':unittest.main()
