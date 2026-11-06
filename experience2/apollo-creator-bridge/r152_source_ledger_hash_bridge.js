/* FV Apollo R152: opt-in, isolated Research Desk navigation enhancement.
 * Candidate replacement for PR #158's source-ledger.js; do not load alongside it.
 * Keeps the six archival records in HTML, never fetches or stores visitor data.
 */
(()=>{'use strict';
 document.querySelectorAll('[data-fvx-ledger]').forEach(root=>{
  if(root.dataset.fvxInitialized==='yes')return;
  const search=root.querySelector('[data-fvx-search]');
  const tools=root.querySelector('[data-fvx-tools]');
  const status=root.querySelector('[data-fvx-status]');
  const cards=[...root.querySelectorAll('[data-fvx-record]')];
  const empty=root.querySelector('[data-fvx-empty]');
  const clear=root.querySelector('[data-fvx-clear]');
  if(!search||!tools||!status||!cards.length||!empty||!clear)return;
  const revealAll=()=>cards.forEach(card=>{card.hidden=false;});
  const restore=()=>{
   revealAll();empty.hidden=true;clear.hidden=true;tools.hidden=true;
   status.textContent='';root.dataset.fvxInitialized='';
   search.removeEventListener('input',filter);
   search.removeEventListener('keydown',onKeydown);
   clear.removeEventListener('click',clearSearch);
   root.removeEventListener('click',navigate);
   window.removeEventListener('hashchange',revealHash);
  };
  const filter=()=>{
   try{
    const needle=search.value.trim().toLocaleLowerCase();
    let shown=0;
    cards.forEach(card=>{
     const indexed=card.getAttribute('data-fvx-search');
     if(indexed===null)throw new Error('Missing source search index');
     const content=`${indexed} ${card.textContent||''}`.toLocaleLowerCase();
     card.hidden=!!needle&&!content.includes(needle);
     if(!card.hidden)shown++;
    });
    status.textContent=`${shown} of ${cards.length} evidence records`;
    empty.hidden=shown!==0;
    clear.hidden=!needle;
   }catch(_){restore();}
  };
  const clearSearch=()=>{
   search.value='';filter();
   if(root.dataset.fvxInitialized==='yes')search.focus();
  };
  const onKeydown=event=>{
   if(event.key==='Escape'&&search.value){event.preventDefault();clearSearch();}
  };
  // History navigation can arrive from a different component, Back/Forward,
  // another tab, or an anchor click. Never leave a target hidden by search.
  const targetFromHash=()=>{
   let hash=window.location.hash.slice(1);
   try{hash=decodeURIComponent(hash);}catch(_){return null;}
   return cards.find(card=>card.id===hash)||null;
  };
  const revealHash=()=>{
   const card=targetFromHash();
   if(!card)return;
   if(card.hidden||search.value){search.value='';filter();}
   if(card.hidden)return; // malformed indexes fail open in filter/restore
   // Focusing the restored article gives keyboard/screen-reader users a
   // meaningful landing point, without creating a normal tab stop.
   if(!card.hasAttribute('tabindex')){
    card.setAttribute('tabindex','-1');
    card.addEventListener('blur',()=>card.removeAttribute('tabindex'),{once:true});
   }
   card.focus({preventScroll:true});
   card.scrollIntoView({block:'start',behavior:'auto'});
  };
  const navigate=event=>{
   const link=event.target.closest('[data-fvx-chrono-link]');
   if(!link||!root.contains(link))return;
   const href=link.getAttribute('href')||'';
   if(!href.startsWith('#'))return;
   let id;try{id=decodeURIComponent(href.slice(1));}catch(_){return;}
   const card=cards.find(c=>c.id===id);
   if(!card)return;
   if(search.value||card.hidden){search.value='';filter();}
   // Native navigation is left intact; hashchange will focus the target.
  };
  try{
   search.addEventListener('input',filter);
   search.addEventListener('keydown',onKeydown);
   clear.addEventListener('click',clearSearch);
   root.addEventListener('click',navigate);
   window.addEventListener('hashchange',revealHash);
   root.dataset.fvxInitialized='yes';filter();
   tools.hidden=root.dataset.fvxInitialized!=='yes';
   // Hash might have been present when JS booted, or when returning to this view.
   if(targetFromHash())revealHash();
  }catch(_){restore();}
 });
})();
