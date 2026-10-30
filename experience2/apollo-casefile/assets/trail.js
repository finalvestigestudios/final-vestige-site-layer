/* Optional path selector. Native trail cards, links and disclosures always exist. */
(()=>{'use strict';const d=document,controls=d.querySelector('[data-ex2-trail-controls]'),select=d.querySelector('[data-ex2-trail-select]'),reset=d.querySelector('[data-ex2-trail-reset]'),status=d.querySelector('[data-ex2-trail-status]'),cards=[...d.querySelectorAll('[data-ex2-trail-card]')];
 if(!controls||!select||!reset||!status||cards.length!==6)return;
 const reveal=()=>{cards.forEach(x=>x.hidden=false);controls.hidden=true};
 try{
  const choose=()=>{const v=select.value;if(v!=='all'&&!/^0[1-6]$/.test(v))throw Error('Unknown audited route');const shown=cards.map(x=>v==='all'||x.id==='trail-'+v);if(!shown.some(Boolean))throw Error('Missing audited route');cards.forEach((c,i)=>c.hidden=!shown[i]);status.textContent=v==='all'?'All six trails visible':'Route '+v+' of six shown; choose All six source trails to restore the full record.'};
  const visit=()=>{const m=/^#trail-(0[1-6])$/.exec(location.hash);if(!m)return;const el=d.getElementById('trail-'+m[1]);if(!el)return;if(el.hidden){select.value='all';choose()}el.focus({preventScroll:true});el.scrollIntoView({block:'start',behavior:'auto'})};
  const safe=()=>{try{choose()}catch(_){reveal()}};
  select.addEventListener('change',safe);reset.addEventListener('click',()=>{select.value='all';safe();select.focus()});
  choose();controls.hidden=false;
  addEventListener('hashchange',()=>{try{visit()}catch(_){reveal()}});
  if(location.hash)queueMicrotask(()=>{try{visit()}catch(_){reveal()}});
 }catch(_){reveal()}
})();
