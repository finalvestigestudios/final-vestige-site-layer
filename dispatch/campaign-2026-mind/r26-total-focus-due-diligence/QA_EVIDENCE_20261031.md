# R26 — independently executed editorial, code, and compliance evidence

**Date:** 2026-10-31. **Scope:** `dispatch/campaign-2026-mind/` only, stacked on draft PR #338 at `dce76cddcc90cd12aa2b959ca724f70b0a95d8cf`. Owner Issue #174; merchant owner Issue #171. **NOT A SEND AUTHORIZATION.**

## What was actually executed

1. Reconstructed the prior R25 source slice from earlier source/QA ZIPs; independently checked GitHub Git blob identities for the exact parent Issue 05, manifest, existing preview renderer, and historic tests. Not a full fresh repository clone. Corrected one R24 local test-copy variable naming mismatch by reading the exact GitHub file and matching its blob SHA before final execution.
2. After improving Issue 05 and synchronizing manifest, ran Python command `python -m unittest discover -s dispatch/campaign-2026-mind/tests -p 'test_*.py' -q`: **134 tests, 0 failures** (104 inherited + 30 new).
3. Ran actual local Node `node dispatch/campaign-2026-mind/tools/build_previews.cjs --check`: **all 13 deterministic preview assets passed**.
4. Regenerated 13 offline previews from the **exact GitHub** renderer and actual GitHub issue/manifest contents in an isolated V8 file-system shim. Committed changed Issue 05 HTML/TXT and index. Those three Git blobs matched the independent local Node output hashes: `4e3c2434c205c86187d66ee3dab2acfe709a2f95`, `783ae70745d9197195b28fa6079b91ca553db739`, `7c1c5e21c4fa1207d9befe4e59599446efbfd4a0`.
5. Ran the exact GitHub `wordpress-post-bridge-r23/build_native_candidates.cjs` via an isolated V8 file-system shim over all six real GitHub sources, generated 8 review files and committed three changed assets: Issue 05 Gutenberg block candidate, six-issue board, compatibility ledger. **No WordPress posts created.**
6. Opened the exact locally generated Issue 05 HTML in headless Chromium with Playwright at **320 / 360 / 390 / 768 / 1024 / 1440 pixels**. 6/6 no horizontal overflow, zero page errors, present disclosures, source links, warnings, unlinked merchant placeholder, no active merchant destinations. 390px and 1440px screenshots saved in local QA evidence. This is browser verification of offline HTML, **not actual delivered email**.

## Independent privacy / legal / partner source reads

- WordPress authenticated read-only 2026-10-31 **19:38 UTC**: `subscriptions=true`, `email_new_posts_by_default=false`, `email_content_format=excerpt`, `recent_sends=[]`, `site_can_send=true`. Subscriber counters total 2, confirmed 2, unconfirmed 2, suppressed 0 may be non-additive; **actual consenting deliverable audience not verified**. The welcome configuration contains the 52-page Focus Fieldbook link; **actual receipt is unverified**. Existing /dispatch/, /focus/ and Editorial Standards reviewed read-only.
- Official merchant https://hypnosislive.com/mental-skills/total-focus currently advertises Total Focus, 33 min, 47 MB, a sample, and unproven concentration and 'brain reprogramming' claims. NIH https://www.nccih.nih.gov/health/hypnosis covers selected hypnosis research but **does not validate this product**. Third-party store variant metadata cannot establish the precise official store SKU.
- FTC https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business requires appropriate postal address and practical opt-out for commercial messages. Final Vestige business address and actual Jetpack unsubscribe/footer rendering **NOT VERIFIED**. No real received .eml evidence exists. Merchant affiliate account acceptance, email rights, tier-specific link formats, permitted creative, current checkout terms and two live reviewed buyer guides also **NOT VERIFIED**.
- Site configured to send **excerpts**, so local full-text HTML is not proof subscribers would receive the editorial content or disclosure. No email preview test or settings change authorized.

## Release state

Original **4 editorial / 2 commercial** mix unchanged. All six `HOLD_UNSENT`; Issues 03/05 also `HOLD_MERCHANT`. The placeholder `[[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]]` remains intentionally inert. No send, test send, schedule, CMS write, settings update, subscriber import, merchant contact, affiliate earning URL, new expense, merge, or homepage PR #49 edit. **Hosted GitHub Actions CI has not been verified green and prior Actions jobs failed before recording runner steps.** Do not claim CI or native delivery success from local tests.

## Next independent gates

(a) Merchant written permission for email and exact SKU tracking; (b) published and reviewed Mind-owned guide; (c) valid Final Vestige postal address; (d) real WordPress opt-out and native received email; (e) eligible subscriber scope; (f) full-text/excerpt decision with separately approved setting change if needed; (g) human final content/audience/schedule authorization. No checkboxes silently implied true.
