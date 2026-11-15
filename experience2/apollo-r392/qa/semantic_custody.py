#!/usr/bin/env python3
"""Sealed, read-only semantic source custody gate for Apollo 1 staging and no-JS.
Not a substitute for independent editorial or deployed WordPress verification.
"""
import hashlib
import json
from pathlib import Path

CUSTODY_PATH=Path(__file__).resolve().parents[2]/'apollo-r377'/'custody.json'
CUSTODY_SHA256='60bfa330398b7684463c95afcc7e6ef347d44f22d5a2f1350286a660edb3a76f'
BOARD='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
TESTS='https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/'
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
RIGHTS='https://www.nasa.gov/nasa-brand-center/images-and-media/'
PHASES=('January 27, 1967 · the test and fire','1967 · what the Board could not prove',
        'December 1967–February 1968 · later testing')

def norm(s):
    return ' '.join((s or '').split())

def verified_records():
    data=CUSTODY_PATH.read_bytes()
    if hashlib.sha256(data).hexdigest()!=CUSTODY_SHA256:
        raise ValueError('HARD STOP: unreviewed Apollo research-custody file')
    root=json.loads(data)
    records=root.get('records')
    if (root.get('schema')!='fv.apollo.research-desk.source-custody.v1'
        or not isinstance(records,list) or len(records)!=6
        or [r.get('id') for r in records]!=['01-ground-test','02-oxygen','03-fire-sequence',
                                            '04-hatch','05-ignition','06-testing']):
        raise ValueError('HARD STOP: invalid custody schema, order or source count')
    return records

# Evaluation via Playwright DevTools works even with visitor JavaScript disabled.
# The inspector never clicks a CTA, fetches a remote source or mutates the DOM.
SNAPSHOT_JS="""() => {
  const all = (s, node=document) => Array.from(node.querySelectorAll(s));
  const t = (n) => n ? n.textContent : '';
  const field = (n,s) => t(n.querySelector(s));
  const link = (n) => n ? {href:n.getAttribute('href'),rel:n.getAttribute('rel')} : null;
  const gallery = document.querySelector('[data-fv-r384-gallery]');
  return {
    galleryCount:all('[data-fv-r384-gallery]').length,
    publicationCount:all('[data-fv-r384-publication]').length,
    publicationLinks:all('[data-fv-r384-publication]').map(link),
    sourceIndexText:t(document.querySelector('.fv-r384__source-index')),
    sourceIndexLinks:all('.fv-r384__source-index a[href^="#"]').map(link),
    phases:all('.fv-r384__phase').map(n=>({id:n.id,heading:field(n,'h3')})),
    phaseRail:all('.fv-r384__rail a').map(link),
    cards:all('[data-fv-r384-record]').map(n=>({
      id:n.id, sourceId:n.getAttribute('data-fv-r384-source-id'),
      heading:field(n,'h4'), kind:field(n,'.fv-r384__number'),
      claim:field(n,'p:has(strong)'),
      boundary:field(n,'.fv-r384__limit'),
      role:field(n,'.fv-r384__drawer p:nth-of-type(1)'),
      catalog:field(n,'.fv-r384__drawer p:nth-of-type(2)'),
      detailsCount:all('details',n).length,
      summary:field(n,'summary'),
      nasa:all('[data-fv-r384-nasa]',n).map(link)
    })),
    ctas:all('[data-fv-free-cta]').map(link),
    rightsText:t(document.querySelector('.fv-r384__rights')),
    rightsLinks:all('.fv-r384__rights a').map(link),
    sourceCount:all('[data-fv-r384-nasa]').length,
    unsafeMediaCount:all('[data-fv-r384-gallery] img, [data-fv-r384-gallery] video, [data-fv-r384-gallery] canvas, [data-fv-r384-gallery] iframe').length,
    duplicateIds:all('[id]').map(n=>n.id).filter((id,i,arr)=>id&&arr.indexOf(id)!==i),
    galleryText:t(gallery)
  };
}"""

