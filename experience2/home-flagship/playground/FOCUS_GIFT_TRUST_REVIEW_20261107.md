# EX2 / Focus Fieldbook — URL-spoofed gift-message review patch (2026-11-07)

**REVIEW ONLY — RELEASE HOLD.** Parent is #1443; #1415 demonstrated that the currently published Page 1579 gift UI can be revealed by an arbitrary `?subscribe=made_up_value` string without a subscriber. This patch addresses that **specific UI false-positive**; it does not solve the earlier source-only self-linking Jetpack fallback or prove a confirmed subscriber. It is *not* approved for WordPress deployment.

**Offer → step → blocker → change → evidence → owner.** Free 52-page Seven Day Focus Fieldbook → homepage CTA /focus/ → visual download confirmation. Blocker: query-string spoofing can reveal post-signup copy. Candidate: remove URL-based gift promotion; show only when Jetpack renders an `is-subscriber` DOM state; hide again if removed. Evidence: 13/13 local Python/Chromium scenarios (seven actual browser states + six source/patch checks), 8/8 Node VM scenarios, and 390/1440 source-derived before/after Chromium fixtures (untrusted subscribe parameter revealed the old gift but no longer reveals the candidate). **Owner:** Claude/Jetpack production engineering for potential implementation; independent Site QA for browser/hydration acceptance; homepage engineering for safe proposal.

The candidate **does not equate** an `is-subscriber` CSS class with a verified subscriber. DOM classes are untrusted as commercial records; lead counts require the actual Jetpack subscriber source. GitHub issue #820 owns attribution. No new instrumentation.

## Source custody and artifact

Published read-only Page 1579 reported modified **2026-11-05 17:44:02**. Parent #1415 contains `focus_gift_source_20261107.json` with original inline-script SHA-256 `f5b7a56cf46a17b350a6245684cc222d59ce4b7da62650515d208169f89426a7`. `propose_focus_gift_guard.py` verifies that exact source before writing *a distinct local HTML preview*, never WordPress. Refuses drift, duplicate tags, same-input overwrite and candidate URL/network state signals. Run `node test_focus_gift_guard.mjs` against the inherited pinned fixture; optionally run the Python/Chromium suite from the engineering evidence package.

## Before / after and blocked gates

With spoofed `?subscribe=made_up_value`, original UI: gift message **visible**, no form submission or subscriber confirmation. Candidate: gift message **hidden**. Same in 390px and 1440px source-derived Chromium fixtures; existing `is-subscriber` class and mutation still display/hide the gift. These are **synthetic DOM scenarios, not WordPress.com browser measurements**.

**Block on live release** until Jetpack's real browser-delivered signup and confirmation behavior is independently established at 360/390/768/1440px, including keyboard, no-JS, disabled/reduced-motion, and live redirected subscription states, with permission before any test subscriber. Removing a query fallback may impede a legitimate Jetpack redirect if that is the only confirmation signal. Current Page 1579 API markup contains only a self-linking fallback instead of a form; the backend/JS hydration is unverified. Need approved remedy for absent Jetpack form, real image transfer bytes, full homepage Assembler staging acceptance, axe/Lighthouse/CWV and independent CI/QD. Do not deploy merely on these local tests.

No homepage chapter, Margins record, archival image, Inspire3 link, paid offer, Jetpack form, analytic script or production setting changed. No claimed subscribers, orders, commissions or net revenue. Frozen #49 untouched.
