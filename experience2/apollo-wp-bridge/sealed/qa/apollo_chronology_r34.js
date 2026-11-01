/* R34: optional, fail-open year filter; never reorders or falsifies source dates. */
(()=>{'use strict';
  const panel=document.querySelector('.r34-chronology');
  const controls=panel&&panel.querySelector('[data-r34-controls]');
  const status=controls&&controls.querySelector('[data-r34-status]');
  const buttons=controls&&Array.from(controls.querySelectorAll('button[data-r34-year]'));
  const cards=Array.from(document.querySelectorAll('#apollo-r34-records > article[data-source-period]'));
  if(!panel||!controls||!status||!buttons||buttons.length!==4||cards.length!==6)return;
  const years=['all','1966','1967','2017'];
  if(buttons.some((button,i)=>button.dataset.r34Year!==years[i])||
     cards.some(card=>!['1966','1967','2017'].includes(card.dataset.sourcePeriod)))return;
  function reset(){cards.forEach(card=>card.hidden=false);buttons.forEach((button,i)=>button.setAttribute('aria-pressed',i===0?'true':'false'));controls.hidden=true;}
  function show(year){
    let count=0;
    cards.forEach(card=>{const visible=year==='all'||card.dataset.sourcePeriod===year;card.hidden=!visible;if(visible)count++;});
    buttons.forEach(button=>button.setAttribute('aria-pressed',button.dataset.r34Year===year?'true':'false'));
    status.textContent=year==='all'?`Showing all ${count} NASA photographic source records.`:
      `Showing ${count} of 6 NASA photographic source records dated ${year}.`;
  }
  try{
    // Fail before introducing any concealment unless the entire enhancement can attach.
    buttons.forEach(button=>button.addEventListener('click',()=>{try{show(button.dataset.r34Year)}catch(_){reset();}}));
    controls.hidden=false;
    show('all');
  }catch(_){reset();}
})();
