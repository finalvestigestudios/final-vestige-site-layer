/* Experience 2.0 chapter trail: align keyboard focus within the horizontally
   scrollable bar, including partially visible items. No links are rewritten;
   no network, cookies, observers or tracking. */
(() => {
  const root = document.querySelector('[data-fv-home-flagship]');
  const nav = root?.querySelector('.fv-hf__chapter-nav');
  if (!nav) return;
  nav.addEventListener('focusin', (event) => {
    const link = event.target.closest?.('a[href^="#fv-hf-"]');
    if (!link || !nav.contains(link)) return;
    const panel = nav.getBoundingClientRect();
    const item = link.getBoundingClientRect();
    if (panel.width >= nav.scrollWidth - 1) return;
    // getBoundingClientRect is visual pixels; scrollLeft uses unzoomed CSS units.
    const scale = panel.width / Math.max(1, nav.clientWidth);
    const next = nav.scrollLeft + ((item.left - panel.left) + (item.width - panel.width) / 2) / scale;
    nav.scrollTo({left: next, behavior: 'instant'});
  });
})();
