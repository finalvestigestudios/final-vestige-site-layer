(() => {
  const root = document.querySelector('[data-fv-assembly]');
  if (!root) return;
  let reduced = false;
  try { reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (_) {}
  if (reduced) return; // static baseline already shows the resolved fragments; nothing to animate

  root.setAttribute('data-fv-run', '1');
  requestAnimationFrame(() => {
    setTimeout(() => root.setAttribute('data-fv-in', '1'), 60);
    setTimeout(() => root.setAttribute('data-fv-connect', '1'), 1900);
  });
})();
