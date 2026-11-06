/* FV Experience 2.0 / Apollo R153 — Research Desk PR #158 compatibility candidate.
 * Replaces, never co-loads, the R152 candidate or PR #158 source-ledger.js.
 * Progressive enhancement only. No network, storage, analytics, or CMS writes.
 */
(()=>{'use strict';
 for(const root of document.querySelectorAll('[data-fvx-ledger]')){
  if(root.dataset.fvxInitialized==='yes')continue;
  const search=root.querySelector('[data-fvx-search]');
  const tools=root.querySelector('[data-fvx-tools]');
  const status=root.querySelector('[data-fvx-status]');
  const cards=[...root.querySelectorAll('[data-fvx-record]')];
  const empty=root.querySelector('[data-fvx-empty]');
  if(!search||!tools||!status||!cards.length||!empty)continue;
  // PR #158 contains no Clear button and no data-fvx-chrono-link attributes.
  // Never require either to activate the six existing archival records.
  const indexesValid=cards.every(card=>card.id&&card.hasAttribute('data-fvx-search'));
  if(!indexesValid || new Set(cards.map(card=>card.id)).size!==cards.length)continue;
  let clear=root.querySelector('[data-fvx-clear]');
  let generated=false;
  if(!clear){
   clear=document.createElement('button');
   clear.type='button';clear.textContent='Clear search';
   clear.setAttribute('data-fvx-clear','');
   clear.hidden=true;
   search.insertAdjacentElement('afterend',clear);
   generated=true;
  }
  const revealAll=()=>cards.forEach(card=>{card.hidden=false;});
  const filter=()=>{
   const query=search.value.trim().toLocaleLowerCase();let count=0;
   cards.forEach(card=>{
    const indexed=card.getAttribute('data-fvx-search')||'';
    const match=!query||(`${indexed} ${card.textContent||''}`).toLocaleLowerCase().includes(query);
    card.hidden=!match;if(match)count++;
   });
   status.textContent=`${count} of ${cards.length} evidence records`;
   empty.hidden=count!==0;clear.hidden=!query;
  };
  const reset=focus=>{search.value='';filter();if(focus)search.focus();};
  const onEscape=e=>{if(e.key==='Escape'&&search.value){e.preventDefault();reset(true);}};
  const target=raw=>{
   let id=raw;
   try{id=decodeURIComponent(id);}catch(_){return null;}
   return cards.find(card=>card.id===id)||null;
  };
  const focusRecord=card=>{
   if(!card)return;
   if(card.hidden||search.value)reset(false);
   if(card.hidden)return;
   if(!card.hasAttribute('tabindex')){
    card.setAttribute('tabindex','-1');
    card.addEventListener('blur',()=>{if(card.isConnected)card.removeAttribute('tabindex');},{once:true});
   }
   card.focus({preventScroll:true});
   card.scrollIntoView({block:'start',behavior:'auto'});
  };
  const onHash=()=>focusRecord(target(window.location.hash.slice(1)));
  // Same-fragment links do not emit hashchange; capture navigation before
  // native anchor scrolling, even when links originate outside this component.
  const onAnchor=e=>{
   const a=e.target.closest('a[href]');if(!a)return;
   const href=a.getAttribute('href')||'';
   const hash=href.startsWith('#')?href.slice(1):null;
   if(hash===null)return;
   const card=target(hash);if(!card)return;
   if(card.hidden||search.value)reset(false);
   // Do not preventDefault or replace history: preserve native anchor semantics.
   queueMicrotask(()=>focusRecord(card));
  };
  const onClear=()=>reset(true);
  try{
   search.addEventListener('input',filter);
   search.addEventListener('keydown',onEscape);
   clear.addEventListener('click',onClear);
   document.addEventListener('click',onAnchor,true);
   window.addEventListener('hashchange',onHash);
   filter();root.dataset.fvxInitialized='yes';tools.hidden=false;
   if(target(window.location.hash.slice(1)))onHash();
  }catch(_){
   revealAll();empty.hidden=true;tools.hidden=true;
   root.dataset.fvxInitialized='';
   if(generated)clear.remove();
   search.removeEventListener('input',filter);
   search.removeEventListener('keydown',onEscape);
   clear.removeEventListener('click',onClear);
   document.removeEventListener('click',onAnchor,true);
   window.removeEventListener('hashchange',onHash);
  }
 }
})();
