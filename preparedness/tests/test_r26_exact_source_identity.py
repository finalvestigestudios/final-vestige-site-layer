"""R26 adversarial tests: full original source record vs renderer, never safety QA."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import citation_fallback_review_gate as gate
from test_citation_fallback_review_gate import Library, SMALL


def audit(lib=None):
    return gate.audit(Library() if lib is None else lib, expected=SMALL)


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


class EvidenceTests(unittest.TestCase):
    def test_complete_sources(self):
        for r in audit()['review_queue']:
            s = r['original_source_record_as_selected']
            for key, bound in (('id','source_id'),('_origin','source_origin'),
                               ('url','source_url'),('supports','source_supports_as_recorded'),
                               ('notes','source_notes_as_recorded')):
                self.assertEqual(s.get(key),r[bound])
    def test_content_addressed_source(self):
        for r in audit()['review_queue']:
            self.assertEqual(r['original_source_record_sha256'],
                             hashlib.sha256(canonical(r['original_source_record_as_selected'])).hexdigest())
    def test_source_use_digest(self):
        lib=Library()
        for r in audit(lib)['review_queue']:
            self.assertEqual(r['frozen_source_use_sha256'],
                hashlib.sha256(lib.articles[r['slug']]['source_use'][r['source_id']].encode()).hexdigest())
    def test_html_digest(self):
        lib=Library()
        for r in audit(lib)['review_queue']:
            self.assertEqual(r['frozen_article_html_sha256'],
                hashlib.sha256(lib.articles[r['slug']]['_body'].encode()).hexdigest())
    def test_codepoint_offsets_and_context_count(self):
        lib=Library()
        for r in audit(lib)['review_queue']:
            self.assertEqual(r['citation_occurrences'],len(r['citation_token_codepoint_offsets']))
            self.assertEqual(r['citation_occurrences'],len(r['all_citation_contexts_for_human_claim_review']))
            for n in r['citation_token_codepoint_offsets']:
                self.assertTrue(lib.articles[r['slug']]['_body'][n:].startswith('{{cite:'+r['source_id']+'}}'))
    def test_unicode_offsets_are_not_bytes(self):
        lib=Library()
        lib.articles['plan']['_body']='📜 ∆ — '+lib.articles['plan']['_body']
        for r in audit(lib)['review_queue']:
            if r['slug']=='plan':
                for n in r['citation_token_codepoint_offsets']:
                    self.assertTrue(lib.articles['plan']['_body'][n:].startswith('{{cite:'+r['source_id']+'}}'))
    def test_extra_original_metadata_preserved(self):
        lib=Library()
        lib.source_variants['a'][0].update(title='Original scan',publisher='Archive',
            caveats=['only catalogue'],audit={'page':'not examined'})
        s=next(r['original_source_record_as_selected'] for r in audit(lib)['review_queue']
               if r['slug']=='plan' and r['source_id']=='a')
        self.assertEqual(s['caveats'],['only catalogue'])
        self.assertEqual(s['audit']['page'],'not examined')
    def test_hold_status_always_false(self):
        r=audit()
        self.assertEqual(r['release_state'],'HOLD')
        for key in ('may_publish','independent_QD_approval','qualified_safety_clearance',
                    'human_source_reviews_completed','source_claim_accuracy_verified'):
            self.assertIs(r[key],False)
    def test_packet_digest_covers_original_row(self):
        r=audit()
        digest=r.pop('fingerprint_sha256')
        self.assertEqual(digest,hashlib.sha256(canonical(r)).hexdigest())
        r['review_queue'][0]['original_source_record_as_selected']['url']='https://evil.example/'
        self.assertNotEqual(digest,hashlib.sha256(canonical(r)).hexdigest())
    def test_fallback_not_silent(self):
        r=next(x for x in audit()['review_queue'] if x['slug']=='plan' and x['source_id']=='a')
        self.assertTrue(r['base_fallback_requires_human_scope_review'])
        self.assertEqual(r['source_origin'],'base')
    def test_own_scope_selected(self):
        r=next(x for x in audit()['review_queue'] if x['source_id']=='shared')
        self.assertEqual(r['source_origin'],'start')
        self.assertEqual(r['original_source_record_as_selected']['notes'],'Do not infer A/B.')
    def test_source_variant_id_disagreement_fails(self):
        lib=Library()
        lib.source_variants['a'][0]['id']='wrong'
        with self.assertRaisesRegex(gate.ReviewHold,'source variant ID'):
            audit(lib)


class RendererSubstitutionTests(unittest.TestCase):
    pass

# Every candidate retains _origin='base': the R25 origin-only check accepted it.
MUTATIONS=(
('id','different'),('id',None),('url','https://other.example/'),('url','http://other.example/'),
('supports','opposite'),('supports',''),('supports',None),('supports',[]),('supports',1),
('supports',True),('notes','forged'),('notes',''),('notes',None),('notes',{}),('notes',False),
('verified_on','2026-10-30'),('verified_on','2026-10-31'),('verified_on',None),
('verified_on','unknown'),('title','Different title'),('publisher','Other publisher'),
('kind','not extension'),('human_link_check',True),('human_link_check',False),
('reviewed','2026-10-31'),('published','1900-01-01'),('updated','2026-10-31'),
('rights','public domain asserted'),('archive','scan unavailable'),('scope','different section'),
('source_use','unverified claim'),('correction',{'state':'approved'}),
('redirect','https://evil.example/'),('data',['contradicted']),('verified',True),
('verified',1),('factual_claims_safe',True),('independent_QD_approval',True),
('may_publish',True),('publisher',17),('publisher',None),('license','CC0'),
('license',{'name':'unverified'}),('source_hash','f'*40),('_reviewer','self-approved'),
('_publisher_approval','yes'),('test_flag',{'deep':{'could_be':'forged'}}))


def renderer_case(key,value):
    def test(self):
        lib=Library()
        real=lib.source_for
        forged=copy.deepcopy(lib.source_variants['a'][0])
        forged[key]=copy.deepcopy(value)
        lib.source_for=lambda meta,sid: forged if sid=='a' else real(meta,sid)
        with self.assertRaisesRegex(gate.ReviewHold,'source identity or reading scope'):
            audit(lib)
    return test
for i,(key,value) in enumerate(MUTATIONS):
    setattr(RendererSubstitutionTests,f'test_same_origin_{i:02d}_{key}',renderer_case(key,value))


class ImpossibleDateTests(unittest.TestCase):
    pass
INVALID_DATES=('2026-00-05','2026-13-05','2026-02-29','2026-02-30','2026-04-31',
    '1900-02-29','2026-11-31','2026-06-31','2026-09-31','2026-10-32',
    '0000-01-01','2026-12-00','2026-01-32','2026-02-31','2026-11-00')


def invalid_date_case(value):
    def test(self):
        lib=Library()
        lib.source_variants['a'][0]['verified_on']=value
        with self.assertRaises(gate.ReviewHold):
            audit(lib)
    return test
for i,value in enumerate(INVALID_DATES):
    setattr(ImpossibleDateTests,f'test_impossible_{i:02d}',invalid_date_case(value))

if __name__=='__main__':
    unittest.main()
