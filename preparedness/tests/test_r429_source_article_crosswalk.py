"""R429 source/article 35/203/17 escrow; synthetic data only, never QD PASS."""
from __future__ import annotations
import copy
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / 'tools' / 'r429_source_article_crosswalk.py'
_spec = spec_from_file_location('r429_source_article_crosswalk', FILE)
g = module_from_spec(_spec)
_spec.loader.exec_module(g)
_source_test = ROOT / 'tests' / 'test_r410_full_slate_export_gate.py'
_s = spec_from_file_location('r410_fixture_for_r429', _source_test)
f = module_from_spec(_s)
_s.loader.exec_module(f)


def fixture():
    original, manifest, _exports = f.fixture()
    return original, manifest


def review(original=None, manifest=None, *, raw_manifest=None, test_only=True, raw_original=None):
    if original is None:
        original, manifest = fixture()
    if raw_original is None:
        raw_original = json.dumps(original, sort_keys=True).encode('utf-8')
    if raw_manifest is None:
        raw_manifest = json.dumps(manifest, sort_keys=True).encode('utf-8')
    return g.crosswalk_audit(original, manifest, raw_original=raw_original,
                             raw_manifest=raw_manifest, test_only=test_only)


class Baseline(unittest.TestCase):
    def test_full_35_article_203_source_17_exact_url_graph(self):
        out = review()
        self.assertTrue(out['source_reference_structure_ok'], out['errors'])
        self.assertEqual(len(out['article_source_crosswalk']), 35)
        self.assertEqual(out['source_ids_in_original'], 203)
        self.assertEqual(out['source_ids_referenced_by_articles'], 35)
        self.assertEqual(len(out['exact_shared_url_review_groups']), 17)
        self.assertEqual(out['source_ids_unreferenced_by_this_manifest'], 168)
    def test_no_revenue_qd_approval_or_publish_even_if_structural(self):
        out = review()
        for name in ('eligible', 'publication_approved', 'qualified_safety_approved',
                     'paid_activation_approved', 'merchant_offer_verified'):
            self.assertIs(out[name], False)
        self.assertEqual(out['release_state'], 'DRAFT_HARD_HOLD')
        self.assertIsNone(out['verified_paid_orders'])
        self.assertIsNone(out['net_revenue_per_1000_qualified_humans'])
    def test_source_overlap_preserved_without_identity_collapse(self):
        out = review()
        group = out['exact_shared_url_review_groups'][0]
        self.assertEqual(len(group['distinct_source_ids']), 2)
        self.assertIs(group['merged'], False)
        self.assertEqual(group['decision'], 'HUMAN_REVIEW_REQUIRED')
    def test_two_channels_unverified_even_with_valid_crosswalk(self):
        out = review()
        self.assertEqual(out['paired_exports'], 'NOT_TESTED_BY_R429')
        self.assertEqual(out['reading_depth'], 'NOT_TESTED_BY_R429')
    def test_reordering_manifest_rows_does_not_change_crosswalk_digest(self):
        a, m = fixture(); first = review(a, m)
        m['articles'].reverse(); second = review(a, m)
        # Canonical crosswalk sorts article slugs; digest still binds manifest bytes,
        # so a reordered manifest is a new receipt but equivalent article link graph.
        self.assertEqual(first['article_source_crosswalk'], second['article_source_crosswalk'])
        self.assertNotEqual(first['review_crosswalk_sha256'], second['review_crosswalk_sha256'])
    def test_manifest_source_order_is_preserved(self):
        a, m = fixture();m['articles'][0]['sources']=['src-0','src-1']
        out=review(a,m)
        self.assertTrue(out['source_reference_structure_ok'], out['errors'])
        self.assertEqual(out['article_source_crosswalk'][0]['source_ids_in_original_order'],['src-0','src-1'])
    def test_overlap_maps_affected_article_slugs(self):
        a,m=fixture();m['articles'][1]['sources']=['src-1']
        out=review(a,m)
        matches=[x for x in out['exact_shared_url_review_groups'] if x['distinct_source_ids']==['src-0','src-1']]
        self.assertEqual(len(matches),1)
        self.assertEqual(matches[0]['affected_article_slugs'],['guide-0','guide-1'])
    def test_same_source_in_multiple_articles_is_not_duplicate_source_id(self):
        a,m=fixture();m['articles'][1]['sources']=['src-0']
        out=review(a,m)
        self.assertTrue(out['source_reference_structure_ok'],out['errors'])
        self.assertEqual(out['source_ids_referenced_by_articles'],34)
    def test_strict_native_pin_rejects_fake_original(self):
        out=review(test_only=False)
        self.assertFalse(out['source_reference_structure_ok'])
        self.assertIn('R429_ORIGINAL_R397_GRAPH_OR_GIT_PIN_FAILED',out['errors'])
    def test_missing_raw_manifest_rejected(self):
        a,m=fixture();out=g.crosswalk_audit(a,m,test_only=True)
        self.assertIn('R429_MANIFEST_RAW_BYTES_MISSING',out['errors'])
    def test_raw_manifest_different_from_memory_rejected(self):
        a,m=fixture();raw=json.dumps(m).encode();m['articles'][0]['sources']=['src-33']
        out=review(a,m,raw_manifest=raw)
        self.assertIn('R429_MANIFEST_OBJECT_NOT_MATCHING_READ_BYTES',out['errors'])
    def test_duplicate_json_keys_fail_closed(self):
        a,m=fixture();out=review(a,m,raw_manifest=b'{"schema":1,"schema":2}')
        self.assertIn('R429_MANIFEST_JSON_READ_OR_DUPLICATE_KEY_FAILED',out['errors'])
    def test_nonstandard_json_constant_fail_closed(self):
        a,m=fixture();out=review(a,m,raw_manifest=b'{"schema":NaN}')
        self.assertIn('R429_MANIFEST_JSON_READ_OR_DUPLICATE_KEY_FAILED',out['errors'])
    def test_cli_no_evidence_always_exit_2(self):
        p=subprocess.run([sys.executable,str(FILE),'/missing/r397.json','/missing/manifest.json'],
                         capture_output=True,text=True,timeout=12)
        self.assertEqual(p.returncode,2)
        self.assertIs(json.loads(p.stdout)['eligible'],False)
    def test_invalid_top_level_types_hard_hold(self):
        for a,m in [(None,{}),([],{}),({},None),('not object',{})]:
            with self.subTest(a=type(a).__name__,m=type(m).__name__):
                out=g.crosswalk_audit(a,m,test_only=True)
                self.assertFalse(out['source_reference_structure_ok'])


