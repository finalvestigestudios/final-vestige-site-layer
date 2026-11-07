/* Apollo R179 — replacement-only source-custody search, staging, never co-load.
 * Historical records are readable without JS. Any optional search failure must
 * restore all six records, including warnings, before disabling search tools.
 * No analytics, network, persistence, mutation of source wording, or commerce.
 */
(()=>{'use strict';
 document.querySelectorAll('[data-fvx-ledger]').forEach(root=>{
  if(['yes','failed-open'].includes(root.dataset.fvxInitialized))return;
  const search=root.querySelector('[data-fvx-search]');
  const tools=root.querySelector('[data-fvx-tools]');
  const status=root.querySelector('[data-fvx-status]');
  const empty=root.querySelector('[data-fvx-empty]');
  const cards=Array.from(root.querySelectorAll('[data-fvx-record]'));
  if(!search||!tools||!status||!empty||cards.length!==6)return;
  let onInput=()=>{};
  const failOpen=()=>{
   // A half-filtered ledger must never become the only accessible evidence.
   try{search.removeEventListener('input',onInput);}catch(_){}
   cards.forEach(card=>{try{card.hidden=false;}catch(_){}});
   try{empty.hidden=true;}catch(_){}
   try{tools.hidden=true;}catch(_){}
   try{status.textContent='';}catch(_){}
   root.dataset.fvxInitialized='failed-open';
  };
  try{
   const clean=value=>String(value||'').normalize('NFKC').toLocaleLowerCase().replace(/\s+/g,' ').trim();
   const indexes=cards.map(card=>clean((card.dataset.fvxSearch||'')+' '+(card.textContent||'')));
   onInput=()=>{
    if(root.dataset.fvxInitialized==='failed-open')return;
    try{
     const needle=clean(search.value);
     let shown=0;
     cards.forEach((card,i)=>{
      const match=!needle||indexes[i].includes(needle);
      card.hidden=!match;
      if(match)shown++;
     });
     status.textContent=shown+' of '+cards.length+' evidence records';
     empty.hidden=shown!==0;
    }catch(_){failOpen();}
   };
   search.addEventListener('input',onInput);
   onInput();
   if(root.dataset.fvxInitialized==='failed-open')return;
   tools.hidden=false;
   root.dataset.fvxInitialized='yes';
  }catch(_){failOpen();}
 });
})();
