/* Final Vestige / unpublished Experience 2.0 homepage candidate (Black Dossier direction).
 * JS is optional. No external resources, browser persistence, clocks, autoplay,
 * tracking, content rewriting, or concealed facts that cannot be read without JS. */
(() => {
  'use strict';
  const CASES = ['apollo', 'franklin', 'malbone'];

  const showImageFallback = (img) => {
    if (!img || !img.parentElement) return;
    img.hidden = true; // The underlying textual fallback and original source link remain.
  };

  document.querySelectorAll('[data-fv-home-flagship]').forEach((root) => {
    // Optional local media-failure treatment; no blank or infinite loading stage.
    root.querySelectorAll('[data-fv-archive-img]').forEach((img) => {
      img.addEventListener('error', () => showImageFallback(img));
      if (img.complete && img.naturalWidth === 0) showImageFallback(img);
    });

    const group = root.querySelector('[data-fv-case-buttons]');
    const status = root.querySelector('[data-fv-case-status]');
    const caseButtons = Array.from(root.querySelectorAll('[data-fv-case-button]'));
    const casePanels = Array.from(root.querySelectorAll('[data-fv-case]'));

    // Fail open on any missing or duplicate case; every case remains readable.
    if (!group || !status ||
        caseButtons.length !== CASES.length || casePanels.length !== CASES.length ||
        new Set(caseButtons.map((button) => button.dataset.fvCaseButton)).size !== CASES.length ||
        new Set(casePanels.map((panel) => panel.dataset.fvCase)).size !== CASES.length ||
        !CASES.every((id) => caseButtons.some((b) => b.dataset.fvCaseButton === id) &&
                             casePanels.some((p) => p.dataset.fvCase === id))) {
      return;
    }

    let active = CASES[0];
    let enhanced = false;
    const resetStatic = () => {
      enhanced = false;
      casePanels.forEach((panel) => { panel.hidden = false; });
      caseButtons.forEach((button) => { button.setAttribute('aria-pressed', 'false'); });
      group.hidden = true;
      root.classList.remove('fv-hf--enhanced');
      status.textContent = '';
      // No inert, role="tab", focus manipulation or touch-action side effects.
    };

    const selectCase = (id, announce = true) => {
      if (!enhanced || !CASES.includes(id)) return false;
      try {
        casePanels.forEach((panel) => { panel.hidden = panel.dataset.fvCase !== id; });
        caseButtons.forEach((button) => { button.setAttribute('aria-pressed', String(button.dataset.fvCaseButton === id)); });
        active = id;
        if (announce) {
          const current = casePanels.find((panel) => panel.dataset.fvCase === id);
          const heading = current && current.querySelector('h3') && current.querySelector('h3').textContent || 'Selected record';
          status.textContent = 'Now viewing: ' + heading;
        }
        return true;
      } catch (err) {
        resetStatic();
        return false;
      }
    };

    const handleClick = (event) => {
      if (!enhanced) return;
      const button = event.target.closest && event.target.closest('[data-fv-case-button]');
      if (button && group.contains(button)) {
        selectCase(button.dataset.fvCaseButton);
      }
    };

    const handleKeydown = (event) => {
      if (!enhanced || !['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      const button = event.target.closest && event.target.closest('[data-fv-case-button]');
      if (!button || !group.contains(button)) return;
      const current = CASES.indexOf(button.dataset.fvCaseButton);
      if (current === -1) return;
      event.preventDefault();
      let next = current;
      if (event.key === 'ArrowRight') next = (current + 1) % CASES.length;
      if (event.key === 'ArrowLeft') next = (current - 1 + CASES.length) % CASES.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = CASES.length - 1;
      const target = caseButtons.find((item) => item.dataset.fvCaseButton === CASES[next]);
      if (selectCase(CASES[next])) target.focus(); // Focus remains on a real button.
    };

    try {
      if (!('hidden' in document.createElement('div')) || typeof Element.prototype.closest !== 'function') {
        return;
      }
      // Stage all operations before advertising any enhanced behavior.
      casePanels.forEach((panel) => { panel.hidden = panel.dataset.fvCase !== active; });
      caseButtons.forEach((button) => { button.setAttribute('aria-pressed', String(button.dataset.fvCaseButton === active)); });
      enhanced = true;
      group.hidden = false;
      root.classList.add('fv-hf--enhanced');
      root.addEventListener('click', handleClick);
      root.addEventListener('keydown', handleKeydown);
    } catch (err) {
      resetStatic();
    }
  });
})();
