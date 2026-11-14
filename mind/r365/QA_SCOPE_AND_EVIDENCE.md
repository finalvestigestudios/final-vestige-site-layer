# Mind R365 — Source-bound QA record
Date: November 13, 2026 (PT)  
State: **DRAFT ONLY / HARD HOLD / NO LIVE ACTIONS**

## Actually executed

- Read back all **eight** committed source files on the exact R365 branch through the authenticated GitHub connector.
- Evaluated **59 / 59** isolated V8 static source and safety checks against the GitHub-fetched file contents, all passing after correcting an overly broad test that initially mistook `aria-disabled` for the native `disabled` attribute and two brittle phrase assertions.
- Eight deliberately unsafe source mutations were injected into a synthetic copy of Variant A and **8 / 8 rejected**: native disabled removal, deletion of affiliate disclosure label, deletion of commission text, unapproved Zen12 anchor, injected script, iframe, form/email input, and autoplay video.
- A and B share **identical substantive buyer copy**; only B has an original illustrated SVG poster, detailed screen-reader description, transcript, and a separate six-cue VTT ending at exactly 42 seconds.
- All commercial gates in the final matrix remain HOLD; no active merchant destination is present; no extra signup or runtime tracking has been introduced.
- Relevant official sources were viewed November 13, 2026: https://inspire3.com/ ; https://zen12.com/ ; https://hypnosislive.com/mental-skills/total-focus ; https://hypnosislive.com/faq ; https://affiliates.inspire3.com/ ; FTC official endorsement/health claims; the actual published 52-page Focus page and Puységur archive.
- Scoped only to new `mind/r365/` paths. No core site files, existing homepage art, canonical Mind hub PR #172, Dispatch, grok queues or WP CMS were changed.

## Committed but **not** actually executed in native Node

The file `verify.mjs` is committed as an independently reproducible check using Node's native `assert` and filesystem APIs. The 59 V8 assertions above are independently reconstructed source checks, **not a claim of native execution of `verify.mjs`**. The original source had a QA test false positive, and the final test script was corrected before this report.

## NOT tested / NOT verified

Native Node on a checkout of this branch; hosted CI; production build; WordPress HTML sanitization; actual WCAG 2.2 AA browser and assistive technology; 360/390/768/1440/1920 physical/browser layouts; screen reader announcements, visual contrast, 200–400% zoom; real 42-second encode, playback, transcript/caption synchronization or media CWV; real Jetpack consent/confirmed welcome delivery; live seller checkout or refund; partner-specific approval/link/commission terms; Grok actual published mind video asset IDs; first-party qualified-human data; verified paid orders or settled affiliate commissions.

## Critical blockers by priority

1. **Founder/Commerce:** named Inspire3 partner acceptance + permitted channels + issued tracked URL, or verified rights-cleared, actually sellable FV-owned Mind Payhip SKU with tested delivery/refund/checkout.
2. **Grok/Praxxis:** three genuine already-published on-topic media IDs, actual platform link rules, and exact landing intent match. Drive TASK-008 is the *existing* coordination lane. No new task assigned.
3. **Claude/Site QA:** native browser accessibility, WordPress sanitizer and contrast, current Jetpack subscriber consent/delivery, existing first-party measurement instrumentation (avoid duplication).
4. **Founder:** final approval before publishing, merging, deploying or activating merchant links.

Commercial results: **unknown**, not zero. Gross revenue, commissions, confirmed paid orders, refunds, fees, attributed qualified-human sessions and net revenue per 1,000 sessions are **NOT COMPUTABLE**.

**QA conclusion:** source controlled = BUILT; 59 isolated static checks = TESTED LIMITED; playback/browser/transactions = NOT TESTED; WordPress/affiliate links = NOT LIVE; realized revenue = NOT VERIFIED. HARD HOLD.
