/* Apollo R232: source-custody search enhancement; no external requests, storage or DOM injection. */
(() => { 'use strict';
  const normal = value => String(value || '').normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase().replace(/\s+/g, ' ').trim();
  document.querySelectorAll('[data-fvx-ledger]').forEach(root => {
    if (root.dataset.fvxInitialized === 'yes') return;
    const search = root.querySelector('[data-fvx-search]');
    const tools = root.querySelector('[data-fvx-tools]');
    const status = root.querySelector('[data-fvx-status]');
    const cards = [...root.querySelectorAll('[data-fvx-record]')];
    const empty = root.querySelector('[data-fvx-empty]');
    if (!search || !tools || !status || !empty || !cards.length) return;
    const autoOpened = new Set();
    try {
      const filter = () => {
        const terms = normal(search.value).split(' ').filter(Boolean);
        // Return previous auto-opened sources to their prior closed state.
        autoOpened.forEach(d => { if (d.isConnected) d.open = false; });
        autoOpened.clear();
        let shown = 0;
        for (const card of cards) {
          const haystack = normal(card.textContent + ' ' + (card.dataset.fvxSearch || ''));
          const match = terms.every(token => haystack.includes(token));
          card.hidden = !match;
          if (!match) continue;
          shown++;
          // Do not make a matched term discoverable only behind a closed disclosure.
          // Open *only* disclosures which contain every search token and were closed.
          if (terms.length) card.querySelectorAll('details').forEach(d => {
            if (!d.open && terms.every(token => normal(d.textContent).includes(token))) {
              d.open = true; autoOpened.add(d);
            }
          });
        }
        status.textContent = `${shown} of ${cards.length} evidence records`;
        empty.hidden = shown !== 0;
      };
      search.addEventListener('input', filter);
      filter();
      tools.hidden = false;
      root.dataset.fvxInitialized = 'yes';
    } catch (_) {
      autoOpened.forEach(d => { if (d.isConnected) d.open = false; });
      cards.forEach(card => { card.hidden = false; });
      empty.hidden = true;
      tools.hidden = true;
      root.dataset.fvxInitialized = '';
    }
  });
})();
