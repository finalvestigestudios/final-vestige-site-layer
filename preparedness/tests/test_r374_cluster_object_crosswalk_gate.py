"""Adversarial synthetic-only tests; canonical source tree is never written."""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve()
MODULE = HERE.parents[1] / 'tools' / 'r374_cluster_object_crosswalk_gate.py'
spec = importlib.util.spec_from_file_location('r374', MODULE)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def fixture():
    names = ['claude/prep-start-bbfeb8','claude/prep-food-ccdc55','claude/prep-health-837444',
             'claude/prep-hist-field-9db767','claude/prep-hist-food-b81f19','claude/prep-hist-home-0e0e38',
             'claude/prep-shelter-5e1e0e','claude/prep-shelter-continuation','claude/prep-shelter-followup-evidence']
    objects=[]
    def row(path):
        blob=(path+'\n').encode(); return dict(path=path,variants=[dict(branch=names[0],sha=g.git_blob_sha(blob),size=len(blob))],decision='IDENTICAL_OR_SINGLE',selected_sha=None)
    for i in range(35):
        slug=f'article-{i:02d}'
        objects.extend([row(f'preparedness/content/articles/{slug}.body.html'),row(f'preparedness/content/articles/{slug}.meta.json')])
    for i in range(7):objects.append(row(f'preparedness/sources/fragments/source-{i}.json'))
    return dict(schema_version=1,repository='finalvestigestudios/final-vestige-site-layer',release_state='DRAFT_HARD_HOLD',
                branch_pins=[dict(branch=n,sha='a'*40) for n in names],objects=objects,article_count=35,conflict_count=0)


class Contract(unittest.TestCase):
    def setUp(self):self.m=fixture()
    def check(self):return g.inspect_manifest(self.m)
    def test_valid_but_unavailable_is_held(self):
        r=self.check(); self.assertEqual(r['issues'],['authentic working tree not supplied']);self.assertFalse(r['publication_approved'])
    def test_complete_synthetic_tree_is_custody_only(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for row in self.m['objects']:
                p=root/row['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((row['path']+'\n').encode())
            r=g.inspect_manifest(self.m,root)
            self.assertEqual(r['status'],'CUSTODY_MATCH_HARD_HOLD');self.assertEqual(r['checked'],77)
            self.assertFalse(r['qualified_safety_approved'])
    def test_mutation_changes_git_identity(self):
        self.assertNotEqual(g.git_blob_sha(b'abc'),g.git_blob_sha(b'abd'))
    def test_refuses_non_draft(self):
        self.m['release_state']='LIVE';self.assertIn('release hold missing',self.check()['issues'])
    def test_refuses_auto_selection(self):
        self.m['objects'][0]['selected_sha']='a'*40;self.assertTrue(any('auto-selected' in x for x in self.check()['issues']))
    def test_two_variants_trigger_review(self):
        r=self.m['objects'][0];r['variants'].append(dict(branch=self.m['branch_pins'][1]['branch'],sha='b'*40,size=101))
        self.assertTrue(any('conflict not held' in x for x in self.check()['issues']))
        r['decision']='REVIEW_REQUIRED';self.m['conflict_count']=1
        self.assertEqual(self.check()['issues'],['authentic working tree not supplied'])
    def test_held_citation_source_fragment_presence(self):
        self.m['objects']=[o for o in self.m['objects'] if 'source-0' not in o['path']]
        self.assertTrue(any('source fragments missing' in x for x in self.check()['issues']))
    def test_nonsource_path_rejected(self):
        self.m['objects'][0]['path']='README.md'
        self.assertTrue(any('unexpected inventory' in x for x in self.check()['issues']))
    def test_missing_local_root_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            r=g.inspect_manifest(self.m,Path(d));self.assertIn('authentic checkout file unavailable: preparedness/content/articles/article-00.body.html',r['issues'])
    def test_cli_without_checkout_exit_2(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'manifest.json';f.write_text(json.dumps(self.m))
            p=subprocess.run([sys.executable,str(MODULE),str(f)],capture_output=True,text=True)
            self.assertEqual(p.returncode,2);self.assertIn('INVALID_HARD_HOLD',p.stdout)


def add_case(name,change,needle):
    def test(self):
        change(self.m)
        self.assertTrue(any(needle in x for x in self.check()['issues']), self.check()['issues'])
    setattr(Contract,'test_reject_'+name,test)

for key in g.RELEASE_KEYS:
    add_case('promotion_'+key,lambda m,k=key:m.__setitem__(k,True),'release approval asserted')
for i,bad in enumerate(['f'*39,'','abc','g'*40,None,'a'*39,'A'*40]):
    add_case('bad_branch_sha_'+str(i),lambda m,v=bad:m['branch_pins'][0].__setitem__('sha',v),'invalid branch pin')
for i,bad in enumerate(['f'*39,'','abc','g'*40,None,'a'*39,'A'*40]):
    add_case('bad_object_sha_'+str(i),lambda m,v=bad:m['objects'][0]['variants'][0].__setitem__('sha',v),'invalid Git object identity')
for i,bad in enumerate([0,-1,None,'5',1.5]):
    add_case('bad_size_'+str(i),lambda m,v=bad:m['objects'][0]['variants'][0].__setitem__('size',v),'invalid Git object identity')
for i,path in enumerate(['/secret','../secret','preparedness/content/articles/../../x','preparedness/tools/evil.py']):
    add_case('path_'+str(i),lambda m,v=path:m['objects'][0].__setitem__('path',v), 'object path' if i<3 else 'unexpected inventory')
add_case('bad_repo',lambda m:m.__setitem__('repository','other/repo'),'repository mismatch')
add_case('bad_schema',lambda m:m.__setitem__('schema_version',2),'invalid manifest schema')
add_case('duplicate_path',lambda m:m['objects'].append(copy.deepcopy(m['objects'][0])),'duplicate or unsafe object path')
add_case('missing_article',lambda m:m['objects'].pop(0),'article/meta coverage mismatch')
add_case('wrong_article_count',lambda m:m.__setitem__('article_count',34),'inventory tallies altered')
add_case('wrong_conflict_count',lambda m:m.__setitem__('conflict_count',1),'inventory tallies altered')
add_case('missing_ref',lambda m:m['branch_pins'].pop(),'expected nine distinct contributor refs')
add_case('dup_ref',lambda m:m['branch_pins'][0].__setitem__('branch',m['branch_pins'][1]['branch']),'expected nine distinct contributor refs')
add_case('bad_ref_name',lambda m:m['branch_pins'][0].__setitem__('branch','unknown'),'contributor branch name mismatch')
add_case('foreign_variant',lambda m:m['objects'][0]['variants'][0].__setitem__('branch','outside/other'),'variant branch mismatch')
add_case('no_variant',lambda m:m['objects'][0].__setitem__('variants',[]),'missing variants')
add_case('bad_decision',lambda m:m['objects'][0].__setitem__('decision','APPROVED'),'variant conflict not held')


if __name__=='__main__':unittest.main()
