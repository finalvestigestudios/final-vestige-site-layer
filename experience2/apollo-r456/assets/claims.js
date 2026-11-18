/* Isolated enhancement. No network, cookies, storage, analytics or third-party code. */
(()=>{'use strict';
function boot(root){
 if(root.dataset.fv456Ready==='yes')return;
 const controls=root.querySelector('[data-fv456-controls]'),status=root.querySelector('[data-fv456-status]');
 const buttons=[...root.querySelectorAll('[data-fv456-select]')],cards=[...root.querySelectorAll('[data-fv456-case]')];
 if(!controls||!status||buttons.length!==4||cards.length!==3)return;
 const reset=()=>{cards.forEach(card=>{card.hidden=false});controls.hidden=true;status.textContent='All three claims and their supporting sources are available.';};
 try{
   buttons.forEach(button=>button.addEventListener('click',()=>{
      const choice=button.dataset.fv456Select;
      if(!['all','spark','memorial','tests'].includes(choice)){reset();return;}
      let visible=0;
      cards.forEach(card=>{card.hidden=choice!=='all'&&card.dataset.fv456Case!==choice;if(!card.hidden)visible++});
      buttons.forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
      status.textContent=choice==='all'?'All three sourced claims shown.':'Showing '+visible+' of 3 sourced claims.';
   }));
   root.dataset.fv456Ready='yes';controls.hidden=false;
 }catch(_){reset();root.dataset.fv456Ready='';}
}
function run(){document.querySelectorAll('[data-fv456-root]').forEach(boot)}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run,{once:true});else run();
})();
