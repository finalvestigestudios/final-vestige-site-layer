import json,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Gate(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.gate=subprocess.run(['python',str(ROOT/'qa/release_gate.py')],capture_output=True,text=True)
 def test_hard_hold_exit(self):
  self.assertEqual(self.gate.returncode,2)
  self.assertIn('HARD_HOLD',self.gate.stdout)
 def test_all_preconditions_unverified(self):
  d=json.loads((ROOT/'QA/release_gate_result.json').read_text())
  self.assertTrue(all(v=='MISSING' for v in d['required'].values()))
  self.assertFalse(d['sales_verified'])
if __name__=='__main__':unittest.main(verbosity=2)
