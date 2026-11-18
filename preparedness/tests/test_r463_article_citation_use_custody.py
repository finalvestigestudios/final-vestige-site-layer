"""R463 source/claim custody negative fixtures. Structural tests are NEVER a QD pass."""
from __future__ import annotations
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / 'tools' / 'r463_article_citation_use_custody.py'
spec = importlib.util.spec_from_file_location('r463', MODULE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def fixture():
    sl = {
        'a': ({'slug':'a','status':{'publish':'draft'}, 'safety_review':{'state':'pending'},
               'source_use':{'x':'first half','y':'backup'}},
              '<p>{{cite:x}}{{cite:x}}{{cite:y}}</p>'),
        'b': ({'slug':'b','status':{'publish':'draft'}, 'safety_review':{'state':'not-required'},
               'source_use':{'s':'other half','y':'base fallback'}},
              '<p>{{cite:s}}{{cite:y}}</p>')}
    origins = {'a':'base', 'b':'start'}
    sources = {origin:[] for origin in ('base','food','health','hist-field','hist-food',
                                       'hist-home','shelter','start')}
    sources['base'] = [{'id':'x','url':'https://a.example/x','supports':'one'},
                       {'id':'y','url':'https://a.example/y','supports':'two'}]
    sources['start'] = [{'id':'s','url':'https://a.example/s','supports':'three'}]
    sources['food'] = [{'id':'x','url':'https://other.example/x','supports':'different'}]
    return sl, origins, sources

def check(sl, origin, sources):
    return m.inspect(sl, origin, sources, expected=(2,5,4))

class PositiveCases(unittest.TestCase):
    def test_structural_success_is_still_hold(self):
        result=check(*fixture())
        self.assertEqual(result['state'],'SOURCE_USE_CITATION_STRUCTURAL_HOLD')
        self.assertFalse(result['qualified_qd_pass'])
        self.assertFalse(result['may_publish'])
        self.assertFalse(result['merchant_offer_verified'])
        self.assertIsNone(result['verified_paid_orders'])
        self.assertEqual(result['citation_occurrences'],5)
        self.assertEqual(result['distinct_article_source_use_memberships'],4)
        self.assertEqual(result['source_origin_fallbacks'][0]['id'],'y')
        self.assertEqual(result['conflicting_literal_url_source_id_references'][0]['id'],'x')
    def test_order_does_not_change_sources(self):
        slate, orig, src = fixture()
        slate = {'b':slate['b'],'a':slate['a']}
        self.assertEqual([r['slug'] for r in check(slate,orig,src)['articles']],['a','b'])
    def test_source_from_own_origin_wins(self):
        slate,orig,src=fixture()
        src['start'].append({'id':'y','url':'https://own.example/y','supports':'own'})
        out=check(slate,orig,src)
        self.assertEqual(out['source_origin_fallbacks'],[])
    def test_git_blob_identity(self):
        self.assertEqual(m.git_blob(b'hello\n'),'ce013625030ba8dba906f756967f9e9ca394464a')
    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(m.ArticleHold):
            json.loads('{"a":1,"a":2}',object_pairs_hook=m.pairs_unique)
    def test_pinned_bytes_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            (p/'real').write_bytes(b'ok')
            (p/'link').symlink_to(p/'real')
            with self.assertRaises(m.ArticleHold):
                m.pinned_bytes(p,'link',m.git_blob(b'ok'))
    def test_pinned_bytes_blob_drift_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/'real').write_bytes(b'ok')
            with self.assertRaises(m.ArticleHold):
                m.pinned_bytes(p,'real','0'*40)
    def test_pinned_bytes_directory_escape_rejected(self):
        with self.assertRaises(m.ArticleHold):
            m.pinned_bytes(Path('/tmp'),'../secret','0'*40)

