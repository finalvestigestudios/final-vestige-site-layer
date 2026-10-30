/* Unintrusive Experience 2.0 enhancement. No network calls, cookies, telemetry or dependencies. */
(()=>{'use strict';
 const root=document;
 const tools=root.querySelector('[data-ex2-atlas-tools]');
 const search=root.querySelector('[data-ex2-atlas-search]');
 const filter=root.querySelector('[data-ex2-atlas-filter]');
 const items=[...root.querySelectorAll('[data-ex2-atlas-item]')];
 const count=root.querySelector('[data-ex2-atlas-status]');
 const empty=root.querySelector('[data-ex2-atlas-empty]');
 if(tools&&search&&filter&&count&&empty&&items.length){
   try{
     const update=()=>{
       const q=search.value.trim().toLocaleLowerCase();const theme=filter.value;
       let shown=0;
       items.forEach(item=>{const visible=(theme==='all'||item.dataset.ex2Theme===theme)&&(!q||item.dataset.ex2Search.includes(q));item.hidden=!visible;if(visible)shown++});
       count.textContent=`${shown} of ${items.length} investigations`;empty.hidden=shown!==0;
     };
     search.addEventListener('input',update);filter.addEventListener('change',update);
     update();tools.hidden=false;
   }catch(_){items.forEach(item=>item.hidden=false);empty.hidden=true;tools.hidden=true;}
 }
 /* The claims are evidence, not a JS-only feature. Filtering is optional and fail-open. */
 const claimTools=root.querySelector('[data-ex2-claim-tools]');
 const claimFilter=root.querySelector('[data-ex2-claim-filter]');
 const claimReset=root.querySelector('[data-ex2-claim-reset]');
 const claimItems=[...root.querySelectorAll('[data-ex2-claim-item]')];
 const claimCount=root.querySelector('[data-ex2-claim-count]');
 const claimEmpty=root.querySelector('[data-ex2-claim-empty]');
 if(claimTools&&claimFilter&&claimReset&&claimCount&&claimEmpty&&claimItems.length===6){
   try{
     const choose=()=>{
       const v=claimFilter.value;
       const visibility=claimItems.map(item=>v==='all'||item.dataset.ex2ClaimCategory===v);
       claimItems.forEach((item,i)=>{item.hidden=!visibility[i]});
       const shown=visibility.filter(Boolean).length;
       claimCount.textContent=shown+' of '+claimItems.length+' claims';
       claimEmpty.hidden=shown!==0;
     };
     claimFilter.addEventListener('change',choose);
     claimReset.addEventListener('click',()=>{claimFilter.value='all';choose();claimFilter.focus()});
     choose();claimTools.hidden=false;
   }catch(_){claimItems.forEach(item=>{item.hidden=false});claimEmpty.hidden=true;claimTools.hidden=true;}
 }
 /* Deep links must lead to an actually OPEN, keyboard-readable native source drawer.
    With scripts disabled the native details summary remains visible and operable. */
 const visitEvidenceHash=()=>{
   try{
     const hash=decodeURIComponent(window.location.hash.slice(1));
     if(!/^(source|custody)-(0[1-6])$/.test(hash))return;
     const target=root.getElementById(hash);
     if(!target)return;
     if(hash.startsWith('source-') && target.tagName==='DETAILS'){
       target.open=true;
       const summary=target.querySelector('summary');
       if(summary)summary.focus({preventScroll:true});
     }else if(hash.startsWith('custody-')){
       /* A deep-linked card may be hidden by the optional claim filter. Reveal it. */
       if(target.hidden && claimFilter){claimFilter.value='all';claimFilter.dispatchEvent(new Event('change',{bubbles:true}))}
       target.hidden=false;
       target.focus({preventScroll:true});
     }
     target.scrollIntoView({block:'start',behavior:'auto'});
   }catch(_){/* Linking must never erase or disable evidence. */}
 };
 try{
   window.addEventListener('hashchange',visitEvidenceHash);
   if(window.location.hash)queueMicrotask(visitEvidenceHash);
 }catch(_){/* Native anchors and details remain available. */}
 /* A missing/throwing IntersectionObserver must not hide or change any evidence. */
 const sections=[...root.querySelectorAll('[data-ex2-stage]')];
 const links=[...root.querySelectorAll('[data-ex2-rail-link]')];
 if(typeof IntersectionObserver!=='function'||sections.length!==6||links.length!==6)return;
 let observer;
 try{
   observer=new IntersectionObserver(entries=>{
     for(const entry of entries){if(!entry.isIntersecting)continue;
       links.forEach(link=>{if(link.hash===`#${entry.target.id}`){link.setAttribute('aria-current','location')}else{link.removeAttribute('aria-current')}});
     }
   },{rootMargin:'-10% 0px -65% 0px',threshold:0});
   sections.forEach(section=>observer.observe(section));
 }catch(_){if(observer)observer.disconnect();links.forEach(link=>link.removeAttribute('aria-current'));}
})();
