# Focus subscription gift-state QA (draft only)

This **offline-only** guard tests a very specific feature on the published
`/focus/` WordPress page: its inline script decides when to unhide the optional
PDF download prompt (`#fvf-gift`). The visitor's query string and the Jetpack
`is-subscriber` class are simulated with a tiny stub DOM. No real emails,
subscribers, accounts or WordPress pages are modified.

## Why this matters

The saved script observed on **October 30, 2026** contains:

```js
if(q&&bad.indexOf(q)<0){show();}
```

where `q` is the `subscribe` URL query value and `bad` lists five error states.
This allows **any other nonempty value**, including `subscribe=0` or a made-up
value, to reveal the post-submission PDF prompt. The prompt's PDF CTA carries
`data-fv-location="after_signup"`. This is a **verified saved-script logic
property**, not proof the public page renders incorrectly, of a successful or
failed Jetpack submission, or of unauthorized access: the PDF is intended to
be free and its URL is public. It can make the apparent post-signup download
state and event attribution untrustworthy for unusual or manipulated URLs.

## Run locally

```sh
node --check qa/focus/subscribe_state_guard.cjs
node --check qa/focus/subscribe_state_guard.test.cjs
node --test qa/focus/subscribe_state_guard.test.cjs
node qa/focus/subscribe_state_guard.cjs /path/to/sanitized-focus-html-export
```

The checker reads **only a local file** (for example an owner-exported,
redacted Gutenberg `content.raw` snapshot). It makes no HTTP requests. Exit 1
means an arbitrary-query review finding; 0 means the two tested arbitrary
queries did not expose the gift; 2 means inconclusive/invalid input. Exit 0
**does not certify the entire subscription workflow**. The Node VM timeout
and limited stub globals are accident guards, not a security boundary: run
only against a trusted, sanitized local WordPress export.

## Editorial handoff — no production patch proposed

Before a WordPress change, confirm real Jetpack successful/pending/error query
values from a logged-out browser and a fresh consenting test address. Then
choose a narrowly scoped and tested post-submission display rule, preserving
intended immediate PDF access, double-opt-in wording, accessible announcements,
and the approved signup helper. Do **not** change the signup mechanism, remove
the download, infer email deliverability from the state UI, or overwrite Claude's
active content. Actual welcome email receipt and PDF bytes still require
separate verification. Existing Focus campaign tracking: issue #129.

**DRAFT / DO NOT MERGE, DEPLOY OR MODIFY WORDPRESS.** This is a QA-only file
set with no runtime frontend code and no new dependencies.
