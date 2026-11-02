/* Emergency kit and go-bag planner: page behavior. Choices and ticks live only in the page's checkboxes. */
(function () {
  var app = document.getElementById('kb-app');
  if (!app || typeof kbVisibleGroups !== 'function') return;
  document.documentElement.setAttribute('data-kb-js', '');
  var $ = function (id) { return document.getElementById(id); };
  var checklist = $('kb-checklist');

  function selected() {
    return Array.prototype.filter.call(app.querySelectorAll('[data-scenario]'), function (c) { return c.checked; }).map(function (c) { return c.getAttribute('data-scenario'); });
  }
  function groups() {
    return Array.prototype.map.call(checklist.querySelectorAll('.kb-group'), function (g) {
      return { id: g.getAttribute('data-group'), scenario: g.getAttribute('data-scenario-group') || '', node: g };
    });
  }
  function items() {
    return Array.prototype.map.call(checklist.querySelectorAll('[data-kb-item]'), function (c) {
      var g = c.closest('.kb-group');
      return { id: c.getAttribute('data-kb-item'), checked: c.checked, visible: !g.hidden, group: g.getAttribute('data-group'),
        groupTitle: g.querySelector('h3').textContent, label: c.closest('.kb-label').querySelector('.kb-text').textContent };
    });
  }
  function status(msg) { var s = $('kb-summary'); if (s) s.textContent = msg; }
  function refresh() {
    var vis = kbVisibleGroups(groups().map(function (g) { return { id: g.id, scenario: g.scenario }; }), selected());
    groups().forEach(function (g, i) { g.node.hidden = !vis[i].visible; });
    status(kbSummaryText(kbSummarize(items())));
  }
  function labels() {
    return Array.prototype.filter.call(app.querySelectorAll('[data-scenario]'), function (c) { return c.checked; }).map(function (c) { return c.parentNode.querySelector('span').firstChild.textContent.trim(); });
  }
  app.addEventListener('change', function (ev) { if (ev.target.hasAttribute('data-scenario')) refresh(); });
  checklist.addEventListener('change', function (ev) { if (ev.target.hasAttribute('data-kb-item')) status(kbSummaryText(kbSummarize(items()))); });
  app.addEventListener('click', function (ev) {
    var b = ev.target.closest('[data-kb-action]'); if (!b) return;
    var a = b.getAttribute('data-kb-action');
    if (a === 'print') {
      document.body.setAttribute('data-kb-print', '1');
      var done = function () { document.body.removeAttribute('data-kb-print'); window.removeEventListener('afterprint', done); };
      window.addEventListener('afterprint', done); window.print(); done();
    } else if (a === 'download') {
      var blob = new Blob([kbToText({ scenarios: labels(), items: items() })], { type: 'text/plain;charset=utf-8' });
      var url = URL.createObjectURL(blob), l = document.createElement('a');
      l.href = url; l.download = 'emergency-kit-checklist.txt'; document.body.appendChild(l); l.click(); document.body.removeChild(l);
      setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
      status('Saved to your device as emergency-kit-checklist.txt. It was not sent anywhere.');
    } else if (a === 'reset') {
      Array.prototype.forEach.call(app.querySelectorAll('[data-scenario]'), function (c) { c.checked = c.getAttribute('data-scenario') === 'adults'; });
      Array.prototype.forEach.call(checklist.querySelectorAll('[data-kb-item]'), function (c) { c.checked = false; });
      refresh(); status('Choices and ticks cleared. ' + $('kb-summary').textContent);
    }
  });
  refresh();
})();
