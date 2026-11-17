/* Progressive enhancement only: never tracks, transmits or mutates published historical content. */
(function () {
  'use strict';
  function init(root) {
    root.querySelectorAll('button[data-fv-r421-copy]').forEach(function (button) {
      var targetId = button.getAttribute('data-fv-r421-copy');
      var source = document.getElementById(targetId);
      if (!source || !root.contains(source)) return;
      button.hidden = false;
      button.addEventListener('click', function () {
        var status = button.parentElement.querySelector('.fv-r421__status');
        if (!status) return;
        if (!navigator.clipboard || typeof navigator.clipboard.writeText !== 'function') {
          status.textContent = 'Clipboard unavailable. Select the text above to copy it.';
          source.focus(); return;
        }
        navigator.clipboard.writeText(source.textContent || '').then(function () {
          status.textContent = 'Source receipt copied.';
        }).catch(function () {
          status.textContent = 'Copy failed. Select the text above to copy it.';
          source.focus();
        });
      });
    });
  }
  document.querySelectorAll('[data-fv-r421-receipts]').forEach(init);
}());
