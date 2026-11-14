# R362 independently executed QA and provenance

## Original source untouched

Master draft [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) still has HEAD `d57ccdba3aee8f065e143e101c2945f4f3d01647` and is OPEN/DRAFT. Current GitHub connector readback of its manifest, test file and six original issues matches **8/8 expected Git blob SHA-1 identifiers** to the archived source fixture. The original campaign test executed **6/6 PASS** under native Python in the isolated local working container on November 14, 2026. No original drafts or manifest edited.

## R362 new native checks

Offline source file `funnel_truth.py` was executed with `python -m unittest -v test_funnel_truth`: **32/32 PASS**, using synthetic fabricated events only, no emails/network/merchant/WordPress accesses. Groups:

- Eight subscriber-snapshot tests, including count non-additivity, missing/negative/boolean count rejection and technical send capability never meaning permission.
- Fifteen receipt tests, including PDF download ≠ signup, attempt ≠ confirmation, claimed provider receipt treated only as candidate, duplicate event and duplicate provider receipt rejected, noncanonical `utm_medium=social` excluded, unverified order claim not a paid sale, and no echo of private recipient identifiers.
- Nine settlement/hold tests, including an illustrative arithmetic-only net revenue formula, missing/invalid denominators, refunds, negative net, four/two issue allocation and always-HOLD release.

After committing `funnel_truth.py` and `test_funnel_truth.py`, the source was retrieved directly from GitHub on the draft branch; its blob hashes matched the exact locally executed files:

- `funnel_truth.py`: `a837f5b1afce39819691e895e26199f5ef374ac6`
- `test_funnel_truth.py`: `f06cf36f1f0d4e83a254428d442828050eb04504`

**Test fixture caution:** the 3/3/2 values in tests correspond to the observed provider aggregate but are *synthetic input fixtures*, not actual subscriber rows or a private recipient lookup. Likewise, the $85.00 hypothetical example from 1,000 sessions is an arithmetic illustration **not reported revenue**. Tests do NOT prove WordPress's real event callback, browser pixels, inbox receipt or merchant ledger integrity.

## Current production observations / gaps

Authenticated newsletter status/settings at **2026-11-14 20:39 UTC**: subscriptions ON, can-send true, automatic new-post sends OFF, full content, sender Final Vestige Studios, reply-to no-reply, welcome Fieldbook configured; total3/confirmed3/unconfirmed2/suppressed0, WordPress.com followers3/email0; five sampled post notifications `never_sent_opted_out`. Actual eligible recipients, real double opt-in, received welcome, compliant physical address and unsubscribe behavior remain UNKNOWN.

Public [/focus/](https://finalvestige.com/focus/) independently shows a download CTA and a separate confirm-email instruction; direct public PDF retrieval in the crawler returned **cache miss**, not verified download success. Public [/dispatch/](https://finalvestige.com/dispatch/) has a rendered subscription input. No form submission performed.

[Official WordPress preview workflow](https://wordpress.com/support/newsletter/email-appearance/) was reviewed; only the preview action is non-sending. A real Preview email through authenticated site UI was not performed in this run, and no Send test email is authorized. [FTC guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) was reviewed; publisher address and functional opt-out remain release blockers.

[Official Total Focus SKU](https://hypnosislive.com/mental-skills/total-focus) was directly checked and lists 33min/47MB. Seller marketing claims and headline 14-day refund are not independent efficacy/refund at referred checkout. Inspire3 **named** publisher approval, EMAIL permission, account earning URLs, exact price/commission and live guide remain UNVERIFIED. No merchant links activated.

## Source vs QA vs actual business outcome

**BUILT:** privacy-minimizing classifier and original-gate docs, six-issue mapping. **TESTED:** 32 synthetic Python cases and 6 original master cases; source hashes pinned. **LIVE:** only existing public Focus/Dispatch pages and current Jetpack settings. **NOT VERIFIED:** qualified-human sessions, actual confirmed-recipient population, downloads, received welcome, native email UI/opt-out, merchant rights and independently settled paid orders.

**Release:** six HOLD_UNSENT, 03/05 also HOLD_MERCHANT; all optional copy NOT_ADOPTED; net revenue / 1,000 qualified human sessions NOT COMPUTABLE. No emails, tests emails, WordPress writes, imports, tracking deployment, publishing, affiliate activation, social posts, merges or costs. Homepage flagship and PR #49 untouched.
