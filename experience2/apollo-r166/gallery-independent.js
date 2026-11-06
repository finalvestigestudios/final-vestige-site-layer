/* Apollo archival views: independent of fire-second slider. Staging candidate only.
 * No network, storage, analytics, HTML-string injection or extra purchases. */
(() => {
  'use strict';
  document.querySelectorAll('[data-fvx-chrono-gallery]').forEach(gallery => {
    if (gallery.dataset.fvxIndependentReady === 'yes') return;
    const figures = [...gallery.querySelectorAll('[data-fvx-chrono-photo]')];
    const frames = gallery.querySelector('.fvx-chrono-gallery__frames');
    const position = gallery.querySelector('[data-fvx-chrono-position]');
    if (figures.length !== 3 || !frames || !position ||
        figures.some((figure, i) => figure.getAttribute('data-fvx-chrono-photo') !== String(i) ||
          !figure.querySelector('img[alt]') ||
          !figure.querySelector('figcaption a[href^="https://www.nasa.gov/"],figcaption a[href^="https://images.nasa.gov/"]'))) {
      return; // Fail open: preserve the three photographs, captions and source links.
    }
    const labels = ['Crew training · 1966', 'Spacecraft processing · 1967', 'Hatch exhibition · 2017'];
    const controls = document.createElement('div');
    controls.className = 'fvx-archive-choice';
    controls.setAttribute('role', 'group');
    controls.setAttribute('aria-label', 'Choose a contextual NASA archival photograph — not a fire chronology marker');
    const buttons = labels.map((label, i) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'fvx-archive-choice__button';
      button.textContent = label;
      button.dataset.fvxArchiveIndex = String(i);
      button.setAttribute('aria-pressed', String(i === 0));
      controls.append(button);
      return button;
    });
    let current = 0;
    const show = index => {
      current = index;
      figures.forEach((figure, i) => {
        figure.hidden = i !== index;
        figure.classList.toggle('is-current', i === index);
      });
      buttons.forEach((button, i) => button.setAttribute('aria-pressed', String(i === index)));
      position.hidden = false;
      position.textContent = 'Context photo ' + (index + 1) + ' of 3: ' + labels[index] + '. Photographs are not synchronized to the fire timeline.';
    };
    buttons.forEach((button, i) => {
      button.addEventListener('click', () => show(i));
      button.addEventListener('keydown', event => {
        const offset = event.key === 'ArrowRight' || event.key === 'ArrowDown' ? 1 :
          event.key === 'ArrowLeft' || event.key === 'ArrowUp' ? -1 : 0;
        const next = event.key === 'Home' ? 0 : event.key === 'End' ? 2 :
          offset ? (i + offset + 3) % 3 : -1;
        if (next === -1) return;
        event.preventDefault();
        buttons[next].focus();
        show(next);
      });
    });
    // Only mutate visibility after all controls and handlers are prepared.
    gallery.insertBefore(controls, frames);
    show(0);
    gallery.dataset.fvxIndependentReady = 'yes';
  });
})();
