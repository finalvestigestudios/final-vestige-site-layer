import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from stage_firstparty_hero_png_v1 import plan, stage, validate_manifest


class HeroBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((Path(__file__).parent / 'firstparty_hero5_20261105.json').read_text())

    def test_01_manifest_and_actual_total(self):
        self.assertEqual(plan(self.manifest)['total_original_stored_bytes'], 13267538)

    def test_02_all_hold(self):
        self.assertTrue(all(a['derivative_permission']['status']=='hold' for a in self.manifest['assets']))

    def test_03_reject_false_browser_status(self):
        doc = json.loads(json.dumps(self.manifest)); doc['assets'][0]['browser_http_status'] = 404
        with self.assertRaises(ValueError): validate_manifest(doc)

    def test_04_reject_external_source(self):
        doc = json.loads(json.dumps(self.manifest)); doc['assets'][0]['source_url'] = 'https://images.example.com/foo.png'
        with self.assertRaises(ValueError): validate_manifest(doc)

    def test_05_reject_duplicate_media(self):
        doc = json.loads(json.dumps(self.manifest)); doc['assets'][1]['post_id'] = 34; doc['assets'][1]['media_id'] = 39
        with self.assertRaises(ValueError): validate_manifest(doc)

    def test_06_reject_false_responsive_variants(self):
        doc = json.loads(json.dumps(self.manifest)); doc['assets'][0]['registered_subsizes'] = 1
        with self.assertRaises(ValueError): validate_manifest(doc)

    def test_07_reject_unapproved_clearance_evidence(self):
        doc = json.loads(json.dumps(self.manifest)); doc['assets'][0]['derivative_permission']['approved_by'] = 'invented'
        with self.assertRaises(ValueError): validate_manifest(doc)

    def test_08_reject_wrong_geometry(self):
        doc = json.loads(json.dumps(self.manifest)); doc['assets'][0]['target_height'] = 541
        with self.assertRaises(ValueError): validate_manifest(doc)

    def test_09_fail_closed_without_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'HOLD'):
                stage(self.manifest, 39, tmp+'/bogus.png', tmp)

    def test_10_approved_synthetic_staging_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); source_dir = base / 'input'; outdir=base/'output'
            source_dir.mkdir(); outdir.mkdir()
            row=self.manifest['assets'][0]
            path=source_dir/Path(row['source_url']).name
            im=Image.new('RGB',(1672,941),(90,140,210))
            output=io.BytesIO(); im.save(output, format='PNG', compress_level=0)
            data=output.getvalue(); path.write_bytes(data)
            fixture=json.loads(json.dumps(self.manifest)); a=fixture['assets'][0]
            a['original_bytes']=len(data)
            a['approved_source_sha256']=hashlib.sha256(data).hexdigest()
            a['derivative_permission']={'status':'approved','approved_by':'fixture-only','evidence':'synthetic test image'}
            # The synthetic source must still exceed 1.5MiB to exercise guards.
            self.assertGreater(len(data),1572864)
            result=stage(fixture,39,path,outdir)
            self.assertEqual(result['derivative_dimensions'],[960,540])
            self.assertEqual(result['editorial_visual_qa'],'HOLD')
            self.assertLess(result['derivative_bytes'],result['original_bytes'])
            with self.assertRaises(FileExistsError): stage(fixture,39,path,outdir)
            path.write_bytes(data[:-1]+b'x')
            with self.assertRaisesRegex(ValueError,'SHA-256 mismatch'):
                stage(fixture,39,path,outdir)


if __name__=='__main__':
    unittest.main()
