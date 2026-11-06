/* FV EX2 — REVIEW ONLY. Never assert this proves a confirmed subscriber.
   Jetpack's 'subscribe=success' is a SUBMISSION status, not a verified confirmation.
   Fail closed on undocumented query values; do not add analytics or send messages.
   Source for live comparison: WordPress Page 1579 modified 2026-11-05 17:44:02.
 */
(function () {
  'use strict';
  var gift = document.getElementById('fvf-gift');
  if (!gift) return;
  var widget = document.querySelector('.wp-block-jetpack-subscriptions__container');
  var submissionAccepted = false;
  try {
    submissionAccepted = new URLSearchParams(window.location.search).get('subscribe') === 'success';
  } catch (e) {
    submissionAccepted = false;
  }
  function inspect() {
    var widgetShowsSubscriber = !!(widget && widget.classList.contains('is-subscriber'));
    // The PDF is an ungated free resource. This only controls when the
    // 'after signup' panel is displayed, not whether a visitor can obtain it.
    if (submissionAccepted || widgetShowsSubscriber) gift.hidden = false;
  }
  inspect();
  if (widget && window.MutationObserver) {
    new MutationObserver(inspect).observe(widget, {
      attributes: true, attributeFilter: ['class']
    });
  }
})();
