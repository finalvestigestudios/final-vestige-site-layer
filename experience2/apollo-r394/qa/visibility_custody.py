#!/usr/bin/env python3
"""R394 Apollo proof-visibility gate: read-only browser DOM evidence, no network calls.

Combines R393 exact NASA text/topology checks with evidence that source proofs,
chronology and the sole CTA are perceivable and pointer/keyboard reachable.
Intentionally does NOT claim to replace axe-core or human screen-reader review.
"""
import sys
from pathlib import Path

R393_QA=Path(__file__).resolve().parents[2] / 'apollo-r393' / 'qa'
if str(R393_QA) not in sys.path:
    sys.path.insert(0,str(R393_QA))
from topology import verify_page as verify_topology_page

# Only inspect reviewed evidence subtree. No user-data extraction or mutation.
VISIBILITY_JS=r'''() => {
 const root=document.querySelector('[data-fv-r384-gallery]');
 if(!root) return {absent:true};
 const checks=[
   {key:'gallery', el:root, interactive:false},
   {key:'rights', el:root.querySelector('.fv-r384__rights'), interactive:false},
   {key:'source_index', el:root.querySelector('.fv-r384__source-index'), interactive:false},
   {key:'chronology', el:root.querySelector('.fv-r384__rail'), interactive:false},
   ...[...root.querySelectorAll('[data-fv-r384-publication]')].map((el,i)=>({key:`publisher_${i+1}`,el,interactive:true})),
   ...[...root.querySelectorAll('.fv-r384__source-index a[href^="#"]')].map((el,i)=>({key:`index_link_${i+1}`,el,interactive:true})),
   ...[...root.querySelectorAll('.fv-r384__rail a')].map((el,i)=>({key:`rail_link_${i+1}`,el,interactive:true})),
   ...[...root.querySelectorAll('[data-fv-r384-record]')].map((el,i)=>({key:`record_${i+1}`,el,interactive:false})),
   ...[...root.querySelectorAll('[data-fv-r384-record] details summary')].map((el,i)=>({key:`drawer_${i+1}`,el,interactive:true})),
   ...[...root.querySelectorAll('[data-fv-r384-nasa]')].map((el,i)=>({key:`nasa_${i+1}`,el,interactive:true})),
   {key:'free_cta',el:root.querySelector('[data-fv-free-cta]'),interactive:true}
 ];
 const check=(item)=>{
    const el=item.el;
    if(!el) return {key:item.key, present:false};
    const box=el.getBoundingClientRect();
    let a=el,visible=true,clickable=true,reason=[];
    while(a){
       const css=getComputedStyle(a);
       if(a.hidden||a.inert||a.getAttribute('aria-hidden')==='true') {visible=false;reason.push('hidden_ancestor');}
       if(css.display==='none'||css.visibility==='hidden'||css.visibility==='collapse'||css.contentVisibility==='hidden') {visible=false;reason.push('css_hidden');}
       if(parseFloat(css.opacity)<0.05) {visible=false;reason.push('transparent');}
       if(/opacity\(\s*(0(?:\.0+)?|0?\.0{0,2}[1-4])\s*\)/.test(css.filter)) {visible=false;reason.push('filter_transparent');}
       if(css.clipPath==='inset(100%)'||css.clipPath==='circle(0%)') {visible=false;reason.push('clipped');}
       if(item.interactive&&css.pointerEvents==='none') {clickable=false;reason.push('pointer_blocked');}
       a=a.parentElement;
    }
    if(box.width<1||box.height<1) {visible=false;reason.push('zero_area');}
    // May be vertically below fold; horizontal offscreen is not an ordinary long-page position.
    if(box.right<=0||box.left>=window.innerWidth) {visible=false;reason.push('horizontally_offscreen');}
    if(item.interactive){
       const css=getComputedStyle(el);
       if(parseFloat(css.fontSize)<1) {visible=false;reason.push('zero_font');}
       if(el.getAttribute('aria-disabled')==='true') {clickable=false;reason.push('aria_disabled');}
       if(el.tabIndex<0) {clickable=false;reason.push('not_keyboard_reachable');}
       if(el.matches('a') && !el.hasAttribute('href')) {clickable=false;reason.push('missing_href');}
    }
    return {key:item.key,present:true,visible,clickable,reason:[...new Set(reason)]};
 };
 return {absent:false,checks:checks.map(check)};
}'''

REQUIRED_KEYS=tuple(['gallery','rights','source_index','chronology']+
 ['publisher_'+str(i) for i in range(1,3)]+
 ['index_link_'+str(i) for i in range(1,7)]+
 ['rail_link_'+str(i) for i in range(1,4)]+
 ['record_'+str(i) for i in range(1,7)]+
 ['drawer_'+str(i) for i in range(1,7)]+
 ['nasa_'+str(i) for i in range(1,7)]+['free_cta'])

def evaluate_visibility(snapshot):
    """Deterministic reason codes. Fails closed for absent/duplicate expected controls."""
    if snapshot.get('absent'):
        return False,['gallery_missing']
    items=snapshot.get('checks',[])
    keys=[item.get('key') for item in items]
    issues=[]
    if keys!=list(REQUIRED_KEYS):
        issues.append('proof_control_inventory_or_order')
    for item in items:
        key=item.get('key','unknown')
        if not item.get('present') or not item.get('visible'):
            issues.append(key+'_visually_unavailable')
        if key in REQUIRED_KEYS and (key.startswith(('publisher_','index_link_','rail_link_','drawer_','nasa_')) or key=='free_cta'):
            if not item.get('clickable'):
                issues.append(key+'_inoperable')
    return not issues,issues

def verify_page(page):
    prior_ok,prior_issues=verify_topology_page(page)
    new_ok,new_issues=evaluate_visibility(page.evaluate(VISIBILITY_JS))
    return prior_ok and new_ok, prior_issues+new_issues
