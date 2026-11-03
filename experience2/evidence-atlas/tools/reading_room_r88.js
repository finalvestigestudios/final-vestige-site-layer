/* R88 progressive enhancement. The six source records and disclosures always work without JS. */
(() => {
  'use strict';
  const root = document.querySelector('#r88-main');
  const panel = document.querySelector('#r88-compare');
  if (!root || !panel) return;
  const records = [...root.querySelectorAll('article.record[data-record]')];
  if (records.length !== 6 || new Set(records.map(r => r.dataset.record)).size !== 6) return;
  const controls = records.map(r => r.querySelector('.compare-choice'));
  if (controls.some(c => !c || !c.querySelector('input[type="checkbox"]'))) return;
  const status = panel.querySelector('.compare-status');
  const output = panel.querySelector('.comparison');
  const clear = panel.querySelector('button.clear');
  if (!status || !output || !clear) return;
  const selected = [];
  function render() {
    output.replaceChildren();
    for (const id of selected) {
      const record = records.find(r => r.dataset.record === id);
      if (!record) continue;
      const card = document.createElement('section');
      card.className = 'comparison-card';
      const heading = document.createElement('h3');
      heading.textContent = 'Source ' + id + ': ' + record.dataset.title;
      card.append(heading);
      for (const [label, key] of [['Catalog', 'catalog'], ['Photograph date', 'date'], ['Evidence boundary', 'limit']]) {
        const p = document.createElement('p');
        const strong = document.createElement('strong'); strong.textContent = label + ': ';
        p.append(strong, document.createTextNode(record.dataset[key] || ''));
        card.append(p);
      }
      const official = record.querySelector('a.source');
      const link = official.cloneNode(true);
      card.append(link);
      output.append(card);
    }
    status.textContent = selected.length === 2 ? 'Two sources selected. Compare their dates, identities and evidence limits.'
      : selected.length === 1 ? 'One source selected. Select one more to compare.'
      : 'No sources selected. The original six evidence plates remain available below.';
    clear.disabled = selected.length === 0;
  }
  for (const control of controls) {
    const checkbox = control.querySelector('input');
    checkbox.addEventListener('change', () => {
      const id = checkbox.value;
      const index = selected.indexOf(id);
      if (index >= 0) selected.splice(index, 1);
      if (checkbox.checked) selected.push(id);
      if (selected.length > 2) {
        const displaced = selected.shift();
        const previous = controls.find(c => c.querySelector('input').value === displaced);
        if (previous) previous.querySelector('input').checked = false;
      }
      render();
    });
  }
  clear.addEventListener('click', () => {
    selected.splice(0);
    for (const c of controls) c.querySelector('input').checked = false;
    render();
    controls[0].querySelector('input').focus();
  });
  for (const c of controls) c.hidden = false;
  panel.hidden = false;
  render();
})();
