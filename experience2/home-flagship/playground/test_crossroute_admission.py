import json,unittest
from pathlib import Path
from zipfile import ZipFile
import io
from crossroute_admission import admit
ROOT=Path(__file__).resolve().parent
C=ROOT.parent/'pr1515/candidate/fv-ex2-official-playground-web-review.zip'
G=ROOT/'focus_gift_guard.js';F=ROOT/'focus_gift_source_20261107.json'
class CrossRoute(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.c=C.read_bytes();cls.g=G.read_bytes();cls.f=F.read_bytes()
 def test_exact_pass_and_hold(self):
  r=admit(self.c,self.g,self.f);self.assertEqual(r['offline_contract'],'PASS');self.assertEqual(r['cross_route_release'],'HOLD')
 def test_modified_bundle_holds(self):
  with self.assertRaisesRegex(ValueError,'protected package'):admit(self.c+b'0',self.g,self.f)
 def test_modified_guard_holds(self):
  with self.assertRaisesRegex(ValueError,'guard drift'):admit(self.c,self.g+b'0',self.f)
 def test_modified_original_holds(self):
  f=json.loads(self.f);f['script']+=' ';x=json.dumps(f).encode()
  with self.assertRaisesRegex(ValueError,'script drift'):admit(self.c,self.g,x)
 def test_wrong_page_holds(self):
  f=json.loads(self.f);f['page_id']=6
  with self.assertRaisesRegex(ValueError,'script drift'):admit(self.c,self.g,json.dumps(f).encode())
 def test_unsafe_guard_rejected_by_custody(self):
  with self.assertRaisesRegex(ValueError,'guard drift'):admit(self.c,self.g+b'window.location.search',self.f)
if __name__=='__main__':unittest.main()
