# EX2 P0 — native keyboard order + visible-focus admission
**2026-11-05 | DRAFT / RELEASE HOLD | Parent PR #1089 head 459e0a12edf36d0506ce49c81761d897a6957ae5**

## Specific release-qualification false positives discovered
Previous `inspect_focus_entry()` used `secondary.focus()` and then `document.activeElement===el`, which **does not demonstrate that a visitor can reach the action with Tab in the intended order**, or see a focus indicator. It falsely accepted all three real-Chromium reproductions below:

| Representative browser mutation | Previous gate | Corrected gate |
|---|---|---|
| Remove the secondary link's keyboard focus outline | FALSE PASS | REJECT: visible focus absent |
| Put an unrelated native button between the evidence and Focus hero links | FALSE PASS | REJECT: Tab reaches the button first |
| Give the Focus link `tabindex="1"` (inappropriate positive tabindex) | FALSE PASS | REJECT: next native Tab from evidence misses Focus |

These are **verification defects** in the staging browser test, not observed production WordPress failures.

## Exact isolated engineering change
1. Preserve the nine existing Focus interface checks (evidence-primary hierarchy, two anchors, free 52-page offer, exact destination, 44px dimensions, horizontal containment, early placement, hit-test unobstructed, keyboard focus).
2. Replace the final scripted focus-only proof with a **native Chromium Tab** from the evidence-first action to the second Focus action. Require the target to become `document.activeElement` and match `:focus-visible`.
3. Require an actual computed outline (not `none` or `hidden`) at least 2px wide. The existing production-candidate `flagship.css` specifies a 3px antique-gold `:focus-visible` outline, so the fixture now matches that source style.
4. Add twelve hostile cases total, including three new mutations above. The existing exact-head verifier already calls `inspect_focus_entry()` at 360/390/768/1440/1920 with an additional no-JS 390 stage pass, and already Git-attests the helper and browser test. Both files changed on this isolated branch; no public homepage, WordPress, or analytics change.

## Executed evidence
- **Native Python Playwright + system Chromium:** 6/6 offline reduced-motion, no-JS positives (320/360/390/768/1440/1920) and 12/12 adversarial rejections: **18/18 PASS**.
- Before/after Chrome reproduction independently executed the ORIGINAL PR #1089 helper and the revised helper against each of the three new mutations. All three were **false passes before** and **correct rejections after**.
- Source custody: exact local `git hash-object` new helper `64432932b192734d2ba332fc7984dd88b22a01a6`; new browser test `65653487ab70998c366b1bea61e1fd5f430c6a3c`. GitHub blob receipts must match on review.
- Local syntax compilation passed. Evidence archive is supplied in the automation report; no user/customer data included.
- Scope of evidence: **isolated browser fixture**. No real WordPress Playground/Assembler integration, current exact-head CI, axe/WCAG AA, native 200% browser zoom, Safari, first-party media bytes, Lighthouse, or field CWV pass claimed.

## Identity, rights, commercial truth
Evidence-first hero and original Franklin Victory Point note folio unchanged. All 7 chapters, 72 Hidden in the Margins items, existing /focus/ destination and Jetpack subscription remain outside this branch's editing scope. The historical rights ledger remains a release gate, particularly NYPL reproduction status. No images, audio, scripts, analytics, affiliate links, sales claims, merchant checkout, services or costs introduced. The published page is not modified.

**OFFER → FUNNEL STEP → BLOCKER → CHANGE → PASS/FAIL → OWNER:** existing free 52-page Focus Fieldbook → historical-evidence hero to resource → scripted-focus false positives mask invisible/disordered keyboard conversion route → demand a real Tab, sequential focus and visible 2px+ indicator → representative Chromium 18/18, WordPress integration HOLD → homepage engineering; Claude for backend/attribution, Grok/Praxxis for acquisition.

No confirmed subscribers, merchant-paid orders or realized net revenue measured. Primary commercial KPI remains verified net revenue per 1,000 qualified human sessions, not link clicks.

## Release decision
**HOLD.** Run the current combined candidate in authorized private isolated WordPress Playground/Assembler, including the exact code-backed staging verifier, source hashes, authentic media transfers, axe, keyboard/touch/no-JS/reduced motion, 200% zoom, Lighthouse and founder first-screen review. QD and CI must pass on this exact head, and founder must approve release explicitly. Do not merge/deploy, publish to WordPress, install plugins, activate affiliates, change tracking, send mail, or spend.
