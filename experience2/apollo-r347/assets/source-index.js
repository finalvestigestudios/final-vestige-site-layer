/* Optional source-index filter. Atomic enhancement: source records remain usable without JavaScript. */
(function () {
  'use strict';
  var choices = [
    ['all', 'All records'], ['findings', 'Board findings'],
    ['chronology', 'Chronology'], ['later', 'Later history'], ['photos', 'Photographs']
  ];

  function upgrade(root) {
    if (root.dataset.fvApolloIndexReady === '1') return;
    var bar = root.querySelector('[data-fv-apollo-filters]');
    var status = root.querySelector('[data-fv-apollo-status]');
    var entries = root.querySelectorAll('[data-fv-apollo-entry]');
    var groups = Array.prototype.slice.call(root.querySelectorAll('[data-fv-apollo-group]'));
    if (!bar || !status || entries.length !== 13 || groups.length !== 4) return;
    // Only enhance a complete, curator-approved set. Unexpected/missing groups stay fully readable.
    var keys = groups.map(function (group) { return group.dataset.fvApolloGroup; });
    if (keys.slice().sort().join('|') !== 'chronology|findings|later|photos') return;
    var buttons = [];
    function restore() {
      groups.forEach(function (group) { group.removeAttribute('hidden'); });
      bar.textContent = '';
      bar.hidden = true;
      status.hidden = true;
      status.textContent = '';
      root.removeAttribute('data-fv-apollo-index-ready');
    }
    function select(key, selected) {
      try {
        var count = 0;
        groups.forEach(function (group) {
          // The only hidden content is an optional JS filter; on any failure, reveal it all.
          group.hidden = key !== 'all' && group.dataset.fvApolloGroup !== key;
          if (!group.hidden) count += group.querySelectorAll('[data-fv-apollo-entry]').length;
        });
        buttons.forEach(function (button) {
          button.setAttribute('aria-pressed', button === selected ? 'true' : 'false');
        });
        status.textContent = 'Showing ' + count + ' of ' + entries.length + ' evidence entries.';
      } catch (error) {
        restore();
      }
    }
    try {
      var fragment = document.createDocumentFragment();
      choices.forEach(function (choice) {
        var button = document.createElement('button');
        button.type = 'button';
        button.textContent = choice[1];
        button.setAttribute('aria-pressed', choice[0] === 'all' ? 'true' : 'false');
        button.addEventListener('click', function () { select(choice[0], button); });
        fragment.appendChild(button);
        buttons.push(button);
      });
      // Commit the entire control set at once. If creation/installation fails, defaults survive.
      bar.appendChild(fragment);
      status.textContent = 'Showing all ' + entries.length + ' evidence entries.';
      bar.hidden = false;
      status.hidden = false;
      root.dataset.fvApolloIndexReady = '1';
    } catch (error) {
      restore();
    }
  }

  function ready() {
    Array.prototype.forEach.call(document.querySelectorAll('[data-fv-apollo-source-index]'), upgrade);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ready);
  else ready();
}());
