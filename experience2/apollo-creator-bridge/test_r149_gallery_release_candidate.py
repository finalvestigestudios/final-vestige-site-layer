"""Native offline regression; fixtures model the exact markers in WordPress page 2017."""
from pathlib import Path
import tempfile
import unittest
from r149_gallery_release_candidate import BAD, GOOD, OLD_STATUS, NEW_STATUS, NASA_SOURCES, CTA, MARKERS, inspect, propose, digest, stage

BASE = ('<section data-fvx-chronology>' + ''.join(MARKERS)
        + ''.join(NASA_SOURCES) + CTA + ' Read the full investigation '
        + 'These photographs do not depict the marked seconds.'
        + ''.join(f'<figure data-fvx-chrono-photo="{i}"></figure>' for i in range(3))
        + OLD_STATUS + BAD + '</section>')

class GalleryPatch(unittest.TestCase):
    def test_baseline_matches_provenance(self):
        self.assertEqual([], inspect(BASE))
    def test_change_is_exactly_two_reversible_substitutions(self):
        revised = propose(BASE)
        self.assertEqual(revised.replace(GOOD, BAD).replace(NEW_STATUS, OLD_STATUS), BASE)
        self.assertEqual(revised.count(NEW_STATUS), 1)
    def test_rejects_second_patch(self):
        with self.assertRaisesRegex(ValueError, 'SOURCE_HOLD'):
            propose(propose(BASE))
    def test_rejects_missing_third_photo(self):
        with self.assertRaisesRegex(ValueError, 'PHOTO_2_NOT_UNIQUE'):
            propose(BASE.replace('data-fvx-chrono-photo="2"', 'data-fvx-chrono-photo="0"'))
    def test_rejects_duplicate_old_selector(self):
        with self.assertRaisesRegex(ValueError, 'EXACT_UNPATCHED_GALLERY_SELECTOR'):
            propose(BASE + BAD)
    def test_rejects_lost_board_source(self):
        with self.assertRaisesRegex(ValueError, 'NASA_SOURCE_MISSING'):
            propose(BASE.replace(NASA_SOURCES[-1], ''))
    def test_rejects_missing_chronology_marker(self):
        with self.assertRaisesRegex(ValueError, 'CHRONOLOGY_MARKER_MISSING'):
            propose(BASE.replace(MARKERS[2], ''))
    def test_rejects_link_changed(self):
        with self.assertRaisesRegex(ValueError, 'CONTEXT_OR_CTA_MISSING'):
            propose(BASE.replace(CTA, 'https://example.org/'))
    def test_rejects_false_context(self):
        with self.assertRaisesRegex(ValueError, 'CONTEXT_OR_CTA_MISSING'):
            propose(BASE.replace('photographs do not depict', 'photographs show'))
    def test_staging_requires_independent_hash(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'in.html'; path.write_text(BASE)
            with self.assertRaisesRegex(ValueError, 'independent input SHA'):
                stage(path, Path(d)/'out.html', Path(d)/'receipt.json', 'unknown')
    def test_staging_rejects_drift(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'in.html'; path.write_text(BASE)
            with self.assertRaisesRegex(ValueError, 'does not match'):
                stage(path, Path(d)/'out.html', Path(d)/'receipt.json', '0'*64)
    def test_staging_writes_no_original_and_holds_release(self):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d)/'in.html';out=Path(d)/'candidate.html';receipt=Path(d)/'receipt.json'
            src.write_text(BASE)
            r=stage(src,out,receipt,digest(BASE))
            self.assertEqual(src.read_text(), BASE)
            self.assertEqual(digest(out.read_text()),r['candidate_sha256'])
            self.assertFalse(r['approved_to_publish'])
            self.assertFalse(r['published_to_wordpress'])
    def test_staging_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            src=Path(d)/'in.html';out=Path(d)/'in.html';src.write_text(BASE)
            with self.assertRaisesRegex(ValueError, 'unsafe'):
                stage(src,out,Path(d)/'receipt.json',digest(BASE))

if __name__=='__main__':unittest.main()
