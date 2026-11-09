/* R231: index actual rendered evidence including NASA photo/source context; optional, no network. */
/* Self-contained, optional progressive enhancement. No network, storage, third-party JS or HTML injection. */
(()=>{'use strict';
document.querySelectorAll('[data-fvx-ledger]').forEach(root=>{
 if(root.dataset.fvxInitialized==='yes')return;
 const search=root.querySelector('[data-fvx-search]');
 const tools=root.querySelector('[data-fvx-tools]');
 const status=root.querySelector('[data-fvx-status]');
 const cards=[...root.querySelectorAll('[data-fvx-record]')];
 const empty=root.querySelector('[data-fvx-empty]');
 if(!search||!tools||!status||!cards.length||!empty)return;
 try{
   const filter=()=>{
     const needle=search.value.trim().toLocaleLowerCase();
     let shown=0;
     cards.forEach(card=>{
       const visible=!needle||(card.textContent||'').toLocaleLowerCase().includes(needle);
       card.hidden=!visible;if(visible)shown++;
     });
     status.textContent=`${shown} of ${cards.length} evidence records`;
     empty.hidden=shown!==0;
   };
   search.addEventListener('input',filter);
   root.dataset.fvxInitialized='yes';
   filter();
   tools.hidden=false;
 }catch(_){
   root.dataset.fvxInitialized='';
   cards.forEach(card=>card.hidden=false);
   tools.hidden=true;
   empty.hidden=true;
 }
});
})();
