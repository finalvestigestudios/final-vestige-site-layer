/* Apollo R381: progressive local filtering only. No network, storage, metrics or DOM source rewriting. */
(function () {
  'use strict';
  function enhance(root) {
    var controls = root.querySelector('[data-fv-atlas-controls]');
    var filter = root.querySelector('[data-fv-atlas-filter]');
    var reset = root.querySelector('[data-fv-atlas-reset]');
    var status = root.querySelector('[data-fv-atlas-status]');
    var plates = Array.prototype.slice.call(root.querySelectorAll('[data-fv-atlas-plate]'));
    var phases = Array.prototype.slice.call(root.querySelectorAll('[data-fv-atlas-phase]'));
    if (!controls || !filter || !reset || !status || plates.length !== 6 || phases.length !== 3) { return; }
    var allowed = ['all','test','hazard','record','uncertainty','response'];
    function render() {
      var value = allowed.indexOf(filter.value) >= 0 ? filter.value : 'all';
      var count = 0;
      plates.forEach(function (plate) {
        var shown = value === 'all' || plate.getAttribute('data-fv-atlas-facet') === value;
        plate.hidden = !shown;
        if (shown) { count++; }
      });
      phases.forEach(function (phase) {
        phase.hidden = !phase.querySelector('[data-fv-atlas-plate]:not([hidden])');
      });
      status.textContent = count + (count === 1 ? ' reviewed source record shown.' : ' reviewed source records shown.');
    }
    filter.addEventListener('change', render);
    reset.addEventListener('click', function () { filter.value = 'all'; render(); filter.focus(); });
    controls.hidden = false;
    render();
  }
  function setup() { document.querySelectorAll('[data-fv-atlas]').forEach(enhance); }
  if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', setup); }
  else { setup(); }
}());
