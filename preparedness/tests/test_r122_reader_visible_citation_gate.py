"""R122 synthetic custody and concealed-citation mutations; no repo writes."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / 'tools' / 'r122_reader_visible_citation_gate.py'
SPEC = importlib.util.spec_from_file_location('r122', PATH)
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)
SLUGS = [f'synthetic-guide-{i:02d}' for i in range(35)]


def fixture():
    blobs, original, candidate = {}, {}, {}
    for slug in SLUGS:
        a = '<section><p>Visible {{cite:source-one}}</p><p>More {{cite:source-two}}</p></section>'
        bb = a + ('<p>Additional context {{cite:source-three}}</p>' if slug == SLUGS[0] else '')
        for tree, body in ((original, a),(candidate, bb)):
            value=body.encode()
            oid=gate.oid_bytes(value)
            blobs[oid]=value
            tree[slug+'.body.html']=oid
            tree[slug+'.meta.json']='a'*40
    snap={'schema':gate.SCHEMA,'issue':136,'business_issue':820,
          'governance':{'release_state':'HOLD','may_publish':False,'may_merge':False,
                        'independent_QD_PASS':False,'medical_safety_verified':False,
                        'merchant_offer_verified':False},
          'snapshots':[{'role':'baseline','sha':'a'*40,'article_files':original},
                       {'role':'candidate','sha':'b'*40,'article_files':candidate}]
                       + [{'role':'contributor','cluster':str(i),'sha':str(i+1)*40}
                          for i in range(7)]}
    return snap, blobs

def replace(snap, blobs, slug, injection, version='candidate'):
    tree=snap['snapshots'][1 if version=='candidate' else 0]['article_files']
    old=tree[slug+'.body.html']
    value=(blobs[old].decode() + injection).encode()
    oid=gate.oid_bytes(value)
    blobs[oid]=value
    tree[slug+'.body.html']=oid

def result(snap, blobs):
    return gate.audit(snap,lambda oid:blobs[oid])

class Core(unittest.TestCase):
    def test_clean_corpus_is_hold_not_approval(self):
        s,b=fixture(); r=result(s,b)
        self.assertEqual(r['articles_checked'],35)
        self.assertEqual(r['citation_visibility_blockers'],[])
        self.assertEqual(r['state'],'HOLD')
        self.assertFalse(r['release_authorized'])
        self.assertFalse(r['QD_PASS'])
    def test_changed_citation_counts_still_visible(self):
        s,b=fixture(); self.assertFalse(result(s,b)['citation_visibility_blockers'])
    def test_read_only_and_deterministic(self):
        s,b=fixture(); old=copy.deepcopy((s,b))
        self.assertEqual(result(s,b),result(s,b))
        self.assertEqual((s,b),old)
    def test_duplicate_json_keys(self):
        with self.assertRaisesRegex(gate.Hold,'DUPLICATE_JSON_KEY'):
            gate.no_duplicate_json('{"a":1,"a":2}')
    def test_unauthorized_qd(self):
        s,b=fixture(); s['governance']['independent_QD_PASS']=True
        with self.assertRaisesRegex(gate.Hold,'UNAUTHORIZED_GOVERNANCE_UPGRADE'):
            result(s,b)
    def test_mutated_git_object(self):
        s,b=fixture(); oid=s['snapshots'][1]['article_files'][SLUGS[0]+'.body.html']
        b[oid]=b'forged'
        with self.assertRaisesRegex(gate.Hold,'GIT_OBJECT_MISMATCH'):
            result(s,b)
    def test_roster_missing_meta(self):
        s,b=fixture(); s['snapshots'][0]['article_files'].pop(SLUGS[0]+'.meta.json')
        with self.assertRaisesRegex(gate.Hold,'ARTICLE_ROSTER_CHANGED'):
            result(s,b)
    def test_malformed_citation(self):
        s,b=fixture(); replace(s,b,SLUGS[0],'<p>{{cite:BAD ID}}</p>')
        with self.assertRaisesRegex(gate.Hold,'MALFORMED_CITATION'):
            result(s,b)
    def test_token_in_comment(self):
        s,b=fixture(); replace(s,b,SLUGS[0],'<!-- {{cite:hidden-source}} -->')
        self.assertEqual(len(result(s,b)['citation_visibility_blockers']),1)
    def test_token_in_attribute(self):
        s,b=fixture(); replace(s,b,SLUGS[0],'<div data-note="{{cite:hidden-source}}"></div>')
        self.assertEqual(len(result(s,b)['citation_visibility_blockers']),1)
    def test_script_region(self):
        s,b=fixture(); replace(s,b,SLUGS[0],'<script>{{cite:hidden-source}}</script>')
        self.assertEqual(len(result(s,b)['citation_visibility_blockers']),1)
    def test_unapproved_status(self):
        s,b=fixture(); s['governance']['may_publish']=True
        with self.assertRaisesRegex(gate.Hold,'UNAUTHORIZED_GOVERNANCE_UPGRADE'):
            result(s,b)

HIDDEN = [
    '<!-- {{cite:concealed}} -->',
    '<p hidden>{{cite:concealed}}</p>',
    '<p aria-hidden="true">{{cite:concealed}}</p>',
    '<p style="display:none">{{cite:concealed}}</p>',
    '<p style="visibility: hidden">{{cite:concealed}}</p>',
    '<p class="sr-only">{{cite:concealed}}</p>',
    '<p class="screen-reader-text">{{cite:concealed}}</p>',
    '<p class="visually-hidden">{{cite:concealed}}</p>',
    '<script>{{cite:concealed}}</script>',
    '<style>{{cite:concealed}}</style>',
    '<template>{{cite:concealed}}</template>',
    '<noscript>{{cite:concealed}}</noscript>',
    '<iframe>{{cite:concealed}}</iframe>',
    '<svg><text>{{cite:concealed}}</text></svg>',
    '<p data-x="{{cite:concealed}}">Safe text</p>',
]

def mutation_test(slug, injection):
    def test(self):
        s,b=fixture(); replace(s,b,slug,injection)
        problems=result(s,b)['citation_visibility_blockers']
        self.assertEqual([x['slug'] for x in problems],[slug])
        self.assertLess(problems[0]['candidate_visible'],problems[0]['candidate_raw'])
    return test

# 35 separate article mutations, plus variants for several kinds of concealment.
for i,slug in enumerate(SLUGS):
    setattr(Core,f'test_concealed_across_35_article_roster_{i:02d}',
            mutation_test(slug,HIDDEN[i%len(HIDDEN)]))
for i,v in enumerate(HIDDEN):
    setattr(Core,f'test_hidden_context_{i:02d}',mutation_test(SLUGS[0],v))

if __name__ == '__main__':
    unittest.main()
