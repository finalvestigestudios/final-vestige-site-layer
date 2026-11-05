import tempfile
import unittest
from pathlib import Path
from r150_real_excerpt_gate import git_blob_sha,check_source,run,ACTUAL_WP_EXCERPT_BLOB
from r149_gallery_release_candidate import propose

HERE=Path(__file__).resolve().parent
MODEL=(HERE/'r149_model_fixture_unpatched.html').read_text(encoding='utf-8')

class TestR150Gate(unittest.TestCase):
    def test_pinned_real_git_blob(self):
        self.assertEqual(len(ACTUAL_WP_EXCERPT_BLOB),40)
        self.assertEqual(git_blob_sha('abc'),'f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f')
    def test_model_rejected_when_masquerading_as_real(self):
        with self.assertRaisesRegex(ValueError,'SOURCE_HOLD'):
            check_source(MODEL)
    def test_explicit_model_is_never_real(self):
        self.assertEqual(check_source(MODEL,model=True)['type'],'CONTROLLED_MODEL')
    def test_patch_already_applied_fails(self):
        with self.assertRaisesRegex(ValueError,'SOURCE_HOLD'):
            check_source(propose(MODEL),model=True)
    def test_unreviewed_source_mutation_rejected(self):
        with self.assertRaisesRegex(ValueError,'SOURCE_HOLD'):
            check_source(MODEL.replace('https://www.nasa.gov/image-detail/amf-s66-58038/','https://www.nasa.gov/invalid/'),model=True)
    def test_output_collision_rejected(self):
        with tempfile.TemporaryDirectory() as p:
            d=Path(p)
            with self.assertRaisesRegex(ValueError,'no overwrite'):
                run(HERE/'r149_model_fixture_unpatched.html',d,model=True)
    def test_invalid_axe_fails_closed(self):
        with tempfile.TemporaryDirectory() as p:
            d=Path(p); bad=d/'axe.js';bad.write_text('not axe')
            with self.assertRaisesRegex(ValueError,'credible local script'):
                run(HERE/'r149_model_fixture_unpatched.html',d/'output',model=True,axe=bad)
    def test_model_report_never_claims_commercial_or_live(self):
        with tempfile.TemporaryDirectory() as p:
            r=run(HERE/'r149_model_fixture_unpatched.html',Path(p)/'artifacts',model=True)
            self.assertEqual(r['failed'],0)
            self.assertGreater(r['passed'],150)
            self.assertFalse(r['production_qa_complete'])
            self.assertFalse(r['source_excerpt_qa_complete'])
            self.assertEqual(r['axe'],'NOT_EXECUTED_AXE_UNAVAILABLE')
            self.assertFalse(r['approved_to_publish'])
            self.assertEqual(r['sales'],'NOT_VERIFIED')

if __name__=='__main__': unittest.main()
