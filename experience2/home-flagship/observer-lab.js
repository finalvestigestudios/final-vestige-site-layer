/* Optional Observer Lab enhancement. Fail open: both illustrations and the native answer remain readable. */
(() => {
  'use strict';
  document.querySelectorAll('[data-fv-observer]').forEach((root) => {
    const frames = Array.from(root.querySelectorAll('[data-fv-observer-frame]'));
    const buttons = Array.from(root.querySelectorAll('[data-fv-observer-switch]'));
    const controls = root.querySelector('[data-fv-observer-controls]');
    const status = root.querySelector('[data-fv-observer-status]');
    if (!controls || !status || frames.length !== 2 || buttons.length !== 2 ||
        frames.map((f) => f.getAttribute('data-fv-observer-frame')).join(',') !== 'a,b' ||
        buttons.map((b) => b.getAttribute('data-fv-observer-switch')).join(',') !== 'a,b') return;
    const failOpen = () => {
      frames.forEach((frame) => { frame.hidden = false; });
      buttons.forEach((button) => { button.setAttribute('aria-pressed', 'false'); });
      controls.hidden = true;
      delete root.dataset.fvObserverEnhanced;
    };
    const show = (key) => {
      if (key !== 'a' && key !== 'b') return;
      frames.forEach((frame) => { frame.hidden = frame.getAttribute('data-fv-observer-frame') !== key; });
      buttons.forEach((button) => { button.setAttribute('aria-pressed', String(button.getAttribute('data-fv-observer-switch') === key)); });
      status.textContent = `Frame ${key.toUpperCase()} displayed.`;
    };
    try {
      root.dataset.fvObserverEnhanced = 'true';
      show('a');
      buttons.forEach((button, index) => {
        button.addEventListener('click', () => {
          try { show(button.getAttribute('data-fv-observer-switch')); }
          catch (_) { failOpen(); }
        });
        // Native buttons remain independently tabbable. Arrow/Home/End additionally
        // permit rapid comparison without trapping focus or announcing the answer.
        button.addEventListener('keydown', (event) => {
          const next = event.key === 'ArrowRight' ? (index + 1) % 2
            : event.key === 'ArrowLeft' ? (index + 1) % 2
            : event.key === 'Home' ? 0 : event.key === 'End' ? 1 : -1;
          if (next === -1) return;
          event.preventDefault();
          try { show(buttons[next].getAttribute('data-fv-observer-switch')); buttons[next].focus(); }
          catch (_) { failOpen(); }
        });
      });
      controls.hidden = false;
    } catch (_) { failOpen(); }
  });
})();
