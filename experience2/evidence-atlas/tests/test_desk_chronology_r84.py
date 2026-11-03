"""R84 certainty-mutant checks, with exact native Research Desk source as control."""
from __future__ import annotations
import copy
import re
import unittest
from pathlib import Path
from wp_chronology_r84 import (DATED, ORDERED_TARGETS, PORTRAIT,
                                verify_chronology_r84)

ROOT=Path(__file__).resolve().parents[2]
LEDGER=ROOT/'research-desk/templates/ledger.html'


class DeskPhotoChronologyR84(unittest.TestCase):
    def setUp(self):
        self.good={
            'ordered_dates':DATED,
            'ordered_targets':ORDERED_TARGETS,
            'same_day_group_count':1,
            'unresolved_count':1,
            'unresolved_date':'1967-01',
            'unresolved_target':PORTRAIT,
            'ordered_portrait_count':0,
            'rail_warning':'Photographs, not events during the fire. Their order that day is unknown.',
            'unresolved_warning':'Cannot be placed before or after other dated sources; catalog unconfirmed.',
        }

    def test_reviewed_contract_passes_without_claiming_fire_sequence(self):
        result=verify_chronology_r84(**self.good)
        self.assertEqual(result['verified_dated_milestones'],4)
        self.assertTrue(result['month_only_crew_portrait_outside_rail'])
        self.assertFalse(result['reconstructed_fire_timeline'])

    def test_each_unsupported_chronology_mutation_is_rejected(self):
        variants=[
            {'ordered_dates':('1966-10-18','1967-01','1967-01-03','2017-01-24')},
            {'ordered_dates':tuple(reversed(DATED))},
            {'ordered_dates':DATED[:-1]},
            {'ordered_targets':ORDERED_TARGETS[::-1]},
            {'ordered_targets':ORDERED_TARGETS+(PORTRAIT,)},
            {'same_day_group_count':0},
            {'same_day_group_count':2},
            {'unresolved_count':0},
            {'unresolved_date':'1967-01-27'},
            {'unresolved_target':ORDERED_TARGETS[0]},
            {'ordered_portrait_count':1},
            {'rail_warning':'Photographs reconstruct exactly what happened during the fire'},
            {'unresolved_warning':'Crew portrait confirmed before January 28, catalog approved'},
            {'unresolved_warning':'Cannot be placed before or after; S67-19766 confirmed'},
        ]
        for mutation in variants:
            with self.subTest(mutation=list(mutation)), self.assertRaises(AssertionError) as e:
                verify_chronology_r84(**{**self.good,**mutation})
            self.assertEqual(str(e.exception),'R77_R84_CHRONOLOGY_INTEGRITY')

    def test_actual_source_markup_uses_unplaced_aside_and_single_2017_date(self):
        page=LEDGER.read_text()
        rail=re.search(r'<nav class="fv-ex2-ledger__chronology"[\\s\\S]*?</nav>',page)
        self.assertIsNotNone(rail)
        rail=rail.group(0)
        dated=re.search(r'<ol>[\\s\\S]*?</ol>',rail).group(0)
        self.assertEqual(re.findall(r'<time datetime="(\\d{4}-\\d{2}-\\d{2})"',dated),list(DATED))
        self.assertEqual(dated.count('datetime="2017-01-24"'),1)
        self.assertNotIn('href="'+PORTRAIT+'"',dated)
        self.assertEqual(dated.count('data-fvx-chrono-link'),5)
        self.assertEqual(rail.count('class="fv-ex2-ledger__chrono-same-day"'),1)
        self.assertEqual(rail.count('class="fv-ex2-ledger__chrono-unplaced"'),1)
        self.assertIn('datetime="1967-01"',rail)
        self.assertIn('href="'+PORTRAIT+'"',rail)
        self.assertIn('unconfirmed',rail.lower())
        self.assertIn('not events during the fire',rail.lower())
        self.assertEqual(page.count('data-fvx-record data-fvx-search'),6)

    def test_original_nasa_destinations_and_photo_rights_untouched(self):
        page=LEDGER.read_text()
        self.assertEqual(page.count('NASA archive record ↗'),6)
        self.assertEqual(page.count('Image reuse has not been individually reviewed'),6)
        self.assertEqual(page.count('data-fvx-photo-record='),6)
        self.assertNotIn('<img',page)
        self.assertNotIn('data-lat=',page)
        self.assertNotIn('data-geo-edge=',page)


if __name__=='__main__':unittest.main()
