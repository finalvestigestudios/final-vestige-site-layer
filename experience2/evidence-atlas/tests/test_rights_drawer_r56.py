#!/usr/bin/env python3
"""R56 NASA metadata custody: closed-build mutation tests and transparent static markup."""
from __future__ import annotations
import json
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build_atlas
import build_wordpress_stage


class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags=[]
    def handle_starttag(self,tag,attrs):
        self.tags.append((tag,dict(attrs)))


class RightsDrawerR56(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.custody=build_atlas.validate_custody()
        cls.rights=build_atlas.validate_rights_audit(cls.custody)
        cls.html=build_atlas.make_html(cls.custody, '', '')

    def test_verified_audit_is_pinned_and_pending(self):
        self.assertEqual(self.rights['page_text_reviewed_on'], '2026-11-01')
        self.assertEqual(build_atlas.sha256(build_atlas.RIGHTS_AUDIT.read_bytes()),build_atlas.EXPECTED_AUDIT_SHA256)
        self.assertEqual([x['id'] for x in self.rights['records']],list(build_atlas.IDS))
        self.assertTrue(all(x['rights_status']=='INDIVIDUAL_REVIEW_PENDING' for x in self.rights['records']))

    def test_any_audit_mutation_blocks_compilation(self):
        raw=build_atlas.RIGHTS_AUDIT.read_bytes()
        for changed in (raw+b'\n', raw.replace(b'INDIVIDUAL_REVIEW_PENDING',b'APPROVED',1),
                        raw.replace(b'S67-19766',b'S67-19765',1)):
            with tempfile.TemporaryDirectory() as temp:
                p=Path(temp)/'audit.json';p.write_bytes(changed)
                with self.assertRaisesRegex(ValueError,'audit changed without review'):
                    build_atlas.validate_rights_audit(self.custody,p)

    def test_each_nasa_source_drawer_is_auditable_without_js(self):
        html=self.html
        self.assertEqual(html.count('data-fva-catalog-status'),6)
        self.assertEqual(html.count('NASA metadata reviewed 2026-11-01'),6)
        self.assertEqual(html.count('Individual review required. No photograph is reproduced here.'),6)
        self.assertEqual(html.count('data-fva-custody-status'),1)
        self.assertIn('5 of 6',html)
        self.assertIn('1 of 6',html)
        self.assertIn('0 of 6',html)
        self.assertIn('No individual image credit displayed in reviewed metadata.',html)
        self.assertIn('NASA/Kim Shiflett',html)
        self.assertIn('Catalog-to-photograph identity remains unconfirmed',html)
        self.assertNotIn('<img',html)
        self.assertNotIn('data-lat=',html)
        self.assertNotIn('data-lng=',html)

    def test_staged_wordpress_fragment_has_six_custody_disclosures(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest=build_wordpress_stage.build(Path(tmp))
            fragment=(Path(tmp)/'fv-ex2-evidence-atlas/templates/atlas-fragment.html').read_text()
        tags=Collector();tags.feed(fragment)
        self.assertEqual(sum(t=='details' and 'data-fva-drawer' in a for t,a in tags.tags),6)
        self.assertEqual(sum(t=='dd' and 'data-fva-catalog-status' in a for t,a in tags.tags),6)
        self.assertEqual(sum(t=='section' and 'data-fva-custody-status' in a for t,a in tags.tags),1)
        self.assertEqual(manifest['media_rights_unreviewed'],6)
        self.assertEqual(manifest['embedded_images'],0)
        self.assertEqual(manifest['geographic_pins'],0)
        self.assertNotIn('<main',fragment)

if __name__=='__main__': unittest.main()
