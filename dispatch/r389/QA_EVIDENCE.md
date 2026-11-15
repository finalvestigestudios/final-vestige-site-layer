# R389 — Exact-source native QA and non-send acceptance evidence

**Branch:** `dispatch-r389-clever-hans-recipient-normalization-20261115`, stacked on DRAFT #2673 @ `eb10f01ee60e0eb0c1e7f79eb5478f2038a15494`. Original campaign PR #175 @ `d57ccdba3aee8f065e143e101c2945f4f3d01647` **UNMODIFIED**; gate PR #201 untouched. This is evidence for [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). All edits are new files under `dispatch/r389/`, plus a narrowly scoped local bugfix to R389's own offline HTML before closing the PR.

### Source and test execution
- Original six PR #175 Python test assertions independently **reproduced 6/6** against all eight exact GitHub Git blob IDs plus manifest and `test_campaign.py`. This run did **NOT** execute that Python test file natively. Previous R388 run did execute the master suite natively 6/6; do not roll that into this run's native count.
- R389 `recipient_gate.mjs` and `recipient_gate.test.mjs` were written to a local native Node 22 environment. **21/21 Node tests passed**, 0 failed, using `node --test recipient_gate.test.mjs`.
- Exact local Git hash for `recipient_gate.mjs` `02bdf16d8b8ca9f64556688f86800a2e3180d58e` matched GitHub blob; test file Git hash `10818168d181490356f9e9b1fb2375ff3c0f9cd2` matched GitHub blob. Executed code is **identical to committed source**.
- Historical issue candidate and email-style HTML underwent **18/18 V8 source assertions** for true chronology, one primary CTA, honest no-medical-claims, retained legal hold, table semantics, single H1, no JavaScript, no external images, source links and plain-text coverage.
- R389 offline HTML specimen exact GitHub blob after fix: `6285ea84b1d2b910bf6432daaf054eb85de45f3d`; the local file used by Chromium has the **same** Git hash.
- Real offline Chromium / Python Playwright test: **initial FAIL** at 320px / 200% zoom (document width 381px, viewport 320px), due to wide title/table text; fixed scoped word wrapping, constrained table layout and padding, **final PASS 9/9**: widths 320/360/390/768/1200 and 200% zoom at 320/390/768/1200. Reproducible source is `browser_qa.py`; recorded measurements in `BROWSER_QA.json`; screenshots 320/390/768 included in a separate offline bundle (not pushed into the GitHub repo, no publication).
- Browser measured: exactly one H1, one intended editorial primary CTA to live Mesmerism article, historical source links separate, legal hard-stop placeholders present. This is a **static HTML specimen** only, NOT a native Jetpack preview, delivered-email proof or screen-reader audit. No screenshot is asserted to show actual subscriber content.

### Site and merchant evidence checked read-only
- WordPress newsletter status `as_of=2026-11-15T23:37:10Z`: 3 total, 3 confirmed, 2 unconfirmed, 0 suppressed, 0 paid; recent five records all `never_sent_opted_out`. Actual email-eligible inbox count remains UNKNOWN. WordPress newsletter settings `as_of=2026-11-15T23:37:12Z`: ON, auto-new-post OFF, FULL, welcome with Focus PDF, no-reply, no categories.
- Confirmed and unconfirmed counters **are not required to add to total** per WordPress official documentation [Manage subscribers](https://wordpress.com/support/subscribers/). Previous 'count conflict' language in the R388/earlier notes was too strong based on the aggregate numbers alone. This is a real diagnostic correction, not verified eligible-recipient evidence.
- Gmail has an October 25 confirmation request, **not** a verifiable final welcome delivery. Seller consumer promo emails not equal named affiliate approval. No exact-SKU email rights or referred checkout observed.
- Official seller pages Zen12/Total Focus were examined but no account-specific contract or affiliate earning URL verified. Prices vary or are conditional, so no price is included in the new candidate.
- FTC CAN-SPAM and WordPress native Preview email documentation checked (sources in SOURCE_OF_TRUTH_AND_RELEASE.md).

### Release disposition (no new live activity)
- Original six: `HOLD_UNSENT`; 03 and 05: `HOLD_MERCHANT`; 04: `HOLD_COPY`. R389 alternate Issue 02: `NOT_ADOPTED`.
- No final founder send/audience/schedule approval; no verified qualifying publisher postal address, actual native unsubscribe, native Jetpack Preview email, real welcome receipt, merchant EMAIL permissions/earning URL, settled publisher commission, audited qualified human denominator.
- No WordPress write, no email or test email, no subscriber contact or list export/import, no merchant or affiliate activation, no Grok social post/queue edit, no new tracking code or spending, no deployment/merge.
- `net realized publisher revenue / 1,000 qualified human sessions = NOT_COMPUTABLE` because authoritative components are missing; this is not a zero measured revenue claim.

### Owner acceptance handoff
**Focus/Claude/Founder:** private provider-email-status filter, consent dedup and previously received Fieldbook welcome. **Dispatch/Founder:** native non-sending Preview, actual sender address/footer/unsub, approval of one recipient cohort and schedule. **Mind/Commerce:** exact seller SKU, named partner EMAIL authorization, rights-cleared approved guide, specific earning URL and referred checkout. **Grok/Praxxis/Claude:** authentic source-tagged on-topic asset IDs, audited sessions and eventual merchant-confirmed commission data without exposing subscriber identities.
