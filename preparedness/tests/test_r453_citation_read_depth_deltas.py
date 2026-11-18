"""Synthetic regressions for R453; no authentic clinical/food/WordPress QA."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / 'tools'))
import r452_qa157_semantic_custody as custody
import r453_citation_read_depth_deltas as gate

P = custody.PATHS


def fixture():
    h = ('<h2 id="a">Practice</h2><p>do not switch off the main breaker; '
         'smoke and carbon monoxide alarms and medical equipment need power '
         '{{cite:start-redcross-older-adults}}</p>')
    m = ('<h2 id="b">Medicine</h2><p>Ask pharmacist about refrigerated medicine '
         'interim-use and replacement plan {{cite:start-cdc-pyh-prescriptions}}</p>')
    sources = {'sources': [
        {'id':'start-redcross-older-adults','kind':'nonprofit','url':'https://example.org/r',
         'publisher':'American Red Cross','supports':'Original long supporting scope and caveats.',
         'notes':'Read only certain claim scopes'},
        {'id':'start-cdc-pyh-prescriptions','kind':'agency','url':'https://example.gov/m',
         'publisher':'CDC','supports':'Medication planning with clinician advice.'}
    ]}
    slate = [{'slug': f'article-{i}', 'n':i,'title':f'Article {i}',
              'track':'modern','section':'start-here','status':'drafted-pending-safety-review',
              'gate': True} for i in range(1,36)]
    for k, slug in enumerate(sorted(custody.CRITICAL)):
        slate[k]['slug'] = slug
    return {P[0]:h.encode(),P[1]:m.encode(), P[2]:json.dumps(sources).encode(),
            P[3]:json.dumps({'slate':slate}).encode()}


def call(qa=None, candidate=None):
    qa = qa or fixture()
    candidate = candidate or dict(qa)
    return gate.review_packet(qa, candidate, [custody.git_blob(qa[p]) for p in P],
                              [custody.git_blob(candidate[p]) for p in P])


class GateTests(unittest.TestCase):
    def test_baseline(self):
        r = call()
        self.assertEqual(r['release_state'], custody.HOLD)
        self.assertEqual(r['qualified_review'], 'NOT_APPROVED')
        self.assertEqual(r['unresolved_source_disputes'], 5)
        self.assertEqual(r['unselected_forks'], 9)
        self.assertEqual(r['article_citation_changes_requiring_review'][0]['citation_occurrences_removed'], {})
    def test_scope_diminution_is_visible(self):
        a=fixture();b=dict(a);s=json.loads(b[P[2]])
        s['sources'][0]['supports']='Scope'
        b[P[2]]=json.dumps(s).encode()
        self.assertTrue(call(a,b)['source_changes_requiring_review'][0]['reading_scope_changed'])
    def test_citation_removal_is_visible(self):
        a=fixture();b=dict(a);b[P[0]]=b[P[0]].replace(b'{{cite:start-redcross-older-adults}}',b'')
        r=call(a,b)
        self.assertEqual(r['article_citation_changes_requiring_review'][0]['citation_occurrences_removed'],
                         {'start-redcross-older-adults':1})
    def test_heading_change_visible(self):
        a=fixture();b=dict(a);b[P[1]]=b[P[1]].replace(b'Medicine</h2>',b'Medications</h2>')
        self.assertTrue(call(a,b)['article_citation_changes_requiring_review'][1]['heading_sequence_changed'])
    def test_not_elevated_to_approval_when_unchanged(self):
        self.assertEqual(call()['article_citation_placements'], 'NOT_INDEPENDENTLY_VERIFIED')
    def test_real_pins_reject_synthetic(self):
        with self.assertRaises(custody.CustodyError):
            gate.review_packet(fixture(),fixture())
    def test_duplicate_json_key_rejected(self):
        a=fixture(); b=dict(a);b[P[2]]=b'{"sources":[],"sources":[]}'
        with self.assertRaises(custody.CustodyError):call(a,b)
    def test_citations_repeat_occurrences(self):
        self.assertEqual(gate.citations('{{cite:a}} {{cite:a}} {{cite:b}}'),{'a':2,'b':1})
    def test_url_reassignment_rejected(self):
        a=fixture();b=dict(a);o=json.loads(b[P[2]]);o['sources'][0]['url']='https://bad.example'
        b[P[2]]=json.dumps(o).encode()
        with self.assertRaises(custody.CustodyError):call(a,b)
    def test_published_state_rejected(self):
        a=fixture();b=dict(a);o=json.loads(b[P[3]]);o['slate'][0]['status']='published'
        b[P[3]]=json.dumps(o).encode()
        with self.assertRaises(custody.CustodyError):call(a,b)


def make_case(n, pattern):
    def test(self):
        a=fixture(); b=dict(a)
        if n%2:
            b[P[0]]+=('<p>New longer context '+pattern+' {{cite:additional-doc}}</p>').encode()
        else:
            b[P[1]]+=('<h3>Section '+pattern+'</h3>').encode()
        r=call(a,b)
        rec=r['article_citation_changes_requiring_review'][0 if n%2 else 1]
        self.assertTrue(rec['requires_qualified_review'])
        self.assertEqual(r['release_state'], 'DRAFT_HARD_HOLD')
        self.assertEqual(r['qualified_review'], 'NOT_APPROVED')
        if n%2:self.assertEqual(rec['citation_occurrences_added'].get('additional-doc'),1)
        else:self.assertTrue(rec['heading_sequence_changed'])
    test.__name__ = f'test_delta_case_{n:02}'
    return test

for i in range(1,53):
    setattr(GateTests,f'test_delta_case_{i:02}',make_case(i,'claim'+str(i)))

if __name__=='__main__':unittest.main()
