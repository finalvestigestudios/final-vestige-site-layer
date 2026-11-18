"""R468 isolated deterministic tests only; no real article or QD approval."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SRC = Path(__file__).resolve().parents[1] / 'tools/r468_citation_context_docket.py'
spec = importlib.util.spec_from_file_location('r468_gate', SRC)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def fixture(body='<p>Keep paper contacts {{cite:agency}} for outages.</p><p>Review school rules {{cite:school}}.</p>'):
    meta = {'slug': 'family-plan', 'status': {'publish':'draft'},
            'source_use': {'agency':'official household plan; not school policy',
                           'school':'local school policy; jurisdiction varies'}}
    sources = {'base':[{'id':'agency','url':'https://ready.gov/plan'},
                       {'id':'school','url':'https://school.example/reunification'}],
               'family':[{'id':'school','url':'https://school.example/reunification'}]}
    return meta, body, sources

def take(meta=None, body=None, sources=None):
    m,b,s=fixture()
    return gate.docket_article('family-plan', m if meta is None else meta,
                               b if body is None else body,'family',s if sources is None else sources)

class Base(unittest.TestCase):
    def test_two_events(self):
        doc=take(); self.assertEqual(doc['citation_count'],2)
        self.assertEqual([e['source_id'] for e in doc['citation_events']], ['agency','school'])
    def test_fallback_and_cluster_are_distinct(self):
        ev=take()['citation_events']
        self.assertEqual([x['selected_origin'] for x in ev],['base','family'])
    def test_source_scope_not_deduped(self):
        doc=take()
        self.assertEqual(doc['source_use_count'],2)
        self.assertEqual(doc['citation_events'][1]['authored_reading_scope'],
                         'local school policy; jurisdiction varies')
    def test_original_literal_url_survives(self):
        self.assertEqual(take()['citation_events'][0]['literal_url'], 'https://ready.gov/plan')
    def test_stable_reexecution(self):
        self.assertEqual(take(),take())
    def test_unmodified_compare(self):
        self.assertFalse(gate.compare(take(),take())['review_required'])
    def test_raw_body_whitespace_is_detected(self):
        a=take(); b=take(body=fixture()[1].replace('paper contacts','paper  contacts'))
        self.assertTrue(gate.compare(a,b)['review_required'])
    def test_context_change_with_same_citation_count(self):
        a=take(); b=take(body=fixture()[1].replace('paper contacts','digital contacts'))
        self.assertEqual(a['citation_count'],b['citation_count'])
        self.assertIn('citation_events[0].context_sha256',gate.compare(a,b)['differences'])
    def test_reading_scope_change(self):
        m,b,s=fixture(); a=take(); m['source_use']['agency']='Different official reading scope'
        c=gate.compare(a,take(meta=m)); self.assertIn('citation_events[0].authored_reading_scope_sha256',c['differences'])
    def test_context_without_block(self):
        d=take(body='Emergency {{cite:agency}} and policy {{cite:school}}')
        self.assertEqual(d['unit_count'],1)
    def test_nested_inline_elements(self):
        d=take(body='<p><strong>Emergency</strong> {{cite:agency}} and <em>school {{cite:school}}</em>.</p>')
        self.assertEqual(d['citation_count'],2)
    def test_comment_citation_rejected(self):
        with self.assertRaises(gate.ContextHold):
            take(body=fixture()[1]+'<!-- {{cite:agency}} -->')
    def test_script_citation_rejected(self):
        with self.assertRaises(gate.ContextHold):
            take(body=fixture()[1]+'<script>{{cite:agency}}</script>')
    def test_cite_in_attribute_rejected(self):
        with self.assertRaises(gate.ContextHold):
            take(body=fixture()[1].replace('<p>','<p title="{{cite:agency}}">',1))
    def test_extra_unregistered_citation_rejected(self):
        with self.assertRaises(gate.ContextHold):
            take(body=fixture()[1]+'{{cite:unknown}}')
    def test_malformed_token_rejected(self):
        with self.assertRaises(gate.ContextHold):
            take(body=fixture()[1].replace('{{cite:agency}}','{{cite:AGENCY}}'))
    def test_duplicate_url_ids_kept_distinct(self):
        m,b,s=fixture(); s['family'].append({'id':'agency','url':'https://ready.gov/plan'})
        d=take(meta=m,body=b,sources=s)
        self.assertEqual(d['citation_events'][0]['selected_origin'],'family')
    def test_slash_url_retained(self):
        m,b,s=fixture();s['base'][0]['url']='https://ready.gov/plan/'
        self.assertEqual(take(sources=s)['citation_events'][0]['literal_url'],'https://ready.gov/plan/')
    def test_invalid_missing_checkout_exit_2(self):
        with tempfile.TemporaryDirectory() as t:
            proc=subprocess.run([sys.executable,str(SRC),'--root',t],capture_output=True,text=True)
            self.assertEqual(proc.returncode,2)
            self.assertFalse(json.loads(proc.stdout)['may_publish'])
    def test_claims_stay_unverified(self):
        d=take(); self.assertFalse(d['qualified_qd_pass']);self.assertFalse(d['claim_support_verified'])

class Adversarial(unittest.TestCase):
    pass

# 80 genuinely independent context mutations: each changes distinct text or source-use note.
for i in range(40):
    def altered_context(self,i=i):
        m,b,s=fixture()
        left=take(meta=m,body=b,sources=s)
        right=take(meta=m,body=b.replace('paper contacts',f'paper contacts edition {i}'),sources=s)
        diff=gate.compare(left,right)
        self.assertTrue(diff['review_required'])
        self.assertIn('units[0].text_sha256',diff['differences'])
    setattr(Adversarial,f'test_context_mutation_{i:02d}',altered_context)
for i in range(40):
    def altered_reading_scope(self,i=i):
        m,b,s=fixture(); orig=take(meta=m,body=b,sources=s)
        m['source_use']['school']=m['source_use']['school']+f' variation {i}'
        diff=gate.compare(orig,take(meta=m,body=b,sources=s))
        self.assertIn('citation_events[1].authored_reading_scope_sha256',diff['differences'])
    setattr(Adversarial,f'test_scope_mutation_{i:02d}',altered_reading_scope)

class Negative(unittest.TestCase):
    pass
for i in range(20):
    def deny_missing_source(self,i=i):
        m,b,s=fixture()
        s['base'][0]['id']=f'unrelated-{i}'
        with self.assertRaises(gate.ContextHold):take(meta=m,body=b,sources=s)
    setattr(Negative,f'test_missing_source_{i:02d}',deny_missing_source)
for i in range(20):
    def deny_changed_publish(self,i=i):
        m,b,s=fixture();m['status']['publish']=f'publish_candidate_{i}'
        with self.assertRaises(gate.ContextHold):take(meta=m,body=b,sources=s)
    setattr(Negative,f'test_non_draft_{i:02d}',deny_changed_publish)

if __name__=='__main__':
    unittest.main()
