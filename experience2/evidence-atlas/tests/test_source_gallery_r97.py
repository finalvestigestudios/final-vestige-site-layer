#!/usr/bin/env python3
"""R97 adversarial source, rights and deterministic artifact tests."""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
TOOLS=ROOT/"experience2/evidence-atlas/tools"
spec=importlib.util.spec_from_file_location("r97_gallery",TOOLS/"build_source_gallery_r97.py")
r97=importlib.util.module_from_spec(spec)
spec.loader.exec_module(r97)

class GalleryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work=tempfile.TemporaryDirectory()
        t=Path(cls.work.name)
        subprocess.run([sys.executable,str(TOOLS/"build_reciprocal_routes_r92.py"),str(t/"r92")],check=True,capture_output=True)
        subprocess.run([sys.executable,str(TOOLS/"build_source_passports_r93.py"),"--src",str(t/"r92"),"--out",str(t/"r93")],check=True,capture_output=True)
        subprocess.run([sys.executable,str(TOOLS/"build_curated_atlas_r94.py"),"--src",str(t/"r93"),"--out",str(t/"r94")],check=True,capture_output=True)
        cls.source=t/"r94"

    @classmethod
    def tearDownClass(cls):
        cls.work.cleanup()

    def copy(self):
        t=tempfile.TemporaryDirectory()
        p=Path(t.name)/"input"
        shutil.copytree(self.source,p)
        return t,p

    def test_source_contract(self):
        rows,files=r97.load(self.source)
        self.assertEqual(len(rows),6)
        self.assertEqual(len(files),25)
        self.assertEqual(sum(x["provisional"] for x in rows),1)

    def test_no_unreviewed_media_or_geography(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"export"
            receipt=r97.build(self.source,p)
            self.assertEqual(len(receipt["files"]),28)
            self.assertEqual(receipt["photo_rights_cleared"],0)
            self.assertEqual(receipt["geo_pins"],0)
            self.assertEqual(receipt["inferred_edges"],0)
            self.assertEqual(receipt["images_embedded"],0)
            h=(p/"R97_SOURCE_GALLERY.html").read_text()
            self.assertEqual(h.count('class="card"'),6)
            self.assertEqual(h.count("ARCHIVAL IMAGE WITHHELD"),6)
            self.assertEqual(h.count("data-compare-controls hidden"),7)
            for item in ("<img","<iframe","<video","<canvas"):
                self.assertNotIn(item,h)

    def test_twice_built_identical_zip_and_sha(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            r97.build(self.source,p/"a",p/"a.zip")
            r97.build(self.source,p/"b",p/"b.zip")
            self.assertEqual((p/"a.zip").read_bytes(),(p/"b.zip").read_bytes())
            receipt=json.loads((p/"a"/"R97_GALLERY_RECEIPT.json").read_text())
            for name,h in receipt["files"].items():
                self.assertEqual(r97.sha(p/"a"/name),h)

    def test_extra_js_fails_closed(self):
        t,p=self.copy()
        try:
            (p/"unreviewed.js").write_text("alert('unsafe')")
            with self.assertRaisesRegex(ValueError,"R97_UNREVIEWED_INPUT"):
                r97.load(p)
        finally:t.cleanup()

    def test_hash_changed_html_fails_closed(self):
        t,p=self.copy()
        try:
            f=p/"R94_CURATED_ATLAS.html";f.write_text(f.read_text()+"<img>")
            with self.assertRaisesRegex(ValueError,"R97_SHA_MISMATCH"):
                r97.load(p)
        finally:t.cleanup()

    def test_falsely_cleared_rights_fails_closed(self):
        t,p=self.copy()
        try:
            f=p/"R94_ATLAS_RECEIPT.json";v=json.loads(f.read_text())
            v["photo_rights_cleared"]=1;f.write_text(json.dumps(v))
            with self.assertRaisesRegex(ValueError,"R97_RELEASE_GATE"):
                r97.load(p)
        finally:t.cleanup()

    def test_forged_crew_day_even_if_receipt_updated_fails(self):
        t,p=self.copy()
        try:
            f=p/"R93_SOURCE_PASSPORTS.json";v=json.loads(f.read_text())
            v["records"][0]["date"]="January 27, 1967"
            f.write_text(json.dumps(v))
            receipt=p/"R94_ATLAS_RECEIPT.json";x=json.loads(receipt.read_text())
            x["files"][f.name]=r97.sha(f);receipt.write_text(json.dumps(x))
            with self.assertRaisesRegex(ValueError,"R97_INVENTED_CREW_DAY"):
                r97.load(p)
        finally:t.cleanup()

    def test_forged_clearance_even_if_receipt_updated_fails(self):
        t,p=self.copy()
        try:
            f=p/"R93_SOURCE_PASSPORTS.json";v=json.loads(f.read_text())
            v["records"][0]["rights"]="CLEARED";f.write_text(json.dumps(v))
            receipt=p/"R94_ATLAS_RECEIPT.json";x=json.loads(receipt.read_text())
            x["files"][f.name]=r97.sha(f);receipt.write_text(json.dumps(x))
            with self.assertRaisesRegex(ValueError,"R97_SOURCE_BINDING"):
                r97.load(p)
        finally:t.cleanup()

    def test_nonempty_output_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);(p/"old").write_text("existing")
            with self.assertRaisesRegex(ValueError,"R97_NONEMPTY_OUTPUT"):
                r97.build(self.source,p)

if __name__=="__main__":
    unittest.main()
