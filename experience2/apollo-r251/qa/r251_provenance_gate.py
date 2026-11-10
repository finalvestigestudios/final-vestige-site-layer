#!/usr/bin/env python3
"""R251: original-source NASA provenance, outbound-link and offer-integrity gate.

Executes the pinned R238 PHP adapter. Offline staging QA; no merchant or WP writes.
"""
import argparse, hashlib, json, re, subprocess
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup

MANIFEST='f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68'
CTA='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
NASA={'Apollo 204 Review Board','S66-58038','S67-15717','S67-21294'}

def sha(b): return hashlib.sha256(b).hexdigest()

def check(html):
    soup=BeautifulSoup(html,'html.parser')
    plates=soup.select('[data-fv-plate-source]')
    assert len(plates)==4 and {p['data-fv-plate-source'] for p in plates}==NASA, 'NASA records altered'
    assert len(soup.select('a.cta'))==1 and soup.select_one('a.cta')['href']==CTA, 'only free investigation CTA permitted'
    assert len(soup.select('a[href="'+CTA+'"]'))==1, 'duplicate destination'
    assert not soup.select('img,script,iframe,canvas,svg,video,[data-latitude],[data-longitude]'), 'unreviewed media/geo'
    assert not re.search('(?i)payhip|checkout|awin1|merchant-confirmed|mini museum',html), 'unreviewed commerce'
    assert 'not conclusively identified' in soup.get_text(' ',strip=True).lower(), 'uncertainty deleted'
    assert len(soup.select('.fv-apollo-print-custody a[href^="https://www.nasa.gov/"]'))>=8, 'print bibliography altered'
    times=[t['datetime'] for t in soup.select('#fv-apollo-chronology ol time[datetime]')]
    assert len(times)>=5 and times==sorted(times), 'chronology altered'
    ids=[n['id'] for n in soup.select('[id]')]
    assert len(ids)==len(set(ids)), 'duplicate ids'
    for p in plates:
        nasa_links=p.select('a[href^="https://www.nasa.gov/"]')
        assert len(nasa_links)>=1, 'NASA source action missing'
        for a in nasa_links:
            assert {'noopener','noreferrer'} <= set(a.get('rel',[])), 'source-plate outbound-link policy changed'
    for a in soup.select('a[href]'):
        href=a['href']
        if href.startswith('#'):
            assert soup.find(id=href[1:]), 'orphan anchor'
        else:
            u=urlparse(href)
            assert u.scheme=='https' and u.hostname in ('www.nasa.gov','finalvestige.com'), 'unreviewed outbound origin'
    return {'plates':len(plates),'links':len(soup.select('a[href]')),'chronology_events':len(times)}

def main(root):
    assert sha((root/'manifest.json').read_bytes())==MANIFEST, 'manifest mismatch'
    m=json.loads((root/'manifest.json').read_text())
    assert m['status']=='STAGING_HOLD' and m['not_live'] is True
    for path, expected in m['files'].items():
        assert sha((root/path).read_bytes())==expected, 'file drift: '+path
    cmd=['php',str(root/'wp-render-shim-r224.php'),str((root/'fv-ex2-apollo-r224.php').resolve()),'normal']
    data=json.loads(subprocess.run(cmd,check=True,capture_output=True,text=True,timeout=20).stdout)
    html=data['html']
    assert html==(root/'templates/atlas-fragment.html').read_text(), 'PHP render drift'
    baseline=check(html)
    changes={
      'unreviewed_host':('https://www.nasa.gov/','https://unreviewed.invalid/'),
      'http_source':('https://www.nasa.gov/','http://www.nasa.gov/'),
      'unsafe_rel':('rel="noopener noreferrer"','rel="opener"'),
      'orphan_jump':('href="#fv-apollo-main"','href="#absent"'),
      'fake_order':('</article>','<p>merchant-confirmed</p></article>'),
      'fabricated_location':('<article','<article data-latitude="28"'),
      'checkout':('</article>','<a href="https://payhip.com/order">Buy</a></article>'),
    }
    rejected=[]
    for name,(old,new) in changes.items():
        assert old in html, 'mutation target unavailable: '+name
        try: check(html.replace(old,new,1))
        except AssertionError: rejected.append(name)
    assert len(rejected)==len(changes), 'mutation escaped gate'
    print(json.dumps({'status':'PASS','test':'R251 original NASA source custody','manifest_sha256':MANIFEST,
                      'baseline':baseline,'negative_controls_rejected':rejected,'production':'NOT_LIVE'},sort_keys=True))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--atlas',required=True,type=Path)
    main(p.parse_args().atlas)
