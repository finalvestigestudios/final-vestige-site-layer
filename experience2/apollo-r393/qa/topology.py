#!/usr/bin/env python3
"""Read-only integrity gate for the Apollo source/chronology navigation graph.

R392 verified text and destination membership, but not the exact association
between an index item, its publication, the chronologically correct phase, and
its accessible label. This module additionally rejects invisible proof/CTAs.
It never follows source/checkout URLs, clicks links, or changes page state.
"""
import sys
from pathlib import Path

R392_QA = Path(__file__).resolve().parents[2] / 'apollo-r392' / 'qa'
if str(R392_QA) not in sys.path:
    sys.path.insert(0, str(R392_QA))
from semantic_custody import PHASES, norm, verified_records, verify_page as verify_semantic_page

TOPOLOGY_JS = r"""() => {
 const g=document.querySelector('[data-fv-r384-gallery]');
 if (!g) return {absent:true};
 const text=n=>n ? n.textContent.trim().replace(/\s+/g,' ') : '';
 const linked=(el,headingSelector)=>{
   const label=el?.getAttribute('aria-labelledby')||'';
   const target=label ? document.getElementById(label) : null;
   return {label, resolves:!!target, within:!!target && el.contains(target),
           heading:text(el?.querySelector(headingSelector)), resolvedText:text(target)};
 };
 const isPubliclyAvailable=el=>{
   if(!el) return false;
   for(let n=el;n;n=n.parentElement){
     if(n.hidden || n.inert || n.getAttribute('aria-hidden')==='true') return false;
     const cs=getComputedStyle(n);
     if(cs.display==='none' || cs.visibility==='hidden' || cs.visibility==='collapse') return false;
   }
   const r=el.getBoundingClientRect();
   return r.width > 0 && r.height > 0;
 };
 const phases=Array.from(g.querySelectorAll('.fv-r384__phase'));
 const groups=Array.from(g.querySelectorAll('.fv-r384__source-index .fv-r384__source-group'));
 const cards=Array.from(g.querySelectorAll('[data-fv-r384-record]'));
 const index=g.querySelector('.fv-r384__source-index');
 const nav=g.querySelector('.fv-r384__rail');
 const cta=g.querySelector('[data-fv-free-cta]');
 const pubs=Array.from(g.querySelectorAll('[data-fv-r384-publication]'));
 return {
  absent:false, galleryLabel:linked(g,'h2'),
  indexLabel:linked(index,'h3'),
  navLabel:nav?.getAttribute('aria-label'),
  groupNames:groups.map(el=>text(el.querySelector('h4'))),
  groupSourceLabels:groups.map(el=>Array.from(el.querySelectorAll('a[href^="#"]')).map(a=>({href:a.getAttribute('href'),text:text(a)}))),
  groupPublicationIds:groups.map(el=>Array.from(el.querySelectorAll('[data-fv-r384-publication]')).map(a=>a.getAttribute('data-fv-r384-publication'))),
  phaseInfo:phases.map(el=>({id:el.id,label:linked(el,'h3'),recordIds:Array.from(el.querySelectorAll('[data-fv-r384-record]')).map(n=>n.getAttribute('data-fv-r384-source-id'))})),
  rail:Array.from(nav?.querySelectorAll('a')||[]).map(a=>({href:a.getAttribute('href'),text:text(a)})),
  cardInfo:cards.map(el=>({id:el.id,sourceId:el.getAttribute('data-fv-r384-source-id'),
    parentPhase:el.closest('.fv-r384__phase')?.id||null,
    visible:isPubliclyAvailable(el), headingVisible:isPubliclyAvailable(el.querySelector('h4')),
    disclosureVisible:isPubliclyAvailable(el.querySelector('details summary')),
    sourceLinkVisible:isPubliclyAvailable(el.querySelector('[data-fv-r384-nasa]'))})),
  indexVisible:isPubliclyAvailable(index), navVisible:isPubliclyAvailable(nav),
  publicationLinksVisible:pubs.map(isPubliclyAvailable),
  ctaVisible:isPubliclyAvailable(cta), ctaInNext:!!cta?.closest('.fv-r384__next'),
  ctaName:text(cta), ctaClickable:!!cta && getComputedStyle(cta).pointerEvents!=='none'
 };
}"""

