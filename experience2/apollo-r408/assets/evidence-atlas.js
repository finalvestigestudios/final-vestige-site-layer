/* R408 progressive question filters. No network, cookies, tracking or content generation. */
(() => {
  'use strict';
  for (const root of document.querySelectorAll('[data-fv-r408-atlas]')) {
    if (root.dataset.fvR408) continue;
    const cards = [...root.querySelectorAll('[data-fv-r408-card]')];
    const filters = root.querySelector('[data-fv-r408-filters]');
    const status = root.querySelector('[data-fv-r408-status]');
    const buttons = filters ? [...filters.querySelectorAll('[data-fv-r408-filter]')] : [];
    const kinds = new Set(['conditions', 'sequence', 'investigation', 'aftermath']);
    const failOpen = () => {
      cards.forEach(card => card.hidden = false);
      if (filters) filters.hidden = true;
      if (status) status.textContent = 'All six evidence questions are available.';
      root.dataset.fvR408 = 'failed-open';
    };
    try {
      if (!filters || !status || cards.length !== 6 || buttons.length !== 5 ||
          new Set(cards.map(card => card.querySelector('.fv-r408__jump')?.getAttribute('href'))).size !== 6 ||
          cards.some(card => !kinds.has(card.dataset.fvR408Kind) ||
            !card.querySelector('details > summary') || !card.querySelector('.fv-r408__jump[href^="#"]'))) {
        failOpen(); continue;
      }
      const names = ['all', ...kinds];
      if (buttons.some((button, i) => button.dataset.fvR408Filter !== names[i])) {
        failOpen(); continue;
      }
      const apply = kind => {
        if (root.dataset.fvR408 === 'failed-open') return;
        for (const card of cards) {
          const show = kind === 'all' || card.dataset.fvR408Kind === kind;
          if (!show && card.contains(document.activeElement)) filters.querySelector('[data-fv-r408-filter="all"]').focus();
          card.hidden = !show;
        }
        buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.fvR408Filter === kind)));
        const count = cards.filter(card => !card.hidden).length;
        status.textContent = `${count} of six evidence questions shown.`;
      };
      buttons.forEach(button => button.addEventListener('click', () => {
        try { apply(button.dataset.fvR408Filter); } catch (_) { failOpen(); }
      }));
      root.dataset.fvR408 = 'ready';
      apply('all');
      filters.hidden = false;
    } catch (_) { failOpen(); }
  }
})();
