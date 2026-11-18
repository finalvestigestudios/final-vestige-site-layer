/* Progressive source-only controls. No cookies, storage, fetch, pixels or attribution claims. */
(()=>{'use strict';
 const all = () => document.querySelectorAll('[data-fv458-root]').forEach(root => {
  if(root.dataset.fv458Ready==='1')return;
  const tools=root.querySelector('[data-fv458-tools]'),buttons=[...root.querySelectorAll('[data-fv458-filter]')];
  const cards=[...root.querySelectorAll('[data-fv458-card]')],status=root.querySelector('[data-fv458-status]');
  if(!tools||!status||buttons.length!==4||cards.length!==6)return;
  const allowed=new Set(['all','recorded','reconcile','source_hold']);
  function show(which){
   if(!allowed.has(which))return;
   let count=0;
   cards.forEach(card=>{const yes=which==='all'||card.dataset.fv458Card===which;card.hidden=!yes;if(yes)count++;});
   buttons.forEach(btn=>btn.setAttribute('aria-pressed',String(btn.dataset.fv458Filter===which)));
   status.textContent=`Showing ${count} of 6 editorial source records. Filters do not constitute reuse approval.`;
  }
  try{
   buttons.forEach(btn=>btn.addEventListener('click',()=>show(btn.dataset.fv458Filter)));
   root.dataset.fv458Ready='1';tools.hidden=false;show('all');
  }catch(_){cards.forEach(card=>card.hidden=false);tools.hidden=true;status.textContent='All source records are available.';}
 });
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',all,{once:true});else all();
})();
