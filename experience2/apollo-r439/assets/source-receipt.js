/* FV Apollo R439: entirely local, opt-in evidence receipts. No tracking, fetch, storage or auto-download. */
(()=>{'use strict';
  const tidy=(value)=>String(value||'').replace(/[\r\n\t]+/g,' ').replace(/\s{2,}/g,' ').trim();
  function init(root){
    if(root.dataset.r439Ready==='true')return;
    const atlas=root.querySelector('[data-r438-atlas-root]');
    const receipt=root.querySelector('[data-r439-receipt]');
    if(!atlas||!receipt)return;
    const cards=[...atlas.querySelectorAll('[data-r438-card]')];
    if(cards.length!==5)return;
    const status=receipt.querySelector('[data-r439-status]');
    const manual=receipt.querySelector('[data-r439-manual]');
    if(!status||!manual)return;
    const selectedCards=()=>{
      const pressed=[...atlas.querySelectorAll('[data-r438-pick][aria-pressed="true"]')];
      if(pressed.length!==2)return cards;
      const ids=new Set(pressed.map(b=>b.dataset.r438Pick));
      const chosen=cards.filter(c=>ids.has(c.dataset.r438Card));
      return chosen.length===2?chosen:cards;
    };
    const receiptText=()=>{
      const chosen=selectedCards();
      const lines=['FINAL VESTIGE | APOLLO 1 EVIDENCE RECEIPT',
        chosen.length===2?'Selection: two compared NASA-linked sources':'Selection: all five curated NASA-linked sources',
        'Research use only. Source links are not a commercial media license or NASA endorsement.',
        'Each entry is a record of what a source supports AND what it cannot prove.',''];
      chosen.forEach((card,i)=>{
        const node=(sel)=>tidy(card.querySelector(sel)?.textContent);
        const link=card.querySelector('a[href^="https://www.nasa.gov/"]');
        const source=link?.getAttribute('href')||'';
        const time=card.querySelector('time');
        const rights=card.querySelector('details p');
        lines.push(`${i+1}. ${node('h3')}`,
          `Source type: ${node('.fv-r438__kind')}`,
          `Record date or publication: ${tidy(time?.textContent)}`,
          `Supported finding: ${node('[data-r438-supports]')}`,
          `Cannot establish: ${node('[data-r438-limit]')}`,
          `Custody/rights limitation: ${tidy(rights?.textContent)}`,
          `Original NASA URL: ${source}`,'');
      });
      lines.push('Free full investigation: https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/',
        'Verify each claim against its original NASA record. Do not infer causal links or geographic coordinates from this list.');
      return lines.join('\n')+'\n';
    };
    const controls=document.createElement('div');controls.className='fv-r439__controls';
    const save=document.createElement('button');save.type='button';save.textContent='Save source receipt (.txt)';
    save.addEventListener('click',()=>{
      const content=receiptText();
      const url=URL.createObjectURL(new Blob([content],{type:'text/plain;charset=utf-8'}));
      const a=document.createElement('a');a.href=url;a.download='fv-apollo-1-evidence-receipt.txt';
      a.style.display='none';receipt.append(a);a.click();a.remove();
      setTimeout(()=>URL.revokeObjectURL(url),3000);
      status.textContent='Evidence receipt prepared for download. This does not submit or store your selections.';
    });
    const copy=document.createElement('button');copy.type='button';copy.textContent='Copy source receipt';
    copy.addEventListener('click',async()=>{
      const content=receiptText();
      try{
        if(!navigator.clipboard?.writeText)throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(content);
        manual.hidden=true;receipt.querySelector('[data-r439-manual-label]').hidden=true;status.textContent='Source receipt copied locally to your clipboard.';
      }catch(_){
        manual.value=content;manual.hidden=false;receipt.querySelector('[data-r439-manual-label]').hidden=false;manual.focus();manual.select();
        status.textContent='Clipboard permission unavailable. Select and copy the visible receipt text manually.';
      }
    });
    controls.append(save,copy);receipt.querySelector('[data-r439-controls]').append(controls);
    root.dataset.r439Ready='true';
  }
  const start=()=>document.querySelectorAll('[data-r439-root]').forEach(init);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
