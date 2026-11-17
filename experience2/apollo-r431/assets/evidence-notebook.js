/* Apollo R431: progressive enhancement only. No fetch, cookies, localStorage, analytics or submissions. */
(() => {
  'use strict';
  const select = (root, selector) => root.querySelector(selector);
  const all = (root, selector) => Array.from(root.querySelectorAll(selector));
  function init(root) {
    if (root.dataset.fvR431Ready === 'yes') return;
    const questions = all(root, '.fv-r430__question');
    const controls = select(root, '[data-fv-r431-actions]');
    if (questions.length !== 3 || !controls || questions.some(q => !select(q, 'textarea') || !select(q, 'label') || !select(q, '.fv-r430__source a'))) return;
    const fields = questions.map(q => select(q, 'textarea'));
    const status = select(root, '[data-fv-r431-status]');
    const progress = select(root, '[data-fv-r431-progress]');
    const prints = [];
    let lastCount = -1;
    function setStatus(message) { status.textContent = message; }
    function update() {
      const count = fields.filter(f => f.value.trim()).length;
      if (count !== lastCount) {
        progress.textContent = `${count} of ${fields.length} answers drafted`;
        lastCount = count;
      }
      prints.forEach((node, index) => { node.textContent = fields[index].value.trim() || 'No answer written yet.'; });
    }
    function notes() {
      const lines = ['APOLLO 1 — EVIDENCE NOTEBOOK', 'Original worksheet: Final Vestige Studios', 'NASA sources linked below; no NASA endorsement.', ''];
      questions.forEach((q, i) => {
        const src = select(q, '.fv-r430__source a');
        lines.push(`QUESTION ${i + 1}: ${select(q, 'label').textContent.trim()}`);
        lines.push(`Date shown: ${select(q, 'time')?.textContent.trim() || 'See source'}`);
        lines.push(`My answer: ${fields[i].value.trim() || '[not answered]'}`);
        lines.push(`Source: ${src.textContent.trim()}`);
        lines.push(`URL: ${src.href}`, '');
      });
      lines.push('These are user-entered notes and linked historical records, not a NASA finding.');
      return lines.join('\n');
    }
    // Build all print mirrors and verify enhancement controls BEFORE revealing them.
    try {
      questions.forEach(q => {
        const p = document.createElement('p');
        p.className = 'fv-r431__print-answer';
        p.setAttribute('aria-hidden', 'true');
        select(q, 'textarea').insertAdjacentElement('afterend', p);
        prints.push(p);
      });
      const copy = select(root, '[data-fv-r431-copy]');
      const save = select(root, '[data-fv-r431-export]');
      const print = select(root, '[data-fv-r431-print]');
      if (!copy || !save || !print || !status || !progress || typeof Blob !== 'function' || !URL.createObjectURL || !URL.revokeObjectURL) throw Error('Unsupported browser');
      copy.addEventListener('click', async () => {
        if (!navigator.clipboard || typeof navigator.clipboard.writeText !== 'function') {
          setStatus('Clipboard unavailable. Select your answers individually, or use Save .txt notes.');
          return;
        }
        try { await navigator.clipboard.writeText(notes()); setStatus('Cited notes copied to your clipboard.'); }
        catch (_err) { setStatus('Copy denied by your browser. Use Save .txt notes instead.'); }
      });
      save.addEventListener('click', () => {
        let url;
        try {
          url = URL.createObjectURL(new Blob([notes()], {type:'text/plain;charset=utf-8'}));
          const a = document.createElement('a');
          a.href = url; a.download = 'apollo-1-evidence-notes.txt'; a.hidden = true;
          root.appendChild(a); a.click(); a.remove();
          setStatus('A plain-text download was requested. Check your browser downloads.');
        } catch (_err) { setStatus('Download unavailable. Select and copy your answers instead.'); }
        finally { if (url) setTimeout(() => URL.revokeObjectURL(url), 1000); }
      });
      print.addEventListener('click', () => { update(); window.print(); });
      fields.forEach(f => f.addEventListener('input', update));
      window.addEventListener('beforeprint', update);
      update();
      root.classList.add('fv-r431--enhanced');
      controls.hidden = false;
      root.dataset.fvR431Ready = 'yes';
    } catch (_error) {
      controls.hidden = true;
      root.classList.remove('fv-r431--enhanced');
      // The real, cited R430 worksheet remains usable without this enhancement.
    }
  }
  function start() { document.querySelectorAll('[data-fv-r431]').forEach(init); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();
