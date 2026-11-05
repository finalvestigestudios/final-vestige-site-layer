"""Synthetic, adversarial review queue tests; NEVER a substitute for actual R133 custody."""
from __future__ import annotations
from copy import deepcopy
import importlib.util
from pathlib import Path
import sys
import unittest

TOOL = Path(__file__).resolve().parents[1] / 'tools' / 'r135_review_queue.py'
spec = importlib.util.spec_from_file_location('r135_review_queue', TOOL)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
review_queue, ReviewHold, fingerprint = module.review_queue, module.ReviewHold, module.fingerprint

SLUGS = [
 'emergency-hygiene-sanitation','family-communication-plan','fire-making-across-time',
 'food-safety-power-outage','go-bags','history-of-food-preservation','home-fire-escape-plan',
 'homemade-water-filters','household-emergency-plan','lewis-and-clark-salt-works',
 'making-water-safer','medication-and-devices','navigation-before-gps',
 'outage-heat-cold-generators','pantry-rotation','pemmican-and-dried-meats',
 'pickling-fermentation-old-recipes','pioneer-supply-chains-failed','pioneer-travel-rations',
 'preparedness-real-households','pressure-canning-low-acid','rain-barrels-and-cisterns',
 'root-cellars-cool-storage','safe-jerky-dehydration','salt-beef-salt-pork-age-of-sail',
 'sanitation-before-germ-theory','shelter-or-evacuate','ships-biscuit-and-hardtack',
 'smokehouses-salting-curing','three-day-kit','two-week-water-storage',
 'warnings-radios-offline-maps','water-advisories-explained','water-math',
 'water-purification-through-history']


def fixture():
    out={'purpose':'HUMAN_REVIEW_PACKET_NOT_SAFETY_APPROVAL','status':'HOLD',
         'qd_pass':False,'may_publish':False,'merchant_offer_verified':False,
         'candidate_parent':'immutable-R132-head','article_count':len(SLUGS),
         'citation_occurrences':len(SLUGS),'articles':[]}
    for i,slug in enumerate(SLUGS):
        b={'citation_id':'s','source_origin':'start','source_url':'https://example.org/s',
           'author_reading_scope':'exact author context','source_supports':'limited claim',
           'source_verified_on':'2026-11-03','human_link_check':False,
           'author_shadows_different_base_source':False,
           'shared_source_group':i%32+1}
        block={'block_index':1,'excerpt':'Medication guidance',
               'review_keyword_families':['medicine-medical-dependency'],
               'citation_occurrences':1,'attention_no_inline_citation':False,
               'bindings':[b]}
        out['articles'].append({'slug':slug,'origin':'start','publication_state':'draft',
           'safety_review_state_historical_only':'pending','citation_occurrences':1,
           'blocks_for_human_review':[block]})
    return out


def run(p): return review_queue(p,expected_articles=35,expected_citations=35,expected_groups=32)


class TestAll35(unittest.TestCase):
    pass


def make_one(slug):
    def test(self):
        r=run(fixture())
        self.assertEqual(r['status'],module.HOLD)
        self.assertTrue(any(t['slug']==slug for t in r['safety_passage_tasks']))
        self.assertFalse(r['may_publish'])
    return test

for slug in SLUGS:
    setattr(TestAll35,'test_'+slug.replace('-','_'),make_one(slug))


