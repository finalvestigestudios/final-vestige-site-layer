"""R282 three-snapshot lineage tests; entirely synthetic, no repository writes."""
import copy
import importlib.util
import json
import tempfile
import subprocess
import sys
import unittest
from pathlib import Path

MOD=Path(__file__).resolve().parents[1]/'tools/r282_evidence_lineage_hold.py'
spec=importlib.util.spec_from_file_location('r282_evidence_lineage_hold',MOD)
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)

def oid(i):return '%040x' % i

def fixture():
    articles=[];entries=[];locks=[]
    for n in range(1,36):
        slug='article-%02d'%n
        oldbody,oldmeta=oid(1000+n),oid(2000+n)
        newbody=oid(3000+n) if n<=14 else oldbody
        newmeta=oid(4000+n) if 6<=n<=17 else oldmeta
        lockbody=oid(5000+n) if n%5==0 else oldbody
        lockmeta=oid(6000+n) if n%6==0 else oldmeta
        original_origin='start'
        history_origin='base' if n<=6 else 'start'
        articles.append(dict(n=n,slug=slug,route=f'/preparedness/{slug}/',source_cluster=original_origin,
                             body_oid=oldbody,body_bytes=100+n,meta_oid=oldmeta,meta_bytes=80+n))
        entries.extend([dict(path=f'content/articles/{slug}.body.html',role='article_body',sha=newbody,size=110+n),
                        dict(path=f'content/articles/{slug}.meta.json',role='article_meta',sha=newmeta,size=90+n)])
        locks.append(dict(slug=slug,origin=history_origin,
             body=dict(path=f'preparedness/content/articles/{slug}.body.html',git_blob_sha=lockbody,bytes=100+n),
             metadata=dict(path=f'preparedness/content/articles/{slug}.meta.json',git_blob_sha=lockmeta,bytes=80+n)))
    for n in range(1,7):
        entries += [dict(path=f'content/tools/tool-{n}.body.html',role='tool_body',sha=oid(7000+n),size=300),
                    dict(path=f'content/tools/tool-{n}.meta.json',role='tool_meta',sha=oid(8000+n),size=90)]
    for n in range(14):
        entries.append(dict(path=f'extra/{n}',role='source_origin' if n<8 else 'misc',sha=oid(9000+n),size=100))
    assert len(entries)==96
    locks.append(dict(slug='water-planner',origin='base',
       body=dict(path='preparedness/content/tools/water-planner.body.html',git_blob_sha=oid(13001),bytes=500),
       metadata=dict(path='preparedness/content/tools/water-planner.meta.json',git_blob_sha=oid(13002),bytes=200)))
    return (dict(artifact_count=35,state=g.HOLD,articles=articles),
            dict(schema='fv-r276-all-slate-identity-v1',state=g.HOLD,entries=entries,
                 source_review={'shared_url_groups':32,'duplicate_id_groups':15,'held_occurrences':3}),
            dict(longform_article_count=35,local_tool_count=1,records=locks))

