/* Apollo Research Desk R406 — optional progressive enhancement, staging-only.
 * R405 allocates stable unique IDs on the SERVER. Never rewrite those IDs in JS:
 * a deep link to an instance-N card must resolve before and after enhancement.
 * No fetch, storage, analytics, HTML injection, generated claims or commerce. */
(() => {
  'use strict';
  const all = [...document.querySelectorAll('[data-fvx-ledger]')];
  const idCounts = new Map();
  document.querySelectorAll('[id]').forEach(el => {
    idCounts.set(el.id, (idCounts.get(el.id) || 0) + 1);
  });

  all.forEach(root => {
    if (root.dataset.fvxR406) return;
    const cards = [...root.querySelectorAll('[data-fvx-record]')];
    const tools = root.querySelector('[data-fvx-tools]');
    const input = root.querySelector('input[data-fvx-search]');
    const status = root.querySelector('[data-fvx-status]');
    const empty = root.querySelector('[data-fvx-empty]');
    const fail = () => {
      cards.forEach(c => { c.hidden = false; });
      if (empty) empty.hidden = true;
      if (tools) tools.hidden = true;
      root.dataset.fvxR406 = 'failed-open';
    };
    // Includes the document scope, not just this component. Never silently
    // claim valid ID custody if an unrelated component reused one of our IDs.
    const ownedIds = [...root.querySelectorAll('[id]')];
    if (!tools || !input || !status || !empty || cards.length !== 6 ||
        ownedIds.some(el => !el.id || idCounts.get(el.id) !== 1) ||
        cards.some(card => !card.id || !card.dataset.fvxSearch ||
          !card.querySelector('details > summary') ||
          !card.querySelector('a[href^="https://www.nasa.gov/"]'))) {
      fail(); return;
    }
    // Require explicit, resolved label and controls relationships.
    const label = root.querySelector(`label[for="${input.id}"]`);
    const controlled = root.querySelector('[id]#' + input.getAttribute('aria-controls'));
    if (!label || !controlled || controlled !== cards[0].parentElement) { fail(); return; }
    try {
      const clear = document.createElement('button');
      clear.type = 'button';
      clear.className = 'fv-ex2-ledger__clear';
      clear.textContent = 'Clear search';
      clear.setAttribute('aria-label', 'Clear evidence search');
      clear.hidden = true;
      input.insertAdjacentElement('afterend', clear);
      const reveal = () => {
        const term = input.value.trim().toLocaleLowerCase();
        let shown = 0;
        cards.forEach(card => {
          const match = !term || card.dataset.fvxSearch.toLocaleLowerCase().includes(term);
          // Never cause focus to disappear inside a filtered record.
          if (!match && card.contains(document.activeElement)) input.focus({ preventScroll: true });
          card.hidden = !match;
          if (match) shown++;
        });
        status.textContent = `${shown} of ${cards.length} evidence records`;
        empty.hidden = shown !== 0;
        clear.hidden = !term;
      };
      const reset = (focus = true) => {
        input.value = '';
        reveal();
        if (focus) input.focus({ preventScroll: true });
      };
      const hashTarget = () => {
        if (!location.hash || location.hash.length > 200) return null;
        let id;
        try { id = decodeURIComponent(location.hash.slice(1)); }
        catch (_) { return null; }
        const target = document.getElementById(id);
        return target && root.contains(target) ? target : null;
      };
      const recoverFragment = () => {
        const target = hashTarget();
        if (!target) return;
        const card = target.closest('[data-fvx-record]');
        if (card && card.hidden) reset(false);
        // Native disclosure first, then focus the originally requested target.
        const details = target.closest('details');
        if (details && root.contains(details)) details.open = true;
        if (!target.matches('a,button,input,summary,[tabindex]')) target.setAttribute('tabindex', '-1');
        if (typeof target.focus === 'function') target.focus({ preventScroll: true });
      };
      input.addEventListener('input', () => {
        try { reveal(); } catch (_) { fail(); }
      });
      input.addEventListener('keydown', event => {
        if (event.key === 'Escape' && input.value) {
          event.preventDefault(); reset();
        }
      });
      clear.addEventListener('click', () => reset());
      window.addEventListener('hashchange', recoverFragment);
      root.dataset.fvxR406 = 'ready';
      reveal();
      tools.hidden = false;
      recoverFragment();
    } catch (_) { fail(); }
  });
})();