class TestAdversarial(unittest.TestCase):
    def test_exact_roster(self): self.assertEqual(len(SLUGS),35)
    def test_unique_roster(self): self.assertEqual(len(set(SLUGS)),35)
    def test_deterministic_output(self): self.assertEqual(run(fixture()),run(fixture()))
    def test_crosswalk_groups_all_exposed(self): self.assertEqual(len(run(fixture())['source_group_tasks']),32)
    def test_all_human_pending(self): self.assertTrue(all(x['decision']=='UNREVIEWED_HUMAN_REQUIRED' for x in run(fixture())['source_group_tasks']))
    def test_no_merchant_approval(self): self.assertFalse(run(fixture())['merchant_offer_verified'])
    def test_no_medical_approval(self): self.assertFalse(run(fixture())['medical_safety_verified'])
    def test_no_qd_pass(self): self.assertFalse(run(fixture())['qd_pass'])
    def test_missing_true_human_checks(self): self.assertEqual(run(fixture())['summary']['citation_bindings_without_true_human_link_check'],35)
    def test_cited_authors_preserved(self): self.assertEqual(run(fixture())['source_group_tasks'][0]['cited_variant_identities_only'][0][0],'start')
    def test_stable_fingerprint(self): self.assertEqual(fingerprint({'b':2,'a':1}),fingerprint({'a':1,'b':2}))
    def test_mutating_claim_changes_witness(self):
        a=fixture(); b=fixture(); b['articles'][0]['blocks_for_human_review'][0]['excerpt']='Changed warning'
        self.assertNotEqual(run(a)['safety_passage_tasks'][0]['task_id'],run(b)['safety_passage_tasks'][0]['task_id'])
    def bad(self, fn):
        p=fixture(); fn(p)
        with self.assertRaises(ReviewHold):run(p)
    def test_upstream_pass_forbidden(self): self.bad(lambda p:p.update(status='PASS'))
    def test_upstream_qd_forbidden(self): self.bad(lambda p:p.update(qd_pass=True))
    def test_upstream_publish_forbidden(self): self.bad(lambda p:p.update(may_publish=True))
    def test_upstream_merchant_forbidden(self): self.bad(lambda p:p.update(merchant_offer_verified=True))
    def test_upstream_count_forgery(self): self.bad(lambda p:p.update(citation_occurrences=2000))
    def test_article_missing(self): self.bad(lambda p:p['articles'].pop())
    def test_slug_duplicate(self): self.bad(lambda p:p['articles'][1].update(slug=p['articles'][0]['slug']))
    def test_article_published(self): self.bad(lambda p:p['articles'][0].update(publication_state='publish'))
    def test_article_unknown_safety(self): self.bad(lambda p:p['articles'][0].update(safety_review_state_historical_only='safe'))
    def test_missing_citation_occurrence(self): self.bad(lambda p:p['articles'][0].update(citation_occurrences=2))
    def test_missing_blocks(self): self.bad(lambda p:p['articles'][0].pop('blocks_for_human_review'))
    def test_bad_block_count(self): self.bad(lambda p:p['articles'][0]['blocks_for_human_review'][0].update(citation_occurrences=2))
    def test_duplicate_block_index(self):
        def mutate(p):p['articles'][0]['blocks_for_human_review'].append(deepcopy(p['articles'][0]['blocks_for_human_review'][0]))
        self.bad(mutate)
    def test_unknown_keyword(self):self.bad(lambda p:p['articles'][0]['blocks_for_human_review'][0].update(review_keyword_families=['magic']))
    def test_duplicate_keyword(self):self.bad(lambda p:p['articles'][0]['blocks_for_human_review'][0].update(review_keyword_families=['water-treatment','water-treatment']))
    def test_fake_no_citation(self):self.bad(lambda p:p['articles'][0]['blocks_for_human_review'][0].update(attention_no_inline_citation=True))
    def test_missing_source_url(self):self.bad(lambda p:p['articles'][0]['blocks_for_human_review'][0]['bindings'][0].update(source_url=''))
    def test_missing_author_reading_scope(self):self.bad(lambda p:p['articles'][0]['blocks_for_human_review'][0]['bindings'][0].update(author_reading_scope=' '))
    def test_invalid_shared_group(self):self.bad(lambda p:p['articles'][0]['blocks_for_human_review'][0]['bindings'][0].update(shared_source_group=99))
    def test_source_group_missing(self):
        def mutate(p):
            for article in p['articles']:
                for b in article['blocks_for_human_review'][0]['bindings']:
                    if b['shared_source_group'] == 1: b['shared_source_group'] = None
        self.bad(mutate)
    def test_missing_risk_still_cited(self):
        p=fixture(); p['articles'][0]['blocks_for_human_review'][0]['review_keyword_families']=[]
        self.assertEqual(len(run(p)['safety_passage_tasks']),34)
    def test_historical_approved_not_new_approval(self):
        p=fixture();p['articles'][0]['safety_review_state_historical_only']='approved'
        self.assertFalse(run(p)['medical_safety_verified'])
    def test_historical_not_required_not_new_approval(self):
        p=fixture();p['articles'][0]['safety_review_state_historical_only']='not-required'
        self.assertFalse(run(p)['qd_pass'])
    def test_source_id_collision_kept_separate(self):
        p=fixture();e=p['articles'][1]['blocks_for_human_review'][0]['bindings'][0]
        e['source_origin']='hist-food';e['source_url']='https://example.org/s/'
        v=run(p)['source_group_tasks'][1]['cited_variant_identities_only']
        self.assertEqual(v[0][0],'hist-food')
    def test_unchecked_citation_flag(self):
        p=fixture();p['articles'][0]['blocks_for_human_review'][0]['bindings'][0]['human_link_check']=True
        self.assertEqual(run(p)['summary']['citation_bindings_without_true_human_link_check'],34)
    def test_uncited_keyword_is_review_task(self):
        p=fixture();a=p['articles'][0];a['blocks_for_human_review'].append({'block_index':2,'excerpt':'Check insulin storage','review_keyword_families':['medicine-medical-dependency'], 'citation_occurrences':0,'attention_no_inline_citation':True,'bindings':[]})
        o=run(p);self.assertEqual(o['summary']['risk_passages_without_inline_citations'],1)
    def test_priority_med_before_water(self):
        p=fixture();p['articles'][0]['blocks_for_human_review'][0]['review_keyword_families']=['water-treatment']
        self.assertEqual(run(p)['safety_passage_tasks'][0]['priority'],1)
    def test_missing_excerpt(self):self.bad(lambda p:p['articles'][0]['blocks_for_human_review'][0].pop('excerpt'))
    def test_too_long_excerpt(self):self.bad(lambda p:p['articles'][0]['blocks_for_human_review'][0].update(excerpt='x'*221))
    def test_nonpositive_block_number(self):self.bad(lambda p:p['articles'][0]['blocks_for_human_review'][0].update(block_index=0))
    def test_suspicious_nonurl_source(self):self.bad(lambda p:p['articles'][0]['blocks_for_human_review'][0]['bindings'][0].update(source_url='file://private'))

if __name__=='__main__':unittest.main()
