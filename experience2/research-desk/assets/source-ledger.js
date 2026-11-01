/* Optional, per-instance source search. No network, storage, third-party JS or HTML injection. */
(()=>{'use strict';
document.querySelectorAll('[data-fvx-ledger]').forEach(root=>{
 if(root.dataset.fvxInitialized==='yes')return;
 const search=root.querySelector('[data-fvx-search]');
 const tools=root.querySelector('[data-fvx-tools]');
 const status=root.querySelector('[data-fvx-status]');
 const cards=[...root.querySelectorAll('[data-fvx-record]')];
 const empty=root.querySelector('[data-fvx-empty]');
 if(!search||!tools||!status||!cards.length||!empty)return;
 const navigate=(event)=>{
   const link=event.target.closest('[data-fvx-chrono-link]');
   if(!link||!root.contains(link)||!search.value)return;
   search.value='';
   filter(); // restore hidden target before native anchor navigation
 };
 const restore=()=>{
   // If any card becomes malformed while filtering, retain the complete evidence.
   cards.forEach(card=>{card.hidden=false;});
   empty.hidden=true;
   tools.hidden=true;
   status.textContent='';
   root.dataset.fvxInitialized='';
   search.removeEventListener('input',filter);
   root.removeEventListener('click',navigate);
 };
 const filter=()=>{
   try{
     const needle=search.value.trim().toLocaleLowerCase();
     let shown=0;
     cards.forEach(card=>{
       const indexed=card.getAttribute('data-fvx-search');
       if(indexed===null)throw new Error('Missing source search index');
       const visible=!needle||indexed.toLocaleLowerCase().includes(needle);
       card.hidden=!visible;if(visible)shown++;
     });
     status.textContent=`${shown} of ${cards.length} evidence records`;
     empty.hidden=shown!==0;
   }catch(_){restore();}
 };
 try{
   search.addEventListener('input',filter);
   root.addEventListener('click',navigate);
   root.dataset.fvxInitialized='yes';
   filter();
   tools.hidden=root.dataset.fvxInitialized!=='yes';
 }catch(_){restore();}
});
})();
