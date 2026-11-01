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
  const indexJumps=[...root.querySelectorAll('[data-fva-jump]')];
  const timeJumps=[...root.querySelectorAll('[data-fva-timejump]')];
  const jumps=[...indexJumps,...timeJumps];
  const citationList=root.querySelector('[data-fva-citations]');
  const citations=[...root.querySelectorAll('[data-fva-cite-id]')];
  const copyButtons=[...root.querySelectorAll('[data-fva-copy]')];
  const copyStatus=root.querySelector('[data-fva-copy-status]');
  if(!controls||!input||!reset||!status||!empty||cards.length!==6||buttons.length!==4||indexJumps.length!==6||timeJumps.length!==6||!citationList||citations.length!==6||copyButtons.length!==6||!copyStatus)return;
  let year='all';
  let active=false;
  const restore=()=>{
    cards.forEach(card=>{card.hidden=false;});
    controls.hidden=true;
    empty.hidden=true;
    copyButtons.forEach(b=>{b.hidden=true;});
    copyStatus.textContent='';
    status.textContent='';
    root.dataset.fvaReady='';
    if(active){buttons.forEach(b=>b.removeEventListener('click',onFilter));
      input.removeEventListener('input',apply);
      input.removeEventListener('keydown',onKey);
      reset.removeEventListener('click',onReset);
      jumps.forEach(link=>link.removeEventListener('click',onJump));
      copyButtons.forEach(b=>b.removeEventListener('click',onCopy));
      window.removeEventListener('hashchange',onHash);}
    active=false;
  };
  const valid=()=>{
    if(!cards.every((card,i)=>card.dataset.fvaId===expected[i]&&
        ['1966','1967','2017'].includes(card.dataset.fvaYear)&&
        card.id===`fva-record-${expected[i]}`&&
        indexJumps[i].getAttribute('href')===`#${card.id}`))return false;
    // The chronology must contain exactly one native permalink to every
    // custody record, grouped by the photograph's verified year (not geography).
    if(!citations.every((li,i)=>li.dataset.fvaCiteId===expected[i] &&
       li.querySelector('[data-fva-citation-text]')?.textContent.trim() &&
       copyButtons[i].closest('[data-fva-cite-id]')===li))return false;
    const seen=new Set();
    return timeJumps.every(link=>{
      const id=link.dataset.fvaTimeId;
      if(!expected.includes(id)||seen.has(id))return false;
      seen.add(id);
      const card=cards[expected.indexOf(id)];
      const era=link.closest('[data-fva-era]');
      return era && era.dataset.fvaEra===card.dataset.fvaYear&&
         link.getAttribute('href')===`#${card.id}`;
    })&&seen.size===6;
  };
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
  const onCopy=async event=>{
    const button=event.currentTarget;
    const row=button.closest('[data-fva-cite-id]');
    const citation=row?.querySelector('[data-fva-citation-text]')?.textContent?.trim();
    try{
      if(!valid()||!citation||!navigator.clipboard?.writeText)throw new Error('Citation not available');
      await navigator.clipboard.writeText(citation);
      copyStatus.textContent='Copied NASA source '+row.dataset.fvaCiteId+' citation.';
    }catch(_){
      copyStatus.textContent='Clipboard unavailable. Select the visible citation text to copy manually.';
    }
  };
  const onFilter=event=>{year=event.currentTarget.dataset.fvaFilter;apply();};
  const onReset=()=>{year='all';input.value='';apply();if(active)input.focus();};
  const onKey=event=>{if(event.key==='Escape'&&(input.value||year!=='all')){
    event.preventDefault();onReset();}};
  const revealTarget=target=>{
    // Native anchors are the no-JS fallback. Enhanced browsing must also
    // restore a record concealed by a user-selected filter before focusing it.
    if(target.hidden){year='all';input.value='';if(!apply())return;}
    requestAnimationFrame(()=>{if(active)target.focus({preventScroll:true});});
  };
  const onJump=event=>{
    const target=cards.find(card=>'#'+card.id===event.currentTarget.getAttribute('href'));
    if(target)revealTarget(target);
  };
  const onHash=()=>{
    const target=cards.find(card=>'#'+card.id===window.location.hash);
    if(target)revealTarget(target); // Covers back/forward navigation after filtering.
  };
  try{
    if(!valid())throw new Error('Source records missing');
    buttons.forEach(b=>b.addEventListener('click',onFilter));
    input.addEventListener('input',apply);
    input.addEventListener('keydown',onKey);
    reset.addEventListener('click',onReset);
    jumps.forEach(link=>link.addEventListener('click',onJump));
    copyButtons.forEach(b=>b.addEventListener('click',onCopy));
    window.addEventListener('hashchange',onHash);
    active=true;
    root.dataset.fvaReady='yes';
    // apply() can itself detect altered custody and roll back listeners.
    // Do not expose controls after that rollback (previously a stale live UI).
    if(apply() && active){
      controls.hidden=false;
      // Native citation text is always accessible. Copy is optional and only
      // exposed when the browser actually supports a clipboard API.
      if(typeof navigator.clipboard?.writeText==='function'){
        copyButtons.forEach(b=>{b.hidden=false;});
      }
      if(location.hash)onHash();
    }
  }catch(_){restore();}
})();
