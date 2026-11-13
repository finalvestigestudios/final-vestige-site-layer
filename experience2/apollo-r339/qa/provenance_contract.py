#!/usr/bin/env python3
"""R339 NASA-photo provenance and conversion-boundary contract (offline; stdlib only).

This tests the staged Research Desk's exact source file from the current checkout.
Photograph catalogue identification is not a grant of reuse rights, does not turn
photographs into documentary/telemetry records, and does not prove ignition.
"""
from pathlib import Path
from html import unescape
import re

TEMPLATE = Path(__file__).resolve().parents[2] / 'research-desk/templates/ledger.html'
NASA_REPORT = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
EXPECTED = [
    ('01', 'January 1967', 'catalogue ID not stated', 'apollo-1-crew-honored/', 'View NASA crew photograph'),
    ('02', 'January 3, 1967', 'S67-15717', 'amf-s67-15717/', 'spacecraft-preparation photograph'),
    ('03', 'October 18, 1966', 'S66-58038', 'amf-s66-58038/', 'altitude-training photograph'),
    ('04', 'January 24, 2017', 'KSC-20170124-PH_KLS01_0164', 'amf-ksc-20170124-ph_kls01_0164/', '2017 tribute mockup'),
    ('05', 'January 28, 1967', 'S67-21294', 'amf-s67-21294/', 'post-fire cabin photograph'),
    ('06', 'January 24, 2017', 'KSC-20170124-PH_KLS01_0090', 'amf-ksc-20170124-ph_kls01_0090/', '2017 redesigned-hatch exhibit'),
]

def check(src: str) -> None:
    cards = re.findall(r'<article\b[^>]*\bdata-fvx-record\b[^>]*>.*?</article>', src, re.S | re.I)
    assert len(cards) == 6, f'expected six source cards, found {len(cards)}'
    assert src.count('data-fvx-source-role="documentary-support"') == 6
    assert src.count('data-fvx-source-role="contextual-photo-only"') == 6
    assert src.count('data-fvx-reuse-review="required"') == 6
    assert src.count('data-fvx-claim-proof="no"') == 6
    assert 'some show 2017 memorial exhibits rather than 1967 events' in src
    for card, (number, date, catalogue, url_tail, label) in zip(cards, EXPECTED):
        assert f'EVIDENCE {number} / 06' in card, number
        assert date in unescape(card), (number, 'missing date')
        assert catalogue in unescape(card), (number, 'unclear record identity')
        assert url_tail in card and label in card, (number, 'wrong photo destination or label')
        links = re.findall(r'<a\s+[^>]*?href="([^"]+)"[^>]*?>', card, re.S | re.I)
        assert len(links) == 2, (number, 'unexpected link count')
        assert links[0].startswith('https://www.nasa.gov/'), (number,'document first')
        assert links[1].startswith('https://www.nasa.gov/image-detail/'),(number,'photo not external merchant')
        assert card.index('data-fvx-source-role="documentary-support"') < card.index('data-fvx-source-role="contextual-photo-only"'),(number,'documentary first')
        assert 'data-fvx-claim-proof="no"' in card and 'data-fvx-reuse-review="required"' in card
    assert NASA_REPORT in src
    assert 'S67-19766' not in cards[0], 'unsubstantiated precise accession on linked NASA page'
    assert 'not fire telemetry' in cards[2]
    assert 'not 1967 event footage' in cards[3]
    assert 'not conclusive ignition proof' in cards[4]
    assert src.count('https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/') == 1
    assert not re.search(r'data-(?:geo-pin|map-edge|latitude|longitude)\b|payhip\.com|stripe\.com|paypal\.com', src, re.I)
    assert not re.search(r'commercially (?:cleared|licensed)|NASA[- ]approved', src, re.I)

def main():
    src = TEMPLATE.read_text(encoding='utf-8')
    check(src)
    mutations = {
        'misdated 2017 memorial': src.replace('January 24, 2017', 'January 24, 1967', 1),
        'fabricated photo accession': src.replace('catalogue ID not stated', 'NASA S67-19766', 1),
        'false commercial clearance': src.replace('data-fvx-reuse-review="required"', 'data-fvx-reuse-review="commercially cleared"', 1),
        'false documentary role': src.replace('data-fvx-source-role="contextual-photo-only"', 'data-fvx-source-role="documentary-support"', 1),
        'source-to-merchant hijack': src.replace('https://www.nasa.gov/image-detail/apollo-1-crew-honored/', 'https://payhip.com/fake-checkout', 1),
        'unapproved geo claim': src.replace('<section class="fv-ex2-ledger"', '<section data-geo-pin="invented" class="fv-ex2-ledger"', 1),
    }
    for label,changed in mutations.items():
        try: check(changed)
        except AssertionError: continue
        raise AssertionError(f'negative control was NOT detected: {label}')
    print(f'PASS: 6 documentary/photo pairs, provenance boundaries, {len(mutations)} adversarial cases; no production/network access')

if __name__ == '__main__':main()
