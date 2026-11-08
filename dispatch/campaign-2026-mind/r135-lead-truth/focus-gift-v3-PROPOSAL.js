/* DRAFT ONLY. Narrowly scoped proposed replacement for the EXISTING
   <script id="fvf-gift-v2">; NOT deployed; needs signed-out browser QA,
   editor approval and founder release approval. No analytics or network.
   A public PDF download prompt is not proof of newsletter consent. */
(function () {
  'use strict';
  const gift = document.getElementById('fvf-gift');
  if (!gift) return;
  let acknowledged = false;
  try {
    const params = new URL(window.location.href).searchParams.getAll('subscribe');
    acknowledged = params.length === 1 && params[0] === 'success';
  } catch (_error) { acknowledged = false; }
  const container = document.querySelector('.wp-block-jetpack-subscriptions__container');
  const update = () => {
    const nativeMarker = !!container && container.classList.contains('is-subscriber');
    gift.hidden = !(acknowledged || nativeMarker);
    // DO NOT report confirmed_signup here: URL and UI markers are insufficient.
  };
  update();
  if (container && window.MutationObserver) {
    new MutationObserver(update).observe(container, {attributes: true, attributeFilter: ['class']});
  }
})();
