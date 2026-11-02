"""R62 immutable photographic dates: exact original R37 custody, not fire sequence."""
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import build_atlas,build_wordpress_stage

class DateCustodyR62(unittest.TestCase):
    def test_six_js_pins_exactly_match_reviewed_custody(self):
        js=(ROOT/'atlas.js').read_text()
        match=re.search(r'const pinnedDates=\[(.*?)\n  \];',js,re.S)
        self.assertIsNotNone(match,'Client-side source-date custody guard removed')
        pairs=re.findall(r"\['(\d\d)','(\d{4})','([\d-]+)','([^']+)'\]",match.group(1))
        custody=build_atlas.validate_custody()
        expected=[(r['id'],r['date'][:4],r['date'],r['date_label']) for r in custody['records']]
        self.assertEqual(pairs,expected)
        self.assertEqual(len(set(row[0] for row in pairs)),6)

    def test_card_time_era_and_citation_must_agree_with_original_dates(self):
        js=(ROOT/'atlas.js').read_text()
        self.assertIn('record.dataset.fvaYear===year',js)
        self.assertIn("record.querySelector('.fva-card__date span')?.textContent.trim()===label",js)
        self.assertIn("link?.closest('[data-fva-era]')?.dataset.fvaEra===year",js)
        self.assertIn("time?.getAttribute('datetime')===iso",js)
        self.assertIn("time?.textContent.trim()===label",js)
        self.assertIn("text?.includes('photograph date '+label)",js)
        self.assertIn("if(!valid()){restore();return;}\n    if(onDeskHash",js)

    def test_generated_markup_still_contains_all_reviewed_dates_without_media_or_geo(self):
        custody=build_atlas.validate_custody()
        with tempfile.TemporaryDirectory() as tmp:
            result=build_wordpress_stage.build(Path(tmp))
            html=(Path(tmp)/'fv-ex2-evidence-atlas/templates/atlas-fragment.html').read_text()
        self.assertEqual(result['embedded_images'],0)
        self.assertEqual(result['geographic_pins'],0)
        self.assertEqual(result['media_rights_unreviewed'],6)
        for row in custody['records']:
            self.assertIn(f'data-fva-year="{row["date"][:4]}"',html)
            self.assertIn(f'<time datetime="{row["date"]}">{row["date_label"]}</time>',html)
            self.assertIn('photograph date '+row['date_label'],html)
        self.assertNotIn('<img ',html)

    def test_no_event_or_geospatial_inference_added(self):
        js=(ROOT/'atlas.js').read_text()
        for token in ('navigator.geolocation','fetch(', 'localStorage','leaflet','google.maps'):
            self.assertNotIn(token,js)
        self.assertIn('These six pairs come from the reviewed R37 custody crosswalk.',js)

if __name__=='__main__':unittest.main()
