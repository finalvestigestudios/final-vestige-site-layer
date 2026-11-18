/* Optional progressive enhancement only; no storage, network or pixel tracking. */
(()=>{'use strict';
 for(const root of document.querySelectorAll('[data-fv-r447]')){
   if(root.dataset.r447Init==='yes') continue;
   const bar=root.querySelector('[data-fv-r447-controls]');
   const buttons=[...root.querySelectorAll('[data-fv-r447-filter]')];
   const cards=[...root.querySelectorAll('[data-fv-r447-card]')];
   const status=root.querySelector('[data-fv-r447-count]');
   if(!bar||buttons.length!==4||cards.length!==4||!status)continue;
   const filter=(era)=>{
     if(!['all','before','event','later'].includes(era))return;
     let shown=0;
     for(const card of cards){const visible=era==='all'||card.dataset.era===era;card.hidden=!visible;if(visible)shown++;}
     for(const button of buttons)button.setAttribute('aria-pressed',String(button.dataset.fvR447Filter===era));
     status.textContent=`${shown} of 4 source records`;
   };
   for(const button of buttons)button.addEventListener('click',()=>filter(button.dataset.fvR447Filter));
   filter('all');bar.hidden=false;root.dataset.r447Init='yes';
 }
})();
