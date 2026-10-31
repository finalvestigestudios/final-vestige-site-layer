"""Native Python/Pillow offline test fixtures; never use site or archive images."""
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from prepare_hero_derivatives import prepare_one, run, sha256


class HeroBuilderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'originals'
        self.root.mkdir()
        self.out = Path(self.tmp.name) / 'staged'
        self.row = dict(media_id=39, filename='synthetic.png', post_id=34,
                        source_url='https://finalvestige.com/wp-content/uploads/test.png',
                        width=1200, height=600, target_width=960, target_height=480,
                        original_bytes=0)
        im = Image.effect_noise((1200,600), 30).convert('RGB')
        im.save(self.root/'synthetic.png')
        raw=(self.root/'synthetic.png').read_bytes()
        self.row['original_bytes']=len(raw)
        self.approval=dict(media_id=39,original_sha256=sha256(raw),
                           source_url=self.row['source_url'], reviewer='Test fixture only',
                           rights_basis='original_work_owned', rights_evidence='generated fixture',
                           credit_text='Synthetic test art', reviewed_on='2026-10-31',
                           visual_identity_reviewed=True,no_wordpress_write=True)

    def test_image_encodes_and_no_upscaling(self):
        b,r=prepare_one(self.row,self.approval,self.root)
        self.assertIsNotNone(b)
        self.assertEqual(r['status'],'STAGED_LOCAL_CANDIDATE_NOT_PUBLISHED')
        self.assertEqual([r['target_width_px'],r['target_height_px']],[960,480])
        self.assertIsNone(r['visitor_transfer_bytes'])
        self.assertFalse(r['wordpress_upload_authorized'])
        with Image.open(io.BytesIO(b)) as img:
            self.assertEqual((img.format,img.size),('WEBP',(960,480)))

    def test_hash_mismatch_rejected(self):
        a={**self.approval,'original_sha256':'0'*64}
        with self.assertRaisesRegex(ValueError,'original_hash_mismatch'):
            prepare_one(self.row,a,self.root)

    def test_rights_not_established_rejected(self):
        a={**self.approval,'rights_basis':'unknown'}
        with self.assertRaisesRegex(ValueError,'rights_not_established'):
            prepare_one(self.row,a,self.root)

    def test_wrong_source_url_rejected(self):
        a={**self.approval,'source_url':'https://other.example/photo.png'}
        with self.assertRaisesRegex(ValueError,'source_url_mismatch'):
            prepare_one(self.row,a,self.root)

    def test_visual_review_required(self):
        a={**self.approval,'visual_identity_reviewed':False}
        with self.assertRaisesRegex(ValueError,'visual_identity_not_reviewed'):
            prepare_one(self.row,a,self.root)

    def test_unapproved_wordpress_write_rejected(self):
        a={**self.approval,'no_wordpress_write':False}
        with self.assertRaisesRegex(ValueError,'production_write_guard_missing'):
            prepare_one(self.row,a,self.root)

    def test_modified_pixels_with_old_hash_rejected(self):
        with (self.root/'synthetic.png').open('ab') as fh:
            fh.write(b'suspicious trailing bytes')
        with self.assertRaisesRegex(ValueError,'original_hash_mismatch'):
            prepare_one(self.row,self.approval,self.root)

    def test_wrong_dimensions_rejected(self):
        a={**self.row,'width':100}
        with self.assertRaisesRegex(ValueError,'image_dimensions_mismatch'):
            prepare_one(a,self.approval,self.root)

    def test_symlink_rejected(self):
        (self.root/'synthetic.png').unlink()
        target=Path(self.tmp.name)/'outsider.png'
        Image.new('RGB',(1200,600)).save(target)
        (self.root/'synthetic.png').symlink_to(target)
        with self.assertRaisesRegex(ValueError,'input_must_be_local_non_symlink_regular_file'):
            prepare_one(self.row,self.approval,self.root)

    def test_unknown_media_id_rejected_before_writes(self):
        with self.assertRaisesRegex(ValueError,'must_select_unique_known_media_ids'):
            run([999],{'schema_version':1,'items':[]},self.root,self.out)
        self.assertFalse(self.out.exists())

    def test_zero_approval_does_not_write(self):
        with self.assertRaisesRegex(ValueError,'missing_media_specific_rights_approval'):
            run([39],{'schema_version':1,'items':[]},self.root,self.out)
        self.assertFalse(self.out.exists())

    def test_positive_local_staging_and_no_overwrite(self):
        with patch('prepare_hero_derivatives.catalog_rows', return_value={39:self.row}):
            result=run([39],{'schema_version':1,'items':[self.approval]},self.root,self.out)
        self.assertFalse(result['production_write_made'])
        self.assertFalse(result['claimed_76_percent_verified'])
        self.assertTrue((self.out/'fv-hero-39-960w.webp').is_file())
        self.assertTrue((self.out/'fv-hero-derivative-review.json').is_file())
        with patch('prepare_hero_derivatives.catalog_rows', return_value={39:self.row}):
            with self.assertRaisesRegex(ValueError, 'refusing_to_overwrite_existing_staged_files'):
                run([39],{'schema_version':1,'items':[self.approval]},self.root,self.out)

    def test_source_only_plan_has_exact_storage_sum(self):
        from prepare_hero_derivatives import catalog_rows
        rows=catalog_rows()
        self.assertEqual(len(rows),5)
        self.assertEqual(sum(x['original_bytes'] for x in rows.values()),13267538)
        self.assertTrue(all((r['width'],r['height'],r['target_width'],r['target_height']) ==
                            (1672,941,960,540) for r in rows.values()))


if __name__=='__main__':
    unittest.main()
