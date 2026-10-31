#!/usr/bin/env python3
"""R30 release contract mutation suite; must fail on missing rights and invented geography."""
from __future__ import annotations
import unittest
from browser_release_head_r30 import enforce


def baseline():
    return {'duplicate_ids': [], 'missing_anchors': 0, 'unnamed_links': 0,
            'unsafe_links': 0, 'unlabeled_fields': 0, 'doc_width': 390,
            'viewport_width': 390, 'nasa_records': 6,
            'catalog_holds': 1, 'rights_holds': 6, 'geo_pins': 0}


class R30ReleaseContract(unittest.TestCase):
    def test_exact_six_custodied_nasa_records_accepted(self):
        self.assertIsNone(enforce(baseline()))

    def test_hidden_or_removed_rights_reviews_refused(self):
        for key, value in [('rights_holds', 5), ('catalog_holds', 0), ('nasa_records', 5)]:
            with self.subTest(key=key):
                case = baseline(); case[key] = value
                with self.assertRaises(RuntimeError): enforce(case)

    def test_no_fabricated_geo_locations(self):
        case = baseline(); case['geo_pins'] = 1
        with self.assertRaises(RuntimeError): enforce(case)

    def test_accessible_navigation_must_resolve(self):
        for key, value in [('duplicate_ids', [['source-01',2]]),('missing_anchors',1),
                           ('unnamed_links',1),('unsafe_links',1),('unlabeled_fields',1)]:
            with self.subTest(key=key):
                case = baseline(); case[key] = value
                with self.assertRaises(RuntimeError): enforce(case)

    def test_320px_horizontal_overflow_refused(self):
        case = baseline(); case['viewport_width'] = 320; case['doc_width'] = 400
        with self.assertRaises(RuntimeError): enforce(case)


if __name__ == '__main__': unittest.main()
