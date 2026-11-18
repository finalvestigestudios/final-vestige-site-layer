/* Optional, scoped, no network/storage or injected HTML. All records readable without JS. */
(()=>{'use strict';
 for(const root of document.querySelectorAll('[data-r444-root]')){
  if(root.dataset.r444Ready==='yes')continue;
  const controls=root.querySelector('[data-r444-controls]');
  const records=[...root.querySelectorAll('[data-r444-record]')];
  const status=root.querySelector('[data-r444-count]');
  if(!controls||!status||records.length!==5)continue;
  const buttons=[...controls.querySelectorAll('button[data-r444-filter]')];
  if(buttons.length!==3)continue;
  try{
   const show=filter=>{
    let visible=0;
    for(const record of records){const on=filter==='all'||record.dataset.r444Period===filter;record.hidden=!on;if(on)visible++;}
    for(const b of buttons)b.setAttribute('aria-pressed',String(b.dataset.r444Filter===filter));
    status.textContent=`${visible} of ${records.length} source records shown`;
   };
   for(const b of buttons)b.addEventListener('click',()=>show(b.dataset.r444Filter));
   show('all');controls.hidden=false;root.dataset.r444Ready='yes';
  }catch(_){for(const r of records)r.hidden=false;controls.hidden=true;root.dataset.r444Ready='';}
 }
})();
