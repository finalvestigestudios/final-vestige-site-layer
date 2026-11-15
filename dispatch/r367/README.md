# Dispatch R367 — Non-sending MIME rehearsal + conversion evidence

**NOT RELEASED · DO NOT SEND · REVIEW FILES ONLY.** This is a separate stacked draft on [#2544](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2544), preserving the original founder 4-editorial/2-commercial pilot [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), the original hard gates [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201), and source-of-truth [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174).

## Why this is not another alternate newsletter
The latest R366 work already supplies HTML and plaintext reading previews. This sprint adds a **genuine offline multipart/alternative RFC-5322 round-trip rehearsal** with intentionally **no From, To, Cc, Bcc, Reply-To or Date headers**, forced HOLD headers, original-text and merchant-link invariant tests, and 24 Chromium viewport checks. These files are unaddressed review samples, NOT Jetpack output and NOT deliverable messages. No vendor or subscriber credentials and no real recipients.

Run with the existing Python standard library plus optional mistune and Playwright:
```bash
python -m unittest discover -s dispatch/campaign-2026-mind/tests -v
python -m unittest discover -s dispatch/r367 -p 'test_review_mime.py' -v
python dispatch/r367/build_review_mime.py dispatch/campaign-2026-mind /tmp/fv-r367-review
python dispatch/r367/browser_qa.py /tmp/fv-r367-review
```
The last command requires a local Chromium/Playwright installation. The HTML fallback uses escaped preformatted text when mistune is absent; it never fetches external assets or remote images. Do not run any generated artifact through a sending system.

Original six original issue source blob hashes were compared to master PR #175 exact HEAD `d57ccdba3aee8f065e143e101c2945f4f3d01647` before independent execution. **Local native results:** original campaign 6/6, R367 suite 20/20, isolated Chromium layouts 24/24 at 360/390/768/1440px. This does NOT establish accessibility in real inboxes, sender footer compliance, WordPress's native preview, actual download or delivery.

**Release:** All six HOLD_UNSENT; Issues 03/05 additionally HOLD_MERCHANT; alternatives not adopted. No email, test email, site setting change, subscriber contact, partner activation, PR merge, deploy, social post or spend. The frozen homepage PR #49 remains untouched.

See [seller claims](SELLER_AND_CLAIM_ATTESTATION.md), [subscriber-to-sale progression](CONVERSION_PROGRESSION.md) and [QA ledger](QA_EVIDENCE.md).