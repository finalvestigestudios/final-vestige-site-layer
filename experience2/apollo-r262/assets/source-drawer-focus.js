/* Apollo R261: optional SourceDrawer fragment focus bridge, staging only.
 * Native <details>, #hash navigation and all NASA/source links work without JS.
 * No tracking, external resources, storage, or history rewriting. */
(() => {
  'use strict';
  const HASH = '#fv-apollo-source-drawer';
  for (const root of document.querySelectorAll('.fv-apollo-atlas')) {
    if (root.dataset.fvDrawerFocus === 'ready') continue;
    const drawer = root.querySelector('details#fv-apollo-source-drawer');
    const summary = drawer?.querySelector(':scope > summary');
    if (!summary) continue;
    root.dataset.fvDrawerFocus = 'ready';
    const reveal = focus => {
      if (window.location.hash !== HASH) return;
      drawer.open = true;
      if (focus) summary.focus({ preventScroll: true });
    };
    // Preserve native anchor navigation; support repeat clicks on the same hash.
    root.addEventListener('click', event => {
      const link = event.target instanceof Element
        ? event.target.closest('a[href="#fv-apollo-source-drawer"]') : null;
      if (!link || !root.contains(link)) return;
      drawer.open = true;
      requestAnimationFrame(() => summary.focus({ preventScroll: true }));
    });
    // Hashchange includes browser back/forward; initial deep links expand without
    // stealing focus from the browser's initial page-reading position.
    window.addEventListener('hashchange', () => reveal(true));
    reveal(false);
  }
})();
