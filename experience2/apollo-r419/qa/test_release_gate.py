import importlib.util,unittest,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('rg',ROOT/'qa/release_gate.py');rg=importlib.util.module_from_spec(spec);spec.loader.exec_module(rg)
class ReleaseHold(unittest.TestCase):
    def test_hard_hold(self):self.assertEqual(rg.result()['decision'],'HOLD')
    def test_exact_code(self):self.assertEqual(rg.result()['exit_code'],2)
    def test_missing_axe_and_merchant(self):
        b=' '.join(rg.result()['blocks']);self.assertIn('axe-core',b);self.assertIn('merchant SKU',b)
if __name__=='__main__':unittest.main(verbosity=2)
