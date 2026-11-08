# R218 — source-mapped browser-only gift state, no live test

## Authenticated observed HTML/script
WordPress page 1579 at `/focus/`, modified 2026-11-05 17:44:02 (read-only at 2026-11-08 21:32Z). The `fvf-gift` element is initially hidden in rendered HTML. Its inline JavaScript checks:

```js
var bad=['invalid_email','error','blocked_email','opted_out','blocked'];
var q=null;
try{q=new URLSearchParams(window.location.search).get('subscribe');}catch(e){}
if(q){if(bad.indexOf(q)<0){show();}}
var c=document.querySelector('.wp-block-jetpack-subscriptions__container');
function check(){if(c){if(/\bis-subscriber\b/.test(c.className)){show();}}}
check();
if(c){if(window.MutationObserver){new MutationObserver(check).observe(c,{attributes:true,attributeFilter:['class']});}}
```

This code is treated as **untrusted client presentation**. It does not call a Jetpack API, check server-confirmed double opt-in, authenticate subscription identity, or attest received welcome. The `fvf-gift` link is a public PDF URL and may work without subscription. Browser truth and subscriber truth are separate.

| Offline synthetic condition | Gift display according to observed code | Provider confirmed lead? |
|---|---:|---|
| No `subscribe` and no matching class | Hidden | Unknown |
| `subscribe=invalid_email` | Hidden | Unknown |
| `subscribe=pending` | Visible | Unknown |
| `subscribe=failed` | Visible | Unknown |
| `subscribe=arbitrary` | Visible | Unknown |
| Container class `is-subscriber` | Visible | Unknown |
| Class text `not-is-subscriber-x` | Visible because regex word boundaries match around hyphens | Unknown |
| `subscribe=error` and class `is-subscriber` | Visible | Unknown |

Even an email confirmation success notification inside a browser **would not verify** subscriber permissions absent an authenticated provider record. A backend-confirmed event needs a stable deduplicated provider event identity, status, timestamp, and authenticated provenance. Do not copy addresses or hashes of actual recipients into GitHub.

## Distinct facts and outstanding evidence
- Verified: page source can visually reveal an ungated file for unrecognized query strings. **No evidence of a real live signup attempt using these strings, no data leak claim.**
- Verified: Jetpack reports total=3 and confirmed=3, with unconfirmed=2; these counters cannot be summed, nor directly mapped to the separate follower breakdown (WP.com=3/email=0).
- Configured: welcome message embeds the 52-page PDF download URL. **Not verified** that a specific final welcome was received.
- Not observed: authenticated per-recipient eligible audience, one genuine delivered email with unsubscribe and publisher physical mailing address, vetted live Zen12 guide, named EMAIL-affiliate permission, paid order.

## Risk to measurement
If front-end analytics is ever configured to record `confirmed_signup` when `fvf-gift` is revealed, it would incorrectly classify a query-string/UI event as verified double opt-in. This is a conditional risk: **there is no evidence that such production analytics currently exists**. An observed PDF click should be `fieldbook_download_click` (diagnostic), never an opt-in or sale.

## Native offline test
`node dispatch/r218/test_focus_client_gate.cjs` checks 27 synthetic assertions. No browser test on real users, provider authenticator, actual email or telemetry is executed.
