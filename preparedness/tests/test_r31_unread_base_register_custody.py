"""R31: 14 frozen, unread Issue #136 source listings stay unread and unapproved.

No modifications to original register, source evidence, metadata or CMS.
"""
from __future__ import annotations
from pathlib import Path
import copy
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import claim_corpus_release_gate as gate

ORIGINAL = {
    'nchfp-jerky': 'Listed in Issue #136; for article 11.',
    'nchfp-pressure-ground-meat': 'Listed in Issue #136; for article 10.',
    'fsis-power-failure': 'Listed in Issue #136; for article 9.',
    'fsis-emergency-foods': 'Listed in Issue #136; for article 8.',
    'usfa-fire-escape': 'Listed in Issue #136; for article 13.',
    'cdc-co-generators': 'Listed in Issue #136; for article 12.',
    'cdc-hygiene-emergency': 'Listed in Issue #136; for article 18.',
    'nws-nwr': 'Listed in Issue #136; for article 19.',
    'ready-are-you-ready': 'Listed in Issue #136; for articles 1 and 15.',
    'nps-lewis-clark-salt': 'Listed in Issue #136; for article 23.',
    'nps-salt-works': 'Listed in Issue #136; for article 23.',
    'loc-pioneer-diaries': 'Listed in Issue #136; for articles 24 and 34.',
    'loc-prairie-traveler': 'Listed in Issue #136; for articles 24 and 34.',
    'nchfp-historical-origins': 'Listed in Issue #136; for article 35.',
}

def row(sid, note):
    return {'row_key':'base:20:'+sid,'origin':'base','source_id':sid,
            'url':'https://example.org/documentary-only-test','verified_on':None,
            'human_link_check':False,'supports':None,'reading_limits':note}

def check_one(record):
    return gate.verify_physical_source_custody(
        [record],expected_count=1,expected_repeated_url_groups=0,
        expected_distinct_urls=1)

class Invariants(unittest.TestCase):
    def test_exact_source_listing_inventory(self):
        self.assertEqual(gate.ORIGINAL_UNREAD_ISSUE136_REFERENCES,ORIGINAL)
        self.assertEqual(len(ORIGINAL),14)
    def test_no_implicit_machine_verification(self):
        for sid,note in ORIGINAL.items():
            with self.subTest(sid=sid):
                a=row(sid,note)
                b=copy.deepcopy(a)
                check_one(a)
                self.assertEqual(a,b)
                self.assertIsNone(a['verified_on'])
                self.assertIs(a['human_link_check'],False)
    def test_literal_note_not_published_as_human_check(self):
        report=check_one(row('nchfp-jerky',ORIGINAL['nchfp-jerky']))
        self.assertEqual(report['unread_base_placeholders_NOT_VERIFIED'],1)
        self.assertNotIn('human_check_approved',report)
        self.assertNotIn('may_publish',report)
    def test_unread_base_generic_not_yet_read_is_still_accepted(self):
        r=row('base-unread-other','not yet read; original evidence remains unverified')
        self.assertEqual(check_one(r)['unread_base_placeholders_NOT_VERIFIED'],1)
    def test_missing_notes_are_not_acceptable(self):
        with self.assertRaises(ValueError):
            check_one(row('nchfp-jerky',''))

class AllFourteen(unittest.TestCase):
    pass

def make_case(sid, note, name):
    def t(self):
        candidate=row(sid,note)
        if name == 'accept':
            result=check_one(candidate)
            self.assertEqual(result['unread_base_placeholders_NOT_VERIFIED'],1)
        else:
            if name == 'alter_note':
                candidate['reading_limits']='Studied completely; qualified safe'
            elif name == 'verified_date':
                candidate['verified_on']='2026-10-31'
            elif name == 'human_link':
                candidate['human_link_check']=True
            elif name == 'wrong_origin':
                candidate['origin']='food'
                candidate['row_key']='food:20:'+sid
            elif name == 'wrong_source_id':
                candidate['source_id']=sid+'-fake'
                candidate['row_key']='base:20:'+sid+'-fake'
            else:
                raise AssertionError('unknown case')
            with self.assertRaisesRegex(ValueError,'unverified placeholder'):
                check_one(candidate)
    return t

for index,(sid,note) in enumerate(ORIGINAL.items()):
    for scenario in ('accept','alter_note','verified_date','human_link',
                     'wrong_origin','wrong_source_id'):
        setattr(AllFourteen,'test_%02d_%s'%(index,scenario),
                make_case(sid,note,scenario))

class NativeInventory(unittest.TestCase):
    def test_all_224_original_rows_if_trusted_checkout_available(self):
        root=Path(__file__).resolve().parents[1]
        if not (root/'sources'/'register.json').is_file():
            self.skipTest('requires trusted full checkout; never fabricate original corpus')
        import source_review_queue
        physical=source_review_queue.source_rows(root)
        self.assertEqual(len(physical),224)
        result=gate.verify_physical_source_custody(physical)
        self.assertEqual(result['unread_base_placeholders_NOT_VERIFIED'],15)
        self.assertEqual(result['literal_urls'],186)
        self.assertEqual(result['repeated_url_groups_UNRESOLVED'],30)

class BooleanSourceClearanceSentinel(unittest.TestCase):
    def test_false_is_literal_boolean_not_numeric_zero(self):
        import json
        from private_release_preflight import verify_hold_json
        receipt={'release_state':'HOLD','may_publish':False,
                 'independent_human_source_checks_verified':False}
        verified=verify_hold_json(json.dumps(receipt).encode('utf-8'))
        self.assertIs(verified['independent_human_source_checks_verified'],False)
    def test_numeric_zero_cannot_impersonate_boolean_false(self):
        import json
        from private_release_preflight import PreflightHold, verify_hold_json
        receipt={'release_state':'HOLD','may_publish':False,
                 'independent_human_source_checks_verified':0}
        with self.assertRaisesRegex(PreflightHold,'falsely asserted review approval'):
            verify_hold_json(json.dumps(receipt).encode('utf-8'))

if __name__ == '__main__':
    unittest.main()
