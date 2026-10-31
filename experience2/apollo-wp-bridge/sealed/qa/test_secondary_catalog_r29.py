#!/usr/bin/env python3
"""R29 source-identity editor guard; offline, no license / NASA identity approval."""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from qa.research_desk_crosswalk import (
    CrosswalkHold, SECONDARY_WITNESS, SECONDARY_WITNESS_SHA256,
    build_crosswalk, verify_secondary_catalog,
)
from qa.source_concordance import CASEFILE


class SecondaryCatalogR29(unittest.TestCase):
    def test_pinned_real_secondary_evidence_is_hold(self):
        info = verify_secondary_catalog()
        self.assertEqual(sha256(SECONDARY_WITNESS.read_bytes()).hexdigest(), SECONDARY_WITNESS_SHA256)
        self.assertEqual(info['identity_status'], 'UNRESOLVED_NOT_FIRST_PARTY_CONFIRMED')
        self.assertEqual(info['secondary_listing']['displayed_nasa_identifier'], 'S67-19766')
        self.assertFalse(info['secondary_listing']['first_party_nasa_catalog_record'])
        self.assertFalse(info['secondary_listing']['establishes_same_image_as_casefile_link'])
        self.assertFalse(info['secondary_listing']['promotes_geolocation_or_rights'])
        self.assertEqual(info['atlas_geographic_pins'], 0)

    def test_crosswalk_is_no_js_and_preserves_hold(self):
        html, report = build_crosswalk(json.loads((CASEFILE / "records.json").read_text(encoding="utf-8"))["records"])
        self.assertIn('data-secondary-catalog-review="hold"', html)
        self.assertIn('data-secondary-source-status="not-first-party"', html)
        self.assertIn('1968–1972', html)
        self.assertIn('not linked by a first-party NASA identifier', html)
        self.assertIn('href="#source-01"', html)
        self.assertIn('href="#stage-01"', html)
        self.assertIn('NASA S67-19766', html)
        self.assertIn('S66-30236', html)
        self.assertEqual(html.count('data-crosswalk-id='), 6)
        self.assertEqual(html.count('data-crosswalk-review="hold"'), 1)
        self.assertNotIn('<script', html)
        self.assertNotIn('<img', html)
        self.assertNotIn('data-lat=', html)
        self.assertEqual(report['catalog_label_review_holds'], 1)
        self.assertFalse(report['source_identifier_verified'])
        self.assertFalse(report['secondary_first_party_corroboration'])
        self.assertFalse(report['secondary_image_equivalence'])
        self.assertEqual(report['geo_pins'], 0)
        self.assertEqual(report['photo_bytes_copied'], 0)

    def test_changed_witness_bytes_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'witness.json'
            dest.write_bytes(SECONDARY_WITNESS.read_bytes() + b'\n')
            with self.assertRaises(CrosswalkHold):
                verify_secondary_catalog(dest)

    def test_semantic_promotions_rejected_even_if_rehashed(self):
        original=json.loads(SECONDARY_WITNESS.read_text(encoding='utf-8'))
        changes=[
            ('secondary_listing','first_party_nasa_catalog_record',True),
            ('secondary_listing','establishes_same_image_as_casefile_link',True),
            ('secondary_listing','promotes_geolocation_or_rights',True),
            ('secondary_listing','date_correlates_with_casefile_january_1967',True),
            ('secondary_listing','displayed_nasa_identifier','S66-30236'),
            ('secondary_listing','url','https://attacker.example.com/'),
            ('identity_status',None,'RESOLVED'),
            ('photo_reuse_status',None,'CLEARED'),
            ('atlas_geographic_pins',None,1),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/'candidate.json'
            for section,key,val in changes:
                data=json.loads(json.dumps(original))
                if key is None:data[section]=val
                else:data[section][key]=val
                raw=(json.dumps(data,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
                file.write_bytes(raw)
                with self.subTest(section=section,key=key,val=val):
                    with patch('qa.research_desk_crosswalk.SECONDARY_WITNESS_SHA256',sha256(raw).hexdigest()):
                        with self.assertRaises(CrosswalkHold):
                            verify_secondary_catalog(file)


if __name__=='__main__':unittest.main()
