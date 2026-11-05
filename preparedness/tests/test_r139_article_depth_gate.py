"""Synthetic adversarial tests. A trusted 35-file native checkout is still required."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CENSUS_PATH = ROOT / 'docs/r139/article_depth_census.json'
SOURCE = ROOT / 'tools/r139_article_depth_gate.py'
spec = importlib.util.spec_from_file_location('r139_article_depth_gate', SOURCE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
CENSUS = json.loads(CENSUS_PATH.read_text(encoding='utf-8'))

def sample():
    x = copy.deepcopy(CENSUS)
    obs = [dict(slug=r['slug'], observed_prose_words=r['observed_approx_prose_words'],
                citation_occurrences=r['citation_occurrences'], source_use_ids=r['source_use_ids'],
                historical_safety_state=r['historical_safety_state'], publish='draft',
                editorial='drafted') for r in x['articles']]
    return x, obs

class R139Basic(unittest.TestCase):
    def test_exact_synthetic_census_passes_only_a_hold(self):
        x, obs = sample()
        result=m.check_census(x,obs)
        self.assertEqual(result['article_count'],35)
        self.assertFalse(result['qd_pass'])
        self.assertFalse(result['may_publish'])
        self.assertFalse(result['merchant_offer_verified'])
    def test_order_has_no_semantic_effect(self):
        x, obs = sample(); obs.reverse(); x['articles'].reverse()
        self.assertEqual(m.check_census(x,obs)['citation_occurrences'],2000)
    def test_whitespace_html_is_not_prose(self):
        self.assertEqual(m.approx_words('<p>Hello <strong>world</strong> {{cite:foo}}</p>'),2)
    def test_author_scope_matches_exact_citation_id(self):
        self.assertEqual(m.inspect('test',{'slug':'test','source_use':{'source-a':'Scope'},
                         'status':{'publish':'draft','editorial':'drafted'},
                         'safety_review':{'state':'pending'}},'<p>x {{cite:source-a}}</p>')['citation_occurrences'],1)
    def test_author_scope_missing_fails(self):
        with self.assertRaises(m.DepthHold):
            m.inspect('x',{'slug':'x','source_use':{}},'{{cite:x}}')
    def test_malformed_cite_fails(self):
        with self.assertRaises(m.DepthHold):
            m.inspect('x',{'slug':'x','source_use':{}},'{{cite:bad id}}')
    def test_census_duplicate_slug_fails(self):
        x, obs=sample();x['articles'][1]['slug']=x['articles'][0]['slug']
        with self.assertRaises(m.DepthHold):m.check_census(x,obs)
    def test_extra_observed_slug_fails(self):
        x, obs=sample();obs[0]['slug']='new'
        with self.assertRaises(m.DepthHold):m.check_census(x,obs)
    def test_approved_flag_fails(self):
        x, obs=sample();x['qd_pass']=True
        with self.assertRaises(m.DepthHold):m.check_census(x,obs)
    def test_float_count_fails(self):
        x, obs=sample();obs[0]['citation_occurrences']=float(obs[0]['citation_occurrences'])
        with self.assertRaises(m.DepthHold):m.check_census(x,obs)
    def test_parent_ref_tampering_fails(self):
        x, obs=sample();x['source_ref']='main'
        with self.assertRaises(m.DepthHold):m.check_census(x,obs)

# Independently exercise every article against three risks: depth, citation and publication drift.
def _case(index, field):
    def test(self):
        x,obs=sample()
        if field=='depth':obs[index]['observed_prose_words']=0
        if field=='cite':obs[index]['citation_occurrences']-=1
        if field=='publish':obs[index]['publish']='publish'
        with self.assertRaises(m.DepthHold):m.check_census(x,obs)
    return test
for i in range(35):
    for t in ('depth','cite','publish'):
        setattr(R139Basic,f'test_article_{i:02d}_{t}_must_hold',_case(i,t))
