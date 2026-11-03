# R103 handoff — Mind & Perception / Zen12
**Status: DRAFT ONLY · HARD HOLD · 2026-11-03**

## Deliverables

- `investigation.md`: ~2,032-word original **The Word That Was Never Said**, interpreting Deese (1959), Roediger & McDermott (1995), Loftus & Palmer (1974), and Robinson & Roediger (1997). Its Puységur bridge is a **historical-methodology analogy, not a claim of scientific corroboration**. Includes a free **explicitly unvalidated** exercise; never infer autobiographical falsehood from lab rates. **No commerce in investigation**.
- `zen12-guide.md`: ~1,796-word independent, exact-offer buyer guide. Verified public catalog, sales page, full-course checkout, privacy and precise `inspire3.com/terms/` seller terms as of Nov 3. No fabricated use, commission, price or benefits.
- `pilot-a.html` and `pilot-b.html`: complete *unpublished Gutenberg Custom HTML* source; **identical substantive buying advice**. B alone adds an original inline SVG poster and 40-second storyboard/transcript using `<details open>`. No simulated video playback.
- `optional-film.vtt`: six consecutive caption cues across exactly 40 seconds for **future original first-party** media only; this milestone does **NOT** create, upload or host an MP4.
- `mind-hub-alternative.html`: four-stream Mind Archive editorial UX concept. **Do not supersede or merge over canonical Mind hub PR #172**.
- `evidence-and-gates.json`: 15 identifiable sources, 45 decisions (including invalid/unsupported claims), 39 CLOSED activation/release gates, zero earning URLs.
- `attribution.mjs`: nonexecuting-by-default, **synthetic-only** offline measurement contract. `recordLiveEvent()` always throws; no raw referrer, PII, URL, tokens, buyer identities, event timestamp, session ID, cookies, localStorage, beacon or network calls. Categorical rows only, suppress groups with fewer than 20 rows; synthetic counts **do not establish actual sales or a conversion rate**.
- `pilot.test.mjs`: ten reproducible Node test cases for core equality, disclosure, disabled controls, source grounding, responsive/a11y structural safeguards, film provenance, strict privacy, cell suppression and live hard hold. To run from repository: `node --test mind/review-r103-false-memory-zen12/pilot.test.mjs`.

## Evidence update unique to R103

The seller's accessible `https://inspire3.com/terms/` states that **Zen12 is covered by a 1-year seller money-back guarantee** and that card refunds requested after 90 days are handled manually through PayPal. It also states that digital MP3/PDF downloads *may be tagged with purchaser personal information* and mentions SMS marketing at approximately **3–4 messages per week**. This is **verification of what the public seller terms say**, not proof of refund processing, actual tagging, delivery, or product benefits. Do not transplant the **14-day** Hypnosis Live return window into Zen12: the seller's terms distinguish the products. The seller's `https://inspire3.com/privacy/` explicitly permits sharing referred buyer names, emails and purchased-product details with affiliates. Final Vestige needs a **written aggregate-only / no-identifying-buyer-information agreement** before permitting an affiliate integration.

Sourced science: Ingendoh et al. 2023, https://doi.org/10.1371/journal.pone.0286023; 14 heterogeneous binaural-beat EEG studies (5 consistent, 8 contrary, 1 mixed). This is **not** a clinical trial of Zen12 and not support for one-hour equivalence. FTC policy: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking and https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .

Exact seller offer inspected: https://inspire3.com/ ; https://zen12.com/hnp ; https://zen12.com/getstarted ; https://inspire3.com/privacy/ ; https://inspire3.com/terms/ . Never present seller advertising as validated independent benefit.

## Founder A/B design hypothesis, NOT an outcome

**A — source guide only:** clear promise-to-proof distinction, answer to seven objections, free exercise, single existing Focus route, pros/cons, current seller privacy/refunds and disabled merchant control. **B — same content + optional original short film:** inline vector art and six-scene text transcript on one small conceptual prototype. Neither version requires JavaScript; video is **not hosted** and no play action is represented. If an actual film is produced later, use a first-party H.264/AV1 fallback with a light poster, `preload="none"`, real `<track kind="captions">`, explicit user play, no autoplay, no cookies, and verified transcript parity.

Performance budget proposal for approved media, not a measured score: static B extra DOM/SVG under 25 KB; future optional media poster under 30 KB and video under 350 KB compressed, loaded only on user action. Confirm actual assets and server compression independently.

Suggested future experimental unit: same-source randomized *consenting, privacy-safe* visits when approved, A vs B. Predefine only aggregate CTA-visibility or allowed outbound-click counts by **categorical** source, no purchase attribution unless merchant privacy-safe agreement exists. Pre-register primary metric (legitimate disclosed offsite click-through among eligible visits), guard against confounding placement and unequal copy. Report small cells below twenty as withheld and never infer revenue from clicks. **NO A/B experimentation or visitor collection in this draft.**

## Internal linking / SEO and distribution (none made live)

- Existing published Change Blindness → /mind/ when and only when future hub has approval; contextual primary science rather than offer funnel.
- Existing Puységur Animal Magnetism Files → historical-suggestion stream; new false-memory draft as **cross-reading**, not evidence about animal magnetism.
- New *The Word That Was Never Said* potential slug `/the-word-that-was-never-said/` (proposal only; do not create a broken link) → /mind/ four streams; optional existing Focus Fieldbook.
- Proposed search targets: “false memory word list experiment,” “why do we remember words never said,” “zen12 audio meditation evidence,” and “binaural beats brainwave entrainment review.” Research intent and commercial intent **must not be conflated**.
- TikTok 20-second hook: “Did you remember a word that was never said?” Explain experiment constraints in caption and point to eventual investigation, NOT directly to a paid audio checkout. No simulated success metric, misleading visual demo or reposted copyrighted stimuli.
- Planned product paths: /mind/ → independent Zen12 buyer guide, without requiring Focus sign-up. Dispatch Issue 03/05 commercial CTA remain **HOLD_MERCHANT**; Issue #174 owner retains newsletter authority.

## QA handoff / blockers

**Source-only checks** must pass on exact committed SHA. No actual runtime WordPress browser test or native Node run should be claimed unless executed. Before release demand mobile widths 360/390/768/1440/1920, keyboard and screen-reader review, WCAG 2.2 AA contrast, no-JS, reduced motion, real caption sync, CSP/XSS scrutiny, HTTPS destination/affiliate redirects, privacy-by-design legal review, exact merchant SKU terms/refund/creative/approval, independently verified product health claims and founder CMS release. The prototype's embedded `<style>` may be sanitized by WordPress; test Gutenberg processing and actual theme styles rather than assuming production compatibility.

**Coordination:** PR #49 is frozen flagship and Issue #150 is owned by homepage art lead. Mind canonical hub is PR #172; this proposal is a comparison and must not overwrite it. Site QA is #126. Dispatch #174 owns newsletter drafts, approvals and existing Jetpack welcome; do not modify or send. Preserve the **single** Focus route, no new paid SaaS or mailing-list form.

**Safety and release:** No WordPress CMS writes, menu changes, emails, signup changes, affiliate links, buyer-data requests, pixels, live attribution, source-copying of partner ads, merges or deployment. Maintain 39 CLOSED release gates until each is independently evidenced.

**Practical QA:** `node --test mind/review-r103-false-memory-zen12/pilot.test.mjs` (only after access to native Node). Compare exact GitHub file blobs to reported source hashes; inspect visual at agreed breakpoints and screen-reader semantics. R103 review notes/testing must be recorded under Issue #171 with exact branch and final commit SHA.
