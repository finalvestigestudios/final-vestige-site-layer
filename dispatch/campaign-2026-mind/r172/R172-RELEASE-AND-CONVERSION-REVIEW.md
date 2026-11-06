# Dispatch R172 — consent-to-customer evidence and release decision (UNSENT)

**Read-only source review:** 2026-11-06 15:35 PT. This is a draft evidence package, not an authorized newsletter send or a WordPress change. Issue #174 is the campaign master; #171 owns seller-guide/merchant eligibility; #129 owns Focus engineering; #820 owns conversion reporting. The flagship homepage and PR #49 are untouched. Stack on draft PR #1315, not on main.

## Live provider facts, with meaning

- Jetpack newsletter: **ON**; site can send **YES**, **no provider send blockers**; **per-post new-post default OFF**, recent five posts show `never_sent_opted_out`; sender is "Final Vestige Studios", reply-to no-reply, email content full. **Do not treat default-off as a global safety lock**: the individual post's send-to-subscribers option must also be inspected.
- Configured welcome contains the complete 52-page Focus Fieldbook PDF URL. This is **configuration evidence only**. Gmail search on 2026-11-06 found a **confirmation request** dated 2026-10-25 but no completed welcome in the bounded search; absence in one mailbox is not global proof of failure.
- Newsletter provider reports `total=3, confirmed=3, unconfirmed=2, suppressed=0`. Jetpack Stats reports `wpcom=3, email=0` (legacy email followers). **These are different surfaces, not addends.** Three counted followers **do not** establish three people who opt into email. WordPress documentation explicitly states that "Not confirmed" is outside total, and Reader-only users may be "Not subscribed" by email. Filter the native Jetpack → Newsletter → Subscribers **Email subscription** column. The available connector does **not** expose that private row-level status, and therefore we did not inspect or export the list.
- `/dispatch/` page 523 remains published with native subscriptions block in editable source; WordPress view-context rendition exposes a Subscribe self-link rather than an email input. Neither rendering is evidence of the actual guest form. **Browser guest verification missing.**
- `/focus/` page 1579 published; the known `?subscribe=`/CSS-class false-success source risk is not remediated live; the R164 proposal is review-only. A revealed PDF panel is **not** a verified `confirmed_signup` event.
- Editorial Standards require original/primary sources, visible uncertainties, corrections, and clear commercial relationships. None of our offer testimonials, vendor brainwave or clinical claims may be presented as independent proof.

### Provider-status decision and privacy

Only a review of **provider-native Email subscription status** may support email eligibility. A user entering an address, clicking a confirmation link, seeing a URL parameter, opening the download, being present in subscriber totals, or reading in WordPress Reader cannot on its own satisfy this. R172's checkpoint module is a deliberately **offline** method for consistency checking already independently reviewed transitions. It is not a WordPress integration, not a source of real signups, and never converts synthetic examples into actual confirmed leads. It deduplicates **across runs**, unlike a per-batch Set, and separates **resuming paused email** from a **new email enrollment**. Its local persistent checkpoint is restricted operational data, **never commit actual checkpoint or event records to a repository, Drive, or email**. Do not generate IDs from subscriber names, email addresses, IPs, or unkeyed email hashes; only privacy-reviewed randomly generated provider-event tokens are acceptable.

## Single-offer pilot: ONE commercial hypothesis; no premature affiliate link

**Hypothesis:** Readers arriving from evidence-led attention or perception videos may want to compare a short meditation audio product with their free 7-day observation routine. The intended optional evaluation is **Zen12 Premium**, not a generic unspecified "Zen12" purchase. Mind Studio R178 PR #1317 remains unpublished and has its purchase link disabled.

Official merchant's public sales page `https://zen12.com/`, read 2026-11-06, **claims** 12 levels, four options per level, 48 MP3 files and a displayed Premium price of **$87.99** and advertises a one-year money-back guarantee. Those are **seller page claims**, not a finalized checkout price, independently tested download, refund execution, or scientific outcome. The headline claims an "hour of meditation in 12 minutes", which has **not** been independently established for this particular product. Do **not** repeat its stress/anxiety, health, brainwave, automatic meditation, or time-equivalence promises as fact. The site also displays Beginner and Advanced tiers ($67.77), making offer-specific copy and user choice materially important. The source shows embedded product videos, not our verification of their accuracy or rights.

**Email slot #03 remains HOLD_MERCHANT** until Mind Studio can evidence Final Vestige's actual partner acceptance, allowed email channel, correct tracking/link format, exact version/checkout/refund and guide URL, approved disclosure and genuine legal/footer previews. Slot #05 (Hypnosis Live) remains separately HOLD_MERCHANT. One merchant approval must never be generalized to all products or channels. Unverified affiliate terms can block any promotional CTA even if the product is generally available for purchase.

