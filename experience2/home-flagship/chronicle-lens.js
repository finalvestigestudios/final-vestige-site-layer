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
  if (!tools || !original || !addition || !note || buttons.length !== 3) return;
  const labels = {
    original: 'Showing only the original 1847 entry. The April 1848 addition is temporarily hidden. Select Addition or Compare both to read it.',
    addition: 'Showing only the April 1848 marginal addition. The 1847 original is temporarily hidden. Select Original or Compare both to read it.',
    both: 'Both entries are visible. The original and later addition share one surviving sheet.'
  };
  const restore = () => {
    section.removeAttribute('data-fv-chronicle-mode');
    tools.hidden = true;
    // The default DOM always contains both entries. Never force a selection or change the source text.
    original.hidden = false;
    addition.hidden = false;
  };
  const setView = (view) => {
    if (!Object.prototype.hasOwnProperty.call(labels, view)) return;
    section.setAttribute('data-fv-chronicle-mode', view);
    for (const b of buttons) b.setAttribute('aria-pressed', String(b.dataset.fvChronicleView === view));
    note.textContent = labels[view];
  };
  try {
    // Register all listeners before exposing any enhancement. If initialization fails,
    // restore() removes mode and leaves all historical content visible.
    for (const button of buttons) {
      button.addEventListener('click', () => setView(button.dataset.fvChronicleView));
      button.addEventListener('keydown', (event) => {
        const position = buttons.indexOf(button);
        const target = event.key === 'ArrowRight' ? (position + 1) % 3
          : event.key === 'ArrowLeft' ? (position + 2) % 3
          : event.key === 'Home' ? 0 : event.key === 'End' ? 2 : -1;
        if (target < 0) return;
        event.preventDefault();
        buttons[target].focus();
        setView(buttons[target].dataset.fvChronicleView);
      });
    }
    setView('both');
    tools.hidden = false;
  } catch (error) {
    restore();
  }
})();
