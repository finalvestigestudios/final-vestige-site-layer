/* Optional Evidence Atlas filters. No fetch, analytics, geolocation, or storage. */
(()=>{'use strict';
  const root=document.querySelector('[data-fva-atlas]');
  if(!root||root.dataset.fvaReady==='yes')return;
  const controls=root.querySelector('[data-fva-controls]');
  const buttons=[...root.querySelectorAll('[data-fva-filter]')];
  const proofButtons=[...root.querySelectorAll('[data-fva-proof-filter]')];
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
  const citeJumps=[...root.querySelectorAll('[data-fva-to-citation]')];
  const backLinks=[...root.querySelectorAll('[data-fva-back-record]')];
  // Source citations are never filtered. Backlinks share the same fail-open
  // record-reveal behavior as source-index and chronology anchors.
  jumps.push(...backLinks);
  const copyButtons=[...root.querySelectorAll('[data-fva-copy]')];
  const copyStatus=root.querySelector('[data-fva-copy-status]');
  const exportButton=root.querySelector('[data-fva-export]');
  const exportStatus=root.querySelector('[data-fva-export-status]');
  const compare=root.querySelector('[data-fva-compare]');
  const compareStatus=root.querySelector('[data-fva-compare-status]');
  const compareClear=root.querySelector('[data-fva-compare-clear]');
  const compareSlots=[...root.querySelectorAll('[data-fva-compare-slot]')];
  const compareButtons=[...root.querySelectorAll('[data-fva-select]')];
  // R48: the optional same-page Research Desk bridge is admitted only after
  // independently matching all six *exact* source identities. This metadata
  // pin is a DOM-drift guard, not a defense against arbitrary hostile scripts.
  const pinned=[
    ['01','S67-19766','https://www.nasa.gov/image-detail/apollo-1-crew-honored/'],
    ['02','S67-15717','https://www.nasa.gov/image-detail/amf-s67-15717/'],
    ['03','S66-58038','https://www.nasa.gov/image-detail/amf-s66-58038/'],
    ['04','KSC-20170124-PH_KLS01_0164','https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/'],
    ['05','S67-21294','https://www.nasa.gov/image-detail/amf-s67-21294/'],
    ['06','KSC-20170124-PH_KLS01_0090','https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/']
  ];
  // R62: The ChronologyRail must not accept a plausible but *different* NASA
  // photographic date just because its year is in the allowed three-year set.
  // These six pairs come from the reviewed R37 custody crosswalk. They are not
  // the Apollo 1 fire/event chronology, and record 01 has no verified day.
  const pinnedDates=[
    ['01','1967','1967-01','January 1967; exact day not asserted'],
    ['02','1967','1967-01-03','January 3, 1967'],
    ['03','1966','1966-10-18','October 18, 1966'],
    ['04','2017','2017-01-24','January 24, 2017'],
    ['05','1967','1967-01-28','January 28, 1967'],
    ['06','2017','2017-01-24','January 24, 2017']
  ];
  // R66: every displayed SourceDrawer value is part of the reviewed source
  // custody, not merely a decorative caption. Pin ALL 54 dt/dd facts against
  // the exact R37 crosswalk and SHA-256-pinned R55 NASA-page audit. Earlier
  // validators checked only selected rights strings and permitted silent
  // alteration of credits, producing centers, dates and identity notes.
  // These are EDITORIAL DRIFT checks, not hostile-script security guarantees;
  // no photograph is licensed or embedded by this verification.
  const pinnedCustody=[["S67-19766","NASA-hosted image filename corroborates S67-19766; structured catalog metadata not separately confirmed","Not printed on the linked NASA page; attribution provisional.","NASA","No producing center displayed in reviewed metadata.","2023-03-26","NASA metadata reviewed 2026-11-01; no human link check or photograph inspection completed.",null,"crew portrait, not cabin/fire evidence. The photograph alone does not prove the cause or sequence of the Apollo 1 fire."],["S67-15717","Photo link verified; image-reuse review outstanding","Identifier displayed in the linked NASA page PIA field.","No individual image credit displayed in reviewed metadata.","JSC","2024-06-06","NASA metadata reviewed 2026-11-01; no human link check or photograph inspection completed.",null,"spacecraft preparation, not cabin-atmosphere evidence. The photograph alone does not prove the cause or sequence of the Apollo 1 fire."],["S66-58038","Photo link verified; image-reuse review outstanding","Identifier displayed in the linked NASA page PIA field.","No individual image credit displayed in reviewed metadata.","JSC","2024-06-06","NASA metadata reviewed 2026-11-01; no human link check or photograph inspection completed.",null,"earlier altitude-chamber rehearsal, not the fire. The photograph alone does not prove the cause or sequence of the Apollo 1 fire."],["KSC-20170124-PH_KLS01_0164","NASA/Kim Shiflett credit; image-reuse review outstanding","Identifier displayed in the linked NASA page PIA field.","NASA/Kim Shiflett","KSC","2023-05-04","NASA metadata reviewed 2026-11-01; no human link check or photograph inspection completed.",null,"2017 tribute hatch exhibit, not a 1967 accident scene. The photograph alone does not prove the cause or sequence of the Apollo 1 fire."],["S67-21294","Photo link verified; image-reuse review outstanding","Identifier displayed in the linked NASA page PIA field.","No individual image credit displayed in reviewed metadata.","JSC","2024-06-06","NASA metadata reviewed 2026-11-01; no human link check or photograph inspection completed.",null,"post-fire interior; cannot establish unique ignition mechanism. The photograph alone does not prove the cause or sequence of the Apollo 1 fire."],["KSC-20170124-PH_KLS01_0090","NASA/Kim Shiflett credit; image-reuse review outstanding","Identifier displayed in the linked NASA page PIA field.","NASA/Kim Shiflett","KSC","2024-06-12","NASA metadata reviewed 2026-11-01; no human link check or photograph inspection completed.",null,"2017 redesigned-hatch tribute exhibit, not the 1967 cabin. The photograph alone does not prove the cause or sequence of the Apollo 1 fire."]];
  const custodyLabels=['Catalog reference','Record identity note',
    'Catalog verification on NASA page','Credit displayed by NASA',
    'Producing center displayed by NASA','NASA page last updated',
    'Editorial source check','Reuse status','Documentary boundary'];
  const custodyIntact=()=>cards.every((card,i)=>{
    const drawer=card.querySelector('[data-fva-drawer]');
    if(!drawer||drawer.querySelectorAll('dl').length!==1)return false;
    const children=[...drawer.querySelector('dl').children];
    if(children.length!==custodyLabels.length*2)return false;
    return custodyLabels.every((name,j)=>{
      const label=children[j*2],value=children[j*2+1];
      return label?.tagName==='DT'&&label.textContent.trim()===name&&
        value?.tagName==='DD'&&value.textContent.trim()===(j===7
          ? 'Individual review required.'+' No photograph is reproduced here.'
          : pinnedCustody[i][j]);
    });
  });
  const deskLinks=[...root.querySelectorAll('[data-fva-to-desk]')];
  const deskStatus=root.querySelector('[data-fva-desk-status]');
  let desk=null;
  let deskRecords=[];
  // Optional reciprocal links belong to the Atlas enhancement, never to the
  // independently versioned Research Desk plugin or its static source HTML.
  const deskBacklinks=[];
  const removeDeskBacklinks=()=>{
    deskBacklinks.forEach(link=>link.remove());
    deskBacklinks.length=0;
  };
  if(!controls||!input||!reset||!status||!empty||cards.length!==6||buttons.length!==4||proofButtons.length!==3||indexJumps.length!==6||timeJumps.length!==6||!citationList||citations.length!==6||copyButtons.length!==6||citeJumps.length!==6||backLinks.length!==6||!copyStatus||!exportButton||!exportStatus||!compare||!compareStatus||!compareClear||compareSlots.length!==2||compareButtons.length!==6||deskLinks.length!==6||!deskStatus)return;
  let year='all';
  let proofFilter='all';
  let active=false;
  const selected=[];
  const restore=()=>{
    cards.forEach(card=>{card.hidden=false;});
    controls.hidden=true;
    empty.hidden=true;
    copyButtons.forEach(b=>{b.hidden=true;});
    compareButtons.forEach(b=>{b.hidden=true;b.setAttribute('aria-pressed','false');});
    selected.length=0;
    compareSlots.forEach(slot=>slot.replaceChildren());
    compareClear.hidden=true;
    compare.hidden=true;
    compareStatus.textContent='';
    copyStatus.textContent='';
    exportButton.hidden=true;
    exportStatus.textContent='';
    status.textContent='';
    deskLinks.forEach(link=>{link.hidden=true;link.removeEventListener('click',onDeskJump);});
    removeDeskBacklinks();
    deskStatus.hidden=true;
    deskStatus.textContent='';
    desk=null;deskRecords=[];
    root.dataset.fvaReady='';
    if(active){buttons.forEach(b=>b.removeEventListener('click',onFilter));
      proofButtons.forEach(b=>b.removeEventListener('click',onProofFilter));
      input.removeEventListener('input',apply);
      input.removeEventListener('keydown',onKey);
      reset.removeEventListener('click',onReset);
      jumps.forEach(link=>link.removeEventListener('click',onJump));
      copyButtons.forEach(b=>b.removeEventListener('click',onCopy));
      exportButton.removeEventListener('click',onExport);
      compareButtons.forEach(b=>b.removeEventListener('click',onSelect));
      compareClear.removeEventListener('click',onClearSelection);
      compare.removeEventListener('click',onCompareJump);
      window.removeEventListener('hashchange',onHash);}
    active=false;
  };
  const valid=()=>{
    if(!cards.every((card,i)=>card.dataset.fvaId===expected[i]&&
        card.dataset.fvaCatalogState===(i===0?'provisional':'page-displayed')&&
        ['1966','1967','2017'].includes(card.dataset.fvaYear)&&
        card.id===`fva-record-${expected[i]}`&&
        indexJumps[i].getAttribute('href')===`#${card.id}`))return false;
    // The chronology must contain exactly one native permalink to every
    // custody record, grouped by the photograph's verified year (not geography).
    if(!citations.every((li,i)=>li.dataset.fvaCiteId===expected[i] &&
       li.id===`fva-citation-${expected[i]}` &&
       li.querySelector('[data-fva-citation-text]')?.textContent.trim() &&
       citeJumps[i].closest('[data-fva-record]')===cards[i] &&
       citeJumps[i].getAttribute('href')===`#${li.id}` &&
       backLinks[i].closest('[data-fva-cite-id]')===li &&
       backLinks[i].getAttribute('href')===`#${cards[i].id}` &&
       copyButtons[i].closest('[data-fva-cite-id]')===li &&
       compareButtons[i].closest('[data-fva-record]')===cards[i] &&
       compareButtons[i].dataset.fvaSelect===expected[i]))return false;
    // A source URL and its citation could otherwise be altered together and
    // pass a mere cross-reference consistency check. Pin each original NASA
    // destination and catalog against immutable build-reviewed metadata.
    if(!pinned.every(([id,catalog,url],i)=>
        cards[i].dataset.fvaId===id &&
        cards[i].querySelector('.fva-card__plate span')?.textContent.trim()===catalog &&
        cards[i].querySelector('.fva-card__external')?.getAttribute('href')===url &&
        citations[i].querySelector('[data-fva-citation-text]')?.textContent.includes(catalog) &&
        citations[i].querySelector('[data-fva-citation-text]')?.textContent.includes(url) &&
        deskLinks[i].closest('[data-fva-record]')===cards[i] &&
        deskLinks[i].getAttribute('href')===`#fv-ex2-ledger-apollo1-record-${id}`))return false;
    // A forged date label could previously flow into the source comparison
    // or a chronology jump without invalidating the interactive view. Require
    // complete agreement across source card, time element, era and citation.
    if(!pinnedDates.every(([id,year,iso,label],i)=>{
      const record=cards[i];
      const link=timeJumps.find(jump=>jump.dataset.fvaTimeId===id);
      const time=link?.querySelector('time');
      const text=citations[i].querySelector('[data-fva-citation-text]')?.textContent;
      return record.dataset.fvaYear===year &&
        record.querySelector('.fva-card__date span')?.textContent.trim()===label &&
        link?.closest('[data-fva-era]')?.dataset.fvaEra===year &&
        time?.getAttribute('datetime')===iso &&
        time?.textContent.trim()===label &&
        text?.includes('photograph date '+label);
    }))return false;
    // Withdraw optional filters/export/comparison if ANY custody value drifts.
    // Original native source disclosures and complete citations stay readable.
    if(!custodyIntact())return false;
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

  // Verify a single Research Desk root before revealing shortcuts. Both pages
  // remain useful independently. No external requests or altered Desk files.
  const verifyDesk=()=>{
    const roots=[...document.querySelectorAll('[data-fvx-ledger]')];
    if(roots.length!==1)return null;
    const candidate=roots[0];
    const records=[...candidate.querySelectorAll('[data-fvx-record]')];
    if(records.length!==6)return null;
    if(!pinned.every(([id,catalog,url],i)=>{
      const record=records[i];
      const photoLinks=[...record.querySelectorAll('a[href^="https://www.nasa.gov/image-detail/"]')];
      const optionalIds=[...record.querySelectorAll('[data-fvx-photo-record]')];
      return record.id===`fv-ex2-ledger-apollo1-record-${id}` &&
        record.querySelector('.fv-ex2-ledger__recordid')?.textContent.includes(catalog) &&
        photoLinks.length===1 && photoLinks[0].getAttribute('href')===url &&
        (optionalIds.length===0 || (optionalIds.length===1 && optionalIds[0].dataset.fvxPhotoRecord===id));
    }))return null;
    return {root:candidate,records};
  };
  const withdrawDesk=(explain=false)=>{
    deskLinks.forEach(link=>{link.hidden=true;});
    removeDeskBacklinks();
    desk=null;deskRecords=[];
    if(explain){
      deskStatus.textContent='Research Desk shortcuts are unavailable. All six original NASA references remain above.';
      deskStatus.hidden=false;
    }
  };
  const onDeskJump=event=>{
    // Recheck immediately before navigating: the other component could have
    // changed independently after the Atlas finished loading.
    const proof=verifyDesk();
    const link=event.currentTarget;
    const id=link.closest('[data-fva-record]')?.dataset.fvaId;
    const target=proof?.records[expected.indexOf(id)];
    if(!valid()||!proof||!target){
      event.preventDefault();withdrawDesk(true);return;
    }
    if(target.hidden){
      const search=proof.root.querySelector('[data-fvx-search]');
      if(search){search.value='';search.dispatchEvent(new Event('input',{bubbles:true}));}
    }
    if(target.hidden){event.preventDefault();withdrawDesk(true);return;}
    // The Research Desk's record elements are normally not keyboard focusable.
    // Temporarily set tabindex without modifying its source or listener code.
    target.setAttribute('tabindex','-1');
    requestAnimationFrame(()=>target.focus({preventScroll:true}));
  };
  const onDeskBackJump=event=>{
    // A late source mutation must not leave a misleading shortcut available.
    const proof=verifyDesk();
    const link=event.currentTarget;
    const id=link.dataset.fvxToAtlas;
    const index=expected.indexOf(id);
    if(!valid()||!proof||index<0||proof.records[index].querySelector('.fv-ex2-ledger__recordlinks')!==link.parentElement ||
       cards[index].id!==link.getAttribute('href').slice(1)){
      event.preventDefault();withdrawDesk(true);return;
    }
    revealTarget(cards[index]);
  };
  const initDesk=()=>{
    const proof=verifyDesk();
    if(!proof){withdrawDesk();return;}
    desk=proof.root;deskRecords=proof.records;
    deskLinks.forEach(link=>{link.hidden=false;link.addEventListener('click',onDeskJump);});
    // Legacy PR #158 contains one recordlinks container per card but no
    // back-navigation. Enhance it only when all six eligible slots exist.
    // Synthesized, incomplete or duplicated records never get partial links.
    const slots=proof.records.map(record=>record.querySelector('.fv-ex2-ledger__recordlinks'));
    if(slots.every(Boolean) && slots.every(slot=>!slot.querySelector('[data-fvx-to-atlas]'))){
      expected.forEach((id,i)=>{
        const link=document.createElement('a');
        link.setAttribute('data-fvx-to-atlas',id);
        link.href='#'+cards[i].id;
        link.textContent='Open photographic record '+id+' in Evidence Atlas';
        link.addEventListener('click',onDeskBackJump);
        slots[i].appendChild(link);
        deskBacklinks.push(link);
      });
    }
  };
  const apply=()=>{
    try{
      if(!valid())throw new Error('Source record altered');
      const query=input.value.trim().toLocaleLowerCase();
      let count=0;
      cards.forEach(card=>{
        const matchYear=year==='all'||card.dataset.fvaYear===year;
        const matchProof=proofFilter==='all'||card.dataset.fvaCatalogState===proofFilter;
        const matchText=!query||card.textContent.toLocaleLowerCase().includes(query);
        card.hidden=!(matchYear&&matchProof&&matchText);
        if(!card.hidden)count++;
      });
      buttons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.fvaFilter===year)));
      proofButtons.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.fvaProofFilter===proofFilter)));
      status.textContent=`${count} of 6 NASA photographic-source records shown`;
      empty.hidden=count!==0;
      return true;
    }catch(_){restore();return false;}
  };
  // R46: source-pair inspection is an optional derived VIEW of already printed
  // NASA metadata. Text-only DOM APIs prevent accidental unsourced HTML injection.
  // No metadata is loaded from a network, and the two photos are not asserted
  // to depict the same place, event, cause, or moment.
  const updateComparison=()=>{
    compareSlots.forEach((slot,i)=>{
      slot.replaceChildren();
      const id=selected[i];
      if(!id)return;
      const card=cards[expected.indexOf(id)];
      const catalog=card.querySelector('.fva-card__plate span')?.textContent?.trim();
      const date=card.querySelector('.fva-card__date span')?.textContent?.trim();
      const role=card.querySelector('h2')?.textContent?.trim();
      if(!catalog||!date||!role)throw new Error('Source content missing');
      const heading=document.createElement('h3');
      heading.textContent='NASA record '+id+' · '+catalog;
      const dateLine=document.createElement('p');
      dateLine.textContent='Photograph date: '+date;
      const scope=document.createElement('p');
      scope.textContent='Documentary scope: '+role;
      const rights=document.createElement('p');
      rights.textContent='Photograph reuse: individual review required.';
      const link=document.createElement('a');
      link.href='#'+card.id;
      link.textContent='Read full source custody for record '+id;
      slot.append(heading,dateLine,scope,rights,link);
    });
    compareButtons.forEach(b=>b.setAttribute('aria-pressed',String(selected.includes(b.dataset.fvaSelect))));
    compareClear.hidden=selected.length===0;
    compareStatus.textContent=selected.length===0?'No records selected.':
      selected.length===1?'One source selected. Choose another NASA record to compare documented metadata.':
      'Two NASA records selected. Comparison is metadata-only, not evidence of a historical connection.';
  };
  const onSelect=event=>{
    try{
      if(!valid())throw new Error('Source index altered');
      const id=event.currentTarget.dataset.fvaSelect;
      const existing=selected.indexOf(id);
      if(existing!==-1)selected.splice(existing,1);
      else{if(selected.length===2)selected.shift();selected.push(id);}
      updateComparison();
    }catch(_){restore();}
  };
  const onClearSelection=()=>{
    selected.length=0;
    try{updateComparison();}catch(_){restore();}
  };
  const onCompareJump=event=>{
    const link=event.target.closest('a[href^="#fva-record-"]');
    if(!link||!compare.contains(link))return;
    const target=cards.find(card=>'#'+card.id===link.getAttribute('href'));
    if(target)revealTarget(target);
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
  // R47: local, metadata-only archival citation export. We derive every line
  // from the six visible original source citations, not filtered cards or a
  // remote API. No image binaries, location metadata, or license assumptions.
  // A mismatched NASA source/citation immediately withdraws this enhancement.
  // R58: preserve the six complete *on-page* source-custody disclosures in the
  // downloadable text sheet, not just the older catalog/date/URL citations.
  // This copies reviewed static HTML into plain text; it does not clear rights,
  // fetch NASA data, or invent extra metadata. On tampering, the download is
  // refused and the always-readable native source drawers remain accessible.
  const custodyFields=[
    'Catalog reference','Record identity note','Catalog verification on NASA page',
    'Credit displayed by NASA','Producing center displayed by NASA',
    'NASA page last updated','Editorial source check','Reuse status',
    'Documentary boundary'
  ];
  const sourceCustody=(card,id,catalog)=>{
    const drawer=card.querySelector('[data-fva-drawer]');
    if(!drawer||drawer.querySelectorAll('dl').length!==1)throw new Error('Custody drawer missing');
    const dl=drawer.querySelector('dl');
    const children=[...dl.children];
    if(children.length!==custodyFields.length*2)throw new Error('Incomplete source custody');
    const fields=[];
    custodyFields.forEach((name,i)=>{
      const label=children[i*2],value=children[i*2+1];
      const txt=value?.textContent?.trim();
      if(label?.tagName!=='DT'||label.textContent.trim()!==name||
         value?.tagName!=='DD'||!txt)throw new Error('Custody field drift');
      fields.push(txt);
    });
    if(fields[0]!==catalog ||
       fields[2]!== (id==='01'
         ? 'Not printed on the linked NASA page; attribution provisional.'
         : 'Identifier displayed in the linked NASA page PIA field.') ||
       fields[6].indexOf('no human link check or photograph inspection completed.')<0 ||
       fields[7]!==('Individual review required.'+' No photograph is reproduced here.') ||
       fields[8].indexOf('does not prove the cause or sequence')<0){
      throw new Error('Custody claims changed');
    }
    return custodyFields.map((name,i)=>'    '+name+': '+fields[i]);
  };
  const sourceRegister=()=>{
    if(!valid())throw new Error('Source register failed validation');
    const lines=[];
    expected.forEach((id,i)=>{
      const source=cards[i].querySelector('.fva-card__external');
      const catalog=cards[i].querySelector('.fva-card__plate span')?.textContent?.trim();
      const citation=citations[i].querySelector('[data-fva-citation-text]')?.textContent?.trim();
      const href=source?.getAttribute('href');
      let url;
      try{url=new URL(href);}catch(_){throw new Error('Invalid NASA source URL');}
      if(url.protocol!=='https:'||url.hostname!=='www.nasa.gov'||
         url.pathname.indexOf('/image-detail/')!==0||!catalog||
         !citation||!citation.includes(catalog)||!citation.includes(href)||
         !citation.includes('individual review required')){
        throw new Error('Citation/source mismatch');
      }
      lines.push(id+'. '+citation);
      lines.push('  Source custody disclosure (editorial metadata; NOT rights clearance):');
      lines.push(...sourceCustody(cards[i],id,catalog));
      lines.push('');
    });
    return ['FINAL VESTIGE STUDIOS — APOLLO 1 EVIDENCE ATLAS',
      'NASA photographic-source reference AND CUSTODY register — STAGING ONLY',
      'Six source links; no photographs are reproduced. NASA does not endorse this publication.',
      'Image reuse: six individual photo-rights reviews are outstanding.',
      'Metadata is transcribed from the linked NASA-page source notes and has NOT received a human link or image-rights check.',
      'Dates identify source photographs, not the sequence or causes of the fire.',
      'January 1967 photograph S67-19766 has no independently verified day or confirmed catalog-to-photo match.',
      'Every entry is a source reference, not a reproduction license.',
      '',...lines,
      'Primary technical investigation: '+root.querySelector('.fva-guide a')?.getAttribute('href'),
      'NASA media guidance: '+root.querySelector('.fva-footer a')?.getAttribute('href'),
      ''].join('\n');
  };
  const onExport=()=>{
    let link,blobUrl;
    try{
      const text=sourceRegister();
      if(typeof Blob!=='function'||typeof URL.createObjectURL!=='function')throw new Error('Download unsupported');
      blobUrl=URL.createObjectURL(new Blob([text],{type:'text/plain;charset=utf-8'}));
      link=document.createElement('a');
      link.href=blobUrl;
      link.download='apollo-1-nasa-source-register.txt';
      link.style.display='none';
      root.appendChild(link);
      link.click();
      exportStatus.textContent='Six NASA citations and source-custody disclosures prepared for download; rights reviews remain pending.';
    }catch(_){
      exportStatus.textContent='Download unavailable. All six citations remain readable below, or print the complete register.';
    }finally{
      if(link)link.remove();
      if(blobUrl){setTimeout(()=>URL.revokeObjectURL(blobUrl),5000);}
    }
  };
  const onFilter=event=>{year=event.currentTarget.dataset.fvaFilter;apply();};
  const onProofFilter=event=>{proofFilter=event.currentTarget.dataset.fvaProofFilter;apply();};
  const onReset=()=>{year='all';proofFilter='all';input.value='';apply();if(active)input.focus();};
  const onKey=event=>{if(event.key==='Escape'&&(input.value||year!=='all'||proofFilter!=='all')){
    event.preventDefault();onReset();}};
  const revealTarget=target=>{
    // Native anchors are the no-JS fallback. Enhanced browsing must also
    // restore a record concealed by a user-selected filter before focusing it.
    if(target.hidden){year='all';proofFilter='all';input.value='';if(!apply())return;}
    requestAnimationFrame(()=>{if(active)target.focus({preventScroll:true});});
  };
  const onJump=event=>{
    const target=cards.find(card=>'#'+card.id===event.currentTarget.getAttribute('href'));
    if(target)revealTarget(target);
  };
  // R61: a browser-history or pasted #Research-Desk-record fragment is not a
  // click on an Atlas shortcut. Before this handler, changing the hash while a
  // Desk search hid that record silently landed on invisible historical proof.
  // Revalidate the ENTIRE Desk against the reviewed six-source crosswalk first;
  // do not manufacture missing content or bypass a failed source-custody gate.
  const onDeskHash=hash=>{
    const match=/^#fv-ex2-ledger-apollo1-record-(0[1-6])$/.exec(hash);
    if(!match)return false;
    const index=expected.indexOf(match[1]);
    const proof=verifyDesk();
    if(!valid()||!proof||index<0){withdrawDesk(true);return true;}
    const target=proof.records[index];
    if(target.hidden){
      const search=proof.root.querySelector('[data-fvx-search]');
      if(search){
        search.value='';
        search.dispatchEvent(new Event('input',{bubbles:true}));
      }
    }
    if(target.hidden){withdrawDesk(true);return true;}
    // No synthetic hash changes; let native anchor scrolling occur. Set
    // programmatic focus only after visibility has been restored, preserving
    // keyboard/screen-reader continuity without changing reviewed R38 bytes.
    target.setAttribute('tabindex','-1');
    requestAnimationFrame(()=>{
      if(active&&target.isConnected&&!target.hidden)target.focus({preventScroll:true});
    });
    return true;
  };
  const onHash=()=>{
    // History navigation is itself an enhancement: recheck custody even when
    // the destination is already visible, not only when a filter is cleared.
    if(!valid()){restore();return;}
    if(onDeskHash(window.location.hash))return;
    const target=cards.find(card=>'#'+card.id===window.location.hash);
    if(target)revealTarget(target); // Covers back/forward navigation after filtering.
  };
  try{
    if(!valid())throw new Error('Source records missing');
    buttons.forEach(b=>b.addEventListener('click',onFilter));
    proofButtons.forEach(b=>b.addEventListener('click',onProofFilter));
    input.addEventListener('input',apply);
    input.addEventListener('keydown',onKey);
    reset.addEventListener('click',onReset);
    jumps.forEach(link=>link.addEventListener('click',onJump));
    copyButtons.forEach(b=>b.addEventListener('click',onCopy));
    exportButton.addEventListener('click',onExport);
    compareButtons.forEach(b=>b.addEventListener('click',onSelect));
    compareClear.addEventListener('click',onClearSelection);
    compare.addEventListener('click',onCompareJump);
    window.addEventListener('hashchange',onHash);
    active=true;
    root.dataset.fvaReady='yes';
    // apply() can itself detect altered custody and roll back listeners.
    // Do not expose controls after that rollback (previously a stale live UI).
    if(apply() && active){
      controls.hidden=false;
      compare.hidden=false;
      exportButton.hidden=false;
      compareButtons.forEach(b=>{b.hidden=false;});
      updateComparison();
      initDesk();
      // Native citation text is always accessible. Copy is optional and only
      // exposed when the browser actually supports a clipboard API.
      if(typeof navigator.clipboard?.writeText==='function'){
        copyButtons.forEach(b=>{b.hidden=false;});
      }
      if(location.hash)onHash();
    }
  }catch(_){restore();}
})();