EXPECTED_GROUPS=(
 'Publication A · 1967 Apollo 204 Review Board',
 "Publication B · NASA's 2018 retrospective"
)
EXPECTED_PHASE_IDS=('event','finding','later')
EXPECTED_RECORD_PHASE=(0,0,0,0,1,2)


def evaluate_topology(snapshot):
    """Pure deterministic QA; returns (pass, stable failure codes)."""
    records=verified_records()
    bad=[]
    def want(condition,code):
        if not condition: bad.append(code)
    if snapshot.get('absent'):
        return False,['gallery_missing']
    def label_ok(data):
        return (data.get('resolves') and data.get('within') and
                norm(data.get('heading'))==norm(data.get('resolvedText')))
    want(label_ok(snapshot.get('galleryLabel',{})),'gallery_accessible_heading')
    want(label_ok(snapshot.get('indexLabel',{})),'index_accessible_heading')
    want(snapshot.get('navLabel')=='Three documented phases','rail_accessible_name')
    want(snapshot.get('groupNames')==list(EXPECTED_GROUPS),'publication_group_titles')
    want(snapshot.get('groupPublicationIds')==[['A'],['B']],'publication_group_custody')
    groups=snapshot.get('groupSourceLabels',[])
    cards=snapshot.get('cardInfo',[])
    phases=snapshot.get('phaseInfo',[])
    if len(cards)!=6: bad.append('card_topology_count')
    if len(groups)!=2: bad.append('publication_index_groups')
    else:
        expected=[[(f"#{cards[i]['id']}",f"Question {i+1} · {records[i]['heading']}") for i in range(5)] if len(cards)==6 else [],
                  [(f"#{cards[5]['id']}",f"Question 6 · {records[5]['heading']}")] if len(cards)==6 else []]
        for j in range(2):
            observed=[(a.get('href'),norm(a.get('text'))) for a in groups[j]]
            want(observed==expected[j],f'publication_{j+1}_link_order_and_labels')
    want(len(phases)==3,'phase_topology_count')
    if len(phases)==3 and len(cards)==6:
        expected_phase_records=[[],[],[]]
        for i,record in enumerate(records):
            expected_phase_records[EXPECTED_RECORD_PHASE[i]].append(record['id'])
        for i,p in enumerate(phases):
            want(label_ok(p.get('label',{})) and norm(p['label'].get('heading'))==norm(PHASES[i]),f'phase_{i+1}_accessible_heading')
            want(p.get('recordIds')==expected_phase_records[i],f'phase_{i+1}_membership')
        expected_rail=[{'href':'#'+p['id'],'text':norm(PHASES[i])} for i,p in enumerate(phases)]
        rail=[{'href':a.get('href'),'text':norm(a.get('text'))} for a in snapshot.get('rail',[])]
        want(rail==expected_rail,'chronology_rail_sequence_and_labels')
        for i,c in enumerate(cards):
            want(c.get('parentPhase')==phases[EXPECTED_RECORD_PHASE[i]].get('id'),f'record_{i+1}_phase_ownership')
            want(c.get('visible') and c.get('headingVisible') and
                 c.get('disclosureVisible') and c.get('sourceLinkVisible'),f'record_{i+1}_accessible_visibility')
    want(snapshot.get('indexVisible') and snapshot.get('navVisible'),'navigation_visibility')
    want(snapshot.get('publicationLinksVisible')==[True,True],'publisher_link_visibility')
    want(snapshot.get('ctaVisible') and snapshot.get('ctaInNext') and snapshot.get('ctaClickable')
         and norm(snapshot.get('ctaName'))=='Read the complete free Apollo 1 investigation','free_cta_operability')
    return not bad,bad


def verify_page(page):
    semantic_ok, semantic_errors=verify_semantic_page(page)
    topo_ok, topo_errors=evaluate_topology(page.evaluate(TOPOLOGY_JS))
    return semantic_ok and topo_ok, semantic_errors+topo_errors
