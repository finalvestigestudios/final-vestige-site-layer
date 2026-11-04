/* Final Vestige Experience 2.0 behaviour.
   Rules: no network, no storage, no HTML-string injection (DOM is cloned from inert templates), no third-party code. Every enhancement is optional:
   content is complete HTML first, a module only reveals its controls after it has wired up successfully,
   and a thrown error in one module leaves the static page intact. */
(() => {
  'use strict';
  const $ = (root, sel) => root.querySelector(sel);
  const $$ = (root, sel) => Array.from(root.querySelectorAll(sel));
  const reducedMotion = () => (window.matchMedia ? !!window.matchMedia('(prefers-reduced-motion: reduce)').matches : false);

  /* ---- Chapters: current-chapter marker + optional scroll-linked reveals ---- */
  function initChapters(root) {
    const bar = $(root, '[data-fvx-chapterbar]');
    const chapters = $$(root, '[data-fvx-chapter]');
    if (window.CSS ? (CSS.supports ? CSS.supports('animation-timeline: view()') : false) : false) {
      const sync = () => root.setAttribute('data-fvx-motion', reducedMotion() ? 'off' : 'on');
      sync();
      if (window.matchMedia) window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', sync);
    }
    if (!bar || !chapters.length || !('IntersectionObserver' in window)) return;
    const links = new Map($$(bar, 'a[href^="#"]').map((a) => [a.getAttribute('href').slice(1), a]));
    const title = $(bar, '[data-fvx-chapter-title]');
    const visible = new Map();
    const mark = (id) => {
      links.forEach((a, key) => (key === id ? a.setAttribute('aria-current', 'location') : a.removeAttribute('aria-current')));
      const chapter = chapters.find((c) => c.id === id);
      if (title) { if (chapter) title.textContent = chapter.getAttribute('data-fvx-chapter-name') || ''; }
    };
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => (e.isIntersecting ? visible.set(e.target.id, e.intersectionRatio) : visible.delete(e.target.id)));
      if (!visible.size) return;
      const best = [...visible.entries()].sort((a, b) => b[1] - a[1])[0][0];
      mark(best);
    }, { rootMargin: '-20% 0px -45% 0px', threshold: [0, 0.15, 0.4, 0.7] });
    chapters.forEach((c) => io.observe(c));
  }

  /* ---- Source drawer (native modal dialog) ---- */
  function initDrawer(root) {
    const dialog = $(root, 'dialog[data-fvx-drawer]');
    const body = dialog ? $(dialog, '[data-fvx-drawer-body]') : null;
    const templates = $$(root, 'template[data-fvx-source]');
    const openers = $$(root, '[data-fvx-open-source]');
    if (!dialog || !body || typeof dialog.showModal !== 'function' || !templates.length || !openers.length) return;
    const ids = templates.map((t) => t.getAttribute('data-fvx-source'));
    const prev = $(dialog, '[data-fvx-drawer-prev]');
    const next = $(dialog, '[data-fvx-drawer-next]');
    const labelId = 'fvx-drawer-title-' + Math.random().toString(36).slice(2, 8);
    let current = -1;
    let opener = null;

    const render = (index) => {
      const tpl = templates[index];
      body.replaceChildren(tpl.content.cloneNode(true));
      const heading = $(body, '[data-fvx-drawer-title]');
      if (heading) { heading.id = labelId; dialog.setAttribute('aria-labelledby', labelId); }
      current = index;
      if (prev) prev.disabled = index === 0;
      if (next) next.disabled = index === ids.length - 1;
      dialog.scrollTop = 0;
      try { history.replaceState(null, '', '#source-' + ids[index]); } catch (_) { /* ignore */ }
    };
    const open = (id, trigger) => {
      const index = ids.indexOf(id);
      if (index < 0) return;
      opener = trigger || opener;
      render(index);
      if (!dialog.open) { dialog.showModal(); document.documentElement.classList.add('fv-ex2-scroll-lock'); }
      const close = $(dialog, '[data-fvx-drawer-close]');
      if (close) close.focus();
    };
    openers.forEach((btn) => btn.addEventListener('click', () => open(btn.getAttribute('data-fvx-open-source'), btn)));
    $$(dialog, '[data-fvx-drawer-close]').forEach((b) => b.addEventListener('click', () => dialog.close()));
    if (prev) prev.addEventListener('click', () => { if (current > 0) render(current - 1); });
    if (next) next.addEventListener('click', () => { if (current < ids.length - 1) render(current + 1); });
    dialog.addEventListener('click', (e) => { if (e.target === dialog) dialog.close(); });
    dialog.addEventListener('close', () => {
      document.documentElement.classList.remove('fv-ex2-scroll-lock');
      const id = ids[current];
      try { history.replaceState(null, '', '#' + id); } catch (_) { /* ignore */ }
      const target = openers.find((b) => b.getAttribute('data-fvx-open-source') === id) || opener;
      // The browser restores focus to the element that opened the dialog during its own close steps, and the order
      // relative to this event differs between engines. Move focus on the next task so the opener of the record the
      // reader ended on (they may have paged with Next/Previous) always wins.
      setTimeout(() => { if (target) { if (target.isConnected) target.focus(); } }, 0);
      body.replaceChildren();
    });
    openers.forEach((b) => { b.hidden = false; });
    const fromHash = /^#source-(.+)$/.exec(location.hash);
    if (fromHash ? ids.includes(fromHash[1]) : false) {
      const chapter = document.getElementById(fromHash[1]);
      if (chapter) chapter.scrollIntoView();
      open(fromHash[1], openers.find((b) => b.getAttribute('data-fvx-open-source') === fromHash[1]));
    }
  }

  /* ---- Chronology: slider over documented markers; nothing is interpolated ---- */
  function initChronology(root) {
    $$(root, '[data-fvx-chronology]').forEach((box) => {
      const tool = $(box, '[data-fvx-chrono-tool]');
      const range = tool ? $(tool, 'input[type="range"]') : null;
      const out = tool ? $(tool, '[data-fvx-chrono-readout]') : null;
      const items = $$(box, '[data-fvx-marker]');
      const dots = $$(box, '[data-fvx-dot]');
      const cursor = $(box, '[data-fvx-cursor]');
      if (!tool || !range || !out || !items.length) return;
      const markers = items.map((li) => ({
        t: parseFloat(li.getAttribute('data-t')), label: li.getAttribute('data-label'), clock: li.getAttribute('data-clock'),
      }));
      const max = parseFloat(range.max) || 1;
      const fmt = (n) => (Number.isInteger(n) ? String(n) : n.toFixed(1));
      const update = () => {
        const t = parseFloat(range.value);
        let last = -1;
        markers.forEach((m, i) => { if (m.t <= t + 1e-9) last = i; });
        items.forEach((li, i) => li.setAttribute('data-passed', i <= last ? 'true' : 'false'));
        dots.forEach((d, i) => d.setAttribute('data-passed', i <= last ? 'true' : 'false'));
        if (cursor) cursor.style.setProperty('--fvx-p', String((t / max) * 100));
        const upcoming = markers[last + 1];
        const exact = last >= 0 ? Math.abs(markers[last].t - t) < 0.05 : false;
        let text;
        if (last < 0) text = 'Before the first recorded marker.';
        else if (exact) text = 'Marker ' + (last + 1) + ' at +' + fmt(markers[last].t) + ' s (' + markers[last].clock + '): ' + markers[last].label + '.';
        else text = 'At +' + fmt(t) + ' s. Last recorded marker: ' + (last + 1) + ', ' + markers[last].label + ' (+' + fmt(markers[last].t) + ' s). Nothing is recorded between markers.';
        if (upcoming ? !exact : false) text += ' Next marker: ' + upcoming.label + ' at +' + fmt(upcoming.t) + ' s.';
        out.textContent = text;
        /* Historical context views: these photos are NOT time-stamped fire evidence. */
        const photos = $(box, '[data-fvx-chrono-photo]');
        if (photos.length === 3) {
          const index = t < 6 ? 0 : (t < 11.3 ? 1 : 2);
          photos.forEach((photo, i) => {
            photo.hidden = i !== index;
            photo.classList.toggle('is-current', i === index);
          });
          const position = $(box, '[data-fvx-chrono-position]');
          if (position) {
            position.hidden = false;
            position.textContent = 'Context photo ' + (index + 1) + ' of 3 · These photographs do not depict the marked seconds.';
          }
        }
      };
      range.addEventListener('input', update);
      update();
      tool.hidden = false;
    });
  }

  /* ---- Search + chip filter for Research Desk and Atlas ---- */
  function initFilter(root) {
    const tools = $(root, '[data-fvx-tools]');
    const search = $(root, '[data-fvx-search]');
    const status = $(root, '[data-fvx-status]');
    const empty = $(root, '[data-fvx-empty]');
    const items = $$(root, '[data-fvx-item]');
    if (!tools || !search || !status || !empty || !items.length) return;
    const chips = $$(root, '[data-fvx-filter]');
    const noun = root.getAttribute('data-fvx-noun') || 'records';
    let theme = 'all';
    const run = () => {
      const needle = search.value.trim().toLocaleLowerCase();
      let shown = 0;
      items.forEach((el) => {
        const okText = !needle || (el.getAttribute('data-fvx-text') || '').toLocaleLowerCase().includes(needle);
        const okTheme = theme === 'all' || (el.getAttribute('data-fvx-theme') || '').split(' ').includes(theme);
        el.hidden = !(okText ? okTheme : false);
        if (!el.hidden) shown++;
      });
      status.textContent = shown + ' of ' + items.length + ' ' + noun;
      empty.hidden = shown !== 0;
    };
    search.addEventListener('input', run);
    chips.forEach((chip) => chip.addEventListener('click', () => {
      theme = chip.getAttribute('data-fvx-filter');
      chips.forEach((c) => c.setAttribute('aria-pressed', c === chip ? 'true' : 'false'));
      run();
    }));
    run();
    tools.hidden = false;
  }

  const modules = [initChapters, initDrawer, initChronology, initFilter];
  const boot = () => {
    document.querySelectorAll('[data-fvx]').forEach((root) => {
      if (root.getAttribute('data-fvx-ready')) return;
      let failed = false;
      modules.forEach((fn) => {
        try { fn(root); } catch (err) { failed = true; if (window.console) console.warn('[fv-ex2]', fn.name, err); }
      });
      root.setAttribute('data-fvx-ready', failed ? 'partial' : 'true');
    });
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
