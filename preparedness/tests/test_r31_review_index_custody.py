"""R31 synthetic-only mutation suite. No external links or WordPress writes."""
from __future__ import annotations
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import citation_fallback_review_gate as r25
import citation_review_index_gate as gate
from test_citation_fallback_review_gate import Library, SMALL

def packet():
    return r25.audit(Library(), expected=SMALL)

def resign(obj):
    obj['fingerprint_sha256'] = gate.digest({k: v for k,v in obj.items()
                                             if k != 'fingerprint_sha256'})
    return obj

def rows():
    return packet()['review_queue']

class Acceptance(unittest.TestCase):
    def test_packet_from_original_gate_is_indexed(self):
        x = gate.build_index(packet(), expected=SMALL)
        self.assertEqual(len(x['article_review_cards']), 2)
        self.assertEqual(sum(c['citations'] for c in x['article_review_cards']), 4)
        self.assertEqual(sum(c['relationships'] for c in x['article_review_cards']), 3)
        self.assertEqual(x['counts']['base_fallback_relationships'], 1)
    def test_repeated_citation_positions_preserved(self):
        x=gate.build_index(packet(),expected=SMALL)
        self.assertEqual(next(y for y in x['article_review_cards'] if y['slug']=='plan')['citations'],3)
    def test_not_a_source_review_or_safety_approval(self):
        x=gate.build_index(packet(),expected=SMALL)
        for k in ('may_publish','human_source_reviews_completed',
                  'independent_QD_approval','qualified_safety_clearance',
                  'source_claim_accuracy_verified'):
            self.assertIs(x[k],False)
        self.assertTrue(all(y['review_state']=='UNREVIEWED' for y in x['source_url_index']))
    def test_original_source_record_and_reading_scope_untouched(self):
        p=packet(); before=copy.deepcopy(p)
        gate.build_index(p,expected=SMALL)
        self.assertEqual(p,before)
    def test_index_carries_parent_hash_and_own_hash(self):
        p=packet(); x=gate.build_index(p,expected=SMALL)
        self.assertEqual(x['parent_R25_fingerprint_sha256'],p['fingerprint_sha256'])
        self.assertEqual(x['fingerprint_sha256'],gate.digest({k:v for k,v in x.items()
                                               if k!='fingerprint_sha256'}))
    def test_deterministic_repeatable_sort(self):
        self.assertEqual(gate.build_index(packet(),expected=SMALL),
                         gate.build_index(packet(),expected=SMALL))
    def test_two_articles_retain_separate_source_references(self):
        x=gate.build_index(packet(),expected=SMALL)
        a=next(x for x in x['source_url_index'] if x['source_url']=='https://example.org/a')
        self.assertEqual([r['slug'] for r in a['source_relationships_preserved_without_dedup']],
                         ['plan','water-planner'])
    def test_mismatched_expected_corpus_fails_closed(self):
        with self.assertRaises(gate.IndexHold):gate.build_index(packet())
    def test_non_write_contract(self):
        self.assertIn('Never writes',gate.__doc__)

