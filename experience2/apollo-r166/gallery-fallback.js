/* Apollo Evidence Atlas gallery: additive, no network, no analytics, no HTML templating.
 * Enhances the established three-photo chronology; never replaces original NASA captions.
 * Candidate for isolated WordPress staging only; not included in production. */
(()=>{'use strict';
  const SELECTOR='[data-fvx-chrono-gallery]';
  document.querySelectorAll(SELECTOR).forEach(gallery=>{
    gallery.querySelectorAll('[data-fvx-chrono-photo]').forEach(figure=>{
      if(figure.dataset.fvxFallbackBound==='yes') return;
      const img=figure.querySelector('img');
      const link=figure.querySelector('figcaption a[href^="https://www.nasa.gov/"],figcaption a[href^="https://images.nasa.gov/"]');
      if(!img||!link) return; // Fail open: retain the unmodified archival record.
      figure.dataset.fvxFallbackBound='yes';
      const report=()=>{
        if(figure.querySelector('[data-fvx-image-fallback]'))return;
        img.classList.add('fvx-chrono-gallery__image--unavailable');
        img.setAttribute('aria-hidden','true');
        const note=document.createElement('p');
        note.className='fvx-chrono-gallery__fallback';
        note.dataset.fvxImageFallback='';
        note.setAttribute('role','status');
        note.textContent='Archival image unavailable here. Its dated description and original NASA source remain below.';
        img.insertAdjacentElement('afterend',note);
      };
      img.addEventListener('error',report,{once:true});
      if(img.complete&&img.naturalWidth===0)report();
    });
  });
})();
