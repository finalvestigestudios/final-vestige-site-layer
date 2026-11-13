#!/usr/bin/env python3
"""R337: fail-closed source-custody QA for the isolated PR #158 Research Desk.
The test protects markup/provenance semantics; not a NASA rights clearance,
WordPress acceptance, commercial conversion proof or accessibility certification.
Run: python3 experience2/apollo-r337/qa/desk_source_custody_contract.py experience2/research-desk/templates/ledger.html
"""
from pathlib import Path
from urllib.parse import urlsplit
import re
import sys

BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
RETRO = 'https://www.nasa.gov/history/55-years-ago-tragedy-on-the-launch-pad/'
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
PHOTOS = (
    'https://www.nasa.gov/image-detail/apollo-1-crew-honored/',
    'https://www.nasa.gov/image-detail/amf-s67-15717/',
    'https://www.nasa.gov/image-detail/amf-s66-58038/',
    'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/',
    'https://www.nasa.gov/image-detail/amf-s67-21294/',
    'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/',
)

def audit(html):
    errors = []
    cards = re.findall(r'<article class="fv-ex2-ledger__card"[^>]*>.*?</article>', html, re.S)
    if len(cards) != 6:
        return [f'expected 6 cards, found {len(cards)}']
    if 'not evidence of the ignition point' not in html or 'reuse rights' not in html:
        errors.append('visible provenance and reuse boundary missing')
    if '102 deliberate ignition tests' in html:
        errors.append('unsupported exact post-fire test count')
    for n, card in enumerate(cards, 1):
        group = re.search(r'<div class="fv-ex2-ledger__recordlinks">(.*?)</div>', card, re.S)
        if not group:
            errors.append(f'card {n}: missing source group')
            continue
        links = re.findall(r'<a\\s+([^>]+)>(.*?)</a>', group.group(1), re.S)
        if len(links) != 2:
            errors.append(f'card {n}: expected 2 distinct custody links')
            continue
        href = [re.search(r'\\bhref="([^"]+)"', attrs).group(1) for attrs, _ in links]
        if href[0] != (RETRO if n == 1 else BOARD):
            errors.append(f'card {n}: documentary support is not first')
        if href[1] != PHOTOS[n-1]:
            errors.append(f'card {n}: contextual photo accession drift')
        if 'data-fvx-source-role="documentary-support"' not in links[0][0]:
            errors.append(f'card {n}: documentary role missing')
        if not all(x in links[1][0] for x in ('data-fvx-source-role="contextual-photo-only"', 'data-fvx-claim-proof="no"', 'data-fvx-reuse-review="required"')):
            errors.append(f'card {n}: photograph masquerades as claim proof or has no rights review')
        if 'photo' not in links[1][1].lower() or 'context' not in links[1][1].lower():
            errors.append(f'card {n}: photo accessibility label unclear')
        if any(urlsplit(u).hostname != 'www.nasa.gov' for u in href):
            errors.append(f'card {n}: unexpected source host')
    urls = re.findall(r'\\bhref="([^"]+)"', html)
    if urls.count(FREE) != 1:
        errors.append('one canonical editorial continuation required')
    if any(any(s in u.lower() for s in ('payhip','checkout','affiliate','utm_')) for u in urls):
        errors.append('unauthorized commerce or campaign link')
    if re.search(r'data-geo-(?:lat|lng)|data-map-edge|data-geo-pin', html):
        errors.append('invented geospatial fact')
    return errors

def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('experience2/research-desk/templates/ledger.html')
    html = path.read_text(encoding='utf-8')
    problems = audit(html)
    if problems:
        for p in problems: print('FAIL', p)
        raise SystemExit(1)
    mutants = [
        html.replace('data-fvx-source-role="documentary-support"','data-fvx-source-role="contextual-photo-only"',1),
        html.replace('not evidence of the ignition point','evidence of the ignition point',1),
        html.replace(FREE,'https://payhip.com/b/not-verified',1),
        html.replace('</section>','<span data-map-edge="invented"></span></section>',1),
        html.replace('</section>','102 deliberate ignition tests</section>',1),
    ]
    assert all(audit(m) for m in mutants), 'negative-control regression escaped'
    print('PASS R337: six source roles, 12 custody destinations, one editorial CTA; 5/5 negative controls')

if __name__ == '__main__':
    main()
