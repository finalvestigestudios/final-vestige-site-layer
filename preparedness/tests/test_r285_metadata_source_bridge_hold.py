"""R285 metadata/source bridge adversarial regression, entirely synthetic."""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

FILE = Path(__file__).resolve().parents[1]/'tools/r285_metadata_source_bridge_hold.py'
spec=importlib.util.spec_from_file_location('r285_metadata_source_bridge_hold', FILE)
g=importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def fixture():
    articles=[]; entries=[]; metadata={}; sources={}
    for origin in sorted(g.SOURCE_ROSTER):
        sources[origin]={'sources': []}
    origin = 'sources/register.json'
    for n in range(244):
        sources[origin]['sources'].append({'id':f'source-{n}', 'url':f'https://example.org/source-{n}',
                                           'verified_on':'2026-10-29'})
    for n in range(1, 36):
        slug = f'article-{n:02d}'
        section = 'start-here' if n<=20 else 'lost-ways'
        track = 'modern' if n<=20 else 'lost-ways'
        articles.append({'n':n,'slug':slug,'section':section,'track':track})
        path=f'content/articles/{slug}.meta.json'
        entries.append({'path':path,'role':'article_meta','sha':'a'*40,'size':100})
        metadata[path] = {'n':n,'slug':slug,'section':section,'track':track,
             'status':{'publish':'draft'},'safety_review':{'state':'pending','reviewer':None},
             'source_use':{'source-0':'Limited source scope recorded here.'}}
    for n in range(6):
        slug=f'tool-{n}'
        path=f'content/tools/{slug}.meta.json'
        entries.append({'path':path,'role':'tool_meta','sha':'b'*40,'size':100})
        metadata[path]={'n':102+(n%2),'slug':slug,'status':{'publish':'draft'},
             'safety_review':{'state':'pending'},'source_use':{'source-1':'Specific narrow application.'}}
    entries += [{'path':f'extra/{n}','role':'source_origin','sha':'c'*40,'size':100} for n in range(55)]
    assert len(entries)==96
    original={'state':g.HOLD,'publication_authorized':False,'independent_qd_pass':False,
              'medical_safety_verified':False,'articles':articles}
    integrated={'state':g.HOLD,'publication_authorized':False,'independent_qd_pass':False,
                'medical_safety_verified':False,'entries':entries}
    return original,integrated,metadata,sources

