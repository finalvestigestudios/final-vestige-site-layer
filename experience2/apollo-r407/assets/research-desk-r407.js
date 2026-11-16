/* FV Apollo R407: optional, no-network evidence navigation. Server owns IDs and historical copy. */
(() => {
  'use strict';
  const idCounts = new Map();
  document.querySelectorAll('[id]').forEach(el => idCounts.set(el.id, (idCounts.get(el.id) || 0) + 1));
  document.querySelectorAll('[data-fvx-ledger]').forEach(root => {
    if (root.dataset.fvxR407) return;
    const cards = [...root.querySelectorAll('[data-fvx-record]')];
    const tools = root.querySelector('[data-fvx-tools]');
    const input = root.querySelector('[data-fvx-search]');
    const status = root.querySelector('[data-fvx-status]');
    const empty = root.querySelector('[data-fvx-empty]');
    let clear;
    const fail = () => {
      cards.forEach(card => { card.hidden = false; });
      if (tools) tools.hidden = true;
      if (empty) empty.hidden = true;
      if (clear) clear.remove();
      root.dataset.fvxR407 = 'failed-open';
    };
    try {
      if (!tools || !input || !status || !empty || cards.length !== 6 ||
          !input.id || !root.contains(input) ||
          [...root.querySelectorAll('[id]')].some(el => !el.id || idCounts.get(el.id) !== 1) ||
          cards.some(card => !card.id || !card.dataset.fvxSearch ||
            !card.querySelector('details > summary') ||
            !card.querySelector('a[href^="https://www.nasa.gov/"]'))) {
        fail(); return;
      }
      const gridId = input.getAttribute('aria-controls');
      const controlled = gridId && document.getElementById(gridId);
      const label = [...root.querySelectorAll('label[for]')].find(el => el.htmlFor === input.id);
      if (!label || !controlled || !root.contains(controlled) ||
          controlled !== cards[0].parentElement ||
          !cards.every(card => card.parentElement === controlled)) {
        fail(); return;
      }
      clear = document.createElement('button');
      clear.type = 'button';
      clear.className = 'fv-ex2-ledger__clear';
      clear.textContent = 'Clear search';
      clear.setAttribute('aria-label', 'Clear evidence search');
      clear.hidden = true;
      input.insertAdjacentElement('afterend', clear);
      const reveal = () => {
        const needle = input.value.trim().toLocaleLowerCase();
        let shown = 0;
        for (const card of cards) {
          const match = !needle || card.dataset.fvxSearch.toLocaleLowerCase().includes(needle);
          if (!match && card.contains(document.activeElement)) input.focus({preventScroll: true});
          card.hidden = !match;
          if (match) shown++;
        }
        status.textContent = `${shown} of ${cards.length} evidence records`;
        empty.hidden = shown !== 0;
        clear.hidden = !needle;
      };
      const reset = (focus = true) => {
        input.value = '';
        reveal();
        if (focus) input.focus({preventScroll:true});
      };
      const recover = () => {
        if (!location.hash || location.hash.length > 200) return;
        let id;
        try { id = decodeURIComponent(location.hash.slice(1)); } catch (_) { return; }
        const target = document.getElementById(id);
        if (!target || !root.contains(target)) return;
        const card = target.closest('[data-fvx-record]');
        if (card && card.hidden) reset(false);
        const details = target.closest('details');
        if (details && root.contains(details)) details.open = true;
        if (!target.matches('a,button,input,summary,[tabindex]')) target.setAttribute('tabindex', '-1');
        if (target.focus) target.focus({preventScroll:true});
      };
      input.addEventListener('input', () => { try { reveal(); } catch (_) { fail(); }});
      input.addEventListener('keydown', event => {
        if (event.key === 'Escape' && input.value) { event.preventDefault(); reset(); }
      });
      clear.addEventListener('click', () => { try { reset(); } catch (_) { fail(); }});
      window.addEventListener('hashchange', recover);
      root.dataset.fvxR407 = 'ready';
      reveal();
      tools.hidden = false;
      recover();
    } catch (_) { fail(); } // Bad ARIA selectors must never suppress another instance.
  });
})();
