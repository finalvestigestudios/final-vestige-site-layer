/* R458 overlapping, source-scoped filters. No network, storage, cookies, analytics or inferred reuse permission. */
(()=>{'use strict';
function boot(root){if(root.dataset.fv457Ready)return;
 const controls=root.querySelector('[data-fv457-controls]'),status=root.querySelector('[data-fv457-status]');
 const cards=[...root.querySelectorAll('[data-fv457-card]')],buttons=[...root.querySelectorAll('[data-fv457-choice]')];
 if(!controls||!status||cards.length!==6||buttons.length!==4)return;
 const apply=choice=>{
  if(!['all','shown','homepage','withheld'].includes(choice))return;
  let visible=0;
  for(const c of cards){const show=choice==='all'||(choice==='homepage'?c.dataset.fv457Home==='confirmed':c.dataset.fv457Card===choice);c.hidden=!show;if(show)visible++;}
  buttons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.fv457Choice===choice)));
  status.textContent=`Showing ${visible} of ${cards.length} provenance records. Filters describe published-page placement, not image rights.`;
 };
 try{buttons.forEach(b=>b.addEventListener('click',()=>apply(b.dataset.fv457Choice)));root.dataset.fv457Ready='yes';controls.hidden=false;apply('all');}
 catch(_){cards.forEach(c=>c.hidden=false);controls.hidden=true;status.textContent='All six source records available.';}
}
function run(){document.querySelectorAll('[data-fv457-root]').forEach(boot)}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run,{once:true});else run();
})();
