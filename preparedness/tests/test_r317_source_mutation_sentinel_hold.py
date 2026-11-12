"""R317 AST-only synthetic fixtures; no canonical-source filesystem mutation."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]/'tools'/'r317_source_mutation_sentinel_hold.py'
spec=importlib.util.spec_from_file_location('r317_sentinel',SOURCE)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class SourceMutationSentinel(unittest.TestCase):
    def chk(self, code): return m.audit_test_text('def test_fixture():\n    '+code.replace('\n','\n    '), 'synthetic.py')
    def test_missing_directory(self):
        with tempfile.TemporaryDirectory() as p:
            self.assertEqual(m.scan_tree(Path(p))['state'],'INVALID_HARD_HOLD')
    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as p:
            (Path(p)/'preparedness/tests').mkdir(parents=True)
            self.assertIn('NO_TESTS_DISCOVERED',m.scan_tree(Path(p))['errors'])
    def test_legacy_pr169_real_source_fixture(self):
        a=self.chk('frag = ROOT / "sources" / "fragments" / "_dup_test.json"\nfrag.write_text("x")\nfrag.unlink()')
        self.assertEqual([x['operation'] for x in a],['write_text','unlink'])
    def test_temporary_fixture_safe(self):
        self.assertFalse(self.chk('sandbox = Path(td) / "preparedness"\nfrag = sandbox / "sources" / "fragments" / "_dup.json"\nfrag.write_text("x")'))
    def test_subsequent_reassignment_safe(self):
        self.assertFalse(self.chk('frag = ROOT / "sources" / "x"\nfrag = Path(td) / "safe.json"\nfrag.write_text("x")'))
    def test_read_only_allowed(self):
        self.assertFalse(self.chk('frag = ROOT / "sources" / "x"\ndata = frag.read_text()'))
    def test_issue_id_not_qa_pass(self):
        self.assertFalse(m.scan_tree(Path(tempfile.mkdtemp()))['independent_qd_pass'])

for op in sorted(m.MUTATORS):
    for area in sorted(m.SOURCE_COMPONENTS):
        def t(self,op=op,area=area):
            code=f'file = ROOT / "{area}" / "frag.json"\nfile.{op}("x")'
            self.assertEqual(len(self.chk(code)),1)
        setattr(SourceMutationSentinel,f'test_{area}_{op}',t)
for name in sorted(m.ROOT_FILES):
    def t(self,name=name):
        self.assertEqual(len(self.chk(f'f = ROOT / "{name}"\nf.write_text("x")')),1)
    setattr(SourceMutationSentinel,'test_rootfile_'+name.replace('.','_'),t)
for spelling in ['w','a','x','r+','wb','ab','x+']:
    def t(self,spelling=spelling):
        self.assertEqual(len(self.chk(f'frag = ROOT / "sources" / "s.json"\nfrag.open("{spelling}")')),1)
    setattr(SourceMutationSentinel,'test_open_'+spelling.replace('+','plus'),t)
for spelling in ['r','rb','rt','']:
    def t(self,spelling=spelling):
        self.assertFalse(self.chk(f'frag = ROOT / "sources" / "s.json"\nfrag.open("{spelling}")'))
    setattr(SourceMutationSentinel,'test_read_open_'+(spelling or 'default'),t)
for expr in ['ROOT / "sources" / "x"','ROOT.joinpath("sources", "x")','(ROOT / "sources").joinpath("x")']:
    def t(self,expr=expr):
        self.assertEqual(len(self.chk(f'f = {expr}\nf.write_bytes(b"x")')),1)
    setattr(SourceMutationSentinel,'test_path_'+str(len(SourceMutationSentinel.__dict__)),t)

if __name__=='__main__': unittest.main()
