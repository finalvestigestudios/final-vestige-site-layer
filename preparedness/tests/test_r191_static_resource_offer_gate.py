"""R191 synthetic tests. None assert real browser privacy, source/QD or sales."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import tempfile
import unittest

PATH=Path(__file__).resolve().parents[1]/'tools/r191_static_resource_offer_gate.py'
spec=importlib.util.spec_from_file_location('r191', PATH)
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)

CSS_BAD=[
 'background:url(https://example.test/a.png)',
 'background:url(http://example.test/a.png)',
 'background:url(//example.test/a.png)',
 'background:url(/private/track)',
 'background:url(data:image/svg+xml;base64,AAAA)',
 'background:url(file:///etc/passwd)',
 'background:url(javascript:alert(1))',
 'background:url(../track.png)',
 'background:url(track.png)',
 'background:url("")',
 '@import url(https://example.test/a.css)',
 '@import "test.css";',
 '@font-face {font-family:x;src:url(#x)}',
 '@namespace svg "http://www.w3.org/2000/svg";',
 'background: image-set(url(#x) 1x)',
 'background: -webkit-image-set(url(#x) 1x)',
 'filter: expression(alert(1))',
 'behavior: url(#x)',
 '-moz-binding: url(#x)',
 'background: cross-fade(url(#x),url(#y),50%)',
 'background: element(#id)',
 'background:url(foo',
 'background:url(#foo',
 'background: u\\72l(https://example.test/a)',
 'background:u\\000072l(https://example.test/a)',
 '@im\\70ort url(#x)',
 'background:url(&#104;ttps://example.test/a)',
 'background:url(\"https://example.test/a\")',
 'background: url(\'https://example.test/a\')',
 'background:url(#fake?query=1)',
]
HTML_BAD=[
 '<img src="https://example.test/p.png">',
 '<video poster="/x.jpg"></video>',
 '<audio src="/x.mp3"></audio>',
 '<track src="captions.vtt">',
 '<source srcset="a.jpg 1x, b.jpg 2x">',
 '<picture><source src="a.png"></picture>',
 '<svg><image href="https://example.test/image.svg"/></svg>',
 '<svg><use xlink:href="https://example.test/sprite.svg#id"/></svg>',
 '<svg><use href="foo.svg#id"/></svg>',
 '<svg><foreignObject>x</foreignObject></svg>',
 '<svg><animate attributeName="x"/></svg>',
 '<form action="/post"><input></form>',
 '<script type="application/ld+json">{"@type":"Product","name":"Tool"}</script>',
 '<script type="application/ld+json">{"@type":"Offer"}</script>',
 '<script type="application/ld+json">{"@type":"https://schema.org/BuyAction"}</script>',
 '<script type="application/ld+json">{"@type":"Article","offers":{"price":19}}</script>',
 '<script type="application/ld+json">{"@type":"Article","potentialAction":{"@type":"OrderAction"}}</script>',
 '<script type="application/ld+json">{"@type":"Article","priceCurrency":"USD"}</script>',
 '<script type="application/ld+json">{invalid}</script>',
 '<style>p{background:url(https://example.test/track)}</style>',
 '<div style="background:url(https://example.test/track)">x</div>',
 '<link href="https://example.test/css.css" rel="stylesheet">',
 '<script src="/beacon.js"></script>',
 '<svg><rect fill="url(https://example.test/track)"/></svg>',
 '<svg><rect stroke="url(/path.svg)"/></svg>',
 '<svg><rect filter="url(//external.test/f)"/></svg>',
 '<svg><rect clip-path="url(data:image/svg+xml,a)"/></svg>',
 '<svg><rect mask="url(http://external.test/m)"/></svg>',
 '<table background="https://example.test/b"></table>',
]
HTML_OK=[
 '<p>Hello</p>',
 '<style>.x{font-weight:bold}</style>',
 '<svg><defs><pattern id="x"/></defs><rect fill="url(#x)"/></svg>',
 '<div style="background:url(#local)"></div>',
 '<script type="application/ld+json">{"@type":"Article","name":"Tool"}</script>',
 '<script type="application/ld+json">{"@graph":[{"@type":"Article"},{"@type":"BreadcrumbList"}]}</script>',
 '<form onsubmit="return false"><input type="text"></form>',
 '<button type="button" onclick="window.print()">Print</button>',
 '<style>@media print{.x{display:block}}</style>',
 '<svg><use href="#local"/><image xlink:href="#local"/></svg>',
 '<svg><rect stroke="url(#local)" fill="url(#local)"/></svg>',
]
class Cases(unittest.TestCase):
    pass

def _register_cases(kind, payloads, expected):
    for i,item in enumerate(payloads):
        def f(self, item=item, expected=expected, kind=kind):
            val=g.css_errors(item) if kind=='css' else g.scan(item)
            self.assertEqual(bool(val),expected, (item,val))
        setattr(Cases, f'test_{kind}_{"blocked" if expected else "accepted"}_{i:02d}', f)
_register_cases('css',CSS_BAD,True)
_register_cases('html',HTML_BAD,True)
_register_cases('html',HTML_OK,False)

class Corpus(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup)
        self.prep=Path(t.name)/'preparedness'
        (self.prep/'content/tools').mkdir(parents=True)
        (self.prep/'build/wp').mkdir(parents=True)
        for slug in g.TOOLS:
            (self.prep/'content/tools'/f'{slug}.body.html').write_text('<h1>Free draft</h1><style>.x{background:url(#id)}</style>')
            (self.prep/'build/wp'/f'{slug}.html').write_text('<!-- wp:html -->\n<h1>Draft</h1>\n<!-- /wp:html -->')

    def test_success_is_hard_hold(self):
        x=g.check(self.prep)
        self.assertEqual((x['state'],x['authored_checked'],x['wp_exports_checked'],x['errors']),(g.HOLD,6,6,[]))
        self.assertFalse(x['publication_authorized'])
        self.assertFalse(x['merchant_offer_verified'])

    def test_source_only_invalid(self):
        x=g.check(self.prep,exports=False)
        self.assertEqual((x['state'],x['authored_checked'],x['wp_exports_checked']),(g.INVALID,6,0))
        self.assertTrue(x['errors'])

    def test_missing_export_invalid(self):
        (self.prep/'build/wp'/f'{g.TOOLS[0]}.html').unlink()
        self.assertEqual(g.check(self.prep)['state'],g.INVALID)

    def test_extra_source_invalid(self):
        (self.prep/'content/tools/unknown.body.html').write_text('<p>Extra</p>')
        self.assertEqual(g.check(self.prep)['state'],g.INVALID)

    def test_missing_source_invalid(self):
        (self.prep/'content/tools'/f'{g.TOOLS[2]}.body.html').unlink()
        self.assertEqual(g.check(self.prep)['state'],g.INVALID)

    def test_css_source_injection_invalid(self):
        (self.prep/'content/tools'/f'{g.TOOLS[0]}.body.html').write_text('<style>@import url(https://tracking.test/c)</style>')
        self.assertEqual(g.check(self.prep)['state'],g.INVALID)

    def test_css_export_injection_invalid(self):
        (self.prep/'build/wp'/f'{g.TOOLS[0]}.html').write_text('<!-- wp:html --><style>@import url(https://tracking.test/c)</style><!-- /wp:html -->')
        self.assertEqual(g.check(self.prep)['state'],g.INVALID)

    def test_checkout_schema_export_invalid(self):
        (self.prep/'build/wp'/f'{g.TOOLS[0]}.html').write_text('<!-- wp:html --><script type="application/ld+json">{"@type":"Product","offers":{"price":19}}</script><!-- /wp:html -->')
        self.assertEqual(g.check(self.prep)['state'],g.INVALID)

    def test_wrong_wp_wrapper_invalid(self):
        (self.prep/'build/wp'/f'{g.TOOLS[0]}.html').write_text('<p>no wordpress markers</p>')
        self.assertEqual(g.check(self.prep)['state'],g.INVALID)

    def test_symlink_source_invalid(self):
        x=self.prep/'content/tools'/f'{g.TOOLS[0]}.body.html'
        x.unlink();x.symlink_to(self.prep/'content/tools'/f'{g.TOOLS[1]}.body.html')
        self.assertEqual(g.check(self.prep)['state'],g.INVALID)

    def test_symlink_export_invalid(self):
        x=self.prep/'build/wp'/f'{g.TOOLS[0]}.html';x.unlink();x.symlink_to(self.prep/'build/wp'/f'{g.TOOLS[1]}.html')
        self.assertEqual(g.check(self.prep)['state'],g.INVALID)

    def test_symlink_directory_invalid(self):
        link=self.prep/'alias';link.symlink_to(self.prep,target_is_directory=True)
        self.assertEqual(g.check(link)['state'],g.INVALID)

    def test_reject_oversize(self):
        f=self.prep/'content/tools'/f'{g.TOOLS[0]}.body.html'
        before=g.MAX_SIZE
        try:
            g.MAX_SIZE=10
            self.assertEqual(g.check(self.prep)['state'],g.INVALID)
        finally:g.MAX_SIZE=before

    def test_offer_nested(self):
        bad={'@graph':[{'@type':'Article','mainEntity':{'seller':'x'}}]}
        self.assertTrue(g.offer_errors(bad))

    def test_offer_noncommercial_json_valid(self):
        self.assertFalse(g.offer_errors({'@graph':[{'@type':'Article','dateModified':'2026-11-07'}]}))

    def test_inline_css_fragment_valid(self):
        self.assertEqual(g.css_errors('.x{fill:url(#fw-pat)}'),[])

    def test_incomplete_css_url_invalid(self):
        self.assertTrue(g.css_errors('.x{background:url(foo'))

if __name__=='__main__':unittest.main()
