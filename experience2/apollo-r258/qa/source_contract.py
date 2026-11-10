#!/usr/bin/env python3
"""Offline Apollo Evidence Atlas R258: actual-PHP source + single-free-CTA admission.
No site writes, network fetches, sale inference, WordPress install or media license.
"""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess

SEAL = 'f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68'
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
PLATES = {'Apollo 204 Review Board', 'S66-58038', 'S67-15717', 'S67-21294'}
DATES = ('1966-10-18', '1967-01-03', '1967-01-27', '1967-01-28', '1967-04')


class Reader(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links, self.plates, self.danger = [], [], [], []

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'a':
            self.links.append(attrs.get('href', ''))
        if 'data-fv-plate-source' in attrs:
            self.plates.append(attrs['data-fv-plate-source'])
        if tag in ('script', 'iframe', 'form'):
            self.danger.append(tag)
        self.danger += [name for name in attrs if name.lower().startswith('on') or name in
                        ('data-geo-pin', 'data-lat', 'data-lon', 'data-merchant')]


def admit(html):
    r = Reader()
    r.feed(html)
    assert not r.danger, 'unapproved script, geodata, commerce or form'
    assert len(r.ids) == len(set(r.ids)), 'duplicate IDs'
    assert len(r.links) == 87 and r.links.count(FREE) == 1, 'link/one-CTA custody drift'
    assert r.links.count(FREE) == 1 and set(r.plates) == PLATES and len(r.plates) == 4, 'evidence/source custody drift'
    assert all(h.startswith(('https://www.nasa.gov/', '#')) or h == FREE for h in r.links), 'unknown outbound URL'
    assert all(h[1:] in r.ids for h in r.links if h.startswith('#')), 'broken fragment navigation'
    assert sum(h.startswith('https://www.nasa.gov/') for h in r.links) == 55, 'NASA bibliography drift'
    assert sum(h.startswith('#') for h in r.links) == 31, 'internal navigation drift'
    assert 'NASA does not endorse Final Vestige' in html, 'rights/endorsement boundary absent'
    assert 'No single ignition source' in html, 'technical uncertainty erased'
    for d in DATES:
        assert f'datetime="{d}"' in html, 'chronology drift ' + d
    return {'links': len(r.links), 'nasa_links': 55, 'internal_links': 31,
            'free_investigation_links': 1, 'plates': sorted(r.plates), 'ids': len(r.ids)}


def main(atlas):
    manifest = atlas / 'manifest.json'
    assert hashlib.sha256(manifest.read_bytes()).hexdigest() == SEAL, 'sealed manifest mismatch'
    for name, digest in json.loads(manifest.read_text())['files'].items():
        assert hashlib.sha256((atlas / name).read_bytes()).hexdigest() == digest, name
    result = subprocess.run(['php', str(atlas / 'wp-render-shim-r224.php'),
                             str((atlas / 'fv-ex2-apollo-r224.php').resolve()), 'normal'],
                            capture_output=True, text=True, check=True)
    html = json.loads(result.stdout)['html']
    assert html == (atlas / 'templates/atlas-fragment.html').read_text(), 'PHP output drift'
    baseline = admit(html)
    cases = [
        html.replace('<article ', '<article data-geo-pin="12,34" ', 1),
        html.replace('href="' + FREE + '"', 'href="https://payhip.com/buy"', 1),
        html.replace('href="#fv-apollo-evidence"', 'href="#missing"', 1),
        html.replace('data-fv-plate-source="S67-21294"', 'data-fv-plate-source="fiction"', 1),
        html.replace('<article ', '<article onclick="alert(1)" ', 1),
        html.replace('datetime="1967-01-28"', 'datetime="1999-01-28"'),
        html + '<a href="' + FREE + '">duplicate</a>',
        html.replace('NASA does not endorse Final Vestige', 'endorsement omitted'),
    ]
    for number, changed in enumerate(cases, 1):
        assert changed != html, 'negative control made no change'
        try:
            admit(changed)
        except AssertionError:
            continue
        raise AssertionError(f'unsafe mutation {number} was not rejected')
    print(json.dumps({'pass': True, 'negative_controls_rejected': len(cases),
                      'manifest_sha256': SEAL, 'php_html_sha256': hashlib.sha256(html.encode()).hexdigest(),
                      'custody': baseline}, sort_keys=True))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--atlas', type=Path, required=True)
    main(p.parse_args().atlas)
