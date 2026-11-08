# Dispatch R197 — evidence-led alternate + real consent/revenue gates (DRAFT ONLY)

**As of:** 2026-11-07 ~16:38 America/Los_Angeles (newsletter provider snapshot at 2026-11-08T00:38:05Z). **Owner:** Dispatch #174. **Companion:** Mind #171 and its **unpublished** guide PR #1499; Focus #129; conversion #820. **Stacked on:** Dispatch R196 PR #1496 at `c29fab67ad7a9d431c57933d98eaa56cfe983c67`. Frozen homepage PR #49 and original campaign PR #175 remain untouched. This directory is additive only.

## What is new and why it matters
- `01_WHEATSTONE_OPTIONAL_UNSENT.{md,txt,html}`: original evidence-led optional Issue 01 based on Charles Wheatstone's 1838 Royal Society stereoscope paper, with Smithsonian and MPIWG archival corroboration; one primary CTA to the **published** Change Blindness investigation. This is **not** an approved replacement for the original pilot.
- `COPY_CONVERSION_AUDIT.md`: critical review of all six original subjects, audience match, duplicate CTAs, dead guide destinations, direct PDF/welcome issue, and legal/merchant facts; concrete proposed edits only.
- `CONSENT_ATTRIBUTION_ONE_OFFER_CONTRACT.md`: actionable but **NOT DEPLOYED** `confirmed_signup` contract and read-only reconciliation plan for Grok asset attribution → live article → one Jetpack opt-in → actual welcome → only an approved Zen12 guide → independently settled paid commission.
- `release_gate.cjs` with `tests/release_gate.test.cjs`: fail-closed six-edition release, deduplicated provider confirmation and revenue proof functions; no network calls. Tests use only synthetic records and **do not attest to real email subscribers or actual revenue**.
- `EVIDENCE_SNAPSHOT.json`: source-linked WordPress/merchant blockers, *null* rather than fabricated conversion data.

## Independent checks
- Master PR #175 remains at Git SHA `d57ccdba3aee8f065e143e101c2945f4f3d01647`. From the prior verified-source bundle, exact Git blob hashes for all eight master-source files matched this run's GitHub fetch; **native Python 6/6 passed** in the local container on 2026-11-07 PT. This is a local reconstructed source tree, NOT a GitHub checkout.
- R197 GitHub-fetched committed source: **11/11 synthetic V8/CommonJS-compatible test cases passed**, plus **8/8 committed-source static checks**, including single editorial CTA, subject/preheader equality across MD/TXT/HTML, publisher postal/unsubscribe HOLD placeholders, no script/tracking pixel/external merchant link, and hard-held offers. **No native Node.js, CI, browser render or actual received Jetpack mail** was executed for R197. Email reviewer HTML is a preview, not Jetpack's final rendering.
- Official product page inspection: Zen12 and Total Focus current **seller copy only**; merchant terms and final checkout not independently verified. Site has no publicly evidenced named FV affiliate/email permission or merchant-approved earning link.

## Provider read-only facts
Jetpack: enabled, `site_can_send=true`, new post auto-email false, full format, 52-page welcome configured; 3 total counter, 3 confirmed counter, 2 unconfirmed counter, suppressed 0. Followers: 3 WPcom and 0 email-only. These are not additive and **email-eligible subscribed aggregate is unknown**. Five recent posts opted out of newsletter sending. The browser's Focus success state (query/CSS) is not provider consent. Received welcome, valid FV postal-address footer, working unsubscribe and publisher partner acceptance remain unverified. No raw subscriber identifiers accessed.

## Release decision
All 6 = **HOLD_UNSENT**. Issues 03 and 05 = **HOLD_MERCHANT**. Zero emails/test sends/scheduled sends/published WordPress posts/list imports/settings changes/affiliate activations/tracking deployments/paid services/Grok queue changes.

**Next meaningful pass/fail tasks in owner order:** (1) Focus/Claude: privately reconcile actual `Email subscription=Subscribed` and dedupe/suppression; (2) Dispatch: read-only authentic received welcome + Fieldbook link evidence, genuine authorized Jetpack rendering and actual FV postal/unsubscribe; (3) Mind: named Inspire3 acceptance, explicit email channel permission, issued earning URL, seller claims/terms, **live** vetted guide; (4) Commerce/Praxxis: reconcile paid orders/commissions with refunds, fees and qualified human traffic (7/30-day cohorts), otherwise **NOT COMPUTABLE**.

**Official references:** Wheatstone DOI https://doi.org/10.1098/rstl.1838.0019 ; archival record https://vision.mpiwg-berlin.mpg.de/items/d7kczgme/ ; Smithsonian https://www.cooperhewitt.org/2016/08/10/through-the-looking-glass/ ; Zen12 https://zen12.com/hnp ; Total Focus https://hypnosislive.com/mental-skills/total-focus ; merchant portal https://affiliates.inspire3.com/ ; FTC https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .
