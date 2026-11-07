"""Explicit negative tests for same-ID source definitions in separate Claude clusters."""
import importlib.util
import json
from pathlib import Path
import unittest

P=Path(__file__).resolve().parent/'test_r196_fragment_source_custody_gate.py'
spec=importlib.util.spec_from_file_location('r196_fixtures',P)
fixtures=importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixtures)
g=fixtures.g

class CrossClusterTests(unittest.TestCase):
    def setUp(self):
        self.d,self.objects,self.pins,self.expected=fixtures.fixture()

    def run_shared(self, conflict, field='notes'):
        docket=json.loads(self.d)
        for group in ('hist-field','hist-food'):
            old_pair=list(self.pins[group])
            for vi,ver in enumerate(('frozen','observed')):
                entry=json.loads(self.objects[old_pair[vi]])
                entry['sources'][1]['id']='shared-id-for-review'
                if group=='hist-food' and conflict:
                    entry['sources'][1][field]='Different cluster interpretation'
                raw=json.dumps(entry,sort_keys=True).encode()
                new=g.oid(raw);self.objects[new]=raw
                old_pair[vi]=new;docket['source_fragments'][group][ver]=new
            self.pins[group]=tuple(old_pair)
        raw=json.dumps(docket,sort_keys=True).encode()
        return g.inspect(raw,self.objects.__getitem__,docket_oid=g.oid(raw),
                         pins=self.pins,expected=self.expected)

    def test_shared_id_same_definition_not_false_conflict(self):
        r=self.run_shared(False)
        self.assertEqual(r['state'],g.HOLD)
        self.assertEqual(r['cross_cluster_conflicts'],[])

    def test_shared_id_different_notes_stays_human_pending(self):
        r=self.run_shared(True)
        self.assertEqual(r['state'],g.HOLD)
        self.assertEqual(len(r['cross_cluster_conflicts']),1)
        x=r['cross_cluster_conflicts'][0]
        self.assertEqual(x['source_id'],'shared-id-for-review')
        self.assertEqual(x['differing_fields'],['notes'])
        self.assertTrue(x['automatic_merge_prohibited'])
        self.assertEqual(x['human_review'],'PENDING')

    def test_shared_id_different_supports_cannot_be_approved(self):
        r=self.run_shared(True,'supports')
        self.assertEqual(r['cross_cluster_conflicts'][0]['differing_fields'],['supports'])
        self.assertFalse(r['source_claims_human_approved'])
        self.assertEqual(r['source_aliases_approved'],0)
        self.assertIsNone(r['realized_net_revenue'])

if __name__=='__main__':unittest.main()
