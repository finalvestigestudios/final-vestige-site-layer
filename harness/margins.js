(() => {
  const root = document.querySelector('.fv-margin-strip');
  const viewport = root && root.querySelector('[data-fv-margin-viewport]');
  const list = root && root.querySelector('[data-fv-margin-list]');
  const controls = root && root.querySelector('[data-fv-margin-controls]');
  if (!root || !viewport || !list || !controls) return;

  const items = Array.from(list.children);
  if (items.length < 2) return;

  let reduced = false;
  try { reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (_) {}

  root.setAttribute('data-fv-enhanced', '1');
  controls.hidden = false;
  const countEl = root.querySelector('[data-fv-margin-count]');
  const prevBtn = root.querySelector('[data-fv-margin-prev]');
  const nextBtn = root.querySelector('[data-fv-margin-next]');
  const playBtn = root.querySelector('[data-fv-margin-play]');

  let index = items.findIndex((el) => el.getAttribute('data-fv-active') === '1');
  if (index < 0) index = 0;
  let playing = !reduced;
  let timer = null;

  const show = (i) => {
    items[index].removeAttribute('data-fv-active');
    index = (i + items.length) % items.length;
    items[index].setAttribute('data-fv-active', '1');
    if (countEl) countEl.textContent = String(index + 1).padStart(2, '0') + ' / ' + items.length;
  };

  const stop = () => { if (timer) { clearInterval(timer); timer = null; } };
  const start = () => {
    stop();
    if (!playing) return;
    timer = setInterval(() => show(index + 1), 5200);
  };

  show(index);
  start();

  const pauseForInteraction = () => { playing = false; stop(); if (playBtn) playBtn.setAttribute('aria-label', 'Resume rotation'); };
  viewport.addEventListener('mouseenter', pauseForInteraction);
  viewport.addEventListener('focusin', pauseForInteraction);
  viewport.addEventListener('mouseleave', () => { if (playBtn && playBtn.getAttribute('aria-label') !== 'Resume rotation') { playing = true; start(); } });

  prevBtn && prevBtn.addEventListener('click', () => { pauseForInteraction(); show(index - 1); });
  nextBtn && nextBtn.addEventListener('click', () => { pauseForInteraction(); show(index + 1); });
  playBtn && playBtn.addEventListener('click', () => {
    playing = !playing;
    playBtn.textContent = playing ? '⏸' : '▶';
    playBtn.setAttribute('aria-label', playing ? 'Pause rotation' : 'Resume rotation');
    if (playing) start(); else stop();
  });

  viewport.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight') { pauseForInteraction(); show(index + 1); }
    else if (e.key === 'ArrowLeft') { pauseForInteraction(); show(index - 1); }
  });
})();
