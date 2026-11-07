/* Apollo R177: optional, offline, source-ledger search replacement (staging only).
 * Replace the original source-ledger.js in a controlled staging manifest; NEVER co-load.
 * Searches actual visible source-custody / provenance text, not only the stale index.
 * No network calls, DOM HTML injection, cookies, storage, analytics, or commerce links.
 */
(()=>{'use strict';
  document.querySelectorAll('[data-fvx-ledger]').forEach(root=>{
    if(root.dataset.fvxInitialized==='yes') return;
    const search=root.querySelector('[data-fvx-search]');
    const tools=root.querySelector('[data-fvx-tools]');
    const status=root.querySelector('[data-fvx-status]');
    const empty=root.querySelector('[data-fvx-empty]');
    const cards=Array.from(root.querySelectorAll('[data-fvx-record]'));
    if(!search||!tools||!status||!empty||cards.length!==6) return;
    const clean=value=>String(value||'').normalize('NFKC').toLocaleLowerCase().replace(/\s+/g,' ').trim();
    try{
      // Both historical aliases and all rendered source-custody / media warnings are indexed.
      // Cache before filtering; textContent includes closed <details> (which remain readable).
      const indexes=cards.map(card=>clean(`${card.dataset.fvxSearch||''} ${card.textContent||''}`));
      const filter=()=>{
        const needle=clean(search.value);
        let shown=0;
        cards.forEach((card,i)=>{
          const match=!needle||indexes[i].includes(needle);
          card.hidden=!match;
          if(match) shown++;
        });
        status.textContent=`${shown} of ${cards.length} evidence records`;
        empty.hidden=shown!==0;
      };
      search.addEventListener('input',filter);
      filter();
      tools.hidden=false;
      root.dataset.fvxInitialized='yes';
    }catch(_){
      // The full sourced record set must remain available on enhancement failure.
      root.dataset.fvxInitialized='';
      cards.forEach(card=>card.hidden=false);
      tools.hidden=true;
      empty.hidden=true;
    }
  });
})();
