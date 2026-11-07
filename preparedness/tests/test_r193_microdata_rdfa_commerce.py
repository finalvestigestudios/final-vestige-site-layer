"""R193 synthetic regressions for previously unguarded non-JSON-LD commerce.

All fixtures are invented and contain no customer or checkout data.
DRAFT_HARD_HOLD never establishes qualified source, browser, merchant, or QD review.
"""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'tools/r191_static_resource_offer_gate.py'
spec = importlib.util.spec_from_file_location('r193_scanner_under_test', SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

BAD = [
    '<div itemscope itemtype="https://schema.org/Product"></div>',
    '<div itemscope itemtype="https://schema.org/Product/"></div>',
    '<div itemscope itemtype="https://schema.org/Offer"></div>',
    '<div itemscope itemtype="https://schema.org/Offer/"></div>',
    '<div itemscope itemtype="https://schema.org/AggregateOffer"></div>',
    '<div itemscope itemtype="https://schema.org/IndividualProduct"></div>',
    '<div itemscope itemtype="https://schema.org/BuyAction"></div>',
    '<div itemscope itemtype="https://schema.org/OrderAction"></div>',
    '<div itemscope itemtype="schema:Product"></div>',
    '<div itemscope itemtype="https://schema.org/%50roduct"></div>',
    '<div itemscope itemtype="https://schema.org/%4Fffer"></div>',
    '<div itemscope itemtype="https://schema.org/WebPage https://schema.org/Offer"></div>',
    '<div typeof="Product"></div>',
    '<div typeof="Offer"></div>',
    '<div typeof="BuyAction"></div>',
    '<div typeof="schema:Product"></div>',
    '<div typeof="https://schema.org/Product"></div>',
    '<div typeof="https://schema.org/Offer/"></div>',
    '<div typeof="https://schema.org/AggregateOffer"></div>',
    '<div typeof="schema:OrderAction"></div>',
    '<div typeof="Article schema:Product"></div>',
    '<div typeof="https://schema.org/%50roduct"></div>',
    '<span itemprop="offers"></span>',
    '<span itemprop="price"></span>',
    '<span itemprop="priceCurrency"></span>',
    '<span itemprop="availability"></span>',
    '<span itemprop="seller"></span>',
    '<span itemprop="merchant"></span>',
    '<span itemprop="checkoutUrl"></span>',
    '<span itemprop="inventoryLevel"></span>',
    '<span itemprop="hasOfferCatalog"></span>',
    '<span itemprop="name price"></span>',
    '<span itemprop="schema:price"></span>',
    '<span property="schema:offers"></span>',
    '<span property="schema:priceCurrency"></span>',
    '<span property="https://schema.org/price"></span>',
    '<span property="schema:paymentAccepted"></span>',
    '<span property="schema:acceptedPaymentMethod"></span>',
    '<span property="foo schema:BuyAction"></span>',
    '<span rel="schema:offers"></span>',
    '<span rel="schema:purchaseUrl"></span>',
    '<meta property="product:price:amount" content="19">',
    '<meta property="product:price:currency" content="USD">',
    '<meta name="product:price:amount" content="19">',
    '<meta property="og:price:amount" content="19">',
    '<meta property="commerce:price" content="19">',
    '<meta property="schema:price" content="19">',
    '<meta property="%70roduct:price:amount" content="19">',
    '<meta http-equiv="product:price" content="19">',
    '<script type="application/ld+json">{"@type":"https://schema.org/Product/"}</script>',
    '<script type="application/ld+json">{"@type":"https://schema.org/Offer/"}</script>',
    '<script type="application/ld+json">{"@type":["Thing","schema:BuyAction"]}</script>',
    '<script type="application/ld+json">{"@graph":[{"@type":"https://schema.org/Offer/"}]}</script>',
    '<script type="application/ld+json">{"@type":"https://schema.org/%50roduct"}</script>',
    '<div itemscope itemtype="https://schema.org/Article"><span itemprop="price"></span></div>',
]
GOOD = [
    '<div itemscope itemtype="https://schema.org/Article">Research</div>',
    '<span property="schema:datePublished">2026</span>',
    '<div typeof="schema:Article"></div>',
    '<div itemprop="author">The Preparedness Archive</div>',
    '<meta name="viewport" content="width=device-width, initial-scale=1">',
    '<meta property="og:title" content="A household emergency plan">',
    '<article aria-label="Product information is not verified">Free guidance</article>',
    '<div data-label="price"></div>',
    '<svg><pattern id="fw-pat"></pattern><rect fill="url(#fw-pat)"></rect></svg>',
    '<script type="application/ld+json">{"@type":"Article","headline":"Preparedness"}</script>',
    '<style>.warning{font-weight:bold;}</style>',
    '<div style="background:url(#local-gradient)">Unpublished</div>',
    '<span typeof="https://schema.org/CreativeWork">Sources first</span>',
    '<div itemscope itemtype="https://schema.org/HowTo">Draft only</div>',
    '<span property="schema:citation">Primary record</span>',
]

class MarkupSafety(unittest.TestCase):
    pass

def add_case(idx, html, forbidden):
    def test(self):
        result = gate.scan(html)
        if forbidden:
            self.assertTrue(result, 'missed unapproved commercial markup: ' + html)
        else:
            self.assertEqual(result, [], 'false commerce flag: ' + html)
    setattr(MarkupSafety, f'test_{"reject" if forbidden else "allow"}_{idx:03}', test)

for i, markup in enumerate(BAD):
    add_case(i, markup, True)
for i, markup in enumerate(GOOD):
    add_case(i, markup, False)

class SixToolContract(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'preparedness'
        (self.root / 'content/tools').mkdir(parents=True)
        (self.root / 'build/wp').mkdir(parents=True)
        for slug in gate.TOOLS:
            text = '<section><p>Unpublished free planning tool.</p></section>'
            (self.root / 'content/tools' / (slug + '.body.html')).write_text(text, encoding='utf-8')
            (self.root / 'build/wp' / (slug + '.html')).write_text(
                '<!-- wp:html -->\n' + text + '\n<!-- /wp:html -->', encoding='utf-8')

    def test_clean_six_tools_hold_not_pass(self):
        result = gate.check(self.root)
        self.assertEqual(result['state'], 'DRAFT_HARD_HOLD')
        self.assertEqual(result['authored_checked'], 6)
        self.assertEqual(result['wp_exports_checked'], 6)
        self.assertFalse(result['publication_authorized'])
        self.assertFalse(result['merchant_offer_verified'])
        self.assertIsNone(result['verified_paid_orders'])
        self.assertIsNone(result['realized_net_revenue'])

for i, slug in enumerate(('family-reunification-card', 'home-fire-escape-worksheet',
                          'kit-builder', 'power-outage-planner',
                          'reunification-plan', 'water-planner')):
    def mutation(self, target=slug):
        file = self.root / 'build/wp' / (target + '.html')
        markup = file.read_text(encoding='utf-8')
        file.write_text(markup.replace('</p>', '</p><span itemprop="price">19</span>'),
                        encoding='utf-8')
        result = gate.check(self.root)
        self.assertEqual(result['state'], 'INVALID_HARD_HOLD')
        self.assertTrue(result['errors'])
        self.assertFalse(result['publication_authorized'])
    setattr(SixToolContract, f'test_export_{i+1}_rejects_unreviewed_offer', mutation)

if __name__ == '__main__':
    unittest.main()
