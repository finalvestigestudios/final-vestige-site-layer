"""R350 adversarial tests: synthetic in-memory branch documents, never source writes."""
from __future__ import annotations
from copy import deepcopy
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
import json
import tempfile
import unittest

spec=spec_from_file_location('r350',Path(__file__).resolve().parents[1]/'tools'/'r350_nine_branch_content_custody_hold.py')
r=module_from_spec(spec);spec.loader.exec_module(r)

def document(kind='articles',i=0):
    slug=f'example-{kind}-{i:02}'
    return {'id':f'{kind}/{slug}',
            'body':'<article><p>PRIVATE CLAIM WITH PLACEHOLDER {{cite:source-one}}</p></article>',
            'meta':{'slug':slug,'status':{'publish':'draft'},
                    'safety_review':{'state':'pending'},'track':'modern',
                    'source_use':{'source-one':'source reviewed separately'},
                    'canonical_url':f'/preparedness/{kind}/{slug}/'}}

def sample():
    d=[document('articles',i) for i in range(35)]+[document('tools',i) for i in range(6)]
    bs=list(r.PINS)
    return {b:{'sha':r.PINS[b],'documents':d[i::len(bs)]} for i,b in enumerate(bs)}

class TestBaseline(unittest.TestCase):
    def setUp(self):self.c=sample()
    def test_9(self):self.assertEqual(r.ledger(self.c)['branch_count'],9)
    def test_41(self):self.assertEqual(r.ledger(self.c)['unique_documents'],41)
    def test_35_6(self):self.assertEqual((r.ledger(self.c)['article_count'],r.ledger(self.c)['tool_count']),(35,6))
    def test_never_publish(self):self.assertFalse(r.ledger(self.c)['may_publish'])
    def test_never_merge(self):self.assertFalse(r.ledger(self.c)['may_merge'])
    def test_never_qd(self):self.assertFalse(r.ledger(self.c)['qualified_qd_pass'])
    def test_never_merchant(self):self.assertFalse(r.ledger(self.c)['commerce_offer_verified'])
    def test_never_paid(self):self.assertFalse(r.ledger(self.c)['verified_paid_orders'])
    def test_no_original_text(self):self.assertNotIn('PRIVATE CLAIM',json.dumps(r.ledger(self.c)))
    def test_no_raw_url(self):self.assertNotIn('/preparedness/articles/',json.dumps(r.ledger(self.c)))
    def test_reordering(self):
        a=r.ledger(self.c);self.c=dict(reversed(list(self.c.items())))
        self.assertEqual(a,r.ledger(self.c))
    def test_draft_stays_held(self):self.assertEqual(r.ledger(self.c)['status'],'DRAFT_REVIEW_ONLY_HARD_HOLD')
    def test_incomplete_git_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(r.audit_repo(Path(tmp))['status'],'INVALID_HARD_HOLD')
    def test_missing_document(self):
        next(iter(self.c.values()))['documents'].pop()
        self.assertIn('UNION_NOT_35_ARTICLES_6_TOOLS',r.ledger(self.c)['errors'])
    def test_extra_document(self):
        next(iter(self.c.values()))['documents'].append(document('articles',36))
        self.assertIn('UNION_NOT_35_ARTICLES_6_TOOLS',r.ledger(self.c)['errors'])
    def test_metadata_only_not_counted(self):
        self.c[next(iter(self.c))]['documents'][0]['meta']['source_use']['source-two']='metadata only'
        self.assertEqual(r.ledger(self.c)['status'],'DRAFT_REVIEW_ONLY_HARD_HOLD')
    def test_add_same_doc_same_content_no_conflict(self):
        names=list(self.c)
        self.c[names[1]]['documents'].append(deepcopy(self.c[names[0]]['documents'][0]))
        self.assertFalse(r.ledger(self.c)['manual_review'])
    def test_add_same_doc_different_body_conflicts(self):
        names=list(self.c);dup=deepcopy(self.c[names[0]]['documents'][0]);dup['body']+=' MORE ORIGINAL DEPTH'
        self.c[names[1]]['documents'].append(dup)
        x=r.ledger(self.c);self.assertIn('UNRESOLVED_MULTIBRANCH_CONTENT_CONFLICTS',x['errors'])
        self.assertEqual(x['manual_review'][0]['max_words']-x['manual_review'][0]['min_words'],3)
    def test_safety_conflict_in_manual_review(self):
        names=list(self.c);dup=deepcopy(self.c[names[0]]['documents'][0]);dup['meta']['safety_review']['state']='not-required';dup['meta']['track']='lost-ways'
        self.c[names[1]]['documents'].append(dup)
        self.assertIn('pending',r.ledger(self.c)['manual_review'][0]['safety_variants'])
    def test_deduplicate_url_across_documents(self):
        docs=list(self.c.values()); docs[1]['documents'][0]['meta']['canonical_url']=docs[0]['documents'][0]['meta']['canonical_url']
        self.assertIn('DUPLICATE_CANONICAL_URL',r.ledger(self.c)['errors'])
    def test_frozen_sha_pins(self):
        self.assertEqual(len(r.PINS),9);self.assertTrue(all(len(v)==40 for v in r.PINS.values()))