class Bridge(unittest.TestCase):
    def setUp(self):self.o,self.i,self.m,self.s=fixture()
    def result(self):return g.evaluate(self.o,self.i,self.m,self.s)
    def first(self):return self.m['content/articles/article-01.meta.json']
    def test_00_baseline_stays_hard_hold(self):
        x=self.result()
        self.assertEqual(x['state'],g.HOLD)
        self.assertEqual((x['articles'],x['tools'],x['source_records'],x['metadata_records']),(35,6,244,41))
        self.assertEqual(x['source_use_mentions'],41)
        self.assertFalse(x['independent_qd_pass'])
        self.assertTrue(x['requires_source_scope_review'])
    def test_01_deterministic(self):self.assertEqual(self.result(),self.result())
    def test_02_original_article_order_does_not_matter(self):
        expected=self.result();self.o['articles'].reverse();self.assertEqual(expected,self.result())
    def test_03_duplicated_id_is_held_not_silently_resolved(self):
        self.s['sources/fragments/food.json']['sources'].append(self.s['sources/register.json']['sources'].pop())
        self.s['sources/fragments/food.json']['sources'].append(copy.deepcopy(self.s['sources/register.json']['sources'][0]))
        self.s['sources/register.json']['sources'].pop(2)
        self.assertIn('source-0',self.result()['ambiguous_citation_ids'])
    def test_04_approved_metadata_not_independent_approval(self):
        self.first()['safety_review']={'state':'approved','reviewer':'unverified chat message'}
        x=self.result();self.assertIn('article-01',x['historical_metadata_approved_labels_NOT_independent_approval'])
        self.assertFalse(x['medical_safety_verified']);self.assertFalse(x['publication_authorized'])
    def test_05_duplicate_tool_numbers_legitimate(self):
        self.assertEqual(self.result()['tools'],6)
    def test_06_unknown_source_always_errors(self):
        self.first()['source_use']={'missing-agency':'Unverified.'}
        with self.assertRaisesRegex(ValueError,'unregistered citation IDs'):self.result()
    def test_07_duplicate_json_keys_fail(self):
        with self.assertRaisesRegex(ValueError,'duplicate JSON key'):g.strict_json(b'{"a":1,"a":2}')
    def test_08_nonfinite_json_fail(self):
        with self.assertRaisesRegex(ValueError,'nonfinite JSON'):g.strict_json(b'{"a":NaN}')
    def test_09_bad_pin_fail(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,'bad pin'):g.pinned_bytes(td,'foo','x')
    def test_10_unsafe_path_fail(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,'unsafe pinned path'):g.pinned_bytes(td,'../foo','a'*40)
    def test_11_pinned_symlink_fail(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'src';p.symlink_to('/etc/hosts')
            with self.assertRaisesRegex(ValueError,'symlinked pinned file'):g.pinned_bytes(td,'src','a'*40)
    def test_12_incomplete_checkout_invalid(self):
        with tempfile.TemporaryDirectory() as td:self.assertEqual(g.audit(td)['state'],g.INVALID)
    def test_13_cli_exit_three_on_incomplete_checkout(self):
        with tempfile.TemporaryDirectory() as td:
            p=subprocess.run([sys.executable,str(FILE),'--root',td],capture_output=True,text=True)
            self.assertEqual(p.returncode,3);self.assertEqual(json.loads(p.stdout)['state'],g.INVALID)

BAD={
 'original_pub':lambda o,i,m,s:o.__setitem__('publication_authorized',True),
 'integrated_pub':lambda o,i,m,s:i.__setitem__('publication_authorized',True),
 'original_medical':lambda o,i,m,s:o.__setitem__('medical_safety_verified',True),
 'integrated_medical':lambda o,i,m,s:i.__setitem__('medical_safety_verified',True),
 'original_qd':lambda o,i,m,s:o.__setitem__('independent_qd_pass',True),
 'integrated_qd':lambda o,i,m,s:i.__setitem__('independent_qd_pass',True),
 'original_missing_gate':lambda o,i,m,s:o.pop('publication_authorized'),
 'integrated_missing_gate':lambda o,i,m,s:i.pop('independent_qd_pass'),
 'original_state':lambda o,i,m,s:o.__setitem__('state','APPROVED'),
 'integrated_state':lambda o,i,m,s:i.__setitem__('state','LIVE'),
 'original_count':lambda o,i,m,s:o['articles'].pop(),
 'integrated_count':lambda o,i,m,s:i['entries'].pop(),
 'double_article_slug':lambda o,i,m,s:o['articles'][1].__setitem__('slug','article-01'),
 'deleted_meta':lambda o,i,m,s:m.pop('content/articles/article-01.meta.json'),
 'extra_meta':lambda o,i,m,s:m.__setitem__('content/articles/evil.meta.json',{}),
 'meta_slug_drift':lambda o,i,m,s:m['content/articles/article-01.meta.json'].__setitem__('slug','alternate'),
 'meta_number_drift':lambda o,i,m,s:m['content/articles/article-01.meta.json'].__setitem__('n',99),
 'meta_section_drift':lambda o,i,m,s:m['content/articles/article-01.meta.json'].__setitem__('section','water'),
 'meta_track_drift':lambda o,i,m,s:m['content/articles/article-01.meta.json'].__setitem__('track','lost-ways'),
 'meta_public':lambda o,i,m,s:m['content/articles/article-01.meta.json']['status'].__setitem__('publish','publish'),
 'meta_missing_status':lambda o,i,m,s:m['content/articles/article-01.meta.json'].pop('status'),
 'meta_bad_n_bool':lambda o,i,m,s:m['content/articles/article-01.meta.json'].__setitem__('n',True),
 'meta_bad_source_map':lambda o,i,m,s:m['content/articles/article-01.meta.json'].__setitem__('source_use',[]),
 'meta_empty_source_map':lambda o,i,m,s:m['content/articles/article-01.meta.json'].__setitem__('source_use',{}),
 'meta_blank_scope':lambda o,i,m,s:m['content/articles/article-01.meta.json']['source_use'].__setitem__('source-0','  '),
 'meta_missing_review':lambda o,i,m,s:m['content/articles/article-01.meta.json'].pop('safety_review'),
 'meta_review_missing_state':lambda o,i,m,s:m['content/articles/article-01.meta.json']['safety_review'].pop('state'),
 'meta_review_bad_type':lambda o,i,m,s:m['content/articles/article-01.meta.json'].__setitem__('safety_review',[]),
 'tool_bad_source':lambda o,i,m,s:m['content/tools/tool-0.meta.json'].__setitem__('source_use',{'not-present':'review'}),
 'tool_public':lambda o,i,m,s:m['content/tools/tool-0.meta.json']['status'].__setitem__('publish','published'),
 'tool_bad_slug':lambda o,i,m,s:m['content/tools/tool-0.meta.json'].__setitem__('slug','tool-9'),
 'source_roster_absent':lambda o,i,m,s:s.pop('sources/fragments/start.json'),
 'source_roster_extra':lambda o,i,m,s:s.__setitem__('sources/x.json',{'sources':[]}),
 'source_not_dict':lambda o,i,m,s:s.__setitem__('sources/register.json',[]),
 'source_not_list':lambda o,i,m,s:s['sources/register.json'].__setitem__('sources',{}),
 'source_count_lost':lambda o,i,m,s:s['sources/register.json']['sources'].pop(),
 'source_url_insecure':lambda o,i,m,s:s['sources/register.json']['sources'][0].__setitem__('url','http://example.com'),
 'source_id_missing':lambda o,i,m,s:s['sources/register.json']['sources'][0].pop('id'),
 'source_id_wrongtype':lambda o,i,m,s:s['sources/register.json']['sources'][0].__setitem__('id',1),
 'source_use_missing_id':lambda o,i,m,s:m['content/articles/article-01.meta.json']['source_use'].__setitem__('none','text'),
}

def make_case(name,mut):
    def test(self):
        mut(self.o,self.i,self.m,self.s)
        with self.assertRaises((ValueError,TypeError,KeyError,AttributeError)):
            self.result()
    test.__name__='test_r285_reject_'+name
    return test
for name,mut in BAD.items():setattr(Bridge,'test_r285_reject_'+name,make_case(name,mut))

if __name__=='__main__':unittest.main(verbosity=2)
