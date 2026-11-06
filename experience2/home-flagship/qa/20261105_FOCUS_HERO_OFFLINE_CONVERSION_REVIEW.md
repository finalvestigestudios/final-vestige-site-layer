# 2026-11-05 — Page 6 conversion CTA review, exact-source offline change (HOLD)

**Release: HOLD. No production WordPress writes.** This is an isolated testable proposal, not permission to publish, add tracking, replace page content or infer revenue.

## Sources and why this matters
- WordPress.com connected site 256784396; published homepage Page 6, edit-context modified `2026-11-05T12:07:24`. Read-only audit of raw editor source: **150,710 UTF-16 characters**, FNV-1a-32 drift fingerprint `70740831` (a drift sentinel, not cryptographic integrity), 72 Margins spans, seven unique Experience 2.0 chapter targets, one Jetpack subscription Gutenberg block, two hero links. This is NOT a browser test.
- The same page's WordPress **view-context content**: 171,183 characters, seven chapters, 72 Margins spans, 8 image elements versus 4 in edit-context. The view-context API output contains 0 literal `<form>` or `<input>` elements. Jetpack may render the signup on the actual visitor page; **do not infer that signup is broken from the API alone**. No network response or field performance was measured.
- Candidate `experience2/home-flagship/index.html` in PR #1194 stack already places a Fieldbook CTA in the hero, but that candidate **omits** live-specific Margins and Jetpack. Replacing Page 6 with candidate HTML would be destructive. The new offline transformer targets **only** the existing hero secondary link.

## OFFER → FUNNEL STEP → BLOCKER → PROPOSAL → ACCEPTANCE → OWNER
**Offer:** Existing no-cost 52-page Seven Day Focus Fieldbook; no unapproved merchant/affiliate claims or URLs.
**Funnel:** Grok-qualified viewer → archival homepage → first-screen contextual Focus CTA → guest Jetpack signup → confirmed lead → separately verified paid product sale.
**Blocker:** Published second hero link currently says *Read the investigations* and goes to `/blog/`, while the review candidate surfaces the Fieldbook; this is a source-proven discrepancy, not an observed conversion loss.
**Proposed experiment:** Preserve primary evidence CTA *Enter the evidence room* unchanged. Replace only the secondary existing hero link with *Explore the free 52-page Focus Fieldbook* pointing to existing `https://finalvestige.com/focus/`. Do **not** add competing links, popup, analytics, affiliate URLs, or additional chapters. No user is shown this change unless explicitly approved for release.
**Evidence:** Executed the replacement **in memory** against the actual WordPress Page 6 edit-context source; preflight passed all 7 chapter IDs, 72 Margins, one Jetpack block, existing NYPL media reference and unique original CTA. The replacement changes **exactly 18 UTF-16 characters net**, from 150,710 to 150,728. The first 17,204 characters and last 133,379 characters of the source remain byte-for-byte as JavaScript strings. No source mutation was sent to WordPress.
**Owner:** Homepage review engineering proposes and checks design; founder approves any production release; Claude owns privacy-safe campaign attribution, confirmed paid revenue and order data; Site QA verifies actual subscriber/keyboard/mobile experience; Grok/Praxxis own campaign asset IDs, social delivery and research.

## Reproducible review-only tool
`node --test experience2/home-flagship/qa/test_prepare_focus_hero_review.mjs`

`node experience2/home-flagship/qa/prepare_focus_hero_review.mjs --input /local/private/wp-page-6-edit-context.json --out /local/private/page6-candidate-review.html`

The tool accepts **local** WordPress edit-context export only. It cannot connect to WordPress. It is deliberately pinned to the observed exact page version, 150,710-character length and FNV-1a sentinel. It fails closed on any source/status/drift change, missing 72 Margins, missing Jetpack, a missing/duplicate chapter, missing evidence CTA, or an already-applied hero link. Output uses exclusive-create local file permissions; no automatic WordPress import or publish step exists. For actual release compare SHA-256 receipts emitted by the tool, reviewed patch and fresh live source.

**Test scope:** Native Node 22 source transformer regression suite: 14 cases passed including 11 failure modes/invariants and no production writes. Tests use a representative synthetic WordPress edit-context fixture. Additional in-memory inspection against live editor content passed; no actual hosted page/browser was modified. This test is not CI or independent QD approval.

## Release HOLD gates
1. Obtain founder visual review of **existing published page** and both hero alternatives at 320/360/390/768/1440/1920 plus native 200% zoom. The published experience already has all seven chapters; do not overwrite its 72 Margins or Jetpack.
2. Independently check anonymous browser rendering/click target, keyboard/touch, no-JS accessible meaning, reduced motion, WCAG 2.2 AA with axe and manual tests. Test live Jetpack form, consent and welcome delivery only under existing approval; don't create test subscribers without consent.
3. Verify exact NYPL Brooklyn digital capture rights and current Apollo/Franklin file identity and actual transferred bytes. Proposed CTA leaves all images unchanged; do not interpret this as rights clearance.
4. Measure lab Lighthouse separately from actual field CWV; no invented results. Compare 7/30-day verified net revenue per 1,000 **qualified human** sessions when campaign-to-order attribution is genuinely available. No paid conversions are established by a CTA click or lead.
5. Hosted WordPress.com Personal has no native staging clone. Use free disposable WordPress Playground/Assembler for complete browser QA; separately retain hosted/Jetpack acceptance. No merges, theme changes, CMS writes, plugin activations, subscriptions or spending.

Coordination: #150 homepage, #820 attribution charter, #818 commercial prioritization, #171 Mind editorial, #158 Apollo R&D. Frozen PR #49 must remain at `10495883299d53596992c26a8987f629b2904670`. This proposal is a **new isolated draft** stacked on #1194; it does not modify existing scripts or publish any URL.