class TestMutations(unittest.TestCase):pass
MUTATIONS={
 'sha_drift':lambda c,b,d:c[b].update(sha='a'*40),
 'empty_sha':lambda c,b,d:c[b].update(sha=''),
 'missing_documents':lambda c,b,d:c[b].update(documents=None),
 'documents_dict':lambda c,b,d:c[b].update(documents={}),
 'documents_string':lambda c,b,d:c[b].update(documents='not a list'),
 'missing_branch':lambda c,b,d:c.pop(b),
 'unknown_branch':lambda c,b,d:c.update({'claude/unknown':{'sha':'0'*40,'documents':[]}}),
 'invalid_document':lambda c,b,d:c[b]['documents'].append(None),
 'duplicate_id':lambda c,b,d:c[b]['documents'].append(deepcopy(d)),
 'empty_body':lambda c,b,d:d.update(body=''),
 'whitespace_body':lambda c,b,d:d.update(body='   '),
 'null_body':lambda c,b,d:d.update(body=None),
 'numeric_body':lambda c,b,d:d.update(body=5),
 'null_metadata':lambda c,b,d:d.update(meta=None),
 'publish_state':lambda c,b,d:d['meta']['status'].update(publish='publish'),
 'approved_state':lambda c,b,d:d['meta']['safety_review'].update(state='approved'),
 'publish_null':lambda c,b,d:d['meta'].update(status=None),
 'publish_missing':lambda c,b,d:d['meta'].pop('status'),
 'safety_null':lambda c,b,d:d['meta'].update(safety_review=None),
 'safety_missing':lambda c,b,d:d['meta'].pop('safety_review'),
 'modern_not_required':lambda c,b,d:d['meta']['safety_review'].update(state='not-required'),
 'wrong_slug':lambda c,b,d:d['meta'].update(slug='wrong'),
 'wrong_type_id':lambda c,b,d:d.update(id='wrong/type'),
 'capital_slug':lambda c,b,d:d.update(id=d['id'].upper()),
 'slash_injection':lambda c,b,d:d.update(id='articles/../../outside'),
 'missing_id':lambda c,b,d:d.pop('id'),
 'source_use_null':lambda c,b,d:d['meta'].update(source_use=None),
 'source_use_list':lambda c,b,d:d['meta'].update(source_use=[]),
 'source_use_bad_key':lambda c,b,d:d['meta'].update(source_use={3:'invalid'}),
 'undeclared_citation':lambda c,b,d:d.update(body=d['body']+' {{cite:second-source}}'),
 'url_external':lambda c,b,d:d['meta'].update(canonical_url='https://evil.example/preparedness/a'),
 'url_http':lambda c,b,d:d['meta'].update(canonical_url='http://finalvestige.com/preparedness/a'),
 'url_query':lambda c,b,d:d['meta'].update(canonical_url='/preparedness/a?track=1'),
 'url_fragment':lambda c,b,d:d['meta'].update(canonical_url='/preparedness/a#token'),
 'url_js':lambda c,b,d:d['meta'].update(canonical_url='javascript:alert(1)'),
 'url_wrong_path':lambda c,b,d:d['meta'].update(canonical_url='/focus/'),
 'url_wrong_type':lambda c,b,d:d['meta'].update(canonical_url=22),
 'url_none':lambda c,b,d:d['meta'].update(canonical_url=None),
 'url_missing':lambda c,b,d:d['meta'].pop('canonical_url'),
 'url_duplicate':lambda c,b,d:c[b]['documents'][1]['meta'].update(canonical_url=d['meta']['canonical_url']),
}
for name,mutation in MUTATIONS.items():
    def generated(f):
        def t(self):
            c=sample();b=next(iter(c));d=c[b]['documents'][0]
            f(c,b,d);x=r.ledger(c)
            self.assertEqual(x['status'],'INVALID_HARD_HOLD',name)
            self.assertTrue(x['errors'],name)
            self.assertFalse(x['may_publish'])
        return t
    setattr(TestMutations,'test_detect_'+name,generated(mutation))
if __name__=='__main__':unittest.main()