class ThreeWay(unittest.TestCase):
    def setUp(self):self.o,self.i,self.l=fixture()
    def test_baseline_hold(self):
        d=g.derive(self.o,self.i,self.l)
        self.assertEqual((d['aggregates']['r200_integrated_article_differences'],d['aggregates']['source_origin_differences']),(17,6))
        self.assertEqual(len(d['articles']),35)
        self.assertFalse(d['publication_authorized']);self.assertFalse(d['independent_qd_pass'])
    def test_semantic_determinism(self):
        self.assertEqual(g.derive(*fixture()),g.derive(*fixture()))
    def test_order_independent(self):
        a=g.derive(self.o,self.i,self.l)
        self.o['articles'].reverse();self.l['records'].reverse();self.i['entries'].reverse()
        self.assertEqual(a,g.derive(self.o,self.i,self.l))
    def test_lineage_all_five_categories(self):
        cases=[('x','x','x','all_equal'),('x','x','y','original_integrated_equal'),
               ('x','y','x','original_lock_equal'),('y','x','x','integrated_lock_equal'),('x','y','z','all_distinct')]
        for a,b,c,expected in cases:self.assertEqual(g.lineage(a,b,c),expected)
    def test_lock_differs_from_frozen_origin_flagged(self):
        d=g.derive(self.o,self.i,self.l)
        self.assertTrue(d['articles'][0]['origin_differs'])
        self.assertEqual(d['articles'][0]['evidence_lock_origin'],'base')
    def test_extra_tool_is_not_approved(self):
        self.assertIs(g.derive(self.o,self.i,self.l)['historical_lock_extra_tool']['not_an_authorized_offer'],True)
    def test_bad_json_duplicate_key(self):
        with self.assertRaisesRegex(ValueError,'duplicate JSON key'):g.strict_json(b'{"x":1,"x":2}')
    def test_bad_json_nonfinite(self):
        with self.assertRaisesRegex(ValueError,'nonfinite'):g.strict_json(b'{"x":NaN}')
    def test_missing_pinned_checkout_invalid(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(g.audit(td)['state'],g.INVALID)
    def test_cli_invalid_checkout_exit_three(self):
        with tempfile.TemporaryDirectory() as td:
            run=subprocess.run([sys.executable,str(MOD),'--root',td],capture_output=True,text=True)
            self.assertEqual(run.returncode,3)
            self.assertEqual(json.loads(run.stdout)['state'],g.INVALID)
    def test_fake_sha_refuses(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'data.json';p.write_text('{}')
            with self.assertRaisesRegex(ValueError,'Git identity mismatch'):
                g.read_pinned(td,'data.json','0'*40)
    def test_pinned_symlink_refuses(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'data.json').symlink_to('/etc/hosts')
            with self.assertRaisesRegex(ValueError,'symlinked'):g.read_pinned(root,'data.json','0'*40)
    def test_pinned_traversal_refuses(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,'unsafe path'):g.read_pinned(td,'../x','0'*40)
    def test_pinned_parent_symlink_refuses(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'alias').symlink_to(root,target_is_directory=True)
            with self.assertRaisesRegex(ValueError,'symlinked'):g.read_pinned(root,'alias/thing.json','0'*40)

BAD_MUTATIONS={
 'missing_article':lambda o,i,l:o['articles'].pop(),
 'duplicate_article_number':lambda o,i,l:o['articles'][1].__setitem__('n',1),
 'duplicate_article_slug':lambda o,i,l:o['articles'][1].__setitem__('slug','article-01'),
 'duplicate_article_route':lambda o,i,l:o['articles'][1].__setitem__('route',o['articles'][0]['route']),
 'changed_article_route':lambda o,i,l:o['articles'][1].__setitem__('route','/preparedness/other/'),
 'article_count':lambda o,i,l:o.__setitem__('artifact_count',34),
 'source_state':lambda o,i,l:o.__setitem__('state','APPROVED'),
 'integration_state':lambda o,i,l:i.__setitem__('state','LIVE'),
 'integration_schema':lambda o,i,l:i.__setitem__('schema','fake'),
 'citation_shared_groups':lambda o,i,l:i['source_review'].__setitem__('shared_url_groups',31),
 'citation_duplicate_ids':lambda o,i,l:i['source_review'].__setitem__('duplicate_id_groups',14),
 'citation_held_occurrences':lambda o,i,l:i['source_review'].__setitem__('held_occurrences',2),
 'missing_source_review':lambda o,i,l:i.pop('source_review'),
 'missing_original_body_sha':lambda o,i,l:o['articles'][0].pop('body_oid'),
 'fake_original_body_sha':lambda o,i,l:o['articles'][0].__setitem__('body_oid','notsha'),
 'old_body_size_boolean':lambda o,i,l:o['articles'][0].__setitem__('body_bytes',True),
 'old_body_size_zero':lambda o,i,l:o['articles'][0].__setitem__('body_bytes',0),
 'wrong_integrated_body_role':lambda o,i,l:i['entries'][0].__setitem__('role','approval'),
 'wrong_integrated_meta_role':lambda o,i,l:i['entries'][1].__setitem__('role','approval'),
 'duplicate_integrated_path':lambda o,i,l:i['entries'][1].__setitem__('path',i['entries'][0]['path']),
 'missing_integrated':lambda o,i,l:i['entries'].pop(),
 'short_integrated':lambda o,i,l:i['entries'][0].__setitem__('size',0),
 'float_integrated_bytes':lambda o,i,l:i['entries'][0].__setitem__('size',1.5),
 'uppercase_integrated_sha':lambda o,i,l:i['entries'][0].__setitem__('sha','A'*40),
 'missing_lock_record':lambda o,i,l:l['records'].pop(),
 'lost_longform':lambda o,i,l:l.__setitem__('longform_article_count',34),
 'lost_tool_count':lambda o,i,l:l.__setitem__('local_tool_count',0),
 'historical_tool_removed':lambda o,i,l:l['records'][-1].__setitem__('slug','other-tool'),
 'historical_wrong_path':lambda o,i,l:l['records'][0]['body'].__setitem__('path','preparedness/content/articles/other.body.html'),
 'historical_wrong_meta_path':lambda o,i,l:l['records'][0]['metadata'].__setitem__('path','bad'),
 'historical_sha_malformed':lambda o,i,l:l['records'][0]['body'].__setitem__('git_blob_sha','XYZ'),
 'historical_bytes_bad':lambda o,i,l:l['records'][0]['body'].__setitem__('bytes',True),
 'duplicate_history_slug':lambda o,i,l:l['records'][1].__setitem__('slug','article-01'),
 'unrecorded_new_change':lambda o,i,l:i['entries'][30].__setitem__('sha',oid(999999)),
 'altered_historical_origin':lambda o,i,l:l['records'][7].__setitem__('origin','base'),
 'added_historical_row':lambda o,i,l:l['records'].append(copy.deepcopy(l['records'][0])),
 'missing_history_meta':lambda o,i,l:l['records'][0].pop('metadata'),
 'missing_original_meta':lambda o,i,l:o['articles'][0].pop('meta_oid'),
 'changed_original_meta_bytes':lambda o,i,l:o['articles'][0].__setitem__('meta_bytes',-5),
 'canonical_route_external':lambda o,i,l:o['articles'][0].__setitem__('route','https://example.com/preparedness/'),
 'citation_wrong_schema':lambda o,i,l:i.__setitem__('source_review',{}),
 'shift_original_count':lambda o,i,l:o['articles'][0].__setitem__('n',36),
}

def add_negative(name, mut):
    def fn(self):
        mut(self.o,self.i,self.l)
        with self.assertRaises((ValueError,KeyError,IndexError,TypeError,AttributeError)):
            g.derive(self.o,self.i,self.l)
    fn.__name__='test_reject_'+name
    return fn
for name,mutation in BAD_MUTATIONS.items():setattr(ThreeWay,'test_reject_'+name,add_negative(name,mutation))

if __name__=='__main__':unittest.main(verbosity=2)
