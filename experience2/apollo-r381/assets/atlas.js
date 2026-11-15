/* Apollo R382 hardens R381 progressive filtering: no dead rail anchors after facet changes. No network or storage. */
(function () {
  'use strict';
  function enhance(root) {
    if (root.dataset.fvAtlasEnhanced === 'yes') { return; }
    var controls = root.querySelector('[data-fv-atlas-controls]');
    var filter = root.querySelector('[data-fv-atlas-filter]');
    var reset = root.querySelector('[data-fv-atlas-reset]');
    var status = root.querySelector('[data-fv-atlas-status]');
    var plates = Array.prototype.slice.call(root.querySelectorAll('[data-fv-atlas-plate]'));
    var phases = Array.prototype.slice.call(root.querySelectorAll('[data-fv-atlas-phase]'));
    var links = Array.prototype.slice.call(root.querySelectorAll('.fv-a381__rail a[href^="#"]'));
    if (!controls || !filter || !reset || !status || plates.length !== 6 || phases.length !== 3 || links.length !== 3) { return; }
    var navItems = phases.map(function (phase) {
      var link = links.find(function (item) { return item.getAttribute('href') === '#' + phase.id; });
      return link && link.closest('li');
    });
    if (navItems.some(function (item) { return !item; })) { return; }
    var allowed = ['all','test','hazard','record','uncertainty','response'];
    function recover() {
      plates.forEach(function (item) { item.hidden = false; });
      phases.forEach(function (item) { item.hidden = false; });
      navItems.forEach(function (item) { item.hidden = false; });
      controls.hidden = true;
      root.dataset.fvAtlasEnhanced = '';
    }
    function render() {
      try {
        var value = allowed.indexOf(filter.value) >= 0 ? filter.value : 'all';
        var count = 0;
        plates.forEach(function (plate) {
          var shown = value === 'all' || plate.getAttribute('data-fv-atlas-facet') === value;
          plate.hidden = !shown;
          if (shown) { count++; }
        });
        phases.forEach(function (phase, index) {
          var active = !!phase.querySelector('[data-fv-atlas-plate]:not([hidden])');
          phase.hidden = !active;
          navItems[index].hidden = !active;
        });
        status.textContent = count + (count === 1 ? ' reviewed source record shown.' : ' reviewed source records shown.');
      } catch (_) { recover(); }
    }
    filter.addEventListener('change', render);
    reset.addEventListener('click', function () { filter.value = 'all'; render(); filter.focus(); });
    controls.hidden = false;
    root.dataset.fvAtlasEnhanced = 'yes';
    render();
  }
  function setup() { document.querySelectorAll('[data-fv-atlas]').forEach(enhance); }
  if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', setup); }
  else { setup(); }
}());