def evaluate_snapshot(snapshot):
    """Return (PASS, fail codes); reject altered claims, proof boundaries and URLs."""
    records=verified_records()
    problems=[]
    def want(test,code):
        if not test: problems.append(code)
    want(snapshot.get('galleryCount')==1,'gallery_count')
    want(snapshot.get('publicationCount')==2,'publication_count')
    want(snapshot.get('sourceCount')==6,'nasa_source_link_count')
    want(snapshot.get('unsafeMediaCount')==0,'unexpected_media')
    want(not snapshot.get('duplicateIds'),'duplicate_element_ids')
    want(len(snapshot.get('ctas',[]))==1,'free_cta_count')
    if len(snapshot.get('ctas',[]))==1:
        want(snapshot['ctas'][0]['href']==FREE,'free_cta_destination')
    publications=snapshot.get('publicationLinks',[])
    want([v.get('href') for v in publications]==[BOARD,TESTS],'publisher_destinations_or_order')
    for item in publications:
        rel=(item.get('rel') or '').split()
        want('noopener' in rel and 'noreferrer' in rel,'publisher_rel')
    want('two underlying nasa publications' in snapshot.get('sourceIndexText','').lower(),'two_publication_disclosure')
    want('after' in snapshot.get('sourceIndexText','').lower(),'post_disaster_temporal_warning')
    phases=snapshot.get('phases',[])
    want([norm(p.get('heading')) for p in phases]==[norm(p) for p in PHASES], 'chronology_phase_headings')
    want(len(snapshot.get('phaseRail',[]))==3,'chronology_rail_count')
    phase_ids={v.get('id') for v in phases}
    want(all(a.get('href','').startswith('#') and a['href'][1:] in phase_ids for a in snapshot.get('phaseRail',[])), 'chronology_rail_targets')
    want(len(snapshot.get('sourceIndexLinks',[]))==6,'source_index_link_count')
    cards=snapshot.get('cards',[])
    want(len(cards)==6,'record_count')
    card_ids=[c.get('id') for c in cards]
    want(len(set(card_ids))==len(card_ids),'record_ids_unique')
    want(all(a.get('href','').startswith('#') and a['href'][1:] in card_ids for a in snapshot.get('sourceIndexLinks',[])), 'source_index_targets')
    for i,r in enumerate(records):
        if i>=len(cards): break
        c=cards[i]; prefix=f'record_{i+1}_'
        want(c.get('sourceId')==r['id'],prefix+'id')
        want(norm(c.get('heading'))==norm(r['heading']),prefix+'heading')
        want(norm(c.get('claim'))==norm('Document supports: '+r['claim']),prefix+'claim')
        want(norm(c.get('boundary'))==norm('Does not establish: '+r['boundary']),prefix+'boundary')
        want(norm(c.get('role'))==norm('Source role: '+r['evidence_role']),prefix+'source_role')
        want(norm(c.get('catalog'))==norm('What a photograph cannot prove: '+r['catalog_note']),prefix+'photo_limit')
        want(r['kind'] in c.get('kind',''),prefix+'classification')
        want(c.get('detailsCount')==1 and norm(c.get('summary'))=='Inspect custody and catalog limitations',prefix+'drawer')
        want(len(c.get('nasa',[]))==1 and c['nasa'][0].get('href')==r['evidence_url'],prefix+'source_url')
        if c.get('nasa'):
            rel=(c['nasa'][0].get('rel') or '').split()
            want('noopener' in rel and 'noreferrer' in rel,prefix+'source_rel')
    rights=snapshot.get('rightsText','').lower()
    want('not reproduced' in rights and 'not endorsed by nasa' in rights,'rights_nonendorsement_disclosure')
    want([a.get('href') for a in snapshot.get('rightsLinks',[])]==[RIGHTS],'rights_guidance_url')
    want('102 deliberate' in snapshot.get('galleryText','') and 'after' in snapshot.get('galleryText','').lower(), 'later_tests_causality_warning')
    return not problems,problems

def verify_page(page):
    return evaluate_snapshot(page.evaluate(SNAPSHOT_JS))
