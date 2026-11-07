"""Exact-source Playground launcher admission and deliberate negative controls."""
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile, ZIP_DEFLATED

import make_private_playground_launcher as maker
import verify_private_playground_bridge as bridge

SOURCE=Path(__file__).with_name("FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json")

class Admission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.bundle=Path(cls.temp.name)/"bundle.zip"
        maker.package(SOURCE,cls.bundle)
    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def altered(self, mutation):
        with ZipFile(self.bundle) as z:
            files={name:z.read(name) for name in z.namelist()}
        mutation(files)
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/"bad.zip"
            with ZipFile(target,"w",compression=ZIP_DEFLATED) as z:
                for name,body in files.items():
                    z.writestr(name,body)
            with self.assertRaises(ValueError):
                bridge.admit_bundle(target)

    def test_exact_source_and_manifest(self):
        meta,html=bridge.admit_bundle(self.bundle)
        self.assertEqual(meta["git_blob"],bridge.BLOB)
        self.assertEqual(meta["parent"],bridge.PARENT)
        self.assertEqual(meta["chapters"],7)
        self.assertEqual(meta["margins"],72)
        self.assertEqual(meta["focus_links"],5)
        self.assertGreater(len(html),190000)

    def test_launcher_generator_is_pinned_to_current_blueprint(self):
        self.assertEqual(maker.BLOB,bridge.BLOB)
        self.assertEqual(maker.validate(SOURCE.read_bytes()),bridge.BLOB)

    def test_modified_historical_record_rejected(self):
        self.altered(lambda x:x.__setitem__("blueprint.json",x["blueprint.json"].replace(b'fv-margin-strip__item',b'changed-record',1)))

    def test_stale_hash_rejected(self):
        def corrupt(x):
            v=json.loads(x["manifest.json"])
            v["blob_sha1"]="455c6cccbf8a00e6ecc4c2524775010d7ee1762c"
            x["manifest.json"]=json.dumps(v).encode()
        self.altered(corrupt)

    def test_tampered_manifest_sha_rejected(self):
        def corrupt(x):
            v=json.loads(x["manifest.json"])
            v["blueprint_sha256"]="0"*64
            x["manifest.json"]=json.dumps(v).encode()
        self.altered(corrupt)

    def test_tampered_link_rejected(self):
        self.altered(lambda x:x.__setitem__("launch_review.html",x["launch_review.html"].replace(b"#ewog",b"#anVua",1)))

    def test_extra_link_rejected(self):
        self.altered(lambda x:x.__setitem__("launch_review.html",x["launch_review.html"]+b'<a href="https://playground.wordpress.net/#abc">extra</a>'))

    def test_unsafe_script_rejected(self):
        self.altered(lambda x:x.__setitem__("launch_review.html",x["launch_review.html"]+b"<script>void 0</script>"))

    def test_extra_zip_file_rejected(self):
        self.altered(lambda x:x.__setitem__("customers.csv",b"forbidden"))

    def test_wrong_image_format_is_not_accepted(self):
        from verify_integrated_playground import verify_image_bytes
        with self.assertRaises(ValueError):
            verify_image_bytes(b"<html>fake</html>"*300,"WEBP")

if __name__=="__main__":
    unittest.main(verbosity=2)
