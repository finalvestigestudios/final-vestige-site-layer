#!/usr/bin/env python3
"""R57 NASA-page catalog certainty is a metadata facet, never photo clearance."""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import build_atlas,build_wordpress_stage
import tempfile

class Collector(HTMLParser):
    def __init__(self):super().__init__();self.cards=[];self.buttons=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='article' and 'data-fva-record' in a:self.cards.append(a)
        if tag=='button' and 'data-fva-proof-filter' in a:self.buttons.append(a)

class CatalogR57(unittest.TestCase):
    def test_only_one_provisional_source_and_five_page_displayed(self):
        page=build_atlas.make_html(build_atlas.validate_custody(),'','')
        parsed=Collector();parsed.feed(page)
        self.assertEqual([a['data-fva-catalog-state'] for a in parsed.cards],
                         ['provisional']+['page-displayed']*5)
        self.assertEqual([a['data-fva-proof-filter'] for a in parsed.buttons],
                         ['all','page-displayed','provisional'])
        self.assertEqual([a['aria-pressed'] for a in parsed.buttons],
                         ['true','false','false'])
        self.assertIn('not image-use permission',page)
        self.assertEqual(page.count('data-fva-cite-id'),6)

    def test_wordpress_stage_preserves_static_citations_and_facet(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest=build_wordpress_stage.build(Path(tmp))
            page=(Path(tmp)/'fv-ex2-evidence-atlas/templates/atlas-fragment.html').read_text()
            parsed=Collector();parsed.feed(page)
            self.assertEqual(len(parsed.cards),6)
            self.assertEqual(len(parsed.buttons),3)
            self.assertNotIn('<main',page)
            self.assertNotIn('<img',page)
            self.assertEqual(manifest['geographic_pins'],0)
            self.assertEqual(manifest['media_rights_unreviewed'],6)

    def test_runtime_source_contract_is_version_57(self):
        root=Path(__file__).resolve().parents[1]
        js=(root/'atlas.js').read_text()
        css=(root/'atlas.css').read_text()
        php=(root/'final-vestige-ex2-evidence-atlas.php').read_text()
        self.assertIn('proofFilter',js)
        self.assertIn('proofButtons.forEach(b=>b.addEventListener',js)
        self.assertIn('card.dataset.fvaCatalogState',js)
        self.assertIn('.fva-proof-filter button[aria-pressed="true"]',css)
        self.assertIn('0.0.58-staging',php)

if __name__=='__main__':unittest.main()
