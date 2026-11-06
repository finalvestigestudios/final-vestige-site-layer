"""Adversarial, synthetic R160 source-context tests; never a source or safety approval."""
from __future__ import annotations
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

module_path=Path(__file__).parents[1]/'tools'/'r160_citation_context_gate.py'
spec=importlib.util.spec_from_file_location('r160',module_path)
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)


def fixture():
    ids=['example-government-a','example-research-b']
    html=' '.join(['<p>'+('This text describes the context, limitations, and historical conditions. '*32)+
                   '{{cite:'+ids[i%2]+'}}</p>' for i in range(30)])
    meta={'slug':'synthetic-sample','section':'start-here','status':{'publish':'draft'},
          'safety_review':{'state':'pending'},
          'source_use':{x:'Pending contextual interpretation; not independently verified.' for x in ids}}
    return meta,html


class Gate(unittest.TestCase):
    def check(self,meta=None,html=None,slug='synthetic-sample'):
        orig,body=fixture()
        return g.article(slug,orig if meta is None else meta,body if html is None else html,'meta-blob','body-blob')
    def test_valid_contexts_and_no_approval(self):
        r=self.check();self.assertEqual(len(r['contexts']),30)
        self.assertEqual(r['citations'],30);self.assertEqual(r['unique_sources'],2)
        self.assertEqual(r['safety_recorded'],'pending')
        self.assertEqual(r['route'],'/preparedness/start-here/synthetic-sample/')
    def test_stability(self):
        self.assertEqual(self.check()['contexts'],self.check()['contexts'])
    def test_context_hash_changes_with_claim(self):
        m,b=fixture();after=b.replace('historical conditions. {{cite:','modern conditions. {{cite:',1)
        self.assertNotEqual(self.check(html=b)['contexts'][0]['context_sha256'],self.check(html=after)['contexts'][0]['context_sha256'])
    def test_known_blob(self):
        self.assertEqual(g.blob(b'hello'),'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')
    def test_missing_and_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'real').write_text('x');(p/'link').symlink_to(p/'real')
            for name in ['link','missing']:
                with self.subTest(name=name),self.assertRaises(ValueError):g.load(p,name)
    def test_wrong_blob(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'file').write_text('x')
            with self.assertRaisesRegex(ValueError,'Git blob'):g.load(p,'file','invalid')
    def test_cli_never_success(self):
        with tempfile.TemporaryDirectory() as d:self.assertEqual(g.main(['--repo',d]),2)
    def test_review_card_hold(self):
        m={'kind':'tool','slug':'family-reunification-card','status':{'publish':'draft'},
           'safety_review':{'state':'pending'},'source_use':{'id-'+str(i):'Pending' for i in range(11)},
           'description':'browser privacy and print behavior remain unverified'}
        html='Independent browser privacy checks remain pending. '+''.join('{{cite:id-'+str(i%11)+'}}' for i in range(16))
        self.assertTrue(g.review_card(m,html)['review_only'])
        for mutation in [('description','great printable'),('slug','published-card'),('status',{'publish':'publish'}),
                         ('safety_review',{'state':'approved'}),('source_use',{})]:
            wrong=copy.deepcopy(m);wrong[mutation[0]]=mutation[1]
            with self.subTest(mut=mutation[0]),self.assertRaises(ValueError):g.review_card(wrong,html)
        with self.assertRaises(ValueError):g.review_card(m,html.replace('Independent browser privacy checks remain pending.',''))

# 64 independently named adversarial tests. No synthetic claim can self-approve.
def case(n):
    def test(self):
        m,b=fixture()
        if n%8==0:m['status']['publish']='published'
        elif n%8==1:m['slug']='forged'
        elif n%8==2:m['section']='not/a/section'
        elif n%8==3:m['safety_review']['state']='PASS'
        elif n%8==4:m['source_use'].pop('example-government-a')
        elif n%8==5:m['source_use']['fabricated-reference']='Unsupported source use.'
        elif n%8==6:b=b.replace('cite:example-government-a','cite:forged-source',1)
        else:b=b.replace('{{cite:', '{{cite :',1)
        with self.assertRaisesRegex(ValueError,'drift|invalid|unknown|mismatch|malformed'):
            self.check(meta=m,html=b)
    return test

for n in range(64):setattr(Gate,f'test_adversarial_{n:02}',case(n))

if __name__=='__main__':unittest.main()
