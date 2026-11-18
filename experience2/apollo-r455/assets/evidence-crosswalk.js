/* Progressive enhancement, no analytics, cookies, storage, requests or third-party code. */
(()=>{'use strict';
function init(root){if(root.dataset.fv455Ready==='yes')return;
 const buttons=[...root.querySelectorAll('[data-fv455-filter]')];
 const cards=[...root.querySelectorAll('[data-fv455-kind]')];
 const status=root.querySelector('[data-fv455-status]');
 const exportButton=root.querySelector('[data-fv455-export]');
 if(buttons.length!==4||cards.length!==4||!status)return;
 const reset=()=>{cards.forEach(card=>{card.hidden=false;});buttons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.fv455Filter==='all')));status.textContent='All four evidence records available.';};
 try{
   buttons.forEach(button=>button.addEventListener('click',()=>{
     const kind=button.dataset.fv455Filter;
     if(!['all','investigation','context','later'].includes(kind)){reset();return;}
     let count=0;
     cards.forEach(card=>{card.hidden=kind!=='all'&&card.dataset.fv455Kind!==kind;if(!card.hidden)count++;});
     buttons.forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
     status.textContent=`${count} of ${cards.length} evidence records displayed.`;
   }));
   if(exportButton){exportButton.addEventListener('click',()=>{
      /* Text assembled from rendered source fields. Static text only; no input or private data. */
      const memo=['FINAL VESTIGE — APOLLO 1 EVIDENCE STUDY NOTE','Research aid, not NASA endorsement',''];
      cards.forEach(card=>{memo.push(card.querySelector('h4').textContent.trim());memo.push(card.querySelector('[data-fv455-supported]').textContent.trim());memo.push(card.querySelector('[data-fv455-limit]').textContent.trim());const link=card.querySelector('a[href^="https://www.nasa.gov/"]');if(link)memo.push('Source: '+link.href);memo.push('');});
      const blob=new Blob([memo.join('\n')],{type:'text/plain;charset=utf-8'});
      const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='fv-apollo-evidence-study.txt';a.style.display='none';document.body.appendChild(a);a.click();a.remove();URL.revokeObjectURL(url);
   });}
   root.dataset.fv455Ready='yes';root.classList.add('fv455--enhanced');
 }catch(_){reset();root.classList.remove('fv455--enhanced');root.dataset.fv455Ready='';}
}
function boot(){document.querySelectorAll('.fv455:not(.fv455--enhanced)').forEach(init)}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();
})();
