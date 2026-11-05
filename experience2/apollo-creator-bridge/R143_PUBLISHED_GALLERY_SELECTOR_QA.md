# Apollo R143 — published chronology gallery selector defect / staging-only correction

**Governance:** Experience 2.0 #150; conversion #820 / #818. Isolated R143 branch stacked on R142, not homepage PR #49 or Research Desk PR #158. No WordPress writes, deployment, Grok queue changes, checkout edits, new scripts or tracking.

## Confirmed source-backed defect (November 5, 2026)

Read-only WordPress page 2017, `https://finalvestige.com/apollo-1-evidence-atlas/` (last modified `2026-11-04T17:09:24`), includes ONE inline JavaScript bundle and EXACTLY THREE ordered `figure[data-fvx-chrono-photo]` records numbered `0,1,2`.

The published inline `initChronology` code contains:

```js
const photos = $(box, '[data-fvx-chrono-photo]');
if (photos.length === 3) { /* switch the gallery by documented marker */ }
```

The same inline bundle defines `$` as `querySelector`, so `photos` is a single `Element`, not an array. Its `.length` is `undefined`, making the `photos.length === 3` condition false. The contextual-gallery switch and its positional status never activate. The range's independent marker readout still exists. Source evidence is **not** live Chromium acceptance, and this bug is separate from claims about media rights.

**Staged one-character correction:** use `$$`, already defined as `Array.from(querySelectorAll(...))`. `r143_gallery_source_repair.cjs` produces the exact string substitution only for an explicit, read-only HTML export; it refuses missing markers, missing current reader action, unexpected script count, duplicate selectors or already-patched inputs. The standalone tool NEVER writes WordPress and NEVER activates a CTA. `String.replace` must use a callback, since replacement text with `$$` is otherwise interpreted as a special replacement token.

## Preservation and source integrity

- The first marker is the initial fire report (+0); the documented intervals also include +6, +11.3, +14.7 seconds. No intermediate times are asserted as independent observations.
- The three images are *separate historical context*, not photographs of the fire or the individual seconds. Keep that note adjacent to the gallery and maintain NASA original-source links.
- The existing and verified static action **Read the full investigation** remains the only recommended next step. Its canonical destination is `https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/`.
- Gallery images in WP source: S66-58038 (crew training), S67-15717 (spacecraft processing), KSC-20170124-PH_KLS01_0129 (hatch museum view). Commercial/promotional rights for each need human review. Images are not embedded in offline fixture.
- NASA generally permits editorial reuse of released material but prohibits implied agency endorsement; identify recognizable persons and any third-party rights before promotional/product use. Source: https://www.nasa.gov/nasa-brand-center/ . This is NOT item-specific clearance.

## Verification and scope

- Native Node v22.16.0: **60/60 PASS** across the pre-existing R141/R142 suites plus R143 (49 + 11). R143 alone 11/11. Tests ran locally, not exact-head hosted CI.
- The committed R143 source and test blobs matched their locally executed files. Runner also matched its local Git blob.
- Chromium v144: **6/6 offline synthetic gallery scenarios PASS** at 320, 360, 390, 768, 1440 and 1920 px. Demonstrated baseline does not change gallery, corrected selector does change exactly one figure at marker thresholds; no-JS leaves all 3 context records visible; reduced-motion, Home keyboard navigation and no horizontal overflow checked. Reproducible screenshot PNGs and receipt SHA-256 hashes are in the separately generated QA artifact.
- The committed exact source patch function was also executed in-memory against **actual WordPress page 2017 content**, identifying precisely one original selector and producing a one-character-only patched copy with the same 3 ordered figure records and same existing primary CTA. WordPress was not changed.
- **Actual page browser navigation:** `ERR_BLOCKED_BY_ADMINISTRATOR` in Chromium. Actual-page axe, LCP, CLS, touch and manual screen-reader acceptance NOT RUN. Offline results DO NOT satisfy production release or WordPress/Assembler QA.

## Conversion-first disposition

OFFER: proposed rights-cleared Apollo educator evidence dossier (not yet verified as sellable); FUNNEL: proposed Grok long-form -> published Atlas -> full investigation -> later approved educator offer -> independently reconciled Payhip order; BLOCKER: reduced trust from dead gallery interaction plus no verified matching commercial SKU; CHANGE: precise nonpublishing selector repair and targeted tests; PASS: source-level and offline synthetic acceptance; FAIL/HOLD: actual-page browser and merchant/rights verification; OWNERS: Apollo isolated prototype, Claude production integration, Founder release, Grok distribution, Praxxis independent social QA.

No verified Apollo-specific Payhip purchase, qualified Grok session, paid affiliate conversion, refunds/fees or realized net revenue. Revenue/1,000 qualified human sessions and 7/30-day cohort conversion are **NOT COMPUTABLE**. Do not count CTA clicks or email interest as paid sales.

## Release requirements

Claude must review any approved staging integration. Independently execute real-page Playwright/axe, touch/keyboard/no-JS, LCP/CLS, desktop/mobile screenshots and source/caption accuracy, obtain individual image-rights review, verify a relevant sellable product and checkout/attribution, obtain independent QD and green exact-head CI, and secure founder release approval. **STAGING HOLD** until all gates pass; no merge or live write.