## Copy-to-route audit of original PR #175, without rewriting

| Edition | Assignment | Source manifest destination | Current release implication |
|---|---|---|---|
| 01 | editorial perception | published Puységur archive | Valid first-party destination; shares #02 destination, diminishing distinctiveness |
| 02 | editorial history of suggestion | published Puységur archive | Alternative in R170 points to published Mesmerism for separation; substitution NOT approved |
| 03 | potential commercial Zen12 | `[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]` | STOP; R178 guide not live, affiliate permission unknown |
| 04 | editorial Apollo 1 | published Apollo 1 historical investigation | First-party destination; claims require source-level NASA confirmation |
| 05 | potential commercial Hypnosis Live | `[[APPROVED_HYPNOSIS_LIVE_WARMUP_GUIDE_URL_REQUIRED]]` | STOP; no approved live page, exact product and channel right missing |
| 06 | editorial attention log | published /focus/ | Live but sends already-subscribed reader back to lead capture; optional Change Blindness alternative R166 NOT approved |

The original four editorial and two provisional commercial issue allocation remains unchanged; no date, audience, or send has been authorized. All six original emails carry `[[VALID_POSTAL_ADDRESS_REQUIRED]]` and `[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]`, correctly blocking use as publishable post content. The WordPress.com/Automattic postal address in its own confirmation email is not Final Vestige's valid business mailing address.

## Offer → funnel step → blocker → experiment/change → evidence → owner

| Order | Offer → step | Blocker | Change/experiment (non-live) | PASS/FAIL evidence now | Owner |
|---|---|---|---|---|---|
| P0 | Free Fieldbook → actual email opt-in | Provider truth unavailable; Focus UI implies success too early | Claude validates signed-out guest and R164 repair, never treating download clicks as signups | FAIL for trustworthy measured signup; risk reproduced, live fix not deployed | Claude / Site QA |
| P0 | Reader/follower → email recipient | Total3/confirmed3 vs 2 pending are nonadditive; email eligibility unknown | Private filtered provider status reconciliation; log **aggregates only** | NOT VERIFIED; native row list unavailable to this read-only connector | Dispatch |
| P0 | Opted-in reader → received welcome | Configuration != receipt | Review existing owned inbound evidence or later explicitly authorized controlled mailbox test | NOT VERIFIED; search found confirmation request only | Dispatch |
| P0 | Editorial newsletter → legitimate delivery | Real Jetpack email preview/postal/unsubscribe unknown | Authorized **non-sending** Jetpack Preview email; separately inspect native footer; do not use Send test email | NOT VERIFIED; static .html or synthetic .eml is not a received Jetpack email | Dispatch / Founder |
| P1 | Interested reader → Zen12 guide | Existing Mind R178 guide unmerged/unpublished; link disabled | Mind verifies product and posts approved first-party guide under its lane | HOLD_MERCHANT; source merchant page read only | Mind Studio |
| P1 | Guide → affiliate purchase | Named approval/authorized earning link/email rights not proven | Confirm partner permission on original named account and approved channel | HOLD_MERCHANT; public affiliate page ≠ acceptance | Mind / Founder |
| P1 | Paid order → net realized proceeds | No settled orders/refunds/fees or human-session denominator verified | Compare source-confirmed merchant/Payhip sale against eligible session cohorts | NOT COMPUTABLE; never infer sale from email click | Commerce / Praxxis |

## Canonical attribution proposal (NOT instrumented or live)

Existing Grok asset ID → UTM source `youtube`/`tiktok` etc, medium `organic_social`, campaign `mind_pilot_2026_11`, content real `asset_id` → Focus landing → native provider-reviewed transition → existing Jetpack email (after founder release) → first-party newsletter CTA with `utm_source=dispatch&utm_medium=email&utm_campaign=mind_pilot_2026_11&utm_content=dispatch_03` → approved guide → authorized merchant earning link → **merchant-confirmed settled conversion** → fees, refunds and realized net revenue. Store source asset and campaign at the session level when legitimately observable, not as a copied subscriber address. WordPress link-click metrics are funnel diagnostics, not settled sales. Report separate 7-day and 30-day cohorts and tiny-sample caveats. KPI is net realized revenue per 1,000 qualified human sessions, and must remain `NOT_COMPUTABLE` without trusted denominator and settlements. Never report fake A/B efficacy on three counted subscribers.

## Release control

**ALL 6 = HOLD_UNSENT. Commercial #03/#05 = ADDITIONAL HOLD_MERCHANT. Founder final campaign approval absent.** No emails, test emails, WordPress publication, site updates, subscriber mutations/imports, affiliate links, new platform, spend, or Grok task writes occurred.

References: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174 ; https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171 ; https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175 ; https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201 ; https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1315 ; https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1317 ; https://wordpress.com/support/subscribers/ ; https://zen12.com/ ; https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .
