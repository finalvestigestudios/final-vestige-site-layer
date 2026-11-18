// Review-only patch generator. No WordPress writes, subscriber queries or sending APIs.
export const LIVE_MODIFIED = '2026-11-16T14:54:58';
export const OLD_PANEL = String.raw`<div id="fvf-gift" class="fvf-gift" hidden role="status">
    <p class="fvf-gift-title">Your fieldbook is ready to download.</p>
    <a class="fvf-btn" href="https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf" data-fv-event="focus_pdf_click" data-fv-location="after_signup">Download the Seven Day Focus Fieldbook</a>
    <p class="fvf-micro">Please confirm your email to join The Dispatch. The welcome email will include this same download link. Check Spam or Promotions if needed.</p>
  </div>`;
export const NEW_PANEL = String.raw`<div id="fvf-gift" class="fvf-gift" role="region" aria-labelledby="fvf-gift-title">
    <h3 id="fvf-gift-title" class="fvf-gift-title">Read the free Fieldbook</h3>
    <p class="fvf-micro">You can read this 52-page PDF without subscribing. There is no purchase or email confirmation required to download it.</p>
    <a class="fvf-btn" href="https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf" data-fv-event="focus_pdf_click" data-fv-location="public_fieldbook">Download the Seven Day Focus Fieldbook</a>
    <p class="fvf-micro">The Dispatch is optional. If you subscribe using the form above, follow WordPress's confirmation instructions when prompted. Our configured welcome message includes this same Fieldbook link. A PDF download is not a confirmed newsletter subscription.</p>
  </div>`;
export const OLD_SCRIPT = String.raw`<script id="fvf-gift-v2">(function(){var g=document.getElementById('fvf-gift');if(!g){return;}
var bad=['invalid_email','error','blocked_email','opted_out','blocked'];
function show(){g.hidden=false;}
var q=null;try{q=new URLSearchParams(window.location.search).get('subscribe');}catch(e){}
if(q){if(bad.indexOf(q)<0){show();}}
var c=document.querySelector('.wp-block-jetpack-subscriptions__container');
function check(){if(c){if(/\bis-subscriber\b/.test(c.className)){show();}}}
check();if(c){if(window.MutationObserver){new MutationObserver(check).observe(c,{attributes:true,attributeFilter:['class']});}}})();</script>`;

function occurrences(haystack, needle) {
  if (!needle) return 0;
  return haystack.split(needle).length - 1;
}
export function proposeFocusPatch(content, modified = LIVE_MODIFIED) {
  if (typeof content !== 'string' || content.length < 200) throw new Error('SOURCE_REQUIRED');
  if (modified !== LIVE_MODIFIED) throw new Error('STALE_WORDPRESS_VERSION');
  if (!content.includes('<!-- wp:jetpack/subscriptions')) throw new Error('JETPACK_FORM_MISSING');
  if (occurrences(content, OLD_PANEL) !== 1) throw new Error('EXPECTED_PANEL_NOT_UNIQUE');
  if (occurrences(content, OLD_SCRIPT) !== 1) throw new Error('EXPECTED_SCRIPT_NOT_UNIQUE');
  if (content.includes(NEW_PANEL)) throw new Error('ALREADY_PATCHED');
  const changed = content.replace(OLD_PANEL, NEW_PANEL).replace(OLD_SCRIPT, '');
  if (changed.includes('id="fvf-gift-v2"') || changed.includes('data-fv-location="after_signup"'))
    throw new Error('STALE_CONSENT_SIGNAL');
  if (occurrences(changed, 'data-fv-event="focus_pdf_click"') !== occurrences(content, 'data-fv-event="focus_pdf_click"'))
    throw new Error('PDF_EVENT_COUNT_CHANGED');
  return { content: changed, sourceModified: modified,
    changedElements: ['free download visibly accessible before subscription', 'spoofable query/class reveal removed',
      'PDF event location no longer implies signup', 'no new signup list or event'], readyToPublish: false };
}
