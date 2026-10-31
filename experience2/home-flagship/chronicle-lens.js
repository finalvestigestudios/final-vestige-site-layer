/* Optional Victory Point reading lens. Fails open to the original two-entry presentation. */
(() => {
  'use strict';
  const section = document.querySelector('.fv-hf__chronicle');
  if (!section) return;
  const tools = section.querySelector('[data-fv-chronicle-lens]');
  const original = section.querySelector('.fv-hf__chronicle-entry--first');
  const addition = section.querySelector('.fv-hf__chronicle-entry--second');
  const note = section.querySelector('[data-fv-chronicle-lens-status]');
  const buttons = tools ? [...tools.querySelectorAll('[data-fv-chronicle-view]')] : [];
  const VIEWS = ['original', 'addition', 'both'];

  // Do not expose a switcher with duplicate, missing or reordered choices.
  // The underlying dated entries remain readable when this enhancement is absent.
  if (!tools || !original || !addition || original === addition || !note ||
      buttons.length !== VIEWS.length ||
      buttons.map((button) => button.dataset.fvChronicleView).join(',') !== VIEWS.join(',')) return;

  const labels = {
    original: 'Showing only the original 1847 entry. The April 1848 addition is temporarily hidden. Select Addition or Compare both to read it.',
    addition: 'Showing only the April 1848 marginal addition. The 1847 original is temporarily hidden. Select Original or Compare both to read it.',
    both: 'Both entries are visible. The original and later addition share one surviving sheet.'
  };
  let running = true;
  const restore = () => {
    running = false;
    // Remove the CSS selection first: never strand an invisible historical entry.
    try { section.removeAttribute('data-fv-chronicle-mode'); } catch (_) { /* best effort */ }
    try { original.hidden = false; addition.hidden = false; } catch (_) { /* best effort */ }
    try { tools.hidden = true; } catch (_) { /* best effort */ }
    buttons.forEach((button) => {
      try { button.setAttribute('aria-pressed', 'false'); } catch (_) { /* best effort */ }
    });
  };
  const setView = (view) => {
    if (!running || !Object.prototype.hasOwnProperty.call(labels, view)) return false;
    try {
      // Complete announcements and button state before hiding either source entry.
      buttons.forEach((button) => {
        button.setAttribute('aria-pressed', String(button.dataset.fvChronicleView === view));
      });
      note.textContent = labels[view];
      section.setAttribute('data-fv-chronicle-mode', view);
      return true;
    } catch (_) {
      restore();
      return false;
    }
  };
  try {
    // Register all handlers before exposing the optional switcher.
    buttons.forEach((button, position) => {
      button.addEventListener('click', () => { setView(button.dataset.fvChronicleView); });
      button.addEventListener('keydown', (event) => {
        if (!running) return;
        const target = event.key === 'ArrowRight' ? (position + 1) % VIEWS.length
          : event.key === 'ArrowLeft' ? (position + VIEWS.length - 1) % VIEWS.length
          : event.key === 'Home' ? 0 : event.key === 'End' ? VIEWS.length - 1 : -1;
        if (target === -1) return;
        event.preventDefault();
        if (!setView(VIEWS[target])) return;
        try { buttons[target].focus(); } catch (_) { restore(); }
      });
    });
    if (!setView('both')) return;
    tools.hidden = false;
  } catch (_) {
    restore();
  }
})();
