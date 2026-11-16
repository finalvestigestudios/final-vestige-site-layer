/* Apollo Research Desk R404 — optional isolated staging replacement, not a production script.
 * No network, storage, analytics, HTML interpolation or claim rewriting. */
(() => {
  'use strict';
  const instances = [...document.querySelectorAll('[data-fvx-ledger]')];
  const reflowAnchor = (root, input, render) => {
    if (!location.hash || location.hash.length > 160) return;
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch (_) { return; }
    const target = [...root.querySelectorAll('[id]')].find(el => el.id === id);
    if (!target || !target.hasAttribute('data-fvx-record')) return;
    if (target.hidden) { input.value = ''; render(); }
    // Focus without forcing scroll or reassigning a publisher/CTA URL.
    if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
    target.focus({ preventScroll: true });
  };

  instances.forEach((root, index) => {
    if (root.dataset.fvxR404 === 'ready') return;
    const search = root.querySelector('[data-fvx-search]');
    const tools = root.querySelector('[data-fvx-tools]');
    const status = root.querySelector('[data-fvx-status]');
    const empty = root.querySelector('[data-fvx-empty]');
    const cards = [...root.querySelectorAll('[data-fvx-record]')];
    const failOpen = () => {
      cards.forEach(card => { card.hidden = false; });
      if (empty) empty.hidden = true;
      if (tools) tools.hidden = true;
      root.dataset.fvxR404 = 'failed-open';
    };
    if (!search || !tools || !status || !empty || cards.length !== 6 ||
        cards.some(card => typeof card.dataset.fvxSearch !== 'string')) {
      failOpen(); return;
    }
    try {
      // The original R158 shortcode uses fixed IDs. Remap only subsequent desks,
      // preserving local label, ARIA, and fragment relationships deterministically.
      if (index > 0) {
        const mapped = new Map();
        root.querySelectorAll('[id]').forEach(el => {
          const before = el.id;
          if (!before || mapped.has(before)) throw Error('duplicate ID within desk');
          const after = `${before}-r404-${index + 1}`;
          mapped.set(before, after); el.id = after;
        });
        root.querySelectorAll('[for],[aria-labelledby],[aria-controls],a[href^="#"]').forEach(el => {
          ['for', 'aria-labelledby', 'aria-controls'].forEach(attr => {
            const raw = el.getAttribute(attr); if (!raw) return;
            el.setAttribute(attr, raw.split(/\s+/).map(id => mapped.get(id) || id).join(' '));
          });
          const href = el.getAttribute('href');
          if (href && href.startsWith('#') && mapped.has(href.slice(1)))
            el.setAttribute('href', '#' + mapped.get(href.slice(1)));
        });
      }
      const clear = document.createElement('button');
      clear.type = 'button'; clear.className = 'fv-ex2-ledger__clear';
      clear.textContent = 'Clear search'; clear.hidden = true;
      clear.setAttribute('aria-label', 'Clear evidence search');
      search.insertAdjacentElement('afterend', clear);
      const render = () => {
        try {
          const needle = search.value.trim().toLocaleLowerCase();
          let visible = 0;
          cards.forEach(card => {
            const match = !needle || card.dataset.fvxSearch.toLocaleLowerCase().includes(needle);
            card.hidden = !match;
            if (match) visible++;
          });
          status.textContent = `${visible} of ${cards.length} evidence records`;
          empty.hidden = visible !== 0;
          clear.hidden = !needle;
        } catch (_) { failOpen(); }
      };
      const reset = () => { search.value = ''; render(); search.focus(); };
      search.addEventListener('input', render);
      search.addEventListener('keydown', event => {
        if (event.key === 'Escape' && search.value) { event.preventDefault(); reset(); }
      });
      clear.addEventListener('click', reset);
      window.addEventListener('hashchange', () => reflowAnchor(root, search, render));
      root.dataset.fvxR404 = 'ready';
      render(); tools.hidden = false;
      reflowAnchor(root, search, render);
    } catch (_) { failOpen(); }
  });
})();
