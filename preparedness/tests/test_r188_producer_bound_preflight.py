"""R188 wrapper synthetic tests; never native corpus, release, QD or revenue evidence."""
from __future__ import annotations

from importlib import util
from pathlib import Path
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
TOOLS=HERE.parent/'tools'
if not (TOOLS/'r188_producer_code_custody_gate.py').is_file():
    TOOLS=HERE

def load(name):
    spec=util.spec_from_file_location(name,TOOLS/(name+'.py'))
    module=util.module_from_spec(spec);spec.loader.exec_module(module);return module

gate=load('r188_producer_code_custody_gate')
wrapper=load('r188_producer_bound_preflight')


def synthetic_tree(root, state='DRAFT_HARD_HOLD', bad_approvals=False):
    prep=root/'preparedness';tools=prep/'tools';tools.mkdir(parents=True)
    source=(TOOLS/'r188_producer_code_custody_gate.py').read_bytes()
    (tools/'r188_producer_code_custody_gate.py').write_bytes(source)
    paths=['tools/'+f'p{i}.py' for i in range(15)]
    pins={}
    for p in paths:
        data=f'# synthetic {p}\n'.encode();(prep/p).write_bytes(data);pins[p]=gate.git_blob(data)
    code=f"def preflight(repo, timeout):\n    return {{'state':'{state}', 'publication_authorized':{bad_approvals}, 'independent_qd_pass':False,'checks':[]}}\n"
    (tools/'r186_whole_archive_preflight.py').write_text(code)
    return prep,pins


class WrapperAdmission(unittest.TestCase):
    def test_wrapper_reports_hard_hold(self):
        with tempfile.TemporaryDirectory() as d:
            prep,pins=synthetic_tree(Path(d))
            receipt=wrapper.preflight(Path(d),synthetic_pins=pins)
            self.assertEqual(receipt['state'],wrapper.HOLD)
            self.assertTrue(receipt['native_build_verified'])
            self.assertFalse(receipt['publication_authorized'])

    def test_bad_native_receipt_remains_invalid(self):
        with tempfile.TemporaryDirectory() as d:
            _,pins=synthetic_tree(Path(d),wrapper.INVALID)
            receipt=wrapper.preflight(Path(d),synthetic_pins=pins)
            self.assertEqual(receipt['state'],wrapper.INVALID)
            self.assertFalse(receipt['native_build_verified'])

    def test_spurious_release_fails(self):
        with tempfile.TemporaryDirectory() as d:
            _,pins=synthetic_tree(Path(d),bad_approvals=True)
            receipt=wrapper.preflight(Path(d),synthetic_pins=pins)
            self.assertEqual(receipt['state'],wrapper.INVALID)
            self.assertIn('falsely cleared',receipt['blocker'])

    def test_invalid_timeout(self):
        with tempfile.TemporaryDirectory() as d:
            _,pins=synthetic_tree(Path(d))
            for timeout in (0,9,1201,True,'300'):
                with self.subTest(timeout=timeout):
                    self.assertEqual(wrapper.preflight(Path(d),timeout,synthetic_pins=pins)['state'],wrapper.INVALID)

    def test_cli_explicit_hold_exit(self):
        self.assertEqual(wrapper.main(['--repo','/does/not/exist']),2)


def mutation_tests():
    for i in range(15):
        def test(self, i=i):
            with tempfile.TemporaryDirectory() as d:
                prep,pins=synthetic_tree(Path(d))
                target=prep/f'tools/p{i}.py'
                target.write_bytes(target.read_bytes()+b'bad')
                result=wrapper.preflight(Path(d),synthetic_pins=pins)
                self.assertEqual(result['state'],wrapper.INVALID)
                self.assertNotIn('native',result)
                self.assertIn('producer',result['blocker'])
        setattr(WrapperAdmission,'test_tampered_input_%02d'%i,test)
mutation_tests()

if __name__=='__main__':unittest.main()
