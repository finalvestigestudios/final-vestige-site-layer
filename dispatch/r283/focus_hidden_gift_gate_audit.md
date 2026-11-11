# Focus / Dispatch consent-gate source audit — R283

**Date:** 2026-11-11. **Scope:** authenticated, read-only WordPress page #1579 (`/focus/`) and Jetpack settings. This is a source inspection, **not browser execution, signup testing or delivery confirmation**. No live page changed.

## What the page source actually contains

The HTML has a subscriptions block and a separate download panel:

```html
<div id="fvf-gift" class="fvf-gift" hidden role="status">
  <p>Your fieldbook is ready to download.</p>
  <a href="[52-page Fieldbook PDF URL]" data-fv-event="focus_pdf_click" data-fv-location="after_signup">Download the Seven Day Focus Fieldbook</a>
</div>
```

CSS `.fvf-gift[hidden] { display: none; }` correctly hides the panel on the initial page. The published `<script id="fvf-gift-v2">` has this relevant conditional (whitespace normalized; do not confuse this illustrative excerpt with authorized production code):

```js
var bad=['invalid_email','error','blocked_email','opted_out','blocked'];
var q = new URLSearchParams(window.location.search).get('subscribe');
if(q){if(bad.indexOf(q)<0){show();}}
var c=document.querySelector('.wp-block-jetpack-subscriptions__container');
function check(){if(c && /\bis-subscriber\b/.test(c.className)){show();}}
```

**Potential defect:** an unrecognized, nonempty query parameter such as `?subscribe=unknown_state` satisfies this conditional and reveals the download panel, even though no authenticated Jetpack confirmation necessarily occurred. That is a *UI state / attribution evidence weakness*, not a demonstrated security bypass or material leak: the Fieldbook is intended as a free PDF, and the observed code only changes what is shown in the browser. We did not navigate a crafted URL or contact a subscriber.

### Source-logic examples (predictions only; not executed)

| Input to existing client-side logic | Predicted `#fvf-gift` state | What it proves |
|---|---|---|
| no `subscribe` query, not `is-subscriber` | Hidden | No panel yet |
| `subscribe=invalid_email` | Hidden | Known blocked value |
| `subscribe=blocked` | Hidden | Known blocked value |
| `subscribe=success` | Shown | Arbitrary allowed status, **not provider eligibility** |
| `subscribe=unknown_state` | Shown | A non-allowlisted query could produce false ready-state |
| `is-subscriber` class | Shown | Client display condition, not independent server attestation |

### Recommendation to Focus/Claude (not permission to edit)

Validate only documented provider success states for **display**; avoid depending on mere presence of a non-denylisted URL parameter. Show a clear pending-confirmation message if confirmation is not established; do not falsely imply confirmed subscription. Treat the PDF's clickable state as fulfillment-interest only, separate from `confirmed_signup`. Confirm provider-side eligible subscription with consent provenance and deduped opaque internal key before counting a lead. Review welcome link actual reception privately with founder-authorized test, and ensure accessible fallback states for scripts disabled or loading.

Do **not** add a new analytics script, store subscriber PII, make a cross-device person-level join, activate an offer, or launch a new mailing list. Send and paid-order events remain wholly separate. Report conversion metrics **unknown** until independently verified.

**Owner:** Claude/Focus Issue #129; Dispatch Issue #174 tracks the measurement contract; Grok/Praxxis Issue #820 coordinate attribution only. Published page remains unchanged.
