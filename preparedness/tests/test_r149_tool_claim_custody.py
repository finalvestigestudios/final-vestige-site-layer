import copy
import json
from pathlib import Path
import tempfile
import unittest

import importlib.util

# Native repository discovery places tests/ on the import path, not tools/.
TOOL_PATH = Path(__file__).resolve().parents[1] / 'tools' / 'r149_tool_claim_custody.py'
SPEC = importlib.util.spec_from_file_location('r149_tool_claim_custody', TOOL_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
CANDIDATES, Hold = MODULE.CANDIDATES, MODULE.Hold
make_docket, verify = MODULE.make_docket, MODULE.verify

class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.base='proof'
        self.source_ids=[f's{i:02d}' for i in range(60)]
        self.write('sources/register.json', {'sources':[self.row('base-s', 'Base source')]})
        self.write('sources/fragments/start.json', {'sources':[self.row(s, f'Support claim {s}') for s in self.source_ids]})
        self.write('sources/fragments/shelter.json', {'sources':[]})
        self.write('sources/crosswalk.json', {'article_origins':{}})
        self.write('content/tools/demo-tool.meta.json', {'slug':'demo-tool','status':{'publish':'draft'},
          'source_use':{s:f'Author-specific interpretation for {s}' for s in self.source_ids}})
        self.body=' '.join('{{cite:'+s+'}}' for s in self.source_ids)
        self.bodypath=self.root/'content/tools/demo-tool.body.html'
        self.bodypath.write_text(self.body,encoding='utf-8')
        self.docket=make_docket(self.root,candidates={'demo-tool':'start'},expected_tool_count=1)
    def row(self,sid,why):
        return {'id':sid, 'url':f'https://example.org/{sid}', 'supports':why,
          'title':sid, 'publisher':'Test reference', 'verified_on':None,'human_link_check':False}
    def write(self,p,obj):
        f=self.root/p
        f.parent.mkdir(parents=True,exist_ok=True)
        f.write_text(json.dumps(obj),encoding='utf-8')
    def read(self,p):
        return json.loads((self.root/p).read_text())
    def good(self):
        out=verify(self.root,self.docket,expected_tool_count=1)
        self.assertEqual(out['status'],'DRAFT_HOLD')
        self.assertFalse(out['publication_allowed'])
        self.assertEqual(out['currently_unresolved_source_ids'],60)

class Positive(Fixture):
    def test_read_only(self): self.good()
    def test_row_count(self): self.assertEqual(len(self.docket['source_use_rows']),60)
    def test_no_approval(self): self.assertTrue(all(r['review_decision']=='PENDING' for r in self.docket['source_use_rows']))
    def test_source_url(self): self.assertEqual(self.docket['source_use_rows'][0]['literal_url'],'https://example.org/s00')
    def test_order_deterministic(self):
        self.assertEqual(self.docket,make_docket(self.root,candidates={'demo-tool':'start'},expected_tool_count=1))

class Tamper(Fixture):
    pass

def make_mutant(i):
    def test(self):
        d=copy.deepcopy(self.docket)
        d['source_use_rows'][i]['author_specific_use']='UNREVIEWED EDIT'
        with self.assertRaises(Hold): verify(self.root,d,expected_tool_count=1)
    return test
for _i in range(60):
    setattr(Tamper,f'test_prohibit_rewriting_author_claim_{_i:02d}',make_mutant(_i))

class Negative(Fixture):
    def reject(self):
        with self.assertRaises(Hold): verify(self.root,self.docket,expected_tool_count=1)
    def test_dropped_citation(self):
        self.bodypath.write_text(self.body.replace('{{cite:s00}}',''),encoding='utf-8'); self.reject()
    def test_added_citation(self):
        self.bodypath.write_text(self.body+' {{cite:s00}}',encoding='utf-8'); self.reject()
    def test_publish_override(self):
        path='content/tools/demo-tool.meta.json'; d=self.read(path)
        d['status']['publish']='published'; self.write(path,d); self.reject()
    def test_source_note_drift(self):
        path='content/tools/demo-tool.meta.json'; d=self.read(path)
        d['source_use']['s30']='Changed author interpretation'; self.write(path,d); self.reject()
    def test_source_url_redirect(self):
        path='sources/fragments/start.json'; d=self.read(path)
        d['sources'][0]['url']='https://evil.example/link'; self.write(path,d); self.reject()
    def test_source_support_drift(self):
        path='sources/fragments/start.json'; d=self.read(path)
        d['sources'][0]['supports']='Changed support claim'; self.write(path,d); self.reject()
    def test_crosswalk_drift(self):
        self.write('sources/crosswalk.json',{'article_origins':{'demo-tool':'start'}}); self.reject()
    def test_duplicate_origin_id(self):
        path='sources/fragments/start.json'; d=self.read(path)
        d['sources'].append(copy.deepcopy(d['sources'][0])); self.write(path,d); self.reject()
    def test_no_support(self):
        path='sources/fragments/start.json'; d=self.read(path)
        del d['sources'][0]['supports']; self.write(path,d); self.reject()
    def test_source_link_as_file(self):
        path=self.root/'sources/fragments/start.json'; path.unlink(); path.symlink_to(self.root/'sources/register.json'); self.reject()
    def test_safety_forgery(self):
        d=copy.deepcopy(self.docket);d['independent_qd']='PASS'
        with self.assertRaises(Hold): verify(self.root,d,expected_tool_count=1)
    def test_status_forgery(self):
        d=copy.deepcopy(self.docket);d['publication_allowed']=True
        with self.assertRaises(Hold): verify(self.root,d,expected_tool_count=1)
    def test_row_deletion(self):
        d=copy.deepcopy(self.docket);d['source_use_rows'].pop()
        with self.assertRaises(Hold): verify(self.root,d,expected_tool_count=1)
    def test_meta_symlink(self):
        p=self.root/'content/tools/demo-tool.meta.json'; d=p.read_bytes(); p.unlink()
        target=self.root/'original-meta.json';target.write_bytes(d); p.symlink_to(target);self.reject()
    def test_candidate_map_mutation(self):
        d=copy.deepcopy(self.docket);d['candidate_tool_origins']['demo-tool']='shelter'
        with self.assertRaises(Hold): verify(self.root,d,expected_tool_count=1)

if __name__=='__main__': unittest.main()
