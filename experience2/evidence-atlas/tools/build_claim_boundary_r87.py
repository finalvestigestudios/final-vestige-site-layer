#!/usr/bin/env python3
"""R87: prove that a photograph link is not substituted for historical claim custody.

Read-only, fail-closed, source-controlled review; no rights-clearance or deployment.
"""
from __future__ import annotations
import hashlib
import html
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DESK = ROOT / 'experience2/research-desk/templates/ledger.html'
R86 = HERE / 'build_concordance_r86.py'
CSS = HERE / 'claim_boundary_r87.css'
EXPECTED_RESEARCH = {
    '01': 'https://www.nasa.gov/history/55-years-ago-tragedy-on-the-launch-pad/',
    **{f'{i:02}': 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
       for i in range(2, 7)},
}
IDS = tuple(EXPECTED_RESEARCH)


def gate(ok, code):
    if not ok:
        raise ValueError('R87_CLAIM_HOLD:' + code)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def official(url):
    try:
        p = urlsplit(url)
        return (p.scheme == 'https' and p.netloc == 'www.nasa.gov' and
                not p.username and not p.password and not p.query and
                not p.fragment and p.path.startswith('/') and '//' not in p.path)
    except (ValueError, TypeError):
        return False


class ClaimLinks(HTMLParser):
    """Capture actual article-specific research and image links, claim and caveat."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cards = {}
        self.current = None
        self.section = None
        self.links_depth = 0
        self.anchor = None
        self.article_depth = 0

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        classes = set(attrs.get('class', '').split())
        if tag == 'article' and 'data-fvx-record' in attrs:
            gate(self.current is None, 'NESTED_RECORD')
            match = re.fullmatch(r'fv-ex2-ledger-apollo1-record-(\d\d)', attrs.get('id', ''))
            gate(match is not None and match.group(1) in IDS and match.group(1) not in self.cards,
                 'CARD_ID')
            self.current = {'id': match.group(1), 'links': [], 'summary': [], 'boundary': []}
            self.article_depth = 1
            return
        if self.current is None:
            return
        if tag == 'article':
            gate(False, 'NESTED_ARTICLE')
        if tag in ('img', 'picture', 'iframe', 'video', 'source') or any(
                k in attrs for k in ('data-lat', 'data-lon', 'data-geo-edge')):
            gate(False, 'UNREVIEWED_MEDIA_GEO')
        if tag == 'div' and 'fv-ex2-ledger__recordlinks' in classes:
            gate(not self.links_depth, 'LINKS_NESTED')
            self.links_depth = 1
        elif self.links_depth and tag == 'div':
            self.links_depth += 1
        if tag == 'p' and 'fv-ex2-ledger__summary' in classes:
            gate(self.section is None, 'DOUBLE_SUMMARY')
            self.section = 'summary'
        if tag == 'div' and 'fv-ex2-ledger__boundary' in classes:
            gate(self.section is None, 'DOUBLE_BOUNDARY')
            self.section = 'boundary'
        if tag == 'a':
            gate(self.links_depth > 0 and self.anchor is None, 'UNTRACKED_ARTICLE_LINK')
            self.anchor = {'href': attrs.get('href', ''), 'text': []}

    def handle_data(self, data):
        if self.current is None:
            return
        if self.section:
            self.current[self.section].append(data)
        if self.anchor is not None:
            self.anchor['text'].append(data)

    def handle_endtag(self, tag):
        if self.current is None:
            return
        if tag == 'a' and self.anchor is not None:
            self.current['links'].append({'href': self.anchor['href'],
                    'text': ' '.join(''.join(self.anchor['text']).split())})
            self.anchor = None
        if tag == 'p' and self.section == 'summary':
            self.section = None
        if tag == 'div' and self.links_depth:
            self.links_depth -= 1
        if tag == 'div' and self.section == 'boundary':
            self.section = None
        if tag == 'article':
            gate(self.anchor is None and not self.links_depth, 'ARTICLE_UNCLOSED_LINK')
            self.cards[self.current['id']] = self.current
            self.current = None


def verify(desk_html=None, report=None):
    modspec = importlib.util.spec_from_file_location('r86_for_r87', R86)
    r86 = importlib.util.module_from_spec(modspec)
    sys.modules[modspec.name] = r86
    modspec.loader.exec_module(r86)
    # This checks the actual generated Atlas and the 3 original NASA registers first.
    base = report if report is not None else r86.verify()
    document = desk_html if desk_html is not None else DESK.read_text('utf-8')
    r86.validate_component(document, base['records'], 'desk')
    parser = ClaimLinks()
    parser.feed(document)
    parser.close()
    gate(parser.current is None and tuple(sorted(parser.cards)) == IDS, 'CARD_SET')
    rows = []
    for record in base['records']:
        number = record['id']
        card = parser.cards[number]
        links = card['links']
        gate(len(links) == 2 and links[0]['href'] == record['url'] and
             links[1]['href'] == EXPECTED_RESEARCH[number], 'CLAIM_PHOTO_LINK_' + number)
        gate(links[0]['text'] == 'NASA archive record ↗' and
             links[1]['text'] == 'Institutional research ↗', 'CLAIM_SOURCE_LABEL_' + number)
        gate(all(official(x['href']) for x in links), 'OFFICIAL_DOMAIN_' + number)
        summary = ' '.join(''.join(card['summary']).split())
        boundary = ' '.join(''.join(card['boundary']).split())
        gate(boundary.startswith('EVIDENCE LIMITATION'), 'BOUNDARY_LABEL_' + number)
        boundary = boundary.removeprefix('EVIDENCE LIMITATION').strip()
        gate(35 <= len(summary) <= 500 and 30 <= len(boundary) <= 400 and
             summary != boundary, 'CLAIM_LIMITATION_' + number)
        if number == '05':
            gate('unproven' in summary.lower() and 'probable is not proven' in boundary.lower(),
                 'IGNITION_UNCERTAINTY')
        if number in ('04', '06'):
            gate('2017' in record['date'], 'RETROSPECTIVE_DATE')
        rows.append({'id': number, 'catalog': record['catalog'], 'title': record['title'],
                     'photo_url': links[0]['href'], 'research_url': links[1]['href'],
                     'photo_date': record['date'], 'precision': record['precision'],
                     'claim': summary, 'limit': boundary,
                     'photo_limit': record['limitation']})
    gate(rows[0]['precision'] == 'MONTH_ONLY', 'CREW_DAY_UNKNOWN')
    return rows


def render(rows):
    e = lambda x: html.escape(str(x), quote=True)
    nav = ''.join(f'<a href="#r87-{r["id"]}">Finding {r["id"]}</a>' for r in rows)
    cards = []
    for r in rows:
        cards.append(f'''<article class="finding" id="r87-{e(r['id'])}" aria-labelledby="r87-title-{e(r['id'])}">
<p class="eyebrow">CLAIM / PHOTOGRAPH BOUNDARY · {e(r['id'])} / 06</p>
<h3 id="r87-title-{e(r['id'])}">{e(r['claim'])}</h3>
<p class="limit"><strong>Interpretive limit:</strong> {e(r['limit'])}</p>
<div class="source-pair"><section aria-label="Documentary basis for finding {e(r['id'])}"><h4>Historical research</h4>
<p>The documentary source supports examination of the historical claim; see its own qualifications.</p>
<a class="source" href="{e(r['research_url'])}" target="_blank" rel="noopener noreferrer">Open NASA institutional source ↗</a></section>
<section aria-label="Photographic source for finding {e(r['id'])}"><h4>Photograph is context, not proof</h4>
<p>{e(r['catalog'])} · {e(r['photo_date'])} ({e(r['precision'])}). Photo date is not an accident chronology date.</p>
<a class="source" href="{e(r['photo_url'])}" target="_blank" rel="noopener noreferrer">Open NASA image-detail page ↗</a></section></div>
<details><summary>Inspect the photograph's evidentiary limit and reuse status</summary>
<p>{e(r['photo_limit'])}</p><p><strong>Media reuse:</strong> Individual assessment not completed. An official source link does not license reproduction.</p>
<p><strong>Attribution:</strong> NASA photo metadata is kept separate from the research report. The proposed S67-19766 portrait association is provisional.</p></details></article>''')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>Apollo | Document versus Photograph — PRIVATE STAGING HOLD</title>
<link rel="stylesheet" href="claim_boundary_r87.css"></head><body><a class="skip" href="#findings">Skip to evidence findings</a>
<div class="wrap"><div class="mast">FINAL VESTIGE / APOLLO EVIDENCE STUDIO / SOURCE REVIEW</div>
<header><p class="eyebrow">THE RESEARCH DESK · SOURCE-CUSTODY AUDIT</p><h1>What the documents say.<br><em>What a photograph cannot.</em></h1>
<p class="lede">Six documented claims, six photographic context records, and their boundaries. Each historical source is separately verified against the actual Research Desk article. No photograph is treated as proof of oxygen pressure, ignition, or the fire sequence.</p>
<div class="hold" role="note"><strong>STAGING HOLD · 0 OF 6 IMAGE REUSE ASSESSMENTS CLEARED.</strong><br>
The crew photograph's exact day is unknown and its S67-19766 association remains provisional. Two 2017 photographs share a date, but have no verified order within that day. No NASA photographs are embedded.</div>
<nav class="jump" aria-label="Jump to an evidence finding">{nav}</nav></header>
<main id="findings"><h2>Six findings · two distinct types of source</h2><p>The finding number is not a photographic or fire-event timeline. Expand any card to inspect its limitations, even without JavaScript.</p>
<div class="cards">{''.join(cards)}</div></main><footer>
<p><strong>Source link ≠ photographic reproduction permission.</strong> Historical source custody and photographic provenance are independently reviewed; neither substitutes for independent editorial, media rights, accessibility or founder signoff.</p>
<p>Official source policy: <a href="https://www.nasa.gov/nasa-brand-center/">NASA Brand Center ↗</a>. No invented map locations or causal edges.</p></footer></div></body></html>'''


def build(destination):
    rows = verify()  # fail before writing anything
    page = render(rows).encode('utf-8')
    gate(not re.search(rb'<(?:img|iframe|picture|video|script)\b|data-lat\b|data-geo-edge\b',
                       page, re.I), 'OUTPUT_MEDIA_GEO')
    style = CSS.read_bytes()
    destination.mkdir(parents=True, exist_ok=True)
    (destination/'R87_CLAIM_PHOTO_BOUNDARY.html').write_bytes(page)
    (destination/'claim_boundary_r87.css').write_bytes(style)
    receipt = {'schema':'fv.apollo.r87.claim-photo-boundary.v1','release':'STAGING_HOLD',
        'record_count':len(rows),'separate_research_sources':len(rows),
        'image_reuse_cleared':0,'images_embedded':0,'geo_pins':0,'speculative_edges':0,
        'hosted_wp_tested':False,'published':False,
        'sha256':{'desk':sha(DESK.read_bytes()),'r86_builder':sha(R86.read_bytes()),
                  'html':sha(page),'css':sha(style)},
        'source_pairs':[{'id':r['id'],'research':r['research_url'],'photo':r['photo_url']}
                        for r in rows]}
    (destination/'R87_RECEIPT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    return receipt

if __name__ == '__main__':
    try:
        build(Path(sys.argv[1]) if len(sys.argv)>1 else Path('/tmp/apollo-r87'))
        print('R87: six documentary/photo source pairs matched real Desk; STAGING HOLD')
    except Exception:
        print('R87_CLAIM_HOLD: verification failed, publication forbidden',file=sys.stderr)
        raise SystemExit(1)
