#!/usr/bin/env python3
"""R416 read-only source/CTA acceptance for actual R415 PHP-produced markup.

A passing result describes a synthetic fixture only. It does not certify NASA rights,
merchant sales, site analytics, WordPress installation, real navigated CWV or axe-core.
"""
from __future__ import annotations
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
LATER = 'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/'
MIXED = 'https://www.nasa.gov/history/50th-anniversary-of-nasa-deciding-on-a-mixed-gas-atmosphere-for-apollo-a-direct-result-of-the-apollo-fire/'
RIGHTS = 'https://www.nasa.gov/nasa-brand-center/images-and-media/'
ARCHIVES = (
    'https://www.nasa.gov/image-detail/apollo-1-crew-honored/',
    'https://www.nasa.gov/image-detail/amf-s67-15717/',
    'https://www.nasa.gov/image-detail/amf-s66-58038/',
    'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/',
    'https://www.nasa.gov/image-detail/amf-s67-21294/',
    'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/',
)
EXPECTED_DATE_LABELS = ('27 January 1967','December 1967 – February 1968','14 March 1968')
ALLOWED_HOSTS = {'www.nasa.gov','finalvestige.com'}


def render_fixture() -> str:
    script = ROOT/'apollo-r415/qa/render_fixture.php'
    return subprocess.run(['php', str(script)], check=True, text=True,
                          capture_output=True, timeout=25).stdout


def inspect_markup(html: str, instances: int = 2) -> dict:
    """Fail on changed historical meaning, source substitutions or extra commerce actions."""
    soup = BeautifulSoup(html, 'html.parser')
    faults = []
    def require(ok: bool, message: str) -> None:
        if not ok: faults.append(message)
    journeys = soup.select('[data-fv-r415-journey]')
    require(len(journeys) == instances, f'expected {instances} independent journey(s), got {len(journeys)}')
    all_ids = [x.get('id') for x in soup.select('[id]')]
    require(len(all_ids) == len(set(all_ids)), 'duplicate document IDs')
    require(not soup.select('img, iframe, video, audio, form, script, canvas, object, embed'),
            'unreviewed media, active scripts, forms or embeddings')
    require(not soup.select('[data-lat], [data-lng], [data-longitude], [data-route-edge]'),
            'unreviewed geographic pin or map edge')
    anchors = soup.select('a[href]')
    for a in anchors:
        href = a['href']
        u = urlsplit(href)
        if u.scheme in ('http','https'):
            require(u.scheme == 'https' and u.hostname in ALLOWED_HOSTS,
                    f'non-allowlisted or insecure link {href!r}')
            require(not u.username and not u.password and not u.port,
                    f'embedded credentials or unexpected port in {href!r}')
            require(not u.query, f'external source/CTA has unreviewed query parameters: {href!r}')
        elif href.startswith('#'):
            target = soup.find(id=href[1:])
            require(target is not None, f'orphan fragment {href!r}')
            parent = a.find_parent(attrs={'data-fv-r415-journey':True})
            if parent is not None and target is not None:
                require(target.find_parent(attrs={'data-fv-r415-journey':True}) is parent,
                        f'cross-instance fragment {href!r}')
        else:
            require(False, f'unsupported link target {href!r}')
        if a.get('target') == '_blank':
            rel = a.get('rel', [])
            require('noopener' in rel and 'noreferrer' in rel, 'unsafe target=_blank')
        require(bool(a.get_text(' ', strip=True) or a.get('aria-label')),
                'link has no accessible text')
    for j, section in enumerate(journeys, 1):
        rail = section.select('.fv-r415__rail > li')
        cards = section.select('.fv-r414__card')
        require(len(rail) == 3, f'instance {j}: chronological milestones not 3')
        require(len(cards) == 6, f'instance {j}: historical records not 6')
        found_dates = tuple(x.get_text(' ',strip=True) for x in section.select('.fv-r415__date'))
        require(found_dates == EXPECTED_DATE_LABELS, f'instance {j}: historical date markers changed')
        texts = section.get_text(' ', strip=True)
        require('did not conclusively identify its ignition initiator' in texts,
                f'instance {j}: unresolved ignition boundary missing')
        require('102 separate, later deliberate ignitions' in texts,
                f'instance {j}: later tests not distinctly identified')
        require('NASA has not approved or endorsed' in texts,
                f'instance {j}: non-endorsement missing')
        require({BOARD,LATER,MIXED}.issubset({x.get('href') for x in section.select('a[href]')}),
                f'instance {j}: chronology source publications substituted')
        src = section.select('.fv-r414__card a[href]')
        src_urls = {a.get('href') for a in src}
        require(set(ARCHIVES).issubset(src_urls), f'instance {j}: a NASA archive record replaced')
        for i, c in enumerate(cards, 1):
            require(c.select_one('details > summary') is not None,
                    f'instance {j} card {i}: no native disclosure')
            require(bool(c.get_text(' ',strip=True)),f'instance {j} card {i}: empty evidence')
        ctas = [a for a in section.select('a[href]') if a['href'] == FREE]
        require(len(ctas) == 1, f'instance {j}: expected exactly one free investigation CTA')
        require(sum(1 for a in section.select('a[href]') if a.get('href') not in
                    (FREE,BOARD,LATER,MIXED,RIGHTS,*ARCHIVES) and not a.get('href','').startswith('#')) == 0,
                f'instance {j}: unreviewed third-party/paid navigation')
    return {
        'status':'PASS' if not faults else 'FAIL',
        'method':'static DOM/source-contract analysis on offline PHP-rendered fixture',
        'instances':len(journeys),'links':len(anchors),'document_ids':len(all_ids),
        'faults':sorted(set(faults)),
    }


