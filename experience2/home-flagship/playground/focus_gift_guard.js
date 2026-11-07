/* Final Vestige /focus/ — UNDEPLOYED review-only replacement for #fvf-gift-v2.
 * The gift's visibility is presentation, NEVER a confirmed subscriber metric.
 * Do not infer subscription or purchase from this UI. The live Jetpack runtime
 * must be validated before any WordPress change is approved.
 */
(function () {
  'use strict';
  var gift = document.getElementById('fvf-gift');
  if (!gift) return;
  gift.hidden = true;
  var container = document.querySelector('.wp-block-jetpack-subscriptions__container');
  if (!container) return;
  function refresh() {
    // No URLSearchParams, query-string success inference, or inferred sales.
    gift.hidden = !container.classList.contains('is-subscriber');
  }
  refresh();
  if (typeof MutationObserver === 'function') {
    new MutationObserver(refresh).observe(container, {
      attributes: true,
      attributeFilter: ['class']
    });
  }
})();
