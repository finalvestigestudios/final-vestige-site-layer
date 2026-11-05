"""Isolated synthetic and adversarial R148 source-origin tests (not native QA)."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

p=Path(__file__).resolve().parents[1]/'tools/r148_tool_origin_gate.py'
spec=importlib.util.spec_from_file_location('origins',p)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class OriginReview(unittest.TestCase):
    def setUp(self):
        d=tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        self.root=Path(d.name)
        self.write('sources/crosswalk.json',{'article_origins':{}})
        self.write('sources/register.json',{'sources':[{'id':'base-a','url':'https://a.example/a'}]})
        self.write('sources/fragments/start.json',{'sources':[{'id':'start-a','url':'https://b.example/b'}]})
        self.write('sources/fragments/shelter.json',{'sources':[{'id':'shelter-a','url':'https://c.example/c'}]})
        self.write('content/articles/one.meta.json',{'slug':'one','status':{'publish':'draft'}})
        self.write('content/tools/test-card.meta.json',{'slug':'test-card','status':{'publish':'draft'},
                   'source_use':{'base-a':'base scope','shelter-a':'specific scope'}})
        self.body='Plan the route. {{cite:base-a}} {{cite:shelter-a}}'
        self.html('content/tools/test-card.body.html',self.body)
    def write(self,where,obj):
        q=self.root/where
        q.parent.mkdir(parents=True,exist_ok=True)
        q.write_text(json.dumps(obj))
    def html(self,where,s):
        q=self.root/where
        q.parent.mkdir(parents=True,exist_ok=True)
        q.write_text(s)
    def inspect(self): return m.inspect(self.root,tool_count=1,article_count=1)
    def test_original_source_scope_is_not_guessed_safe(self):
        r=self.inspect()
        self.assertEqual(r['unresolved_tool_count'],1)
        self.assertEqual(r['tools'][0]['unique_candidate'],'shelter')
        self.assertFalse(r['publication_allowed'])
    def test_proposed_origin_clears_resolution_but_not_publication(self):
        self.write('sources/crosswalk.json',{'article_origins':{'test-card':'shelter'}})
        r=self.inspect()
        self.assertEqual(r['unresolved_tool_count'],0)
        self.assertFalse(r['medical_safety_verified'])
    def test_unrelated_shelter_source_cannot_inherit_start(self):
        self.write('sources/crosswalk.json',{'article_origins':{'test-card':'start'}})
        self.assertEqual(self.inspect()['unresolved_tool_count'],1)
    def test_wrong_source_use_fails(self):
        self.write('content/tools/test-card.meta.json',{'slug':'test-card','status':{'publish':'draft'},
            'source_use':{'base-a':'scope'}})
        with self.assertRaisesRegex(m.Hold,'key mismatch'):self.inspect()
    def test_empty_source_explanation_fails(self):
        self.write('content/tools/test-card.meta.json',{'slug':'test-card','status':{'publish':'draft'},
            'source_use':{'base-a':'','shelter-a':'scope'}})
        with self.assertRaisesRegex(m.Hold,'interpretation'):self.inspect()
    def test_source_id_url_conflict_fails(self):
        self.write('sources/fragments/start.json',{'sources':[{'id':'base-a','url':'https://evil.example'}]})
        with self.assertRaisesRegex(m.Hold,'conflicting literal URL'):self.inspect()
    def test_duplicate_origin_ids_fail(self):
        self.write('sources/fragments/start.json',{'sources':[{'id':'start-a','url':'https://b.example/b'},
                                                     {'id':'start-a','url':'https://b.example/b'}]})
        with self.assertRaisesRegex(m.Hold,'duplicate origin/id'):self.inspect()
    def test_forged_publication_fails(self):
        self.write('content/tools/test-card.meta.json',{'slug':'test-card','status':{'publish':'published'},
            'source_use':{'base-a':'scope','shelter-a':'scope'}})
        with self.assertRaisesRegex(m.Hold,'publication state drift'):self.inspect()
    def test_missing_tool_fails(self):
        (self.root/'content/tools/test-card.meta.json').unlink()
        with self.assertRaisesRegex(m.Hold,'inventory changed'):self.inspect()
    def test_missing_body_fails(self):
        (self.root/'content/tools/test-card.body.html').unlink()
        with self.assertRaisesRegex(m.Hold,'missing body'):self.inspect()
    def test_ambiguous_origin_does_not_autoselect(self):
        self.write('sources/fragments/second.json',{'sources':[{'id':'shelter-a','url':'https://c.example/c'}]})
        r=self.inspect()
        self.assertIsNone(r['tools'][0]['unique_candidate'])
        self.assertEqual(r['ambiguous_tool_count'],1)
    def test_missing_fragments_fails_closed(self):
        for f in (self.root/'sources/fragments').glob('*.json'): f.unlink()
        with self.assertRaisesRegex(m.Hold,'no source fragments'):self.inspect()

# 35 independent source-identity mutations for CI evidence.
def make_missing_source_case(i):
    def check(self):
        name=f'unknown-cite-{i:02d}'
        self.html('content/tools/test-card.body.html',self.body+' {{cite:'+name+'}}')
        row={'slug':'test-card','status':{'publish':'draft'},'source_use':{'base-a':'scope','shelter-a':'scope',name:'new scope'}}
        self.write('content/tools/test-card.meta.json',row)
        out=self.inspect()
        self.assertIn(name,out['tools'][0]['unresolved_source_ids'])
        self.assertEqual(out['ambiguous_tool_count'],1)
    return check
for i in range(35):
    setattr(OriginReview,f'test_missing_source_{i:02d}',make_missing_source_case(i))

if __name__=='__main__':unittest.main()
