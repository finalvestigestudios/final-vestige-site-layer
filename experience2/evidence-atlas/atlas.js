/* Optional Evidence Atlas filters. No fetch, analytics, geolocation, or storage. */
(()=>{'use strict';
  const root=document.querySelector('[data-fva-atlas]');
  if(!root||root.dataset.fvaReady==='yes')return;
  const controls=root.querySelector('[data-fva-controls]');
  const buttons=[...root.querySelectorAll('[data-fva-filter]')];
  const cards=[...root.querySelectorAll('[data-fva-record]')];
  const input=root.querySelector('[data-fva-search]');
  const reset=root.querySelector('[data-fva-reset]');
  const status=root.querySelector('[data-fva-status]');
  const empty=root.querySelector('[data-fva-empty]');
  const expected=['01','02','03','04','05','06'];
  if(!controls||!input||!reset||!status||!empty||cards.length!==6||buttons.length!==4)return;
  let year='all';
  let active=false;
  const restore=()=>{
    cards.forEach(card=>{card.hidden=false;});
    controls.hidden=true;
    empty.hidden=true;
    status.textContent='';
    root.dataset.fvaReady='';
    if(active){buttons.forEach(b=>b.removeEventListener('click',onFilter));
      input.removeEventListener('input',apply);
      input.removeEventListener('keydown',onKey);
      reset.removeEventListener('click',onReset);}
    active=false;
  };
  const valid=()=>cards.every((card,i)=>card.dataset.fvaId===expected[i]&&
       ['1966','1967','2017'].includes(card.dataset.fvaYear));
  const apply=()=>{
    try{
      if(!valid())throw new Error('Source record altered');
      const query=input.value.trim().toLocaleLowerCase();
      let count=0;
      cards.forEach(card=>{
        const matchYear=year==='all'||card.dataset.fvaYear===year;
        const matchText=!query||card.textContent.toLocaleLowerCase().includes(query);
        card.hidden=!(matchYear&&matchText);
        if(!card.hidden)count++;
      });
      buttons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.fvaFilter===year)));
      status.textContent=`${count} of 6 NASA photographic-source records shown`;
      empty.hidden=count!==0;
      return true;
    }catch(_){restore();return false;}
  };
  const onFilter=event=>{year=event.currentTarget.dataset.fvaFilter;apply();};
  const onReset=()=>{year='all';input.value='';apply();if(active)input.focus();};
  const onKey=event=>{if(event.key==='Escape'&&(input.value||year!=='all')){
    event.preventDefault();onReset();}};
  try{
    if(!valid())throw new Error('Source records missing');
    buttons.forEach(b=>b.addEventListener('click',onFilter));
    input.addEventListener('input',apply);
    input.addEventListener('keydown',onKey);
    reset.addEventListener('click',onReset);
    active=true;
    root.dataset.fvaReady='yes';
    // apply() can itself detect altered custody and roll back listeners.
    // Do not expose controls after that rollback (previously a stale live UI).
    if(apply() && active)controls.hidden=false;
  }catch(_){restore();}
})();