def mutate(n,sl,orig,src):
    a=sl['a'][0]; b=sl['b'][0]
    cases=[
        lambda:sl.pop('a'),
        lambda:sl.update(c=copy.deepcopy(sl['a'])),
        lambda:orig.pop('a'),
        lambda:orig.update(b='wrong'),
        lambda:orig.update(b='food'),
        lambda:a.update(slug='b'),
        lambda:a.update(status={'publish':'publish'}),
        lambda:a.update(status={'publish':'private'}),
        lambda:a.update(status={}),
        lambda:a.update(safety_review={'state':'QD_PASS'}),
        lambda:a.update(safety_review={}),
        lambda:a.update(source_use=None),
        lambda:a.update(source_use={}),
        lambda:a['source_use'].update(x=''),
        lambda:a['source_use'].update(x=None),
        lambda:a['source_use'].update(extra='not cited'),
        lambda:a['source_use'].pop('y'),
        lambda:a['source_use'].pop('x'),
        lambda:a['source_use'].update(**{'x-!':'bad id'}),
        lambda:sl.update(a=(sl['a'][0],'<p>{{cite:x}}{{cite:y}}</p>')),
        lambda:sl.update(a=(sl['a'][0],'<p>{{cite:x}}{{cite:z}}{{cite:y}}</p>')),
        lambda:sl.update(a=(sl['a'][0],'<p>{{cite:x}}{{cite:x}}{{cite:bad}}</p>')),
        lambda:sl.update(a=(sl['a'][0],'<p>{{cite:x}}{{cite:x}}{{cite:y</p>')),
        lambda:sl.update(a=(sl['a'][0],'<p>{{cite:x}}{{cite:x}}{{cite:y}} {{cite:}}</p>')),
        lambda:sl.update(a=(sl['a'][0],'<p>{{cite:x}}{{cite:x}}{{cite:y}} {{cite:BAD}}</p>')),
        lambda:sl.update(a=(sl['a'][0],'<p>{{cite:x}}{{cite:x}}{{cite:y}} {{cite: x}}</p>')),
        lambda:sl.update(a=(sl['a'][0],'<p>{{cite:x}}{{cite:x}}{{cite:x}}</p>')),
        lambda:sl.update(a=(sl['a'][0],'<p>no citations</p>')),
        lambda:sl.update(a=(sl['a'][0],123)),
        lambda:sl.update(a=(None,sl['a'][1])),
        lambda:sl.update(**{'not valid':sl.pop('a')}),
        lambda:src.pop('base'),
        lambda:src.pop('start'),
        lambda:src.pop('food'),
        lambda:src.update(extra=[]),
        lambda:src.update(base=None),
        lambda:src['base'].pop(),
        lambda:src['base'].clear(),
        lambda:src['base'][0].update(id='z'),
        lambda:src['base'][0].update(url='http://bad.example'),
        lambda:src['base'][0].update(url=''),
        lambda:src['base'][0].update(id=''),
        lambda:src['base'].append(copy.deepcopy(src['base'][0])),
        lambda:src['base'].append({'id':'x','url':'https://different.example'}),
        lambda:src['start'][0].update(id='t'),
        lambda:src['start'][0].update(url='http://bad.example'),
        lambda:src['start'].clear(),
        lambda:src['food'][0].update(url=''),
        lambda:src.update(food='not a list'),
        lambda:src['health'].append({'id':'h','url':'http://invalid'}),
        lambda:src['health'].append({'id':None,'url':'https://valid.example'}),
        lambda:src['health'].append({'id':'h','url':None}),
        lambda:src['health'].append({}),
        lambda:sl['b'][0]['source_use'].pop('s'),
        lambda:sl['b'][0]['source_use'].update(rogue='text'),
        lambda:sl.update(b=(sl['b'][0],'<p>{{cite:s}}{{cite:rogue}}</p>')),
        lambda:sl.update(b=(sl['b'][0],'<p>{{cite:s}}</p>')),
        lambda:sl.update(b=(sl['b'][0],'<p>{{cite:s}}{{cite:y}}{{cite:y}}</p>')),
        lambda:orig.update(a='no cluster'),
        lambda:a.update(safety_review={'state':'approved-for-all'}),
        lambda:b.update(status={'publish':'public'}),
        lambda:b.update(source_use={'s':'only s'}),
    ]
    cases[n]()

class Adversarial(unittest.TestCase):
    pass
for n in range(61):
    def factory(index):
        def test(self):
            data=fixture();mutate(index,*data)
            with self.assertRaises((m.ArticleHold,TypeError,KeyError,AttributeError,ValueError)):
                check(*data)
        return test
    setattr(Adversarial,'test_mutation_%02d'%n,factory(n))

if __name__ == '__main__':
    unittest.main()
