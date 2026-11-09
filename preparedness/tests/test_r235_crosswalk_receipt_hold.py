"""R235 isolated deterministic crosswalk mutations; source/citation RELEASE HOLD only."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import r235_crosswalk_receipt_hold as gate

def src(i,url,scope):
    return {'id':f's{i}','url':url,'supports':scope,
            'verified_on':'2026-10-29','human_link_check':False}

class R235Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        (self.root/'sources/fragments').mkdir(parents=True)
        self.base=[src(1,'https://example.org/a','a-base'),src(2,'https://example.org/b','b')]
        self.food=[src(1,'https://example.org/a','a-food'),src(3,'https://example.org/c','c')]
        self.paths={'base':'sources/register.json','food':'sources/fragments/food.json'}
        a=[{'origin':'base','source_file':'preparedness/sources/register.json',
            'row_index':0,'source':copy.deepcopy(self.base[0])},
           {'origin':'food','source_file':'preparedness/sources/fragments/food.json',
            'row_index':0,'source':copy.deepcopy(self.food[0])}]
        self.doc={'schema_version':1,'source_files':[],'raw_source_rows':4,
                  'unique_source_urls':3,'duplicate_url_groups':1,'duplicate_id_groups':1,
                  'groups':[{'url':'https://example.org/a','review_status':gate.PENDING,
                             'reviewer':None,'reviewed_on':None,'variants':a,
                             'identities':[{'origin':v['origin'],'id':v['source']['id'],
                                            'row_index':v['row_index']} for v in a]}]}
        self.write()

    def tearDown(self):self.tmp.cleanup()

    def write(self):
        self.doc['source_files']=[]
        for origin,path in self.paths.items():
            raw=json.dumps({'sources':getattr(self,origin)},sort_keys=True).encode()
            (self.root/path).write_bytes(raw)
            self.doc['source_files'].append({'origin':origin,'path':path,
                'git_blob_sha':gate.git_blob(raw),'count':len(getattr(self,origin))})
        (self.root/'sources/crosswalk.json').write_text(json.dumps(self.doc),encoding='utf-8')

    def check(self):
        return gate.audit_crosswalk(self.root,lambda root,rel:(root/rel).read_bytes())

    def test_positive_docket_requires_human(self):
        r=self.check()
        self.assertEqual((r['raw_source_rows'],r['unique_urls'],
                          r['shared_url_groups'],r['pending_human_groups']),(4,3,1,1))
        self.assertEqual(r['state'],gate.HOLD)
        for k in ('release_authorized','source_or_medical_safety_approved',
                  'merchant_approved','independent_qd_pass'):
            self.assertIs(r[k],False)
        self.assertEqual(r['review_queue'][0]['scope_variants'],2)

    def test_trailing_slash_alias_preserves_distinct_reading(self):
        self.food[0]['url']='https://example.org/a/'
        self.doc['groups'][0]['variants'][1]['source']['url']='https://example.org/a/'
        self.doc['unique_source_urls']=3
        self.doc['duplicate_url_groups']=0
        self.write()
        r=self.check()
        self.assertEqual(r['shared_url_groups'],1)
        self.assertEqual(r['exact_duplicate_url_groups'],0)
        self.assertEqual(r['review_queue'][0]['row_count'],2)
        self.assertIs(r['release_authorized'],False)

    def test_duplicate_json_key_fails(self):
        (self.root/'sources/crosswalk.json').write_bytes(b'{"schema_version":1,"schema_version":1}')
        with self.assertRaisesRegex(ValueError,'duplicate JSON'):self.check()

    def test_missing_crosswalk_group_fails(self):
        self.doc['groups']=[]
        self.write()
        with self.assertRaisesRegex(ValueError,'omitted'):self.check()

    def test_fake_resolution_without_review_fails(self):
        self.doc['groups'][0]['review_status']='resolved'
        self.write()
        with self.assertRaisesRegex(ValueError,'unsubstantiated'):self.check()

    def test_named_resolution_still_holds(self):
        self.doc['groups'][0].update(
            review_status='resolved',
            resolution={'reviewer':'Human','date':'2026-11-09','scope_notes':'Record for review only'})
        self.write()
        r=self.check()
        self.assertEqual(r['pending_human_groups'],0)
        self.assertIs(r['independent_qd_pass'],False)
        self.assertIs(r['release_authorized'],False)

def mutated_evidence(index):
    def run(self):
        v=self.doc['groups'][0]['variants'][index%2]
        k=index//2
        changes=[
            ('supports','invented claim'),('verified_on','2099-01-01'),
            ('publisher','false authority'),('url','https://evil.example'),
            ('id','another-id'),('notes','false reading depth'),
            ('human_link_check',True),('title','false title'),
            ('kind','regulator'),('updated','2099-01-01'),
            ('published','1970-01-01'),('reviewed','2099-01-01'),
            ('safety','approved'),('extra','alien key'),
            ('supports','different source scope'),('id','s2'),
            ('publisher','new publisher'),('claim_depth','full')]
        key,value=changes[k]
        v['source'][key]=value
        self.write()
        with self.assertRaisesRegex(ValueError,'scope changed'):self.check()
    return run

for i in range(36):
    setattr(R235Tests,f'test_mutation_{i:02d}_fails',mutated_evidence(i))

if __name__=='__main__':unittest.main()