MUTATIONS = {
 'not_a_dict': lambda p: 'not-a-dict',
 'invalid_schema': lambda p: p.update(schema_version=2),
 'invalid_issue': lambda p: p.update(issue=123),
 'published': lambda p: p.update(release_state='APPROVED'),
 'may_publish_true':lambda p:p.update(may_publish=True),
 'may_publish_zero':lambda p:p.update(may_publish=0),
 'wrong_machine_authority':lambda p:p.update(machine_authority='HUMAN_QD_PASS'),
 'claimed_safety':lambda p:p.update(qualified_safety_clearance=True),
 'claimed_QD':lambda p:p.update(independent_QD_approval=True),
 'claimed_human_sources':lambda p:p.update(human_source_reviews_completed=True),
 'claimed_claim_checks':lambda p:p.update(source_claim_accuracy_verified=True),
 'missing_counts':lambda p:p.pop('counts'),
 'extra_count':lambda p:p['counts'].update(extra=0),
 'wrong_count':lambda p:p['counts'].update(citations=3),
 'wrong_relationships':lambda p:p['counts'].update(relationships=4),
 'wrong_fallback_total':lambda p:p['counts'].update(base_fallback_relationships=2),
 'wrong_group_total':lambda p:p['counts'].update(shared_url_groups_unreviewed=0),
 'missing_queue':lambda p:p.pop('review_queue'),
 'missing_row':lambda p:p['review_queue'].pop(),
 'double_row':lambda p:p['review_queue'].append(copy.deepcopy(p['review_queue'][0])),
 'bad_row_type':lambda p:p['review_queue'].__setitem__(0,'not a row'),
 'bad_slug':lambda p:p['review_queue'][0].update(slug='../../publish'),
 'bad_source_id':lambda p:p['review_queue'][0].update(source_id='id}more'),
 'duplicate_identity':lambda p:p['review_queue'][1].update(slug=p['review_queue'][0]['slug'],source_id=p['review_queue'][0]['source_id']),
 'wrong_article_origin':lambda p:p['review_queue'][0].update(article_origin='alien'),
 'wrong_source_origin':lambda p:p['review_queue'][0].update(source_origin='alien'),
 'wrong_fallback':lambda p:p['review_queue'][0].update(base_fallback_requires_human_scope_review=not p['review_queue'][0]['base_fallback_requires_human_scope_review']),
 'wrong_shared':lambda p:p['review_queue'][0].update(shared_url_group_requires_human_review='pending'),
 'human_link_claimed':lambda p:p['review_queue'][0].update(human_link_checked_by_this_gate=True),
 'human_claim_claimed':lambda p:p['review_queue'][0].update(human_claim_reviewed_by_this_gate=True),
 'wrong_source_id':lambda p:p['review_queue'][0]['original_source_record_as_selected'].update(id='different'),
 'wrong_source_url':lambda p:p['review_queue'][0]['original_source_record_as_selected'].update(url='https://elsewhere.org'),
 'wrong_source_origin_metadata':lambda p:p['review_queue'][0]['original_source_record_as_selected'].update(_origin='food'),
 'wrong_source_supports':lambda p:p['review_queue'][0]['original_source_record_as_selected'].update(supports='Changed reading depth'),
 'wrong_source_notes':lambda p:p['review_queue'][0]['original_source_record_as_selected'].update(notes='fabricated'),
 'wrong_source_date':lambda p:p['review_queue'][0]['original_source_record_as_selected'].update(verified_on='2026-10-30'),
 'impossible_verified_date':lambda p:p['review_queue'][0].update(machine_verified_on='2026-02-31'),
 'wrong_source_sha':lambda p:p['review_queue'][0].update(original_source_record_sha256='0'*64),
 'wrong_scope_sha':lambda p:p['review_queue'][0].update(frozen_source_use_sha256='0'*64),
 'missing_scope':lambda p:p['review_queue'][0].update(article_source_use_as_recorded=' '),
 'wrong_body_sha':lambda p:p['review_queue'][0].update(frozen_article_html_sha256='bad'),
 'inconsistent_same_article_body_sha':lambda p:p['review_queue'][1].update(frozen_article_html_sha256='1'*64),
 'wrong_occurrence_count':lambda p:p['review_queue'][0].update(citation_occurrences=3),
 'negative_offset':lambda p:p['review_queue'][0].update(citation_token_codepoint_offsets=[-1]),
 'duplicate_offset':lambda p:p['review_queue'][0].update(citation_token_codepoint_offsets=[1,1]),
 'unsorted_offsets':lambda p:p['review_queue'][0].update(citation_token_codepoint_offsets=[100,10]),
 'nontext_context':lambda p:p['review_queue'][0].update(all_citation_contexts_for_human_claim_review=[45]),
 'no_citation_in_context':lambda p:p['review_queue'][0].update(all_citation_contexts_for_human_claim_review=['missing marker']),
 'same_offset_different_source':lambda p:p['review_queue'][1].update(citation_token_codepoint_offsets=[p['review_queue'][0]['citation_token_codepoint_offsets'][0]]),
 'source_http':lambda p:p['review_queue'][0].update(source_url='http://example.org'),
 'source_embedded_credentials':lambda p:p['review_queue'][0].update(source_url='https://admin:password@example.org/a'),
 'source_port':lambda p:p['review_queue'][0].update(source_url='https://example.org:8443/a'),
 'source_backslash':lambda p:p['review_queue'][0].update(source_url='https://example.org\\@evil.org/a'),
 'source_space':lambda p:p['review_queue'][0].update(source_url='https://example.org/a b'),
 'source_control':lambda p:p['review_queue'][0].update(source_url='https://example.org/a\n'),
 'source_unicode_hostname':lambda p:p['review_queue'][0].update(source_url='https://éxample.org/a'),
 'source_numeric_host':lambda p:p['review_queue'][0].update(source_url='https://127.0.0.1/a'),
 'source_no_tld':lambda p:p['review_queue'][0].update(source_url='https://localhost/a'),
 'source_trailing_dot':lambda p:p['review_queue'][0].update(source_url='https://example.org./a'),
 'source_upper_host':lambda p:p['review_queue'][0].update(source_url='https://EXAMPLE.org/a'),
 'source_invalid_ipv6':lambda p:p['review_queue'][0].update(source_url='https://[::1/a'),
}
class TamperMutants(unittest.TestCase): pass

