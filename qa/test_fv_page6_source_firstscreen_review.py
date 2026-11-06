"""Synthetic native tests, never a WordPress/Assembler conformance claim."""
import tempfile
import unittest
from pathlib import Path
from fv_page6_source_firstscreen_review import IDS,OLD,NEW,validate,run

def fixture():
    return ('<!-- wp:html --><style>@media(prefers-reduced-motion:reduce){'
            '.fv-margin-strip__item{display:none}.fv-margin-strip__item:nth-child(1){display:block}}'
            '</style>'+''.join(f'<span class="fv-margin-strip__item" style="--i:{i}">QA {i}</span>' for i in range(72))
            +'<!-- /wp:html --><!-- wp:html --><div data-fv-home-flagship>'
            +''.join(f'<div id="{i}"></div>' for i in IDS)
            +'<div class="fv-hf__opening-actions">'+OLD+'</div>'
            +'<a href="https://finalvestige.com/focus/">Focus Fieldbook</a>'
            +'</div><!-- /wp:html --><!-- wp:jetpack/subscriptions -->')

class SourceTests(unittest.TestCase):
    def test_valid(self):validate(fixture())
    def test_mutation_gate(self):
        mutations=[fixture().replace('style="--i:71"','style="--i:72"'),
          fixture().replace('id="fv-hf-evidence"','id="wrong"'),
          fixture().replace('jetpack/subscriptions','jetpack/removed'),
          fixture().replace(OLD,NEW), fixture().replace(OLD,OLD+OLD),
          fixture().replace('<!-- /wp:html -->','',1),
          fixture().replace('https://finalvestige.com/focus/','https://example.invalid/')]
        for item in mutations:
            with self.subTest():
                with self.assertRaises(ValueError):validate(item)
    def test_chromium_fixture(self):
        with tempfile.TemporaryDirectory() as d:
            r=run(fixture(),Path(d)/'run')
            self.assertFalse(r['release_ready'])
            self.assertTrue(r['observations']['focus_route_matches'])
            self.assertFalse(r['observations']['all_72_margins_visible_reduced_motion'])
            self.assertEqual(len(list((Path(d)/'run').glob('*.png'))),12)

if __name__=='__main__':unittest.main()
