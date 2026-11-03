#!/usr/bin/env python3
"""Source-exact R94 checks with actual inherited R92/R93 staging builders."""
import importlib.util,json,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
TOOL=ROOT/"experience2/evidence-atlas/tools/build_curated_atlas_r94.py"
spec=importlib.util.spec_from_file_location("r94",TOOL)
r94=importlib.util.module_from_spec(spec);spec.loader.exec_module(r94)
class AtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=tempfile.TemporaryDirectory();root=Path(cls.base.name)
        subprocess.run([sys.executable,str(ROOT/"experience2/evidence-atlas/tools/build_reciprocal_routes_r92.py"),str(root/"r92")],check=True,stdout=subprocess.DEVNULL)
        subprocess.run([sys.executable,str(ROOT/"experience2/evidence-atlas/tools/build_source_passports_r93.py"),"--src",str(root/"r92"),"--out",str(root/"r93")],check=True,stdout=subprocess.DEVNULL)
        cls.original=root/"r93"
    @classmethod
    def tearDownClass(cls):cls.base.cleanup()
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.src=self.root/"src"
        shutil.copytree(self.original,self.src)
    def change(self,name,fn,rehash=False):
        p=self.src/name;d=json.loads(p.read_text());fn(d);p.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n")
        if rehash:
            q=self.src/"R93_PASSPORT_RECEIPT.json";receipt=json.loads(q.read_text())
            receipt["files"][name]=r94.sha(p)
            q.write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
    def runbuild(self):return r94.build(self.src,self.root/"out")
    def test_real_six_nasa_sources(self):
        a=self.runbuild();s=(self.root/"out/R94_CURATED_ATLAS.html").read_text()
        self.assertEqual(a["source_count"],6)
        self.assertEqual(s.count('class="card"'),6)
        self.assertEqual(s.count("https://www.nasa.gov/image-detail/"),12)
        self.assertEqual(s.count("INDIVIDUAL REVIEW REQUIRED"),6)
        self.assertNotIn("<img",s);self.assertNotIn("<iframe",s)
    def test_same_zip_twice(self):
        r94.build(self.src,self.root/"a",self.root/"a.zip")
        r94.build(self.src,self.root/"b",self.root/"b.zip")
        self.assertEqual((self.root/"a.zip").read_bytes(),(self.root/"b.zip").read_bytes())
    def test_tampered_inherited_source(self):
        (self.src/"R88_READING_ROOM.html").write_text("WRONG")
        with self.assertRaisesRegex(ValueError,"MISMATCH"):self.runbuild()
    def test_tampered_passport(self):
        (self.src/"R93_SOURCE_PASSPORTS.html").write_text("WRONG")
        with self.assertRaisesRegex(ValueError,"MISMATCH"):self.runbuild()
    def test_swapped_nasa_urls_even_if_rehashed(self):
        def swap(d):
            x=d["records"];x[1]["url"],x[2]["url"]=x[2]["url"],x[1]["url"]
        self.change("R93_SOURCE_PASSPORTS.json",swap,True)
        with self.assertRaisesRegex(ValueError,"MISMATCH"):self.runbuild()
    def test_falsely_cleared_rights_even_if_rehashed(self):
        self.change("R93_SOURCE_PASSPORTS.json",lambda d:d["records"][0].__setitem__("rights","APPROVED"),True)
        with self.assertRaisesRegex(ValueError,"MISMATCH"):self.runbuild()
    def test_invented_crew_day(self):
        self.change("R93_SOURCE_PASSPORTS.json",lambda d:d["records"][0].__setitem__("date","January 27, 1967"),True)
        with self.assertRaisesRegex(ValueError,"MONTH_ONLY"):self.runbuild()
    def test_crew_provisional_misrepresented(self):
        self.change("R93_SOURCE_PASSPORTS.json",lambda d:d["records"][0].__setitem__("provisional",False),True)
        with self.assertRaisesRegex(ValueError,"MISMATCH"):self.runbuild()
    def test_changed_tribute_date(self):
        self.change("R93_SOURCE_PASSPORTS.json",lambda d:d["records"][3].__setitem__("date","January 25, 2017"),True)
        with self.assertRaisesRegex(ValueError,"TRIBUTE"):self.runbuild()
    def test_missing_record(self):
        self.change("R93_SOURCE_PASSPORTS.json",lambda d:d["records"].pop(),True)
        with self.assertRaisesRegex(ValueError,"REGISTER"):self.runbuild()
    def test_false_release_gate(self):
        self.change("R93_PASSPORT_RECEIPT.json",lambda d:d.__setitem__("publication_approved",True))
        with self.assertRaisesRegex(ValueError,"CUSTODY"):self.runbuild()
    def test_false_image_rights(self):
        self.change("R85_RIGHTS_RECEIPT.json",lambda d:d.__setitem__("rights_cleared",6))
        with self.assertRaisesRegex(ValueError,"CUSTODY"):self.runbuild()
    def test_new_image_asset_rejected(self):
        (self.src/"unlicensed.png").write_bytes(b"image")
        with self.assertRaisesRegex(ValueError,"UNREVIEWED"):self.runbuild()
    def test_output_overwrite_rejected(self):
        p=self.root/"out";p.mkdir();(p/"old").write_text("x")
        with self.assertRaisesRegex(ValueError,"NONEMPTY"):self.runbuild()
if __name__=="__main__":unittest.main()