# Each mutation is an independent adversarial test against a fresh 35/203/280/17
# synthetic docket + manifest. Never modifies real author branches or sources.
ATTACKS=[]
for key,val in [('schema',2),('schema',True),('release_state','PASS'),
                ('approved',True),('approved',None),('merchant_offer_verified',True)]:
    ATTACKS.append(('manifest_'+key+'_'+str(val),
        lambda a,m,k=key,v=val:m.__setitem__(k,v)))
for key in ('schema','provenance','issue','release_state','publication_approved',
            'qualified_safety_approved','merchant_offer_verified','automatic_variant_selection'):
    ATTACKS.append(('original_'+key,lambda a,m,k=key:a.__setitem__(k,'FORGED_APPROVAL')))
ATTACKS += [
 ('manifest_missing_article', lambda a,m:m['articles'].pop()),
 ('manifest_extra_article', lambda a,m:m['articles'].append(copy.deepcopy(m['articles'][0]))),
 ('manifest_duplicate_slug', lambda a,m:m['articles'][1].__setitem__('slug','guide-0')),
 ('manifest_foreign_slug', lambda a,m:m['articles'][0].__setitem__('slug','outsider')),
 ('manifest_bad_slug', lambda a,m:m['articles'][0].__setitem__('slug','../../secret')),
 ('manifest_unhashable_slug', lambda a,m:m['articles'][0].__setitem__('slug',[])),
 ('manifest_wrong_route', lambda a,m:m['articles'][0].__setitem__('canonical_path','/different/guide-0/')),
 ('manifest_query_route', lambda a,m:m['articles'][0].__setitem__('canonical_path','/preparedness/guide-0/?src=x')),
 ('manifest_missing_route', lambda a,m:m['articles'][0].pop('canonical_path')),
 ('manifest_approved_article', lambda a,m:m['articles'][0].__setitem__('safety_approved',True)),
 ('manifest_source_list_none', lambda a,m:m['articles'][0].__setitem__('sources',None)),
 ('manifest_source_list_text', lambda a,m:m['articles'][0].__setitem__('sources','src-0')),
 ('manifest_source_list_empty', lambda a,m:m['articles'][0].__setitem__('sources',[])),
 ('manifest_source_list_unknown', lambda a,m:m['articles'][0].__setitem__('sources',['unknown-id'])),
 ('manifest_source_list_duplicate', lambda a,m:m['articles'][0].__setitem__('sources',['src-0','src-0'])),
 ('manifest_source_list_case_change', lambda a,m:m['articles'][0].__setitem__('sources',['SRC-0'])),
 ('manifest_source_list_unhashable', lambda a,m:m['articles'][0].__setitem__('sources',[[]])),
 ('manifest_source_list_bad_chars', lambda a,m:m['articles'][0].__setitem__('sources',['src-0\n'])) ,
 ('manifest_ghost_root_field',lambda a,m:m.__setitem__('allow_publish',False)),
 ('manifest_articles_not_array',lambda a,m:m.__setitem__('articles',None)),
 ('original_article_removed',lambda a,m:a['original_articles'].pop()),
 ('original_article_duplicate',lambda a,m:a['original_articles'][0].__setitem__('slug','guide-1')),
 ('original_article_bad_slug',lambda a,m:a['original_articles'][0].__setitem__('slug','../guide')),
 ('original_source_removed',lambda a,m:a['all_original_source_id_crosswalk'].pop()),
 ('original_duplicate_source_id',lambda a,m:a['all_original_source_id_crosswalk'][0].__setitem__('source_id','src-1')),
 ('original_invalid_source_id',lambda a,m:a['all_original_source_id_crosswalk'][0].__setitem__('source_id','s1 s2')),
 ('original_missing_source_url',lambda a,m:a['all_original_source_id_crosswalk'][0]['variants'][0].pop('url')),
 ('original_source_http',lambda a,m:a['all_original_source_id_crosswalk'][0]['variants'][0].__setitem__('url','http://bad.invalid/')),
 ('original_source_js_url',lambda a,m:a['all_original_source_id_crosswalk'][0]['variants'][0].__setitem__('url','javascript:alert(1)')),
 ('original_source_nontext_url',lambda a,m:a['all_original_source_id_crosswalk'][0]['variants'][0].__setitem__('url',[])),
 ('original_source_variant_drift',lambda a,m:a['all_original_source_id_crosswalk'][0]['variants'][1].__setitem__('url','https://www.ready.gov/other')),
 ('original_source_variant_removed',lambda a,m:a['all_original_source_id_crosswalk'][0]['variants'].clear()),
 ('original_source_branch_unknown',lambda a,m:a['all_original_source_id_crosswalk'][0]['variants'][0].__setitem__('branch','evil/branch')),
 ('original_source_blob_wrong',lambda a,m:a['all_original_source_id_crosswalk'][0]['variants'][0].__setitem__('source_blob','abc')),
 ('original_shared_group_removed',lambda a,m:a['shared_exact_url_review_groups'].pop()),
 ('original_shared_group_added',lambda a,m:a['shared_exact_url_review_groups'].append(copy.deepcopy(a['shared_exact_url_review_groups'][0]))),
 ('original_shared_group_membership',lambda a,m:a['shared_exact_url_review_groups'][0]['ids'].__setitem__(0,'src-40')),
 ('original_shared_group_automerge',lambda a,m:a['shared_exact_url_review_groups'][0].__setitem__('review_required',False)),
 ('original_source_dispute_removed',lambda a,m:a['source_evidence_disputes'].pop()),
 ('original_source_dispute_promoted',lambda a,m:a['source_evidence_disputes'][0].__setitem__('decision','PASS')),
 ('original_source_selected',lambda a,m:a['source_evidence_disputes'][0].__setitem__('selected_record',{'source':'selected'})),
 ('original_fork_removed',lambda a,m:a['original_fork_disputes'].pop()),
 ('original_fork_promoted',lambda a,m:a['original_fork_disputes'][0].__setitem__('decision','PASS')),
 ('original_fork_selected',lambda a,m:a['original_fork_disputes'][0].__setitem__('selected_sha','f'*40)),
 ('original_fork_depth_exempt',lambda a,m:a['original_fork_disputes'][0].__setitem__('requires_reading_depth_review',False)),
 ('original_fork_citation_exempt',lambda a,m:a['original_fork_disputes'][0].__setitem__('requires_source_citation_review',False)),
 ('original_branch_pin_removed',lambda a,m:a['branch_pins'].pop()),
 ('original_branch_pin_duplicate',lambda a,m:a['branch_pins'][1].__setitem__('branch','branch-0')),
 ('original_branch_pin_corrupt',lambda a,m:a['branch_pins'][0].__setitem__('sha','nope')),
 ('original_expected_count_changed',lambda a,m:a['expected'].__setitem__('original_distinct_source_ids',202)),
 ('original_observed_count_changed',lambda a,m:a['observed'].__setitem__('source_record_occurrences',279)),
]


def attack_case(label,mutator):
    def case(self):
        a,m=fixture();mutator(a,m)
        out=review(a,m)
        self.assertFalse(out['source_reference_structure_ok'],label+': '+str(out['errors']))
        self.assertFalse(out['eligible'])
        self.assertFalse(out['publication_approved'])
    case.__name__='test_attack_'+label
    return case


class AttackMatrix(unittest.TestCase):
    pass


for idx,(label,mutation) in enumerate(ATTACKS):
    setattr(AttackMatrix,'test_attack_'+str(idx).zfill(2)+'_'+label,attack_case(label,mutation))