def review_campaign(candidate: dict) -> dict:
    """An aligned UTM alone is *not* evidence a Grok post exists or generated sessions."""
    required = ('asset_id','post_url','landing_url','platform','source_review_url')
    missing = [x for x in required if not candidate.get(x)]
    if missing: return {'state':'HOLD','reason':'no independently authenticated published creator asset','missing':missing}
    u = urlsplit(str(candidate['landing_url']))
    params = parse_qs(u.query, keep_blank_values=True)
    match = (u.scheme=='https' and u.hostname=='finalvestige.com' and
             u.path.rstrip('/') == urlsplit(FREE).path.rstrip('/') and
             params.get('utm_source')==[candidate['platform']] and
             params.get('utm_medium')==['organic_social'] and
             params.get('utm_content')==[candidate['asset_id']] and
             len(params.get('utm_campaign',[]))==1 and
             bool(re.fullmatch(r'[a-z0-9][a-z0-9_\-]{3,70}',params['utm_campaign'][0])))
    return {'state':'REVIEW_REQUIRED' if match else 'HOLD',
            'reason':'syntactic campaign contract only; published post, rights, human sessions and attribution require external review' if match else 'landing mismatch, unsafe UTM, or incompatible destination',
            'publisher_verified':False}


def review_commerce(candidate: dict) -> dict:
    """The payload is untrusted. Never equate a receipt someone typed with a merchant settlement."""
    required = ('sku','seller_legal_name','sale_url','rights_manifest','fulfillment_proof',
                'refund_terms','merchant_report_url','independent_review')
    missing = [x for x in required if not candidate.get(x)]
    if missing:
        return {'state':'HOLD','missing':missing,'confirmed_orders':None,
                'net_revenue_per_1000_qualified_sessions':None}
    return {'state':'INDEPENDENT_MERCHANT_AND_RIGHTS_REVIEW_REQUIRED',
            'missing':[],'confirmed_orders':None,
            'net_revenue_per_1000_qualified_sessions':None}


def release_gate(markup: dict, browser: dict|None, signoffs: dict|None = None) -> dict:
    """Never grant automatic production approval from an isolated self-attested fixture."""
    signoffs=signoffs or {}
    outstanding = [
        'independent original-#158 source/media and QD review',
        'installed WordPress/Assembler staging browser evidence',
        'genuine axe-core WCAG 2.2 AA scan and screen reader review',
        'navigated HTTPS LCP/CLS and privacy/CSP acceptance',
        'founder production release authorization',
        'separately authenticated rights-cleared payable Apollo SKU for any paid CTA',
    ]
    if markup.get('status') != 'PASS': outstanding.insert(0,'integrated source/CTA structure FAILED')
    if not browser or browser.get('state')!='FIXTURE_PASS':
        outstanding.insert(0,'real offline Chromium fixture acceptance incomplete')
    # Consciously not treat signoffs as proof: external evidence and approved reviewer still required.
    return {'decision':'HARD_HOLD','reason':'no production or commercial authorization',
            'outstanding':outstanding, 'commercial_metrics':'NOT_COMPUTABLE',
            'browser_runtime':browser.get('runtime') if browser else 'NOT_EXECUTED',
            'claimed_release_approvals':bool(signoffs)}


def main() -> None:
    result = inspect_markup(render_fixture())
    output = {'dom':result,'campaign':review_campaign({}),
              'commerce':review_commerce({}), 'release':release_gate(result,None)}
    p=Path(__file__).resolve().parents[1]/'QA/source_offer_gate.json'
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(output,indent=2,sort_keys=True,ensure_ascii=False)+'\n',encoding='utf-8')
    print(f"R416 source contract: {result['status']}; production: HARD_HOLD; offer: HOLD")
    if result['status']!='PASS': raise SystemExit(1)

if __name__=='__main__': main()
