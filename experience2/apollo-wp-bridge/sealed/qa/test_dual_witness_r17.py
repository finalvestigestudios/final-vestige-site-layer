"""R17: the Review Board interpretation and NASA photo description must stay separate.

No user-facing card may imply a 1966/2017 image proves 1967 telemetry.
These tests exercise actual source-controlled records, including adversarial drift.
"""
import json
from html import escape
from pathlib import Path
import shutil
import tempfile
import unittest
from source_concordance import (
    BOARD_REPORT, CASEFILE, GENERATED, ConcordanceHold,
    build_concordance, build_context_index,
)


class DualWitness(unittest.TestCase):
    def test_no_silent_board_and_photo_conflation(self):
        html,css,receipt=build_concordance()
        context=json.loads(build_context_index())
        records=json.loads((CASEFILE/'records.json').read_text())['records']
        self.assertEqual(receipt['separated_photo_board_witnesses'],6)
        self.assertEqual(receipt['links_to_original_source_drawer'],6)
        self.assertEqual(receipt['links_to_board_report'],6)
        self.assertEqual(html.count('class="fv-ex2-concordance__proof"'),6)
        self.assertEqual(html.count('INTERPRETATION / BOARD RECORD'),6)
        self.assertEqual(html.count('WHAT THE NASA PHOTOGRAPH DEPICTS'),6)
        self.assertEqual(html.count(BOARD_REPORT),6)
        self.assertIn('grid-template-columns:1fr',css)
        for row,item in zip(records,context['records']):
            rid=row['id']
            self.assertIn(escape(row['finding'],quote=True),html)
            self.assertIn(escape(row['image_description'],quote=True),html)
            self.assertIn(f'href="#source-{rid}"',html)
            self.assertIn(f'href="#stage-{rid}"',html)
            self.assertEqual(item['editorial_finding'],row['finding'])
            self.assertEqual(item['photograph_depicts'],row['image_description'])
            self.assertEqual(item['board_report_url'],BOARD_REPORT)
            self.assertEqual(item['geometry'],'not_assigned')
            self.assertEqual(item['evidentiary_relationship'],
                             'photo_does_not_independently_prove_board_finding')
        self.assertEqual(context['geographic_coordinates_assigned'],0)
        self.assertTrue(context['not_a_rights_clearance'])
        self.assertIn('not Board quotations',html)

    def test_blank_photo_caption_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            cp=Path(tmp)/'case'; gp=Path(tmp)/'gen'
            cp.mkdir(); gp.mkdir()
            data=json.loads((CASEFILE/'records.json').read_text())
            data['records'][2]['image_description']='  '
            (cp/'records.json').write_text(json.dumps(data))
            shutil.copyfile(GENERATED/'fragment.html',gp/'fragment.html')
            with self.assertRaises(ConcordanceHold):build_concordance(cp,gp)
            with self.assertRaises(ConcordanceHold):build_context_index(cp,gp)

    def test_script_like_caption_is_escaped(self):
        with tempfile.TemporaryDirectory() as tmp:
            cp=Path(tmp)/'case';gp=Path(tmp)/'gen'
            cp.mkdir();gp.mkdir()
            data=json.loads((CASEFILE/'records.json').read_text())
            data['records'][0]['image_description']='<img src=x onerror=alert(1)>'
            (cp/'records.json').write_text(json.dumps(data))
            shutil.copyfile(GENERATED/'fragment.html',gp/'fragment.html')
            html,_,_=build_concordance(cp,gp)
            self.assertNotIn('<img',html)
            self.assertIn('&lt;img',html)

    def test_photo_years_remain_context_not_accident_timeline(self):
        idx=json.loads(build_context_index())['records']
        self.assertEqual([r['source_era'] for r in idx],
                         ['1967','1967','1966','2017','1967','2017'])
        for row in idx:
            self.assertEqual(row['media_status'][:10],'link_only_')


if __name__=='__main__': unittest.main()
