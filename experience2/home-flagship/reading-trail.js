/* Final Vestige — progressive chapter wayfinding for the seven-chapter archive.
 * Enhances navigation only; source evidence and anchor links remain usable without JS.
 * No timers, persistent storage, tracking, focus traps, or synthetic history. */
(() => {
  'use strict';
  const CHAPTER_IDS = [
    'fv-hf-title', 'fv-hf-chronicle', 'fv-hf-evidence', 'fv-hf-inquiry',
    'fv-hf-method-title', 'fv-hf-observer', 'fv-hf-mind-title'
  ];
  const root = document.querySelector('[data-fv-home-flagship]');
  if (!root) return;
  const nav = root.querySelector('.fv-hf__chapter-nav');
  if (!nav) return;
  const links = Array.from(nav.querySelectorAll('a[href^="#"]'));
  const ids = links.map((link) => link.getAttribute('href').slice(1));
  const targets = CHAPTER_IDS.map((id) => root.querySelector(`[id="${id}"]`));
  if (links.length !== CHAPTER_IDS.length ||
      ids.join('|') !== CHAPTER_IDS.join('|') || targets.some((t) => !t) ||
      new Set(targets).size !== CHAPTER_IDS.length) return;

  // Reading progress must include the whole final chapter, not just its h2.
  // The seven anchor targets remain unchanged for native fragment navigation.
  const lastHeading = targets[targets.length - 1];
  const finalChapter = (typeof lastHeading.closest === 'function' && lastHeading.closest('section')) || lastHeading;
  let running = true;
  let queued = false;
  const originalTabindex = new Map();
  // Make source chapters programmatically focusable, but not part of normal Tab order.
  targets.forEach((target) => {
    originalTabindex.set(target, target.getAttribute('tabindex'));
    if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
  });
  const restore = () => {
    running = false;
    nav.removeAttribute('data-fv-trail-enhanced');
    nav.removeAttribute('data-fv-trail-overflow-left');
    nav.removeAttribute('data-fv-trail-overflow-right');
    nav.style.removeProperty('--fv-trail-progress');
    links.forEach((link) => link.removeAttribute('aria-current'));
    originalTabindex.forEach((value, target) => {
      if (value === null) target.removeAttribute('tabindex');
      else target.setAttribute('tabindex', value);
    });
    window.removeEventListener('scroll', enqueue);
    window.removeEventListener('resize', enqueue);
    window.removeEventListener('hashchange', enqueue);
    nav.removeEventListener('scroll', updateOverflow);
  };
  // The nav scrolls horizontally on narrow viewports (seven full chapter labels
  // never fit); this only signals that more chapters sit off to one side so the
  // CSS can fade that edge -- scrolling itself, and every label's full text,
  // already work with no JS at all.
  const updateOverflow = () => {
    if (!running) return;
    const max = nav.scrollWidth - nav.clientWidth;
    if (max <= 1) {
      nav.removeAttribute('data-fv-trail-overflow-left');
      nav.removeAttribute('data-fv-trail-overflow-right');
      return;
    }
    if (nav.scrollLeft > 2) nav.setAttribute('data-fv-trail-overflow-left', '');
    else nav.removeAttribute('data-fv-trail-overflow-left');
    if (nav.scrollLeft < max - 2) nav.setAttribute('data-fv-trail-overflow-right', '');
    else nav.removeAttribute('data-fv-trail-overflow-right');
  };
  const render = () => {
    queued = false;
    if (!running) return;
    try {
      const scroll = window.scrollY || window.pageYOffset || 0;
      const top = targets[0].getBoundingClientRect().top + scroll;
      const end = finalChapter.getBoundingClientRect().bottom + scroll;
      const viewport = Math.max(1, window.innerHeight);
      const available = Math.max(1, end - top - viewport);
      const progress = Math.max(0, Math.min(1, (scroll - top) / available));
      nav.style.setProperty('--fv-trail-progress', progress.toFixed(4));
      const readingLine = scroll + nav.getBoundingClientRect().height + viewport * 0.28;
      let active = 0;
      targets.forEach((target, index) => {
        if (target.getBoundingClientRect().top + scroll <= readingLine) active = index;
      });
      links.forEach((link, index) => {
        if (index === active) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
      updateOverflow();
    } catch (_) { restore(); }
  };
  function enqueue() {
    if (!running || queued) return;
    queued = true;
    window.requestAnimationFrame(render);
  }
  try {
    // Native fragment navigation, browser history and no-JS behavior are retained.
    links.forEach((link, index) => link.addEventListener('click', (event) => {
      if (!running || event.detail !== 0) return; // Keyboard activation only.
      const target = targets[index];
      // Wait for native anchor navigation, then move keyboard focus to the destination.
      window.setTimeout(() => {
        if (!running) return;
        try { target.focus({ preventScroll: true }); } catch (_) { /* anchor remains usable */ }
      }, 0);
    }));
    nav.setAttribute('data-fv-trail-enhanced', '');
    window.addEventListener('scroll', enqueue, { passive: true });
    window.addEventListener('resize', enqueue, { passive: true });
    window.addEventListener('hashchange', enqueue);
    nav.addEventListener('scroll', updateOverflow, { passive: true });
    enqueue();
    updateOverflow();
  } catch (_) { restore(); }
})();
