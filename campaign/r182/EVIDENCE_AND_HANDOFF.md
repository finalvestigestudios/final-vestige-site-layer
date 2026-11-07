# R182 | Conversion-first Dispatch evidence and Focus false-positive reproduction

**SOURCE BUILT, NATIVE TESTS PENDING IN HOSTED CI; NOT LIVE, NOT APPROVED.** Issue #174; companion #171 / #129 / #820. Master #175 exact d57ccdba3aee8f065e143e101c2945f4f3d01647, stacked on draft #1382 exact 514ae2a18d1f376ad0c8c1f463639633be43b0d3, homepage #49 untouched.

## Observed provider truth at 2026-11-07 09:37 UTC
WordPress Jetpack Newsletter ON, default automatic new-post emails OFF, full-content format; recent 5 published posts **never_sent_opted_out**, not bounced. Counted=3, confirmed=3, unconfirmed=2: categories NONADDITIVE. Independent followers: wpcom=3, legacy email-only=0. **Actual email-eligible recipients UNKNOWN**, not assumed 0 or 3. Welcome configured with 52-page Fieldbook; no actual welcome receipt demonstrated. Bounded connected Gmail search 2026-10-24–2026-11-08 returned no exact "Seven Day Focus Fieldbook" or "Welcome to The Dispatch" message; this does NOT disprove delivery to other subscribers.

## New reproducible client-side evidence
Live Focus page ID1579's `fvf-gift-v2` script treats any nonempty `subscribe` query value outside five error strings as sufficient to reveal gift panel. Exact observed script excerpt isolated in `focus_gate_probe.cjs`, with native Node synthetic negative controls (not actual visitor form submission). `?subscribe=anything` and `?subscribe=unconfirmed` reveal the panel in simulation, while provider confirmation remains unobservable/null. The existence of this query behavior does NOT prove that the signup form fails, that a real subscriber is created or that a publicly available PDF is a security breach. It establishes only that **visible gift panel != confirmed_signup**. The WordPress API page serialization also shows a Subscribe anchor; public crawler evidence has shown an email field, so neither form success nor failure is proven without authorized signed-out inspection.

**Claude #129 owner patch proposal (NOT APPLIED):** never emit `confirmed_signup` from an arbitrary query, DOM class, download, click or browser animation. Display a truthful 'check your email' state for unconfirmed requests; emit the one authoritative event only on a trusted Jetpack provider-confirmation transition, deduplicate in the established provider checkpoint from R172, and do not expose email addresses or confirmation tokens in analytics. Allow an openly accessible PDF as a separate editorial decision.

## High-impact copy review and new optional Issue 01
Original Issues 01 and 02 repeat the Puységur CTA, weakening progression. New alternate Issue 01 sends historical readers to already-live https://finalvestige.com/2026/11/02/change-blindness/ through a specific 1998 Simons/Levin street experiment (primary https://doi.org/10.3758/BF03208840) with **half-detected** bounded to the specific experiment; no generalized false witness, health, or seller efficacy inference. Original 6 manuscripts preserved. Subject/preheader proposed, not verified by Jetpack. Native HTML/plain reviewers ARE NOT Jetpack-rendered mail. One primary first-party CTA; no commercial earning link.

## Exact seller and FTC alignment
Zen12 Premium official https://zen12.com/hnp markets 12 levels / 48 MP3 recordings, plus claimed short-session equivalence and brainwave benefits; seller claim, not independently established outcome. Hypnosis Live Total Focus https://hypnosislive.com/mental-skills/total-focus lists 33 min / 47 MB and strong unsupported focus claims. Sales-page cached prices have differed; no verified checkout price or fulfilled refund. https://affiliates.inspire3.com/ does NOT prove **Final Vestige-specific approval, EMAIL permission or allowed earning-link format**. Mind #171 has NOT marked merchant eligible or approved live warm-up guide. Commercial Issues 03/05 remain HOLD_MERCHANT, 4 editorial remain in mix.

FTC https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business requires truthful commercial headers/subjects, appropriate advertising identification, a valid **Final Vestige** postal address, usable opt-out and honoring opt-outs; Automattic or merchant address does not qualify as FV's own address. Native WordPress editor **View → Email preview** of a published post is documented by WordPress, but **not captured** in this run and not the same as receiving mail. Platform tool provides status/settings, not rendered inbox evidence. Do not change post-level Send checkbox merely to preview.

## OFFER → FUNNEL → BLOCKER → EXPERIMENT → EVIDENCE → OWNER
| Offer/funnel | Blocker | Proposed experiment/change | Evidence state | Owner |
|---|---|---|---|---|
| Focus → confirmed lead | query success UI not provider consent | truthful pending UI + authoritative confirmed event only | **FAIL** arbitrary subscribe value opens gift in isolated source-script test; no real subscriber test | Claude #129 + Dispatch QA |
| Dispatch → welcome + book | configured does not mean received | inspect authorized already-received welcome, no outbound message | **UNKNOWN** bounded Gmail 0, no provider receipt | Dispatch |
| Dispatch → actual inbox | no native email preview, FV postal or unsubscribe proof | read-only published-post editor preview then independent authorized received-mail check | **NOT TESTED**; static reviews are not proof | Dispatch |
| Issue03 Zen12 → approved guide → sale | named email authorization and LIVE guide absent | authenticate agreement/link/approved live page via Mind | **HOLD_MERCHANT** | Mind #171 |
| Sale → realized net revenue | no verified settlement or qualified human sessions | reconcile 7/30-day cohorts with actual Grok asset_id and refunds/fees | **NOT COMPUTABLE** | Commerce/Praxxis #820 |

No UTM values invented, no fake AB stats, no merchant prices copied, no paid conversion claimed. No emails, website or list changes, no Grok queue edits or spend. Original founder final approval required even when all other checks are established.