def make_case(name, fn):
    def t(self):
        p=packet()
        result=fn(p)
        if result is not None:p=result
        if type(p) is dict:resign(p)
        with self.assertRaises(gate.IndexHold, msg=name):
            gate.build_index(p,expected=SMALL)
    return t
for name,fn in MUTATIONS.items():
    setattr(TamperMutants,'test_reject_'+name,make_case(name,fn))

class OriginalPacketChecksum(unittest.TestCase):
    def test_changing_packet_with_no_resign_is_rejected(self):
        p=packet();p['review_queue'][0]['source_url']='https://different.example.org/a'
        with self.assertRaisesRegex(gate.IndexHold,'fingerprint mismatch'):
            gate.build_index(p,expected=SMALL)
    def test_removing_checksum_is_rejected(self):
        p=packet();p.pop('fingerprint_sha256')
        with self.assertRaises(gate.IndexHold):gate.build_index(p,expected=SMALL)
    def test_wrong_checksum_type_is_rejected(self):
        p=packet();p['fingerprint_sha256']=False
        with self.assertRaises(gate.IndexHold):gate.build_index(p,expected=SMALL)

if __name__=='__main__':unittest.main()

class UrlSourceAuthority(unittest.TestCase):
    def test_permitted_deep_link_and_query_retained(self):
        self.assertEqual(gate.url_check('https://www.loc.gov/item/123/?sp=3#section'),'www.loc.gov')
    def test_url_is_not_rewritten_or_network_checked(self):
        src='https://nchfp.uga.edu/how/dry/recipes/jerky'
        self.assertEqual(gate.url_check(src),'nchfp.uga.edu')
    def test_block_punycode_confusables_for_human_review(self):
        # Punycode may be legitimate, but source identity requires manual
        # checking; this static gate does not pretend to validate ownership.
        self.assertEqual(gate.url_check('https://xn--e1afmkfd.xn--p1ai/a'),
                         'xn--e1afmkfd.xn--p1ai')
    def test_explicit_bad_authorities(self):
        for bad in ('http://example.org','https://a:443/a',
                    'https://admin@a.example.org/a','https://a.example.org./a',
                    'https://127.0.0.1/a','https://localhost/a',
                    'https://éxample.org/a','https://EXAMPLE.org/a',
                    'https://example.org/a b','https://example.org/a\n',
                    'https://[::1/a','https://example.org\\@evil.org/a'):
            with self.subTest(bad=bad), self.assertRaises(gate.IndexHold):
                gate.url_check(bad)
    def test_end_to_end_source_record_is_checked_not_just_row_url(self):
        p=packet(); row=p['review_queue'][0]
        url='https://admin:password@example.org/a'
        row['source_url']=url
        row['original_source_record_as_selected']['url']=url
        row['original_source_record_sha256']=gate.digest(row['original_source_record_as_selected'])
        resign(p)
        with self.assertRaisesRegex(gate.IndexHold,'ambiguous source host'):
            gate.build_index(p,expected=SMALL)
