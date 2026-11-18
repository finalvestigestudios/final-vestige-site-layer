/* Progressive disclosure only; no external requests, identifiers, cookies, analytics or storage. */
(()=>{'use strict';
 for(const root of document.querySelectorAll('[data-fv-r448]')){
   if(root.dataset.fvR448Ready==='yes')continue;
   const controls=root.querySelector('[data-fv-r448-controls]');
   const cards=Array.from(root.querySelectorAll('[data-fv-r448-card]'));
   const buttons=Array.from(root.querySelectorAll('[data-fv-r448-filter]'));
   const status=root.querySelector('[data-fv-r448-status]');
   if(!controls||cards.length!==4||buttons.length!==4||!status)continue;
   const known=new Set(['all','before','event','later']);
   const apply=era=>{
     if(!known.has(era))return;
     let count=0;
     for(const card of cards){const show=era==='all'||card.dataset.era===era;card.hidden=!show;if(show)count++;}
     for(const button of buttons)button.setAttribute('aria-pressed',String(button.dataset.fvR448Filter===era));
     status.textContent=`Showing ${count} of 4 evidence records`;
   };
   for(const button of buttons)button.addEventListener('click',()=>apply(button.dataset.fvR448Filter));
   apply('all');controls.hidden=false;root.dataset.fvR448Ready='yes';
 }
})();
